# 09 API Contract

## Purpose
This document defines implemented API contracts, request/response examples,
and explicit planned gaps.

## Status
Implemented routes with release-readiness gaps.

## Implementation Status

The following routes exist and have deterministic API tests:

- `POST /api/notion/index/full`
- `POST /api/notion/index/page`
- `POST /api/notion/index/incremental`
- `GET /api/notion/index/status`
- `POST /api/ingest/source`, `/document`, `/url`, `/youtube`, `/chat-text`,
  and `/image-ocr`
- `POST /api/supplement/propose`, `/accept`, `/reject`, and `/edit-later`
- `GET /api/supplement/pending` and `/{change_request_id}`
- `POST /api/qa`
- `POST /api/telegram/webhook`

Current contract gaps:

- Notion index routes use the bundled mock reader in default runtime wiring;
  setting `NOTION_BACKEND=live` selects the read-only Notion REST adapter and
  append-only writer together, and requires `NOTION_TOKEN` without fallback.
- API routes and the Telegram webhook have optional configured trust boundaries:
  API bearer authentication, Telegram webhook secret validation, and an
  allowed-chat policy. Missing optional settings preserve local/test
  compatibility and are reported by preflight.
- `/health` is shallow liveness. `/ready` is implemented with deterministic
  dependency checks, including Redis/RQ in local mode. `/metrics` is a public
  Prometheus-compatible workflow/stale-run/cost-budget surface.
- Protected `/api/ops/workflows` list/detail routes expose redacted workflow
  metadata and stale state. Protected reconciliation and cost-budget routes
  never contact Notion or rerun business work.
- Telegram webhook updates with a non-null `update_id` are idempotent. When
  `REDIS_URL` is configured, the first request claims the ledger, enqueues the
  background job, and returns `202` with `status=running` and
  `skipped_reason=QUEUED`; the worker later persists the terminal outcome.
  Duplicate
  succeeded/failed updates replay the stored outcome; a duplicate currently
  running update returns `202` with `status=running` and
  `skipped_reason=DUPLICATE_UPDATE_IN_PROGRESS`.
- `POST /api/ingest/*` and `POST /api/supplement/*` accept an optional
  `Idempotency-Key` header. The same key and canonical payload replay the
  persisted response; a different payload returns `409` with
  `error_code=IDEMPOTENCY_KEY_CONFLICT`; a concurrent owner returns `202` with
  `error_code=IDEMPOTENCY_IN_PROGRESS`. Requests without the header keep the
  existing behavior.

The queued Telegram job uses the canonical module-level callable
`src.worker.telegram.process_telegram_webhook_job`. The worker validates that
RQ can import this path before consuming the queue; a worker import failure is
not handled by switching the API back to synchronous execution.

Examples below document route schemas and deterministic tested behavior. They
do not by themselves prove live Notion, Telegram, OpenAI, parser, or worker
integration.

## Ops APIs

### GET `/metrics`

Returns fixed Prometheus text metrics. It does not include workflow metadata,
page ids, source text, credentials, or upstream exception bodies.

### GET `/api/ops/workflows`

Protected workflow status list. Optional `status` and bounded `limit` filters
are supported. Returned metadata is recursively redacted.

### GET `/api/ops/workflows/{workflow_run_id}`

Protected workflow status detail. The response includes `age_seconds`, a
deterministic `stale` flag, and nullable recorded cost.

### POST `/api/ops/workflows/{workflow_run_id}/reconcile`

Protected stale-running reconciliation.

Request:

```json
{
  "status": "failed",
  "failure_reason": "UNKNOWN_ERROR"
}
```

Only stale `running` workflows may transition to `succeeded` or `failed`; the
endpoint never reruns the workflow's business operation.

### GET `/api/ops/cost`

Protected aggregate cost-budget status. Unknown model pricing is reported as
unknown rather than estimated.

## Trust Boundaries

Protected API routes are all `/api` routes except the Telegram webhook. When
`API_BEARER_TOKEN` is set, callers must send:

```text
Authorization: Bearer <configured token>
```

Missing or invalid credentials return `401` with `error_code=API_UNAUTHORIZED`
and `failure_reason=AUTHENTICATION_FAILED`. `/health` and `/ready` remain public
operational endpoints.

The Telegram webhook accepts
`X-Telegram-Bot-Api-Secret-Token: <configured secret>` when
`TELEGRAM_WEBHOOK_SECRET` is set. Missing or invalid values return `403` with
`error_code=TELEGRAM_WEBHOOK_FORBIDDEN`. When
`TELEGRAM_ALLOWED_CHAT_IDS` contains comma-separated chat ids, updates from
other chats return `403` with `error_code=TELEGRAM_CHAT_NOT_ALLOWED` before a
workflow run starts or a reply is sent.

These checks are deterministic backend policy. They do not inspect or delegate
authorization decisions to the LLM.

## Mutation Idempotency

