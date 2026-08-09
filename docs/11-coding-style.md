# Coding Style

## Python

- Use Python with type hints and small, explicit functions.
- Use FastAPI for HTTP routes and Pydantic for request/response schemas.
- Keep business logic out of routes.
- Keep provider, Notion, Telegram, parser, PostgreSQL, Redis, and RQ clients
  behind their documented interfaces.
- Prefer deterministic backend validation to LLM decisions.
- Add comments only for purpose or non-obvious constraints.
- Use clear `error_code` and `failure_reason` values.

## Tests

Tests should use injected clients, fakes, fixtures, or isolated databases for
the default suite. Cover both success and fail-closed behavior, including
idempotency, concurrency, redaction, and production-RAG eligibility.

Live dependency tests must be explicit, bounded, redacted, and safe to repeat.
They must never silently send Telegram messages, write to arbitrary Notion
pages, or mutate a shared database.

## Documentation

Use simple English, short sections, tables, and links to the canonical
document for each concept. Document current behavior and durable design
rationale; do not add temporary verification output or development chronology.
Keep the product label `AI Supplement Zone` unchanged.
