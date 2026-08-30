# Parser & Note Completeness Roadmap

This is the operational execution pointer for `parser-note-completeness-v1`.
It reconciles repository evidence with ADR-0009 and the Q1-Q29 foundation. It
does not reopen frozen contracts, grant benchmark authority, or authorize
production-runtime changes.

## Current Pointer

- Current phase: Parser & Note Completeness execution.
- Current step: 13-case evidence review and formal-authority handoff.
- Status: `blocked` — C01 implementation/audit closure and exact five-case
  technical smoke wiring are verified. Every selected full-profile case now
  has an immutable draft review packet, but Parser metric realization and
  formal execution publication remain blocked by frozen evidence/schema slots
  and human authority.
- Completed milestone immediately before: M4 C01 implementation/audit closure.
- Exact next action: humans review the 13 draft packets, provide fixture
  provenance/rights/privacy evidence, adjudicate gold claim boundaries,
  importance, and applicability, and approve separation of duties. After that,
  freeze the pending Q14 Parser metric contracts and formal Q16-Q24 store/
  provenance schemas before executing the full baseline.
- Blockers: no case has approved fixture provenance/rights/privacy, independent
  gold review, Q25 separation-of-duties approval, or formal manifest/authority
  closure. Q14 Parser formulas and the broader formal result/provenance/store
  schemas remain explicitly pending in the foundation.
- Explicitly not authorized: formal baseline or comparison, candidate ranking,
  thresholds, weights, partial credit, global completeness, universal
  macro/micro aggregation, Parser-specific metrics, production behavior
  changes, rollout/adoption, or expansion beyond C01.

## Status Semantics

- `todo`: not started.
- `doing`: started, with evidence of active work that is not yet closed.
- `blocked`: cannot proceed at the current scope without a named human,
  evidence, or external decision.
- `done`: implemented and verified against the applicable contract; file
  existence alone never qualifies.
- `deferred`: intentionally postponed by the current authority boundary.
- `human_review_required`: Codex may prepare or lint the material, but a human
  approval or adjudication is required before closure.

## Milestone Roadmap