The API middleware applies idempotency to these POST mutation families:
`/api/ingest/source`, `/api/ingest/document`, `/api/ingest/url`,
`/api/ingest/youtube`, `/api/ingest/chat-text`, `/api/ingest/image-ocr`, and
`/api/supplement/propose`, `/accept`, `/reject`, `/edit-later`.

Send the same key on a retry:

```text
Idempotency-Key: source-upload-2026-07-28-001
```

The key is scoped by HTTP method and path. JSON payloads are fingerprinted in
canonical key order; multipart boundaries are normalized. The persistent
ledger stores only the fingerprint and safe response replay data. Telegram
webhook requests are excluded because their `update_id` ledger owns that
contract.

### GET `/health`

Returns shallow process liveness without contacting PostgreSQL, Alembic,
pgvector, Redis, providers, or Notion.

Success response `200`:

```json
{
  "status": "ok"
}
```

### GET `/ready`

Checks database connectivity, current Alembic migration revision, the
PostgreSQL `vector` extension, and the mode-specific provider configuration.
The current `local` mode requires `OPENAI_API_KEY` and a reachable Redis/RQ
backend; `test`, `demo`, and `mock` modes skip those live dependencies.

Ready response `200`:

```json
{
  "status": "ready",
  "mode": "local",
  "checks": {
    "database": {"status": "ok", "detail": "database connection is available", "failure_reason": null},
    "migration": {"status": "ok", "detail": "database migration is current", "failure_reason": null},
    "vector": {"status": "ok", "detail": "pgvector extension is available", "failure_reason": null},
    "mode": {"status": "ok", "detail": "OpenAI embedding configuration is present", "failure_reason": null}
  }
}
```

Not-ready response `503` keeps the same body shape with `status` set to
`not_ready`. Deterministic `failure_reason` values include
`DATABASE_UNAVAILABLE`, `MIGRATION_NOT_CURRENT`,
`VECTOR_EXTENSION_UNAVAILABLE`, and `OPENAI_API_KEY_NOT_CONFIGURED`.
Exception text, URLs, credentials, and private content are not returned.

## Notion Index APIs

### POST `/api/notion/index/page`
Trigger one-page indexing from Notion read-only content.

Request:

```json
{
  "page_id": "page-nlp-week5"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 101,
  "status": "succeeded",
  "page_id": "page-nlp-week5",
  "page_title": "NLP Week 5",
  "notion_path": "Knowledge/NLP/Week5",
  "indexed_block_count": 18
}
```

Failure response example `404` (page not found):

```json
{
  "detail": {
    "error_code": "NOTION_PAGE_NOT_FOUND",
    "message": "Notion page is not found: page_id=page-nlp-week5",
    "failure_reason": "NOTION_PAGE_NOT_FOUND",
    "workflow_run_id": 101
  }
}
```

When the configured source is mock data or the requested page id is in the
fixed synthetic allowlist, a PostgreSQL-backed request fails before any page,
block, chunk, or vector persistence with `409`:

```json
{
  "detail": {
    "error_code": "SYNTHETIC_DATA_NOT_ALLOWED",
    "message": "Synthetic Notion data cannot be persisted to PostgreSQL",
    "failure_reason": "SYNTHETIC_DATA_NOT_ALLOWED",
    "workflow_run_id": 101
  }
}
```

Notes:
- Route must call orchestrator. Route does not call Notion directly.
- Orchestrator must call `ToolRegistry` -> `NotionReaderTool`.
- This endpoint does not perform Notion write operations.
- Workflow runs use `workflow_type=indexing`.

### POST `/api/notion/index/incremental`
Manual sync entrypoint for user manual Notion edits/deletes/merges.

Request:

```json
{
  "page_ids": ["page-nlp-week5", "page-ml-week2"]
}
```

Success response `200`:

```json
{
  "workflow_run_id": 202,
  "status": "succeeded",
  "sync_mode": "manual",
  "processed_page_count": 2,
  "indexed_pages": [
    {
      "page_id": "page-nlp-week5",
      "page_title": "NLP Week 5",
      "notion_path": "Knowledge/NLP/Week5",
      "indexed_block_count": 18
    },
    {
      "page_id": "page-ml-week2",
      "page_title": "ML Week 2",
      "notion_path": "Knowledge/ML/Week2",
      "indexed_block_count": 12
    }
  ]
}
```

Failure response example `404`:

```json
{
  "detail": {
    "error_code": "NOTION_PAGE_NOT_FOUND",
    "message": "Notion page is not found: page_id=missing-page",
    "failure_reason": "NOTION_PAGE_NOT_FOUND",
    "workflow_run_id": 202
  }
}
```

Notes:
- Route must call orchestrator. Route does not call Notion directly.
- Reconciliation uses page-level replacement.
- For each changed page, stale blocks/chunks are removed and current Notion page content is re-indexed.

### POST `/api/notion/index/full`

Discover accessible external Notion page ids and synchronously index each page
through the shared page-level replacement flow.

