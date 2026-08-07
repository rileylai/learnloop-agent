# 08 Observability

## Purpose
This document defines logs, metrics, traces, cost tracking, and failure_reason taxonomy.

## Status
Draft

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
- `workflow_runs` is the current persisted audit/status source. Although the
  schema includes `audit_logs`, no current repository or service writes it.
- `/metrics` computes current aggregates from workflow rows at scrape time; it
  is not a persistent time-series subsystem.

Missing from the current operator surface:

- Log persistence/rotation, a tracing backend, dashboards, and a persistent
  time-series metrics store.

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

## Step 88 Guarded Telegram Live E2E Evidence

The user explicitly confirmed completion of the guarded Telegram live E2E path
through the documented Telegram update, webhook, API, Redis/RQ worker,
PostgreSQL, OpenAI, Notion, and Telegram reply boundaries. This is bounded live
verification evidence, not a claim of cloud deployment, always-on sync,
production-wide readiness, or a new observability backend.

- The evidence boundary is recorded at status level only. This documentation
  does not add workflow identifiers, credentials, private content, cost,
  latency, test-count, or release-report figures.
- `workflow_runs`, redacted workflow metadata, `/metrics`, and the existing
  cost aggregation remain the sources for workflow and cost evidence. Unknown
  model pricing remains `estimated_cost=null`; no cost is inferred from the
  Step 88 confirmation.
- Existing redaction, callback/idempotency metadata, liveness/readiness
  distinction, and explicit operator recovery rules remain unchanged.

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
- Hierarchy picker navigation records only the normalized allowlisted action
  (`open_page`, `select_target`, `back`, or `root`; legacy
  `next_page`/`previous_page` and `change_target_select` mappings remain
  accepted for compatibility) and safe workflow outcome fields. It never records the
  server-side page/navigation context, breadcrumb, callback token, or page
  content. Browse callbacks are expected to have no OCR, provider, source-row,
  change-request, or target-claim timing fields.
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
- Provider-output schema failures record
  `failure_stage=provider_output_validation` and the safe field
  `provider_output`; later deterministic proposal/grounding failures retain
  `failure_stage=proposal_validation` and a safe field such as `summary` or
  `title`. Both paths include only source id and already-measured latency
  fields. They never record OCR, provider output, candidate source text, or
  proposal text.
- Screenshot grounding diagnostics also record only deterministic evidence:
  `source_normalized_char_count`, `candidate_field_char_count`,
  `evidence_claim_count`, `unsupported_claim_count`, `validator_version`,
  `source_snapshot_digest`, `prompt_source_digest`, and
  `validation_source_digest`, plus title-only anchor counts:
  `title_anchor_count`, `matched_title_anchor_count`,
  `unmatched_title_anchor_count`, `title_failure_reason`,
  `matched_high_specificity_anchor_count`,
  `unmatched_high_specificity_anchor_count`, `matched_general_anchor_count`,
  `unmatched_general_anchor_count`, `unmatched_general_ascii_count`,
  `matched_technical_identifier_count`,
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
  Safe numeric note-quality metadata may additionally include `concept_count`,
  `note_count`, `covered_concept_count`, `uncovered_concept_count`, and
  `notes_with_application_count`. It never includes concept strings, matched
  anchor strings, raw note text, OCR, or candidate proposal content.
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
- The screenshot generation prompt is `supplement_proposal_v7`; title,
  summary, and body repair prompts are separately versioned. The bounded call
  budget is one full proposal call, at most one title-only call, and at most
  one eligible summary/body call; sentence count alone never causes a call.
- Provider output is generated-content-only. Source and target are merged from
  persisted backend state before final proposal validation; deterministic
  source display rendering is never treated as source identity.
- QA and supplement proposal workflows also record `token_input`,
  `token_output`, and `estimated_cost` when token usage is available.
- Cost estimates are computed from a small model-pricing catalog inside the
  backend service layer. Unknown models return `estimated_cost=null` instead of
  guessing.
