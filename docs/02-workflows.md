# 02 Workflows

## Purpose
This document defines indexing, ingestion, review, append, sync, and QA workflows.

## Status
Draft

## Current Verification Boundary

The workflows below define implemented orchestration contracts, but most
external boundaries are currently verified with fake or in-memory adapters.
The runtime selects mock/in-memory Notion clients by default, or the live
reader and append-only writer adapters when `NOTION_BACKEND=live` and
`NOTION_TOKEN` are configured. Telegram long work is queued through
`QueueClient`/RQ when `REDIS_URL` is configured; live Telegram delivery and
worker execution remain opt-in.

The deterministic write policy, state-transition, transaction, RAG-exclusion,
and retry rules remain mandatory when live adapters are added.

Worker import boundary (Step 88):
- API enqueue and the worker share the canonical module-level callable
  `src.worker.telegram.process_telegram_webhook_job`.
- `scripts/run_worker.py` derives the repository root from `__file__`, so its
  import path does not depend on the launch cwd.
- Worker startup calls RQ `import_attribute()` for that path before Redis queue
  consumption. An unresolved path fails fast and does not process jobs.
- The worker-class policy selects RQ `SpawnWorker` on Darwin/macOS and the
  standard RQ `Worker` on Linux. The macOS fork-based worker is rejected by
  policy; this does not require `OBJC_DISABLE_INITIALIZE_FORK_SAFETY` and does
  not change the asynchronous queue boundary.
- `scripts/run_worker.py` calls `worker.work(with_scheduler=True)` and uses
  RQ's embedded scheduler for the selected queue. This is required for both
  `enqueue_at`/`enqueue_in` jobs and interval-based RQ retries; Redis being
  reachable by itself is not sufficient.

Prompt safety boundary (Step 80):
- Query, retrieved context, and source text are rendered as explicitly
  delimited untrusted data before entering an LLM request.
- Instructions embedded in source data cannot authorize a tool call, Notion
  write, target change, citation change, or bypass of human acceptance.
- Citation paths come from deterministic backend retrieval results, not from
  model output.
- For a selected indexed page, the backend derives the exact target
  `<canonical notion_path>/AI Supplement Zone`. The proposal validator only
  trims whitespace, removes duplicate slashes, and normalizes trailing slashes;
  it rejects a different page or a child target. The accept writer still
  derives the actual append path from the backend page and change request.

This document will be expanded in later steps.

## Reviewable Proposal Workflow (Step 72)

```text
GET /api/supplement/pending
-> Read pending change requests from PostgreSQL
-> Parse stored proposal content deterministically
-> Resolve stored target FK to the external Notion page id
-> Return proposal content, source citation fallback, and target metadata

GET /api/supplement/{change_request_id}
-> Read one change request and its target metadata
-> Return the same reviewable proposal detail
```

Rules:
- These read APIs do not call Notion and do not write to Notion.
- A proposal target supplied to `POST /api/supplement/propose` is an external
  Notion page id. The backend resolves it to the internal indexed page row
  before persistence; unknown targets fail closed with `NOTION_PAGE_NOT_FOUND`.
- Legacy proposals without explicit citation entries receive a deterministic
  source-document citation fallback for human review.
- Pending proposals remain pending until a separate human review action calls
  the existing accept/reject/edit-later flow.

What belongs here:
- Workflow state transitions.
- Success and failure paths.
- Retry and idempotency behavior.

## Supplement Proposal Workflow (Step 28)

```text
POST /api/supplement/propose
-> Validate request payload
-> Start workflow_run (workflow_type=supplement)
-> Load source document
-> Run duplicate check on production chunks
-> If duplicate: build citation-first proposal
-> Else: call ProviderRouter and validate proposal JSON
-> Create change request with status=pending
-> Mark workflow succeeded
```

