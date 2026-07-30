# 08 Observability

## Purpose
This document defines logs, metrics, traces, cost tracking, and failure_reason taxonomy.

## Status
Draft

This document will be expanded in later steps.

What belongs here:
- Structured logging schema.
- Metrics definitions.
- Workflow tracing and cost reporting.

## Current Implementation Status

Confirmed:

- Structured request/workflow logs and secret/raw-text redaction exist.
- LLM and embedding metadata can record per-workflow token and estimated cost.
- Final workflow audit-update failure has a deterministic reconciliation
  service method.
- Telegram update idempotency persists `running`, `succeeded`, and `failed`
  outcomes without storing raw request payloads or secrets in logs.
- API ingestion and supplement mutation idempotency persists only a request
  scope, payload digest, status, and safe response replay fields. It records
  `running`, `succeeded`, and `failed` outcomes without raw request content.

Missing from the current operator surface:

- Log persistence/rotation, tracing backend, and recovery dashboards.

Implemented in Step 84:

- Public Prometheus-compatible `/metrics` for workflow counts, stale-running
  counts, known daily cost, unknown-cost count, and configured budget alerts.
- Protected workflow status list/detail and cost-budget API surfaces.
- Protected stale-running reconciliation API plus a dry-run-by-default CLI;
  mutation requires `--apply` and only stale `running` workflows qualify.
- Recursive workflow metadata redaction for private source text and secrets.

The `/health` endpoint is liveness only and always reports `ok`; it must not be
used as release-readiness evidence. `/ready` is the dependency-aware readiness
surface and returns 503 when database, migration, pgvector, or required
mode-specific provider configuration is unavailable.

## Readiness Checks

- `database` runs a safe `SELECT 1` through the database readiness probe.
- `migration` compares the `alembic_version` table with the repository's
  migration heads.
- `vector` checks for the PostgreSQL `vector` extension.
- `mode` requires OpenAI embedding configuration in `local` mode and skips the
  live provider requirement in `test`, `demo`, and `mock` modes.
- Readiness failures use deterministic `failure_reason` values and never
  return raw driver exceptions, connection URLs, or secret values.
- `queue` checks the Redis/RQ backend through `QueueClient.is_available()`.
  Local mode reports `REDIS_URL_NOT_CONFIGURED` when no queue URL is supplied
  and `REDIS_UNAVAILABLE` when Redis cannot answer `PING`. Test/demo/mock modes
  may omit the queue dependency.

## Step 88 Telegram Worker Import Boundary

- The queued Telegram callable is the module-level path
  `src.worker.telegram.process_telegram_webhook_job`.
- `scripts/run_worker.py` adds the repository root derived from its own file
  location to `sys.path`; it does not rely on the current working directory or
  a machine-specific absolute path.
- Before connecting to or consuming the RQ queue, worker startup resolves the
  canonical path through RQ `import_attribute()` and compares it with the
  actual callable. Failure is fail-fast and safe to diagnose without running
  Telegram work.
- RQ 2.8.0 supports `SpawnWorker`. The explicit worker-class policy selects
  `SpawnWorker` on Darwin/macOS and the standard `Worker` on Linux by default;
  selecting the fork-based worker on macOS fails closed. Startup logs emit
  only the selected class name (`SpawnWorker` or `Worker`).
- A previously claimed `running` update is not re-run by this fix. The ledger
  remains the source of truth; operators inspect the redacted ledger/job state
  and use an explicit recovery decision rather than raw SQL or replay.

Telegram ingestion observability:
- Workflow metadata records safe operation classes, counts, target-set state,
  and callback/review action status only. It does not record callback tokens,
  canonical page ids, upload bytes, captions, OCR text, or proposal source
  content.
- Redis upload sessions and callback mappings are TTL-bound and scoped by chat
  and user. Their state is not emitted into user-facing logs.
- Duplicate update, settle, target, and preview claims are observable through
  terminal status/failure outcomes without exposing private media or Notion
  content.

## Workflow Metadata Notes

- LLM-backed workflows record `provider_name`, `model`, `prompt_id`, and
  `prompt_version` and `prompt_safety_version` in workflow metadata JSON.
- Prompt templates live under `docs/prompts/*.md` and become runtime inputs
  only when code explicitly loads them.
- Prompt version tracking must be deterministic so prompt changes can be tied
  to workflow results during debugging and evaluation.
- QA and supplement proposal workflows also record `token_input`,
  `token_output`, and `estimated_cost` when token usage is available.
- Cost estimates are computed from a small model-pricing catalog inside the
  backend service layer. Unknown models return `estimated_cost=null` instead of
  guessing.
- Indexing workflows that generate chunk vectors should record
  `embedding_provider`, `embedding_model`, `embedding_dimensions`,
  `embedding_token_input`, and `embedding_estimated_cost`.
- Manual incremental sync should aggregate embedding token and cost metadata
  across all successfully re-indexed pages in the workflow.
