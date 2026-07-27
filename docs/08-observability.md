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

Missing from the current operator surface:

- `/metrics` and a metrics exporter.
- A CLI, API, worker, or scheduler that invokes stale-running workflow
  reconciliation.
- Aggregate cost budgets, alerts, log persistence/rotation, tracing backend,
  and recovery dashboards.

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
- Redis is not part of readiness until the worker is wired in Step 77.

## Workflow Metadata Notes

- LLM-backed workflows record `provider_name`, `model`, `prompt_id`, and
  `prompt_version` in workflow metadata JSON.
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
- Log formatter output must redact bearer tokens, API keys, Notion tokens,
  Telegram bot tokens, and other surfaced secret assignments.
- Log formatter output must redact `raw_text` and `source_text` values because
  they may contain private user or Notion content.
- Tool and provider adapters should sanitize external exception strings before
  returning them to orchestrators or API routes.

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
  `VECTOR_DIMENSION_MISMATCH`, `VECTOR_QUERY_FAILED`,
  `VECTOR_UPSERT_FAILED`, `TELEGRAM_NOT_CONFIGURED`,
  `TELEGRAM_SEND_FAILED`, `TELEGRAM_FILE_DOWNLOAD_FAILED`, and
  `WORKFLOW_AUDIT_UPDATE_FAILED`.
- Current business-rule and workflow reasons:
  `CHANGE_REQUEST_NOT_FOUND`, `WRITE_POLICY_VIOLATION`,
  `DUPLICATE_SOURCE`, and `UNKNOWN_ERROR`.

## Retrieval Fallback Reasons

- Use `retrieval_fallback_reason` instead of workflow `failure_reason` when QA
  safely degrades to lexical retrieval.
- Allowed fallback reasons are:
  `EMBEDDING_PROVIDER_NOT_CONFIGURED`, `EMBEDDING_PROVIDER_ERROR`,
  `VECTOR_DIMENSION_MISMATCH`, `VECTOR_QUERY_FAILED`, and
  `VECTOR_DATA_UNAVAILABLE`.
