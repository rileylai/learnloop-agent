# ADR-0007: Dedicated Queue Contract for Telegram Full Indexing

## Status

Accepted for the 97.x reliability follow-up.

## Context

RQ 2.8.0 applies an implicit 180-second job timeout when a queue job does not
specify one. A production `/index-full` run spent about 317 seconds reading
its first large Notion page, so the generic Telegram webhook job was terminated
before page indexing could complete. RQ's `JobTimeoutException` inherits from
`Exception`, and the Notion adapter's broad catch consequently misclassified
the timeout as `NOTION_BLOCK_FETCH_FAILED`.

## Decision

`QueueClient.enqueue()` and `enqueue_in()` expose an optional,
backend-agnostic `timeout_seconds` field. RQ translates it to `job_timeout` and
constructs queues with an explicit bounded fallback of 180 seconds. Application
call sites pass ordinary Telegram and dedicated indexing bounds explicitly:

- `TELEGRAM_JOB_TIMEOUT_SECONDS`, default `180`;
- `TELEGRAM_INDEXING_JOB_TIMEOUT_SECONDS`, default `10800`.

The second value is a configurable deployment safety bound, not a latency SLA.
No global long queue default is used. Existing retry policies remain unchanged.

With Redis, the generic Telegram worker claims the confirmation and creates the
durable full-index workflow, then enqueues the module-level dedicated job with
the existing workflow id. The dedicated job has no automatic RQ retry and
reuses `NotionFullIndexOrchestrator`. Without Redis, the synchronous
compatibility path remains unchanged.

The RQ-specific timeout is translated at the queue/composition boundary into
the neutral `InfrastructureExecutionTimeout`. Notion and indexing layers do
not import RQ. Known Notion transport failures retain their existing retry and
failure mapping. Neutral infrastructure timeout propagates through the tool
and page-index boundaries; the full-index workflow records the safe,
content-free `QUEUE_JOB_TIMEOUT` reason before re-raising.

## Consequences

- Ordinary Telegram work remains bounded and does not inherit a long timeout.
- Full-index progress is durable and queried through `/index-status`.
- A timeout is no longer reported as a Notion transport failure.
- The large-page sequential-read performance issue remains; bounded concurrency,
  rate-limit safety, pagination safety, and request-duration observability are
  a separate follow-up.
- No live full-index or worker replay is implied by this ADR.