| ID | Status | Goal | Depends on | Evidence | Definition of Done | Next |
| --- | --- | --- | --- | --- | --- | --- |
| M0 | `done` | Establish discovery findings and scope boundary. | — | `01-discovery.md` | Production gaps and benchmark isolation are documented. | Preserve discovery as context; do not turn it into runtime behavior. |
| M1 | `done` | Complete the Q1-Q29 foundation at its stated contract/topology boundary. | M0 | `02-benchmark-foundation.md`, ADR-0009 | Frozen decisions and pending evidence/realization work are recorded without invented constants. | Execute only the pending frontier below. |
| M2 | `done` | Realize the Q14 Generation/End-to-end scorer foundation. | M1, Q26 note artifacts | `q14_scoring.py`, its tests, commit `a3198d1` | Frozen schemas, exact state vectors, support counts, bindings, and digest rules are implemented and verified. | Use the frozen path for C01 only. |
| M3 | `done` | Score C01 from real persisted Parser/Generation/End-to-end execution artifacts. | M2, C01 source/reference, smoke profile | `c01_scoring.py`, draft C01 gold, and seven focused scoring tests | C01 materializes claim maps, claim-to-gold mappings, applicability, contracts, and four Q14 fixture results from persisted artifacts; replay and fail-closed digest tests pass. | Preserve diagnostic-only status until human gates close. |
| M4 | `done` | Close the C01 implementation/audit seam without changing frozen Q14 schemas or production behavior. | M3 | Seven C01 scoring tests plus the package suite pass; raw-source and Parser-output E2E lineage tampering now fails closed. | Diff, imports, bindings, external digests, output roles, and failure modes are contract-reviewed and accepted as the smallest diagnostic slice. | Human gates remain separate under M5. |
| M5 | `blocked` | Close C01 gold and fixture governance authority. | M4, Q22, Q25 | C01 `candidate.json` is `draft_candidate`; `gold.json` is `draft_candidate` and `formal_authority:false`. | Source provenance/rights/privacy, acquisition/creation receipt, independent gold review/adjudication, and separation-of-duties evidence are approved and bound by an immutable manifest. | Human review and evidence submission. |
| M6 | `doing` | Wire the exact five-case smoke profile through diagnostic lane/runner/scoring checks. | M4; M5 is not needed for diagnostic wiring | `test_smoke_technical_wiring.py` executes and replays `P01/W01/Y01/C01/S01` through all three lanes; C01 alone has draft Q14 semantic scoring. | All five reuse full-fixture bytes and references, replay deterministically, and remain explicitly diagnostic; five-case Q14 semantic scoring still requires reviewed mappings/applicability. | Human review packets now expose the exact missing scorer inputs. |
| M7 | `blocked` | Realize the Q14 Parser metric contracts and scorer path. | M1, approved parser units/gold, Q12/Q14 evidence | Parser lane exists; Q14 1.0.0 rejects Parser and the foundation explicitly leaves Parser formulas, tokenization/alignment, measurement boundaries, and aggregation pending. | Versioned parser metrics have approved units, formulas, denominators, mappings, and tests without cross-lane scalarization. | Freeze owner-approved Q14 Parser schema/contracts; do not invent them in scorer code. |
| M8 | `blocked` | Complete the 13-case fixture/reference/gold set for formal use. | M5, Q22, Q25, independent gold review | All 13 selected source/reference trees and immutable `gold-review-packet` artifacts exist; C01 alone also has draft scorable gold. Every packet keeps claim boundary, importance, applicability, provenance, rights, privacy, review, and scorer binding unresolved. | Every case has exact bytes/digests, evidence-approved provenance/rights/privacy, reviewed/adjudicated gold, and canonical eligibility. | Humans review the packets and publish successor governed artifacts. |
| M9 | `blocked` | Close runner, offline, provenance, receipt, and result-store artifacts required for formal execution. | M1, Q16-Q24, Q28/Q29 boundaries | Diagnostic manifests/plans, immutable attempt history, receipts, terminal/collection records, credential rejection, optional attestation validation, local result storage, and replay exist. Formal mode correctly rejects execution; exact formal provenance/store/publication schemas and a real no-egress conformance record remain pending. | Formal execution has complete immutable plans, receipts, provenance, terminal/collection records, result storage, offline enforcement evidence, and replay bindings. | Freeze pending owner schemas and supply genuine OS/container no-egress evidence before enabling formal mode. |
| M10 | `blocked` | Publish the full current-implementation characterization baseline. | M7, M8, M9, Q10 closure | A diagnostic-only full-profile End-to-end readiness run closed all 13 planned slots; it had no no-egress attestation and produced no formal semantic/Parser results or baseline. | All 13 cases and applicable three-lane results are complete, authoritative, replayable, and labeled as characterization baseline without quality inference. | Requires M7-M9 and Q10 authority closure. |
| M11 | `blocked` | Calibrate Q11 gates and resolve Q12 evidence-dependent classifications. | M8, M10, Q11/Q12 evidence | Foundation marks constants/classifications pending; no thresholds or blockers may be invented. | Independent evidence, calibration, review, and immutable gate revisions are approved. | Gather evidence; do not tune against candidate results. |
| M12 | `todo` | Reach Q13 formal comparison readiness. | M10, M11, full-profile pairing and compatible artifacts | Q13 topology is frozen; metric-specific comparison realization/calibration remains pending. | Formal baseline/candidate comparison artifacts have complete identity, eligibility, pairing, digest, and authority closure. | Revisit only after baseline and gates close. |
| M13 | `todo` | Realize Q15 repeat/resource policy where evidence requires it. | M9-M12, Q15 evidence | Repeat/topology is frozen; repeat count, compatibility, schedule, and diagnostic methods remain evidence-dependent. | Any required repeat/resource policy is preregistered, independently reviewed, immutable, and non-inferential. | Resolve only for a demonstrated formal need. |
| M14 | `deferred` | Run preregistered candidate experiments. | M12, M13, approved candidate scope | No candidate comparison or adoption authority is currently available. | Candidate execution uses approved fixtures, gold, contracts, gates, and run membership; no best-of-N or post-result selection. | Defer until formal readiness. |
| M15 | `deferred` | Make a production adoption decision. | M14 and all lane-specific authority/gate closure | ADR-0009 forbids inference from smoke, drafts, partial runs, or diagnostics. | Human governance makes a separately recorded decision; no benchmark result silently changes production behavior. | Remains outside the current authorization. |

