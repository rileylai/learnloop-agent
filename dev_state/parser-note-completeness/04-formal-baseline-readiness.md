# Parser & Note Completeness Formal-Baseline Readiness Audit

Audit date: **2026-08-31**
Benchmark selection: `parser-note-completeness/1.0.1`, full profile
`revision-002`
Outcome: **FORMAL-BASELINE-READY after named human/contract gates; no formal
baseline exists**

This is the authoritative readiness handoff for the current goal. It separates
verified engineering facts from authority. It does not approve a fixture,
Gold, metric, scorer, execution contract, or baseline.

## Status key

- `T`: repository evidence closes the technical record.
- `H`: a human must review, approve, or supply evidence.
- `C`: a frozen owner still requires a contract decision.
- `N/A`: the metric or record does not apply.
- `NO`: the case is not formally eligible.

The missing-item classifications used below are exactly:

1. `repository_evidence_can_close`
2. `codex_can_prepare_but_human_must_approve`
3. `human_must_supply_evidence`
4. `contract_decision_required`
5. `genuinely_unavailable`

## Repository-closed evidence

The selected full profile and benchmark manifest close these technical facts
for all 13 cases:

- exact tracked source bytes and external SHA-256 records;
- selected diagnostic profile `revision-003` fixture revisions and exact
  benchmark `1.0.2` bindings;
- exact reference-document bytes, external SHA-256, canonical serialization,
  and source-snapshot binding;
- producer-configuration bytes and digest binding;
- immutable draft gold-review packet bytes and digest;
- diagnostic Parser, Generation, renderer, and End-to-end execution wiring;
- immutable attempt/receipt/collection history and deterministic replay;
- fail-closed diagnostic/formal separation.

These are `repository_evidence_can_close`. They do not establish source
authorship, redistribution permission, privacy approval, reference fidelity,
Gold truth, independent review, or formal authority.

## Authoritative 13-case readiness matrix

`Gen` and `E2E` mean the technical scoring path is available; every formal
semantic result still needs reviewed Gold/mappings. `Manifest` means the case
is bound by the diagnostic full profile, not by a formal authority manifest.

| Case | Source bytes | Digest | Reference | Provenance | Rights | Privacy | Owner-primary Gold | Independent review | Gold authority | Parser applicability | Parser scoring | Gen | E2E | Manifest | Provenance/receipts | Offline | Replay | Formal eligibility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | T | T | H owner approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| P02 | T | T | H corrected/approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| P03 | T | T | H corrected/approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| P04 | T | T | H corrected/approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| W01 | T | T | H owner approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| W02 | T | T | H corrected/approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| W03 | T | T | H corrected/approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| Y01 | T | T | H owner approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| Y02 | T | T | H owner approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| C01 | T | T | H owner approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H diagnostic result | T/H diagnostic result | T diagnostic | T/C formal | C | T | NO |
| C02 | T | T | H owner identity approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| S01 | T | T | H owner approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |
| S02 | T | T | H owner approved | H owner approved | H owner approved | H owner approved | H owner primary | H pending | H | T matrix | T owner/H pending | T/H | T/H | T diagnostic | T/C formal | C | T | NO |

No row collapses technical and authority readiness. In particular, the
reference document is technically valid but its source fidelity is unreviewed,
and the diagnostic execution is replayable but not formally admissible.

## Fixture and Gold authority classification

