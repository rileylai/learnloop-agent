# ADR-0006: Bounded Embedding Execution Contract

## Status

Accepted

## Date

2026-08-06

## Context

LearnLoop indexes every chunk from one Notion page before replacing that
page's derived database snapshot. The current indexing path sends all chunk
texts in one embedding request.

Step 96 established that the affected production-equivalent page produced
2,483 embedding inputs. That exceeds the documented OpenAI limit of 2,048
inputs in one embedding request and is the supported primary cause of the
observed HTTP 400. The original provider response body was not retained, so
there is no direct provider error-code confirmation. The same configured
model and dimensions succeeded in bounded requests through 64 inputs.

The existing page preparation order is safety-relevant: Notion read,
chunking, and embedding complete before repository replacement begins. An
embedding failure therefore leaves the prior page/block/chunk/vector snapshot
unchanged. Step 97 must fix request execution without weakening that boundary.

ADR-0003 remains authoritative for the OpenAI model, 1,536 dimensions,
pgvector storage, retrieval metric, retrieval fallback, and the rule that
indexing fails closed. This ADR adds only the indexing-time embedding
execution contract.

## Decision

### 1. Ownership boundaries

- The page-index orchestrator owns page workflow sequencing. It obtains chunks,
  requests one complete embedding result, constructs a complete prepared page
  snapshot, and only then invokes page replacement.
- A small `EmbeddingBatchService` owns batch planning, sequential execution,
  bounded retry, response validation, stable reassembly, and aggregate usage
  metadata. It has no repository or Notion dependency.
- The embedding provider adapter owns one upstream request per call, provider
  and model capability lookup, safe transport classification, and bounded
  `Retry-After` parsing. It does not plan page batches, retry requests, or
  persist results.
- The injected HTTP transport performs one attempt and returns a typed,
  sanitized success or failure.
- The read-only Notion client owns bounded retry for its own read operations.
  The Notion writer does not inherit or reuse the read retry policy.

This keeps API Route -> Orchestrator -> Service / Provider / Tool -> Repository
boundaries intact and gives deterministic tests one service seam for embedding
execution.

### 2. Provider capability and operational budget sources

- The OpenAI adapter exposes an immutable, reviewed capability profile keyed by
  provider and model. The initial profile covers only the already-supported
  `text-embedding-3-small` contract and explicit 1,536 dimensions.
- A provider profile supplies hard ceilings such as the documented 2,048-input
  request limit. A setting may only narrow a hard ceiling; it cannot expand it.
- Local byte and estimated-token budgets are operational safety limits. They
  are not represented as provider billing usage and are not evidence of an
  undocumented provider hard limit.
- Capability lookup or service construction fails closed for an unknown
  provider/model/dimensions combination or a configured value that exceeds a
  known hard ceiling.
- Step 97 does not add a second provider, provider routing, or dynamic provider
  discovery.

### 3. Batch planning

The planner receives the complete ordered embedding input list and a validated
effective capability/budget object. It performs a full preflight before the
first provider request.

- Inputs retain their zero-based original ordinals.
- Empty or whitespace-only inputs fail preflight.
- An input that exceeds either the configured single-input byte budget or the
  configured single-input estimated-token budget fails preflight. A chunk is
  never split by the batch service.
- The planner walks inputs once in original order and creates contiguous
  batches greedily. It adds the next input only when the resulting batch stays
  within the input-count, aggregate byte, and aggregate estimated-token limits.
- If adding the next input would exceed any limit, the current non-empty batch
  closes and a new batch starts with that input.
- Inputs are never sorted by size, deduplicated, or reordered.
- The current versioned UTF-8-byte estimator may be used for operational token
  estimates. Its values remain estimates, not tokenizer truth or provider
  usage.

The initial execution concurrency is fixed at `1` and is not configurable in
Step 97.

### 4. Retry and `Retry-After`

The transport and adapter classify a single failed attempt. The caller that
owns the operation owns retry execution:

- `EmbeddingBatchService` retries an embedding batch.
- The read-only Notion client retries an individual read request.

Only client timeout, transport unavailability, HTTP 408, HTTP 429, and the
allowlisted HTTP 500, 502, 503, and 504 statuses are retryable. Authentication
failures, HTTP 400, 413, 422, other deterministic 4xx responses, non-allowlisted
5xx responses, invalid success responses, planning failures, response-count
mismatches, and vector-dimension mismatches are not retried.

