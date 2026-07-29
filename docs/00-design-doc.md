# LearnLoop Agent — Design Doc v1.1

## 1. Project Overview
LearnLoop Agent is a local-first Notion knowledge agent.
It indexes existing Notion notes as read-only knowledge, generates AI supplement proposals from new learning sources, and supports RAG QA with Notion path citation.
The agent can write only accepted content into `AI Supplement Zone`.

## 2. Core Harness Engineering Principles
- Read-only by default.
- No direct overwrite.
- No per-page writable original notes in MVP.
- Append-only `AI Supplement Zone`.
- Human-in-the-loop review.
- Notion is the source of truth.
- Manual sync for manual Notion changes.
- Auto page re-index after accepted agent append.
- Pending/rejected drafts are not used in production RAG.
- Every workflow must be auditable and testable.
- MCP-oriented architecture, not standalone MCP-server-first.
- Provider and tool interfaces are schema-friendly and provider-agnostic.

### 2.1 Two Harness Layers
This project has two separate harness layers.

Development harness:
- Used by Codex, coding agents, and maintainers during software development.
- Main sources: `AGENTS.md`, `docs/*.md`, `dev_state/PROJECT_ROADMAP.md`, and `dev_state/DAILY_LOG.md`.
- Purpose: guide code generation, enforce architecture rules, document workflow/API decisions, and prevent unsafe assumptions.

Runtime agent harness:
- Used by LearnLoop Agent when the product is running.
- Main sources: runtime prompt templates, `docs/prompts/*.md` when explicitly loaded, provider router, tool registry, tool schemas, RAG retrieval policy, Notion indexed notes, accepted AI supplement content, output validators, and permission checks.
- Purpose: answer user learning questions, decide when to use RAG, enforce Notion source-of-truth rules, validate outputs, and support human accept/reject workflows.

Important boundary:
- Project docs under `docs/*.md` are development specifications by default.
- They are not the default production RAG source for user-facing QA.
- Production user QA must retrieve from indexed Notion content and accepted AI supplement content unless a future ADR explicitly approves another source.

## 3. Notion Ownership Model
- Existing notes are read-only for direct agent editing.
- Newly manual-created notes are also read-only for direct agent editing.
- Previously AI-appended content is also read-only for direct agent editing.
- The agent cannot directly edit original page content.
- The agent cannot directly edit old AI supplement blocks.
- The agent cannot have per-page writable original-note mode in MVP.
- Manual edits by the user are allowed.
- If the user manually merges AI supplement content into original notes, that is valid.
- If the user manually deletes AI supplement blocks, that is valid.
- On the next manual sync, the database and vector index are reconciled with current Notion truth.

## 4. AI Supplement Zone Layout
```text
Original page/toggle/section
└── AI Supplement Zone
    └── YYYY-MM-DD
        └── Topic title
            - Source: ...
            - Summary: ...
            - Key Concepts: ...
            - Notes: ...
            - LearnLoop Change Request: change-request-<id>
```

Rules:
- Do not create excessive nested toggles.
- Group supplements by date, then topic.
- The four fixed content lines are `Source`, `Summary`, `Key Concepts`, and `Notes`.
- Every accepted supplement also includes a visible deterministic identity line:
  `LearnLoop Change Request: change-request-<id>`.
- The identity line is used for bounded read-after-write verification and
  durable retry detection across writer/client instances.
- `Source` display rules:
- PDF: show PDF filename.
- URL source: show full URL.
- YouTube source: show video title or transcript source name.
- Screenshot source: show screenshot batch display name.
- Chat text source: show chat text display name.

## 5. Sync Model
Path A: Agent accepted append

```text
Change Request
-> Human Accept
-> Append to AI Supplement Zone
-> Immediate page re-index job
-> Verify the append is visible by its durable change-request identity
-> In one DB transaction, lock and revalidate `pending`, persist the page
   re-index mutation set, and set the change request to `accepted`
-> New accepted supplement becomes available in production RAG
```

Path B: User manual Notion edits / deletes / merges

```text
User edits Notion manually
-> User triggers /api/notion/index/incremental
-> System detects changed pages
-> Page-level replacement
-> Old stale blocks/chunks are removed
-> Current Notion page is re-indexed
```

Sync statements:
- There is no always-on sync in MVP.
- Manual user edits require manual sync.
- Accepted agent appends trigger auto page re-index.
- Notion is the source of truth.