| Item | Cases | Classification | Evidence and required closure |
| --- | --- | --- | --- |
| Selected bytes/revision/digest | all 13 | `repository_evidence_can_close` | Full profile `revision-003`, benchmark `1.0.2`, fixture bytes, external digest records, and validation tests bind the selection. |
| Deterministic creation/reproduction record | P01-P04, P02-P04 references, W02-W03, Y01-Y02, C02, S02 | `repository_evidence_can_close` for technical reproduction only | Builders and/or producer configuration describe project-authored creation. P03/P04/S02 additionally bind the controlled Noto asset. |
| Human creation/acquisition provenance | all 13 | `human_owner_approved`; independent review pending | Riley Lai explicitly approved creator/acquirer identity and the recorded project-owned synthetic creation methods for the exact selected bytes on 2026-08-31. The decision is bound in `human-review-intake.json`; it is not independent approval. |
| Project ownership / redistribution rights | all 13 | `human_owner_approved`; independent review pending | Riley Lai explicitly approved project ownership and redistribution with the repository for the exact selected bytes on 2026-08-31. Q25 independent rights approval remains `human_must_supply_evidence`. |
| Privacy disposition | all 13 | `human_owner_approved`; independent review pending | Riley Lai explicitly approved that the exact selected bytes contain no real personal data, private conversations, or other private source material. Q25 independent privacy approval remains `human_must_supply_evidence`. |
| Independent fixture approval and Q25 duties | all 13 | `human_must_supply_evidence` | Reviewer identity, scope, independence, timestamp, and decision are absent. |
| Reference-document fidelity | all 13 | `human_owner_approved`; independent review pending | Riley approved the bounded clean set and the five corrected successor dispositions. Canonical/digest/source bindings are valid; independent fidelity review remains absent. |
| Owner-primary Gold expected claims, evidence, categories, importance, locators, and structure | all 13 | `human_owner_approved`; independent review pending | Immutable index `governance/owner-primary/revision-001/manifest.json` binds all 13 records and 82 claims; no unresolved owner items remain. |
| Independent Gold review/adjudication | all 13 | `human_must_supply_evidence` | Primary annotator, different reviewer, timestamps, disputes, and adjudications are absent. Codex is not an independent reviewer. |
| Gold/formal manifest authority | all 13 | `human_external_evidence_required` | Independent Gold review/adjudication and scorer/governance approval must be bound without mutating owner-primary revisions. The formal schema cannot encode pending authority as formal. |

No independent Gold/review evidence is `genuinely_unavailable` by repository
fact; it is externally pending. The only presently genuine v1 data absence is
a non-null DOM/PDF/chat locator text span for span-overlap scoring.

## Repository-detected reference-fidelity findings

The source/reference bindings and canonical JSON validate, but direct source
inspection found content-fidelity defects that the digest and schema tests do
not detect. These findings are repository evidence, not human adjudication:

| Case | Finding | Required disposition before reference approval |
| --- | --- | --- |
| P02 | The native PDF uses a synthetic Type0/CID font without an embedded font program. Text extraction recovers the ToUnicode text, but an independent Poppler render does not faithfully display the Chinese glyphs. The reference also omits the two final paragraphs on page 1 and the two development-status paragraphs on page 4; its first-table header cells differ from the source (`Stage / 階段`, `Median ms / 中位毫秒`, `Owner / 負責人`); and both figure captions add `vector processing view`, which is absent from the source. | Publish a successor fixture/reference revision with a controlled embedded font and a complete, source-exact reference. Do not approve the current P02 reference. |
| P03 | Every raster page visibly contains `掃描頁碼 N`, `區域甲`, and `區域乙`, but none of those 15 text regions appears in the reference or an approved source-side exclusion. | Add the regions to a successor reference or obtain an explicit Q12-owned exclusion with rationale. Do not silently omit them from OCR/text denominators. |
| P04 | Native pages use the same non-embedded synthetic CID-font pattern and do not render Chinese faithfully under Poppler. Page 1's paragraph `表格保留單位與欄位關係，方便逐格定位。` is absent from the reference, and the raster-page labels `區域 A` and `Review B` are absent for pages 2 and 4. The source formula label is reduced to the formula value without an explicit disposition for the label. | Publish a successor fixture/reference revision with a controlled embedded native font; add the missing content or record explicit Q12-owned exclusions. Do not approve the current P04 reference. |
| W02 | The visible figure body `[Input] → [Normalize] → [Review]` is absent from the reference; only the empty figure node and caption remain. | Add a source-faithful figure-content element or explicitly approve an exclusion. |
| W03 | The visible figure body `[Snapshot] → [Structure] → [Reference]` is absent from the reference; only the empty figure node and caption remain. | Add a source-faithful figure-content element or explicitly approve an exclusion. |
| C02 | Source messages contain stable `speaker_id` values. The reference folds speaker names into message content but has no typed speaker-identity field or assertion. | Decide whether speaker identity is an applicable v1 Chat assertion, an explicit typed exclusion, or outside the selected contract. Do not infer the decision from display names. |

