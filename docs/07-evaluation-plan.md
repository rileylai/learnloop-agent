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

## Retrieval Hit Rate Evaluation

`tests/evals/retrieval_eval.py` measures whether each golden question's expected
path appears in the top-k paths returned by `ProductionChunkRetriever`.

The MVP Step 37 script uses a synthetic in-memory SQLite fixture built from the
golden question set. This keeps the regression deterministic before public mock
Notion data exists. It still exercises the real repository and retriever path:

`Golden Questions -> Synthetic Notion chunks -> ChunkRepository -> ProductionChunkRetriever -> Hit-rate calculation`

Matching rules:

- Compare expected paths against retrieved top-k paths with exact string match.
- Count one hit per golden question when at least one expected path appears.
- Compute `hit_rate = hit_count / total_questions`.
- Keep retrieval scoped to `source_kind="notion"`.
- Exclude non-production source chunks from retrieved results.

Run:

```bash
uv run python tests/evals/retrieval_eval.py
```

Expected output includes:

```text
retrieval_hit_rate: 1.000 (3/3)
```

## Citation Accuracy Evaluation

`tests/evals/citation_accuracy_eval.py` measures whether deterministic QA
citation paths match the expected source paths in the golden question set.

The MVP Step 38 script uses the same synthetic in-memory SQLite fixture as the
retrieval hit-rate eval. It retrieves production-safe Notion chunks, converts
their `notion_path` values into unique citation paths, then compares those
paths to each golden question's expected paths.

Matching rules:

- Compare citation paths against expected paths with exact string match.
- Count one accurate citation result per golden question when at least one
  expected path appears in the citation paths.
- Compute `citation_accuracy = accurate_count / total_questions`.
- Default threshold is `1.0`.
- Keep citation sources scoped to `source_kind="notion"`.
- Do not inspect or judge generated answer text.

Run:

```bash
uv run python tests/evals/citation_accuracy_eval.py
```

Expected output includes:

```text
citation_accuracy: 1.000 (3/3)
threshold: 1.000
status: pass
```

## Write Safety Evaluation

`tests/evals/write_safety_eval.py` checks deterministic Notion write-safety
invariants using the in-memory Notion writer client. It does not call real
Notion.

Checks:

- Accepted append keeps original/manual blocks unchanged.
- The only write operation is `append_ai_supplement_zone`.
- The append target path stays under `AI Supplement Zone`.
- Retry with the same change request is idempotent and creates no duplicate
  supplement entry.
- Write-policy violations fail closed with `WRITE_POLICY_VIOLATION` and no
  append operation.

Run:

```bash
uv run python tests/evals/write_safety_eval.py
```

Expected output includes:

```text
write_safety: pass (4/4)
```
