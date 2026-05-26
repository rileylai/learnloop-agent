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
