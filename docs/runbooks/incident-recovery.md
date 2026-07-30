# Incident Recovery Runbook

## First response

Pause API and worker mutations. Do not attempt a Notion write while the
database state, workflow outcome, or append identity is uncertain.

Capture only safe operator evidence:

- workflow id, type, status, and failure reason;
- migration revision and readiness checks;
- count/status from `/metrics` and protected operator endpoints;
- whether the affected Notion page was manually edited;
- whether the durable `change-request-<id>` identity is visible.

Never capture tokens, connection URLs, page contents, proposal text, or raw
external exception bodies.

## Choose the recovery path

Generate the deterministic checklist first:

```bash
uv run --no-env-file --frozen python \
  scripts/notion_db_recovery_drill.py \
  --database-restored \
  --json
```

Use the flags that describe the incident. The script is read-only and does not
contact PostgreSQL or Notion.

### PostgreSQL was restored

1. Verify the migration head and `/ready` against the restored target.
2. Treat the restored PostgreSQL state as derived state, not authoritative
   note content.
3. Run `POST /api/notion/index/full` to rebuild the database and vectors from
   current Notion content. Do not append during this rebuild.
4. Verify scoped QA citations and production-RAG exclusion before resuming.

### A user manually edited Notion

1. Read the current page from Notion; current Notion content wins.
2. Run `POST /api/notion/index/incremental` with the known affected page ids.
3. The index path must use page-level replacement, including block deletion and
   chunk replacement for the affected page.
4. If the affected page set is unknown, use the full index route after an
   operator review.

The agent must not repair divergence by editing, deleting, moving, or manually
appending Notion blocks.

### An append result is uncertain

1. Read the target page and search for the durable
   `change-request-<id>` identity. This is a read-only verification step.
2. If the identity exists, treat Notion as authoritative, run page-level
   incremental indexing, and reconcile the workflow only after the index
   succeeds.
3. If the identity is absent, keep the change request unresolved and retry only
   through the existing human accept flow after confirming the target and
   approval. Never manually append a substitute block.
4. If identity visibility is unavailable, stop. Do not guess whether the write
   happened and do not retry.

### A workflow is stale or audit reconciliation failed

1. Inspect the protected workflow detail and confirm the business outcome from
   the external evidence before changing the workflow status.
2. Use `scripts/reconcile_workflow.py` without `--apply` first.
3. Apply a terminal reconciliation only when the outcome is known and the
   failure reason is deterministic. This command never reruns business work.
4. If the business outcome is unknown, leave the workflow unresolved and
   escalate for human review.

## Resume criteria

Resume mutations only after all of these are true:

- migration and readiness checks pass;
- Notion-derived page state has been rebuilt or incrementally reconciled;
- the append identity, if relevant, has been resolved;
- scoped QA returns a current Notion citation;
- pending and rejected change requests remain excluded from production RAG;
- the operator has signed off the recovery evidence.

The project does not provide automatic incident remediation or an always-on
Notion sync in MVP.