Failure path:
- If provider output JSON is invalid, fail workflow with `LLM_OUTPUT_INVALID`.
- If a selected-page proposal target is missing `AI Supplement Zone`, points to
  another page, or is otherwise not the backend-derived exact target, fail with
  `LLM_OUTPUT_INVALID`.
- If source document is missing, fail workflow with deterministic error and workflow id.

State notes:
- New proposals are saved as `pending` change requests.
- Proposal generation does not write to Notion.
- Source prompt-injection text cannot change proposal target or write policy.
- When the workflow reaches the LLM path, workflow metadata records
  `provider_name`, `model`, `prompt_id`, `prompt_version`, and
  `prompt_safety_version`.

## Supplement Review Workflow (Step 29)

```text
POST /api/supplement/accept|reject|edit-later
-> Validate request payload
-> Start workflow_run (workflow_type=supplement)
-> Load change request
-> Enforce legal transition from pending state
-> Update change request status
-> Mark workflow succeeded
```

Legal transitions:
- `pending -> accepted`
- `pending -> rejected`
- `pending -> pending` (edit-later)

Rules:
- Reject stores decision reason in workflow metadata and keeps Notion unchanged.
- Review endpoints do not call Notion write adapters in Step 29.

## Safe Append Tooling Workflow (Step 30)

```text
NotionWriterTool (local tool adapter)
-> Validate append arguments (page_id/change_request_id/topic/source/summary/concepts/notes)
-> Build append target under AI Supplement Zone
-> Apply durable identity `change-request-<id>` per page/change request
-> Append the identity line plus fixed supplement content lines
-> Return append metadata (target path, block count, idempotent replay flag)
```

Rules:
- The tool exposes append-only behavior; there is no update or delete operation.
- The append target must stay under `AI Supplement Zone`.
- Existing page content stays unchanged; only new supplement entries are appended.
- The visible identity is the durable idempotency record; retry detection must
  not depend only on in-memory client state.
- The writer performs bounded read-after-write verification before returning
  append success. An unverified append fails closed for safe retry.

## Accept + Append + Re-index Workflow (Step 31)

```text
POST /api/supplement/accept
-> Validate request payload
-> Start workflow_run (workflow_type=supplement)
-> Load change request
-> Enforce legal transition from pending state
-> Validate accepted write preconditions (target page + proposal payload)
-> Append to AI Supplement Zone through NotionWriterTool
-> Verify append visibility by durable change-request identity
-> Prepare the page re-index snapshot outside the DB transaction
-> Open one business transaction
   - Reload and lock the change request with `SELECT ... FOR UPDATE`
   - Revalidate that status is still `pending`
   - Persist page/block/chunk replacement
   - Update change request status to `accepted`
-> Mark workflow succeeded
```

Failure path:
- If target page is missing, fail closed with `WRITE_POLICY_VIOLATION`.
- If append fails, append visibility cannot be verified, or re-index fails,
  mark workflow failed and keep change request `pending` for safe retry.
- A retry after a durable append reuses the existing Notion supplement and
  never creates a duplicate entry.

Rules:
- Accept path must follow `Change Request -> Human Accept -> Append to AI Supplement Zone`.
- Accepted status is committed only after append visibility is verified and
  the page re-index mutation set commits in the same business transaction.
- Concurrent accept attempts revalidate `pending` while holding the row lock;
  only one attempt may commit `accepted`.
- Reject and edit-later paths keep Step 29 behavior and do not call Notion write adapters.

## Workflow Audit Update Reconciliation (Step 64)

Final workflow audit updates are a separate boundary from business work:

```text
Business transaction commits
-> Attempt final workflow audit update
-> If audit update fails, keep workflow_run status=running
-> Emit WORKFLOW_AUDIT_UPDATE_FAILED
-> Reconcile the stale running workflow explicitly when the final outcome is known
```

Rules:
- A final audit update failure must not rollback or rerun committed business work.
- A final audit update failure must not be routed through the business failure
  handler or mark the workflow failed after business success.
- If business work fails first, the original business exception remains the
  surfaced error even when the failure-audit update also fails.