- Each incremental-sync page is committed through its own short business
  transaction, so an earlier successful page remains committed when a later
  page fails.
- Failed incremental-sync workflow metadata records
  `succeeded_page_ids`, `failed_page_id`, and `remaining_page_ids`, plus their
  counts and the zero-based `failed_page_index`. These fields contain page
  identifiers only, not page content.
- Full-index workflow metadata records `discovered_page_count`,
  `processed_page_count`, and external `page_ids`; a failed full run records
  succeeded, failed, and remaining page identifiers only.
- `GET /api/notion/index/status` returns persisted indexing workflow state and
  safe metadata without re-reading Notion or exposing page content.
- A stale prepared page snapshot fails with `STALE_PAGE_SNAPSHOT`; this is a
  deterministic concurrency-safety failure and is recorded before page block
  or chunk replacement begins.
- Final workflow audit updates are separate from business commits. If one fails,
  the workflow remains `running`, the service emits a sanitized
  `workflow_audit_update_failed` event with `workflow_id`, `audit_action`, and
  `audit_status`, and the business result is not retried.
- `WORKFLOW_AUDIT_UPDATE_FAILED` is returned as a distinct service/API error.
  Operators reconcile the stale running workflow only after confirming the
  business outcome.

## Step 84 Operator Contract

- `WORKFLOW_STALE_AFTER_SECONDS` defaults to `3600` and controls the stale flag
  and reconciliation guard.
- `MAX_WORKFLOW_COST_USD` and `MAX_DAILY_COST_USD` are optional positive USD
  thresholds. Missing thresholds report `unconfigured`; exceeded thresholds
  report `exceeded`; a configured threshold with unknown recorded pricing
  reports `unknown`.
- `/metrics` failures return a fixed redacted failure metric and never expose
  database driver or provider exception text.
- Status metadata is recursively redacted for `raw_text`, `source_text`, API
  keys, tokens, authorization values, and webhook secrets.

## Step 85 Recovery Evidence

- Backup/restore evidence contains fixed check names, migration revision,
  readiness status, re-index counts, and scoped citation counts only.
- The restore drill never reports database URLs, passwords, driver exception
  text, Notion page ids, or private source content.
- Recovery pauses mutations while append identity, workflow outcome, or
  database migration state is uncertain.
- A restored PostgreSQL database is rebuilt from Notion source of truth before
  production QA or accepted append mutations resume.
- An uncertain append is resolved by read-only durable identity inspection:
  identity present -> page re-index then workflow reconciliation; identity
  absent -> unresolved change request and human accept flow; identity unknown
  -> stop without retry.
- The operator records `restore_drill_status`, `migration_revision`,
  `readiness_status`, `reindex_status`, and `scoped_citation_count` as safe
  evidence fields. These are operational evidence, not production RAG input.

## Vector Retrieval Metadata

- Step 53 QA workflows record `retrieval_mode`:
  `pgvector_exact_cosine`, `pgvector_hnsw_cosine`, or `lexical_fallback`.
- QA workflows that fall back to lexical retrieval record nullable
  `retrieval_fallback_reason`.
- QA workflows also record `embedding_provider`, `embedding_model`,
  `embedding_dimensions`, and `vector_distance_metric`.
- A successful lexical fallback still uses workflow `status=succeeded`.
  `failure_reason` should stay null unless the whole workflow actually fails.

## Log Redaction Rules

- Request logs stay minimal: `workflow_id`, path, method, status code, duration,
  and a short event name.
- Trust-boundary failures use the same minimal request log shape and do not
  create a workflow run before authentication or Telegram chat authorization.
- Log formatter output must redact bearer tokens, API keys, Notion tokens,
  Telegram bot tokens, and other surfaced secret assignments.
- Log formatter output must redact `raw_text` and `source_text` values because
  they may contain private user or Notion content.
- Tool and provider adapters should sanitize external exception strings before
  returning them to orchestrators or API routes.

## Adapter Smoke Evidence

The Step 81 adapter smoke matrix emits a redacted report with fixed fields:
`check_id`, `dependency_level`, `status`, and a safe message. It must not log
credentials, URLs, external exception bodies, or extracted source text. A
`skipped` live check means its explicit opt-in or dependency configuration was
absent; it is not equivalent to a passing live dependency check. Reports from
`tests/evals/adapter_smoke_matrix.py` are release evidence only when the
operator records which opt-in live checks were intentionally run.

The Step 82 Notion canary emits fixed counts for indexed pages, blocks, chunks,
incremental pages, citations, Notion requests, and blocked write attempts. Its
HTTP audit reports only operation classes (`POST /v1/search`, `GET
/v1/pages/{id}`, and `GET /v1/blocks/{id}/children`); it must not expose page
ids, paths, titles, credentials, source text, or upstream exception bodies.
`status=passed` requires zero write attempts. A skipped canary is not evidence
of live Notion connectivity. A failed report includes a redacted
`failed_stage` and a standard `failure_reason`; the canary must not expose the
underlying exception text.

