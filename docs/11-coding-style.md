# 11 Coding Style

## Purpose
This document defines repository coding style and documentation rules.

## Status
Draft

This document will be expanded in later steps.

What belongs here:
- Python coding conventions.
- Layered architecture coding rules.
- Documentation maintenance rules.

## Coding and Documentation Rules
- Use simple English in docs.
- Use Python type hints.
- Keep routes thin.
- Put orchestration in orchestrator modules.
- Put external system access in tools/providers.
- Put DB access in repositories.
- Do not write RQ directly into business logic.
- Do not add LangChain, LangGraph, standalone MCP servers, or MCP SDK dependencies in MVP.
- MCP-oriented, schema-friendly tool/provider interfaces are allowed.
- Orchestrators must call Provider Router or Tool Registry, not provider SDKs or external APIs directly.
- Permission checks, write safety, RAG inclusion, output validation, and state transitions stay in deterministic backend code.
- Add comments only for purpose or non-obvious logic.
- Update `dev_state/DAILY_LOG.md` after meaningful local development work.
