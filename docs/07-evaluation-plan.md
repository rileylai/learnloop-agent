# 07 Evaluation Plan

## Purpose
This document defines retrieval hit rate, citation accuracy, write safety, and sync reconciliation tests.

## Status
Active for evaluation and regression steps.

## Verification Levels

Evaluation evidence must state its dependency level:

| Level | Meaning | Current examples |
|---|---|---|
| `deterministic` | Fake/in-memory adapters and synthetic public-safe data. | Golden retrieval, citation, vector fallback, write safety, manual sync, mock demo. |
| `adapter_integration` | Real parser/client library against controlled fixtures or mocked HTTP transport. | Partial coverage only; several parser and Telegram implementations still rely on fake clients in API tests. |
| `live_dependency` | Real credential or service for one bounded dependency. | PostgreSQL/pgvector repository coverage exists; OpenAI vector smoke is opt-in and was not run in the latest audit. |
| `live_e2e` | Real user flow across all required external systems. | None currently. |

Passing deterministic tests must not be reported as proof of real Notion,
OpenAI generation, Telegram, URL, YouTube, or OCR E2E readiness.

## Golden Question Set

The versioned golden question set is stored at:

`tests/evals/golden_questions.yaml`

It contains synthetic examples only. It must not contain private Notion content.

Step 36 starts with three required categories:

| Category | Purpose |
|---|---|
| `nlp` | Verify retrieval and citation for existing manual notes. |
| `iso_9001` | Verify a second knowledge domain and path shape. |
| `ai_supplement_zone` | Verify accepted AI supplement content can be retrieved from production RAG. |

Each question records:

- a stable unique id and query
- deterministic page, section, source-kind, and top-k scope
- expected Notion paths
- expected content state: `manual_note` or `accepted_ai_supplement`
- answer terms that must or must not appear
- deterministic retrieval, citation, and production-RAG exclusion checks

Accepted AI supplement expected paths must be under `AI Supplement Zone`.
Manual note expected paths must not be under `AI Supplement Zone`.
Pending and rejected change request content must never be an expected production result.

## Loading and Validation

`tests/evals/golden_questions.py` loads YAML with `yaml.safe_load` and validates
the complete structure before an eval can run. It rejects unknown fields,
duplicate ids, invalid scopes, and ownership-model path mismatches.

Run the standalone validation command:

```bash
uv run python tests/evals/golden_questions.py
```

## Planned Deterministic Metrics

- Retrieval hit rate: expected path appears in top-k retrieved paths.
- Citation accuracy: returned citation path matches an expected source path.
- Vector retrieval regression: semantic ranking, lexical fallback reason,
  citation de-duplication, and production-RAG exclusion stay deterministic.
- Write safety: original blocks stay unchanged and append occurs only under
  `AI Supplement Zone`.
- Manual sync reconciliation: deleted Notion content is removed after
  page-level replacement sync.
- Production-RAG exclusion: pending and rejected content is absent.

No LLM-as-judge is used in MVP evaluation.

## Retrieval Hit Rate Evaluation

`tests/evals/retrieval_eval.py` measures whether each golden question's expected
path appears in the top-k paths returned by `ProductionChunkRetriever`.

The MVP Step 37 script uses a synthetic in-memory SQLite fixture built from the
golden question set. This keeps the regression deterministic before public mock
Notion data exists. It still exercises the real repository and retriever path:

`Golden Questions -> Synthetic Notion chunks -> ChunkRepository -> ProductionChunkRetriever -> Hit-rate calculation`

Matching rules:

- Compare expected paths against retrieved top-k paths with exact string match.
- Count one hit per golden question when at least one expected path appears.
- Compute `hit_rate = hit_count / total_questions`.
- Keep retrieval scoped to `source_kind="notion"`.
- Exclude non-production source chunks from retrieved results.

Run:

```bash
uv run python tests/evals/retrieval_eval.py
```

Expected output includes:

```text
retrieval_hit_rate: 1.000 (3/3)
```

## Citation Accuracy Evaluation

`tests/evals/citation_accuracy_eval.py` measures whether deterministic QA
citation paths match the expected source paths in the golden question set.

The MVP Step 38 script uses the same synthetic in-memory SQLite fixture as the
retrieval hit-rate eval. It retrieves production-safe Notion chunks, converts
their `notion_path` values into unique citation paths, then compares those
paths to each golden question's expected paths.

Matching rules:

- Compare citation paths against expected paths with exact string match.
- Count one accurate citation result per golden question when at least one
  expected path appears in the citation paths.
- Compute `citation_accuracy = accurate_count / total_questions`.
- Default threshold is `1.0`.
- Keep citation sources scoped to `source_kind="notion"`.
- Do not inspect or judge generated answer text.

Run:

```bash
uv run python tests/evals/citation_accuracy_eval.py
```

Expected output includes:

```text
citation_accuracy: 1.000 (3/3)
threshold: 1.000
status: pass
```

## Vector Retrieval Regression Evaluation

