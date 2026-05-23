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