## 6. Runtime Model
- MVP is local-only.
- The service works only when the user's Mac app/service is running.
- Docker Compose is used for local services such as PostgreSQL and Redis.
- Cloud always-on deployment is V2, not MVP.
- V2 may use AWS EC2/ECS/S3 as future work.

## 7. MVP Scope
| Scope | Item | Description |
|---|---|---|
| In Scope | Telegram first | Use Telegram as the first input channel. |
| In Scope | PDF ingestion | Ingest and parse PDF files. |
| In Scope | URL ingestion | Ingest and parse web articles by URL. |
| In Scope | YouTube transcript-only ingestion | Ingest only YouTube videos with transcript support. |
| In Scope | Multiple screenshot OCR ingestion | Ingest multiple screenshots with OCR. |
| In Scope | Chat text ingestion with length limit | Ingest pasted chat text with MVP length limit. |
| In Scope | Notion initial indexing | Full initial index of existing Notion notes. |
| In Scope | Notion page re-indexing | Re-index a specific page. |
| In Scope | Manual incremental sync | Manual incremental sync for manual Notion changes. |
| In Scope | RAG QA with Notion path citation | Answer questions with path citation. |
| In Scope | AI supplement proposal | Generate supplement proposals from new sources. |
| In Scope | Human review: accept / reject / edit later | Human review before any write. |
| In Scope | Append-only write to `AI Supplement Zone` | Write only accepted content by append. |
| In Scope | Auto page re-index after accepted append | Trigger immediate page re-index after accept. |
| In Scope | pgvector-based vector search | Use pgvector for retrieval. |
| In Scope | structured JSON logs | Use structured JSON logs for workflows. |
| In Scope | token cost tracking | Track token input/output and estimated cost. |
| In Scope | failure_reason logging | Track failures with failure_reason taxonomy. |
| In Scope | MCP-oriented interfaces | Use provider-agnostic LLM interfaces and schema-friendly local tool adapters. |
| Out of Scope | WhatsApp | Not in MVP. |
| Out of Scope | LINE | Not in MVP. |
| Out of Scope | Discord | Not in MVP. |
| Out of Scope | Bilibili | Not in MVP. |
| Out of Scope | speech-to-text for videos without transcript | Not in MVP. |
| Out of Scope | inline editing of proposals | Not in MVP UI. |
| Out of Scope | direct original note editing | Not allowed in MVP. |
| Out of Scope | per-page writable original notes | Not allowed in MVP. |
| Out of Scope | always-on cloud sync | Not in MVP. |
| Out of Scope | reranker | Not in MVP. |
| Out of Scope | LLM-as-judge | Not in MVP. |
| Out of Scope | AWS deployment | Deferred to V2. |
| Out of Scope | Standalone MCP server implementation | Not in MVP; local tool interfaces come first. |
| Out of Scope | LangChain / LangGraph implementation | Not in MVP. |

## 8. Functional Requirements
| ID | Requirement | Description |
|---|---|---|
| FR-001 | Read existing notes | Read existing Notion notes as read-only data. |
| FR-002 | Enforce ownership model | Enforce read-only direct editing rule for all Notion notes and old AI blocks. |
| FR-003 | Full indexing | Build initial full index from Notion pages/blocks. |
| FR-004 | Page re-index | Re-index one specified Notion page. |
| FR-005 | Manual sync entrypoint | Use `/api/notion/index/incremental` for manual Notion edits/deletes/merges. |
| FR-006 | Page-level replacement reconciliation | For changed pages, remove stale blocks/chunks and rebuild page index. |
| FR-007 | Ingest PDF | Parse and ingest PDF. |
| FR-008 | Ingest URL | Parse and ingest URL article. |
| FR-009 | Ingest YouTube transcript | Parse and ingest YouTube transcript sources only. |
| FR-010 | Ingest screenshot OCR | Parse and ingest multi-screenshot OCR text. |
| FR-011 | Ingest chat text | Parse and ingest pasted chat text with length limit. |
| FR-012 | Generate supplement proposal | Generate proposal in note style with source grounding. |
| FR-013 | Human review gate | Require human accept/reject before write. |
| FR-014 | Append accepted supplement only | Write path must be `Change Request -> Human Accept -> Append to AI Supplement Zone`. |
| FR-015 | Auto re-index after accept | Accepted append triggers immediate page re-index job. |
| FR-016 | No direct overwrite | Never overwrite original notes directly. |
| FR-017 | QA with citation | RAG QA returns Notion path citation. |
| FR-018 | Scope query support | Support note-scoped Telegram QA with explicit `/ask --page` and `/ask --section` flags. |
| FR-019 | Audit logging | Log workflow and decision events. |
| FR-020 | Production-RAG exclusion | `pending` and `rejected` change requests are excluded from production RAG. |