- `reconcile_stale_running_workflow()` only transitions a workflow currently in
  `running` to an explicitly supplied terminal status.

## Human-approved Notion Append Canary (Step 83)

```text
Explicit --live + --approve opt-in
-> Prepare one synthetic pending proposal in ephemeral SQLite
-> Run SupplementReviewOrchestrator.accept_change_request
-> Append through NotionWriterTool to AI Supplement Zone
-> Verify LearnLoop Change Request: change-request-<id>
-> Prepare and persist the target page re-index
-> Verify accepted DB state and scoped QA citation
```

Rules:
- The canary is an eval-only operator command and does not change the normal
  API review contract.
- Both flags are required; without them the canary sends zero Notion requests.
- The transport allowlist permits page/block reads and append-only block-child
  PATCH requests. Page updates, deletes, moves, and arbitrary POST requests are
  blocked.
- Derived DB state is ephemeral. Notion remains the source of truth, and the
  report is redacted to operation classes and numeric counts.
- A retry is safe because the writer's durable identity lookup detects the
  existing supplement before another append.

## Operator Observability and Reconciliation (Step 84)

```text
Workflow runs -> protected status service -> redacted status surface
Workflow runs -> metrics service -> Prometheus-compatible /metrics scrape
Stale running workflow -> dry-run CLI/API inspection
-> Explicit terminal resolution -> reconcile running workflow once
Recorded workflow metadata -> deterministic cost aggregation -> budget alert
```

Rules:
- Status and reconciliation routes are protected by the API bearer boundary;
  `/metrics` contains only fixed metric names, safe labels, and numeric values.
- Reconciliation accepts only `running` workflows older than the configured
  stale threshold and transitions them to `succeeded` or `failed` once.
- The reconciliation CLI is dry-run by default; `--apply` is required before
  it commits a terminal state. It never retries business work.
- Cost aggregation sums only recorded known cost fields. Unknown model pricing
  remains `unknown` and does not get guessed; configured budgets expose alert
  status without writing secrets or source content.

## Telegram Entrypoint Workflow (Step 32)

```text
POST /api/telegram/webhook
-> Validate webhook secret and allowed chat policy
-> Validate webhook payload
-> Start workflow_run (workflow_type=telegram)
-> Parse command from message text
-> Build deterministic reply text for /help or /health
-> Send reply through ToolRegistry -> TelegramBotTool
-> Mark workflow succeeded
```

Failure path:
- If Telegram bot token is not configured, fail with `TELEGRAM_NOT_CONFIGURED`.
- If Telegram API send fails, fail with `TELEGRAM_SEND_FAILED`.

Rules:
- API route calls orchestrator only.
- Route and orchestrator do not call Telegram API SDK/client directly.
- Bot gateway keeps no ingestion/QA/review business logic in Step 32.
- Secret and allowed-chat checks happen before a Telegram workflow starts; a
  rejected caller does not create a workflow run or send a reply.

## Telegram Update Idempotency Workflow (Step 75)

```text
POST /api/telegram/webhook with update_id
-> Validate webhook trust boundary
-> Atomically claim unique update_id in telegram_update_ledger
-> If running: return 202 processing response
-> If succeeded/failed: replay stored result or failure
-> If owner: run the Telegram gateway workflow once
-> Persist succeeded/failed outcome for future replay
```

Rules:
- The ledger claim is committed before ingestion, review, provider, or Telegram
  send work begins.
- A unique-constraint race has one owner; the other request never runs the
  command or sends a reply.
- A failed update is replayed as failed rather than automatically retried;
  recovery/reconciliation remains an explicit operator action.
- Updates without `update_id` retain the pre-Step-75 non-idempotent behavior.

## Telegram Background Queue Workflow (Step 77)

