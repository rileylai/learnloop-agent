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