## 9. Non-functional Requirements
| Category | Requirement |
|---|---|
| Security | No real secrets in code or logs. |
| Least privilege | Keep Notion integration permissions minimal. |
| Reliability | Retry recoverable failures without data corruption. |
| Auditability | Keep auditable workflow and decision logs. |
| Observability | Emit structured logs and metrics with failure_reason. |
| Cost tracking | Track token usage and estimated cost. |
| Idempotency | Avoid duplicate writes on retries. |
| Source-of-truth consistency | Notion is source of truth for note content. |
| Safe reconciliation | Reconcile changed pages with page-level replacement. |
| Maintainability | Keep clean boundaries across route/orchestrator/service/repository. |
| Extensibility | Allow future adapters/providers without core rewrites. |
| Local-only MVP runtime | MVP works in local runtime only. |
| Simple docs standard | Repo docs and comments use simple English. |

## 10. Architecture Overview
```text
Telegram Bot
  ↓
Agent Gateway
  - auth
  - Telegram webhook secret and allowed-chat policy
  - request parsing
  - source type detection
  - idempotency key
  ↓
Orchestrators
  - Indexing Orchestrator
  - Ingestion Orchestrator
  - Supplement Orchestrator
  - QA Orchestrator
  ↓
Provider Router
  - OpenAI Provider Adapter first
  - Claude Provider Adapter later
  - Gemini Provider Adapter later
  ↓
Tool Registry
  - Local Tool Adapters in MVP
  - Future MCP Client after tool contracts stabilize
  ↓
Tools / Services / Repositories
  - Notion Reader Tool
  - Notion Writer Tool
  - PDF Parser Tool
  - OCR Tool
  - Web Article Tool
  - YouTube Transcript Tool
  - Vector Search Tool
  - Guardrails
  - Repositories for PostgreSQL/pgvector
  - QueueClient for Redis/RQ
  ↓
Storage (derived state + workflow state)
  - PostgreSQL
  - pgvector
  - Redis
  - Local File Storage
  ↓
Notion (source of truth)
  - Existing notes: read-only for direct agent editing
  - AI Supplement Zone: append-only path after human accept

Sync behavior in MVP:
  - Manual sync for user manual Notion edits: /api/notion/index/incremental
  - Auto page re-index after accepted append
  - No always-on cloud sync

Telegram queue behavior:
  - With `REDIS_URL` configured, the webhook claims update idempotency and
    enqueues long work through `QueueClient` before returning `202`.
  - `scripts/run_worker.py` consumes the RQ `telegram` queue.
  - Telegram jobs use bounded retries; expected domain failures are terminal
    ledger outcomes and unexpected worker crashes can retry while an update is
    still `running`.
  - Local compatibility without `REDIS_URL` retains synchronous Telegram
    handling, but local readiness remains unavailable until Redis is configured.
```

Boundary rules:
- API routes and orchestrators must not import OpenAI, Claude, Gemini, Notion, Redis, PostgreSQL, or external API SDKs directly.
- LLM calls go through Provider Router and provider adapters.
- External capabilities go through Tool Registry and local tool adapters; future MCP clients can be added behind the same registry.
- PostgreSQL and Redis stay backend infrastructure behind repositories and QueueClient, not LLM-facing tools.
- Permission checks, write safety, RAG inclusion rules, output validation, and proposal state transitions remain deterministic backend logic.
- Shared page indexing uses:
  `Indexing Orchestrator -> EmbeddingClient -> ChunkRepository -> PostgreSQL + pgvector`.
- If chunk embeddings cannot be generated, indexing fails closed before page
  block or chunk replacement.

## 11. Main Workflows
### 11.1 Initial Indexing
```text
Run full indexing
-> Read Notion pages and blocks
-> Normalize and chunk
-> Batch chunk text through EmbeddingClient
-> Persist blocks and vectors through ChunkRepository
-> Save index run status
```
Checklist:
- [ ] Full index covers required page/block structure.
- [ ] Citation metadata includes Notion path.
- [ ] Successful indexing writes both live `embedding` and transitional
  `embedding_text` during rollout.

