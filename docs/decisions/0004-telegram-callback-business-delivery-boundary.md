# ADR-0004: Separate Telegram Callback Acknowledgement from Business Delivery

## Status

Accepted

## Date

2026-07-30

## Context

Step 88 originally acknowledged a Telegram page-picker callback after OCR,
proposal generation, and preview delivery. A transient acknowledgement error
therefore raised `TELEGRAM_SEND_FAILED` after the source document and pending
change request had already committed. The workflow and update ledger became
failed even though the business outcome was successful, and a retry could be
ambiguous.

## Decision

- Validate callback token ownership, session state, and selected page first.
- Call `answerCallbackQuery` immediately before OCR, provider, or proposal
  work. Record `callback_ack_status` and classify transport failure as
  `TELEGRAM_CALLBACK_ACK_FAILED`.
- Treat callback acknowledgement as a Telegram UX side effect. It never owns,
  rolls back, or determines the source-document/change-request transaction.
- Commit the source document and pending change request before preview delivery.
- Track preview delivery separately. A failed preview send uses
  `TELEGRAM_PREVIEW_DELIVERY_FAILED`, retains the pending change request, and
  may be recovered by resending the existing preview only.
- Keep `telegram_update_ledger.update_id` and the upload-session target claim as
  the idempotency boundaries. Duplicate updates and unexpected RQ retries must
  not repeat OCR, LLM generation, or business-row creation.
- Store only safe workflow metadata; never store Telegram payloads, callback
  tokens, image/OCR text, proposal source content, or secrets.

## Consequences

Successful business work can have a failed callback acknowledgement while the
workflow and ledger remain succeeded. Preview delivery can be failed and
recoverable without changing the pending proposal. Operators use
`scripts/reconcile_telegram_outcome.py` in dry-run mode first; it verifies the
existing rows and does not use ad-hoc SQL or rerun business work.
