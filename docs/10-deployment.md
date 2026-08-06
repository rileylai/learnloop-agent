# 10 Deployment

## Purpose
This document defines local Docker Compose runtime and future V2 cloud deployment plan.

## Status
Draft

What belongs here:
- Local runtime setup.
- Service dependency model.
- Future cloud deployment architecture.

## Current Deployment Readiness

The repository has a working local architecture and a green deterministic
suite. Step 88 is now complete based on user-confirmed guarded Telegram live
E2E evidence. The repository remains local-only and this bounded evidence does
not establish production-wide or cloud deployment readiness.

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
  profile-required missing items fail the command. The OCR profile invokes
  `tesseract --list-langs` through a bounded stdlib subprocess and requires
  `eng`, `chi_tra`, and `chi_sim`; it never imports `pytesseract`.
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
  behind `NotionWriterTool`. Step 83 verified one human-approved append through
  this live adapter against a dedicated sandbox page, including durable
  identity, re-index, and scoped citation. This is bounded sandbox evidence;
  it does not establish arbitrary production-workspace readiness or the full
  Telegram live E2E.
- Telegram runtime requests enqueue background jobs through `QueueClient` when
  `REDIS_URL` is configured. Run `uv run --no-env-file --frozen python
  scripts/run_worker.py` in a separate process to consume them. The worker
  uses RQ's embedded scheduler (`with_scheduler=True`), so the same process
  promotes delayed settle jobs and interval-based retries.
  Startup emits only safe fields such as
  `queue=telegram worker_started=true scheduler_enabled=true`; it never logs
  the Redis URL or secrets. The worker
  derives the repository root from its own file path and fail-fast validates
  RQ resolution of `src.worker.telegram.process_telegram_webhook_job` before
  consuming jobs. RQ 2.8.0's platform policy selects `SpawnWorker` on
  Darwin/macOS and the standard `Worker` on Linux; selecting the fork-based
  worker on macOS is rejected. Jobs use two bounded retries after the initial
  attempt;
  expected Telegram/domain failures are persisted as terminal ledger outcomes.
- Tesseract OCR requires all three traineddata languages `eng`, `chi_tra`, and
  `chi_sim`. The current host passes this preflight and the real-adapter
  fixture. Step 88 provides user-confirmed guarded Telegram live E2E evidence;
  no broader OCR corpus or recognition benchmark is inferred.
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

Portable preflight, live Notion wiring, authentication, worker, recovery, and
synthetic-data gate implementations exist. Step 88 evidence is complete, but
release sign-off still depends on a passing release-time dependency/gate run
and any environment-specific OCR or restore evidence required by the operator.

### Current Verification Boundary

| Evidence | Recorded result | Limit |
|---|---|---|
| Deterministic suite | `399 passed, 3 skipped` on 2026-08-01 | The skipped tests require opt-in live PostgreSQL; the suite is not external E2E evidence. |
| Step 82 Notion canary | Passed | Dedicated read-only sandbox; deterministic embedding/answer and ephemeral SQLite. |
| Step 83 Notion append canary | Passed | Dedicated approved sandbox append; deterministic embedding/answer and ephemeral SQLite. |
| Step 87 PostgreSQL gate | Passed | Bounded inspection of the configured database at that run. |
| OCR host preflight and adapter fixture | Passed | All three required languages are available; no broader OCR corpus or benchmark is claimed. |
| Telegram live E2E | Passed (user-confirmed guarded evidence) | Bounded local live path; this does not establish production-wide readiness. |
| Live restore drill | Not verified | Only deterministic dry-run/test coverage is recorded. |

Docker Compose remains local infrastructure only and starts PostgreSQL and
Redis, not the API or worker. There is no implemented cloud deployment or
always-on Notion synchronization service.

## Local Startup

From the repository root, export the required process environment without
printing secret values, then run:

```bash
docker compose up -d postgres redis
uv run --no-env-file --frozen alembic upgrade head
./scripts/run_live.sh
```

Run the Telegram worker in a separate terminal with the same environment:

```bash
uv run --no-env-file --frozen python scripts/run_worker.py
```

The API and worker do not load `.env`. A successful process start is not
readiness evidence; check `/ready`, queue/scheduler state, and the release gate
for the intended database.

## Liveness and Readiness

- `GET /health` is a shallow process liveness check and does not contact
  external dependencies.
- `GET /ready` checks database connectivity, current Alembic migrations,
  pgvector, and the mode-specific provider configuration. It returns `200`
  with `status=ready` only when all checks pass, otherwise `503` with safe
  check details.
- `APP_ENV=local` requires `OPENAI_API_KEY` for server-backed indexing. The
  `test`, `demo`, and `mock` modes do not require a live provider.