- Indexing workflows that generate chunk vectors should record
  `embedding_provider`, `embedding_model`, `embedding_dimensions`,
  `embedding_token_input`, `embedding_estimated_cost`,
  `embedding_batch_count`, and `embedding_retry_count`.
- Step 97 records provider input-token usage and cost only when usage is
  complete across every successful batch and no retry makes failed-attempt
  consumption unknowable. Missing or unknowable usage stays absent/unknown;
  planner estimates never substitute for provider usage.
- Safe embedding execution diagnostics are limited to provider/model/
  dimensions, bounded input and batch shapes, attempt/retry counts, duration,
  allowlisted status/category/retryability, and complete usage/cost. They must
  not contain raw provider responses/messages, embedding payloads or vectors,
  chunk text, Notion content or page identity/path, endpoint URLs, or secrets.
- The Step 97 bounded live dependency evidence recorded a 707,454-token
  conservative planning estimate separately from 289,651 provider-reported
  input tokens. Only the provider-reported value fed the USD 0.00579302 cost
  estimate; the planning estimate was not treated as usage or billing data.
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

  ```bash
  uv run --no-env-file --frozen python \
    scripts/reconcile_telegram_outcome.py \
    --update-id <id> \
    --workflow-id <id> \
    --source-document-id <id> \
    --change-request-id <id> \
    --action resend-preview \
    --json
  ```
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

## Steps 89-95 Telegram Operator Observability Contract

Operator command output and workflow metadata follow the bounded contract in
`docs/13-telegram-operator-contract.md`:

- Safe fields include normalized operation, command family, workflow id,
  status, requested scope, bounded counts, remaining work, deterministic
  failure reason, and known or `unknown` cost. Workflow ids are references,
  not rerun instructions.
- `/sync` records operation/scope/count/outcome fields only in the outer
  Telegram workflow. It does not record page ids, hierarchy paths, source
  text, embeddings, or raw Notion payloads there. The child indexing workflow
  retains the existing page-level reconciliation metadata needed to explain a
  partial failure.
- `/index-full` records confirmation state, idempotency outcome, indexing
  counts, and known embedding cost. An unknown estimate remains unknown.
- `/index-status` reads persisted indexing workflow state and does not contact
  Notion. `/cost` and `/workflow` reuse redacted aggregation/status services;
  neither emits prompts, OCR, source text, provider exceptions, or secrets.
- `/cost` supports `today`, rolling `7d`, calendar `month`, and one workflow
  scopes. Recorded `estimated_cost` and `embedding_estimated_cost` fields are
  aggregated separately as LLM/proposal/QA and embedding/indexing costs. A
  missing model price remains `unknown`; daily budget applies to `today`, and
  workflow budget status is evaluated per workflow or counted for period
  scopes.
- `/workflow` returns at most five recent summaries without an id, or one
  fixed-field redacted detail with an id. The Telegram formatter does not
  forward the recursively redacted metadata object; it selects safe operation,
  status, age, stale, failure, and bounded count fields only.
- `/index-full` warning/confirmation state is held in ephemeral operator
  session storage. The durable indexing workflow records page counts and
  deterministic failure state; Telegram output keeps only safe bounded fields.
- `/pending` records bounded review action/status and safe proposal display
  fields only. View is read-only; Accept/reject/change-target actions retain
  existing review and append/re-index audit semantics. The outer Telegram
  workflow records only the bounded `pending_count` and review fields, never
  proposal source text or canonical page ids.
- `/status` exposes liveness separately from readiness and reports only fixed
  states for database, migration, pgvector, provider, Notion configuration,
  Redis, and the RQ scheduler. It never exposes URLs, secrets, or raw probe
  exceptions. `/stats` reports only repository-backed page/block/chunk/vector/
  proposal counts and normalized UTC timestamps for the latest successful full
  index and manual incremental sync; it never includes note content.
- Operator callback tokens, raw callback payloads, Redis keys, canonical page
  ids, and user private content are never logged. Callback ack, business, and
  preview-delivery state remain separate where applicable.

### Step 95 regression and live-evidence boundary