No obvious source/reference discrepancy was found in the bounded review of P01,
W01, Y01, Y02, C01, S01, or S02. That observation prepares human review; it
does not constitute fidelity approval or independent Gold review.

## Fixture-to-Parser-metric applicability matrix

`A` means the selected reference exposes the required modality or unit family.
`P` means partial source support. `—` means the selected fixture does not expose
that metric family. Applicability is technical discovery, not authority.

| Case | Text | OCR CER | Reading order | Structure | Table | Formula | Code | Duplicate/noise | Locator identity | Geometry | Span overlap | Timing | Chat identity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | A | — | A | A | — | — | A | A | A | — | — | — | — |
| P02 | A | — | A | A | A | — | — | A | A | — | — | — | — |
| P03 | A | A | A | A | — | — | — | A | A | A | — | — | — |
| P04 | A | A raster subset | A | A | A | A | — | A | A | P raster subset | — | — | — |
| W01 | A | — | A | A | — | — | A | A | A | — | — | — | — |
| W02 | A | — | A | A | A | — | A | A | A | — | — | — | — |
| W03 | A | — | A | A | A | — | — | A | A | — | — | — | — |
| Y01 | A | — | A | A | — | — | — | A | A | — | — | A | — |
| Y02 | A | — | A | A | — | — | — | A | A | — | — | A | — |
| C01 | A | — | A | A | — | — | — | A | A | — | — | — | A |
| C02 | A | — | A | A | — | — | A | A | A | — | — | — | A |
| S01 | A | A | A | A | — | — | — | A | A | A | — | — | — |
| S02 | A | A | A | A | — | — | — | A | A | A | — | — | — |

The references contain no non-null locator `text_span`, so DOM/text-span
overlap has no v1 scoring unit. Web locators still support exact identity
checks. P04 geometry applies only to the raster region; native-text geometry is
explicitly unavailable. YouTube evaluates the frozen captions, not audio or
ASR quality.

## Parser raw-measurement decision packet

Riley Lai approved the bounded proposal as `9A` on 2026-09-01, restricted to
the metric families actually used by the frozen 13 cases. The implementation
is `parser_raw_measurements.py` with focused tests. It contains no threshold,
weight, partial credit, global score, universal macro/micro aggregate, WER,
ASR, span-overlap, fuzzy alignment, or hypothetical-case framework. The
implementation and registry remain owner-approved with independent scorer /
governance review pending, so they have no formal authority.

| Family | Scoring unit / reference owner | Alignment | Denominator | Proposed deterministic raw measurement | Unresolved decision |
| --- | --- | --- | --- | --- | --- |
| Text extraction | approved source reference or evidence item in reviewed Gold | Q9 priority: locator, structure, exact raw, exact projection, reviewed mapping | authoritative applicable source units | exact preserved/missing unit IDs and counts; optional character edit facts only for an approved aligned span | approve unit inventory, projection profile, alignment disposition, and whether character distance is a separate metric |
| OCR CER | reviewed transcription span for P03/P04-raster/S01/S02 | approved region/locator alignment; abstain otherwise | reference Unicode code-point count per aligned recognition region | Levenshtein edit count and `edit_count/reference_code_points`; define empty-reference result explicitly | approve raw normalization (recommended: line endings only, no semantic correction), region inventory, and empty-reference rule; WER remains separate |
| Reading order | approved aligned reference element IDs | approved alignment groups | approved comparable ordered pairs or another explicitly chosen order-unit set | exact inversions and exact unit count | choose the order unit and formula; do not infer all pairwise assertions from element order without approval |
| Structure | approved structure assertion ID | exact predicate/element alignment | applicable assertion IDs | exact satisfied/missing/conflicting assertion IDs and counts | approve assertion inventory and candidate-kind mapping |
| Table | approved cell/alignment group and structure assertion | reviewed one-to-one/one-to-many/many-to-one cell groups | applicable cell text units and table-structure assertions, kept separate | exact cell text dispositions plus exact row/column/span/header assertion dispositions | approve cell grouping and keep text separate from structure; no flattened-table scalar |
| Formula | approved formula span/assertion | exact raw or approved formula projection; abstain on semantic equivalence | applicable formula IDs | exact preserved/missing/different IDs | approve finite presentation map; no symbolic algebra in v1 |
| Code | approved code element/span | locator/structure then exact raw | applicable code units | exact byte/text identity after only approved CRLF/terminal-newline projection; preserved/missing/different IDs | approve unit boundaries and terminal-newline classification |
| Duplicate/noise | approved candidate output units and source-backed alignment | exact duplicate provenance; abstain on semantic similarity | emitted candidate units or characters under a named contract | exact duplicate unit IDs/counts and exact unmatched/noise unit IDs/counts | define unit, denominator, and whether repeated source-backed material is legitimate recurrence |
| Locator identity | approved locator assertion ID | exact typed identity | applicable locator assertions | exact correct/missing/unavailable/conflicting/fabricated IDs and counts | approve assertion inventory; keep availability separate from identity correctness |
| Geometry | approved aligned locator geometry | exact identity plus approved region alignment | applicable aligned geometry assertions | exact intersection area, union area, and rational IoU; unresolved alignment emits no IoU | approve one geometry unit per assertion/alignment group and zero-area handling; no pass threshold |
| Caption timing | approved aligned caption cue | cue identity or reviewed alignment | applicable aligned cues | signed and absolute start/end deltas in milliseconds | approve cue alignment and whether duration delta is also emitted; no tolerance/pass threshold |
| Chat identity | approved message/thread/reply assertion | exact message locator identity | applicable chat locator/structure assertions | exact correct/missing/conflicting message, sequence, thread, and reply IDs/counts | approve assertion inventory; do not derive speaker or timestamp facts that are absent |

