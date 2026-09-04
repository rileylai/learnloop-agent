# Parser & Note Completeness Primary Gold Proposals

Status: non-authoritative proposal for human-owner decision. This file is not
Gold, does not satisfy Q25 independent review, and grants no scorer, formal-run,
baseline, threshold, comparison, or adoption authority.

## Shared annotation policy

- `source_references` cite the exact successor full-profile reference elements.
  Bilingual restatements and deliberate repeated occurrences support one
  canonical evidence item unless recurrence itself changes meaning.
- Every cited text-bearing element remains available to Parser coverage. A lack
  of an expected note claim does not silently remove it from Parser measurement.
- Each expected claim below has one `required` evidence relation unless the row
  explicitly names more. Headings normally provide structure/context rather
  than a separate claim.
- All cases assert exact element kind, section membership, canonical order, and
  typed locator identity for applicable cited elements. Lists, tables, figures,
  captions, code, cues, messages, threads, replies, images, and geometry also
  retain their applicable source-faithful structure assertions.
- The proposal uses only the frozen Q7 category, importance, and impact-reason
  enums. No numeric weights or partial credit are proposed.

## P01 — Reliable Queue Workers

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| P01-EC01 | `p01-page-1-element-3..5` | procedure | critical | Losing stable identity, replay safety, or terminal reasons removes the principal reliable-work invariants. |
| P01-EC02 | `p01-page-2-element-1..2` | definition | critical | A queue contract without ownership/acknowledgement or with premature success reverses the contract boundary. |
| P01-EC03 | `p01-page-2-element-3..5` | procedure | critical | Omitting payload versioning, lease rules, or post-write acknowledgement makes execution materially unsafe. |
| P01-EC04 | `p01-page-3-element-1..3` | mechanism | critical | Omitting the transactional idempotency-key/effect relation makes safe replay meaning false. |
| P01-EC05 | `p01-page-4-element-1` | limitation | major | Without the bounded-observation limitation, retries may be mistaken for guaranteed success. |
| P01-EC06 | `p01-page-4-element-2..5` | procedure | major | Failure classification, visible backoff, and exhausted-work review are substantive retry controls. |
| P01-EC07 | `p01-page-5-element-1..2` | condition | critical | Losing the no-private-payload and heartbeat-scope conditions changes privacy and ownership truth conditions. |
| P01-EC08 | `p01-page-5-element-3..5` | procedure | major | Heartbeat age, queue facts, and bounded receipts are needed for useful operational visibility. |
| P01-EC09 | `p01-page-6-element-1`, `p01-page-6-element-3` | procedure | critical | An incorrect shutdown sequence can claim new work or lose visible open leases. |
| P01-EC10 | `p01-page-6-element-2`, `p01-page-6-element-4` | condition | critical | Conflating disappearance with closure or inventing success corrupts recovery state. |
| P01-EC11 | `p01-page-7-element-1..5` | procedure | major | Omitting replay/interruption/malformed-input tests leaves a substantive verification gap. |
| P01-EC12 | `p01-page-8-element-1..5` | recommendation | major | The pre-enable checklist is the source's operational decision aid. |

Additional categories: EC01/03/06/09/11 `recommendation`; EC04 `condition`;
EC07 `risk`; EC10 `risk`; EC12 `procedure`. No source exclusions are proposed;
the final checklist is retained as an operational synthesis rather than a
duplicate claim.

## P02 — Bilingual Data Systems Report

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| P02-EC01 | `p02-page-1-paragraph-1..4` | background_context | minor | The project-owned, observable, native-text/table/vector scope improves context but is not the main quantitative content. |
| P02-EC02 | table-1 header cells + row-1 cells | quantitative_result | major | Losing stage, unit, owner, or value would make the Parse median `18 ms` fact uninterpretable. |
| P02-EC03 | table-1 header cells + row-2 cells | quantitative_result | major | Losing stage, unit, owner, or value would make the Index median `42 ms` fact uninterpretable. |
| P02-EC04 | table-1 header cells + row-3 cells | quantitative_result | major | Losing stage, unit, owner, or value would make the Review median `75 ms` fact uninterpretable. |
| P02-EC05 | table-2 header cells + PDF row | conclusion | major | The PDF native/review-pending status is a distinct source-coverage result. |
| P02-EC06 | table-2 header cells + Web row | conclusion | major | The Web native/review-pending status is a distinct source-coverage result. |
| P02-EC07 | table-2 header cells + Scan row | conclusion | major | The Scan image/review-pending status is a distinct source-coverage result. |
| P02-EC08 | `p02-page-4-paragraph-1..4`, both figure captions | limitation | major | Omitting vector/no-external-assets or development-only scope could misrepresent provenance or authority. |

Table row/column/header and caption-to-figure assertions are required. Chinese
and English restatements support the same evidence item. No exclusions.

