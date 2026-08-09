# Evaluation Plan

The repository uses deterministic tests for policy and workflow correctness.
External dependency checks are separate, explicitly enabled operations and
must use synthetic or dedicated resources.

## Default checks

Install the locked development environment and run the normal suite:

```bash
uv sync --dev
uv run --no-env-file --frozen pytest -q
```

Useful focused commands are:

```bash
uv run --no-env-file --frozen python scripts/preflight.py --profile test --json
uv run --no-env-file --frozen python tests/evals/retrieval_eval.py
uv run --no-env-file --frozen python tests/evals/citation_accuracy_eval.py
uv run --no-env-file --frozen python tests/evals/vector_retrieval_eval.py
uv run --no-env-file --frozen python tests/evals/write_safety_eval.py
uv run --no-env-file --frozen python tests/evals/manual_sync_eval.py
uv run --no-env-file --frozen python tests/evals/prompt_injection_eval.py
```

The default suite must remain independent of real Notion writes, Telegram
sends, provider quota, and destructive database operations.

## Evaluation areas

| Area | What the checks protect |
| --- | --- |
| API and schemas | Request validation, error envelopes, auth, and idempotent replay |
| Indexing | Chunk order, page replacement, complete embeddings, and partial full-index outcomes |
| Retrieval | Production filters, cosine ranking, lexical fallback, and citation paths |
| Write safety | Append-only target, human acceptance, durable identity, and no duplicate retry |
| Source ingestion | PDF, URL, YouTube, OCR, chat limits, SSRF protections, and content hashes |
| Telegram | Update ledger, queue boundaries, callbacks, ownership, TTL, reviews, and recovery |
| Observability | Redaction, readiness/liveness, cost unknowns, workflow status, and safe metrics |
| Recovery | Migration, backup/restore, stale workflows, and Notion/database reconciliation |

## Adapter checks

The adapter matrix exercises PDF, URL, OCR, and other library boundaries with
fixtures or injected transports:

```bash
uv run --no-env-file --frozen python tests/evals/adapter_smoke_matrix.py --json
```

Live adapter checks require explicit `--live` or the corresponding environment
flag. Telegram sends require a dedicated chat and an additional explicit send
flag. A skipped live check is not a pass.

## Guarded Notion checks

Read/index/QA canary:

```bash
LEARNLOOP_RUN_NOTION_READ_CANARY=1 \
  uv run --no-env-file --frozen python \
  tests/evals/notion_read_index_qa_canary.py --json
```

It requires a dedicated workspace and `NOTION_TOKEN`, blocks write-shaped
requests, and uses ephemeral derived state.

Append canary:

```bash
uv run --no-env-file --frozen python \
  tests/evals/notion_append_canary.py --live --approve --json
```

Both live opt-in and human approval are required. The canary must target a
dedicated sandbox page and verify durable identity, accepted state, page
re-index, and scoped citation. It must never be used as an implicit production
write path.

## Vector and recovery checks

The live vector smoke requires an isolated PostgreSQL/pgvector database and an
OpenAI key:

```bash
LEARNLOOP_RUN_LIVE_VECTOR_SMOKE=1 \
  uv run --no-env-file --frozen python tests/evals/live_vector_smoke.py
```

Recovery and release checks are guarded and redacted:

```bash
uv run --no-env-file --frozen python scripts/postgres_restore_drill.py --json
uv run --no-env-file --frozen python scripts/notion_db_recovery_drill.py --json
uv run --no-env-file --frozen python scripts/release_gate.py --json
```

The release gate must be run against the intended database. An unavailable
dependency is an inconclusive or failed inspection, not a clean release.

## Quality and safety criteria

- Retrieval and citation tests use exact expected Notion paths.
- Write-safety tests prove original blocks remain unchanged and rejected or
  pending content is not retrievable.
- Prompt-injection tests prove source/context text cannot change backend-owned
  targets, tools, citations, or review state.
- Test fixtures use public-safe or synthetic content and never contain secrets
  or private Notion pages.
- Live reports contain operation classes, statuses, bounded counts, and safe
  failure reasons only.
