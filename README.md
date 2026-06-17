# LearnLoop Agent

LearnLoop Agent is a local-first Notion knowledge agent that turns learning materials into reviewed AI supplements and answers questions using RAG over existing Notion notes.

## 1. What problem this solves

Students and self-learners often collect materials in many places, but notes become fragmented and hard to query.
LearnLoop Agent helps convert new materials into structured, reviewable supplements while protecting existing notes.

## 2. Core idea

- Read existing Notion notes as knowledge.
- Ingest new learning sources.
- Generate AI supplement proposals.
- Require human review.
- Append accepted content to `AI Supplement Zone` only.
- Answer questions with RAG and Notion path citation.

## 3. MVP features

- Telegram-first ingestion.
- PDF, URL, YouTube transcript, screenshot OCR, chat text ingestion.
- Full indexing and page re-indexing.
- Manual incremental sync for manual Notion edits.
- AI supplement proposal + human accept/reject flow.
- Append-only writes to `AI Supplement Zone`.
- Auto page re-index after accepted append.
- RAG QA with citation.

## 4. Safety model

- Existing Notion content is read-only for direct agent editing.
- No direct overwrite.
- Pending/rejected proposals are excluded from production RAG.
- All writes follow: `Change Request -> Human Accept -> Append to AI Supplement Zone`.

## 5. Notion ownership model

- Existing notes are read-only for direct agent editing.
- Manual-created notes are read-only for direct agent editing.
- Old AI supplement blocks are read-only for direct agent editing.
- User manual merge/delete actions are valid.
- Notion is the source of truth.

## 6. AI Supplement Zone layout

```text
Original page/toggle/section
└── AI Supplement Zone
    └── YYYY-MM-DD
        └── Topic title
            - Source: ...
            - Summary: ...
            - Key Concepts: ...
            - Notes: ...
```

## 7. Architecture overview

High-level flow:
`API Route -> Orchestrator -> Service/Tool -> Repository -> External System`

## 8. Tech stack

- Python + FastAPI (implementation starts in later steps)
- PostgreSQL + pgvector
- Redis + RQ via QueueClient interface
- OpenAI provider interface
- Official Notion API
- Local-first Docker Compose runtime

## 9. Current status

This project is in repository foundation stage and is not ready for production yet.
Backend logic is not implemented in this step.

## 10. Local runtime model

- MVP is local-only.
- The service works only when the local app/service is running.
- Always-on cloud deployment is not part of MVP.

## 11. Planned roadmap

- V1: local-first MVP with safe review and append workflow.
- V2: cloud deployment and always-on operation.

## 12. Repository structure

```text
AGENTS.md
README.md
DAILY_LOG.md
docs/
src/
tests/
mock_data/
observability/
```

## 13. Documentation map

- `docs/00-design-doc.md`
- `docs/01-architecture.md`
- `docs/02-workflows.md`
- `docs/03-guardrails.md`
- `docs/04-memory-design.md`
- `docs/05-rag-design.md`
- `docs/06-notion-permission-model.md`
- `docs/07-evaluation-plan.md`
- `docs/08-observability.md`
- `docs/09-api-contract.md`
- `docs/10-deployment.md`
- `docs/11-coding-style.md`

## 14. License

License will be added in a later step.