```text
POST /api/telegram/webhook
-> Validate webhook secret and allowed chat policy
-> Atomically claim unique update_id in telegram_update_ledger
-> Enqueue serializable payload in QueueClient -> RQ (`telegram` queue)
-> Return 202 with status=running and skipped_reason=QUEUED
-> Worker reconstructs the Telegram gateway and processes the claimed update
-> Persist succeeded/failed ledger outcome and workflow audit
```

Rules:
- The API route does not run ingestion, QA, review, file download, provider,
  or Telegram send work when the queue is configured.
- The Telegram job uses bounded RQ retries (`max_retries=2`, intervals of 5
  and 30 seconds). Expected domain failures are terminal ledger failures and
  are not retried by RQ; an unexpected worker crash can retry while the ledger
  is still `running`.
- A duplicate update returns the existing terminal replay or the existing
  `202` running response and does not enqueue a second job.
- If enqueue fails after the ledger claim, the ledger is marked `failed` with
  `TELEGRAM_QUEUE_UNAVAILABLE` so the failure is explicit and replayable.
- If `REDIS_URL` is absent, local/test compatibility uses the existing
  synchronous gateway path. Release readiness still requires Redis.
- A worker cannot silently fall back to synchronous handling after a queued
  request. Import-resolution failure is a startup blocker; the webhook/ledger
  queue contract remains unchanged.
- Existing scheduled jobs are retained when the worker is restarted. The
  embedded scheduler promotes due jobs; the Telegram update ledger and
  upload-session claims make old webhook retries and settle jobs safe to
  replay. Operators inspect them with the read-only queue inspector instead
  of deleting or cleaning a registry.

## API Mutation Idempotency Workflow (Step 76)

```text
POST /api/ingest/* or /api/supplement/* with Idempotency-Key
-> Canonicalize request payload and compute fingerprint
-> Atomically claim (method:path, Idempotency-Key) in api_idempotency_records
-> If running: return 202 processing response
-> If succeeded/failed: replay persisted response
-> If fingerprint differs: return 409 conflict
-> If owner: run the mutation once and persist its response
```

Rules:
- The claim is committed before source persistence, proposal generation, or
  review mutation work starts.
- JSON object key ordering does not change the fingerprint; multipart boundary
  values are normalized so equivalent uploads can be retried safely.
- Only safe response headers are replayed. Request payloads are represented by
  a digest in the ledger and are not logged as raw content.
- The middleware scope intentionally excludes Telegram, Notion indexing, QA,
  and GET routes. Telegram uses its `update_id` ledger.

## Telegram Ingestion Workflow (Step 33)

```text
POST /api/telegram/webhook
-> Parse /ingest command or media upload intent
-> Resolve optional `/ingest --page <external_page_id>` target
-> Download Telegram file bytes through ToolRegistry -> TelegramBotTool (download_file)
-> Route to ingestion orchestrator:
   - PDF document -> DocumentIngestionOrchestrator
   - screenshot batch -> ImageOCRIngestionOrchestrator
-> Create pending change request through SupplementProposeOrchestrator
-> Read stored proposal detail and send deterministic preview through
   ToolRegistry -> TelegramBotTool (send_message)
-> Mark workflow succeeded
```

Failure path:
- If Telegram file download fails, fail with `TELEGRAM_FILE_DOWNLOAD_FAILED`.
- If PDF/OCR parsing fails, reuse deterministic ingestion failures (`PDF_PARSE_FAILED`, `OCR_FAILED`).
- If proposal generation fails, reuse supplement proposal deterministic failures (`LLM_OUTPUT_INVALID`, `PROVIDER_NOT_FOUND`, `LLM_PROVIDER_ERROR`).

Rules:
- Route and gateway orchestrator still call Telegram only through `ToolRegistry`.
- PDF and screenshot ingestion reuse existing ingestion/propose orchestrators; no duplicate business logic in API route.
- Screenshot batch upload creates one `source_documents` row with `source_type=screenshot`.
- Step 33 still follows safe write policy: create `pending` change request only; no Notion append in this workflow.
- `/ingest --page <external_page_id>` resolves the target against indexed
  Notion pages; the target is optional for backward compatibility, but accept
  still fails closed when no target is present.