### 11.2 Manual Incremental Sync
```text
User edits Notion manually
-> Trigger /api/notion/index/incremental
-> Detect changed pages
-> Page-level replacement for each changed page
-> Batch chunk text through the shared embedding flow
-> Remove stale blocks/chunks
-> Re-index current page content
```
Checklist:
- [ ] Manual edits/deletes/merges are reconciled.
- [ ] Rebuilt page reflects current Notion truth.

### 11.3 Agent Accepted Append with Auto Re-index
```text
Change Request
-> Human Accept
-> Append to AI Supplement Zone
-> Trigger immediate page re-index through the shared embedding flow
-> Accepted content becomes searchable in production RAG
```
If the final workflow audit update fails after business work commits, the
business result is not rolled back or retried. The workflow remains `running`
for explicit stale-running reconciliation.
Checklist:
- [ ] Write path is append-only.
- [ ] Auto re-index job starts immediately after accept.

### 11.4 Manual Merge/Delete Reconciliation
```text
User merges/deletes AI supplement blocks
-> Trigger /api/notion/index/incremental
-> Detect changed pages
-> Remove stale snapshot data
-> Rebuild page index from current Notion
```
Checklist:
- [ ] Manual merge is treated as valid.
- [ ] Manual delete is treated as valid.

### 11.5 QA Workflow
```text
User asks question
-> Generate query embedding when available
-> Retrieve production chunks
-> Lexical fallback only when vector retrieval is unavailable or unusable
-> Generate grounded answer
-> Return answer with Notion path citation
```
Checklist:
- [ ] `pending` and `rejected` proposals are excluded.
- [ ] Missing citations are handled safely.
- [ ] Retrieved context is treated as untrusted data; embedded instructions
  cannot change write, target, or citation policy.
- [ ] Query-time vector failures degrade to deterministic lexical fallback instead of failing the whole QA workflow.
- [ ] Workflow metadata records provider name, model name, prompt id, and prompt version.

### 11.6 New Source Ingestion
```text
Receive source (PDF/URL/YouTube/OCR/chat)
-> Parse and normalize
-> Generate supplement proposal
-> Save source metadata and proposal
-> Wait for human review
```
Checklist:
- [ ] Source display format follows source type rule.
- [ ] Chat text length limit is enforced.
- [ ] PDF and OCR upload limits are enforced before parser work, with parser
  output limits revalidated after extraction.
- [ ] PDF page, image pixel, MIME, file-count, byte, and extracted-text limits
  fail closed with deterministic failure reasons.
- [ ] Proposal target paths are validated against the selected page's
  `AI Supplement Zone` before a change request is created.
- [ ] Supplement proposal workflow metadata records provider name, model name, prompt id, and prompt version.

### 11.7 Guarded Notion Read/Index/QA Canary
```text
Explicit operator opt-in
-> Read a dedicated synthetic workspace through the Notion reader
-> Run full indexing into ephemeral local state
-> Run one-page incremental indexing
-> Run scoped QA and verify a Notion path citation
-> Verify the Notion HTTP audit contains no write operation
```

Rules:
- The canary uses only the read-only Notion adapter and a write-blocking HTTP
  transport; Step 82 must not append, patch, delete, or move Notion blocks.
- Full and incremental indexing use the existing indexing orchestrators and
  repository boundaries.
- Embeddings and the QA answer provider may be deterministic local adapters so
  the read canary does not require OpenAI credentials or spend provider quota.
- The canary requires explicit opt-in and a dedicated synthetic workspace/page;
  its report contains counts and redacted operation classes, never page text,
  credentials, page ids, or exception bodies. Failed reports also include a
  fixed `failed_stage` and standard `failure_reason`.

### 11.8 Human Review
```text
Open change request
-> Accept or Reject
-> Save decision and reason
-> Trigger follow-up workflow
```
Checklist:
- [ ] No write before accept.
- [ ] Reject records are preserved for audit/eval only.

### 11.9 Human-approved Notion Append Canary
```text
Explicit live opt-in + human approval
-> Prepare one synthetic pending change request in ephemeral SQLite
-> Run the existing accept orchestrator
-> Append only under AI Supplement Zone
-> Verify durable change-request identity by read-after-write
-> Re-index the target page in the same accept workflow
-> Run scoped QA and verify a citation for the target page
```

