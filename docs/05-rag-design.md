# 05 RAG Design

## Purpose
This document defines chunking, embeddings, metadata filters, citation behavior, and production-RAG rules.

## Status
Draft

### Current Implementation Status

Chunking, page replacement, embedding generation, pgvector cosine retrieval,
lexical fallback, citation construction, and synthetic-data filtering are
implemented and deterministic test verified. Step 82 provides bounded live
Notion read/index/QA evidence. Live OpenAI plus PostgreSQL vector smoke remains
opt-in and was not run as an independent vector smoke in the latest audit. The
user-confirmed guarded Step 88 Telegram live E2E is recorded separately and
does not widen production-RAG eligibility or workspace scope.

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

The live Notion reader treats `child_page` and `link_to_page` blocks as page
references. It keeps the reference block in the parent tree but does not inline
the referenced page's children; full discovery indexes that page separately.
This preserves globally unique Notion block IDs while retaining the reference
path for citation metadata.

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
- During rollout, persist both live pgvector data in `embedding` and legacy
  serialized JSON in `embedding_text`.

## Manual Incremental Sync Reconciliation (Step 16)

Endpoint:
- `POST /api/notion/index/incremental`

Goal:
- Reconcile manual Notion edits/deletes/merges with current Notion truth.

Rules:
- Input provides changed `page_ids` for manual sync.
- For each page id:
  - Re-read current page tree from Notion reader tool.
  - Rebuild page blocks with page-level replacement.
  - Rebuild notion chunks, batch them through `EmbeddingClient`, and upsert
    live vectors with page-level replacement.
- If one page fails, fail the incremental workflow deterministically with failure reason and workflow id.

## Shared Live Embedding Indexing Path (Step 50)

Files:
- `src/orchestrators/notion_page_index_orchestrator.py`
- `src/orchestrators/notion_incremental_index_orchestrator.py`
- `src/repositories/chunk_repository.py`

Goal:
- Make page indexing, manual incremental sync, and auto-after-accept re-index
  all use one architecture-safe embedding flow.

Flow:
- `NotionPageIndexOrchestrator -> EmbeddingClient -> ChunkRepository -> PostgreSQL + pgvector`

Rules:
- Build chunk drafts from the current page snapshot before mutating page
  blocks or chunk rows.
- Batch all chunk text for one page through `EmbeddingClient` with explicit
  `dimensions=1536`.
- Persist successful embeddings to both `knowledge_chunks.embedding` and the
  transitional `knowledge_chunks.embedding_text`.
- Missing embedding configuration or embedding-provider failure must fail
  closed before block or chunk replacement begins.
- Manual incremental sync and auto-after-accept re-index must reuse the same
  page indexing orchestrator instead of implementing vector writes separately.

## Large-page Failure Diagnostics (Step 96)

Observed live evidence shows that increasing the Notion reader's per-request
timeout from 10 to 30 seconds allowed one large read-only traversal to reach
the embedding stage, where the existing single page-wide request returned HTTP
400. This evidence does not establish payload size as the cause; model,
dimensions, endpoint compatibility, empty input, single-input size, aggregate
size, and other validation hypotheses remain open until bounded diagnostics
establish a provider category or controlled failure boundary.

The first guarded matrix subsequently passed with the configured OpenAI
embedding endpoint class, `text-embedding-3-small`, and `dimensions=1536` for
1, 4, 8, 16, 32, and 64 inputs. The largest tested request contained 24,916
bytes / 6,254 estimated tokens, and no input was empty. This proves only that
the tested model/dimensions and tested multi-input shapes work. It produced no
provider category or failure boundary and does not explain the original
page-wide HTTP 400.

The deterministic Step 96 implementation adds typed, sanitized Notion and
embedding errors plus versioned request-shape diagnostics. It classifies HTTP
status, normalized provider category, and retryability without storing raw
provider bodies/messages, embedding payloads, chunk text, vectors, Notion
content, URLs, or credentials.

The guarded diagnostic uses the current body-only chunk inputs and executes
single-input, small-batch, and progressively count/byte/token-bounded probes
sequentially with no retry. Explicit request and total token-estimate budgets
stop an inconclusive run with a nonzero exit. This harness does not implement
production sub-batching. It never persists diagnostic embeddings or enters
page replacement. Step 97 remains responsible for the embedding execution
contract, bounded batching, retry, and aggregate usage.

The next diagnostic phase is shape-only: read and chunk the same page, compute
the full original request's count and byte/token distribution in memory, and
emit only aggregate/max/percentile estimates plus the safe ordinal of the
largest input. It does not create an embedding client or provider request.

## Legacy Chunk Vector Gap Handling (Step 51)

Goal:
- Define safe behavior while some existing Notion chunks still have no live
  vector during rollout.