- In the primary target-picker flow, upload alone stores only a TTL session and
  does not create a proposal. A legacy direct caller may still create a
  targetless pending row, but it receives no Accept prompt and remains blocked
  by the existing target guardrail.

## Telegram Target-Picker Ingestion Workflow (Step 88 UX Redesign)

```text
Telegram message or caption with PDF/image
-> webhook secret + allowed-chat checks
-> update ledger claim
-> API returns 202 when Redis/RQ is configured
-> worker upserts a chat/user-scoped Redis upload session with TTL
   - media_group_id groups multiple image messages
   - attachment identity deduplicates Telegram retries
-> media group schedules one idempotent settle job; single media sends one receipt
-> settle job claims the picker and sends full hierarchy-path inline buttons
-> callback_data contains only `ll:<opaque_token>`
-> Redis resolves token by chat/user to the canonical external Notion page id/path
-> callback parser restores callback_kind/action from the server-side mapping
-> callback validates token ownership, session state, and selected page
-> answerCallbackQuery immediately; record callback_ack_status separately
-> review callbacks dispatch before generic picker/session callbacks
   - Accept/Reject -> TelegramReviewOrchestrator
   - Change target -> review target picker
-> atomic target claim starts existing PDF/OCR -> proposal orchestration
-> commit source document and pending change request
-> atomically claim preview delivery and send one preview with
   Accept / Reject / Change target buttons
-> finalize workflow run and update ledger
-> explicit Accept callback or `/accept` reuses TelegramReviewOrchestrator
```

Rules:
- Parent and child pages are separate button targets; hierarchy paths are UI
  labels, while the external Notion page id remains the canonical backend
  target.
- Full external page ids never appear in inline `callback_data`; opaque tokens
  are short-lived Redis mappings isolated by chat and user.
- Server-side callback mappings carry `callback_kind` (`review` or `picker`)
  and an explicit action. Legacy mappings without that field infer the kind
  from the allowlisted action, then fail closed for unknown actions.
- Review actions are dispatched before picker/session actions. The
  `ready_for_review`/`proposal_created` presentation state cannot intercept a
  valid Accept or Reject callback; Accept still validates the change request's
  durable `pending` status through `SupplementReviewOrchestrator`.
- Normal review targets come from the change request's indexed target page.
  `LEARNLOOP_NOTION_CANARY_PAGE_ID` is restricted to canary/evaluation code and
  is not a runtime fallback for a Telegram review.
- `/ingest` text/caption parsing remains a fallback. The primary flow is upload,
  page button selection, target-aware pending proposal, then explicit review.
- `answerCallbackQuery` is a Telegram UX side effect. After basic callback and
  session validation, its failure is recorded as
  `TELEGRAM_CALLBACK_ACK_FAILED` and does not own or rollback business work.
- Target claim, source/proposal commits, and preview delivery claims are
  separate boundaries. A valid callback runs business work at most once for
  the claimed session; an acknowledged callback may therefore have
  `callback_ack_status=failed` while the workflow still succeeds.
- Media-group settle and target claims are atomic/idempotent. A successful
  business commit creates exactly one source document and pending change
  request for the update/session. An unexpected RQ retry reuses the ledger or
  session claim and must not rerun OCR, proposal generation, or change-request
  creation.
- Upload sessions carry a monotonic settle version. The settle job atomically
  promotes `collecting` to `settled`, sorts attachments by Telegram
  `message_id`, and stale/duplicate versions skip before picker or business
  work. Duplicate `file_unique_id` values are ignored in the session store.
- Preview delivery is post-commit. A failed `send_message` records
  `TELEGRAM_PREVIEW_DELIVERY_FAILED`, preserves the pending change request, and
  emits a short recovery message. Recovery may resend the existing preview but
  never reruns ingestion or proposal generation.
