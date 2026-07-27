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
  `NOTION_AUTH_FAILED`, `NOTION_PAGE_NOT_FOUND`,
  `NOTION_BLOCK_FETCH_FAILED`, `OCR_FAILED`, `PDF_PARSE_FAILED`,
  `URL_FETCH_FAILED`, `YOUTUBE_TRANSCRIPT_NOT_FOUND`,
  `PROVIDER_NOT_FOUND`, `LLM_PROVIDER_ERROR`, `LLM_OUTPUT_INVALID`,
  `EMBEDDING_PROVIDER_NOT_CONFIGURED`, `EMBEDDING_PROVIDER_ERROR`,
  `VECTOR_DIMENSION_MISMATCH`, `VECTOR_QUERY_FAILED`,
  `VECTOR_UPSERT_FAILED`, `TELEGRAM_NOT_CONFIGURED`,
  `TELEGRAM_SEND_FAILED`, and `TELEGRAM_FILE_DOWNLOAD_FAILED`.
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
