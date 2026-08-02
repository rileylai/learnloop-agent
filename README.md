# LearnLoop Agent

LearnLoop Agent is a local-first Notion knowledge agent.
It reads existing Notion notes as knowledge, generates reviewable AI supplement
proposals from new learning sources, and writes accepted content only into
`AI Supplement Zone`.

## What it does

- Index existing Notion notes as read-only knowledge.
- Ingest PDF, URL, YouTube transcript, screenshot OCR, and chat text sources.
- Generate AI supplement proposals from new sources.
- Require human review before any write.
- Append accepted content only under `AI Supplement Zone`.
- Answer questions with RAG and Notion path citation.

## Current readiness

The repository is currently **demo-ready**, not local-user-ready or
release-ready.

Confirmed today:

- The deterministic one-command mock demo runs without external credentials.
- Core indexing, RAG, proposal, review, append-only, re-index, and Telegram
  orchestration paths have deterministic tests with fake or in-memory
  adapters.
- PostgreSQL/pgvector schema and repository support exist.

Not yet available as a real-user flow:

- The default Notion backend uses bundled mock JSON. A live read-only reader
  and append-only writer can be selected with `NOTION_BACKEND=live`. Step 83
  verified one human-approved append against a dedicated sandbox page, but
  this does not establish arbitrary production-workspace readiness.
- A wired Redis/RQ worker is optional by configuration. Prometheus-compatible
  metrics, protected workflow status/reconciliation, and cost-budget alerts
  are implemented. API/webhook authentication, persistent Telegram update idempotency, and `/ready` are
  implemented; `/ready` now provides
  dependency-aware readiness; it is distinct from the shallow `/health` route.
- Telegram transport and target-aware `/ingest` are mock-tested. Step 88 also
  has user-confirmed guarded Telegram live E2E evidence; future live runs still
  require explicit operator configuration and opt-in.
- A complete Notion indexing -> QA -> proposal -> accept -> append -> re-index
  flow has been verified in the dedicated sandbox canary, and Step 88 has
  separately completed the guarded Telegram live path. Neither establishes
  arbitrary production-workspace, cloud, or always-on sync readiness.

See `dev_state/PROJECT_ROADMAP.md` for the local
`Real-World Usability + Release Hardening` plan.

## Safety model

- Existing Notion content is read-only for direct agent editing.
- Manual-created notes are read-only for direct agent editing.
- Old AI supplement blocks are read-only for direct agent editing.
- Pending and rejected change requests are excluded from production RAG.
- All AI writes follow: `Change Request -> Human Accept -> Append to AI Supplement Zone`.
- Notion remains the source of truth.

## Architecture rule

High-level flow:

```text
API Route -> Orchestrator -> Service / Tool -> Repository -> External System
```

LLM flow:

```text
API Route -> Orchestrator -> Provider Router -> Provider Adapter
```

Tool flow:

```text
API Route -> Orchestrator -> Tool Registry -> Local Tool Adapter
```

### Architecture diagram

This diagram shows the target MVP boundaries. The current runtime differences
are listed in `Current readiness` above.

```mermaid
flowchart TD
    USER["User or Telegram Bot"] --> API["FastAPI routes"]
    API --> ORCH["Orchestrators"]
    ORCH --> ROUTER["Provider Router"]
    ROUTER --> PROVIDER["Provider Adapter"]
    PROVIDER --> LLM["OpenAI now; Claude or Gemini later"]
    ORCH --> TOOLS["Tool Registry"]
    TOOLS --> ADAPTERS["Local tool adapters in MVP"]
    ADAPTERS --> NOTION["Notion API after live adapter wiring"]
    ADAPTERS --> PARSERS["PDF / URL / OCR / YouTube parsers"]
    ORCH --> CORE["Repositories, QueueClient, and deterministic guardrails"]
    CORE --> STORAGE["PostgreSQL / pgvector; Redis after worker wiring"]
    NOTION --> SOURCE["Existing notes: read-only source of truth"]
    NOTION --> ZONE["AI Supplement Zone: append-only after accept"]
```

## Local runtime

