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
- When the queue is required, readiness also checks the RQ scheduler lock for
  the `telegram` queue. Redis `PING` can pass while delayed jobs remain in
  `ScheduledJobRegistry`; that state is reported as
  `RQ_SCHEDULER_NOT_RUNNING` and `/ready` stays unavailable.

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
- Worker startup also emits safe `queue`, `worker_started`,
  `scheduler_enabled`, and `scheduler_mode=embedded` fields. It never emits
  `REDIS_URL` or credentials.

Telegram ingestion observability:
- Workflow metadata records safe operation classes, counts, target-set state,
  and callback/review action status only. For target-picker callbacks it also
  records `business_status`, `callback_ack_status`, and
  `preview_delivery_status`. It does not record callback tokens,
  canonical page ids, upload bytes, captions, OCR text, or proposal source
  content.
- Review callback metadata records the normalized action and
  `change_request_status` only. Callback routing uses a server-side
  `callback_kind` (`review` or `picker`); the opaque callback token and raw
  Telegram payload are never logged. Legacy mappings are normalized by their
  allowlisted action so an old Accept token remains a review callback.
- A valid callback acknowledgement emits a structured warning with
  `failure_reason=TELEGRAM_CALLBACK_ACK_FAILED` when `answerCallbackQuery`
  fails. This warning is independent from the workflow terminal status; a
  business-successful callback may finish with `workflow_runs.status=succeeded`.
- A post-commit preview send failure is terminal only for delivery and uses
  `failure_reason=TELEGRAM_PREVIEW_DELIVERY_FAILED`. Metadata retains
  `business_status=succeeded` and `preview_delivery_status=failed`, while the
  pending change request remains recoverable.
- Redis upload sessions and callback mappings are TTL-bound and scoped by chat
  and user. Their state is not emitted into user-facing logs.
- Duplicate update, settle, target, and preview claims are observable through
  terminal status/failure outcomes without exposing private media or Notion
  content.
- Screenshot proposal workflows record redacted latency evidence in milliseconds:
  `download_ms`, `ocr_ms`, `llm_ms`, `persist_ms`, `preview_delivery_ms`, and
  `total_business_ms`. These are numeric stage timings only; OCR text, proposal
  fields, file bytes, callback tokens, URLs, and secrets are excluded.
- Screenshot proposal metadata may record `title_repair_attempted` and
  `title_repair_succeeded`. A repair is one title-only LLM call using the same
  source snapshot; it never starts a second OCR or full-proposal generation
  stage.
- Deterministic title fallback records `title_fallback_attempted` and
  `title_fallback_succeeded` separately from the title LLM repair result. If a
  repaired or fallback title passes before body validation fails, the title
  stage remains successful in metadata.
- Screenshot proposal metadata may also record
  `summary_repair_attempted` and `summary_repair_succeeded`. This repair is
  eligible only for a single summary field failure with no new number,
  version, product, technical identifier, advice, comparison, or result. It
  makes one summary-only LLM call against the same source snapshot and is
  bounded to one retry.
- Safe multi-item lexical failures may record `body_repair_eligible`,
  `body_repair_attempted`, and `body_repair_succeeded`. One body-only repair
  may replace summary/concepts/notes and must pass the unchanged deterministic
  validator. New identifiers, numbers, advice, comparisons, or results disable
  this repair.
- Upload sessions carry a monotonic settle version. The settle job atomically
  promotes `collecting` to `settled`, sorts attachments by Telegram
  `message_id`, and stale/duplicate versions skip before picker or business
  work. Every update in the same `media_group_id` refreshes the debounce
  version; earlier delayed jobs are expected to be visible as safe stale skips.
  Duplicate `file_unique_id` values are ignored in the session store.
- A failed screenshot proposal retains `source_document_id`, target page, and
  attachment count in the session state. `/retry-proposal` and an old screenshot
  picker callback use that existing source without download/OCR. Redacted
  workflow metadata still records only stage identifiers, counts, and latency
  fields.
- Proposal validation failures record `failure_stage=proposal_validation` and
  a safe `validation_field` such as `summary` or `title`, plus the source id
  and already-measured latency fields. They never record OCR or proposal text.
