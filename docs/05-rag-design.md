# 05 RAG Design

## Purpose
This document defines chunking, embeddings, metadata filters, citation behavior, and production-RAG rules.

## Status
Draft

## Citation Path Builder (Step 12)

File:
- `src/rag/block_path_builder.py`

Goal:
- Build deterministic block citation paths from block hierarchy during indexing.
- Do not rely on external path text as source of truth.

Input:
- `page_path` (for example `Knowledge/NLP/Week5`)
- Nested block tree with `block_id`, `block_type`, `content_text`, and `children`

Output:
- Same tree shape with computed `block_path` on each block.

Rules:
- Page path is normalized by trimming spaces and duplicate slashes.
- Each block path starts from parent path.
- If block `content_text` is non-empty after whitespace normalization, append it as one new path segment.
- If block `content_text` is empty, inherit parent path.
- The same rule applies to mixed block types, including heading, toggle, and child page blocks.

Example:

```text
page_path: Knowledge/Mixed
heading: Root Heading
toggle: Toggle Topic
child_page: Child Page A
paragraph: Leaf Note
```

Computed paths:

```text
Knowledge/Mixed/Root Heading
Knowledge/Mixed/Root Heading/Toggle Topic
Knowledge/Mixed/Root Heading/Toggle Topic/Child Page A
Knowledge/Mixed/Root Heading/Toggle Topic/Child Page A/Leaf Note
```

## Notion Chunker (Step 13)

File:
- `src/rag/chunker.py`

Goal:
- Convert indexed Notion blocks into chunk drafts for retrieval and embedding.
- Keep `notion_path` metadata on each chunk for citation traceability.

Input:
- One indexed Notion page (`notion_page_id`, title, `notion_path`)
- Nested blocks with block id, block type, text, block path, and children

Output:
- Ordered chunk drafts with:
  - `chunk_index`
  - `chunk_text`
  - `notion_path`
  - `citation_meta` (`notion_page_id`, `notion_page_title`, `notion_page_path`, `notion_block_ids`)

Boundary rules:
- Start a new chunk when block type hits a section boundary:
  - `heading_1`, `heading_2`, `heading_3`, `toggle`, `child_page`
- This enforces chunking around page/toggle/heading/section boundaries.
- Non-boundary text before the first section boundary stays in page-level chunks.

Chunk text rules:
- Normalize whitespace in block text.
- Skip empty text lines.
- Split chunk text when adding the next line would exceed `max_chunk_chars`.

## Embedding Provider Abstraction (Step 14)

Files:
- `src/providers/embedding.py`

Goal:
- Keep embedding logic behind a provider-style interface.
- Start with OpenAI embedding adapter while keeping extension points for other providers.

Components:
- `EmbeddingClient`: abstract embedding interface for orchestrator/service usage.
- `EmbeddingRequest`: input schema (`inputs`, optional `model`, optional `dimensions`, optional metadata).
- `EmbeddingResponse`: output schema (`embeddings`, token usage, provider/model metadata).
- `OpenAIEmbeddingClient`: OpenAI-first adapter implementing `EmbeddingClient`.

Rules:
- Orchestrators and services should depend on `EmbeddingClient`, not provider SDKs.
- OpenAI adapter can use transport injection for deterministic unit tests.
- Mock tests validate request payload, response mapping, and error behavior without real network.

## Chunk Upsert with Page Replacement (Step 15)

Files:
- `src/repositories/chunk_repository.py`

Goal:
- Upsert Notion chunks with page-level replacement semantics.
- Re-indexing the same page must replace old chunks and avoid duplicates.

Component:
- `ChunkRepository.upsert_chunks(notion_page_db_id, chunks)`

Rules:
- Scope deletion to `source_kind="notion"` chunks mapped to blocks in the target page.
- Delete old page chunks first, then insert new chunks in `chunk_index` order.
- Keep cross-page chunks untouched.
- Map each chunk to a page block via `notion_block_ids` from citation metadata.
- Store embedding vectors as serialized text in current MVP schema (`embedding_text`).
