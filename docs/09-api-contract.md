# 09 API Contract

## Purpose
This document defines planned API contracts and request/response examples.

## Status
Draft

## Notion Index APIs

### POST `/api/notion/index/page`
Trigger one-page indexing from Notion read-only content.

Request:

```json
{
  "page_id": "page-nlp-week5"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 101,
  "status": "succeeded",
  "page_id": "page-nlp-week5",
  "page_title": "NLP Week 5",
  "notion_path": "Knowledge/NLP/Week5",
  "indexed_block_count": 18
}
```

Failure response example `404` (page not found):

```json
{
  "detail": {
    "error_code": "NOTION_PAGE_NOT_FOUND",
    "message": "Notion page is not found: page_id=page-nlp-week5",
    "failure_reason": "NOTION_PAGE_NOT_FOUND",
    "workflow_run_id": 101
  }
}
```

Notes:
- Route must call orchestrator. Route does not call Notion directly.
- Orchestrator must call `ToolRegistry` -> `NotionReaderTool`.
- This endpoint does not perform Notion write operations.
- Workflow runs use `workflow_type=indexing`.

### POST `/api/notion/index/incremental`
Manual sync entrypoint for user manual Notion edits/deletes/merges.

Request:

```json
{
  "page_ids": ["page-nlp-week5", "page-ml-week2"]
}
```

Success response `200`:

```json
{
  "workflow_run_id": 202,
  "status": "succeeded",
  "sync_mode": "manual",
  "processed_page_count": 2,
  "indexed_pages": [
    {
      "page_id": "page-nlp-week5",
      "page_title": "NLP Week 5",
      "notion_path": "Knowledge/NLP/Week5",
      "indexed_block_count": 18
    },
    {
      "page_id": "page-ml-week2",
      "page_title": "ML Week 2",
      "notion_path": "Knowledge/ML/Week2",
      "indexed_block_count": 12
    }
  ]
}
```

Failure response example `404`:

```json
{
  "detail": {
    "error_code": "NOTION_PAGE_NOT_FOUND",
    "message": "Notion page is not found: page_id=missing-page",
    "failure_reason": "NOTION_PAGE_NOT_FOUND",
    "workflow_run_id": 202
  }
}
```

Notes:
- Route must call orchestrator. Route does not call Notion directly.
- Reconciliation uses page-level replacement.
- For each changed page, stale blocks/chunks are removed and current Notion page content is re-indexed.

## QA API

### POST `/api/qa`
Run production RAG QA and return answer with citation paths.

Request:

```json
{
  "query": "Explain attention in week5 notes",
  "top_k": 5,
  "page_ids": ["page-nlp-week5"],
  "section_paths": ["Knowledge/NLP/Week5/Attention"],
  "source_kinds": ["notion"],
  "provider_name": "openai",
  "model": "gpt-4o-mini"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 301,
  "status": "succeeded",
  "answer": "Attention aligns query and key to weight values.",
  "insufficient_info": false,
  "retrieved_chunk_count": 2,
  "citations": [
    {
      "notion_path": "Knowledge/NLP/Week5/Attention",
      "page_id": "page-nlp-week5",
      "score": 0.934211
    }
  ],
  "provider": "openai",
  "model": "gpt-4o-mini",
  "token_input": 25,
  "token_output": 10
}
```

Insufficient-info response `200`:

```json
{
  "workflow_run_id": 302,
  "status": "succeeded",
  "answer": "I do not have enough information in production notes to answer safely.",
  "insufficient_info": true,
  "retrieved_chunk_count": 0,
  "citations": [],
  "provider": null,
  "model": null,
  "token_input": null,
  "token_output": null
}
```

Failure response example `500` (provider not configured):

```json
{
  "detail": {
    "error_code": "PROVIDER_NOT_FOUND",
    "message": "Provider is not registered: 'openai'",
    "failure_reason": "UNKNOWN_ERROR",
    "workflow_run_id": 303
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator retrieves production chunks and calls `ProviderRouter`.
- `pending` and `rejected` content remains excluded by production retrieval policy.