Rules:
- The canary requires both a live opt-in and a separate approval flag before
  any Notion request is sent.
- The target must be a dedicated sandbox page; the report contains counts and
  redacted operation classes, never page ids, credentials, or source text.
- The canary transport allows page/block reads and append-only
  `PATCH /v1/blocks/{id}/children` requests only.
- A passed report requires `pending -> accepted`, visible durable identity,
  indexed blocks/chunks, and a scoped QA citation.

## 12. Database Design
Design notes:
- PostgreSQL and pgvector store derived state from Notion plus workflow state.
- Notion remains the source of truth for note content.
- For changed pages, reconciliation uses page-level replacement.
- Live vector rollout starts with a nullable `embedding` column and keeps
  legacy `embedding_text` during the transition. No startup-wide automatic
  backfill is allowed.

### 12.1 notion_pages
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Internal primary key. |
| notion_page_id | TEXT (UNIQUE) | Notion page identifier. |
| title | TEXT | Current page title snapshot. |
| path | TEXT | Page path used for citation. |
| last_edited_time | TIMESTAMPTZ | Last Notion edit time. |
| indexed_at | TIMESTAMPTZ | Last indexing time. |
| created_at | TIMESTAMPTZ | Created time. |
| updated_at | TIMESTAMPTZ | Updated time. |

### 12.2 notion_blocks
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Internal primary key. |
| notion_block_id | TEXT (UNIQUE) | Notion block identifier. |
| notion_page_id | TEXT | Parent page id. |
| parent_block_id | TEXT NULL | Parent block id. |
| block_type | TEXT | Block type. |
| content_text | TEXT | Normalized text content. |
| block_path | TEXT | Block path snapshot. |
| last_edited_time | TIMESTAMPTZ | Last Notion edit time. |
| created_at | TIMESTAMPTZ | Created time. |
| updated_at | TIMESTAMPTZ | Updated time. |

### 12.3 source_documents
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Source document primary key. |
| source_type | TEXT | `pdf` / `url` / `youtube` / `screenshot` / `chat_text`. |
| source_display_name | TEXT | Display name based on source rule. |
| source_url | TEXT NULL | Full URL when applicable. |
| file_path | TEXT NULL | Local file path for upload handling. |
| content_hash | TEXT | Hash for dedup. |
| raw_text | TEXT | Parsed raw text. |
| status | TEXT | `received` / `parsed` / `failed`. |
| failure_reason | TEXT NULL | Failure taxonomy value. |
| created_at | TIMESTAMPTZ | Created time. |
| updated_at | TIMESTAMPTZ | Updated time. |

### 12.4 knowledge_chunks
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Chunk primary key. |
| source_kind | TEXT | `notion` or `source_document`. |
| source_ref_id | UUID/TEXT | Source reference id. |
| chunk_text | TEXT | Chunk text. |
| chunk_order | INT | Chunk order. |
| notion_path | TEXT NULL | Notion path metadata. |
| citation_meta | JSONB | Citation metadata. |
| embedding | VECTOR | pgvector embedding. |
| embedding_text | TEXT NULL | Transitional legacy serialized embedding during rollout. |
| is_production | BOOLEAN | Production RAG eligibility flag. |
| created_at | TIMESTAMPTZ | Created time. |
| updated_at | TIMESTAMPTZ | Updated time. |

Rollout note:
- Step 49 migration foundation adds supporting filter indexes on
  `knowledge_chunks.source_kind`, `knowledge_chunks.notion_block_id`,
  `knowledge_chunks.notion_path`, and `notion_blocks.notion_page_id`.
- PostgreSQL also gets a partial HNSW cosine index on non-null
  `knowledge_chunks.embedding`.
- Step 50 writes both live `embedding` and transitional `embedding_text`
  through the shared indexing path on every successful page re-index.

### 12.5 change_requests
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Change request id. |
| target_notion_page_id | TEXT | Target page id. |
| target_section_path | TEXT | Target section path. |
| proposal_text | TEXT | AI proposal text. |
| status | TEXT | `pending` / `accepted` / `rejected`. |
| reviewer | TEXT NULL | Reviewer id or name. |
| reviewed_at | TIMESTAMPTZ NULL | Review timestamp. |
| reject_reason | TEXT NULL | Reject reason. |
| source_document_id | UUID | Linked source document id. |
| created_at | TIMESTAMPTZ | Created time. |
| updated_at | TIMESTAMPTZ | Updated time. |