## 13-Case Fixture Matrix

The matrix is based on the tracked fixture/reference trees, external checksum
records, profile bindings, vertical-slice tests, and governance candidate
records. `✅` means complete for the named engineering artifact only; it does
not mean formal eligibility. `🟡` means draft/provisional. `👤` means a human
gate is known and unsatisfied. `❌` means the named artifact or closure is
missing. `—` means not applicable. `?` means the repository evidence cannot
establish the value.

For source and reference columns, the selected revisions are the ones bound by
the current profile: P03/P04/S02 use `revision-002`; preserved `revision-001`
bytes are tested separately. The existing vertical-slice tests demonstrate
canonical source/reference bytes and deterministic builders. The candidate
records do not prove gold completion, rights, privacy, review, or authority.

| Case | source bytes/canonical source | digest | provenance/rights/privacy | reference NormalizedDocument | gold candidate | independent gold review | canonical eligibility | Parser scoring | Generation scoring | E2E scoring | deterministic replay | formal/full eligibility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| P02 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| P03 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| P04 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| W01 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| W02 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| W03 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Y01 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Y02 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| C01 | ✅ | ✅ | 👤 | ✅ | 🟡 draft + scaffold | 👤 | ❌ | ❌ | 🟡 | 🟡 | ✅ | ❌ |
| C02 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| S01 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| S02 | ✅ | ✅ | 👤 | ✅ | 🟡 scaffold | 👤 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |

Evidence details:

- Source/reference completion is exercised by the per-family vertical-slice
  tests, `normalized_document.py`, the full/smoke profiles, and their digest
  validation. It is not a claim that the cases are canonical.
- Every selected case has a `gold-review-packet.json` plus external digest.
  The packet is an unreviewed element inventory: it proposes no claim boundary,
  importance, applicability, provenance, rights, privacy, or authority outcome.
- C01's `gold.json` and `gold.sha256` are explicitly draft and are not
  independent review records. C01's `🟡`
  Generation/E2E entries refer to the working-tree diagnostic adapter and
  tests, not a formal metric result.
- `❌` Parser scoring means the Parser lane exists diagnostically but the
  Q14-specific Parser metric formulas and scorer realization are not present.
- `✅` deterministic replay means the persisted source/reference/build or
  renderer replay is tested. C01 also has deterministic Q14 result replay,
  still diagnostic-only.
- All candidate records currently set `candidate_status=draft_candidate`,
  `formal_manifest_present=false`, and every authority flag to false, with Q22
  and Q25 evidence pending.

## Smoke Profile

The smoke profile is exactly `P01`, `W01`, `Y01`, `C01`, and `S01`, resolved
through the same full-fixture/reference semantics. One integration test now
executes all five through Parser, Generation, renderer, and End-to-end,
replays their immutable candidate/projection artifacts, checks diagnostic
membership, and replays C01's four Q14 results. The other four cases have
review packets but no reviewed semantic mapping/applicability input, so Q14
semantic scoring correctly remains unmaterialized.

