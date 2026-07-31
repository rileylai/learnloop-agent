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
| `adapter_integration` | Real parser/client library against controlled fixtures or an injected HTTP transport. | `pypdf`, trafilatura, Notion REST, Telegram HTTP, OpenAI transport mapping, and conditional Tesseract adapter coverage. |
| `live_dependency` | Real credential or service for one bounded dependency. | Step 82 Notion read/index/QA, Step 83 approved sandbox append, and Step 87 PostgreSQL cleanup/release gate passed within their stated scopes. |
| `live_e2e` | Real user flow across all required external systems. | None currently. |

Passing deterministic tests must not be reported as proof of real Notion,
OpenAI generation, Telegram, URL, YouTube, or OCR E2E readiness.

Current audit baseline on 2026-08-01: the full deterministic suite completed
with `399 passed, 3 skipped`. The skipped cases are opt-in live PostgreSQL
repository tests and are not passing live evidence. The test-profile preflight
passed with warnings for unconfigured live dependencies.

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
uv run --no-env-file --frozen python tests/evals/golden_questions.py
```

## Deterministic Metrics

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
uv run --no-env-file --frozen python tests/evals/retrieval_eval.py
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
uv run --no-env-file --frozen python tests/evals/citation_accuracy_eval.py
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
uv run --no-env-file --frozen python tests/evals/vector_retrieval_eval.py
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
uv run --no-env-file --frozen python tests/evals/live_vector_smoke.py
```

Optional:

```bash
LEARNLOOP_RUN_LIVE_VECTOR_SMOKE=1 \
OPENAI_API_KEY=... \
uv run --no-env-file --frozen python tests/evals/live_vector_smoke.py --keep-database-on-failure
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
uv run --no-env-file --frozen python tests/evals/write_safety_eval.py
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
uv run --no-env-file --frozen python tests/evals/manual_sync_eval.py
```

Expected output includes:

```text
manual_sync_reconciliation: pass (4/4)
```

## Prompt-Injection and Adversarial Evaluation (Step 80)

`tests/evals/prompt_injection_eval.py` runs deterministic checks with synthetic
public-safe data. It does not call an LLM and does not require an API key.

Checks include:

- English and Traditional Chinese source/context instructions remain inside
  explicit untrusted-data prompt blocks.
- Proposal target paths remain scoped to the selected page's `AI Supplement Zone`.
- Backend-derived citation paths stay accurate and production-RAG retrieval
  excludes unsafe/pending/rejected paths.
- Append-only write safety and fail-closed `WRITE_POLICY_VIOLATION` behavior
  remain intact.

Run:

```bash
uv run --no-env-file --frozen python tests/evals/prompt_injection_eval.py
```

The evaluation reports `prompt_injection: pass (5/5)` when all deterministic
checks pass. It is not evidence of live model resistance; live provider tests
remain opt-in and must never replace backend invariants.

## Screenshot Proposal Quality Evaluation

Screenshot OCR language coverage is deterministic at the adapter boundary:

- `tests/test_image_ocr_tool.py` verifies that every Tesseract call uses the
  exact `eng+chi_tra+chi_sim` language set and that a missing required
  traineddata language fails before OCR without an English fallback.
- `tests/test_preflight.py` injects a stdlib subprocess runner and covers
  complete, missing, timed-out, failed, and malformed `tesseract --list-langs`
  results without exposing command stderr.
- `tests/test_source_ingest_api.py` uses public-safe mixed-script parser output
  to prove that CJK characters and image order survive preprocessing,
  persistence, and source-snapshot construction. It checks the existing
  language enum without hard-coding a particular non-English enum.

These tests do not prove live Tesseract recognition quality. Real Chinese OCR
requires installed `eng`, `chi_tra`, and `chi_sim` traineddata and a separately
approved re-upload that creates a new source document.

`tests/evals/test_screenshot_proposal_eval.py` uses the public-safe fixture
`tests/fixtures/screenshot_proposal_fixtures.json`. It does not call an LLM,
write to Notion, modify SQL data outside its isolated test database, or delete
Redis state.

The fixtures cover:

- continuous content split across multiple images, merged in message-id order;
- browser tab/address/navigation noise removal;
- Traditional Chinese language selection with original technical terms;
- reasonable English and Traditional Chinese paraphrase acceptance;
- four- and five-image live-shaped MySQL/EXPLAIN Traditional Chinese titles
  with CJK OCR spacing noise, 20–40 character noun phrases, no-number title
  cases, mixed punctuation, and bounded claim-level diagnostics;
- public-safe workflow-252/255-shaped proposals with exactly 15/16 validation
  units and 7/9 matches, proving that counts span summary plus complete concept
  and note items rather than splitting one summary into phrase fragments;
- MySQL/索引/EXPLAIN/SQL title anchors, mixed technical punctuation, and
  deterministic title fallback without another OCR/provider call, including
  unmatched general CJK anchors that remain valid with a matched
  high-specificity anchor;
- deterministic rejection of unsupported products, numbers/percentages,
  technical content, advice, comparisons, conclusions, and browser-noise
  evidence without a second full-proposal LLM judge;
- one summary-only repair using the same source snapshot, with a second
  failure bounded to `LLM_OUTPUT_INVALID` and no new source/OCR row.
- one body-only repair for safe multi-item paraphrase failures, including the
  title-repair-to-body-repair transition and a second failure bounded to
  `LLM_OUTPUT_INVALID`.

Run:

```bash
uv run --no-env-file --frozen pytest -q tests/evals/test_screenshot_proposal_eval.py
```

## Real-Library Adapter Smoke Matrix (Step 81)