`tests/evals/vector_retrieval_eval.py` freezes deterministic vector-first QA
retrieval behavior without real OpenAI calls, real PostgreSQL, or
LLM-as-judge.

The Step 54 eval uses a deterministic fake embedding fixture and an in-memory
vector-capable repository fixture to exercise the real
`ProductionChunkRetriever.retrieve_with_metadata()` decision path.

Checks:

- Semantic ranking returns `pgvector_exact_cosine` when vector results are
  available.
- Query-time vector failure falls back to lexical retrieval with
  `retrieval_fallback_reason=VECTOR_QUERY_FAILED`.
- Missing usable vectors in the filtered scope falls back to lexical retrieval
  with `retrieval_fallback_reason=VECTOR_DATA_UNAVAILABLE`.
- Duplicate retrieved paths collapse into unique citation paths.
- Production RAG excludes non-Notion chunks even when they would otherwise be
  the highest-scoring semantic match.

Run:

```bash
uv run python tests/evals/vector_retrieval_eval.py
```

Expected output includes:

```text
vector_retrieval_regression: pass (4/4)
```

## Live PostgreSQL + OpenAI Vector Smoke Verification

`tests/evals/live_vector_smoke.py` is the Step 55 opt-in live smoke command.
It stays outside the default unit suite and only runs when a developer
explicitly enables it.

Purpose:

- confirm shared page indexing stores live pgvector embeddings through the real
  OpenAI embedding client
- confirm PostgreSQL-side pgvector retrieval returns
  `pgvector_exact_cosine`
- confirm duplicate raw chunk hits collapse into unique citation paths
- confirm scoped-empty QA requests return the deterministic
  `insufficient_info` answer
- confirm repeated page re-index does not create duplicate chunk rows

This smoke step intentionally keeps the answer provider deterministic and local.
It also uses an in-memory Notion reader rather than the real Notion API.
The live dependency under test is the vector path:

`NotionPageIndexOrchestrator -> OpenAIEmbeddingClient -> ChunkRepository -> PostgreSQL + pgvector -> ProductionChunkRetriever -> QAOrchestrator citations`

Therefore, a passing Step 55 smoke proves the embedding/storage/retrieval
boundary only. It does not prove real Notion indexing, real LLM answer
generation, proposal review, Notion append, or Telegram E2E.

The smoke command creates a temporary database, runs the project's real
Alembic migrations to `head`, then executes the live checks against that
isolated schema. It does not rely on partial `Base.metadata.create_all()`
table creation.

Prerequisites:

- local PostgreSQL + pgvector is reachable, usually from
  `docker compose up -d postgres`
- `OPENAI_API_KEY` is set
- the run is explicitly opted in with `LEARNLOOP_RUN_LIVE_VECTOR_SMOKE=1`

Run:

```bash
LEARNLOOP_RUN_LIVE_VECTOR_SMOKE=1 \
OPENAI_API_KEY=... \
uv run python tests/evals/live_vector_smoke.py
```

Optional:

```bash
LEARNLOOP_RUN_LIVE_VECTOR_SMOKE=1 \
OPENAI_API_KEY=... \
uv run python tests/evals/live_vector_smoke.py --keep-database-on-failure
```

If local PostgreSQL is not on the default docker-compose URL, set
`LEARNLOOP_PGVECTOR_ADMIN_DATABASE_URL` or pass `--admin-database-url`.

Expected output includes:

```text
live_vector_smoke: pass (5/5)
```

## Write Safety Evaluation

`tests/evals/write_safety_eval.py` checks deterministic Notion write-safety
invariants using the in-memory Notion writer client. It does not call real
Notion.

Checks:

- Accepted append keeps original/manual blocks unchanged.
- The only write operation is `append_ai_supplement_zone`.
- The append target path stays under `AI Supplement Zone`.
- Retry with the same change request is idempotent and creates no duplicate
  supplement entry.
- Write-policy violations fail closed with `WRITE_POLICY_VIOLATION` and no
  append operation.

Run:

```bash
uv run python tests/evals/write_safety_eval.py
```

Expected output includes:

```text
write_safety: pass (4/4)
```

## Manual Sync Reconciliation Evaluation

`tests/evals/manual_sync_eval.py` checks deterministic manual Notion sync
reconciliation. It uses an in-memory Notion reader and SQLite database, then
exercises the real indexing orchestrators, repositories, chunker, and production
retriever path.

The eval indexes a synthetic page that contains manual content and an accepted
AI supplement under `AI Supplement Zone`. It then simulates the user manually
deleting that AI supplement in Notion and runs manual incremental sync.

Checks:

- The AI supplement chunk is retrievable before manual sync.
- After manual sync, the deleted AI supplement chunk is absent from production
  retrieval and raw Notion chunks.
- Manual note chunks from the same page remain retrievable.
- Incremental sync completes with `sync_mode=manual` and page-level replacement
  metadata.

Run:

```bash
uv run python tests/evals/manual_sync_eval.py
```

Expected output includes:

```text
manual_sync_reconciliation: pass (4/4)
```