The Step 83 Notion append canary emits fixed counts for indexed blocks/chunks,
citation count, appended block count, accepted change-request state, durable
identity visibility, Notion requests, and unexpected operations. Its HTTP audit
reports only `GET /v1/pages/{id}`, `GET /v1/blocks/{id}/children`, and
`PATCH /v1/blocks/{id}/children`. It must not expose page ids, paths, titles,
credentials, source text, request payloads, or upstream exception bodies.
`status=passed` requires both explicit live opt-in and explicit human approval,
`pending -> accepted`, durable identity visibility, successful re-index, and a
target-scoped QA citation. A skipped or approval-blocked canary is not live
append evidence.

## Failure Reason Taxonomy

- Use one shared `failure_reason` taxonomy for workflow runs, API responses,
  and structured logs.
- Prefer specific external failure reasons over `UNKNOWN_ERROR` when the
  backend can deterministically classify the failure.
- Current external API and tool reasons:
  `NOTION_AUTH_FAILED`, `NOTION_PAGE_NOT_FOUND`, `NOTION_APPEND_NOT_VERIFIED`,
  `NOTION_BLOCK_FETCH_FAILED`, `STALE_PAGE_SNAPSHOT`, `OCR_FAILED`, `PDF_PARSE_FAILED`,
  `URL_FETCH_FAILED`, `YOUTUBE_TRANSCRIPT_NOT_FOUND`,
  `PROVIDER_NOT_FOUND`, `LLM_PROVIDER_ERROR`, `LLM_OUTPUT_INVALID`,
  `EMBEDDING_PROVIDER_NOT_CONFIGURED`, `EMBEDDING_PROVIDER_ERROR`,
  `TELEGRAM_QUEUE_UNAVAILABLE`, `REDIS_URL_NOT_CONFIGURED`, `REDIS_UNAVAILABLE`,
  `AUTHENTICATION_FAILED`, `AUTHORIZATION_FAILED`,
  `TELEGRAM_UPDATE_LEDGER_FAILED`,
  `IDEMPOTENCY_KEY_CONFLICT`, `IDEMPOTENCY_IN_PROGRESS`,
  `IDEMPOTENCY_STORE_FAILED`,
  `VECTOR_DIMENSION_MISMATCH`, `VECTOR_QUERY_FAILED`,
  `VECTOR_UPSERT_FAILED`, `TELEGRAM_NOT_CONFIGURED`,
  `TELEGRAM_SEND_FAILED`, `TELEGRAM_FILE_DOWNLOAD_FAILED`, and
  `WORKFLOW_AUDIT_UPDATE_FAILED`.
- Telegram callback/session validation uses `INVALID_ARGUMENT`,
  `INVALID_CALLBACK`, `UPLOAD_MEDIA_MISSING`, `UPLOAD_SESSION_EXPIRED`, and
  `UPLOAD_SESSION_INVALID` when applicable; these reasons must not be collapsed
  into `UNKNOWN_ERROR`.
- Upload/resource reasons include `INVALID_UPLOAD_TYPE`,
  `INVALID_UPLOAD_MIME`, `EMPTY_UPLOAD`, `UPLOAD_LIMIT_EXCEEDED`,
  `UPLOAD_TOO_LARGE`, `PDF_PAGE_LIMIT_EXCEEDED`,
  `IMAGE_PIXEL_LIMIT_EXCEEDED`, `INVALID_IMAGE`, and
  `EXTRACTED_TEXT_LIMIT_EXCEEDED`.
- URL resource reasons include `URL_SSRF_BLOCKED`,
  `URL_DNS_RESOLUTION_FAILED`, `URL_REDIRECT_LIMIT_EXCEEDED`,
  `URL_RESPONSE_TYPE_UNSUPPORTED`, and `URL_RESPONSE_TOO_LARGE`.
- Current business-rule and workflow reasons:
  `CHANGE_REQUEST_NOT_FOUND`, `WRITE_POLICY_VIOLATION`,
  `DUPLICATE_SOURCE`, `SYNTHETIC_DATA_NOT_ALLOWED`, and `UNKNOWN_ERROR`.

## Synthetic Data Hygiene Evidence (Step 87)

Synthetic-data cleanup and release-gate reports may contain only fixed status,
check id, error code, and aggregate counts. They must not expose database URLs,
credentials, page ids, titles, paths, source text, vectors, or exception
bodies. A failed inspection is fail-closed evidence, not a clean result.

## Retrieval Fallback Reasons

- Use `retrieval_fallback_reason` instead of workflow `failure_reason` when QA
  safely degrades to lexical retrieval.
- Allowed fallback reasons are:
  `EMBEDDING_PROVIDER_NOT_CONFIGURED`, `EMBEDDING_PROVIDER_ERROR`,
  `VECTOR_DIMENSION_MISMATCH`, `VECTOR_QUERY_FAILED`, and
  `VECTOR_DATA_UNAVAILABLE`.