- The settle job uses bounded queue retries for unexpected worker failures;
  expected domain errors are terminal and remain explicit.
- An expired session, missing media, invalid callback, or unavailable queue
  returns an explicit deterministic error. The bot never guesses another
  chat/user's upload or silently reports success.
- Invalid callback data is recorded as `INVALID_CALLBACK`; an expired or
  unusable upload session is recorded as `UPLOAD_SESSION_EXPIRED` or
  `UPLOAD_SESSION_INVALID`, never as `UNKNOWN_ERROR`.
- Invalid/expired callback state fails closed before callback acknowledgement
  and before any source or change-request row is created.
- No proposal without a target receives an Accept prompt. No callback or worker
  path auto-accepts; appending and re-indexing remain behind the existing
  human review guardrails.

Outcome metadata uses only safe state fields: `business_status`,
`callback_ack_status`, `callback_ack_failure_reason`, and
`preview_delivery_status`. It never stores callback payloads, upload bytes,
OCR text, proposal source text, or secrets. A committed but undelivered outcome
is inspected and reconciled with
`scripts/reconcile_telegram_outcome.py`, which is dry-run by default and uses
repositories plus one explicit preview resend/reconcile transaction; it does
not use ad-hoc SQL.

## Telegram Page and Review Workflow (Step 73)

```text
POST /api/telegram/webhook with `/pages`
-> Read indexed Notion page ids through NotionPageRepository
-> Send deterministic page list and target-aware usage

POST /api/telegram/webhook with `/ingest --page <page_id>` and media
-> Create pending proposal for the selected external target
-> Send proposal preview with summary, notes, citations, and review commands

POST /api/telegram/webhook with `/accept <change_request_id>`
-> Reuse SupplementReviewOrchestrator
-> Append to AI Supplement Zone and immediately re-index
-> Send success reply only after the business workflow succeeds

POST /api/telegram/webhook with an inline Accept callback
-> Validate callback mapping and acknowledge Telegram
-> Delegate to TelegramReviewOrchestrator.accept_change_request()
-> Reuse the same pending validation -> append -> durable identity check
   -> page re-index -> accepted transition as the text command
-> Send success reply
```

Rules:
- `/pages` is read-only and does not contact the Notion writer.
- Preview content is read from the stored pending proposal; preview does not
  accept, append, or expose pending content to production RAG.
- Telegram chat id remains the deterministic reviewer identity.
- Inline Accept is an explicit user callback and delegates to the same
  `SupplementReviewOrchestrator` as `/accept`; it does not create a second
  write path.
- Inline Reject delegates to the same review orchestrator with a deterministic
  non-sensitive callback reason; it never calls a Notion writer.
- Inline Change target opens the picker and changes only the pending request's
  target. It does not run OCR, LLM proposal generation, or append work.
- Duplicate `update_id` callbacks replay the durable result and cannot append
  the same change request twice.

## Telegram QA Workflow (Step 34)

```text
POST /api/telegram/webhook
-> Parse /ask command and optional --page / --section scope flags
-> Delegate to TelegramQAOrchestrator
-> Reuse QAOrchestrator for production chunk retrieval and grounded answer generation
-> Format answer with deterministic Notion path citations
-> Send reply through ToolRegistry -> TelegramBotTool (send_message)
-> Mark workflow succeeded
```

Failure path:
- Invalid scope flags fail with `INVALID_ARGUMENT`.
- Missing providers and provider failures reuse QA workflow failures
  (`PROVIDER_NOT_FOUND`, `LLM_PROVIDER_ERROR`, `LLM_OUTPUT_INVALID`).
- The Telegram gateway workflow fails when delegated QA fails.

Rules:
- Scope syntax is
  `/ask [--page <page_id>] [--section <notion/path>] <question>`.
