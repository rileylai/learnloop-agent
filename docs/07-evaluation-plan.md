# 07 Evaluation Plan

## Purpose
This document defines retrieval hit rate, citation accuracy, write safety, and sync reconciliation tests.

## Status
Active for evaluation and regression steps.

## Golden Question Set

The versioned golden question set is stored at:

`tests/evals/golden_questions.yaml`

It contains synthetic examples only. It must not contain private Notion content.

Step 36 starts with three required categories:

| Category | Purpose |
|---|---|
| `nlp` | Verify retrieval and citation for existing manual notes. |
| `iso_9001` | Verify a second knowledge domain and path shape. |
| `ai_supplement_zone` | Verify accepted AI supplement content can be retrieved from production RAG. |

Each question records:

- a stable unique id and query
- deterministic page, section, source-kind, and top-k scope
- expected Notion paths
- expected content state: `manual_note` or `accepted_ai_supplement`
- answer terms that must or must not appear
- deterministic retrieval, citation, and production-RAG exclusion checks

Accepted AI supplement expected paths must be under `AI Supplement Zone`.
Manual note expected paths must not be under `AI Supplement Zone`.
Pending and rejected change request content must never be an expected production result.

## Loading and Validation

`tests/evals/golden_questions.py` loads YAML with `yaml.safe_load` and validates
the complete structure before an eval can run. It rejects unknown fields,
duplicate ids, invalid scopes, and ownership-model path mismatches.

Run the standalone validation command:

```bash
uv run python tests/evals/golden_questions.py
```

## Planned Deterministic Metrics

- Retrieval hit rate: expected path appears in top-k retrieved paths.
- Citation accuracy: returned citation path matches an expected source path.
- Write safety: original blocks stay unchanged and append occurs only under
  `AI Supplement Zone`.
- Manual sync reconciliation: deleted Notion content is removed after
  page-level replacement sync.
- Production-RAG exclusion: pending and rejected content is absent.

No LLM-as-judge is used in MVP evaluation.