- Redis and the RQ scheduler are required in local readiness because Telegram
  webhook work depends on delayed queue promotion. Test/demo/mock modes may
  skip them. Redis availability without a live scheduler fails `/ready` with
  `RQ_SCHEDULER_NOT_RUNNING`.
- Worker startup is cwd-independent: it adds the repository root derived from
  `scripts/run_worker.py` to `sys.path`. Do not replace this with a hardcoded
  local path or a synchronous fallback. Use `--worker-class auto` for the
  platform policy, or explicitly pass `--worker-class spawn` / `worker` when
  the selected policy is appropriate. `--burst` is reserved for an empty,
  disposable smoke queue; do not point it at a queue containing live work.

## Portable Preflight Contract

- Run `uv run --no-env-file --frozen python scripts/preflight.py --profile api`
  to check the API profile in the locked environment.
- Run `--profile test` to include development test dependencies.
- Run `--profile ocr` to require the `tesseract` executable, plus the `eng`,
  `chi_tra`, and `chi_sim` traineddata languages, in addition to Python
  dependencies. On Homebrew installations, install the extra language data
  with `brew install tesseract-lang`, then verify `tesseract --list-langs`
  before restarting the API and worker.
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

## RQ delayed-job inspection

Inspect queue counts, scheduler liveness, and scheduled job identity without
deleting or cleaning any registry:

```bash
uv run --no-env-file --frozen python scripts/inspect_rq_queue.py \
  --queue telegram --json
```

The report includes only queue name, counts, scheduler state, job id, callable,
status, schedule/enqueue timestamps, and retries left. It never prints job
arguments or the Redis URL. Existing scheduled webhook retry and upload-settle
jobs should remain in place; after the worker starts with the embedded scheduler,
due jobs are promoted and the update ledger/session version claims prevent
duplicate business work. Do not run registry cleanup or deletion as recovery.

## Adapter Smoke Matrix

Before a live canary, run the real-library adapter matrix with the locked
environment:

```bash
uv run --no-env-file --frozen python tests/evals/adapter_smoke_matrix.py --json
```

The default run is local-only. It verifies PDF and URL extraction with
controlled fixtures and verifies OCR only when the local Tesseract executable
and required `eng`, `chi_tra`, and `chi_sim` traineddata are available. Missing
optional OCR runtime is reported as `skipped`; use `--require-ocr` when the
deployment requires OCR. Production screenshot OCR checks the same fixed
language set again before processing any image and fails closed rather than
silently using English.

Use `--live` only with dedicated synthetic resources. Live checks are opt-in
for YouTube transcript access, OpenAI embeddings, PostgreSQL connectivity, and
an explicitly permitted Telegram synthetic send. The matrix does not call
Notion and never performs a Notion write. Keep the JSON report as release
evidence only after checking that it contains no secret or private content.

## Guarded Large-page Failure Diagnostic (Step 96)

The default command is local and skipped. It makes zero Notion or OpenAI
requests:

```bash
uv run --no-env-file --frozen python \
  tests/evals/large_page_failure_diagnostic.py --json
```

The live diagnostic must not run without separate approval. After exporting
`NOTION_TOKEN`, `OPENAI_API_KEY`, and
`LEARNLOOP_NOTION_DIAGNOSTIC_PAGE_ID` without printing their values, the
approved command is:

```bash
LEARNLOOP_RUN_LARGE_PAGE_DIAGNOSTIC=1 \
  uv run --no-env-file --frozen python \
  tests/evals/large_page_failure_diagnostic.py \
  --live --approve --json --bounded-count 64 \
  --max-aggregate-bytes 1000000 \
  --max-aggregate-token-estimate 250000 \
  --max-request-count 8 \
  --total-token-estimate-budget 500000
```

The command reads one page with the diagnostic 30-second timeout, keeps chunk
inputs in memory, and sends sequential single-input, small-batch, and
progressively count/byte/token-bounded probes using the same OpenAI model and
`dimensions=1536`. It stops after the first failure or explicit request/token
budget, does not retry, and
does not run a full index, write Notion, use PostgreSQL, or persist vectors.

Expected JSON contains only fixed status/diagnosis/message fields plus case,
endpoint class, provider/model/dimensions, input/empty counts, size estimates,
duration, HTTP status, normalized category, retryability, and bounded numeric
`Retry-After`. It must not contain page identity/path, Notion or chunk content,
payloads, vectors, URLs, raw upstream messages/bodies, or credentials.
Budget exhaustion returns `status=inconclusive`, keeps
`diagnosis=unresolved`, and exits nonzero so it cannot be mistaken for a
completed diagnostic.

Risks remain: the read may issue many Notion requests, the embedding probes use
provider quota and send the selected private note content to the already
configured embedding provider, and a generic HTTP 400 may remain unresolved.
The command provides bounded dependency evidence only and does not authorize
Step 97 or a payload-size root-cause claim.