### 12.6 audit_logs
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Audit event id. |
| workflow_id | UUID | Workflow run id. |
| event | TEXT | Event name. |
| actor | TEXT | `system` / `user` / `reviewer`. |
| entity_type | TEXT | Entity type. |
| entity_id | TEXT | Entity id. |
| payload | JSONB | Structured event payload. |
| created_at | TIMESTAMPTZ | Event timestamp. |

### 12.7 workflow_runs
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Workflow run id. |
| workflow_type | TEXT | `indexing` / `ingestion` / `supplement` / `qa`. |
| status | TEXT | `running` / `succeeded` / `failed`. |
| source_type | TEXT NULL | Source type for this run. |
| source_display_name | TEXT NULL | Source display name. |
| sync_mode | TEXT NULL | `manual` / `auto_after_accept`. |
| reconciliation_strategy | TEXT NULL | `page_level_replacement`. |
| source_of_truth | TEXT NULL | `notion`. |
| duration_ms | INT NULL | Duration in ms. |
| token_input | INT NULL | Input token count. |
| token_output | INT NULL | Output token count. |
| estimated_cost | NUMERIC NULL | Estimated cost. |
| failure_reason | TEXT NULL | Failure taxonomy value. |
| started_at | TIMESTAMPTZ | Start time. |
| finished_at | TIMESTAMPTZ NULL | Finish time. |

### 12.8 telegram_update_ledger
| Column | Type | Description |
|---|---|---|
| update_id | BIGINT (PK) | Telegram update id and idempotency key. |
| status | TEXT | `running` / `succeeded` / `failed`. |
| workflow_run_id | BIGINT NULL | Linked Telegram workflow run when available. |
| result_json | JSON/TEXT NULL | Deterministic successful response for replay. |
| failure_json | JSON/TEXT NULL | Deterministic failure response for replay. |
| created_at | TIMESTAMPTZ | Claim time. |
| updated_at | TIMESTAMPTZ | Last ledger transition time. |

Idempotency rules:
- A unique `update_id` claim is committed before Telegram business work starts.
- A duplicate `running` update returns processing status and does not execute
  the command again.
- A duplicate `succeeded` or `failed` update replays the persisted outcome.
- Updates without `update_id` remain backward-compatible but are not deduped.

### 12.9 api_idempotency_records
| Column | Type | Description |
|---|---|---|
| id | BIGINT (PK) | API idempotency record id. |
| request_scope | VARCHAR(256) | HTTP method and mutation path. |
| idempotency_key | VARCHAR(255) | Caller-provided `Idempotency-Key`. |
| request_fingerprint | VARCHAR(64) | SHA-256 of the canonical request payload. |
| status | TEXT | `running` / `succeeded` / `failed`. |
| response_status_code | INT NULL | Persisted response status for replay. |
| response_body | TEXT NULL | Persisted JSON response body for replay. |
| response_headers_json | JSON/TEXT NULL | Safe replay headers only. |
| created_at | TIMESTAMPTZ | Claim time. |
| updated_at | TIMESTAMPTZ | Last record transition time. |

API mutation idempotency rules:
- `POST /api/ingest/*` and `POST /api/supplement/*` accept an optional
  `Idempotency-Key`; no key preserves existing behavior.
- The first request commits a unique `(request_scope, idempotency_key)` claim
  before business work. A duplicate running claim returns `202` and does not
  execute the mutation again.
- A duplicate completed claim replays the persisted response. Reusing a key
  with a different canonical payload returns `409`.
- Telegram webhook deduplication remains owned by `telegram_update_ledger`.

Metadata note:
- LLM-backed workflows record `provider_name`, `model`, `prompt_id`, and
  `prompt_version` inside workflow metadata JSON, plus the deterministic
  `prompt_safety_version` used for untrusted-content boundaries.
- When token usage is available, the same workflow metadata also records
  `token_input`, `token_output`, and `estimated_cost`.
- Prompt templates under `docs/prompts/*.md` are runtime inputs only when code
  explicitly loads them.

## 13. Core APIs
### 13.1 Notion Index APIs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/notion/index/full` | Trigger full initial index run. |
| POST | `/api/notion/index/page` | Trigger one page re-index by page id. |
| POST | `/api/notion/index/incremental` | Manual sync entrypoint for user manual Notion edits/deletes/merges. |
| GET | `/api/notion/index/status` | Get index workflow status. |

