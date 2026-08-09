# Memory and Synchronization

## Memory layers

LearnLoop separates authoritative content, derived knowledge, and workflow
coordination state.

| Layer | Stored state | Authority |
| --- | --- | --- |
| Notion | Pages, blocks, manual edits, and accepted supplement blocks | Source of truth |
| PostgreSQL snapshot | Notion page/block rows, chunks, vectors, sources, proposals, and workflows | Rebuildable derived state |
| Redis | Telegram queue, upload sessions, callback mappings, and short-lived operator sessions | Ephemeral coordination |

The application database is not a second authoring system. It records the
current indexed snapshot and business decisions needed to make workflows
recoverable.

## Proposal state

Source documents are normalized snapshots with a content hash. Proposals are
stored as change requests:

```text
source document -> pending change request
pending -> accepted | rejected
pending -> pending (edit later)
```

Pending and rejected content is review state, not production knowledge. An
accepted change request is considered production-ready only after its Notion
append is verified and the target page has been re-indexed.

## Derived index state

For each page, the index stores a current page/block snapshot and ordered
chunks with citation metadata. Re-indexing replaces all derived rows for that
page after the new snapshot and complete embeddings have been prepared.

This prevents partial page state when reading, parsing, embedding, or response
validation fails. A full index may contain a partial workspace result because
each successfully completed page is committed independently.

## Reconciliation

Manual Notion changes are reconciled explicitly:

```text
User changes Notion
  -> call full or page-scoped incremental sync
  -> read current Notion page
  -> replace affected derived page state
  -> production retrieval sees only the current snapshot
```

There is no background Notion watcher in the MVP. If the affected page set is
unknown, use a full index after reviewing the operational impact.

Accepted agent appends use the same page indexer immediately after the writer
verifies the durable change-request identity. This keeps the Notion write path
and retrieval path aligned without allowing the database to outrank Notion.

## Recovery boundaries

If PostgreSQL is restored, rebuild derived state from current Notion before
resuming accepted appends. If an append result is uncertain, inspect its
`change-request-<id>` identity in Notion before retrying. If identity visibility
is unavailable, stop rather than guessing.

See [incident recovery](runbooks/incident-recovery.md) and [backup and restore](runbooks/backup-restore.md).