Request body: empty.

Success response `200`:

```json
{
  "workflow_run_id": 303,
  "status": "succeeded",
  "discovered_page_count": 2,
  "processed_page_count": 2,
  "indexed_pages": [
    {
      "page_id": "page-nlp-week5",
      "page_title": "NLP Week 5",
      "notion_path": "Knowledge/NLP/Week5",
      "indexed_block_count": 18
    }
  ]
}
```

Notes:
- Discovery and page reads are read-only Notion operations.
- The endpoint uses external Notion page ids; internal PostgreSQL ids are not
  sent to the reader tool.
- Repeating the operation replaces each discovered page's derived blocks and
  chunks, so stale content is removed without duplicate page rows.
- If one page fails, earlier page transactions remain committed and the
  workflow status records succeeded, failed, and remaining page ids.

### GET `/api/notion/index/status`

Get one indexing workflow status by `workflow_run_id`. If the query parameter
is omitted, return the latest indexing workflow.

Success response `200`:

```json
{
  "workflow_run_id": 303,
  "workflow_type": "indexing",
  "status": "succeeded",
  "failure_reason": null,
  "started_at": "2026-07-27T10:00:00+00:00",
  "finished_at": "2026-07-27T10:00:03+00:00",
  "metadata": {
    "operation": "index_full",
    "discovered_page_count": 2,
    "processed_page_count": 2,
    "page_ids": ["page-nlp-week5", "page-rag-basics"]
  }
}
```

Status reads PostgreSQL workflow state only and does not contact Notion. Its
metadata contains counts and identifiers, not page content.

## Ingestion Foundation API

### POST `/api/ingest/source`
Create one `source_documents` row from normalized source text.

Request:

```json
{
  "source_type": "pdf",
  "source_display_name": "lecture1.pdf",
  "raw_text": "Transformer notes from lecture 1"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 401,
  "status": "succeeded",
  "source_document_id": 1,
  "source_type": "pdf",
  "source_display_name": "lecture1.pdf",
  "content_hash": "4f9b56d58d6f1d4a2c7c87791ce58eceefc9c1be9b9c517f4f67de9f0f5b74f1"
}
```

Failure response example `400` (unsupported source type):