### 13.2 Ingestion APIs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ingest/source` | Create source document metadata from normalized source text. |
| POST | `/api/ingest/document` | Ingest PDF/document source. |
| POST | `/api/ingest/url` | Ingest URL article source. |
| POST | `/api/ingest/youtube` | Ingest YouTube transcript source. |
| POST | `/api/ingest/chat-text` | Ingest pasted chat text. |
| POST | `/api/ingest/image-ocr` | Ingest image OCR source. |

### 13.3 Supplement APIs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/supplement/propose` | Create supplement change request. |
| GET | `/api/supplement/pending` | List pending proposals with review content, citations, and target metadata. |
| GET | `/api/supplement/{change_request_id}` | Read one reviewable proposal detail. |
| POST | `/api/supplement/accept` | Accept change request, append to `AI Supplement Zone`, and trigger immediate page re-index. |
| POST | `/api/supplement/reject` | Reject change request and keep audit/eval record. |
| POST | `/api/supplement/edit-later` | Keep change request in pending state for later review. |

### 13.4 QA API
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/qa` | Run RAG QA and return citation. |

### 13.5 Ops APIs
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check endpoint. |
| GET | `/ready` | Dependency-aware readiness check for database, migration, pgvector, and mode-specific provider configuration. |
| GET | `/metrics` | Metrics endpoint. |

### 13.6 Telegram APIs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/telegram/webhook` | Handle Telegram webhook update for `/help`, `/health`, `/pages`, target-aware `/ingest`, scoped `/ask` QA, and command-based accept/reject review. |

Trust boundary rules:
- API routes under `/api` use `Authorization: Bearer <API_BEARER_TOKEN>` when
  `API_BEARER_TOKEN` is configured. `/health` and `/ready` remain public ops
  surfaces.
- The Telegram webhook uses
  `X-Telegram-Bot-Api-Secret-Token` when `TELEGRAM_WEBHOOK_SECRET` is
  configured, then applies the optional comma-separated
  `TELEGRAM_ALLOWED_CHAT_IDS` policy before starting a workflow.
- Authentication and chat authorization stay deterministic backend checks and
  never depend on an LLM response.

Production-RAG invariant:
- `pending` and `rejected` change requests are never used in production RAG.

Proposal target invariant:
- User-facing proposal APIs use external Notion page ids. The backend resolves
  them to indexed page rows before storing the internal foreign key used by
  the accept transaction.

## 14. Tech Stack Decisions
| Layer | Decision |
|---|---|
| Backend | Python + FastAPI |
| Package manager | uv |
| DB migration | Alembic |
| Database | PostgreSQL |
| Vector DB | pgvector |
| Queue | Redis + RQ behind QueueClient interface |
| Cache/session/idempotency | Redis |
| LLM | OpenAI first behind Provider Router and provider interface |
| Embedding | OpenAI embedding first behind provider interface |
| Tool access | Local Tool Registry first; future MCP Client after contracts stabilize |
| Notion | Official Notion API |
| PDF parsing | PyMuPDF or pdfplumber |
| OCR | Tesseract first, PaddleOCR optional later |
| URL extraction | trafilatura |
| YouTube transcript | youtube-transcript-api |
| Logging | structured JSON logs |
| Deployment | local-first Docker Compose |

Decision notes:
- No standalone MCP server in MVP.
- MCP-oriented provider/tool interfaces are allowed in MVP.
- No LangChain in MVP.
- No LangGraph in MVP.
- Keep RQ access behind QueueClient interface only.
- Keep DB access behind repositories only.

## 15. Guardrails
| Guardrail | Rule |
|---|---|
| No direct overwrite | Never directly overwrite existing Notion notes. |
| No direct edit to manual notes | Never directly edit manually created notes. |
| No direct edit to old AI blocks | Never directly edit old AI supplement blocks. |
| No per-page writable original notes | Never enable per-page writable original-note mode in MVP. |
| Append-only path only | `Change Request -> Human Accept -> Append to AI Supplement Zone`. |
| Manual sync after manual edits | Manual Notion edits/deletes/merges require `/api/notion/index/incremental`. |
| Auto re-index after accepted append | Accepted append must trigger immediate page re-index. |
| Pending/rejected exclusion | `pending` and `rejected` are excluded from production RAG. |
| Notion source of truth | Notion content is authoritative for reconciliation. |
| Secrets management | Never log secrets or private raw source content. |
| Untrusted prompt data | Query, retrieved context, and source text cannot change citations, targets, tools, or write policy. |

