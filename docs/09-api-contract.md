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