- `/ask` without a question returns a usage reply and does not start a QA workflow.
- Telegram QA reuses `QAOrchestrator`; the gateway contains no retrieval or provider logic.
- Production retrieval remains Notion-only and keeps pending/rejected proposals excluded.
- Telegram workflow metadata records citation count only, not question text or citation paths.
- The delegated QA workflow records `provider_name`, `model`, `prompt_id`, and
  `prompt_version` in its own workflow metadata.
- When the delegated LLM call returns token usage, the QA workflow metadata also
  records `token_input`, `token_output`, and `estimated_cost`.

## Telegram Review Workflow (Step 35)

```text
POST /api/telegram/webhook
-> Parse /accept or /reject command
-> Delegate to TelegramReviewOrchestrator
-> Reuse SupplementReviewOrchestrator
-> For accept:
   - validate pending state and write preconditions
   - append through NotionWriterTool to AI Supplement Zone
   - immediately re-index page
   - mark change request accepted
-> For reject:
   - mark pending change request rejected
   - perform no Notion write or re-index
-> Send deterministic result reply through ToolRegistry -> TelegramBotTool
-> Mark Telegram workflow succeeded
```

Failure path:
- Invalid change request ids fail with `INVALID_ARGUMENT`.
- Missing change requests and illegal transitions reuse review workflow failures
  (`CHANGE_REQUEST_NOT_FOUND`, `INVALID_STATE_TRANSITION`).
- Accept write-policy violations fail closed with `WRITE_POLICY_VIOLATION`;
  the change request stays `pending` and no Telegram success reply is sent.

Rules:
- Command syntax is `/accept <change_request_id>` and
  `/reject <change_request_id> <reason>`.
- Telegram chat id is recorded as the deterministic reviewer identity.
- Telegram review reuses `SupplementReviewOrchestrator`; the gateway contains
  no state-transition or Notion write logic.
- Accept follows `Change Request -> Human Accept -> Append to AI Supplement Zone`
  and replies only after immediate page re-index succeeds.
- Reject never calls Notion writer or page re-index.
- Telegram gateway metadata records review action/status/workflow id only, not
  the reject reason.
- Inline review buttons remain deferred.

## Same-page Snapshot Safety (Step 62)

- The reader includes the Notion page `last_edited_time` in every page snapshot
  when the source provides it.
- Page persistence takes a PostgreSQL transaction-scoped advisory lock keyed by
  the stable Notion page id before checking the stored snapshot.
- A prepared snapshot with an older non-NULL `last_edited_time` fails with
  `STALE_PAGE_SNAPSHOT` before blocks or chunks are replaced.
- Legacy rows with a NULL timestamp accept the first timestamped snapshot;
  timestamp-less legacy readers do not erase an existing timestamp.
- SQLite test backends skip the PostgreSQL-only advisory lock but exercise the
  same deterministic stale-snapshot comparison.

## Step 85 Recovery Workflow

Recovery is an operator workflow, not an automatic background repair:

```text
Pause mutations
-> Inspect redacted workflow/readiness/migration evidence
-> If PostgreSQL was restored: verify migration head
-> Rebuild derived state from current Notion content
   (full index after restore, page-level incremental sync for known edits)
-> If an append is uncertain: read durable change-request identity
-> Re-index before workflow reconciliation or any retry
-> Run scoped QA and resume only after operator sign-off
```

Rules:

- Notion remains the source of truth for page and block content.
- A restored PostgreSQL database is treated as derived state and must not
  authorize a direct Notion edit, delete, move, or manual append.
- A visible `change-request-<id>` identity means the Notion append is
  authoritative; verify it, page-re-index it, then reconcile the workflow.
- An absent identity keeps the change request unresolved; retry only through
  the existing human accept flow after target and approval checks.
- An unverified identity stops recovery. The agent must not guess or duplicate
  an append.
- `pending` and `rejected` change requests remain excluded from production RAG.

The read-only checklist generator is
`scripts/notion_db_recovery_drill.py`; the database lifecycle drill is
`scripts/postgres_restore_drill.py`. Detailed operator commands are in
`docs/runbooks/`.