Backfill strategy:
- The approved MVP backfill path is page-scoped re-index only.
- Use the shared indexing flow to regenerate blocks, chunks, and vectors for
  one page at a time.
- Manual incremental sync is the normal operator path when user manual edits
  or known vector gaps exist on specific pages.
- Future standalone backfill commands, if added, must still call the same
  page indexing orchestrator page by page.

Forbidden behavior:
- Do not walk the whole database and generate vectors automatically at app
  startup.
- Do not mix partial page replacement with failed vector generation.

Retrieval behavior during rollout:
- Current QA generates one query embedding when an embedding provider is
  configured and prefers repository-owned pgvector cosine retrieval.
- Mixed vector state remains safe: missing or unusable vectors in the eligible
  scope trigger a request-level lexical fallback over that same scope.
- When a page is re-indexed successfully, all notion chunks for that page must
  leave the shared indexing flow with both live `embedding` and transitional
  `embedding_text`.
- Unusable or missing vectors in the filtered retrieval scope are a
  request-level lexical fallback condition, not permission to silently skip
  unsupported rows.

## Repository-Owned pgvector Top-k Retrieval (Step 52)

Files:
- `src/repositories/chunk_repository.py`
- `src/rag/retriever.py`

Goal:
- Move semantic top-k ranking into PostgreSQL while keeping filter logic and
  production-safety deterministic.

Flow:
- `ProductionChunkRetriever -> ChunkRepository -> PostgreSQL + pgvector`

Rules:
- The repository owns vector-distance ordering when a caller provides a query
  embedding and PostgreSQL + pgvector are available.
- Apply production-safe `source_kind="notion"` filtering before top-k.
- Apply page and section filters before top-k.
- Exclude `embedding IS NULL` rows inside the repository query instead of
  trying to rank them in Python.
- Order semantic results by cosine distance ascending, then by stable chunk id
  for deterministic tie breaking.
- The QA orchestrator supplies query embeddings when configured. If the vector
  path is unavailable or unusable, it explicitly invokes lexical fallback.

## Production Chunk Retrieval (Step 17)

File:
- `src/rag/retriever.py`

Goal:
- Retrieve relevant chunks for QA from production-safe indexed content.
- Support deterministic scope filtering before answer generation.

Component:
- `ProductionChunkRetriever`

Scope filters:
- `page_ids`: filter chunks to specific Notion pages.
- `section_paths`: filter chunks by Notion path prefix for section-level scope.
- `source_kinds`: filter by chunk source kind.

Ranking behavior:
- Use lexical overlap scoring by default.
- If query embedding is provided on PostgreSQL + pgvector, use the
  repository-owned semantic top-k path.
- Otherwise, keep the current deterministic Python lexical path, with optional
  local embedding scoring still available for non-PostgreSQL test fixtures.
- Keep ranking deterministic and stable.

Production-RAG rules in this step:
- Current MVP production retrieval is constrained to `source_kind="notion"`.
- Non-production chunk kinds are excluded.
- No reranker is used in MVP.

## Current Retrieval State

Audited code paths:
- `src/db/models.py`
- `alembic/versions/989de3f24186_initial_schema.py`
- `src/orchestrators/notion_page_index_orchestrator.py`
- `src/repositories/chunk_repository.py`
- `src/rag/retriever.py`
- `src/orchestrators/qa_orchestrator.py`

Current state:
- `knowledge_chunks` stores nullable live vectors in `embedding` and keeps
  serialized JSON in `embedding_text` during rollout.
- The shared Notion indexing flow now batches page chunks through
  `EmbeddingClient` before chunk persistence.
- `ChunkRepository.list_production_chunks()` applies production-safe filters in SQL for lexical retrieval.
- `ChunkRepository.list_production_chunks_by_vector()` now applies
  production-safe filters and cosine-distance top-k in PostgreSQL when a query
  embedding is available.
- QA now generates query embeddings through `EmbeddingClient` and prefers the
  repository-owned pgvector retrieval path when PostgreSQL + pgvector are available.
- Query-time fallback is lexical-only for QA. The QA path no longer mixes
  lexical and local embedding scores after a vector fallback condition.
- Legacy pages that still have NULL vectors stay safe because query-time
  vector gaps degrade to lexical fallback on the same filtered production scope.

## Live Embedding and pgvector Retrieval Contract (Step 48)

Contract summary:
- Embedding provider and model: OpenAI `text-embedding-3-small`.
- Embedding dimensions: always send `dimensions=1536` explicitly for both chunk and query embeddings.
- Stored vector shape: nullable pgvector `vector(1536)` is the live contract. Legacy `embedding_text` stays transitional during rollout only.
- Distance metric: cosine distance.
- PostgreSQL operator and index ops: use `<=>` and `vector_cosine_ops`.
- Vector index strategy: exact cosine search on the filtered subset is the correctness baseline. A cosine HNSW index is the approved acceleration path. IVFFlat is not part of the MVP rollout contract.
- Scope: production-safe `source_kind="notion"` chunks only. No reranker.

