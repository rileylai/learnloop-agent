# 04 Memory Design

## Purpose
This document defines working memory, archival memory, Notion source of truth, and sync model.

## Status
Draft

This document will be expanded in later steps.

What belongs here:
- Memory scopes and retention.
- Sync and reconciliation model.
- Derived state vs source-of-truth model.

## Notion Discovery and Full Index (Step 69)

- Notion remains the source of truth; PostgreSQL blocks and chunks are derived
  snapshots.
- Full indexing discovers accessible external Notion page ids through the
  read-only reader tool, then indexes each page with page-level replacement.
- Re-indexing a page removes stale derived blocks and chunks before storing the
  current page snapshot. It does not write, move, or delete Notion content.
- Manual incremental sync continues to accept external Notion page ids in
  `page_ids`; internal PostgreSQL ids are never sent to the Notion reader.
- Full-index workflow state is persisted in `workflow_runs` and is available
  through `/api/notion/index/status`. Status responses contain workflow
  metadata and identifiers, not page content.
