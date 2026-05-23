# 03 Guardrails

## Purpose
This document defines safety rules, write policy, production-RAG exclusion, and failure handling for LearnLoop Agent.

## Status
Draft

This document is development and maintenance context.
It is not a production RAG source unless a future ADR and implementation explicitly make it one.

## Source of Truth
These rules are based on `AGENTS.md`, `docs/00-design-doc.md`, `docs/01-architecture.md`, `docs/11-coding-style.md`, and the current project roadmap.
Do not weaken these rules without updating the design docs and recording a decision.

## Safety Invariants
| Guardrail | Rule |
|---|---|
| Read-only by default | Treat all existing Notion notes as read-only for direct agent editing. |
| No direct overwrite | Never directly overwrite existing Notion notes. |
| No direct edit to manual notes | Never directly edit manually created notes or blocks. |
| No direct edit to old AI blocks | Never directly edit old AI supplement blocks after they have been appended. |
| No original-note write mode | Never create per-page writable original-note mode in MVP. |
| Append-only write path | All AI writes must follow `Change Request -> Human Accept -> Append to AI Supplement Zone`. |
| Production-RAG exclusion | `pending` and `rejected` change requests must not be used in production RAG. |
| Notion source of truth | Notion is the source of truth for note content and reconciliation. |
| Manual sync after manual edits | User manual Notion edits, deletes, and merges require `/api/notion/index/incremental`. |
| Auto re-index after accept | Accepted agent appends must trigger immediate page re-index. |
| No secret or raw private content logs | Never log secrets, API keys, or private raw source content. |

## Write Policy
The only allowed AI write path is:

```text
Change Request
-> Human Accept
-> Append to AI Supplement Zone
-> Immediate page re-index
-> Accepted content becomes available in production RAG
```

Rules:
- Proposal generation does not write to Notion.
- `pending` change requests stay in workflow state only and are excluded from production RAG.
- `rejected` change requests stay available for audit and evaluation only and are excluded from production RAG.
- `accepted` change requests may be appended only to `AI Supplement Zone`.
- The agent may append accepted content, but must not update or delete original blocks or old AI supplement blocks.
- If a retry happens after an accepted append, idempotency must prevent duplicate writes.

## Manual Notion Edits
Users may manually edit Notion because Notion is the source of truth.
Valid user actions include:
- Editing original notes.
- Creating new manual notes.
- Merging AI supplement content into original notes.
- Deleting AI supplement blocks.

After those manual actions, the user must run `/api/notion/index/incremental`.
The system must reconcile derived PostgreSQL and vector state by page-level replacement from current Notion content.

## Production-RAG Rules
Production RAG may retrieve:
- Indexed current Notion content.
- Accepted AI supplement content after it has been appended and re-indexed.

Production RAG must not retrieve:
- `pending` change requests.
- `rejected` change requests.
- Development docs such as `AGENTS.md` or `docs/*.md`, unless a future ADR and implementation explicitly allow that.
- Raw private source content that should not be exposed in logs or answers.

## Deterministic Backend Ownership
Guardrails are deterministic backend logic.
They must not be delegated to an LLM, prompt text, Provider Router, Provider Adapter, Tool Registry, Local Tool Adapter, future MCP Client, future MCP server, or external API.

Backend code owns:
- Permission checks.
- Notion write safety.
- RAG inclusion and exclusion rules.
- Output validation.
- Change request state transitions.
- Audit logging decisions.
- Failure reason mapping.

Provider and tool boundaries may execute requests, but they do not decide whether a write is allowed.

## Failure Handling
If code attempts a prohibited Notion write or RAG inclusion, fail closed.
Use `WRITE_POLICY_VIOLATION` as the `failure_reason` for write-policy violations.

Expected behavior:
- Do not perform the Notion write.
- Do not include unsafe content in production RAG.
- Record an audit or workflow failure event without secrets or raw private content.
- Return a deterministic error that callers can test.

## MVP Non-Goals
The MVP does not support:
- Direct original note editing by the agent.
- Per-page writable original-note mode.
- Inline proposal edit UI.
- Always-on cloud sync.
- Standalone MCP servers.
- LangChain or LangGraph.