Retrieval rules:
- Page, section, source-kind, and production-safety filters must apply before semantic top-k.
- Citations may come only from rows actually returned by retrieval.
- QA does not merge vector results and lexical results when the vector path
  succeeds. The vector path is the primary ranking path.
- Repository-owned exact cosine search remains the fallback SQL shape when filter-first correctness is clearer or safer than using the ANN index.

Fallback policy:
- Query-time lexical fallback is allowed and required when the vector path is unavailable or unusable.
- Lexical fallback must reuse the existing deterministic production-safe Notion retrieval scope.
- If lexical fallback also returns no supporting chunks, QA returns the existing insufficient-info response instead of an ungrounded answer.

Deterministic vector degradation cases:
- Missing embedding provider configuration -> lexical fallback.
- Embedding API call failure -> lexical fallback.
- Query or stored vector dimension mismatch -> lexical fallback.
- pgvector query failure -> lexical fallback.
- Eligible chunks exist but no usable stored vectors are available yet -> lexical fallback.

Indexing-side rule:
- Embedding generation failures fail closed before page replacement. The
  system does not silently commit partial page snapshots with mixed vector
  state.

## RAG QA Endpoint (Step 19)

Files:
- `src/orchestrators/qa_orchestrator.py`
- `src/app/api/routes/qa.py`

Goal:
- Expose `POST /api/qa` for grounded QA over production chunks.
- Return answer with Notion-path citations, or deterministic insufficient-info response.

Flow:
- API Route -> QA Orchestrator -> ProductionChunkRetriever -> ProviderRouter.
- Route does not call provider SDKs or database SQL directly.

Behavior:
- Retrieve production chunks using scope filters (`page_ids`, `section_paths`, `source_kinds`).
- If no chunk is retrieved, return insufficient-info response and empty citations.
- If chunks exist, build context prompt and call LLM through `ProviderRouter`.
- Return structured citations from retrieved chunk paths for deterministic citation output.

Failure handling:
- Provider missing or provider call failure returns deterministic error with workflow id.
- Invalid or empty LLM output maps to `LLM_OUTPUT_INVALID`.

## Query Embedding QA Path (Step 53)

Files:
- `src/orchestrators/qa_orchestrator.py`
- `src/rag/retriever.py`

Goal:
- Switch QA from lexical-only retrieval to query-embedding-first retrieval
  while preserving grounded citations and deterministic fallback.

Flow:
- `API Route -> QA Orchestrator -> EmbeddingClient -> ProductionChunkRetriever -> ChunkRepository -> grounded LLM answer`

Rules:
- Generate one query embedding per QA request with explicit
  `dimensions=1536`.
- When pgvector retrieval succeeds, use only the repository-returned semantic
  result set for citations and prompt context.
- When query embedding generation fails, query vector dimensions are invalid,
  pgvector retrieval fails, or the filtered scope has no live vectors yet,
  fall back to deterministic lexical retrieval on the same filtered scope.
- QA lexical fallback must not mix semantic and lexical result sets for one
  request.
- Workflow metadata records `retrieval_mode`,
  `retrieval_fallback_reason`, `embedding_provider`,
  `embedding_model`, `embedding_dimensions`, and
  `vector_distance_metric`.
- Current runtime retrieval modes are `pgvector_exact_cosine` and
  `lexical_fallback`. The migration includes an HNSW index as an acceleration
  option, but the application does not emit a separate HNSW retrieval mode.

## Same-page Snapshot Safety (Step 62)

- Build and embed the complete page snapshot before entering the short DB
  transaction, then lock the page key before replacing stored blocks/chunks.
- Compare timestamps in UTC. An older prepared snapshot is rejected with
  `STALE_PAGE_SNAPSHOT`, so stale content cannot delete or replace current RAG
  rows.
- Existing pages with NULL `last_edited_time` are accepted deterministically;
  a timestamp-less reader update preserves a timestamp already stored for the
  page.

## Synthetic Data Exclusion (Step 87)

Production retrieval accepts Notion chunks by `source_kind`, so synthetic
Notion rows must not be present in the live PostgreSQL database. The indexing
orchestrator blocks known synthetic page ids and mock-source writes when the
database dialect is PostgreSQL. Demo and deterministic eval flows continue to
use ephemeral SQLite state.

The fixed synthetic allowlist is inspected by
`scripts/cleanup_synthetic_data.py`, and `scripts/release_gate.py` fails
closed if any allowlisted page, block, or production-eligible chunk remains.
Cleanup is explicit, transactional, and does not access Notion. This is a
release invariant; it is not a retrieval-time substitute for the existing
production source and pending/rejected-state filters.
