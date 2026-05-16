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
- Do not add LangChain/LangGraph/MCP implementation in MVP.
- Add comments only for purpose or non-obvious logic.
- Update `dev_state/DAILY_LOG.md` after meaningful local development work.