| Track | Current state | Meaning |
| --- | --- | --- |
| Three-lane engineering wiring | `done` | Exact five-case execution, artifact schemas, renderer, replay, diagnostic membership, and error paths are verified. |
| Q14 semantic scorer wiring | `doing` | C01 coverage/support scoring and replay are verified; P01/W01/Y01/S01 require reviewed claim mappings and applicability before equivalent scoring is honest. |
| Formal authority | `blocked` | Smoke is permanently `diagnostic_only` for this foundation; draft gold, incomplete Q22/Q25 evidence, and missing full authority prevent baseline, gate, comparison, and adoption claims. |

## Parser Metric Realization Status

The reference artifacts establish where metric families may apply, but they do
not approve the pending Q14 Parser schemas, formulas, alignment/tokenization
rules, or measurement boundaries. No Parser result is emitted until those
owner decisions exist.

| Metric family | Reference cases with visible applicability | Technical status | Exact blocker |
| --- | --- | --- | --- |
| Extraction coverage | all 13 | `blocked` | Source-side unit inventory, normalization/alignment formula, and denominator disposition are pending. |
| OCR CER/WER | P03, P04, S01, S02 candidate scope | `blocked` | Language tokenization, normalization, recognition boundary, and reviewed transcription gold are pending. |
| Reading order | all 13 | `blocked` | Approved source-side block alignment and exact inversion formula contract are pending. |
| Structure preservation | all 13; typed table/code/formula subsets below | `blocked` | Assertion inventory, label mapping, denominator, and aggregation contract are pending. |
| Locator identity/alignment | all 13 | `blocked` | Approved locator assertions and alignment dispositions are pending. |
| Geometry / IoU | P03, P04, S01, S02 | `blocked` | IoU formula/application unit and any genuine measurement boundary are pending. |
| Span overlap | no selected reference exposes a non-null locator text span | `not_realized` | No frozen unit inventory supports a v1 result; do not synthesize spans. |
| Caption timing | Y01, Y02 | `blocked` | Temporal alignment/delta formula and caption gold review are pending. |
| Table structure | P02, P04, W02, W03 | `blocked` | Cell alignment groups, row/column/span/header assertions, and formula are pending. |
| Formula preservation | P04 | `blocked` | Formula comparison/equivalence contract is pending. |
| Code preservation | P01, W01, W02, C02 | `blocked` | Approved strict-literal/code units and exact preservation result contract are pending. |

## Runner / Offline / Replay / Store Status

| Capability | Diagnostic technical state | Formal closure |
| --- | --- | --- |
| Profile manifests and run plans | Complete for exact smoke/full diagnostic profiles | Formal membership/plan schema pending |
| Terminal and collection records | Canonical external digests and explicit closed/invalid/operational/unclosed/missing states | Formal publication binding pending |
| Attempt history and resume | Append-only ordinals; closed slots are not rerun | Formal execution compatibility policy pending |
| Offline protection | Live/provider flags and known credential environment inputs are rejected; attestation bindings validate | Genuine OS/container no-egress conformance evidence is absent |
| Provenance | Parser/generation/renderer producer configuration and lineage digests exist | Q19 formal provenance schema/equivalence rules pending |
| Receipts | Runner start/terminal, lane attempts, and Q28 work-unit receipts exist | Formal receipt/publication binding pending |
| Result storage | Immutable local diagnostic store and Q24 E2E result/attempt packages exist | Q24 formal result-store schema/publication pending |
| Replay | Source/reference, three-lane outputs, renderer projection, C01 Q14 results, and one full 13-case diagnostic E2E collection complete deterministically | Full 13-case Parser and semantic Q14 replay awaits M7/M8 |
| Digest/version compatibility | Canonical schemas and exact external digest checks fail closed | Formal cross-version compatibility approval pending |

## Human / Evidence Gates

Codex may prepare, canonicalize, lint, validate, bind, and test artifacts
within the frozen contracts. Codex may not self-approve the following:

- fixture authorship/acquisition provenance, redistribution rights, privacy
  disposition, and source-specific receipts;