- MVP is local-only.
- Docker Compose provides local PostgreSQL and Redis.
- The bundled mock Notion pages under `mock_data/notion_pages/` are loaded
  automatically for the demo flow. They are test/demo fixtures only; the demo
  uses ephemeral SQLite and production PostgreSQL rejects mock-source indexing.
- The default demo path performs no real Notion write.

To inspect a configured PostgreSQL database for known synthetic rows before a
release, run the dry-run cleanup and fail-closed release gate:

```bash
uv run --no-env-file --frozen python scripts/cleanup_synthetic_data.py --json
uv run --no-env-file --frozen python scripts/release_gate.py --json
```

Review the aggregate dry-run counts before any explicit apply operation. The
cleanup allowlist is fixed, transactional, and does not connect to Notion.

## Prerequisites

- Python 3.9+
- [`uv`](https://docs.astral.sh/uv/)
- Docker Desktop or Docker Engine with Compose
- An OpenAI API key for server-backed indexing, QA, and proposal generation

Notes:

- `OPENAI_API_KEY` is required for the server-backed indexing examples because
  indexing fails closed when chunk embeddings cannot be generated. It is also
  required for live `POST /api/qa` and supplement proposal calls.
- `NOTION_TOKEN` is not required for the mock demo flow.
- Set `NOTION_BACKEND=live` together with `NOTION_TOKEN` to select the live
  reader/writer adapters. Live mode fails closed when the token is missing.
- `TELEGRAM_BOT_TOKEN` is not required for the mock demo flow.
- Tesseract is required for screenshot OCR, but not for `/health` or mock QA.
- The one-command demo script below does not require Docker, Postgres, or an OpenAI key.

## Quick start

### 1. Install Python dependencies

```bash
uv sync --dev
```

### 2. Prepare environment variables

Copy the template:

```bash
cp .env.example .env
```

Edit `.env` with the values you need for the local demo:

```bash
APP_ENV=local
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg://learnloop:learnloop@localhost:5432/learnloop
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-api-key
```

Important:
This project currently reads process environment variables directly.
It does not auto-load `.env`, so load the file into your shell before running
the API or Alembic commands:

```bash
set -a
source .env
set +a
```

Optional:

- `MOCK_NOTION_DATA_DIR` if you want a different mock data directory.
- `NOTION_BACKEND=mock` is the default; use `NOTION_BACKEND=live` with
  `NOTION_TOKEN` for the live Notion adapters.
- `TELEGRAM_BOT_TOKEN` enables Telegram HTTP send/download transport, but does
  not by itself make the Telegram E2E user-ready.

### 3. Start local services

```bash
docker compose up -d
```

This starts:

- PostgreSQL with pgvector on `localhost:5432`
- Redis on `localhost:6379`

The API uses PostgreSQL/pgvector. When `REDIS_URL` is configured, Telegram
webhook work is acknowledged quickly and processed by the RQ worker. Start the
worker in a separate shell with:

```bash
uv run --no-env-file --frozen python scripts/run_worker.py
```

Without `REDIS_URL`, local/test compatibility keeps the synchronous Telegram
path; local readiness still requires Redis for release-style operation.

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

### 5. Start the API

```bash
uv run uvicorn src.app.main:app --reload
```

### 6. Verify health

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{ "status": "ok" }
```

`/health` is a shallow liveness endpoint. It does not prove that PostgreSQL,
Alembic migrations, pgvector, providers, Notion, Telegram, or Redis are ready.

Check release-style local dependencies with:

```bash
curl http://127.0.0.1:8000/ready
```

`/ready` returns `200` only when the database, current migrations, pgvector,
Redis/RQ, and mode-specific provider configuration are available; otherwise it
returns `503`. `/health` remains the process liveness check.

### Portable API entrypoint and preflight

For a portable local API launch, run from any directory inside the repository:

```bash
scripts/run_live.sh
```

The entrypoint resolves the repository root, runs a redacted dependency and
configuration preflight, and then starts the API with the locked `uv` runtime.
It does not load `.env` or print secret values. Load environment variables in
the shell first as shown above.

To inspect a profile without starting the API:

```bash
uv run --no-env-file --frozen python scripts/preflight.py --profile api
uv run --no-env-file --frozen python scripts/preflight.py --profile test
uv run --no-env-file --frozen python scripts/preflight.py --profile ocr
```

Missing `OPENAI_API_KEY`, `NOTION_TOKEN`, and `TELEGRAM_BOT_TOKEN` are reported
without exposing values. `NOTION_TOKEN` is a hard failure only when
`NOTION_BACKEND=live`; the `ocr` profile additionally requires the `tesseract`
executable.

## One-command demo script

If you want a deterministic portfolio demo without Docker, a running server,
or an API key, run:

```bash
uv run python scripts/run_mock_demo.py
```

What it does:

- Calls `/health` through the FastAPI app.
- Calls `POST /api/notion/index/page` for bundled mock page `page-nlp-week5`.
- Calls `POST /api/qa` with a fake provider through the normal Provider Router boundary.
- Uses in-memory SQLite for repositories and workflow state.
- Uses the bundled mock Notion reader path instead of real Notion access.

This keeps the demo aligned with the implemented architecture while staying
deterministic for local verification and portfolio walkthroughs.

Expected output looks like:

```text
LearnLoop mock demo: pass
health=ok
indexed_page=page-nlp-week5 (NLP Week 5), blocks=12
qa_provider=openai model=gpt-4o-mini
qa_citation=Knowledge/NLP/Week5/...
qa_answer=Positional encoding gives the model an order signal ...
```

## Mock demo fixtures

The repo includes synthetic, public-safe mock Notion pages for the isolated
demo and deterministic tests:

- `page-nlp-week5`
- `page-rag-basics`
- `page-iso-9001`

These pages are read through the same `NotionReaderTool` boundary used by the
real indexing flow, but without any real Notion access. Do not index these
fixtures through a server connected to a persistent PostgreSQL database:
PostgreSQL mock-source indexing is blocked with `SYNTHETIC_DATA_NOT_ALLOWED`.
Use `scripts/run_mock_demo.py`, which creates isolated in-memory SQLite state,
for the complete index-and-QA walkthrough.

For a live API walkthrough, select `NOTION_BACKEND=live` and use a real
read-only Notion configuration instead of these fixtures.

The synthetic pages are not production retrieval evidence. Before release,
run the cleanup dry run and fail-closed release gate described above.

## Current limits

- MVP is local-only.
- Telegram is the first user channel, but it is optional for the README demo.
- The isolated demo uses bundled mock Notion pages; production PostgreSQL
  rejects mock-source indexing. Real Notion access requires
  `NOTION_BACKEND=live` and operator verification.
- Full Notion discovery and index-status routes exist; manual incremental sync
  remains an explicit operator action.
- Proposal review list/detail and target-page selection are implemented through
  the review APIs and Telegram `/pages` plus `/ingest --page` flow.
- API bearer auth, Telegram webhook secret/allowed-chat policy, and persistent
  idempotency are implemented; real deployment still requires configuration.
- Configured Telegram long work uses Redis/RQ; local no-Redis compatibility is
  retained, while release readiness requires the worker path.
- `/health` is liveness only; `/ready` is dependency-aware and `/metrics` is a
  redacted Prometheus-compatible operator surface.
- No direct original-note editing.
- No standalone MCP server in MVP.
- No always-on cloud sync.
- No reranker.
- No LLM-as-judge.

## Repository structure

```text
AGENTS.md
README.md
docs/
mock_data/
scripts/
src/
tests/
dev_state/
observability/
```

## Documentation map

- `docs/00-design-doc.md`
- `docs/01-architecture.md`
- `docs/02-workflows.md`
- `docs/03-guardrails.md`
- `docs/04-memory-design.md`
- `docs/05-rag-design.md`
- `docs/06-notion-permission-model.md`
- `docs/07-evaluation-plan.md`
- `docs/08-observability.md`
- `docs/09-api-contract.md`
- `docs/10-deployment.md`
- `docs/11-coding-style.md`
- `docs/12-github-collaboration-rules.md`

## License

See [LICENSE](LICENSE).
