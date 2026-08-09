# Guardrails

## Core invariants

- Existing Notion content is read-only to the agent.
- Old AI supplement blocks are read-only.
- AI writes require an explicit human accept action.
- Accepted writes append only inside `AI Supplement Zone`.
- Pending and rejected proposals are excluded from production RAG.
- Notion is the source of truth for page content.
- Manual Notion edits require an explicit sync.
- Accepted appends trigger target-page re-indexing before retrieval eligibility.
- Secrets, raw source text, OCR text, prompts, embeddings, and private Notion
  content are not emitted in logs or operator responses.

## Write policy

The only supported agent write is:

```text
pending Change Request
  -> explicit human accept
  -> append_ai_supplement_zone
  -> durable identity verification
  -> page re-index
```

The writer has no update, delete, move, or original-note method. Backend code
derives the target from the indexed page and rejects targets outside that
page's `AI Supplement Zone`. The provider may generate content fields only;
source, target, citation, and identity fields remain backend-owned.

## Retrieval eligibility

Production QA filters before ranking:

- `source_kind=notion`;
- eligible indexed page and section scope;
- complete, current page-derived chunks;
- usable vector data for vector ranking when available.

Pending, rejected, synthetic, non-Notion, stale, or uncommitted data must not
enter production retrieval. A vector failure may fall back to lexical retrieval
over the same safe scope, but indexing never writes a partial vector snapshot.

## Trust boundaries

API bearer authentication is checked for protected `/api` routes. Telegram
webhooks validate `X-Telegram-Bot-Api-Secret-Token` when configured and can
restrict updates with `TELEGRAM_ALLOWED_CHAT_IDS`. Callback mappings are
owned by exact `(chat_id, user_id)` pairs.

Authorization, target selection, review state, callback claims, RAG filters,
citations, and Notion writes are deterministic backend decisions. Prompt
delimiters mark query, source, and retrieved context as untrusted data; text
inside those fields cannot grant tools, change targets, bypass review, or
alter citations.

## Bounds and external calls

Uploads, extracted text, URL redirects, URL response size, OCR batch size,
Notion reads, embedding batches, queue jobs, and Telegram messages are all
bounded. Parser and orchestrator layers revalidate limits because callers such
as Telegram do not share the HTTP upload boundary.

Indexing uses complete in-memory page preparation followed by page-level
replacement. Embedding batches are contiguous and sequential. Only retryable
timeouts, transport failures, HTTP 408/429, and allowlisted 5xx responses are
retried. Authentication errors, deterministic 4xx errors, invalid responses,
and vector shape mismatches are not retried.

## Concurrency and idempotency

- API mutations accept an optional `Idempotency-Key` and replay the persisted
  response for the same canonical payload.
- Telegram updates use a unique durable `update_id` ledger.
- One-shot callbacks are claimed atomically and expire from session storage.
- Concurrent reviews lock and revalidate the change request before changing
  status.
- Page replacement validates the prepared page snapshot before deleting or
  inserting derived rows.
- A Notion append is identified by `change-request-<id>` and verified by a
  read-after-write lookup before accepted state is committed.

## Failure handling

Failures return a stable `error_code`, `failure_reason`, and workflow reference
where applicable. Raw upstream exception text is not part of the public error
contract. Important reasons include `NOTION_AUTH_FAILED`,
`NOTION_APPEND_NOT_VERIFIED`, `STALE_PAGE_SNAPSHOT`, `LLM_OUTPUT_INVALID`,
`EMBEDDING_PROVIDER_ERROR`, `VECTOR_QUERY_FAILED`, `QUEUE_JOB_TIMEOUT`,
`TELEGRAM_QUEUE_UNAVAILABLE`, `WRITE_POLICY_VIOLATION`, and upload/URL/OCR
validation reasons.

An audit-update failure is separate from the business result. It must not undo
or repeat a committed append, review, or index operation. Stale workflow
reconciliation is explicit and never reruns business work.

## Data handling

Structured logs may contain workflow ids, route/method/status, operation names,
bounded counts, safe failure reasons, provider/model names, prompt versions,
and known usage/cost fields. They must not contain API keys, bearer values,
Telegram tokens, Notion tokens, URLs with credentials, callback tokens, Redis
keys, raw source/OCR text, prompts, vectors, or private page content.

## Out of scope

The MVP does not support direct original-note editing, per-page writable
original-note mode, inline proposal editing, always-on cloud sync, standalone
MCP servers, LangChain, LangGraph, reranking, or LLM-as-judge.

The [Notion permission model](06-notion-permission-model.md) describes the
content ownership matrix in more detail.
