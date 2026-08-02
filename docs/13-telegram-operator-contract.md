# Telegram Operator Contract

## Purpose

This document defines the Step 89-92 contract for operating synchronization,
indexing, review, cost, workflow, readiness, and knowledge-base status from
Telegram. Steps 90-92 implement selected-page `/sync`, guarded
`/index-full`, read-only `/index-status`, `/cost`, and `/workflow`; the
remaining operator handlers are delivered by Steps 93-95.

## Scope and non-goals

The Telegram gateway is a transport boundary. It parses a bounded update,
checks the caller boundary, claims update idempotency, and delegates a typed
intent to an orchestrator. It does not call Notion, PostgreSQL, Redis, an LLM,
or a provider/tool adapter directly.

Steps 90-92 implement selected-page `/sync`, guarded full indexing, persisted
index status, bounded cost scopes, and redacted workflow queries. The pending
inbox, readiness/status, and stats remain unimplemented until their roadmap
steps. Existing ingestion, QA, and review behavior remains unchanged.

## Command registry

The command name is the first token after an optional `/`. Unknown commands,
unknown options, missing required values, and extra positional values fail with
bounded usage text. Telegram usernames and bot mentions are not used as page
or operator identifiers.

| Command | Syntax | Class | Confirmation | Data/work boundary | Queue |
|---|---|---|---|---|---|
| `/sync` | `/sync` | selected-page derived-index mutation | Final `sync_confirm` callback | Discover current accessible pages, then page-level replacement through the existing indexing flow | `telegram` queue when configured |
| `/index-full` | `/index-full` | full derived-index mutation | Required opaque `index_full_confirm` callback | Reuse `NotionFullIndexOrchestrator`; no direct route-to-Notion call | `telegram` queue when configured |
| `/index-status` | `/index-status [workflow_id]` | read-only | None | Read persisted indexing workflow state; never re-read Notion | Safe read may use the normal gateway path; queue compatibility remains unchanged |
| `/cost` | `/cost [today\|7d\|month\|workflow <workflow_id>]` | read-only | None | Reuse cost aggregation and preserve unknown pricing as `unknown` | Safe read may use the normal gateway path |
| `/pending` | `/pending` | read-only inbox | Per-action View/Accept/Reject/Change target callback | Read PostgreSQL pending rows only; only Accept enters the existing review workflow | List read is safe; callbacks use `telegram` queue when configured |
| `/workflow` | `/workflow [workflow_id]` | read-only | None | Reuse redacted workflow status/detail; never rerun or reconcile | Safe read may use the normal gateway path |
| `/status` | `/status` | read-only readiness | None | Reuse readiness service; distinguish liveness from readiness | Safe read may use the normal gateway path |
| `/stats` | `/stats` | read-only aggregate | None | Repository-backed aggregate page/block/chunk/vector/proposal counts and safe timestamps | Safe read may use the normal gateway path |

The existing `/start` alias continues to render `/help`. Updated help must
list the new commands and state that `/index-full` and `/sync` require button
confirmation, while `/pending` Accept is always an explicit human action.
Help must not suggest typing a Notion UUID, a callback token, or a raw workflow
payload.

### Command output contracts

All operator responses are bounded Telegram messages and may be split into
bounded pages without changing the underlying result. Safe fields may include:

- operation, status, workflow id, requested scope, aggregate counts, remaining
  work, and deterministic `failure_reason`;
- source display name, target display path, and full hierarchy display path
  where the relevant selection flow requires them;
- known estimated cost, budget state, or the literal `unknown` when pricing is
  unavailable;
- pending proposal title/summary preview, source display name, target path,
  and the existing review action state.

Operator output must never include callback tokens, page UUIDs as a required
input or UI payload, Redis keys, raw Notion blocks, OCR/source text, prompts,
embeddings, SQL, provider/tool exception bodies, API keys, bot tokens, bearer
values, webhook secrets, or private metadata. Numeric workflow ids may be
shown only as bounded references for `/index-status` and `/workflow`; they are
not executable rerun or reconciliation commands.

