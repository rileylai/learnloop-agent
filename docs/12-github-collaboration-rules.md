# GitHub Collaboration Rules

## Branches and commits

Use a short topic branch under the repository's configured branch namespace.
Keep commits focused and describe the user-visible or maintenance outcome.
Do not commit `.env`, credentials, private Notion content, generated database
files, or temporary live reports.

## Pull requests

A pull request should explain:

- the behavior or documentation change;
- affected boundaries and safety implications;
- tests or documentation checks run;
- any explicitly unverified live dependency.

Keep API, workflow, guardrail, deployment, and operational documentation in
sync when behavior changes. Record a durable architectural choice as an ADR in
[`decisions/`](decisions/).

## Review expectations

Reviewers should check current code alignment, authorization, append-only write
safety, production-RAG exclusion, idempotency, redaction, and recovery behavior.
Documentation reviews should also check internal links, commands, environment
variable names, and whether claims are supported by current code or tests.
