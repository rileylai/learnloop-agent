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

## Local runtime

- MVP is local-only.
- Docker Compose provides local PostgreSQL and Redis.
- The bundled mock Notion pages under `mock_data/notion_pages/` are loaded
  automatically for the demo flow.
- The default demo path performs no real Notion write.

## Prerequisites

- Python 3.9+
- [`uv`](https://docs.astral.sh/uv/)
- Docker Desktop or Docker Engine with Compose
- An OpenAI API key for the README QA demo

Notes:

- `OPENAI_API_KEY` is required for `POST /api/qa`.
- Without `OPENAI_API_KEY`, indexing still works but `/api/qa` returns `PROVIDER_NOT_FOUND`.
- `NOTION_TOKEN` is not required for the mock demo flow.
- `TELEGRAM_BOT_TOKEN` is not required for the mock demo flow.
- Tesseract is only needed later for screenshot OCR, not for `/health` or mock QA.

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
- `NOTION_TOKEN` only when you later switch from mock pages to the real Notion API.
- `TELEGRAM_BOT_TOKEN` only for Telegram webhook testing.

### 3. Start local services

```bash
docker compose up -d
```

This starts:

- PostgreSQL with pgvector on `localhost:5432`
- Redis on `localhost:6379`

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
{"status":"ok"}
```

## Mock demo flow

The repo already includes synthetic, public-safe mock Notion pages:

- `page-nlp-week5`
- `page-rag-basics`
- `page-iso-9001`

These pages are read through the same `NotionReaderTool` boundary used by the
real indexing flow, but without any real Notion access.

### 1. Index one mock Notion page

```bash
curl -X POST http://127.0.0.1:8000/api/notion/index/page \
  -H "Content-Type: application/json" \
  -d '{"page_id":"page-nlp-week5"}'
```

Expected behavior:

- Response status is `200`
- `page_title` is `NLP Week 5`
- `notion_path` is `Knowledge/NLP/Week5`
- `indexed_block_count` is greater than `0`

### 2. Ask a mock QA question

```bash
curl -X POST http://127.0.0.1:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does positional encoding do?",
    "page_ids": ["page-nlp-week5"],
    "top_k": 5,
    "provider_name": "openai",
    "model": "gpt-4o-mini"
  }'
```

Expected behavior:

- Response status is `200`
- `status` is `succeeded`
- `insufficient_info` is `false`
- `citations` includes a path under `Knowledge/NLP/Week5`
- `provider` is `openai`

The exact answer text can vary by model, but it should stay grounded in the
indexed mock notes and accepted synthetic `AI Supplement Zone` content.

### 3. Optional second QA example

```bash
curl -X POST http://127.0.0.1:8000/api/notion/index/page \
  -H "Content-Type: application/json" \
  -d '{"page_id":"page-rag-basics"}'
```

```bash
curl -X POST http://127.0.0.1:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Why should a learning agent return citations?",
    "page_ids": ["page-rag-basics"],
    "top_k": 5,
    "provider_name": "openai",
    "model": "gpt-4o-mini"
  }'
```

Expected behavior:

- The answer explains citation discipline.
- `citations` includes a path under `Knowledge/AI/RAG Basics`.

## Current limits

- MVP is local-only.
- Telegram is the first user channel, but it is optional for the README demo.
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
