# 06 Notion Permission Model

## Purpose
This document defines Notion ownership, read-only rules, `AI Supplement Zone`, and manual edit behavior.

## Status
Draft

This document is development and maintenance context.
It is not a production RAG source unless a future ADR and implementation explicitly make it one.

## Source of Truth
These rules are based on `AGENTS.md`, `docs/00-design-doc.md`, `docs/01-architecture.md`, `docs/03-guardrails.md`, `docs/11-coding-style.md`, and the current project roadmap.
Notion is the source of truth for note content.

## Ownership Types
| Ownership type | Meaning |
|---|---|
| Original user notes | Existing Notion pages and blocks that the user created before or outside the agent. |
| Manual user blocks | Any blocks the user creates or edits manually, including newly created notes. |
| Old AI supplement blocks | AI content that was already accepted and appended in an earlier workflow. |
| Current append target under `AI Supplement Zone` | The only Notion location where an accepted change request may create new blocks. |
| Pending change requests | Proposed AI content waiting for human review. |
| Rejected change requests | Proposed AI content rejected by the user. |
| Accepted change requests | Proposed AI content approved by the user and eligible for append. |

## Permission Matrix
| Target | Agent read | Agent write | Agent delete | Production RAG eligibility | Notes |
|---|---|---|---|---|---|
| Original user notes | Yes | No | No | Yes, after indexing | Read-only knowledge source. |
| Manual user blocks | Yes | No | No | Yes, after manual incremental sync | Manual user edits require `/api/notion/index/incremental`. |
| Old AI supplement blocks | Yes | No | No | Yes, if present in current Notion index | Old AI blocks are immutable to the agent. |
| Current append target under `AI Supplement Zone` | Yes | Append only after human accept | No | Yes, after append and immediate page re-index | Only `Change Request -> Human Accept -> Append to AI Supplement Zone` is allowed. |
| Pending change requests | Yes, in workflow state | No Notion write | No Notion delete | No | Excluded from production RAG. |
| Rejected change requests | Yes, for audit and evaluation | No Notion write | No Notion delete | No | Excluded from production RAG. |
| Accepted change requests | Yes, in workflow state | Append to `AI Supplement Zone` only | No Notion delete | Yes, only after append and re-index | Append success triggers immediate page re-index. |

## `AI Supplement Zone` Layout
Accepted supplements must be appended under `AI Supplement Zone` using this shape:

```text
Original page/toggle/section
+-- AI Supplement Zone
    +-- YYYY-MM-DD
        +-- Topic title
            - Source: ...
            - Summary: ...
            - Key Concepts: ...
            - Notes: ...
            - LearnLoop Change Request: change-request-<id>
```

Rules:
- Do not create excessive nested toggles.
- Group supplements by date, then topic.
- Keep the fixed labels `Source`, `Summary`, `Key Concepts`, and `Notes`.
- Source display must follow the source type rule from `docs/00-design-doc.md`.

## Write Rules
The agent may create Notion blocks only when all conditions are true:
- A change request exists.
- The change request is accepted by a human.
- The target location is under `AI Supplement Zone`.
- The operation is append-only.
- The workflow can trigger immediate page re-index after append.
- The appended entry includes a visible deterministic change-request identity
  so retries can be reconciled against Notion as source of truth.

The agent must not:
- Edit original user notes.
- Edit manual user blocks.
- Edit old AI supplement blocks.
- Delete Notion blocks.
- Move Notion blocks.
- Create per-page writable original-note mode in MVP.

Violations must fail closed with `WRITE_POLICY_VIOLATION`.

## Manual Edit Reconciliation
Users may manually edit Notion at any time.
Manual user actions are valid, including:
- Editing original notes.
- Creating new notes or blocks.
- Moving or merging AI supplement content into original notes.
- Deleting AI supplement blocks.

Because there is no always-on sync in MVP, manual changes require `/api/notion/index/incremental`.
The incremental sync must treat current Notion content as authoritative and reconcile derived PostgreSQL and vector state by page-level replacement.

## RAG Eligibility
Production RAG may include:
- Current indexed Notion content.
- Accepted AI supplement content after it exists in Notion and the page has been re-indexed.

Production RAG must exclude:
- `pending` change requests.
- `rejected` change requests.
- Accepted change requests that have not yet been appended and re-indexed.
- Development docs unless a future ADR and implementation explicitly allow them.

## Architecture Boundary
Permission checks and Notion write safety stay in deterministic backend logic.
They must not be delegated to an LLM, Provider Router, Provider Adapter, Tool Registry, Local Tool Adapter, future MCP Client, future MCP server, or external API.

Allowed architecture flow:

```text
API Route
-> Orchestrator
-> Service / Tool
-> Repository / Adapter
-> External System
```

The Notion writer tool may perform an append call later, but backend policy must decide whether the append is allowed before the tool is invoked.

## MVP Non-Goals
The MVP does not support:
- Direct original note editing by the agent.
- Per-page writable original-note mode.
- Inline proposal edit UI.
- Always-on cloud sync.
- Standalone MCP servers.
- LangChain or LangGraph.
