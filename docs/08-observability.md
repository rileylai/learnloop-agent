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
  `VECTOR_UPSERT_FAILED`, `TELEGRAM_NOT_CONFIGURED`,
  `TELEGRAM_SEND_FAILED`, and `TELEGRAM_FILE_DOWNLOAD_FAILED`.
- Current business-rule and workflow reasons:
  `CHANGE_REQUEST_NOT_FOUND`, `WRITE_POLICY_VIOLATION`,
  `DUPLICATE_SOURCE`, and `UNKNOWN_ERROR`.
