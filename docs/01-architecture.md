# 01 Architecture

## Purpose
This document defines system architecture, component boundaries, and future diagrams.

## Status
Draft

What belongs here:
- Layer boundaries and dependency rules.
- Runtime component diagram.
- Integration boundaries for Notion, LLM, queue, and storage.

## Core Layering
Primary request flow:

```text
API Route
-> Orchestrator
-> Service / Tool / Provider
-> Repository / Adapter
-> External System
```

Provider flow:

```text
API Route
-> Orchestrator
-> Provider Router
-> Provider Adapter
-> OpenAI / Claude / Gemini
```

Tool flow:

```text
API Route
-> Orchestrator
-> Tool Registry
-> Local Tool Adapter or future MCP Client
-> Notion / RAG / Memory / External API
```

## MCP-Oriented Boundary
LearnLoop is MCP-oriented, not MCP-server-first.

MVP rules:
- Use local tool adapters behind a common Tool Registry.
- Keep tool input/output contracts schema-friendly.
- Do not add standalone MCP servers or MCP SDK dependencies in MVP.
- A future MCP Client can sit behind the Tool Registry after contracts stabilize.
- Extracting a tool into a real MCP server must not change orchestrator logic.

Provider rules:
- LLM calls go through Provider Router and provider adapters.
- OpenAI is the first provider.
- Claude and Gemini adapters must share the same orchestrator-facing interface.
- Orchestrators must not import provider SDKs directly.

Backend-owned deterministic logic:
- Permission checks.
- Notion write safety.
- RAG inclusion and exclusion rules.
- Output validation.
- Proposal state transitions.
- Audit logging decisions.

## Current Interface Skeletons (Implemented)
Provider boundary (Step 6.1):
- `src/providers/models.py`: `LLMMessage`, `LLMRequest`, `LLMResponse`.
- `src/providers/base.py`: `LLMProvider`.
- `src/providers/router.py`: `ProviderRouter` with deterministic registration and lookup errors.

Provider client implementation (Step 18):
- `src/providers/llm.py`: `BaseLLMClient`, `OpenAIClient`, and deterministic `LLMClientError`.
- `OpenAIClient` uses transport injection for deterministic tests and stays behind the provider interface.

Embedding provider implementation (Steps 14 and 50):
- `src/providers/embedding.py`: `EmbeddingClient`, `EmbeddingRequest`,
  `EmbeddingResponse`, and `OpenAIEmbeddingClient`.
- Indexing orchestrators depend on `EmbeddingClient`, not provider SDKs,
  and pass embedded chunk data to repositories only after provider success.

Runtime prompt loading (Step 44):
- `src/services/prompt_template_loader.py`: loads versioned prompt bundles from
  `docs/prompts/*.md`.
- Orchestrators receive the prompt loader as a service dependency.
- Workflow metadata records `prompt_id` and `prompt_version` with provider/model
  metadata for LLM-backed workflows.

Tool boundary (Step 6.2):
- `src/tools/models.py`: `ToolSpec`, `ToolContext`, `ToolResult`, `ToolError`.
- `src/tools/base.py`: `Tool`.
- `src/tools/registry.py`: `ToolRegistry` with deterministic registration and lookup errors.

Orchestrator contract:
- Orchestrators call `ProviderRouter` and `ToolRegistry` only.
- Orchestrators do not import provider SDKs, Notion SDK, Redis clients, or DB drivers directly.
- Shared indexing uses:
  `NotionPageIndexOrchestrator -> EmbeddingClient -> ChunkRepository`.
- Semantic vector top-k retrieval uses:
  `ProductionChunkRetriever -> ChunkRepository -> PostgreSQL + pgvector`.

## Current Runtime Wiring and Readiness

The architecture sections in this document describe both implemented
boundaries and the target MVP integration shape. Current runtime wiring is:

- `get_tool_registry()` selects a shared Notion reader/writer backend from
  `NOTION_BACKEND=mock|live` (default `mock`). Mock mode uses the configured
  JSON page set for both clients. Live mode constructs the read-only and
  append-only REST adapters and requires `NOTION_TOKEN`; it never falls back
  to mock mode.
- `NotionFullIndexOrchestrator` discovers external Notion page ids through the
  reader tool, then reuses `NotionPageIndexOrchestrator` for each page's
  page-level replacement and embedding flow. `GET /api/notion/index/status`
  reads workflow state through `WorkflowRunService` and does not contact
  Notion.
- Real OpenAI LLM and embedding adapters are registered only when
  `OPENAI_API_KEY` is present. Shared page indexing requires the embedding
  adapter and fails closed when it is absent.
- PostgreSQL/pgvector repository paths and migrations exist. Their opt-in live
  verification is separate from the default deterministic suite.
- `/health` remains a shallow liveness route. `/ready` calls the deterministic
  readiness service, which uses a database readiness probe for connectivity,
  Alembic revision, and pgvector extension checks plus mode-specific provider
  configuration checks.
- `RQQueueClient` exists behind `QueueClient`, but runtime dependencies do not
  enqueue work and the repository has no worker entrypoint. Redis is therefore
  not part of current request execution.
- API and Telegram orchestration are synchronous and unauthenticated.
- Parser and Telegram HTTP adapters exist, but external-service E2E remains
  live verification work.

These gaps are tracked in the `Real-World Usability + Release Hardening` phase
of `dev_state/PROJECT_ROADMAP.md`. They must be closed through the existing
provider, tool, queue, repository, and deterministic policy boundaries.

## Future MCP Server Boundary (Post-MVP)
Tools that may be extracted into MCP servers later:

| Local Adapter Family | Future MCP Server Candidate | Keep in Backend |
|---|---|---|
| Notion read access | Notion reader server | Permission checks and page ownership policy. |
| Notion write access | Notion append-only writer server | `AI Supplement Zone` write safety and accept-gate checks. |
| Ingestion adapters | PDF/OCR/URL/YouTube parser servers | Source validation, dedup policy, and workflow decisions. |
| Retrieval adapter | Vector search server facade | Production-RAG inclusion/exclusion and citation policy. |

Logic that must stay deterministic backend code (not MCP-owned):
- Permission checks and ownership model enforcement.
- Notion write safety (`Change Request -> Human Accept -> Append`).
- Production-RAG eligibility checks (`pending` and `rejected` exclusion).
- Output schema validation and failure_reason mapping.
- Change request state transitions and audit decisions.
- Queue scheduling policy and idempotency handling.

## Infrastructure Boundary
- PostgreSQL and pgvector are accessed only through repositories.
- Redis/RQ is accessed only through QueueClient.
- Raw PostgreSQL and Redis must not become LLM-facing tools.
- API routes must not directly call Notion, OpenAI, Claude, Gemini, Redis, PostgreSQL, or external APIs.
- Manual incremental sync and auto-after-accept re-index both reuse the same
  embedding-aware page indexing orchestrator instead of duplicating vector
  persistence logic in routes or review flows.
- pgvector distance ordering, NULL-vector exclusion, and filter-before-top-k
  behavior must stay inside repository queries rather than Python-side
  orchestrator ranking.