## P03 — Traditional Chinese raster scan

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| P03-EC01 | page-1 paragraphs | mechanism | major | Fixed angle/noise preserving scan shape explains how the source enters the workflow. |
| P03-EC02 | page-2 paragraphs | condition | critical | Reordering paragraphs or losing region-return segmentation reverses traceability. |
| P03-EC03 | page-3 paragraphs | condition | critical | Failure/retry provenance and the distinction between noise and loss are core truth conditions. |
| P03-EC04 | page-4 paragraphs | procedure | major | Page/region review location and the no-external/private-data scope are substantive audit context. |
| P03-EC05 | page-5 paragraphs | mechanism | critical | Recovery source/order retention and deterministic bytes are the reproducibility conclusion. |

All five `掃描頁碼 N` and ten region labels remain Parser text/locator units
with exact page/geometry assertions. They do not create separate Generation
claims. No exclusions.

## P04 — Mixed native/scanned PDF

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| P04-EC01 | page-1 paragraphs, page-3 paragraphs | mechanism | major | Omitting native/scanned page-boundary semantics leaves the mixed-modality design materially incomplete. |
| P04-EC02 | `p04-page-1-formula` | core_concept | critical | Missing or changing `F = m * a` loses the source's sole formula. |
| P04-EC03 | table headers + Force row | quantitative_result | major | `Force = 12 N` requires its measure/value/unit relation. |
| P04-EC04 | table headers + Mass row | quantitative_result | major | `Mass = 3 kg` requires its measure/value/unit relation. |
| P04-EC05 | page-2 paragraphs | mechanism | major | The deterministic skewed-scan recipe and retained region position explain page-2 modality. |
| P04-EC06 | page-4 paragraphs | mechanism | major | Bilingual scanned content and geometry-to-source recovery explain page-4 traceability. |

Formula label, table structure, native/scanned page modality, and exact raster
region geometry are required assertions. Four `區域 A`/`Review B` labels remain
Parser text/locator units but do not create separate Generation claims. No
exclusions.

## W01 — Minimal web slice

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| W01-EC01 | `w01-element-1` | background_context | minor | Project-authored minimal-web scope is useful context, not the principal instruction. |
| W01-EC02 | `w01-element-2` | recommendation | critical | Losing heading preservation removes one of two explicit parser requirements. |
| W01-EC03 | `w01-element-3` | recommendation | critical | Losing code-block preservation removes one of two explicit parser requirements. |
| W01-EC04 | `w01-element-4` | procedure | major | The exact normalization example is the concrete implementation content. |

Exact DOM locator, list-item kind, code language/source-supplied metadata, and
canonical order are required. No exclusions.

## W02 — Traceable Data Workflows

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| W02-EC01 | `w02-lede`, `w02-overview-paragraph` | mechanism | major | The boundary-to-bilingual-context relation explains traceability. |
| W02-EC02 | `w02-overview-unordered-1` | recommendation | critical | Losing heading/paragraph hierarchy reverses a principal preservation rule. |
| W02-EC03 | `w02-overview-unordered-2` | recommendation | major | Locatable list items are a substantive structural requirement. |
| W02-EC04 | `w02-overview-unordered-3` | recommendation | major | Distinguishing boilerplate from article body prevents source/noise conflation. |
| W02-EC05 | `w02-overview-ordered-1..2` | procedure | critical | Snapshot-before-reference ordering is the source's core authoring sequence. |
| W02-EC06 | table headers + Parse row | quantitative_result | major | Parse `18 ms` and “Read structure” require the full row/header relation. |
| W02-EC07 | table headers + Review row | quantitative_result | major | Review `42 ms` and “Keep context” require the full row/header relation. |
| W02-EC08 | table headers + Publish row | quantitative_result | major | Publish `75 ms` and “Await decision” require the full row/header relation. |
| W02-EC09 | `w02-code` | procedure | major | Stable-source normalization is the concrete code procedure. |
| W02-EC10 | `w02-figure-text`, `w02-figure-caption` | procedure | critical | Losing Input → Normalize → Review reverses or erases the workflow. |
| W02-EC11 | `w02-aside` | limitation | major | Development-only, non-adoption scope is necessary authority context. |

`w02-header-brand`, `w02-navigation`, and `w02-footer` are proposed Q12
`source_noise` exclusions for Generation and End-to-end expected-claim
denominators only. They remain Parser text/noise units. Table/list/code/figure/
caption/hierarchy/DOM assertions are required.

## W03 — Offline rendered DOM

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| W03-EC01 | `w03-intro` | definition | critical | Browser/network independence defines the offline snapshot. |
| W03-EC02 | `w03-overview-paragraph` | mechanism | major | Nested-section context is the principal hierarchy mechanism. |
| W03-EC03 | `w03-overview-item-1..2` | procedure | critical | Fixed rendered DOM and bilingual preservation are the core input rules. |
| W03-EC04 | `w03-details-paragraph` | mechanism | major | One snapshot identity binding table and figure is material traceability context. |
| W03-EC05 | table headers + Rendered row | conclusion | major | Rendered=yes with fixed DOM is a distinct snapshot state. |
| W03-EC06 | table headers + Network row | limitation | critical | Network=no/offline build is a defining no-network condition. |
| W03-EC07 | `w03-figure-text`, `w03-figure-caption` | procedure | critical | Snapshot → Structure → Reference is the source's core relationship. |
| W03-EC08 | `w03-conclusion-paragraph` | conclusion | critical | Fixed-byte provenance is the reproducibility conclusion. |