`tests/evals/adapter_smoke_matrix.py` runs a small redacted matrix against the
real PDF, OCR, and URL parser libraries. PDF and URL use in-process fixtures
and injected transports, so the default run does not use the network, a
credential, or an external write. OCR passes when the local Tesseract runtime
is available and otherwise skips unless `--require-ocr` is supplied.

Run the default matrix:

```bash
uv run --no-env-file --frozen python tests/evals/adapter_smoke_matrix.py --json
```

The report contains only check id, dependency level, status, and fixed safe
messages. It never includes API keys, URLs, exception bodies, or extracted
source text. The default matrix is not evidence of live service connectivity.

Current 2026-08-01 result: the `pypdf`, Tesseract, and trafilatura fixture
checks passed. YouTube, OpenAI, PostgreSQL, and Telegram live checks were
skipped because live mode was disabled.

Opt-in live checks require `--live` or
`LEARNLOOP_RUN_ADAPTER_SMOKE_LIVE=1`. The YouTube check requires
`LEARNLOOP_SMOKE_YOUTUBE_URL`; the OpenAI check requires `OPENAI_API_KEY`; the
PostgreSQL check requires `LEARNLOOP_SMOKE_DATABASE_URL`; and the Telegram
send check requires `TELEGRAM_BOT_TOKEN`,
`LEARNLOOP_SMOKE_TELEGRAM_CHAT_ID`, and
`LEARNLOOP_SMOKE_ALLOW_TELEGRAM_SEND=1`. Telegram sends a synthetic smoke
message and must use a dedicated test chat. Live checks may use network,
database, or provider quota and are never part of the default pytest suite.

## Guarded Notion Read/Index/QA Canary (Step 82)

`tests/evals/notion_read_index_qa_canary.py` is the opt-in canary for a
dedicated synthetic Notion workspace. It discovers pages, runs full indexing,
re-indexes one configured page through the manual incremental path, and runs
scoped QA with a deterministic local answer provider. Its database state is
ephemeral SQLite state and its embedding provider is deterministic, so the
canary requires only a Notion token.

The live wrapper requires `NOTION_TOKEN`,
`LEARNLOOP_NOTION_CANARY_PAGE_ID`, and an optional
`LEARNLOOP_NOTION_CANARY_QUERY` (default:
`LearnLoop Step 82 canary anchor`). Run it only against a dedicated synthetic
workspace:

```bash
LEARNLOOP_RUN_NOTION_READ_CANARY=1 \
  uv run --no-env-file --frozen python \
  tests/evals/notion_read_index_qa_canary.py --json
```

The wrapper records only fixed operation classes and blocks all write-shaped
requests before dispatch. A passing report requires a full index, an
incremental page, a scoped citation, and zero Notion write attempts. A failed
report includes only the fixed `failed_stage` values `configuration`,
`full_discovery`, `page_preparation`, `embedding`, `db_persistence`,
`incremental_index`, `qa`, or `write_audit`, plus a standard `failure_reason`.
It never prints page ids, titles, paths, source text, credentials, or exception
bodies.
This is read/index/QA evidence only; the human-approved append canary is Step
83.

Recorded Step 82 evidence: `2` indexed pages, `11` blocks, `4` chunks, `1`
incremental page, `1` citation, `9` read-only Notion requests, and `0` write
attempts. This is bounded sandbox evidence, not a current workspace-wide test.

## Human-approved Notion Append Canary (Step 83)

`tests/evals/notion_append_canary.py` reuses the existing human accept
orchestrator with a real Notion reader/writer and ephemeral SQLite derived
state. It requires both live opt-in and explicit approval:

```bash
uv run --no-env-file --frozen python \
  tests/evals/notion_append_canary.py --live --approve --json
```

The transport permits page/block reads and append-only
`PATCH /v1/blocks/{id}/children`. Passing requires `pending -> accepted`, a
visible `change-request-<id>` identity, target-page re-index, and a scoped QA
citation. A human-confirmed dedicated sandbox run passed during Step 83. It is
opt-in live dependency evidence only; it does not prove Telegram delivery,
OpenAI behavior, arbitrary workspace permissions, or full live E2E.

## Synthetic Data Hygiene Gate (Step 87)

`tests/test_synthetic_data_hygiene.py` verifies the fixed allowlist, dry-run
default, explicit apply confirmation, transactional cleanup, preservation of
non-synthetic rows, PostgreSQL persistence blocking, and fail-closed release
gate behavior. Run the operator checks with:

```bash
uv run --no-env-file --frozen python scripts/cleanup_synthetic_data.py --json
uv run --no-env-file --frozen python scripts/release_gate.py --json
```

The default mock fixtures are test/demo inputs, not release evidence. A live
release requires a successful gate against the intended PostgreSQL database;
an unavailable database is a failed inspection and must not be interpreted as
clean.

Recorded Step 87 evidence: the fixed-allowlist cleanup inspection and release
gate passed against the configured live PostgreSQL target. This proves only
the inspected database state at that run; it does not replace a new release
gate execution for a later release candidate.

## Current Release Verification Gaps

- No complete Telegram update -> HTTPS webhook -> API -> Redis/RQ worker ->
  PostgreSQL -> OpenAI -> Notion -> Telegram reply E2E has passed.
- The latest audit did not run live OpenAI vector smoke, YouTube transcript,
  Telegram send, or adapter live checks.
- The current host passes the `eng`, `chi_tra`, and `chi_sim` OCR preflight and
  real-adapter fixture. A live retest with real user screenshots has not been
  run, so recognition quality and Telegram upload behavior remain unverified.
- Step 82/83 cover dedicated Notion canaries, not formal behavior across the
  user's full workspace.
- The PostgreSQL restore drill has deterministic coverage, but no recorded
  live disposable restore drill.
