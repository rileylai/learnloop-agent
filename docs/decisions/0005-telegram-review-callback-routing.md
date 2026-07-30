# ADR-0005: Prioritize Typed Telegram Review Callback Routing

## Status

Accepted

## Date

2026-07-31

## Context

Telegram inline buttons use opaque `ll:<token>` callback data. The server-side
mapping previously exposed only a free-form action, and the gateway evaluated
the generic picker/session branch before explicitly separating review actions.
A restored or legacy Accept mapping could therefore produce the
“already ready for review” response without invoking the review orchestrator.

## Decision

- Persist `callback_kind=review|picker` with the callback mapping.
- Normalize old mappings without that field from the allowlisted action; reject
  unknown or mismatched mappings fail closed.
- Dispatch review actions before picker/session actions. Accept and Reject use
  `TelegramReviewOrchestrator`; Change target opens the review target picker.
- Inline Accept uses the existing pending-validation, append, durable identity,
  re-index, and status-transition path. The session presentation state does not
  replace the change request's durable pending check.
- Resolve normal review targets from the change request's indexed page. The
  canary page environment variable is reserved for canary/evaluation paths.
- Keep Telegram `update_id` idempotency as the outer retry boundary; no callback
  retry may repeat append or proposal creation.

## Consequences

Fresh and legacy review buttons share one deterministic dispatch path. Reject
callbacks need a fixed non-sensitive reason because Telegram's inline button
does not collect free text. The callback mapping remains opaque to Telegram and
contains no payload, source text, secrets, or raw image content.
