# Parser & Note Completeness — Current Roadmap

This file is the authoritative current-state and sequencing document for the
Parser & Note Completeness initiative. It records repository evidence and
review gates; it does not grant formal benchmark authority and it does not
replace the independent-review bundle.

## Current Pointer

**As of 2026-09-04**

- **Where we are:** The project-owned 13-case synthetic conformance /
  diagnostic benchmark is technically wired end to end at the current
  owner-primary boundary. Corrected successor fixtures and references,
  owner-primary Gold, raw Parser measurements, diagnostic replay machinery,
  and the minimal formal/no-egress contracts are present.
- **Authority state:** `owner-primary complete`; `independent review pending`;
  `formal_authority=false`; **no formal baseline exists**.
- **CURRENT NEXT STEP:** Complete independent human review and produce
  genuine no-egress execution evidence for a reproducible/content-addressed
  benchmark image. The no-egress and formal-governance evidence also require
  independent review.
- **Why this is not formal:** Technical wiring and owner decisions are not
  independent evidence. The benchmark image is not yet reproducibly
  content-addressed, genuine no-egress execution has not been evidenced, the
  13-case current baseline has not been formally executed, and the relevant
  governance has not received independent review.
- **LATER:** After those gates close, execute the formal synthetic 13-case
  baseline while retaining this synthetic set.
- **AFTER THAT:** Consider the deferred human-curated representative
  benchmark as a supplement to the synthetic conformance set.
- **ONLY AFTER BASELINES/CALIBRATION:** Consider parser/generation candidate
  experiments and comparisons.
- **Hard stop:** Do not modify the production parser, run a parser candidate
  shootout, tune prompts, set quality thresholds, compare candidates, or
  modify retrieval / Step 100 at this checkpoint.

## Benchmark positioning

The current 13-case benchmark is a **project-owned synthetic conformance /
diagnostic benchmark**. It is retained as a durable diagnostic and contract
calibration set. Future real-world cases must supplement this set; they must
not delete, replace, or silently redefine it.

The full diagnostic profile contains 13 logical cases:

| Source type | Cases | Role |
| --- | --- | --- |
| PDF | P01–P04 | Synthetic conformance / diagnostic coverage |
| Web | W01–W03 | Synthetic conformance / diagnostic coverage |
| YouTube transcript | Y01–Y02 | Synthetic conformance / diagnostic coverage |
| Chat | C01–C02 | Synthetic conformance / diagnostic coverage |
| Screenshot / image | S01–S02 | Synthetic conformance / diagnostic coverage |

The five-case smoke set (`P01`, `W01`, `Y01`, `C01`, `S01`) is a technical
smoke path only. It does not replace the full 13-case diagnostic profile and
it is not a formal baseline.

The current binding records are:

- Full diagnostic profile:
  `tests/evals/parser_note_completeness/v1/manifests/full/revision-003/profile.json`
  — SHA-256
  `45a00105debf8b452bdc18f045fe48a2e75fd2ebaeb94f20a71c1ca877187039`.
- Bound benchmark manifest:
  `tests/evals/parser_note_completeness/v1/manifests/benchmark/1.0.2/manifest.json`
  — SHA-256
  `bf6a50e131d6f2b922717f25efafb1452d2de8a94b5180a3af424cfa5693811f`.
- Owner-primary selection index:
  `tests/evals/parser_note_completeness/v1/governance/owner-primary/revision-001/manifest.json`
  — SHA-256
  `c7603013eb5db52fa265cdfb08854d73a2d280b09cee22a9ad72dd719b42468a`.

The owner-primary index binds the 13 selected records and 82 expected claims
for independent review. The complete source/reference/Gold path, revision,
SHA-256, claim, qualifier, category, importance, and locator inventory is in
the [Human Independent Review Bundle](07-independent-review-handoff.md).

## Authority state

| Area | Current state | Interpretation |
| --- | --- | --- |
| Selected source bytes and revisions | Complete at owner-primary boundary | The selected bytes, exact paths, revisions, and digests are bound for review. |
| Corrected references | Complete at owner-primary boundary | Successor references are selected and content-addressed; fidelity is still a human review question. |
| Fixture provenance, rights, and privacy | Owner decision complete | Project-owned synthetic provenance and no-private/personal-material decisions are recorded; independent review is pending. |
| Owner-primary Gold | Complete | All 13 cases have owner-primary Gold/annotation records; independent review is pending. |
| Parser raw measurements | Implemented | Raw, typed measurements and locators exist; no formal thresholds, weights, partial-credit policy, or global score is being authorized here. |
| Diagnostic execution | Implemented | Runner, history, receipt, store, replay, and diagnostic wiring exist; diagnostic replay is not formal baseline evidence. |
| Formal authority | **False** | No formal authority record has been established. |
| Formal baseline | **Absent** | No formal 13-case current baseline exists. |

The independent-review artifact is intentionally reviewer-facing and does not
require reading raw governance JSON or understanding Q1–Q29:

`dev_state/parser-note-completeness/07-independent-review-handoff.md`

## Completed work

The following work is complete according to the current repository evidence.
“Complete” below means technically or owner-boundary complete; it does not
mean independently reviewed or formally authoritative.

