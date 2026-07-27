# 02 Workflows

## Purpose
This document defines indexing, ingestion, review, append, sync, and QA workflows.

## Status
Draft

## Current Verification Boundary

The workflows below define implemented orchestration contracts, but most
external boundaries are currently verified with fake or in-memory adapters.
The runtime selects mock/in-memory Notion clients by default, or the live
reader and append-only writer adapters when `NOTION_BACKEND=live` and
`NOTION_TOKEN` are configured. There is no background worker and no complete
live Telegram flow. Deterministic Telegram tests cover page selection,
proposal preview, and select-to-accept; live Telegram delivery remains opt-in.

The deterministic write policy, state-transition, transaction, RAG-exclusion,
and retry rules remain mandatory when live adapters are added.

This document will be expanded in later steps.

## Reviewable Proposal Workflow (Step 72)

```text
GET /api/supplement/pending
-> Read pending change requests from PostgreSQL
-> Parse stored proposal content deterministically
-> Resolve stored target FK to the external Notion page id
-> Return proposal content, source citation fallback, and target metadata

GET /api/supplement/{change_request_id}
-> Read one change request and its target metadata
-> Return the same reviewable proposal detail
```

Rules:
- These read APIs do not call Notion and do not write to Notion.
- A proposal target supplied to `POST /api/supplement/propose` is an external
  Notion page id. The backend resolves it to the internal indexed page row
  before persistence; unknown targets fail closed with `NOTION_PAGE_NOT_FOUND`.
- Legacy proposals without explicit citation entries receive a deterministic
  source-document citation fallback for human review.
- Pending proposals remain pending until a separate human review action calls
  the existing accept/reject/edit-later flow.

What belongs here:
- Workflow state transitions.
- Success and failure paths.
- Retry and idempotency behavior.

## Supplement Proposal Workflow (Step 28)

```text
POST /api/supplement/propose
-> Validate request payload
-> Start workflow_run (workflow_type=supplement)
-> Load source document
-> Run duplicate check on production chunks
-> If duplicate: build citation-first proposal
-> Else: call ProviderRouter and validate proposal JSON
-> Create change request with status=pending
-> Mark workflow succeeded
```

Failure path:
- If provider output JSON is invalid, fail workflow with `LLM_OUTPUT_INVALID`.
- If source document is missing, fail workflow with deterministic error and workflow id.

State notes:
- New proposals are saved as `pending` change requests.
- Proposal generation does not write to Notion.
- When the workflow reaches the LLM path, workflow metadata records
  `provider_name`, `model`, `prompt_id`, and `prompt_version`.

## Supplement Review Workflow (Step 29)

```text
POST /api/supplement/accept|reject|edit-later
-> Validate request payload
-> Start workflow_run (workflow_type=supplement)
-> Load change request
-> Enforce legal transition from pending state
-> Update change request status
-> Mark workflow succeeded
```

Legal transitions:
- `pending -> accepted`
- `pending -> rejected`
- `pending -> pending` (edit-later)

Rules:
- Reject stores decision reason in workflow metadata and keeps Notion unchanged.
- Review endpoints do not call Notion write adapters in Step 29.

## Safe Append Tooling Workflow (Step 30)

```text
NotionWriterTool (local tool adapter)
-> Validate append arguments (page_id/change_request_id/topic/source/summary/concepts/notes)
-> Build append target under AI Supplement Zone
-> Apply durable identity `change-request-<id>` per page/change request
-> Append the identity line plus fixed supplement content lines
-> Return append metadata (target path, block count, idempotent replay flag)
```

Rules:
- The tool exposes append-only behavior; there is no update or delete operation.
- The append target must stay under `AI Supplement Zone`.
- Existing page content stays unchanged; only new supplement entries are appended.
- The visible identity is the durable idempotency record; retry detection must
  not depend only on in-memory client state.
- The writer performs bounded read-after-write verification before returning
  append success. An unverified append fails closed for safe retry.

## Accept + Append + Re-index Workflow (Step 31)

```text
POST /api/supplement/accept
-> Validate request payload
-> Start workflow_run (workflow_type=supplement)
-> Load change request
-> Enforce legal transition from pending state
-> Validate accepted write preconditions (target page + proposal payload)
-> Append to AI Supplement Zone through NotionWriterTool
-> Verify append visibility by durable change-request identity
-> Prepare the page re-index snapshot outside the DB transaction
-> Open one business transaction
   - Reload and lock the change request with `SELECT ... FOR UPDATE`
   - Revalidate that status is still `pending`
   - Persist page/block/chunk replacement
   - Update change request status to `accepted`
-> Mark workflow succeeded
```

Failure path:
- If target page is missing, fail closed with `WRITE_POLICY_VIOLATION`.
- If append fails, append visibility cannot be verified, or re-index fails,
  mark workflow failed and keep change request `pending` for safe retry.
- A retry after a durable append reuses the existing Notion supplement and
  never creates a duplicate entry.

