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

## Current Verification Boundary

These invariants are confirmed by deterministic backend tests, in-memory
Notion writer evaluations, fake-transport tests for the read-only live Notion
reader and append-only live Notion writer, and guarded Step 82/83 canary
contracts. Step 83 requires separate live opt-in and human approval before a
sandbox append. Live integration work must preserve every invariant below and
add redacted contract evidence; it must not replace deterministic policy with
prompt behavior.

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
| Caller trust boundaries | Enforce configured API bearer, Telegram webhook secret, and allowed-chat policy in deterministic backend code before business work. |
| Upload resource limits | Enforce deterministic file-count, byte, MIME, PDF-page, image-pixel, and extracted-text limits before expensive parser or OCR work. |
| Untrusted prompt data | Treat user query, retrieved context, and source text as data; embedded instructions cannot change citations, targets, tool calls, or write policy. |

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
- Proposal review APIs may expose pending content and target metadata, but they
  must not invoke a Notion write operation.
- Proposal generation does not write to Notion.
- `pending` change requests stay in workflow state only and are excluded from production RAG.
- `rejected` change requests stay available for audit and evaluation only and are excluded from production RAG.
- `accepted` change requests may be appended only to `AI Supplement Zone`.
- The agent may append accepted content, but must not update or delete original blocks or old AI supplement blocks.
- Accepted supplement content includes a visible deterministic identity line
  (`LearnLoop Change Request: change-request-<id>`).
- The writer must verify that identity is visible after append using a bounded
  read-after-write check. If verification fails, the workflow fails closed and
  keeps the change request retryable.
- If a retry happens after an append or a lost writer response, durable identity
  detection must prevent duplicate writes even with a fresh client instance.
- The accept transaction must reload and lock the change request, revalidate
  `pending`, persist the page re-index mutation set, and update `accepted` in
  one business transaction. This does not claim cross-system atomicity with Notion.

Target policy:
- User-facing proposal APIs accept external Notion page ids only.
- The backend resolves an external id to an indexed `notion_pages` row before
  storing the internal foreign key used by the accept transaction.
- Unknown external targets fail closed with `NOTION_PAGE_NOT_FOUND`; no
  proposal write or Notion write is performed for that target.
- When a selected target page exists, the proposal's suggested `target_path`
  must remain under that page's `AI Supplement Zone`. The accept path remains
  backend-derived and append-only even if proposal text is adversarial.

Telegram review policy:
- `/pages` and proposal preview are read-only operations.
- `/ingest --page <external_page_id>` may create only a `pending` change
  request; it must not append to Notion.
- Telegram `/accept` remains the human acceptance event and may append only
  after the existing target and pending-state checks pass.

Telegram ingestion session policy:
- The primary upload flow never asks the user to type a Notion UUID. It stores
  a short-lived upload session in Redis, keyed with both Telegram chat id and
  user id, and requires a fresh upload after TTL expiry.
- A media group is aggregated by `media_group_id` and deduplicated by Telegram
  file identity. Settle, target selection, and preview delivery use atomic
  claims so retries cannot repeat OCR, proposal creation, or preview messages.
- Inline callback data contains only an opaque short-lived action token. The
  Redis mapping restores the canonical external Notion page id and hierarchy
  path after re-checking chat/user ownership; canonical ids never move into
  the UI short-number mapping or replace backend target identity.
- Parent and child pages are independent selectable targets. A target-aware
  pending proposal is created only after one page is selected.
- An unexpired session with no media, an expired session, a cross-user lookup,
  or an invalid callback fails closed with a clear error. No stale upload is
  guessed or borrowed from another chat/user.
- Inline Accept is only a deliberate user callback. It delegates to the
  existing `SupplementReviewOrchestrator`, allowed-chat checks, pending/target
  checks, append-only `AI Supplement Zone` policy, and immediate re-index
  guardrails. No worker, callback resolver, or preview path auto-accepts.
- A proposal without a target must not display an Accept prompt and remains
  rejected by the existing accept guardrail until a valid target is set.

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

Prompt safety ownership:
- Prompt delimiters are defense-in-depth context boundaries, not authorization.
- The backend owns citation paths, target-page resolution, proposal validation,
  human acceptance, and append-only write checks.
- No LLM output can grant itself a tool, Notion, or target-page permission.

## Failure Handling
If code attempts a prohibited Notion write or RAG inclusion, fail closed.
Use `WRITE_POLICY_VIOLATION` as the `failure_reason` for write-policy violations.

Expected behavior:
- Do not perform the Notion write.
- Do not include unsafe content in production RAG.
- Record an audit or workflow failure event without secrets or raw private content.
- Return a deterministic error that callers can test.

Upload safety behavior:
- Reject oversized or unsupported uploads before starting an ingestion
  workflow when the API can validate metadata and bytes at the boundary.
- Revalidate limits in orchestrators and parser adapters because Telegram
  downloads and non-HTTP callers bypass multipart metadata.
- Never log upload bytes, extracted raw text, or full parser exception bodies.

URL fetch safety behavior:
- Accept only absolute HTTP(S) URLs without embedded credentials.
- Reject localhost and non-public IPv4/IPv6 addresses, including any private
  or link-local address returned by DNS.
- Disable implicit redirect following; validate every redirect target and stop
  after the bounded redirect limit.
- Accept only text article response types and read at most the configured URL
  response byte limit. Return specific failure reasons without exposing
  upstream exception bodies.

## MVP Non-Goals
The MVP does not support:
- Direct original note editing by the agent.
- Per-page writable original-note mode.
- Inline proposal edit UI.
- Always-on cloud sync.
- Standalone MCP servers.
- LangChain or LangGraph.

## Security Review Checklist
Use this checklist before demos and release-style local runs.

| Check | Required state |
|---|---|
| Secret files | `.env` and `.env.*` stay ignored by Git. Only `.env.example` may be tracked. |
| Structured logs | Logs emit only approved request fields plus sanitized event text. |
| API keys and tokens | Bearer tokens, API keys, and Telegram bot tokens must be redacted from logs and surfaced error messages. |
| Caller authentication | Configured API bearer and Telegram webhook secret failures return deterministic 401/403 responses before workflow creation. |
| Raw private source content | `raw_text` and `source_text` values must not appear in logs or surfaced error messages. |
| Workflow metadata | Metadata may include workflow IDs, provider/model names, prompt version, token counts, and cost. It must not include secrets or raw source text. |
| Production RAG | Development docs, `pending`, and `rejected` change requests remain excluded from production retrieval. |

## Step 83 Canary Boundary

- The canary uses ephemeral SQLite for the pending proposal and derived index;
  it does not write proposal state to the production database.
- It may append only after the operator supplies both live opt-in and explicit
  human approval flags.
- The canary's transport allows only page/block reads and append-only block
  child PATCH calls, and reports no page ids, credentials, or source content.
- A successful run must verify the visible durable change-request identity,
  accepted DB state, re-indexed chunks, and a citation scoped to the target
  page.