- Screenshot grounding diagnostics also record only deterministic evidence:
  `source_normalized_char_count`, `candidate_field_char_count`,
  `evidence_claim_count`, `unsupported_claim_count`, `validator_version`,
  `source_snapshot_digest`, `prompt_source_digest`, and
  `validation_source_digest`, plus title-only anchor counts:
  `title_anchor_count`, `matched_title_anchor_count`,
  `unmatched_title_anchor_count`, `title_failure_reason`,
  `matched_high_specificity_anchor_count`,
  `unmatched_high_specificity_anchor_count`, `matched_general_anchor_count`,
  `unmatched_general_anchor_count`, `matched_technical_identifier_count`,
  `unmatched_technical_identifier_count`, `numeric_anchor_count`,
  `unmatched_numeric_anchor_count`, and `title_repair_failure_reason`.
  Title reasons use the fixed enum set `NO_USABLE_TITLE_ANCHOR`,
  `INSUFFICIENT_MATCHED_ANCHORS`, `UNMATCHED_TECHNICAL_IDENTIFIER`,
  `UNMATCHED_PRODUCT_NAME`, `UNMATCHED_NUMBER_OR_VERSION`,
  `GENERIC_TITLE_ONLY`, and `OCR_NORMALIZATION_MISMATCH`.
  `evidence_claim_count` applies only to
  summary/concept/note claims and is the backward-compatible alias for
  `matched_claim_count`. Additional redacted claim diagnostics include
  `validation_granularity`, `validation_unit_count`,
  `matched_validation_unit_count`, `failed_validation_unit_count`,
  `failed_logical_region_count`, `failed_logical_regions`, per-region unit
  counts, `first_unsupported_validation_unit_index`, fixed reason counts,
  redacted failed-unit field/index/evidence-count details,
  `matched_exact_ascii_anchor_count`, `matched_cjk_anchor_count`,
  `unmatched_general_token_count`, `summary_repair_eligible`,
  `body_repair_eligible`, and `repair_scope`. `extracted_claim_count`,
  `matched_claim_count`, and `failed_field_count` remain backward-compatible;
  `failed_field_count` means unique item paths, not proposal fields. The prompt and
  validator digests are computed from the same persisted-source snapshot and
  must match. Telegram outer workflow metadata propagates these fields from
  the supplement workflow through an allowlist, along with
  `source_attachment_count` and `llm_ms`.
  Raw candidate units and matched anchor strings are available only in an
  in-process private diagnostic report. They are never persisted or propagated
  to the outer Telegram workflow.

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

## Step 88 Telegram Outcome Recovery

- For a committed Telegram callback outcome, first run a dry-run inspection:
  `uv run python scripts/reconcile_telegram_outcome.py --update-id <id>
  --workflow-id <id> --source-document-id <id> --change-request-id <id>
  --action resend-preview --json`.
- The inspector verifies the workflow/ledger, source row, pending change
  request, source link, and target page. Apply mode only resends the existing
  preview or reconciles an already-delivered result; it never invokes OCR, an
  LLM, or proposal creation.
- Recovery results store safe status/identifier fields only. They do not store
  Telegram payloads, raw image text, proposal source content, or secrets.

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
  `TELEGRAM_SEND_FAILED`, `TELEGRAM_CALLBACK_ACK_FAILED`,
  `TELEGRAM_PREVIEW_DELIVERY_FAILED`, `TELEGRAM_FILE_DOWNLOAD_FAILED`, and
  `WORKFLOW_AUDIT_UPDATE_FAILED`.
- Telegram callback/session validation uses `INVALID_ARGUMENT`,
  `INVALID_CALLBACK`, `UPLOAD_MEDIA_MISSING`, `UPLOAD_SESSION_EXPIRED`, and
  `UPLOAD_SESSION_INVALID` when applicable; these reasons must not be collapsed
  into `UNKNOWN_ERROR`.
- `TELEGRAM_CALLBACK_ACK_FAILED` is a UX-side-effect warning when business can
  safely continue; it does not imply `workflow_runs.status=failed`.
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