Rules:
- Accept path must follow `Change Request -> Human Accept -> Append to AI Supplement Zone`.
- Accepted status is committed only after append visibility is verified and
  the page re-index mutation set commits in the same business transaction.
- Concurrent accept attempts revalidate `pending` while holding the row lock;
  only one attempt may commit `accepted`.
- Reject and edit-later paths keep Step 29 behavior and do not call Notion write adapters.

## Workflow Audit Update Reconciliation (Step 64)

Final workflow audit updates are a separate boundary from business work:

```text
Business transaction commits
-> Attempt final workflow audit update
-> If audit update fails, keep workflow_run status=running
-> Emit WORKFLOW_AUDIT_UPDATE_FAILED
-> Reconcile the stale running workflow explicitly when the final outcome is known
```

Rules:
- A final audit update failure must not rollback or rerun committed business work.
- A final audit update failure must not be routed through the business failure
  handler or mark the workflow failed after business success.
- If business work fails first, the original business exception remains the
  surfaced error even when the failure-audit update also fails.
- `reconcile_stale_running_workflow()` only transitions a workflow currently in
  `running` to an explicitly supplied terminal status.

## Telegram Entrypoint Workflow (Step 32)

```text
POST /api/telegram/webhook
-> Validate webhook secret and allowed chat policy
-> Validate webhook payload
-> Start workflow_run (workflow_type=telegram)
-> Parse command from message text
-> Build deterministic reply text for /help or /health
-> Send reply through ToolRegistry -> TelegramBotTool
-> Mark workflow succeeded
```

Failure path:
- If Telegram bot token is not configured, fail with `TELEGRAM_NOT_CONFIGURED`.
- If Telegram API send fails, fail with `TELEGRAM_SEND_FAILED`.

Rules:
- API route calls orchestrator only.
- Route and orchestrator do not call Telegram API SDK/client directly.
- Bot gateway keeps no ingestion/QA/review business logic in Step 32.
- Secret and allowed-chat checks happen before a Telegram workflow starts; a
  rejected caller does not create a workflow run or send a reply.

## Telegram Update Idempotency Workflow (Step 75)

```text
POST /api/telegram/webhook with update_id
-> Validate webhook trust boundary
-> Atomically claim unique update_id in telegram_update_ledger
-> If running: return 202 processing response
-> If succeeded/failed: replay stored result or failure
-> If owner: run the Telegram gateway workflow once
-> Persist succeeded/failed outcome for future replay
```

Rules:
- The ledger claim is committed before ingestion, review, provider, or Telegram
  send work begins.
- A unique-constraint race has one owner; the other request never runs the
  command or sends a reply.
- A failed update is replayed as failed rather than automatically retried;
  recovery/reconciliation remains an explicit operator action.
- Updates without `update_id` retain the pre-Step-75 non-idempotent behavior.

## API Mutation Idempotency Workflow (Step 76)

```text
POST /api/ingest/* or /api/supplement/* with Idempotency-Key
-> Canonicalize request payload and compute fingerprint
-> Atomically claim (method:path, Idempotency-Key) in api_idempotency_records
-> If running: return 202 processing response
-> If succeeded/failed: replay persisted response
-> If fingerprint differs: return 409 conflict
-> If owner: run the mutation once and persist its response
```

Rules:
- The claim is committed before source persistence, proposal generation, or
  review mutation work starts.
- JSON object key ordering does not change the fingerprint; multipart boundary
  values are normalized so equivalent uploads can be retried safely.
- Only safe response headers are replayed. Request payloads are represented by
  a digest in the ledger and are not logged as raw content.
- The middleware scope intentionally excludes Telegram, Notion indexing, QA,
  and GET routes. Telegram uses its `update_id` ledger.

## Telegram Ingestion Workflow (Step 33)

```text
POST /api/telegram/webhook
-> Parse /ingest command or media upload intent
-> Resolve optional `/ingest --page <external_page_id>` target
-> Download Telegram file bytes through ToolRegistry -> TelegramBotTool (download_file)
-> Route to ingestion orchestrator:
   - PDF document -> DocumentIngestionOrchestrator
   - screenshot batch -> ImageOCRIngestionOrchestrator
-> Create pending change request through SupplementProposeOrchestrator
-> Read stored proposal detail and send deterministic preview through
   ToolRegistry -> TelegramBotTool (send_message)
-> Mark workflow succeeded
```

Failure path:
- If Telegram file download fails, fail with `TELEGRAM_FILE_DOWNLOAD_FAILED`.
- If PDF/OCR parsing fails, reuse deterministic ingestion failures (`PDF_PARSE_FAILED`, `OCR_FAILED`).
- If proposal generation fails, reuse supplement proposal deterministic failures (`LLM_OUTPUT_INVALID`, `PROVIDER_NOT_FOUND`, `LLM_PROVIDER_ERROR`).