For every family, unresolved alignment produces a named `unresolved` alignment
record and no raw measurement for that unit; it never becomes zero, exclusion,
match, or failure. The frozen Foundation derives the family topology,
source-side ownership, abstention behavior, and anti-duplication rule. The 9A
decision closes the owner formula choice for the frozen-case implementation;
the exact reviewed Gold inventories and independent scorer/governance approval
remain `human_external_evidence_required`.

All proposed values are raw measurements. No pass threshold, global Parser
score, macro/micro authority, importance weight, or partial-credit scalar is
defined. Formal aggregation remains `fixture_vector_only` unless a later
metric-specific decision approves something else.

### Approved bounded deterministic choices

The owner-approved bounded v1 registry uses these exact raw semantics.

- Apply only CRLF-to-LF projection globally. Do not normalize Unicode,
  whitespace, punctuation, case, or semantics. For code only, report a single
  terminal-newline difference separately and compare the remaining bytes.
- Text units are approved text-bearing source-reference units. Emit exact
  `preserved`, `missing`, or `different` IDs and counts. For aligned
  `different` units also emit code-point edit count and reference code-point
  count as separate raw facts; do not merge them into the unit disposition.
- OCR uses approved recognition regions. Emit Levenshtein edits, reference
  Unicode code-point count, and the unreduced rational CER. If the reference is
  empty, emit `empty_reference` plus candidate length and no CER. No WER is in
  this approval batch.
- Reading order uses adjacent edges from each approved canonical sequence plus
  any explicitly approved non-adjacent semantic-order assertions. Emit exact
  satisfied, missing, and reversed edge IDs/counts; do not infer or score every
  pair.
- Structure, locator, and chat identity operate per approved assertion ID and
  emit exact correct/satisfied, missing/unavailable, conflicting, or fabricated
  dispositions. Chat identity includes `speaker_id` only where Gold explicitly
  owns it (currently the C02 owner proposal); absent timestamp assertions are
  never derived.
- Tables keep aligned cell-text dispositions separate from row, column, span,
  and header assertions. Formula v1 is exact projected presentation text with
  no symbolic algebra or presentation-equivalence map. Code uses approved code
  element boundaries and the projection rule above.
- Duplicate/noise units are emitted non-empty parser text elements. A duplicate
  requires exact projected text plus the same source alignment; independently
  aligned repeated source occurrences remain legitimate. Noise is an unmatched
  non-empty emitted unit. Emit IDs/counts only, with no semantic-similarity
  inference or scalar combination.
- Geometry is one approved aligned assertion/group. Emit exact integer
  intersection and union areas plus unreduced rational IoU. Zero-area or
  unresolved alignment emits a named invalid/unresolved record and no IoU.
