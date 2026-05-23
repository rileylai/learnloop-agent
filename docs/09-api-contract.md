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