Rules:
- Route and gateway orchestrator still call Telegram only through `ToolRegistry`.
- PDF and screenshot ingestion reuse existing ingestion/propose orchestrators; no duplicate business logic in API route.
- Screenshot batch upload creates one `source_documents` row with `source_type=screenshot`.
- Step 33 still follows safe write policy: create `pending` change request only; no Notion append in this workflow.
- `/ingest --page <external_page_id>` resolves the target against indexed
  Notion pages; the target is optional for backward compatibility, but accept
  still fails closed when no target is present.

## Telegram Page and Review Workflow (Step 73)

```text
POST /api/telegram/webhook with `/pages`
-> Read indexed Notion page ids through NotionPageRepository
-> Send deterministic page list and target-aware usage

POST /api/telegram/webhook with `/ingest --page <page_id>` and media
-> Create pending proposal for the selected external target
-> Send proposal preview with summary, notes, citations, and review commands

POST /api/telegram/webhook with `/accept <change_request_id>`
-> Reuse SupplementReviewOrchestrator
-> Append to AI Supplement Zone and immediately re-index
-> Send success reply only after the business workflow succeeds
```

Rules:
- `/pages` is read-only and does not contact the Notion writer.
- Preview content is read from the stored pending proposal; preview does not
  accept, append, or expose pending content to production RAG.
- Telegram chat id remains the deterministic reviewer identity.

## Telegram QA Workflow (Step 34)

```text
POST /api/telegram/webhook
-> Parse /ask command and optional --page / --section scope flags
-> Delegate to TelegramQAOrchestrator
-> Reuse QAOrchestrator for production chunk retrieval and grounded answer generation
-> Format answer with deterministic Notion path citations
-> Send reply through ToolRegistry -> TelegramBotTool (send_message)
-> Mark workflow succeeded
```

Failure path:
- Invalid scope flags fail with `INVALID_ARGUMENT`.
- Missing providers and provider failures reuse QA workflow failures
  (`PROVIDER_NOT_FOUND`, `LLM_PROVIDER_ERROR`, `LLM_OUTPUT_INVALID`).
- The Telegram gateway workflow fails when delegated QA fails.

Rules:
- Scope syntax is
  `/ask [--page <page_id>] [--section <notion/path>] <question>`.
- `/ask` without a question returns a usage reply and does not start a QA workflow.
- Telegram QA reuses `QAOrchestrator`; the gateway contains no retrieval or provider logic.
- Production retrieval remains Notion-only and keeps pending/rejected proposals excluded.
- Telegram workflow metadata records citation count only, not question text or citation paths.
- The delegated QA workflow records `provider_name`, `model`, `prompt_id`, and
  `prompt_version` in its own workflow metadata.
- When the delegated LLM call returns token usage, the QA workflow metadata also
  records `token_input`, `token_output`, and `estimated_cost`.

## Telegram Review Workflow (Step 35)

```text
POST /api/telegram/webhook
-> Parse /accept or /reject command
-> Delegate to TelegramReviewOrchestrator
-> Reuse SupplementReviewOrchestrator
-> For accept:
   - validate pending state and write preconditions
   - append through NotionWriterTool to AI Supplement Zone
   - immediately re-index page
   - mark change request accepted
-> For reject:
   - mark pending change request rejected
   - perform no Notion write or re-index
-> Send deterministic result reply through ToolRegistry -> TelegramBotTool
-> Mark Telegram workflow succeeded
```

Failure path:
- Invalid change request ids fail with `INVALID_ARGUMENT`.
- Missing change requests and illegal transitions reuse review workflow failures
  (`CHANGE_REQUEST_NOT_FOUND`, `INVALID_STATE_TRANSITION`).
- Accept write-policy violations fail closed with `WRITE_POLICY_VIOLATION`;
  the change request stays `pending` and no Telegram success reply is sent.

Rules:
- Command syntax is `/accept <change_request_id>` and
  `/reject <change_request_id> <reason>`.
- Telegram chat id is recorded as the deterministic reviewer identity.
- Telegram review reuses `SupplementReviewOrchestrator`; the gateway contains
  no state-transition or Notion write logic.
- Accept follows `Change Request -> Human Accept -> Append to AI Supplement Zone`
  and replies only after immediate page re-index succeeds.
- Reject never calls Notion writer or page re-index.
- Telegram gateway metadata records review action/status/workflow id only, not
  the reject reason.
- Inline review buttons remain deferred.

## Same-page Snapshot Safety (Step 62)

- The reader includes the Notion page `last_edited_time` in every page snapshot
  when the source provides it.
- Page persistence takes a PostgreSQL transaction-scoped advisory lock keyed by
  the stable Notion page id before checking the stored snapshot.
- A prepared snapshot with an older non-NULL `last_edited_time` fails with
  `STALE_PAGE_SNAPSHOT` before blocks or chunks are replaced.
- Legacy rows with a NULL timestamp accept the first timestamped snapshot;
  timestamp-less legacy readers do not erase an existing timestamp.
- SQLite test backends skip the PostgreSQL-only advisory lock but exercise the
  same deterministic stale-snapshot comparison.