## 16. Evaluation Plan
Evaluation metrics:
- retrieval hit rate
- citation accuracy
- write safety
- ownership model compliance
- production-RAG exclusion
- manual sync reconciliation
- failure_reason coverage

Example golden test:

```yaml
id: gq-ownership-001
query: "Summarize NLP week5 attention notes with citation"
scope: "nlp/week5"
expected:
  must_include:
    - "at least 2 Notion path citations"
  must_not_include:
    - "pending change request content"
    - "rejected change request content"
checks:
  ownership_model_compliance: true
  citation_accuracy_min: 0.9
  manual_sync_reconciliation: true
```

## 17. Observability Plan
Required structured fields:
- `workflow_id`
- `workflow_type`
- `event`
- `source_type`
- `source_display_name`
- `sync_mode` (`manual` / `auto_after_accept`)
- `reconciliation_strategy` (`page_level_replacement`)
- `source_of_truth` (`notion`)
- `duration_ms`
- `failure_reason`
- `token_input`
- `token_output`
- `estimated_cost`
- `retrieval_mode`
- `retrieval_fallback_reason`
- `embedding_provider`
- `embedding_model`
- `embedding_dimensions`
- `vector_distance_metric`

Failure taxonomy:
- `NOTION_AUTH_FAILED`
- `NOTION_PAGE_NOT_FOUND`
- `NOTION_BLOCK_FETCH_FAILED`
- `OCR_FAILED`
- `PDF_PARSE_FAILED`
- `URL_FETCH_FAILED`
- `URL_SSRF_BLOCKED`
- `URL_DNS_RESOLUTION_FAILED`
- `URL_REDIRECT_LIMIT_EXCEEDED`
- `URL_RESPONSE_TYPE_UNSUPPORTED`
- `URL_RESPONSE_TOO_LARGE`
- `YOUTUBE_TRANSCRIPT_NOT_FOUND`
- `PROVIDER_NOT_FOUND`
- `LLM_PROVIDER_ERROR`
- `LLM_OUTPUT_INVALID`
- `VECTOR_UPSERT_FAILED`
- `CHANGE_REQUEST_NOT_FOUND`
- `WRITE_POLICY_VIOLATION`
- `DUPLICATE_SOURCE`
- `TELEGRAM_NOT_CONFIGURED`
- `TELEGRAM_SEND_FAILED`
- `TELEGRAM_FILE_DOWNLOAD_FAILED`
- `INVALID_UPLOAD_TYPE`
- `INVALID_UPLOAD_MIME`
- `EMPTY_UPLOAD`
- `UPLOAD_LIMIT_EXCEEDED`
- `UPLOAD_TOO_LARGE`
- `PDF_PAGE_LIMIT_EXCEEDED`
- `IMAGE_PIXEL_LIMIT_EXCEEDED`
- `INVALID_IMAGE`
- `EXTRACTED_TEXT_LIMIT_EXCEEDED`
- `UNKNOWN_ERROR`

## 18. Architectural Decisions
- ADR-001: Use FastAPI.
- ADR-002: MCP-oriented architecture; no standalone MCP server in MVP.
- ADR-003: No LangChain Agent in MVP.
- ADR-004: No LangGraph in MVP.
- ADR-005: Use PostgreSQL + pgvector.
- ADR-006: Use RQ behind Queue Interface.
- ADR-007: Append-only AI Supplement Zone.
- ADR-008: Notion is source of truth.
- ADR-009: Manual sync for manual edits.
- ADR-010: Auto page re-index after accepted append.
- ADR-011: No per-page writable original notes in MVP.

## 19. Final MVP Definition
MVP is complete only when all statements below are true:
- All Notion notes are read-only for direct agent editing.
- AI writes only through `Change Request -> Human Accept -> Append to AI Supplement Zone`.
- There is no direct overwrite.
- There is no per-page writable original notes mode in MVP.
- Manual Notion edits require manual incremental sync.
- Accepted agent append triggers auto page re-index.
- `pending` and `rejected` change requests are never used in production RAG.
- QA answers include Notion path citation.
- MVP runs locally only.
