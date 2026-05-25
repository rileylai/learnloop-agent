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

## Ingestion Foundation API

### POST `/api/ingest/source`
Create one `source_documents` row from normalized source text.

Request:

```json
{
  "source_type": "pdf",
  "source_display_name": "lecture1.pdf",
  "raw_text": "Transformer notes from lecture 1"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 401,
  "status": "succeeded",
  "source_document_id": 1,
  "source_type": "pdf",
  "source_display_name": "lecture1.pdf",
  "content_hash": "4f9b56d58d6f1d4a2c7c87791ce58eceefc9c1be9b9c517f4f67de9f0f5b74f1"
}
```

Failure response example `400` (unsupported source type):

```json
{
  "detail": {
    "error_code": "INVALID_ARGUMENT",
    "message": "source_type must be one of: pdf, url, youtube, screenshot, chat_text",
    "failure_reason": "UNKNOWN_ERROR",
    "workflow_run_id": null
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator starts `workflow_type=ingestion` and persists source metadata through repository.
- Step 20 stores core fields: `source_type`, `source_display_name`, and `content_hash`.

### POST `/api/ingest/document`
Ingest one uploaded PDF document, extract text, and create one source document.

Request:
- `multipart/form-data`
- field: `document` (PDF file)

Success response `200`:

```json
{
  "workflow_run_id": 402,
  "status": "succeeded",
  "source_document_id": 2,
  "source_type": "pdf",
  "source_display_name": "lecture-week5.pdf",
  "content_hash": "b42b4ab40f62f4ec3f71d1677ad86a427b6996f71bf6200ff646862b5f37f06b"
}
```

Failure response example `422` (parse failed):

```json
{
  "detail": {
    "error_code": "PDF_PARSE_FAILED",
    "message": "No extractable text found in PDF",
    "failure_reason": "PDF_PARSE_FAILED",
    "workflow_run_id": 402
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator must call `ToolRegistry` -> `PDFParserTool`.
- This endpoint does not perform Notion write operations.
- Source display name is the uploaded filename.

### POST `/api/ingest/url`
Ingest one URL article, extract normalized text, and create one source document.

Request:

```json
{
  "url": "https://example.com/nlp-week5"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 403,
  "status": "succeeded",
  "source_document_id": 3,
  "source_type": "url",
  "source_display_name": "https://example.com/nlp-week5",
  "content_hash": "271f1c0e18d86bd53b4a46d2a7e05320b89432135b86564f3cd6de44db69b7f3"
}
```

Failure response example `422` (fetch or extraction failed):

```json
{
  "detail": {
    "error_code": "URL_FETCH_FAILED",
    "message": "No extractable text found in URL article",
    "failure_reason": "URL_FETCH_FAILED",
    "workflow_run_id": 403
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator must call `ToolRegistry` -> `URLArticleParserTool`.
- This endpoint does not perform Notion write operations.
- Source display name preserves the full URL string.

### POST `/api/ingest/youtube`
Ingest one YouTube video transcript and create one source document.

Request:

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 404,
  "status": "succeeded",
  "source_document_id": 4,
  "source_type": "youtube",
  "source_display_name": "YouTube transcript (dQw4w9WgXcQ)",
  "content_hash": "972ebd505260f1f7d55d5bdb4e08a4aa4f53b7900f87fbeb1d3e602dcc8f2e38"
}
```

Failure response example `422` (transcript unavailable):

```json
{
  "detail": {
    "error_code": "YOUTUBE_TRANSCRIPT_NOT_FOUND",
    "message": "No transcript found for this YouTube video",
    "failure_reason": "YOUTUBE_TRANSCRIPT_NOT_FOUND",
    "workflow_run_id": 404
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator must call `ToolRegistry` -> `YouTubeTranscriptTool`.
- This endpoint does not perform Notion write operations.
- MVP is transcript-only; no speech-to-text fallback for videos without transcript.

### POST `/api/ingest/chat-text`
Ingest pasted chat text and create one source document.

Request:

```json
{
  "chat_text": "Meeting notes about retrieval quality and attention concepts.",
  "source_display_name": "chat-2026-05-25"
}
```

Success response `200`:

```json
{
  "workflow_run_id": 406,
  "status": "succeeded",
  "source_document_id": 6,
  "source_type": "chat_text",
  "source_display_name": "chat-2026-05-25",
  "content_hash": "cab93f7304657fce4ff3be8f36489039bc384c2d8f559550f8940af8601c7094"
}
```

Failure response example `400` (over MVP length limit):

```json
{
  "detail": {
    "error_code": "INVALID_ARGUMENT",
    "message": "chat_text exceeds MVP length limit (10000 chars)",
    "failure_reason": "UNKNOWN_ERROR",
    "workflow_run_id": null
  }
}
```

Notes:
- Route must call orchestrator only.
- This endpoint does not perform Notion write operations.
- MVP chat text length limit is `10000` characters.

### POST `/api/ingest/image-ocr`
Ingest multiple screenshots, run OCR in upload order, and create one source document.

Request:
- `multipart/form-data`
- repeated field: `images` (image files in intended reading order)

Success response `200`:

```json
{
  "workflow_run_id": 405,
  "status": "succeeded",
  "source_document_id": 5,
  "source_type": "screenshot",
  "source_display_name": "Screenshot batch (3 images)",
  "content_hash": "30c8e52d4dc85f94fcdbdf6916696559f027c7af5269f78f8bdce840f31f586f"
}
```

Failure response example `422` (OCR failed):

```json
{
  "detail": {
    "error_code": "OCR_FAILED",
    "message": "No extractable text found in images",
    "failure_reason": "OCR_FAILED",
    "workflow_run_id": 405
  }
}
```

Notes:
- Route must call orchestrator only.
- Orchestrator must call `ToolRegistry` -> `ImageOCRTool`.
- This endpoint does not perform Notion write operations.
- Uploaded image order must be preserved in OCR text concatenation.

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
