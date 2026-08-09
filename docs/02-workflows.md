# Workflows

This document describes the implemented business workflows. Routes only
validate transport requests and delegate to orchestrators.

## Notion indexing

### Full index

```text
Create indexing workflow
  -> discover accessible Notion pages
  -> read each page and its block tree
  -> build citation paths and chunks
  -> plan and execute bounded embeddings
  -> replace that page's derived snapshot atomically
  -> record counts and outcome
```

Pages are processed sequentially. If one page fails, previously committed pages
remain committed, the failed page keeps its previous complete snapshot, and
later pages are not attempted. With Redis, Telegram `/index-full` queues a
dedicated job and returns the workflow id for `/index-status`.

### Page index and manual sync

`POST /api/notion/index/page` indexes one external Notion page. `POST
/api/notion/index/incremental` accepts one or more known changed page ids and
reconciles each from current Notion content. Each page uses the same page
indexer, embedding service, and replacement transaction. Manual Notion changes
are not detected automatically.

## Source ingestion

The supported source paths are:

```text
PDF / URL / YouTube transcript / screenshot batch / chat text
  -> validate size and source constraints
  -> parse and normalize
  -> persist SourceDocument and content hash
  -> optionally generate a proposal
```

The ingestion API stores a source document. The proposal API then runs the
duplicate check and provider path. Telegram combines upload, parsing, source
persistence, proposal generation, and preview delivery through the same
orchestrators.

Resource limits are enforced before expensive work and revalidated by adapters:

| Resource | Limit |
| --- | ---: |
| PDF upload | 10 MiB |
| PDF pages | 100 |
| Extracted text | 200,000 characters |
| OCR images per request | 10 |
| Each OCR image | 5 MiB |
| OCR batch | 20 MiB |
| Image pixels | 40,000,000 |
| Pasted chat text | 10,000 characters |

URL ingestion accepts public HTTP(S) article URLs, validates redirect targets,
blocks private/local addresses, limits response size, and accepts only text
content. YouTube ingestion requires a supported video URL and an available
transcript. Screenshot OCR requires Tesseract languages `eng`, `chi_tra`, and
`chi_sim`.

## Proposal generation and review

```text
SourceDocument
  -> duplicate check against eligible Notion chunks
  -> provider generates title, summary, concepts, and notes
  -> backend merges canonical source and target fields
  -> strict validation
  -> Change Request(status=pending)
```

The provider never owns source identity, target identity, citations, or
attachment count. Invalid output fails with `LLM_OUTPUT_INVALID`. Proposal
generation does not write to Notion.

Review transitions are:

```text
pending -> accepted
pending -> rejected
pending -> pending  (edit later)
```

Reject and edit-later do not call Notion. The pending query surface is read-only
and provides proposal content, source display information, citations, and the
current target page.

## Accept, append, and re-index

```text
Load and lock pending Change Request
  -> validate target and proposal
  -> append under AI Supplement Zone
  -> verify change-request-<id> is visible
  -> prepare complete target-page snapshot
  -> lock and revalidate pending state
  -> replace page blocks/chunks/vectors and mark accepted in one DB transaction
```

The Notion append is append-only and carries a durable identity. A retry first
checks that identity, so a successfully committed Notion append is not
duplicated. If append verification or re-indexing fails, the change request
remains pending for safe recovery. Only the successful accept path makes the
new content eligible for production QA.

## Grounded QA

```text
Validate question and scope
  -> create query embedding when configured
  -> retrieve eligible Notion chunks
  -> use lexical fallback when vector retrieval is unavailable
  -> render untrusted context for the LLM
  -> return answer and backend-owned Notion path citations
```

QA supports page and section scopes and a bounded `top_k`. It never retrieves
pending or rejected proposals. If no supporting chunks are available, the
response marks `insufficient_info` rather than inventing an answer.

## Telegram processing

With Redis:

```text
Webhook
  -> validate secret and allowed chat
  -> claim update idempotency record
  -> enqueue serializable envelope on telegram queue
  -> return 202
  -> worker runs the gateway and persists terminal outcome
```

Without Redis, a synchronous compatibility path is retained for local/test
operation. Duplicate Telegram `update_id` values replay a running or terminal
outcome and do not repeat OCR, LLM calls, appends, or replies. Callback data is
opaque, TTL-bound, owner-bound, and atomically claimed.

Callback acknowledgement, business completion, and preview delivery are
tracked independently. Acknowledgement failure does not undo committed
business work. A post-commit preview failure keeps the pending proposal and is
recoverable by resending the existing preview.

See the [Telegram operator contract](13-telegram-operator-contract.md) for
operator commands and callback classes.

## Reliability properties

- Notion reads and embedding batches use bounded retry for retryable transport,
  timeout, rate-limit, and allowlisted upstream server failures.
- Invalid requests, authentication failures, invalid provider responses, and
  dimension/count mismatches fail without retry.
- Database row locks and state revalidation prevent concurrent review or page
  replacement from committing conflicting state.
- API mutations support optional `Idempotency-Key` replay; Telegram uses its
  update ledger instead.
- Workflow audit failure is reconciled separately and never reruns business
  work.

For operational recovery, see [incident recovery](runbooks/incident-recovery.md)
and [backup and restore](runbooks/backup-restore.md).
