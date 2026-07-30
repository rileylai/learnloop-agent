# 10 Deployment

## Purpose
This document defines local Docker Compose runtime and future V2 cloud deployment plan.

## Status
Draft

This document will be expanded in later steps.

What belongs here:
- Local runtime setup.
- Service dependency model.
- Future cloud deployment architecture.

## Current Deployment Readiness

The repository is demo-ready, not local-user-ready or release-ready.

- Docker Compose starts PostgreSQL/pgvector and Redis only. It does not define
  the FastAPI app or worker service; start the latter with
  `scripts/run_worker.py` after exporting `REDIS_URL`.
- `scripts/run_live.sh` is a portable repository-relative API entrypoint. It
  runs `scripts/preflight.py` first and then starts Uvicorn through the locked
  `uv` environment with `--no-env-file`. It does not load `.env` or print
  secret values.
- `scripts/preflight.py` is stdlib-only so it can report missing Python
  dependencies before importing the application. Its `api`, `test`, and `ocr`
  profiles produce a redacted dependency/configuration matrix; only
  profile-required missing items fail the command.
- The application reads process environment variables directly and does not
  auto-load `.env`.
- The running API requires PostgreSQL plus migrations for business routes.
  `/health` remains successful even when those dependencies are unavailable;
  `/ready` returns 503 when database, migration, pgvector, or required
  mode-specific provider configuration is unavailable.
- Shared page indexing requires `OPENAI_API_KEY` because embeddings fail
  closed. The one-command mock demo injects fake embeddings and is the only
  no-key indexing path.
- `NOTION_BACKEND=mock|live` selects the Notion backend and defaults to `mock`.
  Live mode constructs the read-only and append-only REST adapters and
  requires `NOTION_TOKEN`; incomplete live configuration fails closed without
  falling back to mock data.
- The append-only Notion REST writer adapter is selected with the live backend
  behind `NotionWriterTool`; it has not been verified against a real workspace.
- Telegram runtime requests enqueue background jobs through `QueueClient` when
  `REDIS_URL` is configured. Run `uv run --no-env-file --frozen python
  scripts/run_worker.py` in a separate process to consume them. Jobs use two
  bounded retries after the initial attempt; expected Telegram/domain failures
  are persisted as terminal ledger outcomes.
- Tesseract is required for OCR. Useful non-English OCR also requires matching
  language data installed on the host.
- Upload limits are enforced in API routes, orchestrators, and parser adapters;
  changing them requires updating the shared `upload_limits` policy and its
  deterministic tests. The limits bound parser/OCR memory and CPU exposure but
  do not replace reverse-proxy request-size limits in a production deployment.
- URL ingestion performs outbound requests only through its guarded URL tool:
  public-address DNS validation, per-redirect validation, bounded redirects,
  supported article content types, and a 5 MiB response limit. A production
  network policy should still restrict application egress to HTTP(S) as a
  second independent boundary.
- Telegram live use additionally needs a bot token, public HTTPS webhook
  delivery, `TELEGRAM_WEBHOOK_SECRET`, and an explicit
  `TELEGRAM_ALLOWED_CHAT_IDS` policy. Telegram and API mutation idempotency
  require applying the latest Alembic migration before starting the API.

Release-style local startup must remain blocked until portable preflight,
live Notion wiring, authentication, worker, and recovery steps in
the `Real-World Usability + Release Hardening` phase are complete.

## Liveness and Readiness

- `GET /health` is a shallow process liveness check and does not contact
  external dependencies.
- `GET /ready` checks database connectivity, current Alembic migrations,
  pgvector, and the mode-specific provider configuration. It returns `200`
  with `status=ready` only when all checks pass, otherwise `503` with safe
  check details.
- `APP_ENV=local` requires `OPENAI_API_KEY` for server-backed indexing. The
  `test`, `demo`, and `mock` modes do not require a live provider.
- Redis is required in local readiness because Telegram webhook work depends on
  the queue when `REDIS_URL` is configured. Test/demo/mock modes may skip it.

## Portable Preflight Contract

- Run `uv run --no-env-file --frozen python scripts/preflight.py --profile api`
  to check the API profile in the locked environment.
- Run `--profile test` to include development test dependencies.
- Run `--profile ocr` to require the `tesseract` executable in addition to
  Python dependencies.
- Use `--require-command COMMAND` for entrypoint-specific executable checks.
- Human and JSON output report only presence, absence, or safe status text;
  environment variable values, tokens, URLs, and filesystem values are never
  printed.
- Missing `OPENAI_API_KEY` and `TELEGRAM_BOT_TOKEN` remain warnings in the API
  profile. Missing `NOTION_TOKEN` is a warning for the default mock backend,
  but a hard failure when `NOTION_BACKEND=live`. Missing Python packages and
  entrypoint commands are hard failures.
- Missing `API_BEARER_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, and
  `TELEGRAM_ALLOWED_CHAT_IDS` are warnings for local compatibility but should
  be configured for a real deployment.
- Preflight checks dependency/configuration state only. Database, Redis,
  migration, vector, and external-service connectivity belong to the later
  readiness step.

## Adapter Smoke Matrix

Before a live canary, run the real-library adapter matrix with the locked
environment:

```bash
uv run --no-env-file --frozen python tests/evals/adapter_smoke_matrix.py --json
```

The default run is local-only. It verifies PDF and URL extraction with
controlled fixtures and verifies OCR only when the local Tesseract executable
is available. Missing optional OCR runtime is reported as `skipped`; use
`--require-ocr` when the deployment requires OCR.

Use `--live` only with dedicated synthetic resources. Live checks are opt-in
for YouTube transcript access, OpenAI embeddings, PostgreSQL connectivity, and
an explicitly permitted Telegram synthetic send. The matrix does not call
Notion and never performs a Notion write. Keep the JSON report as release
evidence only after checking that it contains no secret or private content.

## Guarded Notion Read/Index/QA Canary

After the adapter matrix passes, the read-only Notion canary may be run against
a dedicated synthetic workspace. It uses ephemeral SQLite state and local
deterministic embedding/answer adapters; no OpenAI key or production database
is required. Set `NOTION_TOKEN`,
`LEARNLOOP_NOTION_CANARY_PAGE_ID`, and, when the fixture uses a different
anchor, `LEARNLOOP_NOTION_CANARY_QUERY`, then run:

```bash
LEARNLOOP_RUN_NOTION_READ_CANARY=1 \
  uv run --no-env-file --frozen python \
  tests/evals/notion_read_index_qa_canary.py --json