## Authorization and ownership

Authorization is deterministic and occurs before an operator workflow starts:

1. If `TELEGRAM_WEBHOOK_SECRET` is configured, the webhook secret must match.
2. If `TELEGRAM_ALLOWED_CHAT_IDS` is configured, the update chat id must be in
   that allowlist.
3. The actor identity is `message.from.id`, or `callback_query.from.id` for a
   callback. Every callback mapping is owned by the exact `(chat_id, user_id)`
   pair that created it. A callback from the right chat but a different user
   fails closed.
4. A callback cannot broaden the authority of the original command. The
   server-side mapping determines its action, scope, target selection, and
   expiry; user text cannot replace those fields.

The current MVP has a global chat allowlist and chat/user-scoped callback
ownership. A separate global user allowlist is not inferred from a username or
display name. Adding one later must be an explicit settings/API contract
change, not an LLM or Telegram UI decision.

Rejected secret/chat authorization does not create a workflow run, enqueue a
job, acknowledge a callback, or send a Telegram reply. Authorization failures
use the existing redacted `TELEGRAM_WEBHOOK_FORBIDDEN` or
`TELEGRAM_CHAT_NOT_ALLOWED` response contracts.

## Typed callback contract

Telegram carries only `ll:<opaque_token>`. The token is a short-lived lookup
key, not a serialized command. Redis/session storage resolves it to a typed
server-side mapping after ownership and TTL checks.

The server-side `callback_kind` is one of:

| Kind | Actions | Allowed responsibility |
|---|---|---|
| `picker` | Existing `open_page`, `select_target`, `back`, `root`, and legacy compatibility actions | Upload or review target hierarchy only; navigation is side-effect free |
| `review` | Existing `accept`, `reject`, `change_target` | Existing proposal review orchestrator; only explicit Accept can append and re-index |
| `operator` | `sync_toggle`, `sync_confirm`, `sync_cancel`, `index_full_confirm`, `index_full_cancel` | Steps 90-91 selection/confirmation; Step 92 adds read-only cost/workflow commands without new callbacks |

Operator mappings may retain server-side page ids, workflow ids, proposal ids,
selection sets, chat/user ownership, creation time, expiry, and a one-shot
claim state. None of those values may be encoded into callback data, displayed
as a token, or written to logs. The mapping action and fields must be
allowlisted; unknown kind/action combinations fail closed with
`INVALID_CALLBACK`.

Callback processing rules:

- Validate the `ll:` envelope, mapping, kind/action pair, ownership, expiry,
  and expected state before business work.
- Atomically claim one-shot confirmation and mutation actions before starting
  work. An already claimed or expired action returns a deterministic safe
  replay/expiry result and does not repeat work.
- A valid callback is acknowledged through `ToolRegistry` before long work.
  `TELEGRAM_CALLBACK_ACK_FAILED` describes acknowledgement delivery only; it
  does not authorize a second business execution.
- Review callbacks dispatch through the existing review family. Operator
  callbacks must never fall through to upload picker or review session logic.
- Duplicate Telegram `update_id` delivery replays the ledger outcome and never
  repeats sync, indexing, review, provider, or Notion work.

## Confirmation and mutation rules

The following actions are explicit user intent and cannot be replaced by text
commands with guessed ids or by an LLM response:

- `/sync` displays a bounded live hierarchy selection. Each selected page is
  kept in server-side session state; the final `sync_confirm` callback is
  required before any page re-index begins. Selection is bounded, and the
  callback claim plus Telegram update ledger prevent duplicate work.
- `/index-full` first displays a duration/embedding-cost warning. The full
  index starts only after an unexpired, owner-bound `index_full_confirm`
  callback. Cancel is side-effect free. Unknown embedding pricing remains
  unknown; it never becomes a guessed estimate. `/index-status` reads the
  persisted workflow and cannot trigger discovery or indexing.
