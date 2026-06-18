# ADR-0003: Live Embedding and pgvector Retrieval Contract

## Status
Accepted

## Date
2026-06-19

## Context
LearnLoop already has an embedding client abstraction and a retriever abstraction,
but the live vector path is not wired yet.

Audited current state before this ADR:
- `OpenAIEmbeddingClient` already defaults to `text-embedding-3-small` and
  supports an optional `dimensions` parameter.
- `knowledge_chunks` currently stores only optional serialized embeddings in
  `embedding_text`.
- The shared page indexing flow does not yet call `EmbeddingClient`.
- Production QA currently uses lexical retrieval by default. Optional cosine
  scoring exists only when a caller manually supplies a query embedding.

Step 48 exists to lock the live vector contract before Step 49-55 change schema,
indexing, retrieval, and smoke verification behavior.

## Decision

### 1. Embedding model contract
- LearnLoop will use OpenAI `text-embedding-3-small` for the first live vector
  rollout.
- The same model will be used for chunk embeddings and query embeddings.
- The system will send `dimensions=1536` explicitly on live embedding requests
  instead of relying on provider defaults.
- MVP does not support per-route or per-source embedding model switching.

### 2. Stored vector contract
- Step 49 will introduce a nullable pgvector column with shape
  `vector(1536)`.
- Existing `embedding_text` remains transitional during rollout so old rows and
  deterministic tests can migrate safely.
- The long-term retrieval source is the pgvector column, not serialized JSON
  text.

### 3. Similarity metric contract
- Semantic retrieval uses cosine distance.
- PostgreSQL queries use pgvector cosine operators and `vector_cosine_ops`.
- This keeps the SQL contract aligned with the current retriever's cosine
  mental model and avoids switching score semantics during rollout.
- Inner product remains a future optimization candidate, but it is not the
  Step 48 contract.

### 4. Vector index strategy contract
- Exact cosine search over the already filtered candidate set is the
  correctness baseline.
- A cosine HNSW index is the approved acceleration path for the MVP rollout.
- IVFFlat is not part of the MVP rollout contract.
- Repository queries may still choose exact filtered cosine ordering when that
  is safer for filter-before-top-k correctness.
- Conventional filter indexes remain part of the plan alongside the vector
  index.

### 5. Retrieval scope contract
- Production QA remains limited to production-safe Notion chunks in MVP.
- Page, section, source-kind, and production-safety filters must apply before
  top-k selection.
- No reranker is allowed in MVP.
- Citations must come only from rows actually returned by retrieval.

### 6. Fallback contract
- When the vector path is unavailable or unusable, QA must fall back to the
  existing deterministic lexical retrieval path over the same production-safe
  scope.
- Vector success and lexical fallback are mutually exclusive ranking modes for a
  single query. Step 53 should not merge the two result sets.
- If lexical fallback retrieves no supporting chunks, the QA workflow returns
  the existing insufficient-info response.

### 7. Deterministic failure and observability contract
- Vector-path failures that still allow safe lexical fallback should not mark
  the QA workflow failed.
- QA workflow metadata must record:
  - `retrieval_mode`
  - `retrieval_fallback_reason`
  - `embedding_provider`
  - `embedding_model`
  - `embedding_dimensions`
  - `vector_distance_metric`
- Approved lexical fallback reasons are:
  - `EMBEDDING_PROVIDER_NOT_CONFIGURED`
  - `EMBEDDING_PROVIDER_ERROR`
  - `VECTOR_DIMENSION_MISMATCH`
  - `VECTOR_QUERY_FAILED`
  - `VECTOR_DATA_UNAVAILABLE`
- Indexing-time embedding generation is different from query-time fallback:
  Step 50 must fail closed on embedding-generation errors instead of silently
  writing partial mixed-vector page state.

## Consequences
- Step 49 now has a locked vector dimension and distance contract.
- Step 52 can implement repository-owned pgvector queries without reopening
  metric or index debates.
- Step 53 can preserve current QA safety by keeping lexical fallback explicit,
  deterministic, and observable.
- Rollout stays local-first and correctness-first: exact filtered cosine search
  remains the baseline even when an ANN index is introduced for acceleration.