Nested sections, table relations, figure/caption relation, DOM identity, and
canonical order are required. No exclusions.

## Y01 — Queue-worker transcript

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| Y01-EC01 | chapter-1 cues 0–2 | procedure | critical | Contract ownership, lease, acknowledgement, and before-code timing form one principal prerequisite. |
| Y01-EC02 | chapter-2 cues 3–5 | mechanism | critical | Persisting the idempotency key with the durable effect is necessary for a retry to observe the first result. |
| Y01-EC03 | chapter-3 cues 6–8 | procedure | critical | Heartbeat visibility, shutdown preservation, and recovery reconciliation form the core recovery sequence. |

Chapter headings are navigation structure, not separate claims. Cue identity,
order, start/end timing, chapter membership, and unavailable platform identity
remain explicit assertions. No exclusions.

## Y02 — Bilingual offline captions

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| Y02-EC01 | cue 0 | recommendation | critical | Contract-before-implementation is the principal process prerequisite. |
| Y02-EC02 | cue 1 | mechanism | major | Shared bilingual cue identity is substantive caption structure. |
| Y02-EC03 | cue 2 | condition | critical | Traceable timing boundaries are necessary for locator correctness. |
| Y02-EC04 | cue 3 | limitation | critical | Chapters must not be misrepresented as platform identity. |
| Y02-EC05 | cue 4 | mechanism | critical | Same-byte offline reproduction is the reproducibility mechanism. |
| Y02-EC06 | cue 5 | background_context | minor | Project ownership is provenance context rather than the main process. |
| Y02-EC07 | cue 6 | procedure | critical | Cue order and millisecond ranges are the required preservation rule. |
| Y02-EC08 | cue 7 | limitation | major | Development-only scope prevents authority overstatement. |

Chapter headings are navigation structure, not claims. Cue identity/order/
timing and unavailable platform identity remain assertions. No exclusions.

## C02 — Structured multi-speaker chat

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| C02-EC01 | message 001 and quoted occurrence in message 002 | recommendation | critical | Parser-contract-before-implementation is the principal prerequisite; the quote is supporting recurrence, not a new claim. |
| C02-EC02 | message 002 | recommendation | major | Keeping the source binding is a substantive evidence-integrity step. |
| C02-EC03 | message 003 + embedded code | procedure | critical | Fixed-byte SHA-256 verification is the concrete integrity procedure. |
| C02-EC04 | message 004 | condition | critical | Review that changes the contract would invalidate the stated governance boundary. |
| C02-EC05 | message 005 | recommendation | major | Preserving bilingual order is a substantive content-order rule. |
| C02-EC06 | message 006 | conclusion | major | Follow-up thread independence is a distinct source-structure conclusion. |

The quoted occurrence is linked as `duplicate_occurrence` to C02-EC01 for
Generation/End-to-end claim count only; it remains Parser content. The code is
required evidence for C02-EC03, not a separate claim. Exact message, source
sequence, thread, reply, speaker ID, parent/part relation, and order assertions
are required. Independent review remains pending.

## S01 — Synthetic Study Board

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| S01-EC01 | `s01-element-0` | background_context | minor | Board identity is navigation/context. |
| S01-EC02 | `s01-element-1` | conclusion | major | “Parser lane ready” is the principal displayed status. |
| S01-EC03 | `s01-element-2` | limitation | major | “No external assets” is material provenance scope. |

Exact image identity, geometry, UI-text kind, and reading order are required.
No exclusions.

## S02 — Ordered overlapping screenshots

| ID | Required source elements | Primary category | Importance | Counterfactual rationale |
| --- | --- | --- | --- | --- |
| S02-EC01 | `s02-element-0` | background_context | minor | Screen-one identity provides sequence context. |
| S02-EC02 | `s02-element-1`, `s02-element-4` | core_concept | major | Shared content across both images is the intended overlap fact; recurrence forms one claim. |
| S02-EC03 | `s02-element-2` | condition | major | The overlay badge is a distinct visible region/overlap condition. |
| S02-EC04 | `s02-element-3` | background_context | minor | Screen-two identity provides sequence context. |
| S02-EC05 | `s02-element-5` | conclusion | major | Follow-up state is the final displayed status. |

The second shared-content occurrence is additional source support, not an
excluded source occurrence. Exact image order/identity, geometry, reading
order, and cross-image shared-content relation are required. No exclusions.

## Batched owner decision boundary

Owner approval of this proposal would establish primary annotation only. It
would authorize generation of immutable successor Gold candidates bound to the
exact source/reference/profile digests. It would not satisfy independent Gold
review, scorer approval, formal manifest eligibility, or baseline authority.

The independent reviewer must still check every claim boundary, required
qualifier, category, importance rationale, structure/locator assertion,
duplicate/exclusion disposition, and the absence of unresolved disputes without
seeing candidate scores.