- independent gold review, adjudication, segmentation, expected-claim truth,
  or disputed applicability/denominator decisions;
- Q25 separation of duties and independent approval of fixture, gold, scorer,
  threshold, or governance changes;
- Q10 authority closure, Q11 calibration/threshold approval, Q12
  evidence-dependent blocker classifications, or Q13 formal comparison
  authority;
- evidence-dependent Q14 Parser measurement boundaries and aggregation
  selections, Q15 repeat/resource/compatibility policy, Q28 algorithm or
  measurement choices, or Q29 boundary evidence/configuration approval;
- any formal baseline, candidate comparison, quality gate, or adoption decision.

The required human handoff for C01 is: review the draft expected claims and
applicability, independently review the source/gold and governance evidence,
record any adjudication, and approve a successor immutable governance/gold
revision only if the evidence supports it.

## Pending Contract Realization

This section is an action index, not a restatement of the detailed Q1-Q29
contracts. Frozen boundaries remain authoritative.

- Q11: record evidence-backed gate slots, calibration records, constants, and
  independent approval only after the required baseline and gold/evidence
  closure. Do not add thresholds now.
- Q12: realize scoped authority/blocker/aggregation records only from approved
  evidence. Keep partial states, critical blockers, non-compensation, and
  denominator ownership unchanged.
- Q13: realize full-profile-compatible pairing and comparison artifacts after
  authoritative baseline inputs exist. Do not publish formal comparison from
  smoke or draft results.
- Q14: finish the C01 Generation/E2E diagnostic wiring and replay audit first;
  then realize Parser metric formulas, evidence-supported measurement and
  aggregation, and comparison-dependent result artifacts in their own scope.
  Preserve exact state vectors, support counts, named denominators, and
  external self-digests.
- Q15: realize formal repeat count, schedule/block, execution compatibility,
  end-to-end dependency mode, and any diagnostic method only where evidence
  requires them. Retries and replay are not new samples.
- Q16-Q24: close smoke/full profile semantics, runner terminal/collection
  records, enforced offline boundary, replay provenance, raw resource
  observations, logical-run history, and fixture/governance evidence. Q22/Q25
  are the immediate C01 authority gates; Q24 formal result storage remains a
  separate closure item.
- Q26: reuse the realized `BenchmarkNoteDocument` and rendered projection
  roles; do not merge them with `NormalizedDocument`, gold, or production
  proposal schemas.
- Q28: defer work-unit sizing, overlap, merge, contradiction detection, and
  measurement choices until evidence/owner decisions require them; do not
  introduce retrieval or Step 100 behavior.
- Q29: retain deterministic pre-generation routing and forced-diagnostic
  separation; add only approved boundary/configuration evidence and
  compatibility realization. Do not let candidate output or post-result facts
  influence routing.

## Stop Boundaries

Before formal baseline authority closes, stop at the first request to:

- invent thresholds, weights, partial-credit rules, or a global completeness
  score;
- make universal macro/micro or cross-stratum aggregation authoritative;
- use Parser/OCR/ASR or Generation shootouts as if they were formal evidence;
- turn smoke, a draft gold, a partial profile, or a provisional result into a
  baseline, gate, comparison, or adoption decision;
- change production parser, generation, routing, renderer, or runtime behavior;
- self-approve gold, rights/privacy/provenance, governance, or independent
  review evidence;
- expand implementation to P01-P04, W01-W03, Y01-Y02, S01-S02, or a generalized
  framework before the C01 milestone explicitly authorizes that scope.

## Recommended Next Command

```text
cd "/Users/rileylai/Desktop/code/project/LearnLoop Agent" && rtk uv run --no-env-file --frozen pytest -q tests/evals/parser_note_completeness
```

This verifies the C01 audit closure, exact five-case smoke technical wiring,
13 review packets, runner/replay infrastructure, and adjacent benchmark
contracts. It does not authorize a commit, formal result, or human governance
decision.