```json
{
  "detail": {
    "error_code": "INVALID_ARGUMENT",
    "message": "source_type must be one of: pdf, url, youtube, screenshot, chat_text",
    "failure_reason": "UNKNOWN_ERROR",
    "workflow_run_id": null
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator starts `workflow_type=ingestion` and persists source metadata through repository.
- Step 20 stores core fields: `source_type`, `source_display_name`, and `content_hash`.

### POST `/api/ingest/document`
Ingest one uploaded PDF document, extract text, and create one source document.

Request:
- `multipart/form-data`
- field: `document` (PDF file)

Success response `200`:

```json
{
  "workflow_run_id": 402,
  "status": "succeeded",
  "source_document_id": 2,
  "source_type": "pdf",
  "source_display_name": "lecture-week5.pdf",
  "content_hash": "b42b4ab40f62f4ec3f71d1677ad86a427b6996f71bf6200ff646862b5f37f06b"
}
```

Failure response example `422` (parse failed):

```json
{
  "detail": {
    "error_code": "PDF_PARSE_FAILED",
    "message": "No extractable text found in PDF",
    "failure_reason": "PDF_PARSE_FAILED",
    "workflow_run_id": 402
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator must call `ToolRegistry` -> `PDFParserTool`.
- This endpoint does not perform Notion write operations.
- Source display name is the uploaded filename.
- Upload limits are deterministic: PDF size is at most 10 MiB, page count is
  at most 100, and extracted text is at most 200,000 characters.
- The route accepts only `application/pdf` when a MIME type is supplied. It
  reads at most one byte beyond the configured size limit and rejects an
  over-limit request before creating a workflow.

### POST `/api/ingest/url`
Ingest one URL article, extract normalized text, and create one source document.

Request:

```json
{
  "url": "https://example.com/nlp-week5"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 403,
  "status": "succeeded",
  "source_document_id": 3,
  "source_type": "url",
  "source_display_name": "https://example.com/nlp-week5",
  "content_hash": "271f1c0e18d86bd53b4a46d2a7e05320b89432135b86564f3cd6de44db69b7f3"
}
```

Failure response example `422` (fetch or extraction failed):

```json
{
  "detail": {
    "error_code": "URL_FETCH_FAILED",
    "message": "No extractable text found in URL article",
    "failure_reason": "URL_FETCH_FAILED",
    "workflow_run_id": 403
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator must call `ToolRegistry` -> `URLArticleParserTool`.
- This endpoint does not perform Notion write operations.
- Source display name preserves the full URL string.
- The URL tool rejects embedded credentials, localhost, and non-public IPv4 or
  IPv6 DNS results; redirect targets are checked independently and the
  redirect chain is bounded.
- URL responses are limited to article text content types and 5 MiB of body
  bytes. Deterministic failures use `URL_SSRF_BLOCKED`,
  `URL_DNS_RESOLUTION_FAILED`, `URL_REDIRECT_LIMIT_EXCEEDED`,
  `URL_RESPONSE_TYPE_UNSUPPORTED`, or `URL_RESPONSE_TOO_LARGE` as applicable.

### POST `/api/ingest/youtube`
Ingest one YouTube video transcript and create one source document.

Request:

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 404,
  "status": "succeeded",
  "source_document_id": 4,
  "source_type": "youtube",
  "source_display_name": "YouTube transcript (dQw4w9WgXcQ)",
  "content_hash": "972ebd505260f1f7d55d5bdb4e08a4aa4f53b7900f87fbeb1d3e602dcc8f2e38"
}
```

Failure response example `422` (transcript unavailable):

```json
{
  "detail": {
    "error_code": "YOUTUBE_TRANSCRIPT_NOT_FOUND",
    "message": "No transcript found for this YouTube video",
    "failure_reason": "YOUTUBE_TRANSCRIPT_NOT_FOUND",
    "workflow_run_id": 404
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator must call `ToolRegistry` -> `YouTubeTranscriptTool`.
- This endpoint does not perform Notion write operations.
- MVP is transcript-only; no speech-to-text fallback for videos without transcript.

### POST `/api/ingest/chat-text`
Ingest pasted chat text and create one source document.

Request:

```json
{
  "chat_text": "Meeting notes about retrieval quality and attention concepts.",
  "source_display_name": "chat-2026-05-25"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 406,
  "status": "succeeded",
  "source_document_id": 6,
  "source_type": "chat_text",
  "source_display_name": "chat-2026-05-25",
  "content_hash": "cab93f7304657fce4ff3be8f36489039bc384c2d8f559550f8940af8601c7094"
}
```

Failure response example `400` (over MVP length limit):

```json
{
  "detail": {
    "error_code": "INVALID_ARGUMENT",
    "message": "chat_text exceeds MVP length limit (10000 chars)",
    "failure_reason": "UNKNOWN_ERROR",
    "workflow_run_id": null
  }
}
```

Notes:
- Route must call orchestrator only.
- This endpoint does not perform Notion write operations.
- MVP chat text length limit is `10000` characters.

### POST `/api/ingest/image-ocr`
Ingest multiple screenshots, run OCR in supplied order, and create one source document.

Request:
- `multipart/form-data`
- repeated field: `images` (image files in intended reading order)

Success response `200`:

```json
{
  "workflow_run_id": 405,
  "status": "succeeded",
  "source_document_id": 5,
  "source_type": "screenshot",
  "source_display_name": "Screenshot batch (3 images)",
  "content_hash": "30c8e52d4dc85f94fcdbdf6916696559f027c7af5269f78f8bdce840f31f586f"
}
```

Failure response example `422` (OCR failed):

```json
{
  "detail": {
    "error_code": "OCR_FAILED",
    "message": "No extractable text found in images",
    "failure_reason": "OCR_FAILED",
    "workflow_run_id": 405
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator must call `ToolRegistry` -> `ImageOCRTool`.
- This endpoint does not perform Notion write operations.
- Direct API uploads preserve supplied image order in OCR text concatenation.
  Telegram media groups use Telegram `message_id` order before the same batch
  OCR/proposal path.
- High-confidence browser chrome is removed before source persistence and
  proposal generation; the cleaned OCR is the sole proposal input.
- OCR accepts at most 10 images, 5 MiB per image, and 20 MiB per batch.
  Supported supplied MIME types are JPEG, PNG, WebP, GIF, BMP, and TIFF.
- The real Tesseract adapter rejects images over 40 million pixels before OCR;
  extracted OCR text is limited to 200,000 characters. Limit failures return
  deterministic `failure_reason` values such as `UPLOAD_TOO_LARGE`,
  `IMAGE_PIXEL_LIMIT_EXCEEDED`, and `EXTRACTED_TEXT_LIMIT_EXCEEDED`.

## Supplement Proposal API

### POST `/api/supplement/propose`
Generate one supplement proposal from a source document and create one `pending` change request.

Request:

```json
{
  "source_document_id": 6,
  "provider_name": "openai",
  "model": "gpt-4o-mini",
  "target_notion_page_id": "notion-page-external-6"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 501,
  "status": "succeeded",
  "change_request_id": 21,
  "change_request_status": "pending",
  "source_document_id": 6,
  "duplicate_detected": false,
  "duplicate_notion_path": null,
  "target_notion_page_id": "notion-page-external-6",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "token_input": 120,
  "token_output": 90
}
```

Success response `200` (duplicate knowledge path):

```json
{
  "workflow_run_id": 502,
  "status": "succeeded",
  "change_request_id": 22,
  "change_request_status": "pending",
  "source_document_id": 7,
  "duplicate_detected": true,
  "duplicate_notion_path": "Knowledge/NLP/Week5/Attention",
  "provider": null,
  "model": null,
  "token_input": null,
  "token_output": null
}
```

Failure response example `502` (invalid LLM proposal JSON):

```json
{
  "detail": {
    "error_code": "LLM_OUTPUT_INVALID",
    "message": "LLM output is not valid JSON",
    "failure_reason": "LLM_OUTPUT_INVALID",
    "workflow_run_id": 503
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator must call `ProviderRouter` for proposal generation and deterministic schema validation.
- Orchestrator creates one `change_requests` row with `status=pending`.
- This endpoint does not perform Notion write operations.
- Duplicate detection uses production chunk citations and stores a citation-first pending proposal instead of rewriting duplicated content.
- `target_notion_page_id` is an external Notion page id. The backend resolves
  it to an indexed page row before persistence. Unknown targets return
  `NOTION_PAGE_NOT_FOUND` and do not create a change request.

### GET `/api/supplement/pending`

List pending proposals for human review. This endpoint reads PostgreSQL only;
it does not call Notion or perform any write. The optional `limit` query
parameter is 1-100 and defaults to 50.

The response includes proposal content, citations, status, and the external
Notion target page id/title/path. Legacy proposals without explicit citation
entries receive a deterministic source-document citation fallback.

### GET `/api/supplement/{change_request_id}`

Return one reviewable proposal with the same content, citations, status, and
external target metadata as the pending list. Missing requests return
`CHANGE_REQUEST_NOT_FOUND`. Malformed stored proposal JSON fails closed with
`INVALID_PROPOSAL_PAYLOAD`.

### POST `/api/supplement/accept`
Accept one pending change request.

Request:

```json
{
  "change_request_id": 21,
  "reviewer": "reviewer-a"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 511,
  "status": "succeeded",
  "change_request_id": 21,
  "change_request_status": "accepted",
  "review_action": "accept",
  "reviewer": "reviewer-a",
  "reason": null
}
```

Failure response example `409` (write policy violation):

```json
{
  "detail": {
    "error_code": "WRITE_POLICY_VIOLATION",
    "message": "Accepted change request must include target_notion_page_id before Notion append",
    "failure_reason": "WRITE_POLICY_VIOLATION",
    "workflow_run_id": 516
  }
}
```

Failure response example `409` (invalid state transition):

```json
{
  "detail": {
    "error_code": "INVALID_STATE_TRANSITION",
    "message": "Only pending change requests can be reviewed: current_status=accepted",
    "failure_reason": "UNKNOWN_ERROR",
    "workflow_run_id": 512
  }
}
```

### POST `/api/supplement/reject`
Reject one pending change request.

Request:

```json
{
  "change_request_id": 22,
  "reviewer": "reviewer-b",
  "reason": "Out of scope for this page."
}
```

Success response `200`:

```json
{
  "workflow_run_id": 513,
  "status": "succeeded",
  "change_request_id": 22,
  "change_request_status": "rejected",
  "review_action": "reject",
  "reviewer": "reviewer-b",
  "reason": "Out of scope for this page."
}
```

### POST `/api/supplement/edit-later`
Keep one pending change request in pending state for later review.

Request:

```json
{
  "change_request_id": 23,
  "reviewer": "reviewer-c",
  "reason": "Need more context before final decision."
}
```

Success response `200`:

```json
{
  "workflow_run_id": 514,
  "status": "succeeded",
  "change_request_id": 23,
  "change_request_status": "pending",
  "review_action": "edit_later",
  "reviewer": "reviewer-c",
  "reason": "Need more context before final decision."
}
```

Failure response example `404` (change request not found):

```json
{
  "detail": {
    "error_code": "CHANGE_REQUEST_NOT_FOUND",
    "message": "Change request is not found: change_request_id=99999",
    "failure_reason": "CHANGE_REQUEST_NOT_FOUND",
    "workflow_run_id": 515
  }
}
```

Notes:
- Routes must call orchestrator only.
- Review endpoints enforce legal transitions for pending change requests.
- Accept path performs Step 31 follow-up workflow:
  - append accepted content to `AI Supplement Zone` through `NotionWriterTool`
  - trigger immediate page re-index with `sync_mode=auto_after_accept`
  - update change request status to `accepted` only after append + re-index succeed
- If append/re-index fails, accept workflow fails closed and change request stays `pending` for safe retry.
- Reject path performs no Notion write operations.

Step 30-31 notes:
- Step 30 introduces `NotionWriterTool` as a local append-only tool adapter.
- Step 31 wires accepted review -> append -> immediate page re-index.
- Step 70 adds `NotionAPIWriterClient` behind `NotionWriterTool`; it uses only
  read/locate, append, and bounded verification calls. Step 71 makes the
  mock/live reader and writer selection explicit and fail closed.

## QA API

### POST `/api/qa`
Run production RAG QA and return answer with citation paths.

Request:

```json
{
  "query": "Explain attention in week5 notes",
  "top_k": 5,
  "page_ids": ["page-nlp-week5"],
  "section_paths": ["Knowledge/NLP/Week5/Attention"],
  "source_kinds": ["notion"],
  "provider_name": "openai",
  "model": "gpt-4o-mini"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 301,
  "status": "succeeded",
  "answer": "Attention aligns query and key to weight values.",
  "insufficient_info": false,
  "retrieved_chunk_count": 2,
  "citations": [
    {
      "notion_path": "Knowledge/NLP/Week5/Attention",
      "page_id": "page-nlp-week5",
      "score": 0.934211
    }
  ],
  "provider": "openai",
  "model": "gpt-4o-mini",
  "token_input": 25,
  "token_output": 10
}
```

Insufficient-info response `200`:

```json
{
  "workflow_run_id": 302,
  "status": "succeeded",
  "answer": "I do not have enough information in production notes to answer safely.",
  "insufficient_info": true,
  "retrieved_chunk_count": 0,
  "citations": [],
  "provider": null,
  "model": null,
  "token_input": null,
  "token_output": null
}
```

Failure response example `500` (provider not configured):

```json
{
  "detail": {
    "error_code": "PROVIDER_NOT_FOUND",
    "message": "Provider is not registered: 'openai'",
    "failure_reason": "PROVIDER_NOT_FOUND",
    "workflow_run_id": 303
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator retrieves production chunks and calls `ProviderRouter`.
- `pending` and `rejected` content remains excluded by production retrieval policy.

## Telegram Gateway API

### POST `/api/telegram/webhook`
Handle one Telegram webhook update for `/help`, `/health`, `/pages`, `/ingest`,
`/ask`, `/accept`, and `/reject`.

Request example (`/help`):

```json
{
  "update_id": 1001,
  "message": {
    "message_id": 11,
    "chat": {
      "id": 555
    },
    "text": "/help"
  }
}
```

Success response `200`:

```json
{
  "workflow_run_id": 601,
  "status": "succeeded",
  "handled": true,
  "command": "help",
  "reply_text": "LearnLoop Agent commands: /start or /help, /pages, /ingest, /ask, /accept, /reject, /health",
  "telegram_message_id": 1,
  "skipped_reason": null,
  "source_document_id": null,
  "change_request_id": null,
  "source_type": null,
  "qa_workflow_run_id": null,
  "insufficient_info": null,
  "citations": [],
  "review_workflow_run_id": null,
  "review_action": null,
  "change_request_status": null,
  "target_set": false,
  "business_status": "succeeded",
  "callback_ack_status": "not_applicable",
  "preview_delivery_status": "not_applicable"
}
```

Request example (`/pages`):

```json
{
  "update_id": 1002,
  "message": {
    "message_id": 12,
    "chat": {"id": 555},
    "text": "/pages"
  }
}
```

The reply lists indexed external Notion page ids, titles, and paths, followed
by `/ingest --page <page_id>` usage. `/pages` is read-only.

Primary target-picker request (`/ingest` in a media caption):

```json
{
  "update_id": 1003,
  "message": {
    "message_id": 13,
    "chat": {"id": 555},
    "from": {"id": 777},
    "caption": "/ingest",
    "document": {
      "file_id": "pdf-file-1",
      "file_name": "lesson.pdf",
      "mime_type": "application/pdf"
    }
  }
}
```

The primary upload response acknowledges the file and sends an inline page
picker. Each parent and child page is a separate button labelled with its full
hierarchy path. The response has `change_request_id: null` and
`target_set: false` until the user selects a button. The button data is only
`ll:<opaque_token>`; the Redis session mapping restores the canonical external
page id after chat/user ownership checks.

Callback request after page selection:

```json
{
  "update_id": 1009,
  "callback_query": {
    "id": "callback-1",
    "from": {"id": 777},
    "data": "ll:<opaque_token>",
    "message": {"message_id": 14, "chat": {"id": 555}}
  }
}
```

The callback creates one target-aware `pending` proposal, returns
`target_set: true`, and sends a preview with inline Accept, Reject, and Change
target buttons. Callback Accept is explicit and delegates to the same review
orchestrator as `/accept`; it never appends automatically at proposal time.

Callback button data remains `ll:<opaque_token>`. The server-side mapping has
the following allowlisted semantic fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `callback_kind` | `review`, `picker` | Dispatch family; review is checked first. |
| `action` | `accept`, `reject`, `change_target`, `select_target`, `change_target_select` | Specific operation. |
| `change_request_id` | positive integer or null | Required for review actions. |
| `target_notion_page_id`, `target_notion_path` | server-resolved values | Required only for page-selection actions. |

Redis mappings written before `callback_kind` existed are normalized from the
allowlisted action. Unknown or mismatched mappings fail closed. A
`ready_for_review` or `proposal_created` upload-session state is presentation
state only and cannot route a valid review Accept to the page-picker branch.
The normal Accept target is resolved from the change request; the
`LEARNLOOP_NOTION_CANARY_PAGE_ID` environment variable is not consulted by
normal Telegram review callbacks.

For a valid callback, the backend first validates callback ownership and the
mapping family. Review actions dispatch before generic picker/session actions.
For a page-picker callback, it also validates session state and selected page.
Then it calls Telegram `answerCallbackQuery` before OCR, provider, or proposal
work. The response and workflow metadata expose `business_status`,
`callback_ack_status`, and `preview_delivery_status`. A transient
acknowledgement failure is classified as `TELEGRAM_CALLBACK_ACK_FAILED` and
does not fail a legal review/business workflow. A preview `send_message` failure is classified as
`TELEGRAM_PREVIEW_DELIVERY_FAILED`; the pending change request remains and the
user receives a short recovery message.

Inline Accept delegates to `TelegramReviewOrchestrator` and the existing
`SupplementReviewOrchestrator.accept_change_request()` path: pending
validation, AI Supplement Zone append, durable identity verification, page
re-index, accepted transition, then the Telegram success reply. Inline Reject
uses the same review orchestrator and performs no Notion write. Inline Change
target only opens or applies the target picker. Duplicate `update_id` delivery
replays the stored outcome and never repeats OCR, LLM generation, append, or
change-request creation.

Request example (`/ingest` + PDF):

```json
{
  "update_id": 1004,
  "message": {
    "message_id": 14,
    "chat": {
      "id": 555
    },
    "caption": "/ingest --page page-nlp-week5",
    "document": {
      "file_id": "pdf-file-1",
      "file_name": "lesson.pdf",
      "mime_type": "application/pdf"
    }
  }
}
```

Success response `200` (`/ingest`):

```json
{
  "workflow_run_id": 604,
  "status": "succeeded",
  "handled": true,
  "command": "ingest",
  "reply_text": "Ingestion succeeded (source_type=pdf, source_document_id=12, change_request_id=34, status=pending).",
  "telegram_message_id": 2,
  "skipped_reason": null,
  "source_document_id": 12,
  "change_request_id": 34,
  "source_type": "pdf",
  "target_notion_page_id": "page-nlp-week5",
  "qa_workflow_run_id": null,
  "insufficient_info": null,
  "citations": [],
  "review_workflow_run_id": null,
  "review_action": null,
  "change_request_status": null,
  "target_set": true
}
```

For a targeted ingest, the Telegram reply also includes a deterministic
proposal preview with title, summary, concepts, notes, citations, target page,
and `/accept <change_request_id>` usage. The change request remains `pending`
until a human sends `/accept`.

Request example (`/ask` with section scope):

```json
{
  "update_id": 1005,
  "message": {
    "message_id": 15,
    "chat": {
      "id": 555
    },
    "text": "/ask --section Knowledge/NLP/Week5/Attention Explain attention"
  }
}
```

Success response `200` (`/ask`):

```json
{
  "workflow_run_id": 605,
  "status": "succeeded",
  "handled": true,
  "command": "ask",
  "reply_text": "Attention aligns query and key to weight values.\n\nNotion citations:\n- Knowledge/NLP/Week5/Attention",
  "telegram_message_id": 3,
  "skipped_reason": null,
  "source_document_id": null,
  "change_request_id": null,
  "source_type": null,
  "qa_workflow_run_id": 606,
  "insufficient_info": false,
  "citations": [
    "Knowledge/NLP/Week5/Attention"
  ],
  "review_workflow_run_id": null,
  "review_action": null,
  "change_request_status": null
}
```

Request example (`/accept`):

```json
{
  "update_id": 1006,
  "message": {
    "message_id": 16,
    "chat": {
      "id": 555
    },
    "text": "/accept 34"
  }
}
```

Success response `200` (`/accept`, after append + re-index):

```json
{
  "workflow_run_id": 607,
  "status": "succeeded",
  "handled": true,
  "command": "accept",
  "reply_text": "Change request 34 accepted. Appended to AI Supplement Zone and page re-index completed.",
  "telegram_message_id": 4,
  "skipped_reason": null,
  "source_document_id": null,
  "change_request_id": 34,
  "source_type": null,
  "qa_workflow_run_id": null,
  "insufficient_info": null,
  "citations": [],
  "review_workflow_run_id": 608,
  "review_action": "accept",
  "change_request_status": "accepted"
}
```

Request example (`/reject`):

```json
{
  "update_id": 1007,
  "message": {
    "message_id": 17,
    "chat": {
      "id": 555
    },
    "text": "/reject 35 Out of scope for this note"
  }
}
```

Success response `200` (`/reject`, no Notion write):

```json
{
  "workflow_run_id": 609,
  "status": "succeeded",
  "handled": true,
  "command": "reject",
  "reply_text": "Change request 35 rejected. No Notion write was performed.",
  "telegram_message_id": 5,
  "skipped_reason": null,
  "source_document_id": null,
  "change_request_id": 35,
  "source_type": null,
  "qa_workflow_run_id": null,
  "insufficient_info": null,
  "citations": [],
  "review_workflow_run_id": 610,
  "review_action": "reject",
  "change_request_status": "rejected"
}
```

Skipped response `200` (no text message):

```json
{
  "workflow_run_id": 602,
  "status": "succeeded",
  "handled": false,
  "command": null,
  "reply_text": null,
  "telegram_message_id": null,
  "skipped_reason": "NO_TEXT_MESSAGE",
  "source_document_id": null,
  "change_request_id": null,
  "source_type": null,
  "qa_workflow_run_id": null,
  "insufficient_info": null,
  "citations": [],
  "review_workflow_run_id": null,
  "review_action": null,
  "change_request_status": null
}
```

Failure response example `503` (Telegram bot token not configured):

```json
{
  "detail": {
    "error_code": "TELEGRAM_NOT_CONFIGURED",
    "message": "Telegram bot token is not configured. Set TELEGRAM_BOT_TOKEN.",
    "failure_reason": "TELEGRAM_NOT_CONFIGURED",
    "workflow_run_id": 603
  }
}
```

Notes:
- Route must call orchestrator only.
- A non-null Telegram `update_id` is claimed in the persistent ledger before
  command work starts. Duplicate updates never send a second Telegram reply.
- With Redis configured, command work starts in `scripts/run_worker.py` rather
  than in the webhook request. The worker consumes the `telegram` queue and
  applies bounded retries.
- Worker startup derives the repository root from its own file path and
  fail-fast resolves `src.worker.telegram.process_telegram_webhook_job` through
  RQ. The API and worker therefore use the same fresh-process import path.
- RQ worker selection is explicit and platform-aware: default `auto` selects
  `SpawnWorker` on Darwin/macOS and `Worker` on Linux. The macOS fork-based
  worker is rejected; the webhook remains asynchronous through Redis/RQ.
- Duplicate running updates return `202`; duplicate succeeded and failed
  updates replay the original result or error. Updates without `update_id` are
  accepted for backward compatibility without deduplication.
- `/pages` lists indexed external Notion page ids, titles, and paths for target selection.
- `/ingest --page <page_id>` creates a pending proposal targeted to that external page and returns a deterministic proposal preview with citations and `/accept` usage.
- A selected page proposal stores exactly
  `<indexed canonical notion_path>/AI Supplement Zone` as `proposal.target_path`.
  `LLM_OUTPUT_INVALID` is returned when the model selects another page,
  omits the supplement zone, or cannot satisfy the contract; Telegram sends a
  short redacted callback failure instead of remaining silent.
- Orchestrator sends reply through `ToolRegistry` -> `TelegramBotTool` (`send_message`).
- `/ingest` downloads Telegram files through `ToolRegistry` -> `TelegramBotTool` (`download_file`).
- `/ask` syntax is
  `/ask [--page <page_id>] [--section <notion/path>] <question>`.
- `/ask` delegates to the existing QA orchestrator and returns Notion path citations.
- Scope flags can be repeated. Inline forms such as `--page=page-id` and
  `--section=Knowledge/NLP/Week5` are also accepted.
- `/accept <change_request_id>` delegates to the existing accept workflow and
  replies only after append to `AI Supplement Zone` and immediate page re-index.
- `/reject <change_request_id> <reason>` delegates to the existing reject
  workflow and performs no Notion write or page re-index.
- Telegram chat id becomes the deterministic reviewer identity.
- Inline review buttons use opaque Redis-backed callback tokens and are the
  primary proposal review UX. Text commands remain supported as fallback.
- Route and orchestrator do not call Telegram API directly.
- Within one Telegram update, photo entries are resolution variants of one
  image and the gateway selects the largest variant. Multiple updates sharing
  `media_group_id` are aggregated in a chat/user-scoped Redis session by the
  queued settle job; the session TTL and atomic claims prevent cross-user
  reuse and duplicate OCR/proposal/preview work.
- Expired sessions, missing media, invalid callbacks, and unavailable queue
  paths return explicit deterministic errors. A targetless proposal never
  receives an Accept prompt.
- Invalid callback/session failures expose only redacted messages and specific
  `failure_reason` values such as `INVALID_CALLBACK`,
  `UPLOAD_SESSION_EXPIRED`, or `UPLOAD_SESSION_INVALID`.
- A duplicate `update_id` replays the terminal ledger result/failure and does
  not repeat OCR, LLM proposal generation, source-document creation, or
  change-request creation. Preview recovery is an explicit operation on the
  existing pending proposal.
- `LLM_OUTPUT_INVALID` Telegram callbacks receive the fixed short message
  `Proposal validation failed. Please upload the file again.`; model output
  and canonical paths are not sent to the user.
- `/ingest` creates `pending` change requests only; Notion append remains in accept workflow.
- Telegram QA uses production Notion chunks only; pending and rejected proposals remain excluded.