| Completed item | Current evidence / boundary |
| --- | --- |
| C01 vertical slice / implementation audit | C01 is the original vertical slice and its implementation/audit path is retained as the diagnostic reference case. |
| Five-case smoke technical wiring | The `P01/W01/Y01/C01/S01` smoke profile is wired for bounded diagnostic execution. |
| Full 13-case diagnostic technical wiring | The full profile is bound at `manifests/full/revision-003/profile.json`; all 13 cases are available for diagnostic execution/replay. |
| Corrected successor fixtures/references | Current selected revisions include corrected successors for `P02`, `P03`, `P04`, `W02`, `W03`, and `S02`; the exact matrix is in the independent-review bundle. |
| Owner provenance/privacy decisions | Owner decisions cover the selected project-owned synthetic sources, redistribution/provenance records, and absence of private/personal source material. |
| 13-case owner-primary Gold | The owner-primary selection index binds 13 cases and 82 expected claims, with case-specific Gold paths and revisions. |
| Parser raw-measurement contracts and implementation | Raw measurements and typed locators cover the current parser dimensions, including text/OCR, reading order, structure/table/formula/code, duplicate/noise, caption, chat identity, and applicable geometry/alignment facts. |
| Diagnostic runner/history/receipt/store/replay | The diagnostic execution path records run history/receipts and supports stored-result replay at the non-formal diagnostic boundary. |
| Minimal formal manifest/provenance/publication contract | Fail-closed manifest, provenance, run-identity, and publication-pointer contracts exist as a minimal formalization surface; they do not establish formal authority without the missing evidence gates. |
| Docker no-egress launcher contract | The launcher contract specifies read-only root, dropped capabilities, no-new-privileges, bounded mounts/tmpfs, `--network none`, inspection, and denied DNS/IP/HTTP probes; genuine execution evidence and independent governance review remain outstanding. |

Primary supporting documents:

- [Human Independent Review Bundle](07-independent-review-handoff.md)
- [Formal Baseline Readiness](04-formal-baseline-readiness.md)
- [Human Review Workbook](05-human-review-workbook.md)
- [Primary Gold Proposals](06-primary-gold-proposals.md)
- [Evaluation Plan](../../docs/07-evaluation-plan.md)
- [Benchmark contract decision](../../docs/decisions/0009-parser-note-completeness-benchmark-contract.md)

The implementation files are evidence for the completed contracts, not targets
for this roadmap synchronization. This roadmap update makes no implementation
change.

## Remaining synthetic formal-baseline blockers

The synthetic set cannot become a formal baseline until all of these blockers
close:

1. **Independent human review.** Review the frozen fixture bytes, references,
   owner-primary Gold, scorer-facing bindings, and applicable governance.
2. **Reproducible/content-addressed benchmark Docker image.** Pin the image
   identity and make the benchmark execution environment reproducible.
3. **Genuine no-egress execution evidence.** Execute the bounded launcher and
   retain evidence that network egress is actually unavailable, rather than
   relying only on launcher configuration.
4. **Independent review of no-egress/formal governance.** Review the image
   binding, launcher restrictions, probe evidence, provenance, run identity,
   and publication behavior independently of the owner decision.
5. **Formal 13-case current baseline execution.** Only after the preceding
   evidence is accepted, execute and preserve the immutable full 13-case
   baseline with its current manifest and run identity.

Until then, `formal_authority=false` and there is no formal baseline to use for
quality claims, threshold setting, candidate ranking, or production decisions.

## Sequencing

### CURRENT NEXT STEP

Complete **independent review + genuine no-egress evidence**. The reviewer
should use `07-independent-review-handoff.md` and the simple result template;
the reviewer must inspect the frozen source bytes, not just the bounded
excerpts. No owner-primary Gold is to be changed by this roadmap update.

### LATER

Complete the **formal synthetic baseline**: close the five blockers above,
then execute the current immutable 13-case profile and publish only the
resulting evidence-bound baseline if all formal gates pass.

### AFTER THAT

Develop the deferred **Human-curated representative benchmark** described
below. It is a separate, deliberately small set for real-world
representativeness and must use the same evaluation methodology after its
sources, references, and human-reviewed Gold are frozen.

### ONLY AFTER BASELINES/CALIBRATION

Consider parser/generation candidate experiments, candidate comparison, and
any quality calibration only after the synthetic formal baseline exists and
the calibration plan is independently agreed. These are not current work.

## Future milestone: Human-curated representative benchmark

**Status: DEFERRED. Do not start collection or implementation now.**

Purpose: supplement the current synthetic conformance set with a small amount
of genuine real-world representativeness. This milestone is not a replacement
for the retained 13-case synthetic benchmark.

In the future, the owner will manually select a small number of representative
cases from:

- PDF
- Web
- YouTube
- Screenshot / image
- optionally Chat

For each selected case, the future workflow is:

1. Freeze the exact source artifact.
2. Record provenance, rights, and privacy decisions.
3. Create the exact reference.
4. Create human-reviewed Gold.
5. Run the same evaluation methodology and keep the representative set
   separately identifiable from the synthetic conformance set.

No real-world source collection, fixture creation, reference creation, Gold
creation, or implementation work is authorized in this milestone yet.

## Hard stop at the current checkpoint

Do not:

- modify the production parser;
- run a parser candidate shootout;
- tune a prompt;
- set quality thresholds;
- perform candidate comparison; or
- modify retrieval / Step 100.

Also do not treat diagnostic results as a formal baseline, publish formal
authority, or begin candidate adoption from the current owner-primary state.

## Evidence interpretation for future work

When this initiative resumes, use the following order of interpretation:

1. This document for current status, blockers, sequencing, and stop conditions.
2. `07-independent-review-handoff.md` for the reviewer-facing 13-case bundle,
   including exact source/reference/Gold paths, SHA-256 values, expected claim
   counts, bounded excerpts, and locators.
3. The bound manifest/profile and owner-primary index for exact machine-facing
   selection records.
4. `04-formal-baseline-readiness.md` for the formal evidence checklist and
   remaining gate details.

If a future artifact conflicts with this pointer, resolve the conflict from
current repository evidence before changing authority status. Do not infer
formal status from an old milestone label or an owner-primary Gold file alone.