- Caption timing uses approved cue identity/alignment and emits signed and
  absolute start/end deltas plus signed duration delta in integer milliseconds.
- Any unresolved alignment emits a named `unresolved` record and no raw value;
  it is never converted to zero, exclusion, match, or failure.

The approval authorizes deterministic contracts and focused tests only. It
does not authorize thresholds, a global score, macro/micro aggregation,
importance weights, numeric partial credit, candidate execution, independent
approval, or formal publication.

## Formal execution, offline, provenance, and store audit

| Requirement | Current repository state | Remaining classification |
| --- | --- | --- |
| Benchmark/profile binding | Diagnostic `1.0.2` / full profile `revision-003` bind the selected successor source/reference/config digests. A fail-closed formal-manifest schema now requires exact 13-case Gold, Parser registry/implementation, build, plan, image, policy, and authority digests. | `human_external_evidence_required`: exact independently approved Gold/scorer/governance/no-egress authority bindings do not yet exist, so no formal manifest instance exists. |
| Execution plan/run/collection identity | Diagnostic plan, invocation, slots, attempts, receipts, and collection revision are immutable and digest-bound. The owner-approved formal schema derives run identity from manifest/config/environment/provenance with exact compatibility. | `human_external_evidence_required`: a closure-complete formal plan/manifest cannot be instantiated before reviewed Gold and authority records exist. |
| Attempt history and terminal package | Append-only ordinals, start/terminal receipts, resume, closed-slot protection, and terminal status exist and remain the implementation to reuse. | `human_external_evidence_required`: the formal terminal binding cannot be produced before formal execution becomes eligible. |
| Result storage | Immutable local diagnostic attempts/results/collections and Q24 E2E packages exist. The minimal formal pointer reuses content-addressed local storage, requires a closure-complete manifest, and uses create-if-absent publication. | `human_external_evidence_required`: terminal/replay and authority closure are absent; publication has not run. |
| Provenance | Source/reference/config and lane lineage digests exist. The minimal provenance schema binds revision/diff, lock, Python/platform, image, launcher policy, and explicit model/seed or `not_applicable`. | `human_external_evidence_required`: exact build/image and independent approval records are absent; no equivalence or silent migration is allowed. |
| Credential/live rejection | Live/provider flags and three known credential environment names are rejected without printing values | `repository_evidence_can_close` for this diagnostic safeguard; it is not no-egress proof |
| No-egress enforcement | A thin Docker CLI launcher now creates one container with network none, read-only root, all capabilities dropped, no-new-privileges, bounded mounts/tmpfs, inspect verification, and three denied probes. A separate immutable binding joins its attestation digest to the exact manifest, run, and terminal package. Both remain independent-review-pending and non-formal. | `human_external_evidence_required`: a pinned runnable benchmark image, independent launcher review, and one genuine conformance/execution binding remain absent. |
| Replay | Sources, references, lane artifacts, renderer projection, C01 Q14 results, and full diagnostic E2E collection replay deterministically | `repository_evidence_can_close` diagnostically; complete formal replay awaits approved Parser/Gold/formal bindings |
| Formal/diagnostic separation | Full profile is diagnostic; `--formal` is rejected; diagnostics contain no authority or baseline fields | `repository_evidence_can_close` |

The minimum legitimate no-egress mechanism is an external OS/container launcher
that creates a network namespace with no egress, launches the canonical process
inside it, performs a prescribed failed outbound socket/DNS probe, and emits a
content-addressed attestation bound to the exact invocation. Before coding it,
the owner must approve the launcher/build identity, platform scope, probe
semantics, trust boundary, and how the launcher proves the namespace setting.
A mocked socket or absent credential is insufficient.

### Local no-egress capability audit

The current host is Apple Silicon macOS with Docker Desktop 4.48.0 and Docker
Engine 28.5.1 available. The repository has no application/benchmark Dockerfile
or pinned benchmark image, so Docker availability alone is not formal evidence.
`sandbox-exec` and host-wide `pfctl` are present, but they are not the recommended
boundary: the former has no repository-owned network-denial proof contract and
the latter is privileged, global, and unnecessarily invasive.