- `/pending` View is read-only. Accept, Reject, and Change target callbacks
  remain explicit review actions. Accept delegates to
  `SupplementReviewOrchestrator` and preserves
  `Change Request -> Human Accept -> Append to AI Supplement Zone -> durable
  identity verification -> synchronous page re-index`. Pending and rejected
  content remains outside production RAG.

`/index-status`, `/cost`, `/workflow`, `/status`, and `/stats` are read-only.
They do not expose direct rerun, reconcile, append, target-change, or SQL
mutation controls. `/workflow` is a status/detail surface, not a replacement
for the protected stale-workflow reconciliation API.

## Queue and route boundary

The route performs only request-schema validation, webhook trust validation,
gateway construction, update-ledger claim/enqueue, and response mapping. The
gateway parses the command/callback into a typed intent and delegates to an
operator orchestrator. Orchestrators call services, repositories, tools, and
`QueueClient` interfaces according to the existing architecture.

When `REDIS_URL` is configured, the route claims the update ledger and queues
one serializable Telegram envelope on the `telegram` queue before operator
business work. The worker reconstructs the orchestrator and performs the
workflow. Without Redis, the existing synchronous compatibility path remains
available for local/test operation; this does not permit routes to call
Notion, PostgreSQL, Redis, or provider clients directly.

Operator work must use these boundaries:

- `/sync` and `/index-full`: operator orchestrator -> indexing orchestrator ->
  Notion reader/embedding client/repositories; no Notion write.
- `/index-status` and `/workflow`: workflow service/repository; no Notion read,
  provider call, or direct rerun.
- `/cost`: workflow observability/cost service; unknown pricing is preserved.
- `/pending`: proposal repository/service for reads; existing review
  orchestrator for explicit mutations.
- `/status`: readiness service and its `QueueClient`/database probes.
- `/stats`: aggregate repository/service only.

Redis callback/session state is ephemeral coordination state. PostgreSQL
workflow, update-ledger, proposal, and index state remains the durable source
for operator status. No raw PostgreSQL or Redis client is an LLM-facing tool.

## Steps 90-92 implementation invariants

- Live page discovery goes through the read-only Notion tool and can discover
  pages that are not yet in the local derived index.
- Display paths contain titles only; page ids stay in server-side mappings and
  the selected-page session.
- Each confirmed page reuses page-level replacement/indexing. Earlier page
  commits remain durable when a later page fails.
- The Telegram outer workflow reports only bounded sync status/count fields;
  original Notion notes and `AI Supplement Zone` are never written.
- Full-index confirmation is represented by an expiring, owner-bound session;
  only the one-shot confirm callback starts `NotionFullIndexOrchestrator`.
- `/index-status` exposes bounded persisted workflow fields and never calls
  the Notion reader or indexing orchestrator.
- `/cost` accepts only `today`, rolling `7d`, calendar `month`, and
  `workflow <workflow_id>` scopes. It separates recorded LLM/proposal/QA and
  embedding/indexing costs where metadata supports them; unknown pricing stays
  `unknown` and no token-based estimate is invented.
- `/workflow` without an id returns at most five recent workflow summaries;
  with an id it returns one fixed-field redacted detail. It never reruns or
  reconciles work and never forwards prompts, OCR/source text, secrets, raw
  exceptions, page ids, or private metadata.

## Step 89 acceptance invariants

- Every new command has one documented syntax, read/mutation class, safe output
  set, and queue boundary.
- Every mutation has an explicit confirmation/acceptance rule and an
  idempotency owner.
- Callback data is opaque, typed server-side, TTL-bound, owner-bound, and
  allowlisted.
- Authorization, confirmation, write safety, RAG exclusion, and state
  transitions remain deterministic backend policy.
- This contract does not implement the remaining Steps 93-94 or imply live
  cost, review-inbox, readiness, or stats verification.