```

The transport blocks non-reader operations before dispatch. Do not continue to
Step 83 unless the report is `passed`, the target workspace is synthetic, and
the report shows zero Notion write attempts. If it fails, use the redacted
`failed_stage` and `failure_reason` fields to diagnose the local index/QA
boundary; the report does not expose exception text. This canary does not
authorize or perform an append.

## Local Secret Handling

- Keep runtime secrets in local shell environment or ignored `.env` files only.
- `.env.example` may show placeholder variable names, but must not contain real
  credentials.
- `.env` and `.env.*` must stay ignored by Git so local Notion, OpenAI, and
  Telegram credentials never enter the repository.

## Live Vector Rollout Contract

- The first live vector rollout uses OpenAI `text-embedding-3-small` with
  explicit `dimensions=1536`.
- Local PostgreSQL must have the `vector` extension available before Step 49
  migrations run.
- The rollout database shape is a nullable pgvector `vector(1536)` column plus
  transitional legacy `embedding_text` while old rows are being migrated.
- Exact cosine search on the filtered subset is the correctness baseline. A
  cosine HNSW index is the approved acceleration path. IVFFlat is not part of
  the MVP rollout contract.
- Step 49 migration foundation enables `CREATE EXTENSION IF NOT EXISTS vector`
  on PostgreSQL and adds the nullable `embedding` column before any live
  backfill or shared indexing changes.
- Step 49 also adds supporting B-tree indexes for planned filter-first
  retrieval and a PostgreSQL-only partial HNSW cosine index on non-null
  vectors.
- Do not run whole-database vector backfill automatically during app startup.
- During rollout, existing NULL-vector rows should be repaired through
  page-scoped re-index, usually by the manual incremental sync path for known
  affected pages.
- If a future maintenance command backfills vectors, it must reuse the shared
  page indexing orchestrator page by page instead of issuing raw SQL updates
  or startup-wide scans.
- If OpenAI embedding access or pgvector retrieval is unavailable during
  rollout, QA may fall back to deterministic lexical retrieval until later
  rollout steps are complete.
- Downgrade removes the rollout column and indexes but intentionally leaves the
  `vector` extension installed, since extension state may be shared by other
  DB objects in the same PostgreSQL database.

## Step 55 Live Smoke Procedure

- The Step 55 smoke run is opt-in only. It must not be added to the default
  unit suite or app startup path.
- The smoke command is `uv run python tests/evals/live_vector_smoke.py`.
- Required env:
  `LEARNLOOP_RUN_LIVE_VECTOR_SMOKE=1` and `OPENAI_API_KEY`.
- The command creates a temporary PostgreSQL database from
  `LEARNLOOP_PGVECTOR_ADMIN_DATABASE_URL` when set, or from the default local
  docker-compose admin URL:
  `postgresql+psycopg://learnloop:learnloop@localhost:5432/postgres`.
- After creating the temporary database, the smoke flow applies the project's
  real Alembic migrations to `head` before any indexing or retrieval checks.
- The temporary database is created only for the smoke run and is dropped at
  the end unless `--keep-database-on-failure` is used for debugging.
- The smoke run uses real OpenAI embeddings plus real PostgreSQL + pgvector,
  but keeps the answer provider deterministic and local because this step is
  verifying vector storage, DB-side retrieval, citation behavior, scoped-empty
  insufficient-info behavior, and duplicate-safe re-indexing.

## Step 85 Recovery Readiness

Backup, restore, migration, and incident procedures live under
[`docs/runbooks/`](runbooks/). The PostgreSQL restore drill is dry-run by
default and requires an explicit `--run`, `DISPOSABLE` confirmation, and an
administrator URL for a disposable local server. It creates and removes only
generated temporary database names; it never targets the configured application
database.

The Notion/DB recovery drill is read-only and emits a deterministic checklist.
After a database restore, current Notion content is authoritative and the
operator must run a full Notion index before resuming mutations. Known manual
Notion edits use page-scoped incremental indexing. An uncertain append must be
resolved through the durable `change-request-<id>` identity before any retry;
identity uncertainty stops recovery.

The release evidence for this step is the redacted drill result, migration
revision, readiness result, re-index result, and scoped QA citation. Secrets,
connection URLs, page ids, and private source content are not evidence fields.

## Step 87 Synthetic Data Release Gate

Before a release, inspect the configured PostgreSQL database and fail closed
on any known synthetic data:

```bash
uv run --no-env-file --frozen python scripts/cleanup_synthetic_data.py --json
uv run --no-env-file --frozen python scripts/release_gate.py --json
```

The cleanup command is dry-run by default. After reviewing aggregate counts,
an operator may apply the fixed allowlist only with
`--apply --confirm CLEAN_SYNTHETIC_DATA`. It is transactional, does not call
Notion, and does not accept arbitrary ids. Run the release gate again after
cleanup; a database connection or inspection failure remains a release
failure.