The Step 95 deterministic regression matrix verifies operator parsing,
authorization, callback ownership/TTL, duplicate claims, confirmation gates,
redaction, review safety, readiness/liveness, aggregate stats, help output,
queue/worker behavior, and existing ingestion/review paths with controlled
dependencies. It does not establish live external-dependency readiness.

Live Telegram/Notion/Redis/OpenAI verification remains explicit opt-in work
with dedicated resources and redacted status/count/workflow/cost evidence. It
must not default to full index, append, Accept, or Telegram send.

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

- Step 53 QA workflows record `retrieval_mode` as
  `pgvector_exact_cosine` or `lexical_fallback`.
- The migration includes an HNSW cosine index, but current runtime code does
  not emit a separate HNSW retrieval-mode value.
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
- Readiness failures are a separate surface. Its current reasons are
  `DATABASE_UNAVAILABLE`, `MIGRATION_NOT_CURRENT`,
  `VECTOR_EXTENSION_UNAVAILABLE`, `OPENAI_API_KEY_NOT_CONFIGURED`,
  `REDIS_URL_NOT_CONFIGURED`, `REDIS_UNAVAILABLE`,
  `RQ_SCHEDULER_NOT_CONFIGURED`, `RQ_SCHEDULER_UNAVAILABLE`,
  `RQ_SCHEDULER_NOT_RUNNING`, and `NOTION_TOKEN_NOT_CONFIGURED`. They must not
  be presented as completed workflow
  outcomes.
- Telegram recovery CLI eligibility/storage codes are operator-command results,
  not additions to `STANDARD_FAILURE_REASONS`. The CLI reports them in a
  redacted result and does not rewrite the business failure taxonomy.

### Step 96 External Diagnostic Categories

Step 96 adds an internal diagnostic category below the existing workflow
failure reasons. Categories are `timeout`, `transport_unavailable`,
`request_invalid`, `authentication_failed`, `request_timeout`,
`request_too_large`, `validation_failed`, `rate_limited`,
`upstream_server_error`, `response_invalid`, and `unknown_http_error`.
Retryability is classification only; Step 96 does not execute a retry.

Embedding diagnostic output may contain only dependency, fixed operation,
fixed endpoint class, provider, model, dimensions, input/empty counts, maximum
single-input character/byte/token estimates, aggregate byte/token estimates,
estimator version, HTTP status, normalized category, retryability, bounded
numeric `Retry-After`, fixed diagnostic case, and duration. Token estimates are
not provider-reported billing usage.

The Step 96 full request-shape inspection may additionally emit total input
count, p50/p95/p99 byte/character/token estimates, and the one-based ordinal of
the first maximum-byte input. The ordinal is not a chunk identifier. Shape-only
success output contains no provider, model, endpoint, page, or content field.
The completed evidence recorded 2,483 total inputs and zero empty inputs; it
did not add raw provider content or a provider error code that was never
captured.

Raw response bodies, raw provider messages or unknown codes, serialized
payloads, chunk/block/page content, page identity/path, embeddings, endpoint
URLs/hosts, authorization headers, tokens, and credentials are prohibited from
logs, workflow metadata, API errors, and diagnostic reports.

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

## Step 98 Experiment Evidence

Normal Step 98 evidence records experiment, manifest, request-plan, capture,
vector-set, input, result, and implementation-source digests; builder/model
versions; dimensions; bounded counts; retry/usage/cost summaries; and fixed
gate outcomes. It must not log derived embedding input, raw source text,
credentials, provider response bodies, or vectors.

The public-safe Phase B capture artifact is the narrow exception for vectors:
it may retain the one shared query-vector set and three document-vector sets so
Phase C can deterministically replay ranking. Creation is explicit,
create-only, bounded, and separately approved. It is not workflow telemetry or
production database state. Any managed digest mismatch rejects capture or
scoring instead of silently producing new evidence.

For `step98-exp-002`, every provider attempt consumes a globally persisted slot
before the call. Success and failure publish a create-only safe receipt in a
single canonical run directory; only complete success publishes vectors.
Failure receipts exclude inputs, partial vectors, provider bodies, credentials,
and database target names. These are local integrity/provenance receipts, not
cryptographic authentication of an external authority.
