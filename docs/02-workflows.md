# 02 Workflows

## Purpose
This document defines indexing, ingestion, review, append, sync, and QA workflows.

## Status
Draft

This document will be expanded in later steps.

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
-> Apply idempotency key per page/change request
-> Append fixed supplement lines only
-> Return append metadata (target path, block count, idempotent replay flag)
```

Rules:
- The tool exposes append-only behavior; there is no update or delete operation.
- The append target must stay under `AI Supplement Zone`.
- Existing page content stays unchanged; only new supplement entries are appended.
- Idempotency prevents duplicate append entries on retry with the same idempotency key.

## Accept + Append + Re-index Workflow (Step 31)

```text
POST /api/supplement/accept
-> Validate request payload
-> Start workflow_run (workflow_type=supplement)
-> Load change request
-> Enforce legal transition from pending state
-> Validate accepted write preconditions (target page + proposal payload)
-> Append to AI Supplement Zone through NotionWriterTool
-> Trigger immediate page re-index (sync_mode=auto_after_accept)
-> Update change request status to accepted
-> Mark workflow succeeded
```

Failure path:
- If target page is missing, fail closed with `WRITE_POLICY_VIOLATION`.
- If append fails or re-index fails, mark workflow failed and keep change request `pending` for safe retry.

Rules:
- Accept path must follow `Change Request -> Human Accept -> Append to AI Supplement Zone`.
- Accepted status is committed only after append and re-index both succeed.
- Reject and edit-later paths keep Step 29 behavior and do not call Notion write adapters.

## Telegram Entrypoint Workflow (Step 32)

```text
POST /api/telegram/webhook
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

## Telegram Ingestion Workflow (Step 33)

```text
POST /api/telegram/webhook
-> Parse /ingest command or media upload intent
-> Download Telegram file bytes through ToolRegistry -> TelegramBotTool (download_file)
-> Route to ingestion orchestrator:
   - PDF document -> DocumentIngestionOrchestrator
   - screenshot batch -> ImageOCRIngestionOrchestrator
-> Create pending change request through SupplementProposeOrchestrator
-> Send ingestion summary reply through ToolRegistry -> TelegramBotTool (send_message)
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