The smallest recommended contract is a repository-owned launcher around a
content-addressed Linux benchmark image and `docker run --network none`. The
launcher must also use a read-only root filesystem, drop capabilities, enable
`no-new-privileges`, avoid Docker-socket/credential/host-network mounts, expose
only explicit read-only input plus a bounded result mount, and inspect the
created container to prove `HostConfig.NetworkMode == "none"`. Inside the
container, the prescribed probe records denied DNS resolution, denied literal-
IP socket connection, and denied HTTP access. The outer launcher, not the
benchmark process alone, emits the canonical attestation binding container ID,
image digest, launcher/policy version and digest, invocation digest, exact
mount/config projection, inspect evidence, probe outcomes, and terminal package.

The approved trust boundary would therefore be the local Docker Desktop engine,
the content-addressed image/build record, and the repository launcher. This
design adds no quality threshold and does not describe provider capture as
offline. Before implementation, the owner must approve this Docker-specific
platform scope and the exact probe/attestation fields; an independent reviewer
must later verify the launcher and one genuine conformance record.

### Approved minimal formal-execution choice

Riley Lai approved `10A` on 2026-09-01 with a minimal, Docker-native,
reuse-first constraint. The implemented contract is fail-closed and local-only:

- a canonical manifest binds all 13 exact fixture/reference/configuration/Gold
  digests, the Parser registry/scorer/build digest, authority records, and one
  execution-plan digest;
- `run_id` is the SHA-256 of the canonical manifest, plan, candidate/build,
  allowlisted configuration, and execution-environment identity; attempts keep
  append-only ordinals and immutable receipts;
- provenance binds repository revision/diff state, dependency lock, Python and
  platform identity, container image digest, launcher/policy digest, and any
  model/seed field as explicit value or `not_applicable`;
- compatibility is exact and fail-closed for schema/registry/scorer/plan/image
  versions; there is no silent migration or equivalence claim;
- results remain immutable, content-addressed local artifacts. A publication
  pointer may be created only after every required terminal/replay/authority
  check succeeds, and it may never overwrite a prior publication;
- formal execution runs in the pinned Linux image through the repository
  launcher with Docker `--network none`, read-only root, dropped capabilities,
  `no-new-privileges`, no Docker socket/credential/host-network mounts, and only
  explicit read-only input plus bounded result mounts;
- the launcher verifies container inspect evidence, three denied DNS/literal-IP
  socket/HTTP probes, and emits the canonical no-egress attestation bound to the
  image, policy, invocation, mounts, inspect result, probes, and terminal
  package.

Approval authorizes implementation and tests, not a formal run. The current
runner still rejects formal execution. Independent Gold/scorer/governance and
launcher review, a pinned runnable image, and one genuine no-egress conformance
record remain required before the formal path may execute or publish.

## Milestone disposition

- **M5:** authority remains blocked; the complete case/evidence review material
  is now prepared.
- **M6:** closed. Exact five-case smoke and all 13 full-profile cases have
  diagnostic three-lane technical execution and replay. Smoke remains
  permanently non-authoritative.
- **M7:** remains blocked by the Parser decisions above; no formula was
  invented.
- **M8:** technical source/reference/packet preparation is closed; formal
  fixture and Gold authority remains blocked for all 13 cases.
- **M9:** diagnostic runner/receipt/history/store/replay readiness is closed;
  formal schemas, compatibility/publication decisions, and genuine no-egress
  evidence remain blocked.
- **M10:** blocked. No formal baseline exists.

## Shortest path to a formal characterization baseline

1. Obtain and bind Q25 independent fixture rights/privacy/provenance approval
   for the 13 owner-approved exact fixture bindings.
2. Review each source/reference pair; produce reviewed Gold with claims,
   evidence, categories, importance rationales, locators/structure, disputes,
   and adjudication.
3. Approve the Parser raw-measurement decisions, then implement and independently
   approve the versioned Parser contracts/scorer tests.
4. Freeze the minimal formal manifest/plan/provenance/store/publication and
   execution-compatibility contracts.
5. Implement and independently verify the approved OS/container no-egress
   launcher and its attestation.
6. Execute the immutable 13-case full plan, replay every applicable three-lane
   result, close Q10 authority, and publish it only as the current-
   implementation characterization baseline.

Q11 numeric calibration remains outside this path until the authoritative
baseline evidence exists.