Retry is bounded by a configured maximum attempt count and capped exponential
backoff. A safe numeric `Retry-After` may increase the wait for a retryable
response, but the effective wait is still capped by the configured maximum.
Date-form or malformed values are ignored. Tests inject the sleeper and never
perform wall-clock waits.

A retry repeats only the current batch. Completed batches are retained in
memory and are not sent again. If attempts are exhausted, the service discards
its accumulated result and raises one sanitized failure.

### 5. Stable result ordering and validation

Each provider response is treated as ordered to match its request. Before any
batch result is accepted, the service validates:

- provider and model match the requested capability profile;
- response embedding count equals that batch's input count;
- every vector has exactly 1,536 dimensions.

Each accepted vector is associated with the input's original ordinal. After
the last batch, the service verifies that ordinals are contiguous from zero,
that every ordinal occurs exactly once, and that the total vector count equals
the original input count. Only then does it expose the ordered aggregate
result to the orchestrator.

### 6. Usage and cost aggregation

- Provider-reported input-token usage is summed across successful batches.
- If any successful batch omits provider usage, page-level token usage and
  estimated cost remain unknown rather than undercounted.
- Failed attempts are not assigned estimated provider usage.
- Cost is calculated once from the complete provider-reported token total and
  the existing pricing contract after all batches succeed.
- Batch count and retry count may be recorded as safe numeric metadata. Input
  text, payloads, vectors, and raw upstream messages remain prohibited.

### 7. Page replacement and failure behavior

The batch service keeps all vectors in memory and returns nothing partial. The
orchestrator does not create a `PreparedNotionPageSnapshot` until every batch
has succeeded and the complete ordered result has passed validation.

No repository replacement method or unit of work may begin during Notion read,
chunking, batch planning, embedding execution, retry, or result validation. A
failure at any of those stages leaves the existing page, block, chunk, and
vector rows exactly unchanged. Successful preparation continues to use the
existing transactional page-replacement path.

No partial batch embeddings are stored in a database, cache, file, workflow
metadata field, or diagnostic artifact.

### 8. Full-index partial outcome

Full index continues to process pages sequentially using the page-index
orchestrator. If one page fails:

- pages committed before it remain committed;
- the failed page's prior complete snapshot remains unchanged;
- later pages are not attempted;
- the workflow retains its existing failed-page, succeeded-page,
  processed-count, and remaining-page partial-outcome metadata;
- the failure maps to the existing safe workflow failure taxonomy.

Step 97 does not make the entire full index one transaction and does not add
cross-page rollback.

## Consequences

- Large pages can exceed a provider request limit without exceeding one page's
  atomic replacement boundary.
- The batching service is reusable by other indexing entry points that already
  share the page-index orchestrator, without putting batching in routes or
  provider transports.
- Sequential execution is slower than parallel embedding calls but has simpler
  rate, ordering, cost, and failure behavior for the first reliability change.
- Conservative operational estimates can reject an input before a provider
  request. They reduce risk but do not replace exact provider tokenization.
- Missing usage makes cost unknown rather than silently incomplete.
- Retry can increase request duration, but attempts and waits are bounded and
  deterministic under injected tests.

## Alternatives Rejected

### Batch in the orchestrator

Rejected because provider execution policy, retry, validation, and usage
aggregation would make the page workflow harder to test and would duplicate
behavior across indexing entry points.

### Batch inside the provider adapter

Rejected because an adapter should represent one provider operation. Hidden
sub-requests would obscure retry, usage, request count, and page-level atomicity
from the application service.

### Retry in the HTTP transport

Rejected because transports cannot apply operation-specific safety rules or
expose deterministic attempt behavior to service tests.

### Persist each successful batch

Rejected because it would create partial vector state and weaken the existing
fail-before-replacement contract.

### Add concurrency in the first implementation

Rejected for Step 97. Concurrency remains fixed at `1` until a separate change
defines rate, ordering, retry, and evaluation evidence.

## Non-goals

- Context-aware embedding inputs or title/path prefixes
- Hybrid retrieval or reciprocal-rank fusion
- Parent-child retrieval
- Reranking
- A second embedding provider
- Retrieval ranking changes
- Full-index transactionality
- Persisting derived embedding input text
