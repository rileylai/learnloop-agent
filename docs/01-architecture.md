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

## Infrastructure Boundary
- PostgreSQL and pgvector are accessed only through repositories.
- Redis/RQ is accessed only through QueueClient.
- Raw PostgreSQL and Redis must not become LLM-facing tools.
- API routes must not directly call Notion, OpenAI, Claude, Gemini, Redis, PostgreSQL, or external APIs.
