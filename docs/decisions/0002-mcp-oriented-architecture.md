# ADR-0002: MCP-Oriented Architecture

## Status
Accepted

## Date
2026-05-19

## Context
LearnLoop MVP starts with OpenAI, local FastAPI, PostgreSQL, pgvector, Redis/RQ, and Notion.
Future versions should be able to add Claude and Gemini providers without changing orchestrators.
Future tool exposure through MCP should also be possible, but the MVP should not start by running standalone MCP servers.

## Decision
LearnLoop will be MCP-oriented and provider-agnostic:
local tool interfaces first, real MCP servers later.

Provider access:
- LLM calls go through Provider Router and provider adapters.
- OpenAI is the first provider adapter.
- Claude and Gemini adapters must share the same orchestrator-facing interface.
- Orchestrators must not import OpenAI, Claude, Gemini, or other provider SDKs directly.

Tool access:
- External capabilities go through Tool Registry and schema-friendly local tool adapters.
- Tool contracts should be compatible with future MCP exposure.
- Real MCP servers or MCP SDK dependencies are deferred until tool contracts stabilize.
- A future MCP Client can sit behind the Tool Registry without changing orchestrators.

Deterministic backend ownership:
- Permission checks stay in backend code.
- Notion write safety stays in backend code.
- RAG inclusion and exclusion rules stay in backend code.
- Output validation stays in backend code.
- Proposal state transitions stay in backend code.

Infrastructure ownership:
- PostgreSQL and pgvector access stays behind repositories.
- Redis/RQ access stays behind QueueClient.
- Raw PostgreSQL and Redis must not become LLM-facing tools.

## Implementation Notes (2026-05-20)
Implemented boundary skeletons:
- `src/providers/`: `LLMProvider`, request/response models, and `ProviderRouter`.
- `src/tools/`: `Tool`, `ToolSpec`/`ToolContext`/`ToolResult` models, and `ToolRegistry`.

Planned MCP extraction scope:
- Local Notion read/write adapters can become MCP servers later.
- Local ingestion adapters (PDF/OCR/URL/YouTube) can become MCP servers later.
- Local retrieval adapter can become an MCP server facade later.

Non-transferable backend ownership:
- Permission checks and ownership model enforcement.
- `AI Supplement Zone` append-only safety and accept gate checks.
- Production-RAG inclusion/exclusion policy.
- Output validation, failure taxonomy mapping, and state transitions.
- Queue/idempotency policy and audit decisions.

## Consequences
- MVP can remain local-first and simple.
- OpenAI, Claude, and Gemini can share one provider boundary.
- Local tools can later be extracted into MCP servers without changing orchestrators.
- The LLM does not own safety, permission, validation, or persistence decisions.