The initial approved matrix passed through 64 inputs and 24,916 bytes / 6,254
estimated tokens without reproducing HTTP 400. It established no provider
category or failure boundary.

The next proposed command is a distinct no-embedding Phase A inspection. It is
documented but not approved for live execution:

```bash
LEARNLOOP_RUN_LARGE_PAGE_DIAGNOSTIC=1 \
  uv run --no-env-file --frozen python \
  tests/evals/large_page_failure_diagnostic.py \
  --live --approve --shape-only --json
```

This mode requires only `NOTION_TOKEN` and
`LEARNLOOP_NOTION_DIAGNOSTIC_PAGE_ID`. It uses the diagnostic 30-second
read-only client, chunks the same page, and returns only total/empty counts,
aggregate and maximum sizes, p50/p95/p99 byte/character/token estimates, the
one-based ordinal of the first maximum-byte input, and estimator version. It
does not create an OpenAI client, send an embedding request, persist data, or
authorize the subsequent boundary matrix.

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

## Human-approved Notion Append Canary (Step 83)

Step 83 has completed its separate live canary against a dedicated synthetic
sandbox page. The canary used explicit live opt-in plus human approval and
verified `pending -> accepted`, append-only `AI Supplement Zone` behavior,
durable change-request identity visibility, page re-index, and a scoped QA
citation. Derived state remained ephemeral and the report was redacted to
counts and operation classes.

This evidence confirms the bounded sandbox append contract only. It is not a
complete production Notion workspace E2E or the complete Telegram-to-Notion
`live_e2e` chain by itself. Step 88 separately has user-confirmed guarded live
evidence, and its live actions remain opt-in rather than running by default.

## Local Secret Handling

- Keep runtime secrets in local shell environment or ignored `.env` files only.
- `.env.example` may show placeholder variable names, but must not contain real
  credentials.
- `.env` and `.env.*` must stay ignored by Git so local Notion, OpenAI, and
  Telegram credentials never enter the repository.

## Live Vector Rollout Contract

- The first live vector rollout uses OpenAI `text-embedding-3-small` with
  explicit `dimensions=1536`.
- Local PostgreSQL must have the `vector` extension available before the
  current migrations are applied.
- The rollout database shape is a nullable pgvector `vector(1536)` column plus
  transitional legacy `embedding_text` while old rows are being migrated.
- Exact cosine search on the filtered subset is the correctness baseline. A
  cosine HNSW index is the approved acceleration path. IVFFlat is not part of
  the MVP rollout contract.
- The current migration foundation enables `CREATE EXTENSION IF NOT EXISTS
  vector`, adds the nullable `embedding` column, supporting B-tree indexes,
  and a PostgreSQL-only partial HNSW cosine index on non-null vectors.
- Do not run whole-database vector backfill automatically during app startup.
- During rollout, existing NULL-vector rows should be repaired through
  page-scoped re-index, usually by the manual incremental sync path for known
  affected pages.
- If a future maintenance command backfills vectors, it must reuse the shared
  page indexing orchestrator page by page instead of issuing raw SQL updates
  or startup-wide scans.
- If OpenAI embedding access or pgvector retrieval is unavailable, QA records
  the deterministic fallback reason and uses lexical retrieval over the same
  production-safe scope.
- Downgrade removes the rollout column and indexes but intentionally leaves the
  `vector` extension installed, since extension state may be shared by other
  DB objects in the same PostgreSQL database.

## Step 55 Live Smoke Procedure

- The Step 55 smoke run is opt-in only. It must not be added to the default
  unit suite or app startup path.
- The smoke command is
  `uv run --no-env-file --frozen python tests/evals/live_vector_smoke.py`.
- Required env:
  `LEARNLOOP_RUN_LIVE_VECTOR_SMOKE=1` and `OPENAI_API_KEY`.
- The command creates a temporary PostgreSQL database from
  `LEARNLOOP_PGVECTOR_ADMIN_DATABASE_URL` when set, or from the configured
  local Docker Compose administration target. Do not put a credential-bearing
  database URL in documentation, shell history, or release evidence.
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

## Step 95 Telegram operator verification boundary

The deterministic operator regression suite is release evidence for bounded
command behavior only. It covers parsing, authorization, callbacks, ownership,
TTL/expiry, duplicate claims, confirmation gates, redaction, review safety,
readiness/liveness, aggregate stats, help output, ingestion, review, queue,
worker, and update-ledger paths through controlled dependencies.

Live Telegram/Notion/Redis/OpenAI verification is separate opt-in evidence.
It requires dedicated resources and redacted status/count/workflow/cost
reporting, and must not default to full index, append, Accept, or Telegram
send. A skipped live run remains unverified external evidence.

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
