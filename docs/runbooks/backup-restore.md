# Backup and Restore Runbook

## Scope

This runbook covers local PostgreSQL/pgvector backups, disposable restore
verification, and the handoff back to the application. PostgreSQL is derived
application state; current Notion content remains the source of truth.

The drill implementation and deterministic tests are verified. A live
disposable restore drill has not been recorded in the current release evidence.

Never restore over the active database as a first test. Use a newly created
database name, verify it, and only switch the local `DATABASE_URL` after the
operator has reviewed the evidence.

## Safety rules

- Stop the API and worker before replacing an active database.
- Take a fresh backup before any restore or migration.
- Keep backup files outside Git and protect them with filesystem permissions.
- Do not put `DATABASE_URL`, `PGPASSWORD`, `NOTION_TOKEN`, or other secrets in
  command output, shell tracing, tickets, or committed files.
- Do not use `pg_restore --clean` against an active or unknown database.
- Do not manually edit or append Notion content during a database restore.
- After a restore, rebuild derived page state from current Notion content before
  resuming writes.

## Prerequisites

- `pg_dump`, `pg_restore`, and PostgreSQL client access.
- An administrator connection that can create and drop two uniquely named
  disposable databases.
- The locked project environment and the current Alembic migrations.
- A backup destination with sufficient space. Check the archive size and keep
  the archive until the restore verification is complete.

## Take a production-local backup

Use a password manager, `.pgpass`, or process environment for credentials. Do
not paste a credential-bearing URL into a shared terminal or log.

```bash
BACKUP_FILE="./data/backups/learnloop-YYYYMMDD-HHMMSS.dump"
mkdir -p ./data/backups
pg_dump \
  --format=custom \
  --no-owner \
  --file "$BACKUP_FILE" \
  --dbname "$POSTGRES_DATABASE_NAME"
pg_restore --list "$BACKUP_FILE" >/dev/null
```

The archive listing is a format check only; it is not evidence that the
application can start from the archive.

## Run the disposable restore drill

The project drill is dry-run by default. It creates two generated database
names, applies the real Alembic migrations, seeds a fixed sentinel, runs
`pg_dump`/`pg_restore`, verifies the sentinel and `alembic_version`, and drops
only the generated databases.

```bash
uv run --no-env-file --frozen python \
  scripts/postgres_restore_drill.py --json
```

For a live drill, provide an administrator URL that points to a disposable
local PostgreSQL server (normally the `postgres` maintenance database), then
explicitly confirm the target scope:

```bash
uv run --no-env-file --frozen python \
  scripts/postgres_restore_drill.py \
  --run \
  --confirm-disposable-target DISPOSABLE \
  --admin-database-url "$LEARNLOOP_RESTORE_DRILL_ADMIN_DATABASE_URL" \
  --json
```

The report contains fixed status and check names only. A failed live drill
does not expose driver errors or connection values. If cleanup fails, do not
reuse either generated database; remove them only after confirming their exact
names and that no application process is connected.

## Restore an application database

1. Stop the API and worker. Record the last known workflow and migration
   status through the protected operator endpoints.
2. Take a fresh backup of the current database, even if the current state is
   suspected to be damaged.
3. Restore into a new empty database using the verified archive:

   ```bash
   createdb "$RESTORE_DATABASE_NAME"
   pg_restore \
     --exit-on-error \
     --no-owner \
     --dbname "$RESTORE_DATABASE_NAME" \
     "$BACKUP_FILE"
   uv run --no-env-file --frozen alembic upgrade head
   ```

   The migration command must use the restored database URL in the process
   environment. Never run it against an unspecified default by accident.
4. Verify `uv run --no-env-file --frozen alembic current`, database
   connectivity, pgvector, and `/ready` before switching application traffic.
5. Rebuild from Notion source of truth. A restored database may be incomplete,
   so use `POST /api/notion/index/full`; use
   `POST /api/notion/index/incremental` only when the affected page set is
   known and the restore is otherwise complete.
6. Verify a scoped QA citation, workflow status, and absence of pending or
   rejected content in production retrieval. Keep the original archive and
   restore evidence until the operator signs off.

## Completion evidence

Record only safe metadata:

- archive format check passed;
- disposable restore drill status and check names;
- restored Alembic revision;
- readiness status;
- indexed page/chunk counts and scoped citation count;
- operator and timestamp.

Do not record database URLs, passwords, Notion tokens, page content, or raw
backup contents.
