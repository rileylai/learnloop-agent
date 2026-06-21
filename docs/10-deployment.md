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
