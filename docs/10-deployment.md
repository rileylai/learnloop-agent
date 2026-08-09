# Deployment and Local Operations

The current runtime is local-only. Docker Compose supplies PostgreSQL/pgvector
and Redis; the FastAPI process and Telegram worker run from the locked `uv`
environment. The application reads process environment variables directly and
does not load `.env` automatically.

## Install

```bash
uv sync --dev
cp .env.example .env
```

Set the required values, export them, and start local services:

```bash
set -a
source .env
set +a
docker compose up -d
uv run --no-env-file --frozen alembic upgrade head
```

The default database URL is
`postgresql+psycopg://learnloop:learnloop@localhost:5432/learnloop`. Set
`DATABASE_URL` explicitly when using another database or when
`POSTGRES_PORT` is not `5432`; Compose's host-port mapping does not rewrite the
application's default URL. Compose exposes the database and Redis ports from
`POSTGRES_PORT` and `REDIS_PORT`.

## Configuration

| Variable | Purpose and default |
| --- | --- |
| `APP_ENV` | Runtime mode; default `local` |
| `LOG_LEVEL` | Log level; default `INFO` |
| `DATABASE_URL` | SQLAlchemy PostgreSQL URL; default local URL above |
| `REDIS_URL` | Redis/RQ connection; required for queued Telegram work |
| `NOTION_BACKEND` | `mock` by default, or `live` |
| `MOCK_NOTION_DATA_DIR` | Optional mock Notion data directory |
| `NOTION_TOKEN` | Required when `NOTION_BACKEND=live` |
| `OPENAI_API_KEY` | Required for live embedding and LLM operations |
| `TELEGRAM_BOT_TOKEN` | Required for Telegram sends/downloads |
| `TELEGRAM_WEBHOOK_SECRET` | Optional webhook secret validation |
| `TELEGRAM_ALLOWED_CHAT_IDS` | Optional comma-separated chat allowlist |
| `API_BEARER_TOKEN` | Optional bearer protection for protected API routes |
| `MAX_WORKFLOW_COST_USD` | Optional per-workflow budget |
| `MAX_DAILY_COST_USD` | Optional daily budget |
| `WORKFLOW_STALE_AFTER_SECONDS` | Stale workflow threshold; default `3600` |
| `TELEGRAM_JOB_TIMEOUT_SECONDS` | Ordinary Telegram job bound; default `180` |
| `TELEGRAM_INDEXING_JOB_TIMEOUT_SECONDS` | Full-index job bound; default `10800` |

Notion read and embedding retry/timeouts and batch limits are also configurable
through the names in `.env.example`: `NOTION_REQUEST_TIMEOUT_SECONDS`,
`NOTION_READ_MAX_ATTEMPTS`, `NOTION_READ_RETRY_BASE_SECONDS`,
`NOTION_READ_RETRY_MAX_SECONDS`, `EMBEDDING_BATCH_MAX_INPUTS`,
`EMBEDDING_BATCH_MAX_SINGLE_INPUT_BYTES`,
`EMBEDDING_BATCH_MAX_SINGLE_INPUT_TOKEN_ESTIMATE`,
`EMBEDDING_BATCH_MAX_AGGREGATE_BYTES`,
`EMBEDDING_BATCH_MAX_AGGREGATE_TOKEN_ESTIMATE`,
`EMBEDDING_REQUEST_MAX_ATTEMPTS`, `EMBEDDING_RETRY_BASE_SECONDS`, and
`EMBEDDING_RETRY_MAX_SECONDS`.

Keep `.env` and credentials outside Git. Do not print or commit secret-bearing
values.

## Start the API and worker

For a preflighted local API:

```bash
uv run --no-env-file --frozen python scripts/preflight.py --profile api --json
uv run --no-env-file --frozen uvicorn src.app.main:app --reload
```

The repository-relative wrapper performs the same preflight:

```bash
./scripts/run_live.sh
```

With `REDIS_URL`, start the Telegram worker in another shell:

```bash
uv run --no-env-file --frozen python scripts/run_worker.py
```

The worker validates the importable callables before consuming the `telegram`
queue, enables RQ's embedded scheduler, and selects `SpawnWorker` on macOS or
the standard worker on other platforms. `REDIS_URL` is required by the worker.

## Readiness and smoke checks

```bash
curl http://127.0.0.1:8000/health
curl --fail-with-body http://127.0.0.1:8000/ready
uv run --no-env-file --frozen python scripts/preflight.py --profile test --json
```

`/health` only proves that the process responds. `/ready` also checks the
database, migrations, pgvector, required provider configuration, Notion mode,
Redis, and scheduler. OCR requires Tesseract languages `eng`, `chi_tra`, and
`chi_sim`; use `--profile ocr` when verifying that host.

## Database operations

Alembic migrations are explicit:

```bash
uv run --no-env-file --frozen alembic current
uv run --no-env-file --frozen alembic upgrade head
```

Do not hide migrations in application startup. Review
[Migration](runbooks/migration.md), [Backup and restore](runbooks/backup-restore.md),
and [Incident recovery](runbooks/incident-recovery.md) before changing or
restoring a shared local database.

## Runtime modes and safety

`NOTION_BACKEND=mock` is safe for the deterministic demo and does not write to
real Notion. `NOTION_BACKEND=live` requires a token and uses read-only Notion
reads plus the append-only writer. A real append still requires explicit human
acceptance through the review workflow.

The default demo is offline and uses controlled adapters:

```bash
uv run --no-env-file --frozen python scripts/run_mock_demo.py
```

Live canaries, Telegram sends, database restore drills, and release gates are
opt-in. See the [evaluation plan](07-evaluation-plan.md).
