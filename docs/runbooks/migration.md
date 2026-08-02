# Migration Runbook

## Migration policy

Alembic is the only supported schema migration path. A migration must be
applied to a disposable restore or staging database before the active local
database. Migrations must not be hidden in application startup.

The current Alembic head is `9c5e7b1a2d4f`. This revision adds the
nullable/indexed canonical `notion_pages.parent_notion_page_id` used by the
deterministic Telegram page hierarchy. It preserves the unique
`notion_page_id` identity and does not infer parentage from titles or paths.

Before applying a migration:

1. Confirm the current database target and stop API/worker writes if the
   database is shared by a running local stack.
2. Take a backup using [the backup and restore runbook](backup-restore.md).
3. Run the PostgreSQL restore drill when the migration changes data shape,
   indexes, extensions, or vector columns.
4. Inspect the migration with `uv run --no-env-file --frozen alembic history`
   and record the current revision with
   `uv run --no-env-file --frozen alembic current`.

## Apply and verify

Use the restored or explicitly selected database URL in the process
environment. The command reads `DATABASE_URL`; it does not load `.env`.

```bash
uv run --no-env-file --frozen alembic upgrade head
uv run --no-env-file --frozen alembic current
```

Then run the application preflight and readiness checks:

```bash
uv run --no-env-file --frozen python scripts/preflight.py --profile api --json
curl --fail-with-body http://127.0.0.1:8000/ready
```

The readiness result must show current migrations, database connectivity, and
pgvector availability. Do not treat `/health` as migration evidence.

## Failure and rollback

- If an upgrade fails before commit, preserve the redacted error code and
  restore evidence; do not repeatedly rerun an unknown partial operation.
- Do not use a blind `alembic downgrade` as an incident rollback for a live
  database. Restore the last verified backup into a new database instead.
- If the migration is known to be safe and a downgrade is explicitly required
  for local development, run it only against the disposable database and
  verify the resulting schema before deleting the database.
- After any restore or schema change, rebuild derived Notion page state before
  resuming accepted appends or other mutations.
