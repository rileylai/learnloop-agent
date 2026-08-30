# Parser & Note Completeness Benchmark Foundation

Status: Q1–Q29 foundation interview complete at the stated contract and topology boundaries; Q26 note/projection and renderer/capture seam foundation, Q28 exhaustive-coverage schema/identity/assignment/DAG/output/closure/mapping contract, Q15/Q17/Q21 per-work-unit receipt/history contract, and Q29 routing schema/decision/conformance foundation are realized  
Benchmark contract: `parser-note-completeness-v1`  
Decision status: Q1–Q11 frozen; Q12 blocking and aggregation topology frozen with evidence-dependent classifications and numeric formulas pending; Q13 non-numeric baseline-comparison and artifact topology frozen with metric-specific policy applicability, schema realization, and numeric calibration pending; Q14 deterministic-scoring and artifact topology, coverage state-vector formulas, support exact-count/non-dilution policy, and Q14-owned metric/scorer/result/aggregation schema realization are frozen in section 2.141, while metric-specific parser measurement formulas, evidence-supported aggregation selections beyond the v1 fixture vector, and numeric calibration remain pending; Q15 finite-suite repeated-run, non-inferential statistical-diagnostic, artifact, and adoption-authority topology frozen; per-work-unit owner receipt/history realization is frozen in section 2.138, while formal repeat count and scheduling, execution compatibility, diagnostic-method activation, broader schema realization, and applicable numeric calibration remain pending; Q16 smoke IDs and reference semantics, Q17 runner/exit/resume topology, Q18 offline-enforcement and provider-capture separation topology, Q19 provenance-capture topology, Q20 raw resource-observation and non-authority topology, and Q21 runner-materialization topology frozen; schema realization outside section 2.138, execution compatibility, cold/warm applicability, diagnostic resource methods, retry details not already governed by Q15, and applicable Q11 numeric ceilings remain pending under their existing owners; Q22 records nine project-owned creation plans as unapproved candidates with canonical eligibility `evidence_required`; Q23 synthetic-only Chat and Screenshot v1 fixture policy, Q24 canonical tracked/ignored-local storage and End-to-end result/attempt package realization in section 2.140, and Q25 artifact-and-scope independence and closure topology frozen; exact Q22 bytes, digests, provenance, rights/privacy evidence, independent approvals, and broader formal collection/store publication remain pending; Q26 renderer-neutral note-artifact and renderer-preservation topology plus the exact Q26-owned note/projection schema contract in section 2.135, Q27 non-compensating three-lane and two-view End-to-end gate topology, Q28 exact exhaustive-coverage schema/identity/assignment/DAG/output/closure/mapping contract in section 2.137, and Q29 deterministic pre-generation routing and forced-diagnostic separation topology frozen; Q28 work-unit sizing, overlap amount, merge algorithm, measurement/contradiction realization, and applicable numeric/evidence boundaries, plus Q14 projection/alignment/metric formulas, Q29 approved boundary evidence/configuration bindings, Q15 repeat/scheduling/statistical-method policy, and remaining provider-capacity compatibility remain pending under their existing owners  
Recorded: 2026-08-19
Branch: `feat/parser-note-completeness`

This document records frozen pre-implementation decisions for the Parser &
Note Completeness Benchmark Foundation. It does not authorize implementation,
dependency adoption, production changes, or a Step 100 retrieval decision.

The discovery evidence and initial benchmark proposal are recorded in
`01-discovery.md`.

## 1. Scope and isolation

The benchmark covers five source families through 13 canonical cases:

- PDF: `P01` through `P04`
- Web: `W01` through `W03`
- YouTube captions: `Y01` and `Y02`
- Chat text: `C01` and `C02`
- Multiple screenshots: `S01` and `S02`

This foundation must not change the current MVP default behavior. The full
benchmark is not part of default MVP CI. It runs only through an explicit
benchmark or adoption workflow. Step 100 retrieval remains separate and
deferred.

## 2. Frozen decisions

### 2.1 Benchmark authority

The current MVP result is a characterization baseline. It may fail quality
thresholds for capabilities the MVP does not support.

The benchmark infrastructure itself must pass all of the following before its
results are accepted:

- manifest validation;
- artifact and manifest digest validation;
- schema validation;
- applicable offline-enforcement conformance validation;
- deterministic replay validation;
- versioned scorer-contract validation.

Future parser, generation-flow, prompt, schema, or renderer candidates must use
the same frozen full benchmark version. They must pass preregistered absolute
floors, non-regression gates, and improvement gates. Gold, weights, and
thresholds must not be changed after candidate results are observed.

The smoke profile has no adoption authority.

### 2.2 Execution profiles

`smoke` contains exactly the logical case set `P01`, `W01`, `Y01`, `C01`, and
`S01`, one from each of the five source families. It references the same
canonical fixture revision, source bytes, snapshot digest, and compatible
dependent artifacts used by `full`. It must not create reduced or smoke-only
fixture variants. This freezes logical IDs and reference semantics, not
fixture bytes or digests that do not yet exist.

Smoke validates all applicable runner and lane wiring, artifact schemas,
scorer execution, deterministic replay, and error reporting. It does not claim
subtype coverage and has no baseline, comparison, gate, or adoption authority.

`full` contains all 13 cases. It is the only profile that can support a formal
baseline, candidate comparison, or adoption decision.

The foundation contract may be implemented before fixture annotation is
complete. Until all 13 fixtures, gold artifacts, and required reviews are
complete, the project must not claim that a formal baseline exists and must not
make an adoption decision.

### 2.3 Canonical and local fixture policy

The benchmark uses two fixture classes.

**Canonical repository fixture** is eligible for full scoring and adoption
decisions. Every canonical fixture must record:

- explicit redistribution rights or project ownership;
- original source and acquisition method;
- license or ownership evidence;
- SHA-256 digest;
- fixture version;
- privacy-review status;
- source type and language;
- expected structure and locator metadata;
- change reason and review record.

**Local diagnostic fixture** is ignored by Git and has no acceptance authority.
Private material, material with unknown redistribution rights, material
containing personal data, and personal-viewing-only material belong only in
this class. Its result must not be included in an adoption pass/fail result.

Canonical scoring is offline. Dynamically acquired web or YouTube content is
not canonical input. Formal scoring uses license-permitted, content-addressed
offline snapshots. Live acquisition may be exercised only as a
non-decision-making smoke check.

### 2.4 Candidate attachment disposition

The three supplied attachments remain candidates and must not be copied into
the repository by this design phase.

| Candidate | Potential role | Current disposition | Requirements before canonical eligibility |
| --- | --- | --- | --- |
| `Stanford AI 系統課程筆記.docx` | Source material for a generated PDF fixture | Local diagnostic only; DOCX is not a benchmark raw-source lane | Confirm authorship and redistribution rights; freeze a reproducible, versioned conversion; record conversion provenance and hash; classify the resulting fixture as PDF, not DOCX |
| `aws_genai_q4_q25_full_notes.md` | Frozen reference document for the generation lane | Candidate only | Confirm ownership, privacy, and content provenance; it cannot represent web or chat parsing without corresponding raw HTML or structured conversation evidence and locator gold |
| `Harness 实践：让 Agent 全自动制作知识讲解视频.srt` | Offline YouTube caption snapshot | Local diagnostic unless rights are established | Confirm subtitle redistribution rights, source video identity, language, timestamps, acquisition method, and permitted snapshot storage |

### 2.5 Evaluation authority boundary

An LLM must not be the formal acceptance judge.

The deterministic scorer owns:

- extraction coverage;
- structure preservation;
- reading order;
- locator checks;
- evidence-ID checks;
- duplicate and noise measurements;
- artifact and schema validation;
- resource metrics;
- scoring-contract validation;
- final pass/fail calculation from approved gold.

Semantic key points, critical evidence, claim-support mappings, and permitted
equivalent expressions must originate in human-approved gold mappings.

An LLM may propose annotation candidates, segment claims, or flag disputes. Its
output cannot directly become approved gold and cannot change scores, weights,
thresholds, or pass/fail. Items that cannot be decided deterministically and
have not been adjudicated remain `unresolved`; an LLM cannot resolve them by
guessing.

### 2.6 Gold review contract

Gold annotation uses a primary annotator and an independent reviewer. A full
second annotation of every character is not required.

The reviewer must verify:

- every critical evidence item;
- evidence importance and weight;
- claim-support mappings;
- reading order;
- locator correctness;
- exclusion and unsupported-claim rules;
- adjudication of every disputed item.

Every fixture gold artifact records:

- annotation version;
- primary annotator;
- reviewer;
- review status;
- reviewed timestamp;
- change reason;
- unresolved disputes;
- adjudication outcome.

Gold review status has at least these states:

- `draft`: usable for runner development or a clearly labeled provisional
  result, but not an adoption decision;
- `reviewed`: independently checked and eligible for an adoption decision when
  it has no blocking unresolved dispute;
- `adjudicated`: disputed items have a recorded final disposition and the gold
  is eligible for an adoption decision.

Only `reviewed` or `adjudicated` gold may support a formal adoption decision.
The reviewer must not be the same LLM that produced an annotation candidate.
Whether a human reviewer may approve LLM-assisted primary annotation remains a
separate workflow question; LLM output never receives review authority.

### 2.7 Evaluation lanes

The benchmark has three non-compensating lanes.

#### Lane 1: raw source to parser artifact

This lane evaluates parsing, OCR, ASR, layout, structure, reading order, and
locators. It uses parser-specific gates.

#### Lane 2: frozen reference document to generated notes

Every generation candidate receives byte-identical frozen input for a given
benchmark version. This lane evaluates evidence coverage, unsupported claims,
deduplication, completeness, output structure, and readability. It uses
generation-specific gates.

#### Lane 3: raw source to final rendered notes

This lane measures integration behavior and renderer loss. It is diagnostic
during the foundation phase. Before formal adoption of a candidate that affects
the end-to-end path, it must pass a separate end-to-end non-regression gate.

A high end-to-end score cannot compensate for failure in the parser or
generation lane. Likewise, aggregate results cannot silently compensate for a
blocking per-fixture or critical-evidence failure once those gates are frozen.

### 2.8 Future benchmark boundary

`NormalizedDocument v1` is a versioned benchmark boundary between parser and
generation evaluation. It is not a production runtime contract. This decision
does not change the current MVP or require runtime code to consume the format.

The artifact preserves enough source structure for later section-aware and
hierarchical long-source generation. It contains no chunks, embeddings,
retrieval scores, query relevance, `top_k`, evidence importance, expected
notes, or Step 100 retrieval behavior.

### 2.9 NormalizedDocument v1 envelope

The top-level artifact contains:

| Field | Contract |
| --- | --- |
| `schema_version` | Exact schema identifier. The first compatible line is `normalized-document/1.0.0`. |
| `artifact_role` | Closed v1 value: `parser_output` or `reference_document`. |
| `document_id` | Benchmark-manifest-assigned logical fixture identity. It remains the same across artifacts for the same source fixture. |
| `source` | Source identity, snapshot digest, source type, display name, and source-level languages. |
| `capabilities` | Availability declarations for information that a producer may not support. |
| `sections[]` | Section hierarchy and ordered element ranges. |
| `elements[]` | Source-derived content and structure in canonical document reading order. |
| `producer_provenance` | Producer identity and all scoring-relevant parser, model, and configuration provenance. |

`source.source_type` uses the five benchmark values `pdf`, `web`, `youtube`,
`chat`, and `screenshots`. This benchmark vocabulary is independent of current
runtime spellings such as `url`, `chat_text`, and `screenshot`.

`source.languages[]` is an ordered, de-duplicated list of BCP 47 language tags.
It supports bilingual and multilingual sources. `und` means the language is
unknown; `mixed` is not a language tag. Element-level `languages[]` may narrow
or refine the document declaration but must not claim a language the producer
did not determine.

`source` also records the canonical fixture ID, display name, acquisition or
snapshot identity supplied by the manifest, and `source_snapshot_sha256` over
the exact offline source bytes. URLs and video IDs may be recorded as source
identity metadata, but dynamic network content is never canonical scoring
input.

Each capability has `status` with one of:

- `available`: the producer supplies the information for every applicable
  unit;
- `partial`: the producer supplies it for only part of the applicable source;
- `unavailable`: the source may contain it but the producer did not supply it;
- `not_applicable`: the capability does not apply to the source.

`partial` and `unavailable` require a machine-readable `reason`. A human
description may supplement the reason. Missing capability declarations are
invalid; an absent field must not be interpreted as unavailable.

The minimum capability set covers hierarchy, language identification,
geometry, table structure, code metadata, source modality, and typed locators.

### 2.10 Sections, elements, and structure

A section is a navigation and planning boundary, not a copy of its content. It
contains `section_id`, optional `parent_section_id`, optional
`heading_element_id`, and inclusive start/end element-order bounds. An
unheaded document or source interval may have an unheaded section. Sections
must form an acyclic hierarchy and their ranges must be consistent with element
order.

Every element contains:

- `element_id`;
- `kind`;
- globally unique, zero-based, gap-free `order`;
- `section_id`;
- optional `parent_element_id`;
- content appropriate to its kind;
- `languages[]`;
- one or more locator records, or an explicit unavailable locator;
- applicable hierarchy, list, geometry, table, code, modality, and provenance
  metadata.

The closed v1 element-kind set is:

- `heading`;
- `paragraph`;
- `list_item`;
- `quote`;
- `code_block`;
- `table`;
- `table_row`;
- `table_cell`;
- `figure`;
- `caption`;
- `formula`;
- `transcript_segment`;
- `message`;
- `ui_text`;
- `page_break`;
- `unknown`.

`unknown` preserves observed content whose type cannot be supported; it must not
be used to guess a more specific kind.

List items record `list_kind` as `ordered` or `unordered`, a zero-based
`nesting_level`, and an `ordinal` when one exists in the source. Parent-child
links preserve nested list structure.

A table is represented as `table` -> `table_row` -> `table_cell`. Cells are the
primary carriers of table text. Table and row elements may contain structural
metadata but must not repeat the concatenated text of all descendant cells.
Cell metadata may identify row/column position, row/column span, and header
role when available.

A code block preserves the source-faithful code string as one element and may
record a source-supplied or producer-detected language hint with provenance. It
is not split into one element per line. Formulas remain distinct from code.

`parent_element_id` expresses structural containment such as list nesting,
table membership, a figure caption, or a quoted message. Source relations that
are not containment, such as a chat reply, use typed relation metadata and do
not overload the parent field.

Geometry uses a top-left origin and integer coordinates normalized to the
closed range `0..1_000_000`. The geometry record includes its coordinate-space
identity. Pixel dimensions may be retained as source metadata, but scoring uses
the normalized integer geometry. Geometry is never inferred when the producer
does not have evidence for it.

Producer provenance exists at document level and may be refined at element
level. Scoring-relevant provenance includes producer name and version, parser
or OCR/ASR model identity when applicable, configuration digest, and processing
stage or method. Volatile run facts do not belong here.

### 2.11 Stable identity and reading order

`document_id` identifies the logical benchmark fixture. `element_id` and
`section_id` are artifact-local identities, not cross-parser alignment keys.

When a canonical source locator is available, an element ID is derived
deterministically from `document_id`, the canonical source anchor, element
kind, and occurrence. When a locator is unavailable, it is derived from
`document_id`, a deterministic producer segmentation path, element kind, and
occurrence. A section ID follows the same rule using its heading anchor or
source/segmentation range.

IDs do not contain extracted text, database IDs, or transient run IDs. Correcting
OCR text therefore need not change an ID when segmentation and anchor identity
remain unchanged. Different parsers or segmentations are not expected to
produce the same IDs. Cross-artifact comparison uses locator alignment and
approved gold mappings.

Element `order` is the canonical reading order for the artifact. It starts at
zero and is unique and gap-free across the complete document. Hierarchy,
section membership, DOM order, page number, timestamp, or image index cannot
replace this field. Parser candidates are evaluated when their proposed order
differs from gold; the artifact format does not silently reorder output.

### 2.12 Typed locator contract

An element may carry multiple locator fragments when content spans source
boundaries. Each fragment declares a locator type and availability status.

| Source | Required identity when available | Optional refinement |
| --- | --- | --- |
| PDF | One-based page number | Normalized bounding box and source text offsets |
| Web | Rendered or static snapshot SHA-256 plus canonical DOM path | Node text offsets or source text span |
| YouTube captions | Video ID, caption-track identity, cue index, start and end milliseconds | Chapter or source-provided segment metadata |
| Chat | Message ID and source sequence | Thread ID, reply-to message ID, source timestamp, text span |
| Screenshots | One-based image index and image SHA-256 | Normalized bounding box and source text span |

When a locator is not available, the locator record uses
`status=unavailable` and a machine-readable reason. It must not invent a page,
DOM path, timestamp, cue, message ID, thread, image index, or geometry.

Locator comparison methods are frozen as follows:

- discrete source identities use exact comparison;
- PDF and screenshot regions use intersection-over-union (IoU);
- DOM or source text spans use normalized span overlap;
- caption timing uses start/end temporal delta;
- chat message and thread identities use exact comparison.

Numeric acceptance thresholds such as minimum IoU, minimum span overlap, and
maximum timing delta are deliberately deferred to the scoring round. They must
be preregistered from fixture evidence before candidate results are inspected.

When gold has an available locator and a candidate reports it unavailable, the
candidate unit is not covered. A locator is N/A only when the approved gold
itself records that locator as unavailable.

### 2.13 Canonical serialization and digest boundary

UTF-8 canonical JSON is the only scoring authority. YAML, pretty-printed JSON,
database rows, and in-memory object ordering are not authoritative forms.

The canonical serializer is explicitly configured:

- object keys are sorted deterministically;
- arrays preserve contract-defined order;
- output uses UTF-8 without a byte-order mark;
- JSON is compact, with no insignificant whitespace or trailing newline;
- strings retain their approved Unicode code points and are not silently NFC,
  NFKC, case, punctuation, or whitespace normalized;
- duplicate object keys, NaN, Infinity, and non-integer numeric values in the
  NormalizedDocument payload are invalid;
- JSON escaping is deterministic and non-ASCII text is emitted as UTF-8 rather
  than implementation-dependent ASCII escapes.

The serializer contract, including escaping behavior and key ordering, is part
of the schema version. A generic JSON serializer with unspecified options is
not sufficient.

`source_snapshot_sha256` covers the exact canonical offline source bytes.
`normalized_document_sha256` covers the complete canonical
NormalizedDocument payload, including schema, role, source identity,
capabilities, content, structure, locators, and scoring-relevant producer
provenance.

Run ID, creation time, hardware, latency, memory, and cost belong only in the
run receipt and do not affect the NormalizedDocument digest. The artifact does
not embed its own digest; its digest is bound by the manifest.

Source snapshot, NormalizedDocument, gold, reference document, candidate
output, run receipt, and manifest each retain a separate digest. The manifest
binds the relevant digests into one benchmark execution identity.

### 2.14 Versioning, revisions, and compatibility

The contracts are versioned independently:

- schema: `normalized-document/1.0.0`;
- benchmark dataset: `parser-note-completeness/1.0.0`;
- each fixture: its own fixture version;
- each gold artifact: its own annotation version;
- scorer: an independent scorer-contract version.

Schema versions use these rules:

- major: a required field, field meaning, identity rule, or locator semantic is
  changed incompatibly;
- minor: an optional field is added without changing existing semantics;
- patch: documentation is clarified without changing serialized or scoring
  behavior.

Benchmark versions use these rules:

- patch: a fixture, gold, review record, or annotation error is corrected;
- minor: cases or cohorts are added without redefining existing case identity;
- major: case identity, gold ontology, weights, or adoption semantics change.

Any scoring-relevant correction creates a new immutable version, manifest, and
digest. Existing artifacts remain available for audit and are never edited in
place.

Baseline and candidate results are directly comparable only when schema,
benchmark, fixture, gold, and scorer versions all match. After a scoring-
relevant revision, every baseline and candidate in the comparison must be
rerun or replayed under the new complete version set.

A runner accepts only an explicit allowlist of schema versions and fails closed
on unknown versions. A new reader may explicitly support older artifacts. An
old reader is not required to accept a newer minor version automatically.
There is no silent coercion. Any converter has its own version, provenance,
configuration digest, input digest, and output digest.

### 2.15 Frozen reference document

The generation lane uses option C: a human-approved, source-faithful
`NormalizedDocument` with `artifact_role=reference_document`.

It is constructed from the canonical source and reviewed independently of any
candidate parser. It preserves the complete source-faithful text, structure,
reading order, and available locators needed by the benchmark. It is not the
gold answer and must be stored separately from gold.

The reference document must not contain evidence importance, expected notes,
claim mappings, acceptance weights, preferred wording, or other answer-bearing
gold fields. This prevents the generation candidate from receiving the answer
key as input.

For a scanned PDF, the reference may contain a human-approved page
transcription. For the YouTube lane, the canonical source is the caption
snapshot: the reference must faithfully preserve that snapshot's text, cues,
and timing even when the captions are automatically generated. It must not
secretly correct captions from video audio. A future audio/ASR benchmark is a
separate, explicitly versioned benchmark.

Every generation candidate receives byte-identical reference-document bytes
and the same digest. Candidates may create their own prompt projection,
section plan, or intermediate evidence artifacts, but each derived artifact
has a separate digest and provenance. A candidate must process all applicable
sections; retrieval or `top_k` must not be used to omit sections.

### 2.16 Plain-language decisions and trade-offs

1. **The benchmark gets a richer document than production has today.** Current
   production mostly stores one flat string. The benchmark needs structure and
   locators to identify where loss begins. The trade-off is a larger annotation
   contract, but no production migration is required now.
2. **IDs are stable inside one artifact, not magical cross-parser identities.**
   This prevents text corrections from needlessly changing every ID while
   avoiding the false claim that two parsers segmented the source identically.
   Cross-parser alignment therefore requires locators and gold mappings.
3. **Missing information is explicit.** `partial`, `unavailable`, and
   `not_applicable` prevent unsupported geometry, language, or structure from
   being fabricated. The trade-off is stricter validation and more verbose
   artifacts.
4. **Canonical JSON is deliberately strict.** Separate, deterministic digests
   make replay and audit trustworthy. The trade-off is that ordinary JSON dumps
   are insufficient and volatile run measurements must live elsewhere.
5. **Corrections create new versions.** This costs additional baseline and
   candidate replays, but prevents benchmark rules or gold from changing after
   results are known.
6. **Generation reads a human-approved source representation, not parser
   output.** This costs annotation effort but cleanly measures generation
   quality. Keeping gold answers separate prevents answer leakage.

### 2.17 Gold artifact responsibility boundary

Q6 is frozen. A gold artifact is separate from the source snapshot,
`reference_document`, parser output, candidate output, and candidate-specific
generated-claim map.

The gold artifact owns these source-side records:

- `source_references[]`;
- `structure_assertions[]`;
- `locator_assertions[]`;
- `evidence_items[]`;
- `expected_claims[]`;
- `source_exclusions[]`;
- annotation and review metadata already required by the gold review contract.

The reference document remains source-faithful. It does not contain semantic
importance, expected claims, claim-support mappings, exclusions, or scoring
answers. Gold may cite its artifact-local element IDs and typed locators, but
must not modify, correct, or supplement source content.

IDs are namespaced by record type and gold artifact. A gold `evidence_id` is
not a `reference_document.element_id`, parser element ID, structure assertion
ID, locator assertion ID, expected claim ID, or generated claim ID.

### 2.18 Source references

A `source_reference` points from gold to source-faithful content in the frozen
reference document. It has exactly one of two modes:

- `whole_element`: cites one complete reference-document element;
- `text_range`: cites a non-empty substring within one element.

A `text_range` uses a Unicode code-point half-open interval `[start, end)` over
the exact original string stored in the referenced element. It must satisfy
`0 <= start < end <= text length`. Offsets are computed without NFC, NFKC, case,
whitespace, punctuation, or any other normalization.

One range cannot cross an element boundary. Evidence spanning multiple
elements uses multiple source references. Gold does not store a second
authoritative copy of cited source text. A display excerpt is derived from the
frozen reference document and is not scoring authority.

The future implementation must include supplementary Unicode character cases
so code-point offsets are not confused with JavaScript UTF-16 code-unit
indices. Offset interpretation is part of the versioned gold contract.

### 2.19 Structure and locator assertions

A `structure_assertion` records an approved source-structure fact independently
from source text. Its predicate comes from a closed, versioned set. The v1
predicate families cover:

- element kind and structural containment;
- section membership and section hierarchy;
- canonical document order;
- immediate adjacency;
- explicitly annotated, semantically important cross-element order;
- list kind, nesting level, and ordinal;
- table row/column position, span, and header role;
- caption-to-figure relation;
- chat reply and thread membership;
- cross-element or cross-image continuation.

Canonical reading order is represented once as the approved order sequence.
Adjacency is recorded where needed, and important non-adjacent order constraints
may be asserted explicitly. Gold must not materialize all possible pairwise
order relations.

A `locator_assertion` independently records the approved typed locator,
locator availability, or locator relationship for referenced source content.
Locator correctness is not encoded as a structure predicate.

Parser-lane scoring may compare parser artifacts directly with structure and
locator assertions. Generation-lane scoring uses them only when an evidence
item explicitly references a structure or locator fact that itself carries
meaning. Merely preserving prose does not grant structure credit, and structure
is not automatically treated as semantic evidence.

### 2.20 Evidence items and expected claims

An `evidence_item` is the smallest semantic proposition for which support can
be judged independently while retaining its complete truth conditions. It is
not automatically a paragraph, sentence, list item, table row, formula, or code
block.

Atomic evidence may cite one or more source references, structure assertions,
and locator assertions. Conditions, negation, exceptions, subject, viewpoint
attribution, time, quantities, units, and uncertainty must remain attached when
they are necessary for the proposition to remain true. Atomicity must not turn
a qualified source statement into a stronger unqualified statement.

Examples of valid structured evidence boundaries include:

- one table cell when that cell independently states a value;
- several cells when row/column labels are required to interpret the value;
- a formula together with its definition or applicability condition;
- code together with source text that explains what the code demonstrates;
- multiple transcript or chat elements when speaker attribution or context is
  required for the proposition.

An `expected_claim` is a distinct gold record describing content that a
complete note is expected to communicate. It is supported by one or more
evidence items. Evidence answers “what the source supports”; an expected claim
answers “what the note is expected to express.” The two record types must not
be merged.

The exact all-of/any-of support logic, paraphrase mappings, partial-coverage
states, contradiction representation, and repeated-evidence rules remain Q8
decisions. Importance semantics remain a Q7 decision. Reference documents
contain none of these semantic annotations.

### 2.21 Candidate-specific generated claim map

A `generated_claim` is the smallest assertion in candidate output that can be
independently judged for source support. Sentence and list-item boundaries are
deterministic initial validation units, not guaranteed claim boundaries.

The formal process is:

1. Apply a versioned deterministic initial segmentation to candidate output.
2. Identify only ambiguous compound units that cannot be safely treated as one
   independently supportable assertion.
3. Review the boundaries of those units without showing the reviewer the
   candidate's aggregate score or allowing score-driven segmentation changes.
4. Freeze a candidate-specific generated-claim map with its own version,
   provenance, and digest.
5. Replay matching and scoring deterministically from that frozen map.

Every generated claim retains the candidate output path and an exact source
span into the original candidate output string. Candidate-provided `claims[]`
may be retained as a segmentation suggestion but has no authority over the
formal claim count or denominator.

An LLM may propose claim boundaries. It cannot approve them. A boundary that
remains indeterminate is marked `unresolved` and follows the frozen Q10 policy.

The generated-claim map is a candidate-specific derived artifact, not gold.
Candidate output-side `presentation_only` classification also belongs in this
map. It may classify headings, labels, citations, or formatting fragments as
non-claims, but it must not hide an unsupported or contradicted semantic
assertion.

### 2.22 Source-side exclusions

Gold contains source-side exclusions only. The closed v1 classes are:

- `source_noise`;
- `duplicate_occurrence`;
- `out_of_scope`;
- `unscorable`, but only after it is processed under the frozen Q10 policy.

Each exclusion has a unique ID, cited source reference or source-side
assertion, affected lane, affected named denominator, machine-readable reason,
review state, and applicable version. Exclusions are explicit and auditable;
they cannot be silently embedded in scorer code.

`source_noise` may be excluded from an extraction-coverage denominator. If a
candidate parser emits that content, the same output may still count toward
the parser noise metric.

`duplicate_occurrence` must point to the retained canonical evidence item. A
repetition is not excluded when recurrence itself carries meaning, but the
semantic rule for such recurrence remains part of Q8.

`out_of_scope` must cite a preregistered scope-rule ID. It cannot be created
after candidate output is inspected merely because content was missed.

`unscorable` starts as an unresolved item. It becomes excludable only when Q10
allows that disposition and the required review or adjudication is recorded.

Candidate output-side `presentation_only` is not gold and is not a source
exclusion. Unsupported or contradicted candidate content cannot be removed by
any exclusion classification. An exclusion affects only its explicitly named
lane and denominator.

### 2.23 Q6 plain-language decisions and trade-offs

1. **Gold points to source text instead of copying it.** This prevents two
   competing versions of the source. Exact code-point offsets are reliable but
   require careful handling across Python and UTF-16-based environments.
2. **Text, structure, and location are separate facts.** A parser may recover
   the words while losing table position or page location. Separate assertions
   expose that loss, at the cost of more annotation records.
3. **Evidence and expected claims do different jobs.** Evidence preserves what
   is true in the source; expected claims specify what complete notes should
   communicate. Keeping both avoids equating source volume with note
   requirements.
4. **Atomic does not mean sentence-sized.** A table value may need its headers,
   and a warning must retain its condition. This improves truthfulness but
   requires annotators to reason about complete truth conditions.
5. **Candidates cannot choose their own claim denominator.** Deterministic
   segmentation is reviewed only where compound claims are ambiguous. This is
   more expensive than punctuation splitting, but prevents score gaming and
   supports exact replay after the map is frozen.
6. **Exclusions remain visible and narrow.** Noise can leave coverage without
   disappearing from the noise metric, and output-side formatting cannot hide
   unsupported claims. This makes scoring stricter but auditable.

### 2.24 Evidence content categories

Q7 is frozen. Category and importance are independent dimensions:

- category states the role that source content plays;
- importance states the impact of omitting, reversing, or misstating an
  expected claim.

Every evidence item has exactly one `primary_category` and zero or more
`additional_categories`. The primary category is the most specific and
principal content role. `core_concept` is used only when no more precise v1
category applies and the evidence is genuinely a core source proposition; it
must not become a general catch-all.

The closed v1 category enum, in canonical serialization order, is:

1. `background_context`
2. `definition`
3. `core_concept`
4. `mechanism`
5. `procedure`
6. `quantitative_result`
7. `condition`
8. `limitation`
9. `exception`
10. `risk`
11. `example`
12. `counterpoint`
13. `conclusion`
14. `recommendation`
15. `uncertainty`
16. `contradiction`
17. `open_question`
18. `attribution_context`

`recommendation` means an action the source recommends. `conclusion` means a
result or conclusion the source reaches. `counterpoint` is a different or
opposing view that need not be logically incompatible; `contradiction` records
claims that cannot both hold or a contradiction explicitly identified by the
source.

`attribution_context` is limited to background such as author, speaker,
occasion, study setting, or test environment. When viewpoint attribution,
source subject, or uncertainty wording changes a proposition's truth
conditions, it remains inside evidence semantics and cannot be relegated to
optional attribution context.

Additional categories are de-duplicated and serialized in the frozen enum
order. They do not create additional evidence items, expected claims,
importance assignments, scoring units, or scores.

The presence of a number does not imply `quantitative_result`. Thresholds,
versions, step numbers, and units are classified by their actual role while
remaining part of the proposition's truth conditions.

### 2.25 Fixture-level category applicability

Each fixture's approved gold contains a category-applicability audit summary.
For every v1 category it records exactly one of:

- `present_and_required`: at least one evidence item in the category
  participates in a formal expected claim;
- `present_but_optional`: the source contains evidence in the category, but it
  does not form an independently required expected claim and may be used only
  as context;
- `not_present`: reviewed annotation found no evidence in the category;
- `not_applicable`: a preregistered scope rule makes the category inapplicable.

This fixture-level summary audits coverage of the ontology. It does not replace
item-level evidence-to-claim mappings. A category marked
`present_and_required` may still contain other optional evidence; it does not
make every item in that category mandatory.

`not_applicable` requires a scope-rule ID and should be rare. Absence of content
is normally `not_present`, not `not_applicable`. Candidate output cannot change
applicability.

A condition, limitation, exception, risk, uncertainty, or contradiction that
changes a required claim's truth conditions, decision meaning, process
correctness, or safety must be retained in a formal claim/support mapping. It
cannot be made optional merely because it is not the source's headline
conclusion.

### 2.26 Importance ownership and support roles

Formal importance exists only as `expected_claim.importance`, with one of
`critical`, `major`, or `minor`. Evidence items do not hold a second importance
value.

Evidence items retain categories, complete truth conditions, source
references, source support, and any referenced structure or locator
assertions. A claim-to-evidence relation has one support role:

- `required`;
- `alternative`;
- `context`.

The formal all-of/any-of semantics for alternatives remain a Q8 decision. If
omitting context would change a claim's truth, qualification, viewpoint
attribution, or certainty, that evidence is `required`, not `context`.

One evidence item may support multiple genuinely distinct claims. One claim
may have multiple evidence items and categories. Neither relationship creates
additional scoring units automatically. If an expected-claim category view is
stored, it is a deterministic, verifiable derivation from its evidence
relations and cannot become a second independently editable category
authority.

### 2.27 Importance semantics

Importance is determined only by the counterfactual impact of omitting,
reversing, or misstating the expected claim. Category, visual prominence,
source length, paragraph count, and repetition do not determine importance.

`critical` means that omission, reversal, or misstatement would materially
distort at least one of:

- the source's core thesis;
- its main conclusion or decision;
- a principal process and its correct execution;
- a necessary prerequisite or important negation;
- a core limitation or key exception;
- material safety or risk meaning.

`major` means that the main thesis remains recognizable, but omission leaves a
substantive gap in understanding the source's concepts, mechanisms,
procedures, results, or argument.

`minor` means that the claim adds background, an example, an extension, or
another lower-impact detail whose omission does not change core understanding,
although retaining it improves completeness, usefulness, or readability.

Examples:

- A source says that human acceptance is required before a Notion append. The
  requirement is `critical` because omitting it reverses the write-safety
  boundary; its category does not make it critical automatically.
- A source explains why section-aware processing reduces middle-section loss.
  That mechanism may be `major`: the recommendation remains identifiable, but
  the explanation has a substantive gap if omitted.
- A source provides a second, redundant low-impact illustration of an already
  established procedure. It may be `minor` if the procedure remains fully
  understandable without it.
- An `example` can be `critical` when it is the decisive counterexample that
  overturns the source's main assumption. A `quantitative_result` can be
  `minor` when its number is incidental to the argument.

There is no `unscored` or `context_only` importance. Every expected claim has
one of the three importance values. Content that need not form an expected
claim remains optional/context evidence or follows the existing
exclusion/unresolved contracts.

### 2.28 Anti-duplication and source-length-bias rules

Importance must not depend on source length, evidence count, paragraph count,
element count, or occurrence frequency.

Repeated occurrences of the same meaning form one canonical evidence item.
Other occurrences are retained as additional source references or linked
through `duplicate_occurrence`. Repetition alone does not create an additional
expected claim. Whether repetition itself carries new meaning remains a Q8
decision.

An evidence item is not restricted to supporting one expected claim. Multiple
claims are justified only when they represent different truth conditions that
can be independently omitted, reversed, and supported. Annotators must not
split one complex proposition merely to create more claims.

A qualifier that is necessary for the original proposition remains within the
same expected claim or a `required` support relation. It does not become a
separate, repeatedly countable claim. Multiple categories, evidence items, or
source occurrences never increase claim count by themselves.

There is no fixed maximum number of critical claims. Reviewers must check for:

- `critical_inflation`;
- `over_segmentation`;
- `under_segmentation`;
- `duplicate_claim`;
- `category_omission`.

A numerically dense critical set will require an additional review trigger,
but the numeric trigger remains with Q12 evidence and Q11 calibration. Q14
forbids importance weights in v1 and freezes metric-specific aggregation
selection without choosing an unsupported macro or micro formula.

### 2.29 Importance audit and review contract

Every expected claim retains this importance audit record:

- `importance`;
- `importance_rationale`;
- `primary_impact_reason`;
- zero or more `additional_impact_reasons`;
- the verifiable derived category view;
- supporting evidence IDs and their support roles;
- `assigned_by` and assignment timestamp;
- `reviewed_by` and review timestamp;
- review status;
- dispute record or an explicit `none`;
- adjudication outcome or `not_required`;
- optional LLM-suggestion provenance.

The closed impact-reason enum, in canonical order, is:

1. `core_meaning_distortion`
2. `conclusion_or_decision_change`
3. `process_correctness`
4. `safety_or_material_risk`
5. `truth_condition_loss`
6. `substantive_understanding_gap`
7. `supplementary_value`

There is one primary impact reason and zero or more de-duplicated additional
impact reasons serialized in enum order. Multiple reasons support audit only;
they do not increase weight or create scoring units.

`importance_rationale` is a reviewable counterfactual statement: it explains
what would happen to understanding, decision-making, process correctness, or
risk if the claim were omitted, reversed, or misstated. “This looks important”
is not a valid rationale.

Every assignment requires a primary human annotator and a different independent
human reviewer. Every critical claim requires explicit claim-level approval.
The reviewer checks category applicability, atomicity, required qualifiers,
duplicate claims, and critical inflation. The reviewer must not see candidate
scores before approving or changing importance.

Disputed importance follows Q10 and has no adoption authority until resolved.
An LLM may propose category or importance candidates and retain suggestion
provenance. It cannot be `assigned_by` or `reviewed_by`, change a denominator,
or determine formal importance.

### 2.30 Q7 plain-language decisions and trade-offs

1. **Category says what a claim does; importance says what happens if it is
   lost.** A number is not automatically important, and an example is not
   automatically minor.
2. **Evidence carries source meaning; expected claims carry importance.** This
   prevents the same content from being weighted once as evidence and again as
   a claim.
3. **Applicability is a pre-candidate audit, not a candidate choice.** Optional
   content remains visible, while a material limitation or uncertainty cannot
   disappear just because it is inconvenient to summarize.
4. **Longer sources do not win by having more annotations.** Repeated meaning,
   extra categories, and multiple supporting spans do not multiply claims.
   Distinct claims require independently testable truth conditions.
5. **Critical has a high bar but no arbitrary quota.** This avoids both
   critical inflation and a fixed cap that could hide several genuine safety
   conditions.
6. **Importance remains human-reviewed and auditable.** Counterfactual reasons
   make the judgment inspectable, while numeric weights and aggregation remain
   deferred to the scoring round.

### 2.31 Acceptable-paraphrase pipeline

Q8 is frozen. Acceptable paraphrase uses four layers:

1. The expected claim's frozen semantic components and truth conditions are
   normative authority.
2. Gold may include a finite set of human-approved paraphrase examples as
   positive regression anchors.
3. A versioned deterministic matcher handles only cases that explicit rules
   can prove.
4. Ambiguous cases enter a candidate-specific human-reviewed claim-to-gold
   mapping artifact.

Paraphrase examples are not a complete allowlist. A candidate cannot be
rejected merely because its faithful wording is absent from those examples.
Lexical similarity is not proof of semantic equivalence. The deterministic
matcher must abstain when its rules cannot prove a decision; it must not force
a semantic match.

An acceptable paraphrase preserves every required condition, negation,
exception, quantity, unit, time/scope, attribution, and uncertainty component.
An LLM may suggest a mapping but cannot approve it. The human matching reviewer
must be blind to candidate identity and aggregate score when deciding or
changing ambiguous mappings.

Any scoring-relevant change to gold semantic components or approved paraphrase
anchors follows the immutable revision policy. Candidate-specific reviewed
mappings do not modify gold.

### 2.32 Coverage and source-support states

Expected-claim coverage and generated-claim source support are separate,
non-compensating dimensions. Primary states are mutually exclusive within a
dimension but may coexist across dimensions.

Expected-claim coverage has exactly one of:

- `fully_covered`: all required semantic components are correctly conveyed;
- `partially_covered`: at least one non-subject required component is correct,
  while at least one other required component is missing or unsatisfied;
- `not_covered`: no non-subject required component is correctly conveyed, or
  the candidate merely mentions the topic;
- `unresolved`: the formal mapping decision remains unresolved.

Generated-claim source support has exactly one of:

- `supported`: the complete claim is supported without expanding its truth
  conditions;
- `partially_supported`: one indivisible truth condition contains both
  supported and unsupported parts, without a more specific contradiction or
  overstatement classification;
- `unsupported`: the substantive claim has no approved source support and no
  directly incompatible approved evidence;
- `contradicted_by_source`: the claim is directly incompatible with approved
  source evidence;
- `overstated`: the claim expands source certainty, scope, frequency,
  generality, attribution, or resolution status;
- `unresolved`: source support cannot yet be formally determined.

Support-state precedence is:

1. `contradicted_by_source`;
2. `overstated`;
3. `partially_supported`;
4. `unsupported`.

`partially_supported` must not hide under-segmentation. If a generated unit
contains independently judgeable supported and unsupported assertions, Q6
claim segmentation must split them. The state is reserved for a single truth
condition that cannot reasonably be decomposed further.

One expected claim may be jointly covered by multiple generated claims. One
generated claim may link to multiple genuinely distinct expected claims.
Coverage and support remain separate authority records rather than being
copied onto every link.

### 2.33 Semantic components and partial coverage

Each expected claim uses the closed v1 semantic-component kind set:

- `subject`;
- `predicate_action`;
- `object_value`;
- `condition`;
- `negation`;
- `exception`;
- `quantity`;
- `unit`;
- `time_scope`;
- `environment_population_scope`;
- `attribution`;
- `uncertainty_modality`;
- `consequence`;
- `comparison_baseline`;
- `relation`;
- `technical_literal`.

Each component records `component_id`, kind, requirement, a human-approved
semantic constraint, applicable evidence/source references, and review
metadata. Requirement is `required`, `optional`, or `not_applicable`.

`fully_covered` requires every required component to be correct.
`partially_covered` requires at least one correct non-subject required component
and at least one missing or unsatisfied required component. Mentioning only the
subject or topic is `not_covered`. Missing optional components does not prevent
full coverage.

If a candidate actively states an incorrect optional detail, that generated
claim still receives a source-support decision. Optional does not mean a
candidate may invent it safely.

A `not_applicable` component is audit-only. It has no semantic value or
evidence IDs and does not enter matching. A wrong quantity, unit, negation,
condition, or technical literal makes the component unsatisfied and also
triggers the applicable generated-claim support failure.

Components are explanation and replay units. They do not create additional
expected claims, importance values, or scoring units. Q14 v1 forbids numeric
partial credit, coverage points, weighted sums, and a combined coverage scalar.

### 2.34 Normative evidence-support expression

Every expected claim has exactly one normative support-expression root. The
closed v1 expression nodes are:

- an evidence-ID leaf;
- `all_of`;
- `any_of`.

Required evidence enters an evidence leaf or `all_of`. Alternative evidence
forms `any_of`. Context evidence does not enter the expression and cannot
independently satisfy it. Context that changes truth conditions must be
reclassified as required under Q7.

Q7 support-role labels remain the readable relation view. The validator must
prove they are consistent with the normative expression. A disagreement
between role labels and the expression fails closed; it is never silently
coerced.

Finite nesting is allowed so a claim can require, for example,
`all_of(A, any_of(B, C))`. The expression is a finite acyclic tree. Every
operator has at least two children, nested operators of the same kind are
flattened, and duplicate children are invalid. Children use canonical ordering
under the frozen serializer so equivalent expressions produce identical
bytes.

V1 has no `at_least_k`, probability, numeric threshold, or weight operator.
The expression may encode only a human-approved faithful synthesis. Combining
evidence must not add a conclusion the source did not make.

### 2.35 Counterpoints and contradictions

Gold source relations distinguish:

- `counterpoint_to`: different or opposing views that may both be valid;
- `contradicts`: source propositions whose complete truth conditions cannot
  hold together.

Contradiction review compares subject, time, scope, environment, attribution,
and every other relevant truth condition. Surface wording differences alone do
not establish contradiction.

A source relation preserves both evidence sides, their attribution and
locators, and source resolution status:

- `resolved`;
- `unresolved`;
- `not_stated`.

`unknown` is not a source resolution status. If an annotator cannot determine
the status, the annotation itself is unresolved and follows Q10. When the
source resolves a contradiction, gold also cites the source's resolution
evidence.

Candidate-internal contradiction is a candidate-specific derived relation.
`contradicted_by_source` remains the support state of one generated claim.
Neither is stored as a gold source contradiction.

When a candidate states only one side of an unresolved source contradiction,
that generated claim may be `supported` while the contradiction-preserving
expected claim is `partially_covered`. If the candidate presents its chosen
side as a settled conclusion, the generated claim is `overstated`. The two
dimensions coexist and do not compensate for each other.

No contradiction is inferred by a scorer from textual dissimilarity. It must
come from approved gold or a reviewed candidate-specific mapping.

### 2.36 Epistemic facets and preservation

Epistemic meaning is represented by separate facets rather than one assumed
linear certainty scale.

`uncertainty_modality` has at least:

- `possible`;
- `probable`;
- `unqualified_assertion`;
- `explicitly_certain`.

An unhedged assertion is not automatically explicit certainty. Attribution,
observation scope, recommendation status, resolution status, negation, and
condition remain distinct facets or semantic components.

The preservation rules are:

- possible written as certain is `overstated`;
- a result observed only in a limited environment written as universal is
  `overstated`;
- an attributed opinion written as source-wide fact is `overstated`;
- a recommendation written as verified fact is `overstated`, unless directly
  incompatible source evidence makes `contradicted_by_source` take precedence;
- reversal of an explicit negation is normally `contradicted_by_source`;
- removal of a truth-defining condition or attribution makes the expected
  claim incomplete and may also create overstatement;
- weakening an explicitly certain source conclusion does not add an
  `understated` primary support state. Support may remain `supported`, coverage
  becomes `partially_covered`, and the map records an
  `epistemic_understatement` flag.

Overstatement is a source-support failure. Understatement is primarily a
coverage loss. The distinction prevents a logically weaker but incomplete
statement from being mislabeled as fabricated.

### 2.37 Repeated and recurrence evidence

Repeated identical meaning produces one canonical evidence item. Other
occurrences remain additional source references or `duplicate_occurrence`
links. Text repetition alone does not prove importance, agreement, trend, or
emphasis.

A separate recurrence evidence item is allowed only when repetition adds a
human-approved truth condition. The closed v1 recurrence kinds are:

- `explicit_frequency`;
- `temporal_trend`;
- `cross_source_agreement`;
- `speaker_consensus`;
- `explicit_emphasis`.

Recurrence evidence cites the canonical evidence, every occurrence reference,
source or speaker identities and independence, applicable time/order data, the
recurrence proposition, and a human rationale. Independence is explicitly
recorded rather than inferred from different surface strings.

`explicit_emphasis` requires a source cue or approved human rationale. It is
not inferred from occurrence count. One recurrence item represents the whole
frequency, trend, agreement, consensus, or emphasis meaning; occurrences do
not each create claims or scoring units. Recurrence evidence does not
automatically increase expected-claim importance.

### 2.38 Candidate-specific claim-to-gold match artifact

The match artifact is candidate-specific, versioned, content-addressed, and
unable to modify gold. It contains four normalized record sets.

`claim_links[]` records:

- `generated_claim_id` and `expected_claim_id`;
- matched evidence IDs;
- satisfied, missing, and incorrect components;
- support-expression path and result;
- decision origin and review metadata.

`expected_claim_coverage_results[]` contains exactly one record for every
expected claim:

- one primary coverage state;
- contributing generated-claim IDs;
- component summary;
- unresolved or dispute record.

`generated_claim_support_results[]` contains exactly one record for every
semantic generated claim:

- one primary support state;
- matched evidence IDs;
- epistemic and contradiction flags;
- unresolved or dispute record.

`candidate_relations[]` records candidate-internal contradiction and other
candidate-side relations.

Coverage state is authoritative only in
`expected_claim_coverage_results[]`. Support state is authoritative only in
`generated_claim_support_results[]`. Neither is duplicated across links as
multiple editable authorities.

Every deterministic decision records matcher rule ID and version. Every
ambiguous semantic decision records human review authority. The artifact binds
the versions and digests of candidate output, generated-claim map, gold,
reference document, schema, and scorer.

The reviewer must not inspect aggregate score or candidate identity before
changing an ambiguous mapping. An LLM cannot approve a mapping or act as the
formal judge. Unresolved items follow Q10 and are not excluded by Q8.

A mapping correction creates a new artifact version and digest. A gold change
follows Q4 and requires all directly compared results to be rerun or replayed
under the new version set.

### 2.39 Q8 plain-language decisions, trade-offs, and examples

**Paraphrase** asks whether different words preserve the same required meaning.
Gold examples help, but truth conditions are the authority and uncertain cases
receive blind human review.

**Coverage** asks whether the candidate conveyed everything an expected claim
requires. **Source support** asks whether each claim the candidate actually
wrote is supported by the source. A note can be incomplete without inventing
anything, or comprehensive-looking while adding unsupported claims.

Examples:

- **Full coverage:** Source says “In the 16 GB test environment, latency fell
  by 20%.” Candidate preserves the environment, metric, direction, amount, and
  observed scope. Coverage is `fully_covered`; support is `supported`.
- **Partial coverage:** Candidate says only “Latency fell by 20%,” omitting the
  required 16 GB environment scope. Coverage is `partially_covered`; the
  generated claim may be `overstated` because it broadens the observation.
- **Unsupported:** Candidate says “The change reduced infrastructure cost,”
  while the source contains no cost claim and no direct opposite claim.
  Support is `unsupported`.
- **Overstated:** Source says the change “may improve latency”; candidate says
  it “always improves latency.” Support is `overstated`.
- **Contradiction:** Source says “Do not enable X below 8 GB”; candidate says
  “Enable X below 8 GB.” Support is `contradicted_by_source`.

The trade-off is deliberate: deterministic replay requires more explicit
components, relations, and reviewed artifacts. In return, lexical similarity,
candidate-controlled claim boundaries, or an LLM judge cannot silently decide
semantic correctness.

### 2.40 Normalization responsibility layers

Q9 is frozen. Normalization and alignment use three separate layers:

1. `authoritative_raw` is the immutable source string in a
   `NormalizedDocument` or candidate output. Every Unicode code-point span
   continues to point to this layer.
2. `comparison_projection` is a deterministic derived view produced by a
   closed, versioned profile. It removes only presentation differences that
   the profile can prove do not change meaning.
3. `reviewed_semantic_mapping` handles translation, paraphrase, Traditional or
   Simplified Chinese rewriting, and other equivalence that presentation rules
   cannot prove. It follows the Q8 human-reviewed mapping contract.

Normalization never edits source, reference, parser, or candidate artifacts in
place. Raw and projection digests are separate. A projection cannot change a
Q6 source-reference identity, replace raw text as span authority, alter gold
truth conditions, or grant parser credit for content or structure that the
parser did not preserve.

Every projected code point is traceable to one or more authoritative raw
ranges. Deletions, merges, and expansions remain explicit. If a safe projection
or complete offset provenance cannot be established, the deterministic process
must `abstain`.

`abstain` means only that an automatic rule cannot decide. It is not an error,
match, mismatch, zero score, or exclusion. It creates a named unresolved record
whose formal disposition follows the frozen Q10 authority policy.

### 2.41 Closed normalization profiles

V1 has six profiles:

- `natural_language`;
- `quantity_unit`;
- `technical_literal`;
- `identifier`;
- `code`;
- `formula`.

A table cell uses the profile appropriate to its approved content type. Table
row, column, header, span, and position remain structure assertions rather than
text normalization.

Every profile freezes its allowed and forbidden operations, operation order,
rule IDs and versions, offset-map requirements, and abstention conditions. The
profile and protected span boundaries are selected by approved gold component,
reference element type, or preregistered span classification before candidate
results are inspected. A candidate cannot select its profile.

Profile spans may not overlap ambiguously. A mixed element may contain adjacent
spans with different profiles, but each authoritative code point belongs to one
approved comparison profile for a given operation. Unclear boundaries require
abstention; the scorer must not choose the most favorable profile after seeing
candidate output.

### 2.42 Natural-language presentation operations

The `natural_language` profile may apply these operations in frozen order:

1. Remove one Unicode BOM only when it occurs at the true beginning of the
   complete authoritative artifact. A BOM-like character at an arbitrary span
   boundary is not removed.
2. Project CRLF and CR line endings to LF.
3. Apply Unicode canonical composition NFC within an approved natural-language
   span. NFKC and NFKD are forbidden.
4. Project NBSP to an ordinary space within an approved natural-language span.
5. Remove line-ending horizontal whitespace within that span.
6. Collapse consecutive horizontal prose whitespace to one space.
7. Project a line break to a space only when source layout metadata proves it
   is a soft prose line break. Paragraph boundaries remain boundaries.
8. Project only an explicit finite set of paired prose quotation marks to a
   common comparison form.
9. Case-fold ordinary English prose only where approved span classification
   establishes that case carries no meaning.
10. Ignore a purely typographic Chinese-Latin prose boundary space only within
    approved natural-language spans.

None of these operations may cross into `quantity_unit`, `technical_literal`,
`identifier`, `code`, or `formula` spans. Quote conversion applies only to
recognized paired prose quotes. It must not rewrite apostrophes, prime marks,
unit symbols, minus signs, or isolated quote-like glyphs.

The profile forbids global NFKC, deleting all punctuation, general zero-width
character removal, confusable-character replacement, and unrestricted
fullwidth/halfwidth conversion. ZWJ, variation selectors, and other internal
zero-width characters are retained unless an explicit safe rule exists;
otherwise comparison abstains. Fullwidth ASCII may be projected only through
an enumerated profile-specific pair, never through generic compatibility
normalization.

Minus, decimal point, percent, slash, colon, underscore, hyphen, parentheses,
and similar symbols may be semantic. Natural-language projection cannot be
used to compensate for lost paragraphs, line structure, list/table structure,
or other parser structure errors.

### 2.43 Chinese, English, and mixed text

Chinese comparison does not depend on whitespace tokenization. English
case-folding applies only to approved ordinary-prose spans. Identifiers,
acronyms, class names, environment variables, model names, and protected
technical literals are case-sensitive by default.

V1 performs no automatic Traditional/Simplified Chinese conversion,
translation, pinyin conversion, stemming, lemmatization, spelling correction,
or synonym expansion to claim semantic equivalence. Translation, Chinese
script rewriting, and natural-language synonymy use the Q8 reviewed semantic
mapping.

Mixed-language content is classified into explicit spans. Prose spacing and
paired quote rules may apply to its natural-language spans, while embedded
technical spans remain unchanged. Unicode confusables such as `O/0` and `l/1`
are not equivalent.

### 2.44 Recognition errors and layout artifacts

Recognition errors are not presentation differences. OCR substitutions such
as `0/O` and `1/l`, wrong or missing characters, incorrect numbers or units,
and ASR homophone substitutions, omitted words, speaker errors, or timestamp
errors must not be corrected by normalization.

Parser-lane metrics use the original parser artifact. A semantic matcher that
infers intended meaning cannot hide extraction, CER/WER, speaker, timestamp,
locator, or reading-order loss. Generation and end-to-end review may record a
human-approved semantic mapping but cannot rewrite the parser artifact or
retroactively grant parser extraction credit.

PDF line-end hyphenation may use a deterministic fast path only when versioned
rules have both layout line-boundary evidence and unambiguous continuation
evidence. A dictionary guess is insufficient. OCR-inserted spaces inside CJK
text may be joined only when layout or OCR segmentation metadata proves a
single token; otherwise the matcher abstains.

A fixture-specific diagnostic map is called a
`recognition-error correspondence map`, not a correction map. It explains the
relationship between erroneous recognition and reference content. It is not
provided to a candidate, cannot serve as an automatic matching fast path, does
not modify artifacts, and grants no parser extraction credit.

OCR/ASR metric definition, tokenization, normalization, measurement method,
and any necessary measurement boundary remain in the Q14 metric-specific
evidence and contract frontier. A gate constant or acceptance threshold remains
in Q11 `pending_calibration`. Repeatability, variance, and statistical
interpretation remain Q15 responsibilities.

### 2.45 Quantity, unit, date, and comparison semantics

A quantity component separates and preserves:

- sign;
- exact numeric value;
- original representation;
- unit identity and multiplier;
- percentage status;
- `comparison_relation`, such as less than, greater than, at least, or at most;
- `range_bounds`;
- `bound_inclusivity`;
- `approximation_status`, such as exact, approximate, or estimated;
- `precision_significance`;
- time or date range;
- comparison baseline;
- applicable condition and scope;
- locale and, when applicable, timezone and calendar.

V1 allows only explicitly versioned, unambiguous lexical equivalences. `20%`,
`20 percent`, and `20 per cent` may share a comparison value. Grouping
separators such as `1,000` are removed only when the approved locale makes the
interpretation unambiguous. Fullwidth digits require an explicit
`quantity_unit` mapping. ISO dates may be compared semantically; named-month
dates require known locale. Ambiguous dates such as `03/04/2026` require
abstention.

`1.0` and `1.00` are automatically equivalent only when approved gold states
that displayed precision does not carry meaning. If decimal places may express
measurement precision, the matcher abstains. No fuzzy rounding, approximate
numeric matching, or numeric tolerance is part of Q9.

V1 performs no automatic cross-unit conversion. It never assumes `GB` equals
`GiB`, `MB` equals `Mb`, or `m` equals `M`. Chinese-number and Arabic-number
equivalence is limited to an explicit, versioned, unambiguous rule set; other
cases require review. Unit conversion and numeric tolerances remain deferred.

### 2.46 Strict literals, code, and formula

API paths, class/function/variable names, environment variables, model/version
names, file paths, commands, hashes, URLs, error codes, database identifiers,
and package names use `identifier` or `technical_literal` and are verbatim or
near-verbatim by default.

These profiles are case-sensitive and perform no stemming, lemmatization,
spelling correction, Traditional/Simplified conversion, or confusable
replacement. Internal whitespace, hyphen, underscore, slash, dot, and colon
are not removed. Surrounding prose punctuation may be classified separately,
but the literal remains unchanged. URL v1 uses raw exact comparison: no
automatic decoding, query sorting, fragment removal, or host/path rewriting.
A reviewed mapping may say two names denote the same concept, but cannot grant
verbatim-preservation credit to an incorrect literal.

Code preserves original line breaks, indentation, internal whitespace, case,
punctuation, and comments. Only CRLF/CR-to-LF and an explicitly classified
terminal-file-newline difference may be treated as presentation differences.
Code is never executed or reformatted. V1 makes no AST or behavioral-
equivalence claim; indentation remains semantic in languages such as Python
and YAML.

Formula preserves operators, minus, superscript/subscript, parentheses,
variable identity, and relation symbols. It uses neither prose punctuation
rules nor symbolic algebra. NFC and an explicit finite safe presentation map
are the only automatic formula projections. LaTeX/Unicode or other mathematical
equivalence without such a rule requires reviewed mapping.

### 2.47 Table content and structure alignment

Table text is compared cell by cell using each cell's approved content
profile. Row, column, header, rowspan, colspan, and position are compared with
structure assertions. The table is never reduced to one flattened token bag.

Correct cell text in the wrong row or column records text alignment success
only. It cannot satisfy an expected claim whose truth conditions depend on the
correct row/column headers. Headers are semantic conditions for numeric cells,
not presentation decoration.

`empty_cell`, `missing_cell`, and `unavailable_extraction` remain distinct.
One-to-many and many-to-one cell segmentation is represented by an alignment
group that retains reference cells/source spans, candidate cells/spans, and
locator/structure evidence. Numeric cell alignment retains the applicable row
and column headers. Cell-overlap and structure-measurement definitions, methods,
and any necessary measurement boundary remain in the Q14 metric-specific
evidence and contract frontier. Gate constants and acceptance thresholds remain
in Q11 `pending_calibration`; repeatability, variance, and statistical
interpretation remain Q15 responsibilities.

### 2.48 Cross-parser alignment

Cross-parser alignment uses this evidence priority:

1. typed locator and source identity;
2. approved structure relation;
3. exact authoritative text/span;
4. exact versioned comparison projection;
5. candidate-specific reviewed alignment;
6. unresolved.

Element IDs are never cross-parser identities. Alignment supports one-to-one,
one-to-many, and many-to-one groups. Each group retains reference
elements/spans, candidate elements/spans, locator and structure evidence,
decision origin, and review metadata.

Stronger evidence conflict cannot be bypassed by falling back to weaker
evidence. For example, conflicting page locators are not ignored merely because
identical text appears elsewhere. Such a case becomes `alignment_conflict` and
requires human review or Q10 disposition.

Exact raw text or projection permits automatic alignment only when the result
is unique, or approved structure and order resolve all ambiguity. Repeated
labels such as “Notes” do not align automatically from text alone.

Every reference and candidate unit appears in one named alignment disposition:

- `aligned`;
- `reference_only`;
- `candidate_only`;
- `alignment_conflict`;
- `unresolved`.

Alignment links corresponding content but cannot change candidate text, create
missing locators, or grant missing structure. Deterministic rules abstain when
they cannot prove alignment. Edit distance, token overlap, IoU, and temporal-
delta thresholds remain deferred. Human reviewers resolve ambiguous groups;
an LLM may only propose candidates.

### 2.49 Projection and alignment audit artifacts

Projection and alignment decisions are separate artifacts with independent
versions and digests.

A `projection_record` contains:

- authoritative artifact ID and digest;
- authoritative raw span;
- profile ID/version;
- ordered operation IDs/versions;
- comparison value and projection digest;
- projected-to-raw offset map;
- deleted raw ranges and responsible operations;
- language/content-type context;
- span/profile classification digest.

Each projected code point maps to one or more raw half-open ranges. When
several raw characters merge, every contributing range remains recorded. When
one raw character expands, each projected code point maps back to that raw
range. Deleted characters have explicit deleted-range records. No projected
character lacks provenance. A run-length representation may compress the map
without changing this logical contract.

An `alignment_decision_record` contains:

- reference and candidate references;
- projection digests used, if any;
- alignment rule ID/version;
- disposition and decision origin;
- reviewer metadata when applicable;
- dispute and unresolved records.

Matcher identity, reviewer, dispute, and alignment outcome do not enter pure
projection identity. The same authoritative input, span/profile classification,
profile, and rule versions must produce byte-identical projection bytes and
digest regardless of reviewer or alignment target.

Both records are derived audit artifacts, not gold or source truth. A
projection cannot become new source-span authority. Any normalization-rule or
span/profile-classification change is scoring-relevant: it produces a new
version and digest and requires directly compared results to be rerun or
replayed. Hidden, unversioned normalization inside a scorer is forbidden.

### 2.50 Abstention and human fallback

A deterministic matcher must abstain when:

- profile selection or protected-span boundaries are ambiguous;
- locale, date, separator, precision, or unit identity is ambiguous;
- an operation could cross a literal, quantity, code, or formula boundary;
- soft-line-break or hyphenation evidence is insufficient;
- a transformation could change negation, quantity, scope, identifier, or
  operator;
- alignment relies only on unapproved fuzzy similarity;
- stronger alignment evidence conflicts;
- offset provenance cannot be constructed completely;
- a rule cannot prove presentation equivalence.

Presentation ambiguity proceeds to reviewed alignment. Semantic equivalence
proceeds to the Q8 reviewed match artifact. Recognition errors remain visible
in parser artifacts. An LLM cannot approve either decision.

Abstention creates a named unresolved record. It is not automatically a match,
mismatch, error, zero score, or exclusion. The frozen Q10 policy determines
whether the unresolved item blocks authority or receives another explicit
disposition.
There is no hidden fallback to NFKC, lowercase, edit distance, token overlap,
or another unversioned heuristic.

### 2.51 Q9 plain-language decisions, trade-offs, and examples

**Presentation normalization** removes a proven surface difference while
keeping a complete trail back to raw text. **Semantic correction** changes or
interprets meaning and therefore requires reviewed Q8 mapping; it never rewrites
the parser or reference artifact.

Examples:

- **Natural language:** `first\r\nline` and `first\nline` may share a line-ending
  projection. Two separate paragraphs are not merged merely to improve match.
- **OCR/ASR:** OCR `O GB` for source `0 GB`, or ASR omitting “not,” remains a
  recognition error. A correspondence map may explain it but cannot award
  extraction credit.
- **Number and unit:** `20%` and `20 percent` may be lexical equivalents.
  `< 8 GB` is not equivalent to `8 GB`, and `GB` is not automatically `GiB`.
- **Identifier:** `OPENAI_API_KEY` is not equivalent to `openai_api_key` under
  ordinary prose case-folding.
- **Code:** Changing Python indentation is not whitespace normalization, even
  if all words remain present.
- **Formula:** `x - y` is not normalized to `x + y`; algebraic equivalence is
  outside the v1 deterministic profile.
- **Table:** `100 ms` aligned to the wrong environment row may receive text
  alignment but cannot satisfy a claim tied to the correct row header.

The contract deliberately prefers abstention and visible review over broad
automatic matching. This increases review cost, but prevents normalization
from hiding parser loss, numeric errors, misplaced table values, or corrupted
technical literals.

### 2.52 Q10 status dimensions

Q10 is frozen. Source meaning, benchmark governance, availability,
evaluation disposition, and run validity are separate dimensions. They must
not be compressed into one six-state enum because more than one may apply to
the same object.

- Source contradiction resolution continues to use the Q8 field
  `resolution_status=resolved | unresolved | not_stated`. Source-expressed
  uncertainty or lack of resolution is authoritative source content. It is
  not a benchmark-process dispute and remains eligible for annotation and
  scoring.
- Governance state records whether an annotation, mapping, normalization, or
  alignment decision still requires human resolution.
- Availability/applicability uses `available`, `unavailable`, or
  `not_applicable` where the relevant contract calls for those values.
- Evaluation disposition records a decided result such as coverage,
  unsupported content, omission, mismatch, or `process_unresolved`.
- Run validity is `valid` or `invalid` and records a machine-readable invalid
  reason and affected scope.

For example, if a source says that a study remains inconclusive, its source
`resolution_status` is `unresolved`. If a candidate says the study proved the
claim, the candidate disposition is the already decided `overstated`; the
case is not a process unresolved item. A process unresolved item exists only
when the benchmark process has not yet made an authoritative decision.

### 2.53 Unresolved ownership, affected scope, and authority effect

Every governance unresolved record separates three concepts:

- `ownership_scope` is `gold`, `candidate`, or `run`;
- `affected_scope` identifies the fixture, candidate when applicable,
  directly affected artifacts and objects, lanes, and named denominators;
- `authority_effect` is derived by a versioned authority rule as blocking or
  non-blocking diagnostic.

These are not one combined enum. Ownership answers who owns the unresolved
decision; affected scope answers which results depend on it; authority effect
answers whether those results may be formally trusted.

A record missing a required scope, object reference, version, or digest fails
artifact validation closed. It is not silently promoted to fixture-global
blocking because doing so would hide an annotation-contract defect. If the
invalid artifact is encountered during a run, the dependent run scope is
invalid.

An unresolved item is blocking whenever it could change a formal denominator,
metric input, expected-claim coverage, generated-claim support, importance,
exclusion, alignment, or authority decision. The versioned rule applies this
test independently of `critical`, `major`, or `minor`. It must not inspect a
candidate score or speculate about whether a future threshold might be
crossed.

Non-blocking unresolved items are limited to diagnostics proven to be outside
every formal denominator and authority-closure condition. Blocking uses the
smallest affected formal scope. Each lane may independently obtain authority,
but a comparison or adoption statement may cover only the applicable required
lanes that have completed authority closure. Q10 determines whether results
are trustworthy; Q11-Q14 own quality, blocker, comparison, and scoring effects,
while Q15 owns repeated-run publication and adoption-support closure without
creating another pass/fail or adoption decision.

For example, an unresolved screenshot bounding-box alignment that affects
only the parser locator denominator blocks that fixture's parser-locator
scope. It does not automatically block an unrelated generation coverage
scope. An unresolved expected-claim meaning in gold affects every candidate
that depends on that gold.

### 2.54 Gold, candidate, and run ownership

Gold-scoped disputes include gold ontology, evidence identity, expected-claim
semantics, importance, support expressions, category applicability, and
source-side exclusions. They affect every candidate whose result depends on
the disputed gold scope.

Candidate-scoped disputes include generated-claim boundaries,
candidate-specific claim-to-gold mappings, expected-claim coverage,
generated-claim support, and candidate alignment. They affect only that
candidate's dependent scope. A candidate-specific unresolved item cannot
modify gold, importance, category applicability, source exclusions, or a
formal denominator.

Malformed artifacts, digest mismatches, missing required artifacts, and
runner crashes are validity failures, not semantic unresolved items.
Invalidity is also scoped to its dependencies:

- a damaged Candidate B mapping artifact invalidates Candidate B's dependent
  result scope;
- damaged shared gold or a scorer manifest invalidates every dependent result;
- one candidate failure does not invalidate independent candidate results
  whose complete dependencies remain valid.

### 2.55 Adjudicated `unscorable` exclusions and evaluation basis

`unscorable` remains a source-side exclusion and may be created only after
human adjudication of a candidate-independent, irrecoverable source problem.
Eligible reasons are limited to cases such as:

- a canonical snapshot is permanently damaged and no lawful reconstruction
  source exists;
- required pages, bytes, or caption cues are permanently missing;
- human reviewers cannot reliably recognize the source content;
- the original fixture cannot support reliable gold for the affected unit.

Annotator disagreement, review cost or scheduling, parser loss, poor candidate
performance, candidate-specific ambiguity, and incomplete matching are not
`unscorable` reasons.

An adjudicated exclusion applies consistently to every candidate under the
same benchmark version and only to its named lane and denominator. If approved
exclusions leave a required named denominator with no eligible gold unit, or
make the fixture unable to test its manifest-preregistered case purpose, that
fixture/lane has `no_formal_evaluation_basis`. It cannot claim formal authority.
This rule is structural and introduces no numeric sufficiency threshold.

For example, an irrecoverably corrupted PDF page that humans cannot read may
be adjudicated as `unscorable`. A parser failing to extract a readable page is
a parser result, not an exclusion.

### 2.56 Provisional, inconclusive, and invalid results

The three terms are distinct:

- `provisional` means a blocking benchmark annotation, mapping,
  normalization, or alignment decision remains unresolved, although the
  runner may still produce diagnostics;
- `invalid` means a schema, digest, manifest, required-artifact, or execution
  contract failed for the stated scope;
- existing evaluation uses of `inconclusive` retain their existing meaning
  and are not automatically equivalent to `provisional`. Any future mapping
  requires a separate versioned rule.

A provisional result may contain decided item-level dispositions, all
unresolved IDs and scopes, decided and unresolved counts, and deterministic
resource or execution diagnostics. It must not:

- report formal pass/fail;
- rank candidates;
- perform a formal baseline comparison;
- support adoption;
- remove unresolved items from a denominator;
- assume a hypothetical resolution to calculate coverage percentages;
- present a metric calculated only from the decided subset as the complete
  metric.

A gold-scoped blocking unresolved item makes every dependent candidate result
provisional. A candidate-scoped item makes only that candidate's dependent
scope provisional.

For example, a still-disputed paraphrase may coexist with latency diagnostics
and decided claim records, but the candidate cannot be declared better than
the baseline until the dispute is adjudicated.

### 2.57 Review and adjudication lifecycle

The closed unresolved lifecycle is:

- `open`;
- `under_review`;
- `adjudicated`;
- `superseded`.

The closed resolution outcomes are:

- `authoritative_decision_recorded`;
- `source_exclusion_created`;
- `output_non_claim_confirmed`;
- `superseded_by_revision`.

There is no unreasoned `ignored`, `dismissed`, `waived`, or silent close. Every
resolution has a machine-readable reason and audit record.

When a primary annotator and independent reviewer have a blocking gold
dispute, a third independent human adjudicator decides it. A candidate-specific
mapping's initial review is performed by a person who did not create the
original mapping; a remaining dispute goes to an independent adjudicator. If
the required independent person is unavailable, the record remains unresolved
and the result remains provisional.

Candidate identity is hidden when practical. If it cannot be hidden, the
reason is recorded. Aggregate score is unavailable to reviewers and
adjudicators until all applicable decisions are complete. An LLM may retain
suggestion provenance but cannot be a reviewer or adjudicator.

### 2.58 Unresolved audit record and derived blocking

Each unresolved audit record has a unique ID and conditionally complete,
machine-readable fields for:

- kind and origin;
- ownership scope;
- fixture and candidate identity when applicable;
- directly affected artifact and object references;
- affected lanes and named denominators;
- authority effect and the authority-rule ID/version that derives it;
- human explanation, reason code, and related evidence references;
- opener identity and timestamp;
- reviewer identity and timestamp after review begins;
- adjudicator identity, timestamp, and outcome after adjudication;
- lifecycle status;
- successor artifact and digest when superseded;
- directly related artifact versions and digests;
- binding/dependency manifest ID and digest;
- optional LLM-suggestion provenance.

Candidate identity is required only for candidate-scoped records.
`reviewed_by` and `reviewed_at` are required only after review begins.
`adjudicated_by`, `adjudicated_at`, and outcome are required only after
adjudication. Successor fields are required only after supersession.

The binding/dependency manifest must resolve the relevant schema, benchmark,
fixture, gold, reference, candidate, mapping, projection, alignment, and
scorer dependencies. Each unresolved record need not duplicate every
transitive digest.

Blocking is fully derived from versioned rules using kind, ownership,
affected scope, and denominator effect. A reviewer may correct the facts,
classification, or scope through review, but cannot directly turn off a
blocking flag. Audit records prefer object references, reason codes, and
digests over copies of private source or candidate text.

### 2.59 Immutable adjudication, rescore, replay, and rerun

All adjudication outputs and successor results are immutable and
content-addressed.

- A gold-scoped change publishes new gold and benchmark-manifest versions and
  digests. Every directly compared candidate is rescored under the new gold.
- A candidate-specific mapping change publishes a new candidate mapping
  artifact. Only that candidate must be rescored, but every comparison or
  ranking publication containing it must be regenerated.
- A normalization, alignment, or authority-rule change publishes a new
  scorer-contract version. Every directly compared result is rescored.
- Old artifacts and results remain available and are marked superseded; they
  are never overwritten.

When frozen candidate output bytes have not changed, a gold, mapping, or
scorer correction normally requires deterministic rescore or replay, not a
new parser, OCR, ASR, or LLM invocation. Candidate execution is required only
when candidate input changes; the reference document changes and is consumed
by the candidate; parser/generator version or configuration changes; candidate
output is missing or untrusted; or the execution contract changes.

Formal candidate comparison requires the same mapping contract/rule version
and review protocol. Candidate-specific mapping artifact digests naturally
differ, but the comparison manifest binds each candidate to its correct
approved digest. Old and new revisions of the same candidate mapping cannot
be mixed in one formal result.

### 2.60 Formal-authority closure invariant

A versioned closure validator decides authority only. It does not calculate or
infer quality pass/fail.

Formal authority requires all of the following for the claimed scope:

- every authority-relevant abstention has an unresolved record;
- every authority-relevant alignment conflict has a formal disposition;
- blocking unresolved count is zero;
- gold is `reviewed` or `adjudicated`;
- every source-side exclusion has completed the required review;
- candidate generated-claim, mapping, and alignment artifacts are complete
  and hold the required authority;
- schema, manifest, artifacts, versions, and digests agree;
- the result is outside every invalid scope;
- baseline and candidate use the same benchmark, fixture, gold, reference,
  and scorer-contract versions;
- they use the same mapping contract version, and the comparison manifest
  binds every candidate's approved mapping digest;
- every applicable lane required by a full-profile formal comparison or
  adoption statement has completed authority closure.

The smoke profile never gains adoption authority. The closure validator must
not define or derive metric thresholds, importance weights, aggregation,
non-regression gates, improvement gates, or adoption gates reserved for
Q11-Q14 or a future independently approved Q11 gate revision.

For example, a comparison with complete deterministic measurements but one
undisposed alignment conflict remains provisional. Closure cannot be obtained
by ignoring the conflict or by observing that current metric values appear
high.

### 2.61 Q10 plain-language decisions and trade-offs

1. **The source being uncertain is still an answer.** If a paper says its
   result is unresolved, complete notes must preserve that fact. Only an
   unfinished benchmark decision is a process unresolved item.
2. **A dispute blocks only what depends on it.** Explicit ownership and scope
   avoid invalidating unrelated lanes, while fail-closed validation prevents
   missing scope from being silently guessed.
3. **Minor does not mean safe to ignore.** Any unresolved item that could
   change a formal denominator or authority decision blocks that scope,
   regardless of importance. Importance weights remain a later scoring issue.
4. **Candidate problems cannot rewrite the answer key.** Candidate-specific
   ambiguity stays with that candidate; shared gold disputes consistently
   affect all dependent candidates.
5. **`unscorable` is an emergency source disposition, not a cleanup tool.** It
   is reserved for irrecoverable source defects. Difficult review, parser loss,
   or poor output stays visible.
6. **Provisional diagnostics are useful but are not a verdict.** They can show
   what is already known without ranking candidates or pretending unresolved
   items disappeared.
7. **Every closure has a named human and reason.** Independent adjudication
   costs more time, but prevents an annotator, candidate, or LLM from silently
   changing authority.
8. **Rule changes usually require rescoring, not regeneration.** Frozen output
   is reused when trustworthy, preserving cost and reproducibility while every
   changed decision receives a new version and digest.
9. **Authority and quality remain separate.** Q10 decides whether a result may
   be trusted. Q11 freezes the quality-gate contract while its constants await
   evidence; Q12-Q14 retain the remaining blocker, scoring, and comparison
   ownership, while Q15 adds repeated-run publication and adoption-support
   closure without a new decision enum.

### 2.62 Q11 contract status and gate topology

Q11 freezes the gate topology, scope, gate types, metric direction and
comparator contract, calibration-evidence requirements, preregistration and
review procedure, versioning, and authority interface. It does not freeze any
exact numeric constant that lacks approved calibration evidence.

The formal status is:

`Q11 gate topology and registration protocol frozen; exact constants pending_calibration`

Q11 must not be described as fully frozen while any required constant remains
pending. A gate slot is a versioned location for a future gate decision, not a
gate decision by itself.

The quality-evaluation order is:

1. Q10 authority closure for the metric scope;
2. absolute floor;
3. non-regression;
4. improvement;
5. a later adoption decision outside Q11.

Q10 closure failure means the affected scope has no formal quality decision.
By contrast, an absolute-floor failure is an authoritative quality result when
its metric inputs, denominator, and gate contract have authority. It does not
invalidate the metric or erase later gate results. Non-regression and
improvement remain formally calculable for independently authoritative metric
scopes even when another quality gate fails.

All required quality-gate results remain non-compensating. A quality-gate
bundle cannot pass when one of its required gates fails, but it retains every
other formal result so reviewers can see both improvements and regressions.
For example, a candidate may formally fail a parser-locator floor and formally
pass a generation improvement gate. The latter does not compensate for the
former.

### 2.63 Sparse gate-address matrix

Every gate address contains at least:

- evaluation lane;
- source type;
- preregistered source subtype;
- metric ID.

Source subtypes come from a closed taxonomy defined by the benchmark manifest
before candidate execution. They cannot be inferred from candidate behavior or
created after results are observed. Each source type uses only its applicable
subtype taxonomy. The initial taxonomy must be able to distinguish the frozen
fixture characteristics, including born-digital, scanned, and mixed PDFs;
static and JavaScript-rendered web snapshots; manual and automatic caption
snapshots; linear and threaded chat; and non-overlapping and overlapping
screenshot sets.

The matrix is sparse. The existence of an address does not imply that a
numeric gate is required. A slot becomes eligible for calibration only after
its metric contract and applicability are complete. Candidate-specific or
post-result cohorts are forbidden.

Q11 freezes gate addressing only. How fixture results form a cohort decision
and how N/A values participate in aggregation remain Q12 decisions.

### 2.64 Absolute-floor slots

An absolute floor states the minimum acceptable quality of a candidate without
regard to how weak the baseline is. There is no global composite floor.
Applicable metrics receive independent floor slots, and one metric cannot
compensate for another metric falling below its floor.

Floor records distinguish:

- `numeric_floor_slot`: inactive for formal decisions until the metric formula
  and calibration are complete and the threshold is approved;
- `discrete_invariant_candidate`: a preregistered requirement and rationale
  whose blocking status and exact scope remain Q12 decisions.

A `discrete_invariant_candidate` cannot independently produce a formal
adoption failure before Q12 resolves its gate role. Q11 does not decide
per-fixture or critical-item blocking.

For example, table-cell text preservation and correct row/column placement
need separate metric slots. High cell-text coverage cannot compensate for
placing a value under the wrong header.

### 2.65 Non-regression comparison primitive

The default non-regression primitive contains:

- a metric-native absolute difference;
- a paired fixture-level baseline and candidate result;
- an explicit direction;
- a canonical unit;
- an exact comparator contract;
- a separate measurement-tolerance slot.

Relative change is not the default. A metric contract must approve it
explicitly and justify why it is meaningful. Q13 freezes the non-numeric
comparison policy for a baseline that is exactly zero, lacks formal comparison
authority, or lacks an eligible paired result. Metric-specific relative
applicability, valid domains, and near-zero calibration remain pending. Q12
decides how paired fixture results form a cohort decision.

Deterministic metric artifacts must reproduce under their frozen replay
contract before comparison. Q15 owns the frozen non-inferential repeated-run
topology for LLM-backed execution variability; formal repeat scheduling,
execution compatibility, and capture realization remain with evidence-dependent
Q15 policy and later runner contracts. Q11 continues to own gate decisions and
constants.

For example, a percentage claim such as “twice the baseline” can exaggerate a
small change when the baseline is close to zero. The authoritative primitive
therefore preserves the metric's native absolute difference and its paired
fixture identities.

### 2.66 Preregistered improvement claims

Every candidate preregisters, for each claimed benefit:

- claimed-benefit lane;
- source cohort;
- primary target metrics;
- comparator form;
- an improvement slot whose constant remains pending until calibrated.

Preregistration must be complete before formal candidate execution, output
capture, candidate-specific mapping review, or formal result disclosure. A
candidate implementer cannot select a favorable metric after seeing output.

Applicable scopes for which the candidate claims no improvement still follow
their absolute-floor and non-regression contracts. They are not required to
improve every metric. Every claimed-benefit scope, however, must use its
preregistered primary target metrics.

For example, a candidate claiming better scanned-PDF OCR cannot later redefine
success as improved web-heading extraction after inspecting its output.

### 2.67 Baseline role and authority

Baseline role and authority status are independent dimensions. The current MVP
may have `role=characterization_baseline` and still obtain formal comparison
authority when it uses:

- the full profile;
- canonical fixtures;
- reviewed or adjudicated gold;
- Q10 authority closure;
- complete version and digest bindings.

The characterization baseline may fall below future absolute floors because
its role is to record current behavior faithfully. It cannot bypass schema,
fixture, gold, manifest, digest, or full-profile requirements.

Smoke, draft-gold, partial, local-diagnostic, provisional, and invalid results
cannot serve as a formal comparison baseline. Baseline metric artifacts may be
created while constants remain pending, but they cannot support formal
non-regression or improvement decisions until the applicable gate constants
are approved.

Formal comparison binds baseline and candidate to matching benchmark,
fixture, gold, reference-document, scorer, gate-contract, and applicable
mapping-contract versions and review protocol. When baseline identity changes,
an old candidate requires compatible rescoring and a regenerated comparison
artifact before direct comparison.

### 2.68 Calibration evidence and independence

Calibration evidence has typed responsibilities:

- normative correctness or safety evidence defines a non-negotiable quality
  requirement or candidate invariant;
- approved fixtures and gold define metric truth and applicability;
- the current MVP baseline describes current behavior but cannot alone set a
  minimum-quality floor;
- a known-good reference helps establish an achievable range;
- annotation and adjudication evidence describes gold-decision stability;
- measurement repeatability calibrates measurement tolerance only and cannot
  lower a quality floor;
- pilot candidates may calibrate a materially meaningful improvement magnitude
  but cannot lower a normative requirement.

Formal candidate data is prohibited from threshold calibration. If pilot data
is genuinely necessary, it uses a preregistered calibration candidate with no
adoption authority and calibration evidence isolated from formal decision
fixtures. When the 13-case benchmark is too small for a safe split, a lawful,
independent calibration corpus is created instead of repeatedly tuning against
the formal fixtures.

A threshold proposer may help design the gate. The formal reviewer and
approver must satisfy independent-review requirements and cannot approve a
threshold after seeing formal candidate results.

Each calibration record retains at least its evidence type, artifact IDs and
digests, calibration cohort, metric contract and version, observed range or
measurement error as applicable, rationale, proposer/reviewer/approver
identities and timestamps, candidate-blinding status, version, and digest.

### 2.69 Numeric authority, precision, and boundary decisions

Scoring authority prefers, in order:

1. integer counts;
2. exact rational numerator and denominator;
3. canonical decimal strings evaluated under a versioned Decimal context.

Binary floating point has no formal authority unless the relevant metric
contract explicitly approves its representation and error behavior.

Every numeric gate declares:

- exact comparator;
- equality behavior;
- metric direction;
- canonical numeric representation;
- computation precision;
- tolerance rule and calibration state;
- display precision.

Display rounding affects reports only and never changes pass/fail. A displayed
value that appears equal to a threshold after rounding does not pass unless
the authoritative value satisfies the registered comparator. Q11 freezes no
numeric tolerance value.

### 2.70 Gate records, calibration state, and immutable revision

A gate record contains at least:

- gate ID and version;
- lane, source type, preregistered subtype, and metric ID;
- metric-contract version;
- gate type: `absolute_floor`, `non_regression`, or `improvement`;
- direction and exact comparator;
- canonical numeric representation;
- `calibration_status` as `pending_calibration` or `approved`;
- `threshold_value` only when calibration is approved;
- measurement tolerance and its separate calibration status;
- calibration evidence, rationale, and artifact digests;
- proposer, reviewer, and approver identities and timestamps;
- effective benchmark version;
- superseded-gate reference when applicable.

`pending_calibration` is not a numeric threshold value. A slot missing its
metric contract, approved threshold, or required calibration evidence cannot
produce a formal gate decision.

All scoring-relevant changes create immutable revisions:

- changing only a gate constant creates a new gate contract, gate evaluation,
  and binding/publication manifest, after which compatible metric artifacts may
  undergo gate reevaluation;
- changing a metric unit, denominator, formula, state transformation,
  direction, or authoritative numeric representation creates a new metric
  contract and requires dependency-scoped rescoring;
- changing comparison-policy selection or comparator semantics creates a new
  comparison-policy revision and requires recomparison of compatible metric
  results, not rescoring;
- changing scorer implementation identity, deterministic calculation behavior,
  or compatibility creates a new scorer contract and requires rescoring when
  calculation behavior may change;
- changing candidate input, implementation, or output requires candidate
  execution.

Q4 version policy applies to the gate contract, scorer, and top-level
benchmark release manifest. A gate change does not by itself rewrite the
fixture dataset. Old gates and results remain immutable and may be marked
superseded. No gate is edited in place after formal candidate execution or
output capture.

### 2.71 Metric-scoped authority interface

Q10 closure is evaluated at the metric scope. When a metric's inputs or
denominator lack closure, that metric has neither a formal gate decision nor a
threshold-distance diagnostic. An unrelated unresolved scope does not remove
authority already established for an independently closed metric.

The whole candidate or adoption statement still waits for every required,
applicable scope to complete closure. Smoke may verify gate machinery and emit
diagnostics but has no adoption authority. Only the full profile can produce a
formal quality-gate decision.

For example, an unresolved parser-locator denominator prevents a formal
locator gate and distance. It does not invalidate a separately closed
generation-latency metric, although neither can support an overall adoption
statement until all required scopes close.

### 2.72 Pending-constant completion conditions

An exact constant remains `pending_calibration` until all applicable
conditions are satisfied:

1. all 13 canonical fixtures complete rights and privacy review;
2. applicable fixtures have reviewed or adjudicated gold;
3. the metric formula, unit, and denominator are frozen;
4. the formal MVP characterization baseline is complete;
5. measurement-repeatability and required annotation evidence are complete;
6. the calibration rationale passes independent review;
7. the gate contract, manifest, and digests are published before any formal
   candidate execution or output capture.

If a constant depends on pending Q12 classifications or Q14 metric-specific
measurement and aggregation evidence, it remains pending.
Before approval, the project may create gate slots, validate artifacts and gate
machinery, and emit diagnostics. It must not produce formal quality pass/fail,
formal non-regression or improvement decisions, or adoption support.

### 2.73 Q11 plain-language decisions and trade-offs

1. **The exam structure is frozen before the passing marks.** We know which
   gate belongs to which lane, source cohort, and metric, but no unsupported
   percentage is invented before fixtures, gold, metrics, and baseline exist.
2. **Authority failure and quality failure are different.** An unresolved
   denominator prevents a formal decision. A valid low score is still an
   authoritative result and does not erase other gate outcomes.
3. **Source subtypes remain visible.** A strong native-PDF result cannot hide a
   scanned-PDF weakness, while the sparse matrix avoids meaningless gates.
4. **There is no compensating global floor.** Correct text in a misplaced table
   cell does not make the table correct, and a generation gain cannot repair a
   parser regression.
5. **Improvement claims are made before output exists.** Candidates cannot
   inspect results and then select the metric on which they happened to win.
6. **The current MVP can be a trustworthy bad baseline.** Formal authority
   means the measurement is trustworthy; it does not mean current quality is
   good enough.
7. **Calibration evidence has narrow jobs.** Repeatability can set measurement
   tolerance but cannot lower quality expectations; pilots cannot weaken a
   normative requirement.
8. **The scorer compares authoritative numbers, not rounded labels.** Display
   formatting never converts a failure into a pass.
9. **Changing a gate creates history rather than rewriting it.** Compatible
   metrics can be reevaluated after a constant change, while formula changes
   require rescoring and candidate changes require re-execution.

### 2.74 Q12 authority and quality outcome axes

Q12 is frozen at the blocking and aggregation-topology level. Authority,
result role, and quality decision are independent axes:

- `authority_status` is exactly the Q10 authority status and is neither renamed
  nor duplicated;
- `result_role` is `formal` or `diagnostic_only`;
- `quality_decision` is `pass`, `hard_blocked`, `aggregate_gate_failed`, or
  `not_evaluated`.

`formal` describes an intended result use; it does not itself grant authority.
`hard_blocked` and `aggregate_gate_failed` remain distinct. `not_evaluated`
uses an already frozen reason such as `pending_calibration` or
`no_formal_evaluation_basis`; the alias `no_evaluation_basis` is forbidden.

Invalid and provisional scopes are not quality failures. Q12 blockers arise
only from decided quality evidence with the required authority. Authority
closure does not imply a quality pass, and a quality blocker does not remove
the authority of its underlying measurement.

Until all required gate constants are calibrated, a candidate bundle cannot
report `pass`. A decided hard blocker may still be recorded formally when its
own scope has authority. For example, an approved critical omission can be a
formal `hard_blocked` result even while an unrelated aggregate gate remains
`not_evaluated` because its constant is pending.

### 2.75 Versioned blocker rules without duplicate facts

The blocking contract does not copy Q8 coverage and support states into a
second failure ontology. Every observation contains:

- its authoritative source fact, such as `partially_covered`, `unsupported`,
  or `overstated`;
- at most one primary `blocker_rule_id`;
- origin or mechanism and any additional diagnostic reasons;
- prerequisites, scope, disposition, and rule version.

Diagnostic reasons do not create extra blockers for the same scoring unit.
For example, `critical_truth_condition_lost` may explain why
`critical_claim_not_fully_covered` fired, but it is not a second blocker.
Likewise, table, renderer, or structure mechanisms do not create another
blocker when their semantic consequence already blocks the same scoring unit.

The closed authoring dispositions are `hard_blocker`, `aggregate_only`, and
`pending_classification`. `pending_classification` is permitted only while
authoring or calibrating the contract. It is not a runtime quality outcome.
If a formal evaluation encounters a classification still capable of changing
the result, it fails closed under Q10 as provisional or `not_evaluated`; it
cannot pass.

Blocking is derived from versioned rules. Reviewers approve the observed state,
prerequisites, and evidence; they cannot inspect scores and freely toggle a
blocker.

### 2.76 Critical expected-claim blockers

A critical expected claim is a hard blocker unless its coverage state is
`fully_covered`. Both `partially_covered` and `not_covered` therefore trigger
the critical-claim blocker. Missing an optional semantic component does not
prevent full coverage and remains diagnostic.

Coverage and generated-claim support remain separate outcomes and named
denominators. A missing condition may create a critical coverage blocker while
an affirmative false statement creates a support blocker. Q12 does not force
those outcomes to share one failure identity; lane-local identities and causal
relations follow section 2.87.

For example, the source says “Do not enable X below 8 GB,” and the candidate
says “Enable X.” The critical claim is not fully covered. If the candidate also
asserts the reversed instruction, that generated claim independently receives
its Q8 support state.

### 2.77 Parser critical dependencies

Parser critical dependencies are derived from a critical expected claim's
approved normative support expression. Evidence receives no second importance
field.

- Missing any required leaf in `all_of` breaks the critical dependency.
- Preserving at least one complete approved alternative in `any_of` avoids the
  critical blocker. Missing other alternatives still records parser
  completeness loss in aggregate or diagnostic results.
- Context evidence does not independently trigger a critical blocker.
- Structure or locator information becomes a critical dependency only when
  approved gold explicitly states that it is necessary to interpret required
  evidence correctly. The scorer cannot infer this relation.

Parser and end-to-end outcomes remain independent. A parser loss may be linked
to a later end-to-end loss only through a reviewed causal relation.

For example, a table value of `100 ms` may support a critical claim only with
its `16 GB` row header. Preserving the number under the wrong header fails the
approved parser critical dependency.

### 2.78 Generated-claim source-support blockers

A formal, adjudicated semantic generated claim is a hard blocker when its
source-support state is:

- `unsupported`;
- `contradicted_by_source`;
- `overstated`;
- `candidate_internal_contradiction`.

Faithfully preserving a contradiction found in the source is not a candidate
internal contradiction. Citation presence cannot compensate for a source-
support failure.

`partially_supported` follows this order:

1. If the unit can be divided into independent claims, the Q6 generated-claim
   map is corrected.
2. If its boundary remains disputed, it follows Q10 unresolved governance and
   has no formal quality decision.
3. If adjudication confirms that it is indivisible and contains a substantive
   unsupported component, it is a hard blocker.

There is no “minor-looking” materiality waiver. Such a waiver would create a
second importance authority on generated claims. Presentation-only and
non-claim output already leave the semantic claim denominator under Q6.

For example, changing a source recommendation into “experimentally proven” is
`overstated` and blocks even when every other note is complete.

### 2.79 Structure, locator, table, formula, code, and renderer loss

Structure, reading order, table, code, formula, and renderer loss is a hard
blocker when it breaks an approved critical dependency or causes a semantic
support failure. General non-critical loss remains in its corresponding
aggregate metric.

A demonstrably fabricated discrete locator identity is a hard blocker. This
includes a page, cue, message, image, or DOM identity that does not exist in
the canonical source. Missing locators, `unavailable` locators, and geometric
or temporal deviations are not fabrication; they follow critical-dependency
rules and later calibrated thresholds.

Renderer-caused critical omission, contradiction, unsupported content, or
overstatement uses the corresponding semantic blocker rule. It does not
create a duplicate renderer blocker for the same scoring unit. IoU, temporal
delta, table alignment, and similar numeric thresholds remain
`pending_calibration`.

For example, omitting a decorative table border is aggregate structure loss.
Moving a critical value to the wrong row, changing `x - y` to `x + y`, or
inventing page 99 when no such page exists may trigger a hard blocker under the
applicable approved rule.

### 2.80 Minimal-scope blocker propagation

A blocker originates at the smallest applicable scope and propagates through
versioned dependency rules:

- an item blocker makes its fixture/lane result `hard_blocked`;
- a containing cohort records `contains_hard_blocker` and the originating
  fixture IDs;
- the required lane bundle is blocked;
- the candidate quality bundle cannot be rescued by higher results in another
  metric or lane.

Other non-compensating lanes retain their own formal outcomes and are not
rewritten as failures. This propagation is a benchmark quality decision, not a
complete production-adoption decision.

For example, a critical table-semantic blocker in P03 blocks P03's parser lane
and is visible in the PDF parser cohort. The frozen-reference generation lane
may still retain a formal passing outcome, but cannot compensate for parser
failure.

### 2.81 Hierarchical scorecard topology

The scorecard uses a hierarchy without a cross-source or cross-lane composite:

1. item outcomes form a fixture result;
2. fixture results enter their preregistered subtype and source cohort;
3. each source cohort retains an independent gate vector;
4. each lane retains its non-compensating gate vector;
5. the candidate scorecard reports those vectors rather than one composite
   score.

Raw item count, source length, paragraph count, and claim count cannot directly
increase cross-fixture weight. Q14 confirms that micro and pooled totals are
diagnostic or audit evidence only. Fixture vectors remain authoritative;
metric-specific formulas and formal aggregation selections require their own
evidence and contracts. Statistical interpretation remains Q15.

A subtype represented by one fixture may still produce a formal result for
that fixture and may be a preregistered required gate. Its artifact records
`fixture_count=1` and the fixture ID, and must not claim statistical
generalization to all sources of that subtype.

### 2.82 Importance strata and scoring identity

Critical, major, and minor expected claims are reported as separate counts and
rates. Critical claims additionally follow the hard-block rule. Q12 assigns no
numeric importance weights.

One expected claim has one formal scoring identity. Multiple categories,
evidence items, source references, or repeated occurrences do not increase its
denominator count. Recurrence adds a unit only when it supports a separately
approved recurrence truth condition and expected claim. Category coverage is
a derived diagnostic view rather than a scoring authority.

### 2.83 Partial-state vectors

Coverage and support states remain separate vectors of counts and rates. No
partial state receives numeric credit in Q12.

- `fully_covered`, `partially_covered`, and `not_covered` remain distinct;
- every generated-claim support state remains distinct;
- critical partial coverage follows the critical blocker rule;
- major and minor partial coverage is reported separately;
- `partially_supported` is not merged into the `unsupported` numerator.

Partial is never automatically converted to a numeric credit. Q14 v1 forbids
numeric partial credit and retains the separate state-vector components.

### 2.84 Typed denominator disposition

Named denominators use these exact dispositions:

- `not_applicable` comes only from approved gold and a preregistered scope-rule
  ID. It leaves only the named denominator.
- `not_present` records that the source lacks the category. It remains in the
  audit trail and is not candidate success. Candidate claims about that absent
  content still receive source-support evaluation.
- Gold `unavailable` removes only the corresponding metric unit.
- Candidate `unavailable` when gold is available is a quality failure. Whether
  it hard-blocks follows an approved critical dependency or blocker rule.
- Approved `unscorable` removes only its named lane and denominator.
- `present_but_optional` does not enter the generation expected-claim
  completeness denominator. It remains parser extraction content, and a
  candidate that mentions it enters generated-claim support evaluation.

A zero denominator produces `no_formal_evaluation_basis` and
`quality_decision=not_evaluated`. It never produces zero or one hundred
percent, and a required gate with no formal evaluation basis cannot pass.

### 2.85 Category and cohort reporting

Category applicability remains a derived diagnostic view and never becomes a
weighted category metric. `not_present` and `not_applicable` categories remain
visible in the audit record but do not enter category-coverage denominators.

Every cohort artifact records eligible fixture IDs, fixture count, exclusion
reasons, and denominator provenance. A cohort with no eligible fixture has
`no_formal_evaluation_basis`. A single-fixture subtype result may be formal for
that named fixture and need not be downgraded to `diagnostic_only`, but it must
not claim source-type-wide statistical generality.

### 2.86 Annotation-quality review triggers

Critical-density and annotation-quality triggers affect gold review, approval,
and Q10 authority closure. They are not candidate quality failures.

The frozen trigger reason codes are:

- `critical_density_review_required`;
- `critical_inflation_review`;
- `over_segmentation_review`;
- `under_segmentation_review`;
- `duplicate_claim_review`;
- `category_omission_review`.

All numeric trigger values remain `pending_calibration`. Gold subject to an
uncompleted required review cannot obtain formal authority. Reviewers cannot
inspect candidate results and then alter the critical distribution.

### 2.87 Lane-local outcome identity and reviewed causal links

There is no global canonical failure ID across lanes. Each lane and metric
observation has its own immutable `failure_event_id` or `outcome_id`.

Reviewed causal relations may use:

- `caused_by`;
- `same_root_cause_as`;
- `derived_from`.

Only human-approved relations may create a `causal_group_id`; temporal or
textual proximity cannot merge outcomes automatically. Coverage and support
retain different outcomes and denominators. Parser and end-to-end outcomes
also remain independent.

Within one named denominator, the formal scoring-unit ID—such as expected
claim, generated claim, or structure assertion ID—prevents duplicate counting.
Causal grouping supports root-cause reporting only. It cannot delete or merge
another lane's formal failure.

For example, an OCR omission of a negation may be reviewed as the cause of a
parser mismatch and an end-to-end contradiction. Both lane outcomes remain;
the causal link explains their relationship without pretending they are the
same measurement.

### 2.88 Blocking and aggregation contract governance

The blocking and aggregation contract is independent, versioned, immutable,
and content-addressed. It records at least:

- contract ID, version, and digest;
- rule ID and version;
- trigger state and prerequisites;
- disposition;
- origin and blocking scope;
- propagation rule;
- aggregation eligibility;
- named denominator;
- N/A and exclusion handling;
- rationale;
- proposer, reviewer, approver, and timestamps;
- dependent benchmark, schema, gold, and scorer versions and digests;
- superseded-contract reference when applicable.

Formal contracts contain no `pending_classification` capable of changing a
result. Rule or classification changes are scoring-relevant: they publish a
new contract and manifest and reevaluate every dependent result. When frozen
candidate and reference artifacts remain compatible, replaying mapping and
scoring is sufficient; parser or LLM execution is unnecessary. Old contracts
and results remain immutable.

### 2.89 Q12 status, pending decisions, and plain-language trade-offs

The formal status is:

`Q12 blocking and aggregation topology frozen; evidence-dependent classifications and numeric formulas pending`

Frozen in Q12 are the authority/quality axes, blocker-rule topology, critical-
claim and source-support blocker semantics, parser critical-dependency
derivation, fabricated-locator invariant, minimal-scope propagation,
hierarchical gate-vector topology, importance strata, partial-state vectors,
typed denominator rules, category diagnostic responsibility, annotation-
quality trigger topology, lane-local outcome identity, reviewed causal links,
and immutable contract governance.

Still pending are Q11 metric-specific gate constants, Q12 evidence-dependent
blocker classifications and critical-density numeric triggers, other discrete
invariants lacking fixture or gold evidence, Q13 metric-specific comparison-
policy evidence and numeric calibration, Q14 metric-specific parser
  measurement formulas and evidence-supported aggregation selections, and Q15
  repeat-policy, compatibility, and diagnostic-method evidence. Q13's
  non-numeric baseline-comparison and artifact topology, Q14's deterministic-
  scoring topology, and Q15's non-inferential repeated-run topology are frozen
  below.

In plain language:

1. **A trustworthy failure stays trustworthy.** Authority says whether the
   measurement can be believed; blocking says what the decided quality means.
2. **One observed fact gets at most one primary blocker rule.** Diagnostic
   causes explain the failure without multiplying punishment.
3. **Critical means complete truth conditions must survive.** A missing
   condition, negation, or required evidence cannot be averaged away.
4. **A single confirmed hallucination cannot hide behind a complete note.** A
   citation or many correct claims do not compensate for unsupported semantic
   content.
5. **Structure blocks when it changes meaning.** Ordinary layout loss is
   measured, while fabricated locators and truth-changing table, formula, or
   renderer errors block.
6. **Results roll upward without becoming one score.** Fixtures feed source
   cohorts and lane vectors, preserving source diversity and preventing long
   documents from dominating.
7. **Nothing applicable is not perfect performance.** A zero denominator is
   `no_formal_evaluation_basis`, never zero or one hundred percent.
8. **Causation is reviewed, not guessed.** Related failures remain valid in
   their own lanes even when a human confirms they share one root cause.

### 2.90 Q13 status, full-profile prerequisite, and comparison levels

The formal status is:

`Q13 non-numeric baseline-comparison and artifact topology frozen; metric-specific relative/recovery applicability, schema realization, and numeric calibration pending.`

The `full` profile remains a global prerequisite for any formal baseline or
candidate comparison. If the execution does not include all 13 canonical
cases, its full manifest is absent or incomplete, its canonical fixture, gold,
or review prerequisites are incomplete, or it is a smoke or partial run, no
formal comparison baseline exists. A direct baseline/candidate calculation may
be published only with `result_role=diagnostic_only`. Independently
authoritative absolute metric evidence for either side remains available, but
the diagnostic calculation cannot support formal non-regression, improvement,
complete-benchmark, or adoption claims.

Whether a failure is full-profile/global or pair-local is determined by its
ownership and the versioned dependency manifest, not by a generic error label
such as `missing artifact` or `authority failure`. Absence of full-profile
identity, omission of a required canonical case from the run, an invalid shared
manifest, or an incomplete shared fixture, gold, or review prerequisite needed
by the formal baseline prevents that baseline from existing. Every direct
baseline/candidate comparison publication is then `diagnostic_only`. This does
not erase independently authoritative absolute evidence for either baseline or
candidate within its own unaffected scope.

Once full-profile execution and bundle identity exist, eligibility is checked
for every `metric × fixture × lane` pair. A scoped invalidity, missing artifact,
authority failure, or contract incompatibility follows Q10's minimal affected
scope: it blocks only dependent comparative outcomes and gates. It does not
erase another pair with complete dependencies, candidate absolute-quality
evidence, or an independently established hard blocker. A required scoped
failure still prevents a complete bundle or adoption claim until every required
scope closes.

After the formal baseline and shared full-profile prerequisites are established,
candidate-specific, mapping-specific, and metric/fixture/lane pair-local
failures propagate through Q10's minimal affected scope. Conversely, a shared
gold, scorer, manifest, or other dependency affecting multiple pairs propagates
to every dependent scope identified by the manifest; it must not be mislabeled
as one pair-local failure. Review incompleteness therefore affects only the
scopes that actually depend on that review, except where the manifest identifies
it as a shared formal-baseline prerequisite.

The contract therefore distinguishes four levels:

1. authoritative absolute metric evidence;
2. diagnostic pair comparison;
3. formal pair comparison;
4. full-bundle or adoption claim.

A P03 locator timeout is a scoped pair failure when P03 entered the established
full-profile run and the missing dependency is the locator-pair result. It is
full-profile absence when P03 never entered the required full run, full-run
identity was not established, or the timeout represents failure of a shared
full-profile prerequisite. Ownership and the dependency manifest decide which
case applies.

**Plain language and trade-off.** A broken pair blocks what depends on that
pair, while a run that was never complete cannot be relabelled as a formal
benchmark. This preserves useful local evidence, at the cost of forbidding a
convenient subset from standing in for the preregistered whole.

### 2.91 Unit dispositions, named denominators, and valid zero

Denominator handling has two stages. First, apply only approved unit-level
dispositions to their expressly named metric unit, lane, or denominator:
approved `not_applicable`, gold `unavailable`, approved `unscorable`, approved
source-side exclusions, and the existing `not_present` and
`present_but_optional` semantics. Second, count the eligible units remaining in
the named denominator.

If eligible units remain, the metric is evaluated over that formal denominator.
If the eligible-unit count is exactly zero, the existing Q12 result is
`no_formal_evaluation_basis` with `quality_decision=not_evaluated`; the result
is never represented as zero percent or one hundred percent. Provenance must
still distinguish a metric contract that originally had no units, approved
`not_applicable`, gold `unavailable`, and approved source-side exclusions that
exhausted an originally non-empty denominator.

A required result missing because of crash, timeout, missing artifact,
schema/digest/version failure, invalidity, or unresolved closure is not a legal
zero denominator. The affected comparison references the existing validity,
authority, or comparison-closure record instead of claiming
`no_formal_evaluation_basis`.

An execution that is valid and produces a complete, schema-valid empty output
against a positive gold denominator may produce a valid zero-quality coverage
result. That zero remains subject to Q12 critical-omission, hard-blocker, and
other quality rules; legality of the measurement does not imply acceptable
quality.

**Plain language and trade-off.** “Nothing was eligible to test” differs from
“the parser returned nothing” and from “the run broke.” Keeping those cases
separate prevents failure laundering, although it requires explicit
denominator provenance.

### 2.92 Exact zero, near-zero policy, and relative comparison

Metric-native absolute difference is the authoritative comparison primitive.
Exact zero is determined only from the authoritative native representation:
an integer, exact rational, canonical Decimal under its versioned Decimal
context, or another representation expressly approved by the metric contract.
A display-rounded value such as `0.00` has no zero-classification authority.

When the authoritative baseline is exactly zero, an eligible absolute
comparison may still run, but the relative result is `not_defined`. Hidden
epsilon substitution and claims of infinite improvement are forbidden. Metric
direction and canonical unit remain native to each higher-is-better,
lower-is-better, bounded-rate, exact-count, error, or distance metric.

Mathematical divisibility of a non-zero baseline does not itself permit a
formal relative comparison. A versioned metric contract must expressly approve
relative meaning, valid domain, prerequisites, exclusions, policy and
calibration dependencies, canonical representation, and direction. If that
validity depends on a near-zero boundary that remains `pending_calibration`,
formal relative comparison is `not_permitted`. No non-zero value may be
self-classified as near-zero, no domain may be inferred from candidate results,
and no implicit boundary or epsilon may be introduced.

A future metric contract may, with independent evidence, approve a relative
comparison over a stated domain without a near-zero exclusion. Q13 does not
pre-authorize that metric-specific choice.

**Plain language and trade-off.** Absolute change remains meaningful at zero;
relative change does not automatically become meaningful merely because a
division is possible. This gives up eye-catching ratios in exchange for stable,
auditable claims.

### 2.93 Restricted recovery-from-zero diagnostic

A recovery-from-zero indication is available only when a versioned metric
contract establishes both that zero means no desired success was achieved and
that the candidate movement is favorable in that metric's direction. A
higher-is-better success count or coverage metric may eventually qualify.
Lower-is-better error, distance, or failure-rate metrics normally do not: when
baseline error is zero, candidate error above zero is regression, never
recovery. A metric whose contract does not support recovery produces no such
diagnostic.

The indication is derived diagnostic information, not a metric, score,
authority decision, gate, blocker, `quality_decision`, or formal improvement
conclusion. Absolute floors, hard blockers, non-regression, and improvement
gates remain independent. Without an eligible baseline, candidate
absolute-quality and hard-block evidence may still stand, while the dependent
comparative gate is `not_evaluated`. The exact JSON field name remains a schema
decision.

**Plain language and trade-off.** Moving away from zero is called recovery only
when zero actually means total absence of desired success. The restriction
avoids praising a worsening error metric, at the cost of requiring
metric-specific evidence before using the diagnostic.

### 2.94 Missing required pairs and scoped `not_evaluated`

A missing required pair remains in the preregistered comparison scope. It must
not be removed, imputed, filled with zero, reweighted, converted to N/A, or
replaced by a successful subset. Successful pairs remain immutable, replayable
evidence.

`not_evaluated` applies only to the comparative cohort outcome or comparative
gate that depends on the missing pair. It does not overwrite candidate
absolute-quality outcomes, candidate hard blockers, other fixtures, metrics,
lanes, or cohorts that do not depend on that pair. A missing required pair is a
comparison closure failure, not `no_formal_evaluation_basis`. The latter is
used only when approved applicability and exclusion rules leave the named
denominator with exactly no eligible units.

**Plain language and trade-off.** A required observation that failed to arrive
cannot disappear from the contract. This makes incomplete cohorts unable to
produce a convenient formal comparison while retaining every valid result for
diagnosis and replay.

### 2.95 Orthogonal comparator subrecords and decision ownership

Comparator execution is represented by two orthogonal semantic subrecords.
Exact field and enum names remain for schema realization; Q13 creates no mixed
absolute/relative/authority/quality super-status.

The absolute comparator subrecord records whether the comparator is applicable,
whether it executed, the selected metric-native comparator, the
comparison-policy contract reference, pair identity and eligibility inputs,
and the absolute result when executed. If it did not execute, its primary
blocking reason answers only why the absolute comparator did not run, using a
narrow comparison-specific reason or a stable reference to the upstream
validity, authority, or denominator record. Existing Q10 and Q12 reasons are
referenced, not copied. Authoritative raw inputs without complete formal-
comparison prerequisites may support a diagnostic absolute calculation, but
publication remains `result_role=diagnostic_only`.

The relative comparator subrecord records whether a versioned metric contract
preregistered and permits the comparator, whether its approved domain and
policy prerequisites are complete, and its relative disposition. The semantic
dispositions cover: performed; not defined because the authoritative baseline
is exactly zero; not permitted because required policy or calibration is
incomplete; not part of the approved metric contract; and not reached because
prerequisite absolute-pair eligibility did not hold. A relative result exists
only when performed. Relative dispositions do not compete with the absolute
primary blocking reason.

The comparison-policy contract versions the following evaluation order:

1. Resolve existing upstream validity, authority, applicability, and
   denominator records.
2. Establish the full-profile context and requested `result_role`.
3. Validate preregistered pair membership, pair identity, and contract
   compatibility.
4. Determine absolute-comparator applicability and eligibility.
5. Execute and save the metric-native absolute result; if execution is blocked,
   save the blocking reason or upstream record reference according to the
   versioned precedence.
6. Independently determine whether a relative comparator belongs to the
   approved metric contract.
7. Validate its approved relative domain and policy or calibration
   prerequisites.
8. Save the relative disposition, and save a relative result only when the
   comparator was performed.
9. Leave gate decisions to Q11 records and evaluations and quality decisions
   to Q12 records.

When the absolute comparator does not execute, its primary reason is the first
applicable condition in this ordered evaluation that prevents absolute
execution. If the actual reason already exists in a Q10–Q12 record, Q13 stores
only that record's stable ID, version, and digest rather than introducing a
synonymous reason. Additional diagnostic facts may be retained but cannot
change the primary reason. Exact-zero, relative `not_defined`, relative
`not_permitted`, and other relative dispositions belong only to the relative
subrecord and never compete for absolute-reason precedence.

`role=characterization_baseline` is a role and valid-zero is a diagnostic fact;
neither may serve as the absolute primary failure reason. The ordered evaluation
and primary-reason precedence are part of the versioned comparison-policy
contract so that replay of the same pair cannot choose a different primary
reason merely because an implementation checked prerequisites in another
order.

Comparator-result artifacts own neither gate nor quality decisions. Q11 gate
records and evaluations own gate decisions, and Q12 records own
`quality_decision`; Q13 does not rename or duplicate `authority_status`,
`result_role`, or `quality_decision` and creates no fourth pass/fail state.
`role=characterization_baseline` identifies purpose only: it neither grants nor
denies formal comparison authority and does not imply `diagnostic_only`.
`baseline_characterization_only` is not a primary failure reason. Exact-zero
may be stored as a diagnostic fact; near-zero cannot be a diagnostic
classification before its policy is approved.

**Plain language and trade-off.** Absolute execution, relative execution,
authority, gates, and quality answer different questions. Separate records are
more verbose, but they prevent one ambiguous status from silently deciding all
of them.

### 2.96 Artifact, digest, and ownership boundaries

Q13 uses Q3's canonical serialization and digest boundary. In particular, no
artifact embeds its own digest in its canonical payload; an external manifest,
artifact index, or binding record stores that digest. Stable logical IDs,
schema and contract versions, and dependency digests may appear in the payload.

| Record or artifact | Owns | Must not own |
| --- | --- | --- |
| Comparator-result artifact | Stable pair identity; baseline and candidate metric-artifact references and digests; metric and comparison-policy contract references; denominator identity and provenance references; authoritative raw values; direction, canonical unit, and numeric representation; absolute applicability, execution, and result; relative eligibility, disposition, and result; required upstream stable references | Q10 authority, Q11 gate decision, Q12 quality decision, run-receipt observations, or its own digest |
| Governance/authority record | Proposer, reviewer, approver, and adjudicator identity; review and approval timestamps; reason, rationale, lifecycle, governance contract, authority decision, and successor or superseded references | Metric calculation or an in-place mutable history |
| Gate record/evaluation | Q11 gate contract, an approved threshold when one exists, gate comparator and equality rule, and gate decision | Raw-metric recomputation or Q10 authority |
| Binding/publication manifest | Immutable references binding fixture and cohort metric-result artifacts, comparator results, Q10 authority records, Q12 blocker and quality outcomes, Q11 gate evaluations, Q13 comparison outcomes, Q15 run-plan manifests, repeated-run collection manifests, statistical diagnostic artifacts, governance records, receipts, result role, and publication context | Metric or statistical recalculation or copied or re-owned authority, quality, gate, comparison, diagnostic, governance, or receipt decisions and content |
| Run receipt | Run ID, execution timestamp, latency, hardware, memory and resource diagnostics, cost, and operational details | Comparator-result calculation or comparator-result digest inputs |

Governance/authority records are immutable, content-addressed, separately
versioned, and revised only through successors. When governance affects
comparison authority, the comparator artifact or binding manifest references
the stable record ID, version, and digest. Run-receipt observations are outside
the scoring-relevant comparator payload digest, but a run receipt has its own
digest, remains immutable, and is never updated in place. “Volatile” therefore
means excluded from another artifact's scoring digest, not mutable.

**Plain language and trade-off.** Calculations, approvals, gate decisions,
publication bindings, and operational observations have separate owners. This
adds references, but makes a replay show exactly which change did—and did not—
alter the comparison.

### 2.97 Immutable comparison revision matrix

Old artifacts remain immutable and may only be superseded. Required work is
selected by the changed dependency:

| Change | Required work |
| --- | --- |
| Gate constant only | Publish a new gate contract, gate evaluation, and binding/publication manifest; reuse the compatible comparator-result artifact. |
| Comparison-policy selection rule or comparator semantics with compatible metric results | Publish a new comparison-policy and comparator-result revision and recompare; do not rescore or re-execute. |
| Metric unit, denominator, formula, state transformation, direction, or authoritative numeric representation | Publish a new metric contract; rescore affected fixture results; rebuild dependent cohort, comparator, and publication artifacts. Publish a new scorer contract only if scorer implementation or compatibility also changes. |
| Cohort aggregation contract | Reaggregate compatible fixture metric results and rebuild dependent comparator and publication artifacts; do not recompute item or fixture metrics and do not re-execute. |
| Scorer implementation identity, deterministic calculation behavior, or compatibility | Publish a new scorer contract; rescore affected trusted artifacts when calculation behavior may change. Do not re-execute a parser or LLM unless candidate raw output or an execution dependency changed, is missing, or is untrusted. |
| Display-only rounding or presentation | Publish only a new non-authoritative display or publication representation; do not change authoritative metric values, rescore, or re-execute. |
| Gold | Rescore baseline and candidate within the affected dependency scope and rebuild dependent cohort, comparator, and publication artifacts; trusted raw output normally does not require re-execution. |
| Candidate-specific mapping | Rescore the affected candidate and rebuild dependent cohort, comparator, and publication artifacts; trusted raw output normally does not require re-execution. |
| Candidate input, implementation, configuration, execution contract, or trusted output | Re-execute, rescore, reaggregate where applicable, and recompare. |
| Missing or untrusted raw output | Re-execute before rescoring and recomparison. |
| Additional run receipt | Publish a new immutable receipt; leave fixture and cohort metric-result artifacts and the comparator-result artifact unchanged. |
| Governance or authority revision | Publish a successor governance record and a new binding/publication manifest. Publish a dependent comparator-result revision only if comparator-policy input or the calculation changed; if only publication authority changed, reuse the comparator result. |

The metric contract owns metric semantics and formula. The comparison-policy
contract owns comparator selection and semantics. The scorer contract owns
implementation identity, deterministic calculation behavior, and compatibility
only; it cannot override the metric contract. Aggregation-contract changes act
on compatible fixture metric results rather than changing item or fixture
calculation.

**Plain language and trade-off.** A policy edit should not automatically rerun
the parser or an LLM, and a gate edit should not recalculate an unchanged
absolute delta. Dependency-scoped revision minimizes cost while immutable
predecessors preserve the complete audit trail.

### 2.98 Q14 status and metric-contract authority

The formal status is:

`Q14 deterministic-scoring and artifact topology, coverage state-vector formulas, support exact-count/non-dilution policy, and Q14-owned metric/scorer/result/aggregation schema realization frozen in section 2.141; metric-specific parser measurement formulas, evidence-supported aggregation selections beyond the v1 fixture vector, comparison artifact realization, and numeric calibration pending.`

Every formal metric has an immutable, versioned, content-addressed metric
contract. That contract owns its scoring unit, named-denominator semantics,
applicability, deterministic formula or state transformation, direction,
canonical unit, authoritative numeric representation, and aggregation
eligibility.

Q12 typed denominator dispositions and their authority records own whether a
unit has an approved exclusion or applicability disposition. A metric contract
defines only how it consumes an already authoritative disposition and how that
disposition affects its named denominator. It cannot create, reclassify, or
override an exclusion, and a scorer cannot decide that a unit should be
excluded.

An immutable metric-registry manifest selects the exact approved metric-
contract IDs, versions, and digests for one benchmark release. It is not a
mutable catalog and owns no formula. A scorer contract owns only implementation
identity, supported metric-contract versions, deterministic execution
requirements, and compatibility. It cannot override a metric formula. The
benchmark manifest binds the exact registry, metric-contract, and scorer-
contract digests with their scoring dependencies.

Integer counts and exact rational results need no artificial scoring-precision
or tolerance slot. Display rounding is non-authoritative. A metric-specific
measurement-boundary policy slot exists only for a family whose measurement
semantics genuinely require one.

**Rationale, trade-off, and misuse protection.** The metric contract defines
the ruler; the registry selects rulers; the scorer executes them. More contract
references increase governance work, but prevent hidden scorer code or a
post-result edit from changing a formula, denominator, or exclusion.

**Example and boundary.** A coverage contract names `expected_claim` as its
unit and defines three separate rate components. A Q11 gate may consume one
component but cannot recompute it or assign partial credit. Frozen now are the
ownership, immutability, and binding topology. Exact schema fields remain a
policy-realization task. Measurement calibration remains pending only for an
approved metric family that genuinely needs a boundary or tolerance.

### 2.99 Coverage v1 exact state-vector scoring

For every authority-closed expected-claim denominator, coverage v1 preserves
separate exact counts and exact rational rates for:

- `fully_covered`;
- `partially_covered`;
- `not_covered`.

`fully_covered_rate` is a formal metric component. The partial and not-covered
rates are also independent formal components. Q14 v1 creates no coverage
points, weighted sum, combined scalar, semantic-component score, or numeric
partial credit. Missing optional components do not create another numerator.

`unresolved` is not a decided-state numerator, zero, failure, success, or
exclusion. It remains in Q10 provisional and audit records. If a blocking
unresolved item can still change a coverage state or denominator, the affected
scope cannot publish a complete formal coverage metric or calculate a decided
subset rate and label it complete. Closure must precede an authoritative
calculation over the formal named denominator.

Critical claims retain the same numeric components, while their Q12 blocker
records remain independent and non-compensating.

**Rationale, trade-off, and misuse protection.** Separate states reveal a move
from no coverage to partial coverage without inventing a fractional reward.
This gives up one convenient ranking scalar but prevents candidates from
touching many topics superficially to collect arbitrary credit.

**Example and boundary.** When a major claim moves from `not_covered` to
`partially_covered`, those two counts and rates change while the fully-covered
component does not. No combined point gain is reported. The v1 vector formula
and prohibition on partial credit are frozen now. Numeric partial credit has no
v1 policy or calibration slot; any future proposal requires a new benchmark
and scorer-contract revision.

### 2.100 Support exact counts, diagnostic rates, and consistency

Generated-claim primary support states remain exactly the Q8 enum:

- `supported`;
- `partially_supported`;
- `unsupported`;
- `contradicted_by_source`;
- `overstated`;
- `unresolved`.

`candidate_internal_contradiction` remains a separate candidate relation and
consistency outcome. It does not enter the primary support denominator, alter a
claim's Q8 state, or create a new support state. Its quality effect references
the existing Q12 blocker outcome.

Formal support calculation preserves exact decided-state counts and their unit
IDs. Derived state rates may be stored only as distribution diagnostics. No
support rate, including `supported_rate`, may by itself support a formal
ranking, Q11 gate, comparative-improvement conclusion, support-quality pass, or
dilution of an unsafe claim. Formal support safety uses exact failure-state
counts, discrete failure presence, and Q12 blocker records. Q14 introduces no
new state for an adjudicated `partially_supported` claim; it references the Q8
and Q12 records that own segmentation, adjudication, and blocking.

`unresolved` may appear in provisional and audit vectors. It is not a failure,
success, zero, exclusion, or decided-state numerator. A decided-subset rate
cannot be presented as the complete formal support metric. While a blocking
unresolved item can affect the result, Q10 prevents the affected scope from
publishing a complete formal support calculation; closure must come first.

Reviewed segmentation prevents a candidate from choosing arbitrary sentence
boundaries, but the candidate still controls output volume. Support ratios are
therefore not presumed to resist verbosity gaming.

**Rationale, trade-off, and misuse protection.** Many supported trivial claims
cannot dilute one unsupported, contradicted, or overstated claim. Diagnostic
rates aid distribution review but lose formal ranking convenience in exchange
for safety and stable denominator semantics.

**Example and boundary.** A candidate with many supported definitions, one
overstated claim, and one candidate-internal contradiction retains Q8 support
counts plus a separate consistency relation. The scorecard binds the applicable
Q12 blocker records; no ratio compensates for them. Frozen now are exact counts,
non-dilution, diagnostic-only rates, and consistency separation. Any future
formal use of a support rate requires a new contract revision and independent
evidence, not calibration of the v1 rule.

### 2.101 Parser metric families, units, and anti-duplication

Parser evaluation uses separate, non-compensating metric families rather than
a parser-global composite. The families cover at least:

- semantic evidence preservation;
- source-text and span preservation;
- OCR or ASR recognition;
- reading order;
- section and hierarchy structure;
- table text and row, column, span, and header alignment;
- code preservation;
- formula preservation;
- locator availability;
- discrete locator identity correctness;
- locator geometry, span, and timing accuracy;
- duplicate and noise output.

Parser semantic-preservation units are source-side `evidence_item` records,
approved source spans or source references, `structure_assertion` records, or
`locator_assertion` records. Generation and end-to-end coverage units are
`expected_claim` records. A parser denominator must not substitute expected
claims for its source-side units.

One assertion ID may enter only one parser denominator. Categories, repeated
references, or downstream effects cannot create a second parser scoring unit.
When one source fact causes both parser loss and a downstream claim loss, the
two lane outcomes remain separate and use only a Q12 reviewed causal relation;
they receive no cross-lane weight or composite penalty.

The benchmark retains exactly three lanes: Parser, Generation, and End-to-end.
It creates no renderer lane. Renderer-origin loss is a causal or diagnostic
origin for an end-to-end outcome unless a future benchmark revision establishes
a different formal boundary.

CER/WER tokenization and normalization, IoU, temporal delta, span overlap,
table-alignment distance, formula semantic equivalence, and comparable
measurement methods require metric-specific policy slots. Q14 freezes no
formula, boundary, tolerance, or constant for those slots.

**Rationale, trade-off, and misuse protection.** Text recovery, table position,
formula fidelity, and locator accuracy are different rulers. Multiple artifacts
cost more to review, but a large volume of ordinary text cannot hide a misplaced
critical value or corrupt formula, and one assertion cannot be counted twice.

**Example and boundary.** If P02 retains `100 ms` but places it under the wrong
row header, text preservation and table alignment remain separate parser
results. A downstream semantic loss is another lane outcome linked causally.
The family topology, unit boundary, anti-duplication rule, and three-lane limit
are frozen now. The named measurement methods remain evidence-dependent policy
slots with calibration only where a real measurement boundary is required.

### 2.102 Generation, end-to-end, and readability boundary

Generation and end-to-end lanes may share the approved coverage and support
formula families. Each result nevertheless binds a different lane identity,
input authority, candidate-output identity, and complete dependency chain.
Generation binds the frozen `reference_document`; end-to-end binds the raw
source through parser, generator, and final rendered note.

Parser-caused downstream loss remains a separate outcome in each affected lane
and is connected only by a reviewed Q12 causal relation. End-to-end quality
cannot compensate for parser or generation failure.

Structure, duplication, noise, and output-side non-claim facts already decided
by the gold and mapping ontology may use their deterministic metric families.
Q14 v1 defines no subjective readability scalar, no human-rubric readability
metric or policy slot, and no LLM judge. Subjective readability is outside v1,
not `pending_calibration`. A future addition requires a separately versioned
ontology, rubric, review authority, inter-review evidence, and benchmark
revision.

**Rationale, trade-off, and misuse protection.** A shared formula avoids lane
semantic drift while distinct dependency chains reveal where loss occurred.
Excluding subjective readability leaves some user experience unmeasured, but
prevents an unreviewed rubric or model preference from becoming authority.

**Example and boundary.** A generator may fully cover a limitation from the
reference document while end-to-end output loses its negation after OCR. The
two results share a coverage formula but not an artifact identity. Shared
formula families, lane-specific identity, non-compensation, and the v1
readability exclusion are frozen now. Subjective readability is a future
benchmark revision rather than a policy or calibration slot.

### 2.103 Importance-stratum vectors

Critical, major, and minor expected claims retain separate coverage count and
rate vectors. Critical results also retain their independent Q12 blocker
outcomes through the scorecard binding layer.

Q14 v1 forbids cross-stratum averages, cross-stratum macro aggregation,
importance-weighted or unweighted overall completeness, and every combined
cross-stratum scalar. Raw cross-stratum totals may be retained only as audit
inventory that verifies claim membership. They must be labeled as inventory,
not as formal or diagnostic completeness quality.

Category views remain derived diagnostics and cannot create another importance
or scoring axis.

**Rationale, trade-off, and misuse protection.** Separate strata prevent many
minor successes from hiding one critical omission. Reports lose a single
headline completeness number but avoid explicit or implicit importance
weights.

**Example and boundary.** Full coverage of every minor claim does not offset a
partially covered critical claim. The three vectors and the critical blocker
remain visible without an overall score. Separate strata and all cross-stratum
aggregation prohibitions are frozen now. Importance weights and an overall
completeness scalar have no v1 policy or calibration slot; a change requires a
future benchmark revision.

### 2.104 Item, fixture, cohort, and scorecard artifact ownership

Q14 uses four calculation and binding layers:

| Layer | Owns | Must not own |
| --- | --- | --- |
| Item disposition or mapping artifact | Q6/Q8 semantic units and states, mappings, candidate relations, and Q10 closure-evidence references | Fixture or cohort calculation, Q11 gate, Q12 blocker or quality, Q13 comparison |
| Fixture metric-result artifact | One fixture, lane, and metric contract; authoritative unit IDs; numerator and denominator IDs and counts; exact rational or result vector; applicability and exclusion provenance; input and contract digests | Authority decision, hard blocker, quality, gate, comparison, governance, or receipt |
| Cohort metric-result artifact | Referenced fixture metric-result IDs and digests; frozen cohort membership; approved aggregation contract; exact aggregate result when authorized | Item remapping, fixture rescoring, authority, blocker, quality, gate, or comparison |
| Scorecard or binding/publication manifest | References binding metric results, Q10 authority records, Q12 blocker and quality outcomes, Q11 gate outcomes, Q13 comparison outcomes, Q15 run-plan manifests, repeated-run collection manifests, statistical diagnostic artifacts, governance records, and receipts | Recalculation or duplicated ownership of any referenced decision or record |

A metric result may reference the item-state IDs used in its deterministic
calculation. It cannot own, derive, or recompute a Q12 blocker. Hard-block,
quality, gate, and comparison references belong to the scorecard or existing
Q13 `Binding/publication manifest` layer. That manifest references governance
and receipt records without copying or re-owning their content.

Every artifact is immutable, versioned, and content-addressed. Its own
canonical payload never contains its own digest; an external manifest, index,
or binding records that digest under the existing canonical serialization
boundary.

**Rationale, trade-off, and misuse protection.** Item records decide states,
metric artifacts perform arithmetic, and the scorecard binds independent
decisions. Following references is more verbose, but prevents a scorer from
recreating Q10-Q13 authority, blockers, gates, or comparisons.

**Example and boundary.** A Q8 `not_covered` item feeds a coverage count; its
fixture metric-result contains no `hard_blocked` value. Q12 owns the blocker,
and the binding manifest references both. The four-layer ownership and digest
boundary are frozen now. Exact schema and manifest fields remain a realization
task, not an invitation to change ownership.

### 2.105 Within-cohort aggregation topology

The fixture vector is always the authoritative cohort foundation. Q14 creates
no universal default macro. Each metric contract preregisters one aggregation
disposition with one of these frozen semantics:

- `fixture_vector_only`;
- an evidence-approved fixture-equal macro;
- a preregistered worst or minimum independent metric;
- another future approved metric-specific aggregation.

These names describe frozen semantics, not final schema enum names. Fixture-
equal macro is a preferred candidate only for a bounded rate proven comparable
across fixtures. No unimplemented metric receives a formal aggregation until
fixture, gold-denominator distribution, and metric-behavior evidence support
the selection.

Micro rates, pooled-denominator rates or totals, and exact-count cohort sums are
diagnostic or audit evidence only. They cannot be formal gate or comparative-
improvement inputs and cannot claim cross-fixture quality. A worst or minimum
result gains formal use only as a preregistered independent metric or gate
input; it cannot be selected after candidate results are visible.

Approved exclusions and missing required fixtures retain the Q12 and Q13
rules. A missing required fixture cannot be excluded, imputed, filled with
zero, or used to shrink the preregistered cohort. A single-fixture result may
be formal for that fixture but is not called a macro and cannot claim subtype
generalization.

Per-metric aggregation selection is an evidence-dependent policy choice, not
numeric calibration. Q14 sets no aggregation threshold or gate constant; Q11
gate constants remain in Q11's `pending_calibration` frontier. Exact counts and
exact rational formulas receive no artificial precision or tolerance slot.

**Rationale, trade-off, and misuse protection.** Fixture vectors prevent long
or claim-rich sources from silently dominating. Some cohorts will lack a
formal summary until evidence supports one, but candidates cannot choose macro,
micro, or worst-case after viewing results.

**Example and boundary.** A claim-rich fixture and a claim-light fixture retain
separate authoritative rates. Their pooled rate is diagnostic. A macro appears
only after the metric contract preregisters it from independent evidence. The
fixture-vector and aggregation-disposition topology are frozen now. The formal
selection for each metric remains an evidence-dependent policy slot; numeric
calibration belongs only to measurement families that genuinely need it.

### 2.106 Canonical replay and revision matrix

A fixture metric-result binds its fixture, lane, metric identity, authoritative
unit IDs, numerator and denominator IDs and counts, exact state counts, exact
rational or result vector, applicability and exclusion provenance, input
artifact digests, metric-registry, metric-contract and scorer-contract digests,
formula identity and version, item disposition or mapping references, and
projection or alignment references when applicable.

A cohort metric-result binds compatible fixture-result IDs and digests, frozen
membership, the aggregation contract, and an exact aggregate only when that
aggregation has authority. Display values remain non-authoritative. All
predecessors remain immutable and may only be superseded.

| Change | Required work |
| --- | --- |
| Q11 gate constant or gate contract | Reevaluate the gate; reuse compatible metric results. |
| Q13 comparison-policy contract | Recompare compatible metric results; do not rescore or re-execute. |
| Cohort aggregation contract | Reaggregate compatible fixture metric results; do not recompute item or fixture metrics and do not re-execute. |
| Metric unit, denominator, item formula, or state transformation | Rescore affected fixture results, then rebuild dependent cohort results. |
| Gold, mapping, projection, alignment, or applicability | Rescore within the dependency scope, then rebuild dependent cohort, comparison, and publication artifacts. |
| Candidate input, implementation, configuration, execution contract, or trusted output | Re-execute, then rescore and rebuild dependent artifacts. |
| Trusted raw output unchanged | Do not re-execute merely because a gate, comparison, or aggregation contract changed. |
| Raw output missing or untrusted | Re-execute before rescoring. |
| Governance or receipt metadata addition | Publish a new immutable record or binding; leave metric calculation unchanged unless a scoring-relevant authority input changed. |

**Rationale, trade-off, and misuse protection.** Gate edits rejudge, comparison
edits recompare, aggregation edits reaggregate, formula edits rescore, and
candidate-output changes re-execute. Dependency tracking costs more than a
single result file but prevents unnecessary stochastic reruns and stale score
reuse.

**Example and boundary.** Changing an approved aggregation from fixture-vector
only to an evidence-approved macro reuses compatible fixture metric results and
creates a new cohort result. It does not rerun a generator. Canonical replay,
immutable revision, and dependency-scoped work are frozen now. Exact schemas
and compatibility evidence remain pending realization.

### 2.107 Q14/Q15 responsibility and remaining boundary

Q14 owns deterministic scoring units, approved states, exact count and rational
formulas, metric contracts, artifact topology, aggregation eligibility,
approved deterministic aggregation, canonical replay, and revision scope.

Q15 owns the finite-suite repeated-run, non-inferential statistical-diagnostic,
artifact, and adoption-authority topology defined below. Q14 makes no
statistical-significance or population-generalization claim from the 13
fixtures, and Q15 does not modify Q14 scoring units, formulas, metric authority,
aggregation, or replay ownership.

Frozen in Q14 are metric/registry/scorer ownership, Q12-controlled exclusion
consumption, coverage state-vector formulas without partial credit, support
exact counts and non-dilution, support/consistency separation, parser family
and unit topology, three-lane identity, the v1 readability exclusion,
importance-stratum separation, four-layer artifact ownership, fixture-vector
authority, aggregation-disposition topology, and deterministic replay.

The exact metric, registry, scorer, aggregation, fixture-result, and
cohort-result schemas are realized in section 2.141. Still pending in Q14
are comparison artifact realization and metric-specific parser unit
inventories and applicability; Q26 owns the note and rendered-projection
schemas and their closed enums. Q14 also retains
CER/WER tokenization and
normalization; IoU, temporal-delta, span-overlap, table-alignment, and formula-
equivalence contracts; evidence-supported aggregation selection; measurement
boundaries or tolerances only for metric families that genuinely require them;
and scorer compatibility and canonical replay evidence.

Numeric partial credit, importance weights, a universal macro, formal micro or
pooled aggregation, formal support-rate use, subjective readability, and a
renderer lane are not pending v1 decisions. They are prohibited or outside v1
and require a future benchmark revision.

**Rationale, trade-off, and misuse protection.** Q14 answers how approved facts
are deterministically calculated; Q15 answers how preregistered repeated results
may be bound and described without creating population inference or a second
quality authority. The boundary prevents deterministic arithmetic from
acquiring an unsupported confidence or generalization claim.

**Example and boundary.** Q14 may publish exact fixture vectors for all 13
cases. Q15 may bind repeated generation results and publish approved descriptive
diagnostics for that finite suite, but neither round can claim a population
confidence interval for all PDFs. Q14's deterministic boundary and Q15's
non-inferential boundary are both frozen; exact repeat policy, compatibility,
method activation, schema, and applicable numeric parameters remain pending.

### 2.108 Q15 status, uncertainty taxonomy, and fixed-suite estimand

The formal status is:

`Q15 finite-suite repeated-run, non-inferential statistical-diagnostic, artifact, and adoption-authority topology frozen; formal repeat count and scheduling, execution compatibility, diagnostic-method activation, schema realization, and applicable numeric calibration pending.`

The 13 canonical fixtures are a fixed conformance suite, not a random sample
from a source or production population. A formal claim is limited to its exact
benchmark version, fixtures or named cohort, lanes, metrics, execution
contracts, and run collections. It must not be generalized to all PDFs, Web
articles, YouTube captions, Chats, Screenshots, future provider executions, or
production traffic.

Q15 keeps these conditions orthogonal:

- Q14 deterministic scoring replay failure;
- deterministic parser execution-contract violation;
- Q15 stochastic execution variability;
- Q10 annotation or mapping unresolved state;
- provider or model compatibility drift;
- execution crash, timeout, or missing output;
- Q12 valid zero or hard blocker.

They do not form a combined uncertainty score. Statistics cannot turn an
invalid execution, unresolved authority, valid zero, or blocker into ordinary
run-to-run noise.

A Q15 estimand is finite-suite only. It binds a named suite or cohort, lane,
metric, baseline and candidate execution contracts when comparative, Q13-
eligible fixture pairs, and the repeated-run design. Fixture remains the
primary baseline/candidate paired unit under Q13. Runs are nested under
`candidate × fixture × lane × execution contract`. Claims, tokens, and evidence
items remain within-fixture Q14 units and are not independent cross-fixture
samples. The metric-specific functional form requires separate evidence and
contract approval and has no population interpretation.

**Plain language and trade-off.** The benchmark is a fixed exam, not a survey.
Keeping failures, reviewer disputes, provider drift, and stochastic variation
separate costs more records but prevents a generic uncertainty number from
hiding the reason evidence is limited.

### 2.109 Run-level pairing and comparative diagnostic ownership

Equal run ordinals do not create a statistical pair. Baseline R1 and candidate
R1 are not paired merely because they share a label. Run-level pairing requires
a preregistered, versioned rule and evidence for all applicable prerequisites:

- controllable shared randomness or a compatible seed policy;
- a matched execution block;
- observable provider and model revision compatibility;
- symmetric execution conditions;
- an approved pairing rule.

Paired scheduling may reduce time or provider drift, but schedule proximity is
receipt evidence and does not grant pairing authority. Without run-level
pairing authority, a publication may place baseline and candidate run vectors
side by side. A future approved method may calculate an unpaired finite-suite
diagnostic, but arbitrary one-to-one run deltas are prohibited.

Q13 continues to own pair eligibility, compatibility, comparator policy,
formal comparator results, and formal comparative-improvement conclusions. A
Q15 statistical diagnostic artifact may reference Q13 pair-eligibility and
compatibility records, compatible baseline and candidate Q14 per-run metric
results, and existing Q13 comparator results. It may calculate a versioned,
finite-suite, `diagnostic_only` statistical contrast. It cannot create a formal
pair, change comparator semantics, relabel a diagnostic contrast as a Q13
formal result, or produce a formal improvement conclusion.

**Example and misuse protection.** If provider randomness cannot be controlled,
the first baseline and candidate outputs remain collection positions rather
than paired observations. Pairing them after scores are known would permit
favorable post-result matching.

### 2.110 Four execution behaviors and lane-specific policy

Q15 distinguishes four behaviors:

1. **Scoring replay** reruns the Q14 scorer over the same trusted output bytes.
   The result and digest must reproduce. A mismatch is a Q14 deterministic
   scoring or replay failure and creates no new run.
2. **Deterministic system re-execution** runs a parser again with the same input
   and execution contract. Output disagreement when the contract promises
   determinism is conformance or invalidity evidence, not a variance sample.
3. **Stochastic repeat** performs a new independent execution of an explicitly
   stochastic model or component. It creates a new immutable output artifact
   and logical run identity.
4. **Retry attempt** retries one logical run under a preregistered transient-
   failure policy. Every attempt and receipt remains immutable, but retries do
   not increase run count or statistical sample size.

The lane policies are:

- A deterministic parser has one preregistered formal execution that produces
  its output. Q14 scoring replay verifies calculation replayability. Any extra
  preregistered parser re-execution is determinism-conformance evidence, not a
  Q15 repeated sample.
- Stochastic generation uses a preregistered formal run collection. Every run
  receives byte-identical Q5 `reference_document` input with the same digest.
- Every end-to-end run binds its parser-output identity. Before capture, its
  execution contract selects either reuse of one authority-closed deterministic
  parser artifact or re-execution of the complete pipeline for every run. One
  formal collection cannot mix these modes. Parser reuse estimates generation
  variability conditional on that parser artifact; full-pipeline execution
  observes complete execution variability. The estimands cannot be pooled.

Idempotent artifact replay and operational retry are not stochastic repeats.
No replay, retry, or parser conformance re-execution may inflate sample size.

### 2.111 Run membership, preregistration, and anti-selection

Every run has a Q15 run-membership role before output capture. For the Q29
interface, the exact closed enum is `formal_required | diagnostic`. Broader
Q15 run/collection schema realization remains pending. This run-membership
role is not Q13 `result_role`, does not modify or extend the Q13 enum, and does
not grant or withdraw Q10 authority, Q12 quality, or Q13 comparison authority.

A diagnostic run cannot be promoted after its output is known, replace a
missing or failed formal slot, or enter the same formal collection as formal
runs. The benchmark prohibits:

- best-of-N selection;
- dropping the worst run;
- post-result seed selection;
- silent retry replacement;
- selective missingness;
- post-capture membership or slot replacement.

All attempts and receipts remain immutable. A successful contract-approved
retry may close its original logical run without overwriting the failed
attempt. It does not create another formal observation.

**Plain language and trade-off.** The plan decides which runs count before the
answers exist. This can leave a formal collection incomplete after an
operational failure, but prevents a pool of diagnostic runs from becoming a
hidden best-of-N search.

### 2.112 Run-scoped blockers, vectors, and derived summaries

Every formal required run retains its independent Q12 blocker and quality
records. A hard blocker in any formal required run cannot be offset by another
run, a mean, an interval, or a majority. The collection therefore cannot
support unconditional adoption. A diagnostic-run blocker remains disclosed
adverse evidence, but does not retroactively enter or rewrite formal membership.
Whether it initiates governance review or a new preregistered evaluation is a
governance policy slot. Q15 creates no quality enum, candidate-level adoption
enum, or statistical pass/fail enum.

Each run's Q10-Q14 artifacts retain their existing authority. A repeated-run
collection manifest only binds a complete ordered set and creates no metric
authority. The full run vector is formal publication and audit evidence because
it exposes every authoritative, failed, missing, or invalid run record. Exact
blocker occurrence and exact execution-failure occurrence are verifiable facts.

These derived values are diagnostic only:

- blocker frequency;
- execution-failure frequency;
- mean;
- median;
- range;
- quantile;
- dispersion;
- variance.

A worst observed value may be published as an exact descriptive fact. It is not
a v1 adoption rule unless a future preregistered, non-compensating Q11 gate is
approved. Missing and invalid runs remain in collection membership but never
enter a numeric calculation.

### 2.113 Resampling, intervals, and annotation disagreement

Q15 v1 does not enable bootstrap or resampling output. It retains only an
evidence-gated diagnostic-method policy slot. Before activation, a method must
have an approved finite-suite estimand, exchangeability and dependence
justification, pairing rules, nested-run treatment, and method evidence.

If a future diagnostic method is approved, fixture is the outer resampling
unit. Runs may be handled only through its approved nested design. Claims,
tokens, and evidence items cannot be cross-fixture resampling units. A method
cannot pool source families or lanes, create or fill a missing pair, or gain
population or formal-gate authority. A source cohort with very few fixtures
publishes its complete fixture vector by default; without method evidence it
publishes no resampling output.

Q15 v1 prohibits population confidence intervals, p-values, alpha or
significance thresholds, statistically significant improvement, inferential
coverage claims, and any interval that overrides a floor, blocker, missing
pair, or authority failure. A deterministic fixed-suite result is exact and has
no sampling confidence interval. A future approved descriptive method may use
terms such as sensitivity interval, resampling band, empirical run range, or
empirical quantile band, but its method and formal name require a separate
contract. `Confidence interval` cannot name a fixed-suite result. A repeated-
execution diagnostic describes only the observed execution contract, not
future provider executions or a production population.

Gold, importance, segmentation, and mapping disagreement cannot enter a
candidate numerator or denominator, become candidate variance, or be resolved
by an interval, average, majority vote, or LLM. They follow Q10 unresolved and
adjudication closure. Agreement metrics are diagnostic evidence for annotation
QA, reviewer training, ontology or rubric improvement, and calibration. They
are not candidate metrics.

### 2.114 Provider drift and incomplete collections

When a provider revision is not observable, the record states `unavailable`
and never invents a revision. A schema-valid, authority-closed single output
retains its absolute-quality evidence. Revision unavailability instead limits
whether runs may be pooled as one known execution distribution, whether a
baseline/candidate difference may be attributed fully to the candidate, and
whether repeated-run stability may be compared formally.

A future restricted compatibility contract must preregister the observable
provider/model identity envelope, bounded capture block or window, symmetric
or randomized schedule, drift observations, and allowed incompatibility
policy. Until that contract and its evidence exist, only a capture-scoped
diagnostic comparison is permitted. Timestamp or capture window is receipt
evidence, not model-revision identity. Hardware, latency, and resource facts
remain receipt data unless the execution contract proves they affect scoring
output and therefore makes them compatibility dependencies.

When a formal required slot is missing or does not close, repeated-run
collection completeness fails. The publication cannot claim complete-set
stability or a complete repeated-run conclusion. Completed runs retain their
own absolute-quality, blocker, authority, and failure facts; collection failure
does not rewrite them as `not_evaluated`. An explicitly incomplete partial
audit view may be published but cannot masquerade as a complete collection
summary.

A missing run is not quality zero, N/A, an approved exclusion, or
`no_formal_evaluation_basis`. Crash, timeout, missing artifact, schema-invalid
output, digest mismatch, authority failure, valid zero, approved exclusion,
N/A, and valid blocked run remain distinct upstream conditions. Collection
completeness is a Q15 membership and completeness semantic, not a new Q10
authority or Q12 quality enum.

### 2.115 Adoption authority and prohibited inference

Q15 statistical diagnostics do not decide adoption. Formal required collection
completeness is a publication and adoption-support closure prerequisite, not a
statistical score. Every formal run's Q10-Q13 outcomes operate under their
existing owners. A hard blocker in any formal required run cannot be
compensated across runs, so that collection cannot support unconditional
adoption. Q15 does not output `adopt` or `reject`.

Any future independent statistical gate requires a new Q11 revision,
preregistration, non-compensating semantics, and independent evidence. It
cannot lower an absolute floor, remove a Q12 blocker, or fill a missing pair or
authority failure. Such a gate is a future benchmark revision, not current
`pending_calibration`.

### 2.116 Q15 artifact and ownership topology

Q15 freezes the following non-schema ownership topology:

| Artifact or record | Owns | Must not own |
| --- | --- | --- |
| Preregistered run-plan manifest | Pre-capture logical run slots; Q15 run-membership roles; order or block; fixture, lane, candidate, and execution-contract references; planned matched-block or pairing references | Captured output references; post-capture membership changes; metric, authority, quality, comparison, statistics, or adoption |
| Per-attempt receipt or execution record | Attempt identity; timeout, retry, provider observations, timestamps, resource, and other operational facts | Score, Q10 authority, Q11 gate, Q12 quality, Q13 comparison, or statistics |
| Per-run output artifact | Immutable output bytes and scoring-relevant dependency references | Metric calculation, statistical summary, gate, quality, comparison, or adoption |
| Per-run Q14 metric result and applicable Q10-Q13 records | Their existing frozen calculation, authority, gate, quality, and comparison scopes | Q15 collection membership or statistical authority |
| Repeated-run collection manifest | Immutable plan-wide binding from the original run plan to every slot's complete success, failure, invalid, missing, or still-unclosed history and its output, receipts, metrics, authority, blocker, gate, and comparison records when present | Run-plan mutation, statistical calculation, missing-slot imputation, slot replacement, or reownership of collection completeness or referenced decisions |
| Statistical diagnostic artifact | Versioned finite-suite estimand, analysis frame, method contract, exact referenced inputs, and derived diagnostic output | Q10 authority, Q11 gate, Q12 quality, Q13 formal comparison, formal improvement, or adoption |
| Binding/publication manifest | Immutable references to the Q15 run plan, repeated-run collection, statistical diagnostics, and existing Q10-Q14 records | Recalculation, mutation, or reownership of referenced content |

The run-plan manifest exists before capture and is bound by version and digest.
Capture never adds output references to it in place. Planned pairing references
do not themselves grant Q13 or run-level pairing authority. The repeated-run
collection is a distinct immutable history-binding artifact that references the
original plan without modifying it, calculates no statistics, and imputes no
missing slot. A partial revision remains an audit view; only Q15 closure over
every formal-required slot establishes collection completeness.

Within-candidate statistical diagnostics reference Q14 per-run metric results.
Comparative diagnostics may reference Q13 eligibility and compatibility,
compatible baseline and candidate Q14 per-run metric results, and existing Q13
comparator results. The statistical artifact does not establish a formal pair
or formal comparative conclusion.

Every artifact is immutable, versioned, and content-addressed. Its canonical
payload does not contain its own digest. An external index, manifest, or binding
records the artifact digest under Q3's canonical serialization boundary.

### 2.117 Q15 immutable revision matrix

Old artifacts remain immutable and may only be superseded. Required work follows
the changed dependency:

| Change | Required work |
| --- | --- |
| Run-plan change after capture begins | Create a new run-plan revision and new formal collection; never modify the old plan. |
| Statistical method change | Reanalyze compatible referenced inputs. |
| Pairing or estimand change | Create a new analysis-contract revision; reanalyze only compatible inputs. |
| Q14 metric change | Rescore, then reanalyze dependent diagnostics. |
| Q13 comparison change | Recompare; then reanalyze diagnostics dependent on that comparison. |
| Output or execution dependency change | Re-execute affected formal slots, then rebuild dependent artifacts. |
| Receipt-only addition | Do not recalculate unless eligibility or collection-closure input changes. |
| Gate-only change | Reevaluate the gate; do not recompute statistics. |
| Governance revision | Create successor records and new bindings; never overwrite predecessors. |

### 2.118 Q15 policy, calibration, and future-revision boundary

Q15 retains evidence-dependent policy or calibration slots only for:

- formal repeat count;
- preregistered scheduling or block design;
- seed policy where supported;
- execution-compatibility requirements;
- run-level pairing rules;
- end-to-end dependency mode;
- metric-specific finite-suite functional form;
- parameters of a separately approved diagnostic method;
- schema and manifest realization.

Population confidence level, alpha, p-value or significance thresholds,
variance or failure-frequency adoption thresholds, a statistical-gate
threshold, and an adoption constant are prohibited in v1 and are not
`pending_calibration`. They require a future benchmark and Q11 gate revision if
ever proposed. Bootstrap iteration count belongs only to realization of a
future approved diagnostic method. Minimum sample size is method-applicability
evidence rather than a number selected now. Timeout and cost ceilings remain
with later runner/resource and Q11 policy. Existing deterministic gate constants
remain owned by Q11.

**Example and boundary.** Changing a diagnostic method reanalyzes compatible
inputs without rerunning a model. Changing an output or execution dependency
re-executes only affected formal slots. The non-numeric Q15 topology is frozen;
method activation and applicable numbers remain evidence-dependent.

### 2.119 Q16 smoke profile and fixture-reference semantics

Q16 freezes the logical smoke set as `P01`, `W01`, `Y01`, `C01`, and `S01`.
Each smoke case resolves through the full-profile manifest to the same
canonical fixture revision, exact source bytes, source-snapshot digest, and
compatible gold, reference, schema, scorer, and other dependent artifacts used
by `full`. Smoke must not create reduced inputs, shortened documents, alternate
gold, or any smoke-only fixture revision.

The frozen selection establishes logical IDs and reference semantics only. It
does not assert that source bytes, fixture revisions, artifact digests, rights
reviews, or gold that have not yet been created already exist. Smoke exercises
all lane and runner wiring applicable to those five cases. Its result remains
`diagnostic_only`, does not establish subtype coverage, and cannot support a
formal baseline, comparison, quality gate, or adoption decision.

**Trade-off.** Reusing full-fixture bytes makes smoke slower than reduced test
material, but prevents a smoke-only representation from concealing fixture or
runner incompatibility.

### 2.120 Q17 versioned runner, terminal package, and resume topology

Q17 freezes one versioned benchmark runner CLI. Every runner-controlled
terminal outcome emits a machine-readable terminal JSON status and references
its canonical, immutable, content-addressed terminal package and applicable
authoritative records. Exact command spelling, schema fields, and enum names
remain realization work.

Host loss, `SIGKILL`, container destruction, or another externally forced
termination may prevent the runner from emitting a terminal JSON status,
terminal package, or process exit code. All already durable attempt records and
partial history remain immutable. A later reconciliation or authorized resume
records the interruption and binds the surviving history under the unchanged
run-plan and execution-contract digests. It must not invent a terminal package
or exit code that the terminated process never emitted.

Process exit codes are coarse runner and transport summaries only:

- `0`: the requested operation completed and emitted a schema-valid terminal
  package; its independent quality records may pass, fail, or hard-block;
- `1`: an operational failure occurred or a required execution or collection
  is incomplete;
- `2`: the input or execution contract was rejected or invalid, including an
  applicable manifest, schema, digest, version, offline-enforcement, or
  deterministic-replay failure.

An exit code does not own, rename, derive, or replace Q10 authority or its
distinct `invalid`, `provisional`, and legacy `inconclusive` meanings; Q11 gate
outcomes; Q12 quality; Q13 `result_role` or comparison; or Q15 collection
status. The terminal JSON preserves those orthogonal states through stable
references to their authoritative records and retains detailed reasons rather
than compressing them into the process code.

Resume may operate only on plan-authorized unattempted or still-open slots
under the identical run-plan and execution-contract digests. It appends
immutable attempts and uses only the preregistered transient-retry policy. It
must not rerun or replace a completed valid-zero, hard-blocked, invalid, or
retry-exhausted slot; mutate membership; add a slot; or hide any prior attempt,
failure, or partial history. Retry details not already governed by Q15 remain a
versioned policy slot.

### 2.121 Q18 offline enforcement and provider-backed capture boundary

Q18 freezes two explicit execution boundaries.

1. Canonical validation, scoring, comparison, aggregation, and deterministic
   replay execute inside an externally enforced no-egress OS or container
   sandbox. Application mocks, adapter conventions, and unset credentials are
   not sufficient enforcement.
2. Candidate output capture may use a preregistered external provider only
   when its Q15 execution contract requires that provider. Capture is separate
   from offline scoring and replay, receives only approved frozen input bytes,
   and must not dynamically acquire canonical source content.

The offline process rejects live flags and credential-bearing inputs, consumes
only an allowlisted and redacted environment projection, and emits an immutable
network-denial conformance record. The record binds the enforcement mechanism
and version, policy digest, execution identity, and denied DNS, socket, and HTTP
probe results where applicable. Probe denial supports the conformance claim but
is not the sole proof that the outer boundary blocks all egress.

Provider-backed Generation or End-to-end capture is not described as offline.
Its immutable output and receipts cross into the separately enforced offline
validation and scoring boundary only through approved artifact references and
digests. The exact sandbox mechanism, conformance schema, and platform-specific
probe realization remain policy and schema work.

### 2.122 Q19 replay-provenance capture topology

Q19 freezes the provenance categories and reference topology needed for replay,
without freezing exact schema names or execution compatibility and equivalence
rules. Applicable execution and artifact records capture references or digests
for:

- executable code or build identity plus dirty-state or source-bundle evidence;
- dependency lock and runtime identity;
- the scoring-relevant allowlisted configuration projection;
- benchmark, fixture, input, output, gold, reference, prompt, schema, metric,
  scorer, comparison, gate, and run-plan contracts;
- OS, architecture, runtime, locale, and other applicable execution facts;
- provider and model revision, or explicit `unavailable` when not observable;
- seed capability and value when supported, otherwise explicit unavailability;
- hardware and resource facts in receipts;
- approved numeric-context and measurement or gate-contract references.

No unrestricted configuration is hashed or persisted. Secret values, tokens,
credential-bearing URLs, raw private source content, and raw private candidate
content outside their approved immutable artifact boundary are prohibited.
Allowlisted configuration evidence must be redacted before persistence and
must prove exactly which scoring-relevant projection was bound.

Receipt-only hardware and resource facts remain outside candidate-output,
metric-result, comparator-result, and other scoring-relevant digests unless a
versioned execution contract proves that a fact affects output or scoring and
therefore makes it an execution-compatibility dependency. Every provenance
artifact follows the existing external self-digest rule: its canonical payload
does not contain its own digest.

### 2.123 Q20 raw resource observations and non-authority topology

Q20 freezes complete raw per-attempt and per-run observation vectors containing,
as applicable:

- monotonic wall duration;
- input and output byte counts or contract-defined unit counts;
- attempt, retry, and terminal operational facts;
- provider usage and token facts;
- known cost, otherwise explicit `unknown` or `unavailable` according to the
  observation contract;
- CPU time and peak memory when the platform supports an approved measurement,
  otherwise explicit unavailability.

Publication retains the complete raw vectors. V1 does not require formal p50,
p95, or another percentile summary. Any future percentile or quantile output
belongs to an independently approved Q15 diagnostic-method contract and cannot
acquire gate or adoption authority by presentation alone.

Cold-versus-warm applicability and repetition design remain versioned policy
slots. Numeric time, resource, and cost ceilings remain Q11
`pending_calibration`; Q20 introduces no ceiling or threshold. Resource
observations and derived diagnostics own neither Q10 authority, Q11 gate
decisions, Q12 quality, Q13 comparison, Q14 metric scoring, nor adoption.

### 2.124 Q21 logical-run and collection materialization topology

Q21 freezes how the runner materializes the existing Q15 topology:

- the preregistered run plan enumerates every `formal_required` and diagnostic
  logical slot before capture;
- every planned stochastic repeat already has a distinct slot and logical-run
  identity;
- retry attempts append beneath the same slot and do not increase run count;
- scoring replay consumes byte-identical trusted output and creates no new run;
- resume cannot add, replace, remove, promote, demote, or otherwise reclassify
  a slot;
- an immutable collection-manifest revision binds every planned slot to its
  complete successful, failed, invalid, missing, or still-unclosed history and
  all required referenced artifacts;
- Parser-reuse and full-pipeline End-to-end modes are selected by the
  preregistered execution contract and cannot be mixed within one collection.

A partial collection-manifest revision is an explicit audit view and cannot
claim collection completeness. Final completeness still follows Q15 and
requires every formal-required slot to reach the closure required by its plan.
Selecting Parser reuse or full-pipeline execution remains the existing Q15
end-to-end dependency-mode policy slot. Exact schema and enum field names
remain realization work for the broader Q21 collection manifest; the
per-work-unit owner receipt fields and enums are frozen in section 2.138.

### 2.125 Q16-Q21 frozen and pending boundary

Frozen are Q16 smoke IDs and full-fixture reference semantics; Q17 runner,
terminal-package, process-exit, and bounded-resume topology; Q18 externally
enforced offline scoring/replay and separated provider-capture topology; Q19
provenance-capture and receipt/scoring-digest topology; Q20 raw observation and
non-authority topology; and Q21 logical-run, attempt, replay, resume, execution-
mode, and collection materialization topology.

These questions are not fully frozen. Except for the per-work-unit owner
receipt/history contract in section 2.138, exact schema and enum realization,
execution compatibility and equivalence, cold/warm applicability, diagnostic
resource methods, retry details not already governed by Q15, sandbox and probe
realization, and applicable numeric time, resource, and cost ceilings remain
pending under Q11, Q14, Q15, or the applicable existing contract owner. No
Q16-Q21 decision creates a new authority, quality, comparison, metric,
statistical, or adoption owner.

### 2.126 Q22 project-owned fixture-source candidate slate

Q22 remains `evidence_required`. The recommended source slate consists of the
following nine project-owned creation plans. Every entry is an unapproved
candidate. Working titles used during authoring are illustrative only and are
not frozen source identities, fixture identities, or manifest values.

| ID | Project-owned creation plan |
| --- | --- |
| `P01` | Author a native English technical PDF of at least eight pages with headings, lists, and project-authored code examples. |
| `P02` | Author a bilingual Traditional Chinese and English report with at least two project-authored tables and figures. |
| `P03` | Author a Traditional Chinese document of at least five pages, then create a reproducible raster-only PDF with documented skew or noise. |
| `P04` | Author a Chinese and English mixed PDF containing both native and reproducibly scanned pages, project-authored formulas, and a table. |
| `W01` | Author a self-contained static technical HTML article with headings, a list, code, and no remote assets. |
| `W02` | Author a self-contained static article with fictional navigation, advertisements, related links, and comments; no real person, brand, account, or tracking identifier is used. |
| `W03` | Author a self-contained HTML, JavaScript, and data bundle in which JavaScript materializes the main article, and retain a deterministic offline rendered snapshot separately from the origin bundle. |
| `Y01` | Author a synthetic YouTube-caption-shaped offline fixture with manual English captions and chapter metadata derived only from project-owned text or recording content. |
| `Y02` | Author a synthetic YouTube-caption-shaped offline fixture with an automatically generated, uncorrected Traditional Chinese or mixed-language caption track derived only from project-owned text or recording content. |

No Q22 candidate is canonical or formally eligible until its exact source
bytes, fixture revision, digests, reproducible acquisition or creation
provenance, rights and privacy evidence, and independent approval exist and are
bound by the formal manifest. A general repository, website, platform, or tool
license is not item-level proof of authorship or redistribution rights.

Synthetic caption fixtures must not fabricate a YouTube video ID, caption-track
ID, provider revision, or other platform identity. When such an identity does
not exist, the applicable typed provenance value is `unavailable`. The caption
fixtures exercise caption parsing and downstream note completeness only. Audio
quality, speech recognition quality, and ASR model quality are outside the
benchmark and receive no score.

### 2.127 Q23 synthetic-only Chat and Screenshot v1 policy

Q23 freezes `C01`, `C02`, `S01`, and `S02` as project-owned synthetic-only v1
fixtures. Chat and Screenshot remain separate source families with their own
fixture identities, source contracts, metric applicability, and formal vectors;
they are not one combined cohort. V1 adds no real-world, openly seeded, or
otherwise derived second cohort. A future second cohort requires a versioned
benchmark revision and independently sufficient rights, privacy, provenance,
gold, and membership evidence.

### 2.128 Q24 canonical and local storage topology

Q24 freezes `tests/evals/parser_note_completeness/v1/` as the canonical tracked
root with this directory topology:

- `fixtures/<fixture_id>/<fixture_revision>/`;
- `governance/<fixture_id>/<record_revision>/`;
- `reference_documents/`;
- `gold/`;
- `manifests/`.

Acquisition receipts belong inside the applicable fixture governance revision.
There is no generic tracked `receipts/` directory. Run receipts and results are
separate run artifacts rather than fixture-tree records. The exact diagnostic
End-to-end result/attempt package, storage path, and durability contract are
frozen in section 2.140; broader formal collection/store publication remains
under its existing owner boundaries.

Local diagnostic fixtures and local run artifacts use
`local_storage/benchmarks/parser_note_completeness/v1/`. Formal manifests must
never reference a local diagnostic fixture or artifact. Sensitive original
consent, license, or ownership evidence remains in an access-controlled
location. Git stores only the lawful redacted reference, its approved metadata,
and an allowed digest that does not reveal the sensitive content.

### 2.129 Q25 artifact-and-scope separation of duties

Q25 freezes independence by artifact and governed scope, not by requiring every
benchmark role to be filled by a globally different person. A person may
perform compatible roles over unrelated artifacts or scopes, but cannot serve
as the independent approver of their own fixture rights/privacy work, gold
annotation, scorer change, gate or threshold proposal, governance change, or
other approval-scoped work.

The required effects are:

- missing independent rights or privacy approval leaves the fixture
  non-canonical and formally ineligible;
- missing independent gold review leaves the affected gold revision `draft`;
- missing required scorer, gate, or governance approval fails the applicable
  formal closure;
- an independence failure does not by itself blanket-label every dependent
  artifact or result `provisional` or `invalid`; Q10-Q15 determine the exact
  scoped authority, validity, quality, comparison, gate, and collection effects.

### 2.130 Q26 renderer-neutral note artifact and rendered projection

Q26 freezes a benchmark-only renderer-neutral note-artifact topology.
`BenchmarkNoteDocument` and its rendered projection now have the exact Q26-
owned schema contract recorded in section 2.135. They remain distinct from
`NormalizedDocument`, gold and expected claims, the production
`SupplementProposalSchema`, and Notion API block or request schemas.

Two comparable artifact roles are frozen:

1. a pre-render generated-note artifact;
2. a final rendered-note projection captured from the renderer's authoritative
   output or verified readback, never merely assumed from an outgoing request.

Their comparable node model preserves, where applicable, stable order and
hierarchy; headings and paragraphs; lists and nesting; code and language
metadata; tables, rows, and cells; citations and typed source-locator
references; and transformation lineage from pre-render nodes to rendered
blocks or projection nodes. It contains no gold, evidence importance, expected
claims, acceptance hints, or Notion-specific authorization.

Renderer-origin evidence includes dropped, duplicated, reordered,
structurally degraded, or text-mutated content; corrupted code or tables; and
lost or fabricated citation or locator content. Exact projection, alignment,
and measurement formulas remain Q14 metric-contract work. Q12 retains hard-
blocker and quality ownership.

Renderer loss remains within the End-to-end lane and may have reviewed causal
diagnostics. It creates neither a fourth renderer lane nor a subjective-
readability metric.

### 2.131 Q27 non-compensating End-to-end adoption topology

Q27 freezes a non-compensating three-lane adoption topology. Parser,
Generation, and End-to-end must each independently complete their applicable
authority, blocker, and gate requirements.

The End-to-end gate vector contains two distinct non-compensating views:

1. **Final rendered-note quality** scores the final rendered-note projection
   against approved gold or reference evidence for coverage, support,
   structure, locators, and other applicable Q14 metrics.
2. **Renderer preservation** compares the pre-render generated-note artifact
   with the final rendered-note projection for renderer-origin loss or
   fabrication.

Perfect preservation of an incomplete or unsupported pre-render note cannot
make final rendered-note quality pass. Strong Parser or Generation results
cannot compensate for final rendering loss.

The End-to-end vector consumes Q10 authority closure, Q12 hard blockers and
quality decisions, Q14 metric artifacts, and Q11 absolute-floor and non-
regression gates. A preregistered improvement gate applies only when an End-to-
end benefit is claimed. Q13 retains comparison ownership. Q27 adds no scalar,
cross-lane compensation, metric formula, or numeric constant.

### 2.132 Q28 exhaustive long-source coverage topology

Q28 freezes three separate immutable artifact responsibilities.

**Pre-capture coverage plan.** Before generation, a versioned coverage plan is
bound to the exact Q5 reference-document digest, routing-policy revision, and
execution contract. It enumerates every applicable section and ordered element
range. Every applicable source unit has exactly one primary work-unit
assignment. Declared context-only overlap creates neither another primary
assignment nor scoring credit. The plan contains scheduling, hierarchy, order,
declared context overlap, and merge dependencies only. It contains no generated
output, post-result mapping, gold, importance, expected claim, or answer hint.

**Work-unit execution artifacts.** Every planned unit produces separate
immutable output and receipt artifacts. Missing, failed, truncated, or invalid
units remain explicit and cannot be silently skipped or replaced.

**Merge and coverage-closure artifact.** A separate immutable closure artifact
binds the original coverage plan, every planned unit outcome, merge order and
hierarchy, the final renderer-neutral note artifact, evidence mappings,
declared-overlap handling, and detected omission, duplication, truncation,
ordering loss, or internal contradiction. Internal contradictions retain their
existing Q12 treatment. Missing or invalid units use existing Q10 and Q15 scope
and collection rules rather than a new status.

Work-unit sizing, overlap amount, merge algorithm, contradiction-detection
realization, measurements, and applicable
numeric boundaries remain policy, evidence, or realization slots. No retrieval,
embedding, relevance
ranking, `top_k`, section selection, or Step 100 behavior is introduced. Every
applicable section remains planned regardless of predicted relevance.

### 2.133 Q29 deterministic pre-generation routing topology

Q29 freezes one versioned routing policy. Before the first generation or model
call, it selects one of the closed modes `single-pass`, `section-aware`, or
`hierarchical`.

The route is deterministic for the same reference artifact and digest; source
size and typed structural facts; section, element, and modality facts;
provider/model execution identity; approved context-capacity facts; and routing-
policy version and configuration digest. Candidate output, quality, gold,
expected claims, evidence importance, and post-generation cost are prohibited
routing inputs. An immutable pre-generation route-decision artifact records the
decision and its input facts.

Formal runs must execute the selected route. A mismatch between the policy
result and executed route is an execution-contract or conformance failure under
existing Q10 and Q15 ownership, not a low quality score.

Forced-mode experiments are preregistered diagnostic slots with separate
execution contracts. They never enter or replace formal results, cannot be
promoted after outputs are observed, cannot select the best mode for the
current formal candidate, and may support a future policy revision only as
separately reviewed pre-formal evidence.

Numeric source-size, element-count, section-count, token, and context-capacity
boundaries remain `evidence_required` routing-policy inputs. They are
operational routing boundaries, not Q11 quality-gate constants. Provider-
capacity changes follow existing execution-compatibility and revision rules;
capacity is explicit `unavailable` rather than invented when it cannot be
established.

### 2.134 Q26-Q29 frozen and pending boundary

Frozen are Q26's renderer-neutral pre-render and authoritative rendered-
projection roles, comparable content topology, and End-to-end lane placement;
Q27's non-compensating three-lane and two-view End-to-end adoption topology;
Q28's immutable pre-capture plan, exhaustive assignment, per-unit execution,
source-reference boundary, observation ownership, and merge/coverage-closure
responsibilities; and Q29's deterministic pre-generation routing, route
conformance, and forced-diagnostic separation topology.

Pending are Q14-owned projection/comparison rules, alignment, measurement,
metric/scorer/result, and scoring policy; Q26 schema realization is completed
in section 2.135. Q28's work-unit sizing, overlap amount, merge algorithm,
contradiction detection, measurement, and applicable boundary evidence; and
Q29 approved boundary evidence/configuration bindings, Q15 repeat and
scheduling policy, statistical methods, and remaining provider-capacity
compatibility policy. Section 2.136 records the frozen Q29 schema, and
section 2.137 records the frozen Q28 contract plus its remaining numeric,
measurement, algorithm, and evidence frontier. Q11 retains
quality-gate constants, Q13 comparison, and Q15 run membership and collection
ownership. The Q1-Q29 foundation interview is complete only at these stated
contract and topology boundaries; it does not claim complete evidence,
fixtures, schemas, metrics, constants, or implementation.

Every Q26-Q29 artifact follows the existing external self-digest rule: its
canonical payload does not contain its own digest.

### 2.135 Q26 BenchmarkNoteDocument schema contract completion

Q26 owns the exact schema, version, fields, enums, identity, ordering,
citation/reference, lineage, and canonical serialization semantics for the two
benchmark-only note artifacts. Q14 owns only the later alignment algorithm,
projection/comparison rules, measurement formulas, metric/scorer/result
schemas, aggregation, and scoring policy. Q11 retains numeric thresholds and
calibration. Nothing in this section creates a quality, authority, comparison,
gate, baseline, adoption, or production-proposal record.

#### Artifact identifiers and roles

The pre-render generated-note artifact uses the schema identifier
`benchmark-note-document/1.0.0` and the closed `artifact_role` value
`pre_render_note`. The final rendered-note artifact uses
`benchmark-rendered-note-projection/1.0.0` and the closed `artifact_role` value
`rendered_note_projection`. These are separate schema identifiers with the
same comparable node model; a reader must reject an unknown identifier or
role, and must not coerce one role into the other.

The required top-level fields of both artifacts are exactly:

| Field | Contract |
| --- | --- |
| `schema_version` | One of the two exact schema identifiers above, matching the artifact role. |
| `artifact_role` | `pre_render_note` or `rendered_note_projection`, as required by `schema_version`. |
| `document_id` | The benchmark-manifest-assigned logical fixture identity; it must equal the frozen reference document's `document_id`. It is not a run ID or provider ID. |
| `reference_document_sha256` | SHA-256 of the complete canonical frozen `NormalizedDocument` input. Generation must bind this digest directly; Parser candidates are not valid inputs. |
| `nodes` | A flat, ordered tuple of renderer-neutral `NoteNode` records. |
| `producer_provenance` | The benchmark output or renderer-capture provenance record defined below. |
| `lineage` | The parent-artifact and transformation-lineage record defined below. |

No other top-level fields are permitted. The schema is strict and
`extra=forbid`; the artifact does not contain its own digest, quality result,
gold, expected claim, evidence importance, metric, or authority record.

#### Closed node and metadata enums

`NoteNode.kind` is closed to:

- `heading`;
- `paragraph`;
- `list_item`;
- `quote`;
- `code_block`;
- `table`;
- `table_row`;
- `table_cell`;
- `figure`;
- `caption`;
- `formula`;
- `transcript_segment`;
- `message`.

The v1 note model deliberately excludes source- or renderer-only `page_break`
and `ui_text` nodes. It also excludes `unknown`: unsupported output must be
represented as a supported node kind or rejected by the artifact contract; it
must not acquire a new semantic kind through an escape hatch.

The other closed enums are:

| Enum | Values |
| --- | --- |
| `list_kind` | `ordered`, `unordered` |
| `code_language_status` | `available`, `unavailable` |
| `code_language_source` | `source_declared`, `producer_detected` |
| `citation_mode` | `whole_element`, `text_range` |
| `locator_type` | `pdf`, `web`, `youtube`, `chat`, `screenshots` |
| `lineage_parent_role` | `reference_document`, `pre_render_note` |
| `lineage_mapping_state` | `not_applicable`, `provided`, `unavailable` |
| `lineage_mapping_shape` | `one_to_one`, `one_to_many`, `many_to_one`, `many_to_many`, `unmatched_source`, `unmatched_target` |
| `producer_role` | `generator`, `renderer` |
| `capture_method` | `authoritative_output`, `verified_readback` |

`NoteNode` contains exactly `node_id`, `kind`, `order`,
`parent_node_id`, `content`, `languages`, `list_metadata`,
`table_cell_metadata`, `code_metadata`, and `citations`. The metadata records
reuse the frozen v1 semantics from `NormalizedDocument`: list items require
`list_kind`, zero-based `nesting_level`, and optional `ordinal`; table cells
require zero-based row and column indexes with optional positive spans and
header role; code blocks require `code_metadata` containing exactly
`code_language_status`, `language_hint`, `language_source`, and `reason`.
`code_language_status=available` requires a nonblank `language_hint` and one
of `source_declared` or `producer_detected` in `language_source`, with
`reason=null`; `unavailable` requires `language_hint=null`,
`language_source=null`, and a machine-readable `reason`. A code language that
is not available is never replaced by an invented language value. The closed
table `header_role` values are `row`, `column`, and `both`.

Content and metadata rules are closed by kind: `table` and `table_row` have
null `content`; text-bearing kinds require nonblank source-faithful or
generated content; `list_item`, `table_cell`, and `code_block` require their
applicable metadata; unrelated metadata is forbidden. `languages` is a
nonempty, ordered, de-duplicated BCP 47 list using the existing `und` rule;
`mixed` is not a language tag. No field stores renderer-specific blocks,
Notion IDs, requests, or authorization.

#### Hierarchy, order, and artifact-local identity

The node array is the canonical flat reading order. `order` is zero-based,
unique, gap-free, and the array must already be in ascending order. A
non-null `parent_node_id` must identify an earlier node; parent links are
acyclic and express containment only. Nested lists use parent links and
`list_metadata.nesting_level`; tables use `table -> table_row -> table_cell`;
figure captions use `figure -> caption`. There is no second `children` array
that could disagree with canonical order.

`node_id` is artifact-local and deterministic. Its identity seed is the
canonical UTF-8 JSON of `document_id`, an anchor, `kind`, and a zero-based
occurrence. When a source citation locator exists, the anchor is the first
typed reference-document locator (`element_id`, `locator_type`, and
`locator_index`); otherwise it is the deterministic parent structural path
and sibling occurrence. The ID is `node-` followed by the lowercase SHA-256
hex digest of that seed. Content, extracted text, database IDs, provider IDs,
timestamps, and transient run IDs are never identity inputs. Pre-render and
rendered nodes do not claim cross-artifact identity; lineage mappings provide
the only comparison relationship.

`citation_id` and `mapping_id` use the same artifact-local rule: they are
lowercase SHA-256 IDs derived from their owning node or mapping identity and
zero-based occurrence, with no content or run facts. IDs are stable when the
anchor and segmentation remain stable, but they are not cross-parser or
cross-render alignment keys.

#### Citation and typed locator references

`citations` is an ordered tuple on each node and may be empty. A citation
contains exactly `citation_id`, `reference_document_id`, `element_id`,
`mode`, `text_span`, and `locator_refs`. `reference_document_id` must equal
the top-level `document_id`; `element_id` must resolve to the frozen reference
document. `whole_element` requires `text_span=null`; `text_range` requires a
non-empty Unicode-code-point half-open `[start, end)` span within that exact
reference element string. The note artifact stores no copied source excerpt.

Each citation has at least one `locator_ref`. A locator reference contains
exactly `locator_type`, `element_id`, and zero-based `locator_index`; it points
to the corresponding typed locator in the referenced `NormalizedDocument`
element, including an explicitly unavailable locator when that is the frozen
source fact. Validation against the reference document must reject a mismatched
locator type or index and must preserve the existing PDF, Web, YouTube, Chat,
and Screenshot identity rules. It must not invent a page, DOM path, timestamp,
cue, message, thread, image, or geometry. Locator comparison thresholds and
algorithms remain Q14-owned metric policy.

Citation order is authoring order within a node and is part of the canonical
payload. Locator references are ordered by the referenced locator index. A
citation does not itself assert support, coverage, correctness, or quality;
those meanings remain in gold and Q14/Q12-owned records.

#### Generation provenance and transformation lineage

`producer_provenance` contains exactly `producer_role`, `producer_name`,
`producer_version`, `configuration_sha256`, `processing_method`,
`processing_stage`, and optional `capture_method`. A pre-render artifact
requires `producer_role=generator`, omits `capture_method`, and uses
`processing_stage=pre_render_generation`. A rendered projection requires
`producer_role=renderer`, requires `capture_method` to be either
`authoritative_output` or `verified_readback`, and uses
`processing_stage=rendered_projection_capture`. `outgoing_request` is not a
valid capture method. These fields identify how the artifact was produced;
they do not authorize a provider, renderer, or Notion write.

`lineage` contains exactly `parent_artifact_role`, `parent_artifact_sha256`,
`mapping_state`, and `mappings`. A pre-render note binds its parent to the
reference document digest, uses `lineage_mapping_state=not_applicable`, and
has an empty mappings tuple; citations, not transformation mappings, express
source references. A rendered projection binds its parent to the external
digest of the pre-render note. It uses `provided` with one or more mappings
when lineage is captured, or `unavailable` with an empty tuple when the
authoritative output/readback cannot provide it. This explicit unavailable
state is not a quality decision.

Each mapping contains exactly `mapping_id`, `source_node_ids`,
`target_node_ids`, and `mapping_shape`. The two ID tuples are nonempty except
for the side named by `unmatched_source` or `unmatched_target`;
`mapping_shape` must agree
with their cardinalities. Mapping arrays are canonicalized by target reading
order, then source reading order, then mapping ID. A source or target node may
participate in more than one mapping so duplication, splitting, merging, and
reordering can be represented without pre-judging whether the transformation
is loss or fabrication. Q14 owns how mappings are computed, aligned,
compared, and measured.

#### Canonical serialization and digest boundary

Both Q26 schemas use the existing benchmark canonical JSON rules: UTF-8 with
no BOM, compact JSON, sorted object keys, deterministic escaping, no
insignificant whitespace, no trailing newline, no Unicode normalization,
duplicate keys, NaN, Infinity, or non-integer numeric values. Contract-defined
array order is preserved rather than sorted generically: node order, citation
authoring order, locator-index order, language declaration order, and lineage
mapping order above are authoritative. The serializer options and array rules
are part of each schema version.

The external digest is SHA-256 over the exact canonical bytes. The payload
does not contain its own digest; a separate digest record names the artifact
file using the existing ASCII checksum-record convention. Parent artifact
digests, the frozen reference digest, and output artifact digests remain
separate bindings. Run IDs, timestamps, hardware, latency, memory, cost,
quality decisions, and authority records belong in receipts or owned result
artifacts and never change the note or projection digest.

#### Renderer projection and alignment boundary

The pre-render note is the renderer-neutral Generation output boundary. The
rendered projection is accepted only from authoritative renderer output or
verified readback, never from an outgoing request assumed to have succeeded.
It uses the same node/citation model and the lineage parent digest to make
preservation inspectable without introducing renderer-specific structure.

Q26 owns the representation of lineage and the closed mapping shapes. Q14
owns the alignment algorithm, projection/comparison rules, measurement
formulas, metric/scorer/result schemas, aggregation, and scoring policy. Q11
owns numeric thresholds and calibration. Therefore this contract can validate
shape, identity, ordering, references, and lineage bindings without deciding
whether a rendered difference is loss, duplication, reordering, structural
degradation, text mutation, corruption, fabrication, quality failure, or gate
failure.

#### Q26 completion and remaining pending items

Q26 schema realization is complete at the artifact-contract boundary. The
following remain pending and are not silently decided here:

- Q14 alignment algorithms, projection/comparison rules, measurement formulas,
  metric/scorer/result schemas, aggregation, and scoring policy;
- Q11 numeric thresholds, calibration, and gate constants;
- Q28 work-unit sizing, overlap amount, merge and contradiction-detection
  realization, measurement, and applicable boundary evidence; the exact
  coverage-plan, work-unit, and closure schema realization is frozen in
  section 2.137;
- Q29 approved boundary evidence/configuration bindings, provider-capacity
  compatibility, and Q15-owned repeat/scheduling/statistical-method policy;
- Q22 fixture eligibility, provenance, rights/privacy evidence, and
  independent approval; and
- Q24 exact formal run-result and receipt-store realization.

### 2.136 Q29 deterministic pre-generation routing contract realization

Q29 owns the benchmark routing-policy, route-decision, forced-diagnostic, and
route-conformance artifact boundaries. It does not own Generation output, Q28
work-unit planning, Q14 measurement, Q11 quality thresholds, Q15 repeated-run
policy, or production routing. This section records the exact frozen schema
and the remaining evidence/compatibility boundaries without extending those
owners' semantics.

#### Frozen routing semantics

The route is decided before the first Generation/model call and before any
candidate output exists. The route decision is a pure function of the exact
canonical input-fact payload, the versioned policy, and its bound
configuration. The same reference digest, policy/configuration digests,
input facts, execution identity, and capacity facts must produce the same
policy-selected mode.

The closed routing-mode vocabulary is exactly:

| Mode | Frozen meaning | Explicit non-meaning |
| --- | --- | --- |
| `single-pass` | One generation execution envelope over the reference document under the selected execution contract. | It does not define Q28 coverage, work-unit, merge, or quality behavior. |
| `section-aware` | A generation execution envelope that preserves section-bounded planning as a route property. | It does not choose section units, overlap, merge order, or coverage measurements. |
| `hierarchical` | A generation execution envelope that preserves source hierarchy as a route property. | It does not define Q28 hierarchy planning, work-unit assignment, merge, or scoring. |

These values are routing modes, not quality labels, provider names, model
names, metrics, thresholds, or authority states. A route policy may select a
mode only from the closed set; an unknown mode is invalid input.

The required logical input-fact categories are frozen even though their exact
serialized field names remain a decision item below:

- exact frozen `reference_document` identity and canonical digest;
- deterministic source-size facts, without copied source text;
- typed structure facts, including element, section, order, hierarchy, and
  applicable modality facts;
- provider and model execution identity facts, or explicit `unavailable`;
- approved context-capacity facts, or explicit `unavailable`;
- routing-policy identity/version and configuration digest;
- the execution-contract identity that will govern the selected route.

Candidate output, parser output, generated note content, gold, expected claims,
evidence importance, quality, alignment, metrics, gates, post-generation cost,
and any result observed after the first model call are prohibited input facts.
Tokens may be recorded only as a deterministic pre-generation fact under an
approved measurement contract; a post-generation usage count is never a
routing input.

#### Policy and decision artifact responsibilities

Q29 requires the following separate immutable logical artifacts. The artifact
names and exact serialized identifiers are not yet frozen; the responsibilities
and dependency directions are frozen:

1. **Routing policy artifact.** It identifies the policy schema/version,
   policy identity and revision, deterministic decision implementation, closed
   mode vocabulary, input-fact schema/version, configuration projection digest,
   and any evidence-bound boundary references. It contains no secret-bearing
   configuration and no candidate result.
2. **Route-decision artifact.** It binds the policy identity/revision and
   policy digest, configuration digest, reference `document_id` and
   `reference_document_sha256`, the canonical deterministic input facts, the
   policy-selected mode, the route-selection basis, and the execution-contract
   digest. It is created before Generation and has no quality or authority
   result.
3. **Route-conformance artifact.** It binds one immutable route decision to
   the exact execution contract and the observed executed mode. For a formal
   route, an executed-mode mismatch is an execution-contract/conformance
   failure under Q10/Q15 and not a quality failure. Conformance must never
   rewrite the preceding route decision.
4. **Forced-diagnostic execution record.** It binds a separately preregistered
   diagnostic slot and execution contract to a forced mode while retaining the
   policy-selected mode as a separate fact. It cannot enter a formal result,
   replace a formal route, be promoted after output observation, or select the
   mode of a current formal candidate.

The route decision and conformance records are references to the exact
artifact digests, not copies of mutable state. A terminal receipt may reference
these artifacts, but receipt status and process exit status remain separate
from route conformance, quality, and authority.

#### Deterministic fact and unavailable boundary

A fact that cannot be established before the first model call is represented by
an explicit unavailable record with a machine-readable reason and its fact
schema/version. It is never represented as zero, an empty string, a guessed
provider revision, infinite capacity, or an inferred token count. An
unavailable provider/model revision follows Q19's existing semantics; an
unavailable capacity measurement does not become a capacity ceiling or a Q11
constant.

Numeric source-size, element-count, section-count, token, and context-capacity
boundaries remain `evidence_required`. Q29 freezes neither a numeric value nor
an implied default. A policy revision cannot silently add a boundary after
route output is observed. Any boundary used by a formal policy must reference
its approved evidence and configuration revision before formal execution.

Until the unavailable-fact behavior and boundary evidence choices below are
resolved, a formal policy must not silently fall back to a mode that could
exceed an unestablished context capacity. A forced diagnostic may exercise a
preregistered mode under a separately labeled diagnostic contract, but that
exercise does not establish formal capacity compatibility.

#### Digest, canonicalization, and revision rules

The routing-policy, route-decision, and conformance payloads use the existing
benchmark canonical JSON boundary: UTF-8 without BOM, compact JSON, sorted
object keys, deterministic escaping, preserved contract-defined array order,
no Unicode normalization, no duplicate keys, no NaN or Infinity, and no
trailing newline. The payload does not contain its own digest. Every artifact
has an external SHA-256 record using the existing ASCII checksum convention.

The route decision must bind all of the following independently:

- the policy schema/version, policy identity/revision, and policy digest;
- the redacted scoring-relevant configuration projection digest;
- the exact reference document identity and canonical digest;
- the deterministic input-fact schema/version and fact payload or fact digest;
- the execution-contract identity/digest; and
- for conformance, the executed-mode observation and the route-decision
  digest.

A policy, configuration, input-fact schema, execution contract, reference
document, provider/model compatibility fact, or approved capacity fact change
creates a new immutable revision or route-decision binding according to the
affected dependency. Existing route decisions and conformance records are not
edited in place. Forced-diagnostic records are separate revisions and cannot
be relabeled as formal decisions.

#### Historical Q29-D1-D7 alternatives (superseded)

The alternatives below record the prior design review. The selected choices
and exact schemas are frozen in the following section; the historical
recommendations below must not be interpreted as pending or active contract.

**Q29-D1 — schema identifiers and version family**

1. Option A: `benchmark-generation-routing-policy/1.0.0`,
   `benchmark-generation-route-decision/1.0.0`, and
   `benchmark-generation-route-conformance/1.0.0`.
   - Trade-off: clearly benchmark- and Generation-scoped, with low collision
     risk; slightly longer identifiers.
2. Option B: `benchmark-routing-policy/1.0.0`,
   `benchmark-route-decision/1.0.0`, and
   `benchmark-route-conformance/1.0.0`.
   - Trade-off: concise and reusable across benchmark lanes; less explicit
     about the pre-generation Generation boundary.
3. Option C: `parser-note-completeness-routing-policy/1.0.0` and matching
   dataset-scoped identifiers.
   - Trade-off: strongest dataset isolation; couples a reusable routing
     contract to one benchmark and makes future reuse or migration harder.

Recommendation: Option A. It preserves the benchmark-only, pre-generation
boundary without binding the schema to production or to a future Q28 artifact.
The recommendation is not frozen until the identifier family is selected.

**Q29-D2 — route-decision selection basis and forced mode representation**

1. Option A: one route-decision schema with closed logical values
   `policy_selected` and `forced_diagnostic`, plus separate
   `policy_selected_mode` and `effective_mode` fields.
   - Trade-off: one reader and explicit visibility of the formal policy result
     versus a slightly wider artifact.
2. Option B: one `mode` field plus a `forced` boolean.
   - Trade-off: compact, but permits ambiguous combinations and makes it
     easier to confuse a forced mode with the formal route.
3. Option C: separate formal route-decision and forced-diagnostic schemas.
   - Trade-off: strongest type separation, but duplicates policy/reference
     binding and increases revision and reader complexity.

Recommendation: Option A. The policy-selected mode must remain observable in
a forced run, while `effective_mode` makes the diagnostic execution explicit.
The exact enum names and field names remain pending Q15 run-membership and
execution-contract schema realization.

**Q29-D3 — deterministic input-fact representation**

1. Option A: a closed, nested fact record with fixed sections for reference,
   source, structure, modality, provider/model, capacity, and execution
   identity.
   - Trade-off: strongest validation and audit readability; adding a new fact
     requires a versioned schema revision.
2. Option B: an ordered typed fact vector of `{fact_id, value_type, value,
   availability, reason}` records.
   - Trade-off: extensible and generic; weaker static validation and more
     opportunity for two policies to interpret the same fact differently.
3. Option C: a small route decision containing only a digest of a separately
   versioned fact artifact.
   - Trade-off: clean separation and privacy boundary; a reader needs another
     artifact to validate the decision and cannot inspect facts from the
     decision alone.

Recommendation: Option A for v1, with an explicit fact-schema version and
canonical ordering. Option C may be added later for sensitive operational
facts without changing route semantics. The exact field inventory is not
frozen because Q19 execution compatibility and Q20 observation realization
still own adjacent fact categories.

**Q29-D4 — provider/model/context-capacity availability shape**

1. Option A: one reusable typed availability wrapper with a closed
   `available`/`unavailable` state, typed identity or capacity value, and
   machine-readable reason when unavailable.
   - Trade-off: one consistent representation and explicit absence; requires
     careful value typing for identity versus numeric capacity.
2. Option B: reuse Q5/Q19 `TypedIdentity` for provider/model and a separate
   Q20 resource-observation record for capacity.
   - Trade-off: minimizes new vocabulary; provider compatibility and routing
     interpretation become distributed across owners.
3. Option C: three closed records (`provider_fact`, `model_fact`,
   `context_capacity_fact`) with separate availability enums.
   - Trade-off: clearest per-fact validation; more duplicated enum and reason
     semantics.

Recommendation: Option A, while referencing Q19 for provider/model revision
compatibility and Q20 for raw capacity observations. The exact wrapper fields,
reason-code enum, capacity unit, and whether a capacity value is a maximum
input-token count or another approved unit remain evidence and schema
decisions, not inferred here.

**Q29-D5 — unavailable required fact behavior**

1. Option A: fail closed with `route_unavailable` for formal execution until
   every policy-required fact is established.
   - Trade-off: safest and preserves formal capacity claims; can leave a
     formal slot incomplete.
2. Option B: deterministic fallback to `single-pass` while recording the
   missing fact.
   - Trade-off: keeps execution moving; may exceed unknown capacity and hides
     an execution-compatibility failure behind a route choice.
3. Option C: allow only a separately preregistered forced diagnostic when the
   fact is unavailable, with no formal route decision.
   - Trade-off: preserves investigation without granting formal meaning; does
     not provide a formal result until evidence is available.

Recommendation: Option A for formal execution plus Option C for diagnostics.
Option B is not recommended because Q29 explicitly forbids invented capacity
and Q17 treats execution-contract rejection as invalidity, not quality.

**Q29-D6 — numeric boundary and evidence binding**

1. Option A: store boundary IDs and evidence/configuration digests in the
   policy; publish numeric values only after evidence approval.
   - Trade-off: strongest provenance and later revision traceability; requires
     a boundary-evidence artifact.
2. Option B: store numeric values inline with an `evidence_required` status.
   - Trade-off: easy to read; risks treating an unapproved value as executable
     policy.
3. Option C: omit boundary fields until evidence closes and allow only
   non-numeric policies in the interim.
   - Trade-off: safest current implementation; limits useful routing coverage
     until evidence is complete.

Recommendation: Option C for the current foundation, followed by Option A
when evidence and the exact boundary contract close. No numeric boundary is
frozen in Q29 here.

**Q29-D7 — route-conformance artifact placement**

1. Option A: a separate immutable route-conformance artifact bound to the
   route-decision and execution-contract digests.
   - Trade-off: preserves the decision as immutable and supports replay; adds
     one artifact to the terminal package.
2. Option B: put conformance fields directly in the terminal receipt.
   - Trade-off: fewer files; couples route validation to receipt realization
     and makes pre-receipt replay/conformance harder.
3. Option C: derive conformance only in the collection artifact.
   - Trade-off: simplest execution path; too late for per-slot terminal
     diagnosis and weakens immutable route evidence.

Recommendation: Option A. The exact conformance enum and artifact identifier
remain pending Q17/Q15 schema realization.

#### Frozen Q29-D1-D7 schema contract

The following choices are frozen. These are benchmark execution artifacts,
not production routing, quality, metric, gate, gold, comparison, baseline, or
authority artifacts.

**D1 — exact schema identifiers and version family**

The exact identifiers are:

- `benchmark-generation-routing-policy/1.0.0`;
- `benchmark-generation-route-decision/1.0.0`;
- `benchmark-generation-forced-diagnostic/1.0.0`; and
- `benchmark-generation-route-conformance/1.0.0`.

Forced diagnostic has an independent schema and is never encoded as a route-
decision variant. The four schemas version independently under the existing
major/minor/patch rules: incompatible required fields, enums, identity,
locator, or canonicalization require a major version; compatible optional
fields require a minor version; documentation-only corrections use a patch
version.

**D2 — formal/forced artifact separation**

The formal route-decision schema records only the policy-selected mode. It has
no forced flag, effective-mode override, or post-decision mode. A forced run
uses the independent forced-diagnostic schema, references the route-decision
digest, copies its policy-selected mode as a separate fact, and records its
own `effective_mode`. The copied mode must equal the referenced decision's
selected mode when that decision is selected; it is null when the referenced
decision is rejected for an unavailable required fact.

**D3 — exact routing-policy and input-fact shapes**

`benchmark-generation-routing-policy/1.0.0` contains exactly:

| Field | Contract |
| --- | --- |
| `schema_version` | Literal `benchmark-generation-routing-policy/1.0.0`. |
| `policy_id` | Stable non-empty policy identity; no secrets or local paths. |
| `policy_revision` | Immutable non-empty revision token. |
| `implementation_id` | Stable deterministic decision-implementation identity. |
| `implementation_version` | Immutable implementation version. |
| `configuration_sha256` | Lowercase SHA-256 of the redacted allowlisted routing-configuration projection. |
| `input_facts_schema_version` | Literal `benchmark-generation-routing-input-facts/1.0.0`. |
| `mode_order` | Exactly `single-pass`, `section-aware`, `hierarchical`, in that order. |
| `boundary_references` | Ordered boundary-reference tuple; empty until approved evidence exists. |
| `execution_contract` | Exact `{contract_id, sha256}` reference for the formal route. |

Each `boundary_references` item contains exactly `boundary_id`,
`evidence_sha256`, and `configuration_sha256`, sorted by `boundary_id`. It
contains no numeric value. Until approved evidence exists,
`boundary_references=[]`; no unapproved numeric source-size, element-count,
section-count, token, or context-capacity boundary may appear in the policy.

The nested `benchmark-generation-routing-input-facts/1.0.0` object contains
exactly the following sections:

| Section | Required shape |
| --- | --- |
| `schema_version` | Literal `benchmark-generation-routing-input-facts/1.0.0`. |
| `reference` | `{document_id, schema_version, artifact_role, sha256}`; schema literal `normalized-document/1.0.0`, role literal `reference_document`. |
| `source` | `{source_type, source_snapshot_sha256, byte_count, token_count}`; existing five-value source enum, non-negative byte count, and availability-wrapped approved `input_tokens` measurement. |
| `structure` | `{sections, elements}`; sections preserve reference section order and use `{section_id, parent_section_id, heading_element_id, start_order, end_order}`; elements preserve reference order and use `{element_id, kind, order, section_id, parent_element_id}`. No source text, locators, or content is copied. |
| `modality` | `{values}`; a unique non-empty tuple from the closed enum `native_text`, `scanned_image`, `caption_text`, `chat_text`, `screenshot_image`, in enum order. Multiple values represent mixed modality; `mixed` is not an enum value. |
| `provider_model` | `{provider, model}`; each is an availability-wrapped strongly typed identity. |
| `capacity` | `{context_capacity}`; the value is an availability-wrapped strongly typed context capacity. |
| `execution` | `{contract_id, contract_sha256}` for the exact execution contract whose facts are evaluated. |

`source_type` remains `pdf`, `web`, `youtube`, `chat`, or `screenshots`.
`kind` uses the existing NormalizedDocument element-kind enum: `heading`,
`paragraph`, `list_item`, `quote`, `code_block`, `table`, `table_row`,
`table_cell`, `figure`, `caption`, `formula`, `transcript_segment`, `message`,
`ui_text`, `page_break`, or `unknown`. Structure facts do not define Q28
work units, overlap, merge, or coverage.

**D4 — availability and strong value types**

Every availability wrapper contains exactly `status`, `value`, and `reason`.
`status` is the closed enum `available | unavailable`.
`availability_reason` is the closed enum `not_observed | not_supplied |
not_supported | not_approved | redacted`.

- `available` requires a non-null typed value and `reason=null`.
- `unavailable` requires `value=null` and one non-null machine-readable reason.
- Zero, empty, guessed, infinite, or inferred values are never unavailable
  representations.

The strongly typed values are:

- `ProviderIdentity`: exactly `{provider_id, revision}`;
- `ModelIdentity`: exactly `{model_id, revision}`;
- `TokenMeasurement`: exactly `{unit, count, measurement_contract_id,
  measurement_contract_sha256}`, with literal `unit=input_tokens`, a
  non-negative integer count, and an approved measurement-contract binding;
- `ContextCapacity`: exactly `{unit, maximum}`, with literal
  `unit=input_tokens` and a positive integer maximum.

Provider/model revisions follow Q19 provenance semantics and raw resource
observations remain Q20-owned. Context capacity is an execution fact, never a
threshold, quality gate, or Q11 constant.

**D5 — route-decision, rejection, and forced-diagnostic records**

`benchmark-generation-route-decision/1.0.0` contains exactly:

| Field | Contract |
| --- | --- |
| `schema_version` | Literal `benchmark-generation-route-decision/1.0.0`. |
| `artifact_role` | Literal `route_decision`. |
| `run_membership` | Closed enum `formal_required | diagnostic`. |
| `policy` | `{schema_version, policy_id, policy_revision, sha256, configuration_sha256}` reference. |
| `reference_document` | `{document_id, schema_version, artifact_role, sha256}` reference to exact canonical reference bytes. |
| `input_facts` | Exact `benchmark-generation-routing-input-facts/1.0.0` object. |
| `input_facts_sha256` | SHA-256 of canonical `input_facts` bytes. |
| `execution_contract` | `{contract_id, sha256}` reference. |
| `decision_status` | Closed enum `selected | rejected`. |
| `selected_mode` | One of the three modes when selected; null when rejected. |
| `decision_reason` | Null when selected; literal `required_fact_unavailable` when rejected. |

The duplicated policy/reference fields must equal the bound artifacts and the
corresponding input-fact fields. A selected decision requires every
policy-required fact to be available. An unavailable required fact produces a
rejected route and execution-contract rejection; there is no silent fallback
to `single-pass`.

`benchmark-generation-forced-diagnostic/1.0.0` contains exactly:

| Field | Contract |
| --- | --- |
| `schema_version` | Literal `benchmark-generation-forced-diagnostic/1.0.0`. |
| `artifact_role` | Literal `forced_diagnostic`. |
| `run_membership` | Literal `diagnostic`. |
| `diagnostic_slot_id` | Stable preregistered diagnostic slot identity. |
| `route_decision_sha256` | Digest of the referenced route decision. |
| `reference_document` | Exact `{document_id, sha256}` reference copied from the route decision. |
| `policy_selected_mode` | Referenced `selected_mode`, or null if that decision was rejected. |
| `effective_mode` | The forced mode actually authorized by the diagnostic slot. |
| `execution_contract` | `{contract_id, sha256}` for the separately preregistered diagnostic contract. |

The forced artifact has no formal membership value, formal result field,
quality field, or authority field. It cannot replace, promote, or close a
formal-required slot.

**D6 — canonical ordering and digest/reference rules**

All four artifacts and the nested fact object use the existing canonical JSON
boundary: UTF-8 without BOM, compact encoding, sorted object keys,
deterministic escaping, no Unicode normalization, no duplicate keys, NaN,
Infinity, or trailing newline. Contract arrays preserve defined order:

- `mode_order` is the fixed three-mode order;
- `boundary_references` sort by `boundary_id`;
- `structure.sections` use reference section order;
- `structure.elements` use zero-based reference element order; and
- `modality.values` use the closed enum order.

No payload contains its own digest. External SHA-256 covers exact canonical
bytes using the existing ASCII checksum-record convention. The route-decision
digest covers its complete payload, including `input_facts` and
`input_facts_sha256`; forced and conformance digests cover their complete
payloads.

`reference_document.sha256` must equal the exact canonical
`NormalizedDocument` bytes with schema `normalized-document/1.0.0` and role
`reference_document`. `policy.sha256` must equal the canonical policy bytes,
and `policy.configuration_sha256` must equal its redacted allowlisted
configuration projection. `input_facts_sha256` must recompute from the nested
fact bytes. `route_decision_sha256` in forced and conformance records must
equal the external digest of the referenced decision. Every execution
contract is an exact `{contract_id, sha256}` pair.

No routing artifact copies source text, candidate output, gold, expected
claims, importance, quality, metric, threshold, gate, comparison, baseline, or
authority data.

**D7 — route-conformance status and reason**

`benchmark-generation-route-conformance/1.0.0` contains exactly:

| Field | Contract |
| --- | --- |
| `schema_version` | Literal `benchmark-generation-route-conformance/1.0.0`. |
| `artifact_role` | Literal `route_conformance`. |
| `run_membership` | Closed enum `formal_required | diagnostic`. |
| `route_decision_sha256` | Digest of the immutable route decision being checked. |
| `execution_contract` | `{contract_id, sha256}` actually used by the slot. |
| `policy_selected_mode` | Must equal the referenced decision's `selected_mode`, including null for rejection. |
| `executed_mode` | Observed mode, or null when no execution occurred. |
| `status` | Closed enum `conformant | mismatch | rejected | forced_diagnostic`. |
| `reason` | Null or `executed_mode_mismatch | execution_contract_mismatch | route_decision_rejected | forced_mode_execution`. |
| `forced_diagnostic_sha256` | Null for ordinary/formal execution; required when `status=forced_diagnostic`. |

Formal selected execution with matching mode and execution-contract digest is
`conformant` with `reason=null`. A formal mode or contract mismatch is
`mismatch` with the corresponding reason and is an execution-contract failure,
not a quality result. A rejected route with no execution is `rejected` with
`reason=route_decision_rejected`. A separately preregistered forced diagnostic
is `diagnostic`, references the forced artifact digest, records its effective
mode as `executed_mode`, and is `forced_diagnostic` with
`reason=forced_mode_execution`. Conformance never rewrites the route decision
or creates a comparison, gate, baseline, or authority outcome.

#### Revision and compatibility rules

The policy revision is immutable. A change to policy implementation identity or
version, configuration projection, input-fact schema, mode vocabulary, boundary
reference, execution-contract reference, reference-document digest, or any
provider/model/capacity fact creates a new applicable policy or route-decision
binding; existing artifacts are never edited in place or silently reused.

The route decision is valid only for the exact reference, policy, configuration,
input-fact, and execution-contract digests recorded in it. A formal slot cannot
reuse a decision after any of those bindings change. An execution-contract or
provider/model/capacity mismatch is rejected or recorded as conformance
`mismatch` according to the affected terminal boundary; it is never converted
into a quality result or repaired by rewriting the decision.

`run_membership` is immutable. A `formal_required` slot must execute the
selected route under the selected contract. A forced artifact is created only
for a separately preregistered `diagnostic` slot and cannot be promoted,
substituted for, or used to close a formal-required slot. Repeat count,
scheduling, statistical methods, retry details not already owned by Q15, and
broader compatibility policy remain pending Q15 decisions.

#### Cross-question compatibility

- **Q26:** no conflict. Q29 binds the frozen reference digest and execution
  contract before creating a `benchmark-note-document/1.0.0` candidate; it does
  not add routing fields to `BenchmarkNoteDocument`, change node identity, or
  alter citation/lineage semantics.
- **Q28:** no conflict. Q28's pre-capture coverage plan binds the routing
  policy revision and exact reference digest. Q29 selects the generation mode
  but does not own work-unit sizing, overlap, merge, contradiction detection,
  or coverage closure.
- **Q14:** no conflict. Route conformance is execution-contract evidence, not
  a metric, alignment, comparison, quality, or scorer result. Q14 may later
  consume outputs under the selected route but cannot retroactively become a
  routing input.
- **Q15:** no conflict. The minimum routing interface is now frozen: the exact
  run-membership enum is `formal_required | diagnostic`; a forced diagnostic
  binds only to a `diagnostic` slot; a `formal_required` slot must execute the
  policy-selected route; and a forced diagnostic cannot replace, promote, or
  close a formal-required slot. Repeat count, scheduling, statistical methods,
  and other compatibility policy remain Q15-owned pending work.

#### Q29 completion status

The following are now frozen: the three routing modes and their non-quality
meanings; pre-generation timing; prohibited input classes; the four artifact
identifiers; required fields and closed enums; nested deterministic fact
shapes; typed availability and explicit unavailable reasons;
reference/policy/configuration/input-fact/execution-contract digest binding;
boundary-reference-only policy representation; formal fail-closed rejection;
separate forced-diagnostic artifacts; the minimum Q15 run-membership
interface; route-conformance status/reason semantics; immutable revision
dependencies; and the canonical external-digest boundary.

Q29 is **sufficient to begin routing implementation at the schema and
deterministic decision boundary**. It is not sufficient to claim a formal
numeric routing policy until approved boundary evidence and configuration
digests populate `boundary_references`. Q15 repeat count, scheduling,
statistical methods, and other compatibility policy remain pending and must
not be inferred by the implementation.

### 2.137 Q28 exhaustive long-source coverage contract realization

This section realizes the Q28 contract boundary without authorizing runtime
implementation. It defines the records Q28 must bind and the invariants a
future implementation must validate. It does not define a retrieval unit,
embedding unit, relevance unit, answer hint, scoring unit, quality state, or
provider-capacity rule.

#### Ownership and non-redefinition boundary

Q28 owns:

- the immutable pre-capture coverage-plan boundary;
- the reference-document source-unit inventory and exactly-one primary
  assignment relation;
- the declaration that an additional source reference is `context_only` and
  cannot create a second primary assignment;
- work-unit identity inputs, hierarchy/dependency topology, and the
  representation of a deterministic planned order once the open choices below
  are selected;
- per-work-unit output-envelope bindings and references to the independent
  receipt history owned by the existing run/receipt owners;
- the merge-plan/merge-order binding;
- the structural coverage-closure record; and
- neutral observations of omission, duplication, truncation, ordering loss,
  and internal contradiction.

Q28 does not own:

| Boundary | Owner and compatibility rule |
| --- | --- |
| Routing mode, route decision, route conformance, and routing-policy revision | Q29. Q28 stores exact Q29 artifact references and never selects or rewrites the route. |
| Final `BenchmarkNoteDocument` / `pre_render_note` schema, node identity, citation, locator, and lineage semantics | Q26. Q28 stores a typed digest/reference and does not add Q28 fields to the note artifact. |
| Omission, duplication, truncation, ordering, contradiction measurement formulas; alignment; metric/scorer/result semantics | Q14. Q28 records neutral observations and their evidence/basis references only. |
| Contradiction support state, blocker, quality, authority, and gate effect | Q8/Q10/Q12. `internal_contradiction` is a Q28 observation kind, not a new support or quality enum. |
| Run membership, repeated-run design, retry, terminal-receipt semantics, collection, and scheduling/collection statistics | Q15 and the existing Q16–Q21 runner/receipt owners. Q28 binds their immutable records without redefining them. |
| Quality, metric, gate, baseline, comparison, adoption, and authority | Q10–Q14 and Q11/Q13. Q28 has no pass/fail or adoption field. |

#### Contract-wide invariants that are frozen now

The following invariants are exact Q28 requirements, independent of the
superseded representation alternatives recorded in the D1–D8 and D11 design
history.

1. **Pre-capture timing.** The coverage plan is complete, immutable, and
   content-addressed before the first Generation/model call. Candidate output,
   post-generation usage, gold, expected claims, evidence importance, quality,
   and observed result facts cannot enter the plan.
2. **Required bindings.** The plan binds these separate references:

   ```json
   {
     "reference_document": {
       "schema_version": "normalized-document/1.0.0",
       "artifact_role": "reference_document",
       "document_id": "<document_id>",
       "sha256": "<lowercase-sha256>"
     },
     "routing_policy": {
       "schema_version": "benchmark-generation-routing-policy/1.0.0",
       "policy_id": "<q29-policy-id>",
       "policy_revision": "<q29-policy-revision>",
       "sha256": "<lowercase-sha256>",
       "configuration_sha256": "<lowercase-sha256>"
     },
     "route_decision": {
       "schema_version": "benchmark-generation-route-decision/1.0.0",
       "sha256": "<lowercase-sha256>"
     },
     "execution_contract": {
       "contract_id": "<contract-id>",
       "sha256": "<lowercase-sha256>"
     }
   }
   ```

   The Q29 route-decision digest is its immutable revision reference. The
   policy reference and route decision must agree on policy identity/revision,
   reference-document identity/digest, and execution-contract identity. Q28
   does not duplicate Q29 input facts or mode-selection logic.
3. **Exhaustive source universe.** The plan includes every reference-document
   section in the source section order and preserves each section's exact
   `section_id`, parent relation, `start_order`, and `end_order`. It includes
   every reference-document element in zero-based `order` as an identity-only
   source unit. There is no relevance filter, `top_k`, section selection, or
   predicted-importance exclusion. A source section is not omitted because it
   is short, repetitive, low-confidence, or expected to be unhelpful.
4. **Atomic assignment identity.** For Q28 assignment purposes, a source unit
   is one reference-document element identity:

   ```json
   {
     "reference_document_id": "<document_id>",
     "section_id": "<section_id>",
     "element_id": "<element_id>",
     "order": 0
   }
   ```

   This is not a Q14 scoring unit and does not select a work-unit size. A
   future work unit may contain one or more such source units; the number,
   token budget, and element/character limits remain pending.
5. **Exactly-one primary partition.** Every applicable source-unit identity
   occurs in exactly one primary assignment. Every planned work unit has at
   least one primary source unit. The plan validator must reject a missing,
   duplicate, foreign, or out-of-range primary assignment. A primary
   assignment is source lineage, not expected-claim coverage or score credit.
6. **Context-only overlap.** A source unit may be referenced by additional
   work units only with the explicit role `context_only`. A context-only
   reference cannot be a primary assignment, cannot create a second work-unit
   ownership, and cannot increase a denominator or score. The plan carries no
   overlap token count, element count, percentage, or implied threshold.
7. **Graph safety.** Every work-unit hierarchy/dependency reference resolves
   to a work unit in the same plan. The declared dependency topology is
   acyclic. A source hierarchy relation, an execution dependency, and a merge
   dependency remain typed relations; a generated answer cannot create a new
   edge after capture.
8. **Independent history.** Each planned work unit has an independent
   immutable output envelope for each recorded attempt and an independent
   reference to the corresponding immutable receipt history. An output or
   receipt artifact cannot be shared as the primary history of two planned
   work units. Q15 decides whether attempts are retries, repeats, replays, or
   collection members.
9. **No silent substitution.** `missing`, `failed`, `truncated`, and `invalid`
   are retained as explicit per-work-unit conditions. A later successful
   attempt, another work unit, a context-only overlap, or the final merge may
   not erase or relabel the earlier history. A terminal selection, if allowed
   by Q15, points to the original immutable attempt and does not delete other
   attempts.
10. **Closure is identity-complete.** A closure record must identify the
    original plan digest, one outcome binding for every planned work-unit ID,
    the selected/observed merge order, the final Q26 `pre_render_note` binding,
    and every Q28 observation. Counts alone cannot establish closure.
11. **Closure is not quality.** A structurally closed record may contain
    failed, missing, truncated, or invalid unit conditions. Those conditions
    remain visible to Q10/Q14/Q15 and do not become a Q28 pass, fail, gate,
    authority, or metric result.

#### Logical artifact set and per-unit binding boundary

The frozen artifact responsibilities are:

1. a pre-capture coverage plan;
2. a per-attempt work-unit output envelope; and
3. a coverage-closure artifact.

The Q28 closure now references the separately versioned Q17 per-work-unit
owner receipt defined in section 2.138. Existing Q15/Q16–Q21 slot/history
records remain owner history artifacts, and Q28 adds only a typed reference
and direct plan/work-unit/attempt binding validation; it does not create a
competing receipt schema. The exact Q28 schema identifiers for the three Q28
responsibilities are frozen in D1 below.

The frozen per-attempt output envelope has exactly these required bindings:

| Field | Frozen meaning |
| --- | --- |
| `coverage_plan_sha256` | Exact immutable plan digest. |
| `work_unit_id` | Exactly one planned work-unit identity. |
| `attempt_ordinal` | The ordinal from the owner-controlled attempt/receipt history; Q28 does not define retry or repeat semantics. |
| `output_condition` | Q28 structural condition: `complete`, `missing`, `failed`, `truncated`, or `invalid`. It is not a Q10 quality state or Q15 collection state. |
| `pre_render_note` | Nullable typed Q26 artifact reference. It is `null` when no valid Q26 pre-render note artifact exists; otherwise it must resolve to the exact Q26 artifact for this plan, unit, and attempt. |

The receipt reference is carried by the selected D6 attempt-binding shape in
the closure, not by the output envelope itself. This one-way binding avoids a
digest cycle when an owner-controlled receipt also references the output
envelope. The condition vocabulary above is closed for Q28's structural
observation layer; the owner-controlled receipt and Q10/Q15 status remain
authoritative for their scopes.

The option analyses in Q28-D1–D8 and D11 below are retained as superseded
design history. The selected contract in **Q28 final frozen schema contract**
is authoritative; any earlier statement that a recommendation was not frozen
no longer describes the current decision state.

### Q28-D1 — schema identifiers and version family

The responsibility boundary is frozen; the identifier family is not.

**Option A — three explicit benchmark-Generation schemas (recommended)**

- `benchmark-generation-coverage-plan/1.0.0`;
- `benchmark-generation-work-unit-output/1.0.0`; and
- `benchmark-generation-coverage-closure/1.0.0`.

Receipt history remains Q15/Q16–Q21-owned and is referenced by Q28. This is
the clearest ownership boundary and avoids inventing a second receipt schema.

**Option B — add a Q28 receipt-binding schema**

Add `benchmark-generation-work-unit-receipt-binding/1.0.0` as a separate
artifact. This makes the per-unit history index explicit, but duplicates
receipt binding responsibilities and increases compatibility work with Q15.

**Option C — one role-discriminated Q28 envelope**

Use one `benchmark-generation-coverage/1.0.0` schema with an `artifact_role`
discriminator. This reduces identifier count but weakens artifact-level type
separation and makes independent revision of plan, output, and closure harder.

Historical review note: the recommendation was not frozen at the prior review.
The selected family below uses the existing major/minor/patch rules:
incompatible required fields, enums, identity, reference, or canonicalization
require a major version; compatible optional fields require a minor version;
documentation-only clarification requires a patch version.

### Q28-D2 — work-unit stable identity seed

The following identity inputs are frozen as eligible inputs: the identity
family/version, exact reference-document digest, the primary assignment,
context-only declaration, route-decision digest, and execution-contract
digest. Attempt ordinal, run ID, retry/repeat identity, provider response,
content, timestamp, cost, and hardware are forbidden identity inputs.

The seed choice remains open:

1. **Primary assignment only:** canonical reference digest plus the ordered
   primary source-unit IDs. It maximizes reuse when context overlap changes,
   but two different execution envelopes could share an identity.
2. **Exact planned envelope (recommended):** canonical reference digest,
   ordered primary source-unit IDs, ordered context-only source-unit IDs,
   route-decision digest, and execution-contract digest. It identifies the
   actual immutable unit being executed, but changing overlap or execution
   bindings creates new work-unit identities.
3. **Plan-local identity:** plan ID/revision plus a canonical work-unit
   ordinal. It is simple and collision-resistant inside one plan, but it does
   not preserve logical identity across equivalent plan revisions.

Historical review note: the seed choice was unresolved at the prior review.
The selected exact planned-envelope seed below is authoritative; changing any
seed input creates a new work-unit identity, and old outputs and receipts
remain readable under the old plan.

### Q28-D3 — primary assignment representation

The partition invariant is frozen: all source-unit IDs must be covered exactly
once as primary assignments. The serialized representation remains open:

1. **Work-unit membership arrays (recommended):** each work unit carries an
   ordered `primary_source_unit_ids` array; the plan validator proves that the
   arrays form an exact partition.
2. **Explicit assignment records:** the plan carries one record per source
   unit, `{source_unit_id, work_unit_id}`; work-unit membership is derived.
   This makes the exactly-one rule very direct but increases artifact size.
3. **Inclusive source ranges:** each work unit carries section/range records
   and the validator expands them to source units. This is compact for
   contiguous plans but is more fragile for non-contiguous hierarchy and table
   structures.

The contract must not store both an authoritative membership array and an
authoritative assignment map unless one is explicitly derived; duplicate
authorities would allow silent divergence.

### Q28-D4 — context-only overlap representation

The meaning is frozen: overlap is an explicit relation with role
`context_only`, and no overlap reference is primary. The exact representation
remains open:

1. **Per-work-unit ordered IDs (recommended):**
   `context_only_source_unit_ids` contains source-unit identities in reference
   order. It is easy to validate and does not introduce a numeric overlap
   measure.
2. **Plan-level overlap edges:** each record contains
   `{work_unit_id, source_unit_id, role=context_only}`. This makes the
   non-primary relation independently queryable but adds one record per edge.
3. **Section/range descriptors:** overlap is expressed as section/range
   references. This is compact but risks treating a range as an assignment and
   makes non-contiguous context harder to represent.

Historical review note: the representation choice was unresolved at the prior
review. The selected per-work-unit ordered-ID representation below is
authoritative. A source unit may be context-only in zero, one, or multiple
work units; context-only occurrence does not alter the primary partition.

### Q28-D5 — work-unit hierarchy, dependency DAG, and planned scheduling

The graph semantics are frozen: work-unit references are typed, same-plan,
acyclic, and content-independent. Q28 may represent source hierarchy,
execution dependency, and merge dependency, but it may not encode provider
capacity, concurrency limits, retry policy, or Q15 run membership.

The representation remains open:

1. **Node-local parent/predecessor fields:** each work unit carries an optional
   hierarchy parent and an ordered predecessor list. This is readable and
   compact, but relation validation is distributed across nodes.
2. **Explicit edge records (recommended):** one graph record contains
   `{predecessor_work_unit_id, successor_work_unit_id, edge_kind}` with closed
   edge kinds `hierarchy`, `execution_dependency`, and `merge_dependency`.
   This makes the DAG and edge ownership explicit.
3. **Separate hierarchy tree plus dependency DAG:** source hierarchy and
   execution/merge dependencies are independent nested records. This is the
   clearest semantic model but adds another artifact substructure and more
   cross-reference validation.

The planned schedule must be represented as a deterministic order or an
equivalent owner-approved order derivation; it must not be inferred from
provider completion time. The exact order representation is coupled to D7 and
is not frozen here.

### Q28-D6 — work-unit terminal outcome references

The safety obligation is frozen: the closure must point to the immutable
attempt/receipt history for every planned work unit and must make the selected
terminal outcome, if one exists, traceable to its original receipt and output
envelope. The representation remains open:

1. **Inline attempt references plus terminal pointer (recommended):** the
   closure stores an ordered tuple of per-unit attempt bindings and a
   `terminal_attempt_ordinal` pointer. This is self-auditing without owning
   retry semantics.
2. **Per-unit history index artifact:** a separate immutable Q28 index stores
   all attempt/output/receipt references; closure stores the history digest and
   terminal pointer. This keeps closure smaller but adds the D1 artifact and
   revision surface.
3. **Terminal receipt only:** closure stores only the terminal receipt digest
   and derives earlier history from Q15 collection artifacts. This is smaller
   but is unsafe when the collection is incomplete or when a later attempt
   could hide a failed/truncated earlier attempt.

Option C was not recommended. The prior review left the choice unresolved
because the exact Q15 receipt/collection realization and Q24 formal store were
adjacent pending boundaries. The selected inline-attempt-binding shape below
is authoritative; a missing history reference is an explicit closure failure,
not an empty success.

### Q28-D7 — merge plan and deterministic merge order

The semantic requirement is frozen: merge order is an immutable, auditable
binding over work-unit identities and cannot be selected from generated
content, provider completion time, or a quality result. The exact
representation remains open:

1. **Explicit planned and observed sequences (recommended):** the plan stores
   `planned_merge_order`; the closure stores `observed_merge_order`. Each is a
   canonical sequence of work-unit IDs, and the closure records any difference
   without erasing the plan.
2. **DAG plus deterministic topological rule:** the plan stores merge edges;
   the merge order is derived by a frozen topological algorithm and tie-break
   rule. This reduces duplicate order data but makes the algorithm itself a
   compatibility dependency.
3. **Separate merge-plan artifact:** a dedicated immutable merge-plan record
   stores dependencies, order, and merge actions. This isolates merge
   revisions but expands D1 and closure binding.

Historical review note: the representation choice was unresolved at the prior
review. The selected explicit planned/observed sequence representation below
is authoritative. A merge order must not contain source text, generated
content, quality values, or threshold decisions. A unit not merged because it
is missing, failed, truncated, or invalid remains visible through its unit
outcome; it cannot disappear from closure accounting.

### Q28-D8 — coverage-closure completeness representation

The following logical completeness contract is frozen because aggregate counts
cannot prove exhaustive closure. Its exact JSON/container representation
remains open; the snippet is illustrative rather than a selected schema:

```json
{
  "coverage_closure_state": "<identity-complete-or-non-closed>",
  "coverage_plan_sha256": "<plan-digest>",
  "unit_outcomes": [
    {
      "work_unit_id": "<work-unit-id>",
      "attempt_history_ref": "<owner-history-ref>",
      "terminal_outcome_ref": "<owner-terminal-ref-or-null>",
      "coverage_condition": "complete"
    }
  ],
  "merge_order": "<D7-selected-order-binding>",
  "final_pre_render_note": "<D9-binding>",
  "observations": []
}
```

`unit_outcomes` is exactly one record for every planned work-unit ID. Its ID
set must equal the plan's work-unit ID set; duplicate, missing, foreign, or
out-of-plan IDs are invalid. `coverage_condition` uses the closed structural
observation vocabulary `complete | missing | failed | truncated | invalid`.
It does not replace the Q10/Q15 terminal or validity status.

The closure representation must distinguish an identity-complete closure from
one that is not closed, but the exact serialized state enum remains part of
the open D8 choice. The recommended vocabulary is `closed | not_closed`.
`closed` requires the plan digest, all unit outcomes, the selected D7
merge-order binding, the D9 final-note binding, and all referenced immutable
artifacts to validate. A closed record may still contain non-`complete` unit
conditions; that is visible audit evidence, not a quality decision. Missing
unit outcomes or missing required bindings force the non-closed state.

Counts such as planned-unit count, complete count, and exception count may be
derived for display, but are not closure authority and must not replace the
per-unit vector. The exact serialized top-level artifact name remains D1;
the per-unit completeness semantics are frozen.

Safe representation options are:

1. **Explicit ordered outcome records (recommended):** the JSON array shown
   above, with one record per work unit. This is easiest to audit and to bind
   to a canonical order, but is verbose.
2. **Keyed outcome map:** one object keyed by `work_unit_id`, plus a canonical
   key-order rule. This is compact and direct, but introduces a second
   object-key ordering dependency.
3. **Separate outcome-vector artifact:** closure stores an immutable digest for
   a per-unit vector artifact. This keeps closure small but adds another
   artifact and compatibility boundary.

Historical review note: the container choice was unresolved at the prior
review. The selected explicit ordered outcome-record representation below is
authoritative. It preserves the exact per-unit ID set and must not be replaced
with counts, a success bit, or a denominator scalar.

### Q28-D9 — final `pre_render_note` binding

This binding is frozen and is a Q26 reference, not a Q28 note schema. The
closure contains exactly one final pre-render-note reference with this shape:

```json
{
  "schema_version": "benchmark-note-document/1.0.0",
  "artifact_role": "pre_render_note",
  "document_id": "<reference-document-document-id>",
  "reference_document_sha256": "<plan-reference-digest>",
  "sha256": "<lowercase-sha256-of-q26-artifact>"
}
```

The referenced Q26 artifact must validate under Q26's exact schema, document
identity, reference digest, node/citation/lineage rules, and canonical bytes.
Q28 must not copy its nodes, citations, source excerpts, lineage, or
producer-provenance fields into the closure. A rendered projection is not a
valid substitute: Q28 closes against the renderer-neutral final
`pre_render_note`; Q26 owns the later rendered projection.

### Q28-D10 — omission, duplication, truncation, ordering-loss, and contradiction observations

Q28 records neutral observations with this closed `observation_kind` enum:

- `omission`;
- `duplication`;
- `truncation`;
- `ordering_loss`; and
- `internal_contradiction`.

Every observation is immutable and carries identity-only references to its
affected source units, work units, output nodes, and observation/evidence
basis artifacts. A logical shape is:

```json
{
  "observation_id": "<immutable-observation-id>",
  "observation_kind": "omission",
  "source_unit_refs": ["<source-unit-ref>"],
  "work_unit_ids": ["<work-unit-id>"],
  "output_node_refs": ["<q26-note-node-ref>"],
  "basis_refs": ["<immutable-basis-ref>"]
}
```

The arrays are references, not copied content. An omission may have no output
node reference; a duplication or ordering-loss observation may reference more
than one node or source unit. The exact reference envelope is governed by D11.

Q28 does not define the detector, numeric truncation boundary, overlap or
ordering metric, contradiction threshold, support state, blocker, or quality
effect. Q14 owns measurement/scoring and Q8/Q10/Q12 own contradiction/support
and authority semantics. `internal_contradiction` must never be serialized as
Q8's `candidate_internal_contradiction` support state by Q28. If the required
basis is absent or disputed, the applicable Q10 unresolved/validity record is
referenced rather than inventing a Q28 outcome.

### Q28-D11 — evidence and source-reference mapping boundary

The ownership boundary is frozen:

- Q28 source references identify the planned source unit and execution
  lineage only;
- Q26 citations remain the authoritative source-locator references on the
  generated note;
- Q6 owns `source_references`, `evidence_items`, and `expected_claims`;
- Q14 owns candidate/reference alignment, metric inputs, formulas, and
  scorer meaning; and
- Q28 must not create, merge, split, score, or relabel Q6/Q8/Q14 semantic
  records.

The Q28-owned identity-only source reference is exactly the four-field
`reference_document_id`, `section_id`, `element_id`, and `order` object shown
above. A Q28 output-node reference contains the Q26 artifact digest and
`node_id`; a Q26 citation reference, when present, contains the same Q26
artifact digest, `node_id`, and `citation_id`. Neither reference copies source
text or locator payloads.

An external evidence/reference record may be carried only as an opaque
immutable reference with `{schema_version, sha256, record_type, record_id}`.
`record_type` and `record_id` are interpreted by the owning Q6/Q8/Q14/Q10
artifact; Q28 validates only the artifact digest and does not infer semantic
support. The exact placement of these identity references—inline on each
observation, in a plan-level mapping table, or in a separately referenced
mapping artifact—remains open under D11:

1. **Inline mapping records (recommended):** closure carries typed source,
   work-unit, Q26 node/citation, and opaque external-record refs together.
2. **Plan-level mapping table:** closure carries one deduplicated mapping table
   and observations reference mapping IDs. This reduces repetition but adds a
   local mapping identity layer.
3. **Digest-only mapping artifact:** closure carries only the mapping-artifact
   digest. This is a stronger privacy boundary but makes closure validation
   depend on another artifact.

Historical review note: the placement choice was unresolved at the prior
review. The selected inline typed mapping representation below is authoritative.
None of these references may turn an external record into a Q28-owned evidence
or scoring decision.

### Q28-D12 — canonical serialization, SHA-256, revision, and compatibility

The following rules are frozen from section 2.13 and apply to every Q28
artifact, nested contract object, and external digest record:

- canonical JSON is UTF-8 without BOM;
- object keys are sorted deterministically;
- JSON is compact with no insignificant whitespace or trailing newline;
- strings retain their exact approved Unicode code points; no implicit NFC,
  NFKC, case, punctuation, whitespace, or source-text normalization is
  applied;
- duplicate keys, NaN, Infinity, and non-integer numeric values are invalid;
- JSON escaping is deterministic and non-ASCII text is emitted as UTF-8;
- arrays preserve contract-defined semantic order and are not generically
  sorted; and
- the serializer behavior is part of the schema version.

The external digest is lowercase SHA-256 over the exact canonical bytes. No
Q28 payload contains its own digest. A separate ASCII checksum record or
binding manifest stores the digest. Plan, work-unit output envelope, owner
receipt, owner attempt history, Q26 pre-render note, merge/closure artifact,
and evidence/basis artifact retain separate digests.

The following array orders are frozen where their semantic source is already
unambiguous:

- reference sections and source units use the reference-document order;
- primary and context-only source-unit references use source order;
- a source-unit reference never sorts by copied text or generated content;
- observation references use their declared artifact-local order; and
- unordered reference sets, when introduced by the selected D1–D11 shape,
  must use a declared stable key rather than process or database order.

The exact work-unit, dependency-edge, merge-order, attempt-history, and
mapping-array order is frozen by the selected D1–D8/D11 contract in the final
schema section below.

All Q28 artifacts are immutable. A change to the reference digest, source-unit
inventory, primary assignment, context-only declaration, work-unit identity
seed, routing policy/decision binding, execution contract, dependency graph,
planned merge order, output binding, observation basis, final-note digest, or
canonicalization changes the relevant artifact revision and external digest;
no artifact is edited in place. A receipt or attempt appended under Q15 does
not mutate the plan; it creates a new immutable history record and a new
closure binding when closure is rebuilt. A schema required-field, field
meaning, enum, identity, reference, or canonicalization incompatibility is a
major revision; a compatible optional field is a minor revision; and a
documentation-only correction is a patch revision. Readers reject unknown
schema versions and silently coercing a newer or incompatible revision is
forbidden.

#### Q28 final frozen schema contract

The following contract freezes the user-selected D1–D8 and D11 options. It is
the authoritative Q28 schema contract; the preceding option text is historical
context only. Q28 still does not own Q15/Q17/Q21 receipt semantics, Q14
measurement, Q10/Q12 authority, or any numeric threshold.

##### Common scalar and reference rules

All Q28 identifiers and digests use these closed rules:

- `Sha256` is exactly 64 lowercase hexadecimal characters.
- `Identifier` is a non-empty ASCII string matching
  `^[A-Za-z0-9][A-Za-z0-9_.-]*$`.
- `plan_revision` is a non-empty `Identifier` chosen by the benchmark
  manifest; the canonical payload digest remains the authoritative content
  identity.
- `work_unit_id` is exactly `work-unit-` followed by 64 lowercase SHA-256
  hexadecimal characters.
- `attempt_ordinal` and all source `order` values are positive or
  non-negative integers respectively; Q28 does not define retry or repeat
  meaning for an ordinal.
- Nullable references use JSON `null`, never an empty string or invented
  digest.

The exact reusable references are:

| Reference | Exact fields |
| --- | --- |
| `ReferenceDocumentRef` | `schema_version="normalized-document/1.0.0"`, `artifact_role="reference_document"`, `document_id`, `sha256`. |
| `RoutingPolicyRef` | `schema_version="benchmark-generation-routing-policy/1.0.0"`, `policy_id`, `policy_revision`, `sha256`, `configuration_sha256`. |
| `RouteDecisionRef` | `schema_version="benchmark-generation-route-decision/1.0.0"`, `artifact_role="route_decision"`, `sha256`. |
| `ExecutionContractRef` | `contract_id`, `sha256`. |
| `ExternalOwnerRecordRef` | `schema_version`, `sha256`, `record_type`, `record_id`. |
| `Q26PreRenderNoteRef` | `schema_version="benchmark-note-document/1.0.0"`, `artifact_role="pre_render_note"`, `document_id`, `reference_document_sha256`, `sha256`. |
| `Q26NodeRef` | `artifact_sha256`, `node_id`. |
| `Q26CitationRef` | `artifact_sha256`, `node_id`, `citation_id`. |

`ExternalOwnerRecordRef` is an opaque cross-owner reference. For receipts it
points to the exact Q15/Q17/Q21 owner artifact. Q28 validates the referenced
owner schema, digest, record identity, and its owner-defined binding to the
same plan/unit/attempt; it does not copy or reinterpret owner fields.

##### D1 — exact artifact schemas

Q28 has exactly these three schema identifiers and artifact roles:

| Schema identifier | Exact `artifact_role` | Required top-level fields |
| --- | --- | --- |
| `benchmark-generation-coverage-plan/1.0.0` | `coverage_plan` | `schema_version`, `artifact_role`, `plan_id`, `plan_revision`, `reference_document`, `routing_policy`, `route_decision`, `execution_contract`, `source_sections`, `source_units`, `work_units`, `dependency_edges`, `planned_execution_order`, `planned_merge_order`. |
| `benchmark-generation-work-unit-output/1.0.0` | `work_unit_output` | `schema_version`, `artifact_role`, `coverage_plan_sha256`, `work_unit_id`, `attempt_ordinal`, `output_condition`, `pre_render_note`. |
| `benchmark-generation-coverage-closure/1.0.0` | `coverage_closure` | `schema_version`, `artifact_role`, `coverage_closure_state`, `coverage_plan_sha256`, `unit_outcomes`, `observed_merge_order`, `final_pre_render_note`, `source_reference_mappings`, `observations`. |

No Q28 receipt schema exists. Receipt/history artifacts remain owned by
Q15/Q17/Q21 and are referenced with `ExternalOwnerRecordRef`.

The schemas are strict: unknown top-level fields, unknown nested fields, and
unknown enum values are invalid. No Q28 artifact embeds its own digest.

##### D2 — exact work-unit identity derivation

`work_unit_id` is derived from this exact canonical seed object:

```json
{
  "identity_schema_version": "benchmark-generation-work-unit/1.0.0",
  "reference_document_sha256": "<plan-reference-digest>",
  "primary_source_unit_ids": ["<element-id>"],
  "context_only_source_unit_ids": [],
  "route_decision_sha256": "<route-decision-digest>",
  "execution_contract_sha256": "<execution-contract-digest>"
}
```

The seed bytes use the Q28 canonical JSON rules, with sorted object keys,
contract-defined array order, UTF-8, compact encoding, and no trailing
newline. The ID is:

```text
work_unit_id = "work-unit-" + sha256(seed_canonical_bytes)
```

`primary_source_unit_ids` and `context_only_source_unit_ids` are ordered by
the reference-document element `order`, ascending. They contain `element_id`
values from the same referenced document. The seed includes no `plan_id`,
`plan_revision`, run ID, attempt ordinal, output, provider response, timestamp,
cost, hardware, or generated content. Any change to a seed field creates a
new work-unit identity; old output and receipt history remains bound to the
old plan/work-unit identity.

##### D3/D4 — exact work-unit specification and assignment rules

Each `WorkUnitSpec` contains exactly:

```json
{
  "work_unit_id": "work-unit-<64-lowercase-hex>",
  "primary_source_unit_ids": ["<element-id>"],
  "context_only_source_unit_ids": []
}
```

`primary_source_unit_ids` is non-empty, unique, and ordered by source
element order. `context_only_source_unit_ids` may be empty, is unique, and is
also ordered by source element order. The two arrays must be disjoint within
one work unit.

The plan has exactly one authoritative assignment representation: the
`primary_source_unit_ids` arrays in `work_units`. There is no second
authoritative source-unit-to-work-unit map. The validator must prove:

1. every planned source-unit ID occurs in exactly one primary array;
2. the union of all primary arrays equals the complete plan `source_units`
   ID set;
3. every work unit has at least one primary source unit;
4. every primary and context-only ID exists in `source_units` and belongs to
   the bound reference document; and
5. a context-only ID may occur in zero, one, or many work units, but never
   becomes a primary assignment through overlap.

Context-only references provide lineage/context declaration only. They create
no second primary assignment, no denominator entry, no scoring credit, and no
relevance or selection behavior.

`SourceSectionRef` contains exactly `section_id`, `parent_section_id`,
`heading_element_id`, `start_order`, and `end_order`. `SourceUnitRef` contains
exactly `reference_document_id`, `section_id`, `element_id`, and `order`.
`source_sections` must include every reference-document section in reference
order. `source_units` must include every reference-document element exactly
once in zero-based element order. No section or element selection predicate
exists in Q28.

##### D5 — exact typed dependency DAG and planned order

Each `DependencyEdge` contains exactly:

```json
{
  "predecessor_work_unit_id": "work-unit-<64-lowercase-hex>",
  "successor_work_unit_id": "work-unit-<64-lowercase-hex>",
  "edge_kind": "hierarchy"
}
```

`edge_kind` is closed to exactly:

- `hierarchy`;
- `execution_dependency`; and
- `merge_dependency`.

Every edge is same-plan, references existing work units, is not self-referential,
and is unique by `(predecessor_work_unit_id, successor_work_unit_id,
edge_kind)`. The union of all edge kinds must be acyclic. Edge direction is
`predecessor -> successor`; for `hierarchy`, this means parent/source unit to
child unit; for the other kinds it means required predecessor to dependent
successor.

`planned_execution_order` is a canonical sequence containing every work-unit
ID exactly once and is a topological order of all dependency edges. It is an
execution-order declaration only; it does not define concurrency, provider
capacity, retry, repeat, run membership, or collection semantics.

`planned_merge_order` is a canonical sequence containing every work-unit ID
exactly once and is a topological order of every `merge_dependency` edge. It
is independent from the edge list: the sequence records order, while the edge
list records dependency meaning. Neither representation may be reconstructed
from provider completion time or generated content.

No concurrency, provider-capacity, retry, repeat, run-membership, or Q15
collection field is present in Q28.

##### D6 — exact per-unit attempt and terminal binding

`output_condition` is closed to exactly `complete`, `missing`, `failed`,
`truncated`, and `invalid`. It is a Q28 structural condition only; it does not
redefine any Q10 quality state or Q15/Q17/Q21 receipt status.

Each closure `UnitOutcome` contains exactly:

```json
{
  "work_unit_id": "work-unit-<64-lowercase-hex>",
  "attempts": [
    {
      "attempt_ordinal": 1,
      "output_sha256": "<work-unit-output-digest>",
      "receipt_ref": {
        "schema_version": "<owner-schema-version>",
        "sha256": "<owner-receipt-digest>",
        "record_type": "<owner-record-type>",
        "record_id": "<owner-record-id>"
      }
    }
  ],
  "terminal_attempt_ordinal": 1,
  "coverage_condition": "complete"
}
```

`attempts` is an ordered immutable array. Its entries are unique by
`attempt_ordinal` and sorted ascending; Q28 does not require or reinterpret
ordinal contiguity beyond the owner contract. Every `output_sha256` must
resolve to one `benchmark-generation-work-unit-output/1.0.0` artifact for the
same plan, work unit, and attempt. Every `receipt_ref` must resolve to the
owner-controlled receipt/history artifact for that same plan, work unit, and
attempt; neither reference is nullable.

`terminal_attempt_ordinal` is either a value present in `attempts` or `null`.
It points only to the selected terminal attempt; it does not redefine terminal
status. `null` means no terminal attempt is available and forces
`coverage_closure_state=not_closed`. Prior failed/truncated/invalid attempts
remain in `attempts` and can never be hidden by the selected terminal attempt.

Q28 does not define retry, repeat, terminal status, run membership, collection,
or attempt eligibility. Those meanings remain in Q15/Q17/Q21 artifacts.

##### D7 — exact planned and observed merge order

The plan's `planned_merge_order` and the closure's `observed_merge_order` are
both canonical sequences of `work_unit_id` values. `planned_merge_order` is
the immutable full sequence stored by the plan. `observed_merge_order` may be
empty or partial, contains no duplicate IDs, and contains only work units in
the plan. It records the actual observed merge sequence and may differ from
the planned sequence.

The observed sequence never mutates, replaces, or is substituted into the
plan. For every `merge_dependency` edge `u -> v`, if `v` appears in the
observed sequence, `u` must also appear earlier in that sequence. The
dependency-edge array remains the authority for dependency meaning; order
arrays remain the authority for planned/observed ordering. A sequence cannot
encode or infer an edge.

##### D8 — exact closure schema and semantics

`coverage_closure_state` is closed to exactly:

- `closed`;
- `not_closed`.

`coverage_condition` is closed to exactly:

- `complete`;
- `missing`;
- `failed`;
- `truncated`; and
- `invalid`.

The closure's `unit_outcomes` array contains exactly one `UnitOutcome` for
every plan work-unit ID. Its ID set must equal the plan work-unit ID set,
with no duplicates, missing IDs, foreign IDs, or alternate assignment map.

`closed` means structural/identity closure only. It requires:

- exact plan digest binding;
- exact work-unit ID set equality;
- complete owner-controlled attempt/output/receipt references for every unit;
- a non-null terminal attempt for every unit;
- valid `observed_merge_order` and dependency checks;
- valid inline mapping and observation references; and
- a valid non-null final Q26 `pre_render_note` binding.

`closed` may contain `failed`, `truncated`, or `invalid` unit conditions. It
does not mean quality pass, authority, gate pass, score, or adoption. A
`missing` condition can also be closed when the missing output is explicitly
represented by a valid immutable output envelope/receipt history. Missing
outcome entries, missing required history/binding, null terminal pointers, or
missing final-note bindings force `not_closed`.

Aggregate planned/complete/exception counts may be retained as derived display
facts only. They are never closure authority and cannot replace
`unit_outcomes`.

##### D9 — exact final `pre_render_note` binding

`final_pre_render_note` is exactly one `Q26PreRenderNoteRef`:

```json
{
  "schema_version": "benchmark-note-document/1.0.0",
  "artifact_role": "pre_render_note",
  "document_id": "<plan-reference-document-id>",
  "reference_document_sha256": "<plan-reference-document-sha256>",
  "sha256": "<q26-pre-render-note-digest>"
}
```

The referenced artifact must validate under Q26's exact schema and its
`document_id`/`reference_document_sha256` must equal the plan bindings. Q28
does not copy Q26 nodes, citations, locators, lineage, or producer fields. A
rendered projection is not a valid substitute for the final pre-render note.

##### D10 — exact neutral observations

`observation_kind` is closed to exactly `omission`, `duplication`,
`truncation`, `ordering_loss`, and `internal_contradiction`.

Each observation contains exactly:

```json
{
  "observation_id": "<immutable-observation-id>",
  "observation_kind": "omission",
  "source_unit_refs": ["<source-unit-ref>"],
  "work_unit_ids": ["work-unit-<64-lowercase-hex>"],
  "output_node_refs": ["<q26-node-ref>"],
  "basis_refs": ["<external-owner-record-ref>"]
}
```

The arrays contain identity/digest references only; they never copy source
text, generated content, locator payloads, or semantic claim content. An
omission may have an empty `output_node_refs` array. `internal_contradiction`
is a neutral Q28 observation and is never serialized as Q8's
`candidate_internal_contradiction` support state.

Q14 owns observation detection/measurement/scoring formulas. Q8/Q10/Q12 own
contradiction, support, blocker, authority, and quality semantics. Truncation
thresholds and contradiction-detector thresholds remain pending.

##### D11 — exact inline typed mapping references

The closure's `source_reference_mappings` array contains exactly:

```json
{
  "source_unit_ref": {
    "reference_document_id": "<document-id>",
    "section_id": "<section-id>",
    "element_id": "<element-id>",
    "order": 0
  },
  "work_unit_id": "work-unit-<64-lowercase-hex>",
  "output_node_ref": {
    "artifact_sha256": "<q26-artifact-digest>",
    "node_id": "<q26-node-id>"
  },
  "citation_ref": {
    "artifact_sha256": "<q26-artifact-digest>",
    "node_id": "<q26-node-id>",
    "citation_id": "<q26-citation-id>"
  },
  "external_owner_record_refs": [
    {
      "schema_version": "<owner-schema-version>",
      "sha256": "<owner-artifact-digest>",
      "record_type": "<owner-record-type>",
      "record_id": "<owner-record-id>"
    }
  ]
}
```

`output_node_ref`, `citation_ref`, and `external_owner_record_refs` may be
empty/null when no such reference exists. If `citation_ref` is present, its
`artifact_sha256` and `node_id` must match `output_node_ref`. The source ref
and work-unit ID must resolve to the same plan. These mappings are inline
lineage/reference bindings only; the plan's `primary_source_unit_ids` remains
the sole assignment authority. Q28 validates only identity, schema, and
digest; it never infers semantic support, coverage, relevance, or score from a
mapping.

##### Exact canonical array ordering

The following order is frozen and is part of the three Q28 schema versions:

- `source_sections`: exact reference-document section order;
- `source_units`: exact reference-document element order;
- `primary_source_unit_ids` and `context_only_source_unit_ids`: ascending
  source element `order`;
- `work_units`: ascending tuple `(first_primary_source_order, work_unit_id)`;
- `dependency_edges`: ascending tuple `(edge_kind_order, predecessor_id,
  successor_id)`, where `edge_kind_order` is `hierarchy=0`,
  `execution_dependency=1`, `merge_dependency=2`;
- `planned_execution_order`, `planned_merge_order`, and
  `observed_merge_order`: declared sequence order, never generic sorting;
- `unit_outcomes`: the plan's canonical `work_units` order;
- `attempts`: ascending `attempt_ordinal`;
- `source_reference_mappings`: ascending tuple `(source_unit.order,
  work_unit_id, output_node_ref_presence, output_artifact_sha256,
  output_node_id, citation_ref_presence, citation_id)`; null presence sorts
  before present;
- `observations`: ascending `observation_id`; and
- all `external_owner_record_refs`: ascending tuple `(schema_version,
  record_type, record_id, sha256)`.

No array is sorted by source text, generated content, provider completion time,
database order, timestamp, or score.

##### Cross-artifact validation and digest checks

The deterministic validator must perform these checks:

1. Recompute every referenced canonical artifact digest and reject mismatches.
2. Validate the exact reference-document schema/role/digest and require every
   plan section/unit identity and order to match it.
3. Validate the Q29 policy/route-decision references, including policy ID,
   policy revision, configuration digest, reference-document digest, and
   execution-contract identity; Q28 never recomputes route selection.
4. Validate every work-unit ID from its exact D2 seed and reject duplicate or
   stale identities.
5. Validate the complete primary partition, context-only rules, all typed
   edges, acyclicity, planned orders, and merge-dependency ordering.
6. Validate each output artifact's plan/unit/attempt binding and, when
   present, its Q26 pre-render-note schema, role, document ID, and reference
   digest.
7. Validate each owner receipt/history reference through the owner schema and
   require the owner artifact to bind the same plan/unit/attempt. Q28 does not
   reinterpret owner terminal/retry/repeat status.
8. Validate closure unit-outcome ID equality, attempt references,
   `terminal_attempt_ordinal`, observed merge order, final-note binding,
   inline mappings, and observation basis references.
9. Require `coverage_closure_state=closed` exactly when all structural and
   identity bindings above close; otherwise require `not_closed`.
10. Reject any aggregate count, score, quality, authority, gate, or semantic
    support field if supplied as a Q28 closure authority.

##### Revision and compatibility rules

The three Q28 schemas are independently versioned but mutually compatible
only when all referenced contract/schema versions and digest bindings remain
compatible. A schema change to a required field, field meaning, enum, identity
seed, reference shape, canonical ordering, or validation rule requires a new
major version. A compatible optional field requires a new minor version.
Documentation-only clarification requires a patch version.

The following changes create new immutable content-addressed artifacts and
never mutate old records:

- any plan binding, source section/unit inventory, primary assignment,
  context-only array, work-unit identity seed, edge, planned order, or merge
  order change creates a new plan revision;
- any attempt output envelope change creates a new output artifact/attempt
  record; an owner receipt/history change creates a new owner artifact;
- any observed merge order, unit outcome, terminal pointer, mapping,
  observation, or final-note digest change creates a new closure artifact;
- a Q29 policy/route/execution-contract/reference digest change requires a new
  compatible Q28 plan; and
- a Q26 pre-render-note schema/digest change requires a new output/closure
  binding, while Q14 measurement/scorer changes do not require a new Q28 plan
  unless a Q28 observation or mapping input itself changes.

Q15/Q17/Q21 retries, repeats, collection revisions, and receipt history are
append-only owner artifacts. They do not rewrite a Q28 plan or erase previous
attempt bindings. A new closure may reference the new owner history under the
same compatible plan; incompatible owner schema or binding changes require a
new compatible Q28 schema/reference revision.

#### Q28-D1–D12 decision register

| Item | Status after this foundation round |
| --- | --- |
| D1 | **Frozen — Option A.** Three exact Q28 schemas; no Q28 receipt schema. |
| D2 | **Frozen — Option 2.** Exact planned-envelope identity seed with the six specified inputs and no run/attempt/output/provider/time/cost/hardware inputs. |
| D3 | **Frozen — Option 1.** Ordered per-work-unit primary ID arrays are the sole authoritative assignment representation and form an exact complete partition. |
| D4 | **Frozen — Option 1.** Ordered per-work-unit context-only ID arrays; zero/one/many overlap is allowed without primary or score credit. |
| D5 | **Frozen — Option 2.** Explicit typed same-plan acyclic edge records with `hierarchy`, `execution_dependency`, and `merge_dependency`; no concurrency/capacity/retry/run semantics. |
| D6 | **Frozen — Option 1.** Ordered per-unit immutable attempt bindings with output/receipt refs and nullable terminal pointer; owner retry/repeat/terminal semantics remain external. |
| D7 | **Frozen — Option 1.** Plan owns `planned_merge_order`; closure owns `observed_merge_order`; both are canonical work-unit sequences and remain separate from edges. |
| D8 | **Frozen — Option 1.** Explicit ordered `unit_outcomes`, exact `closed | not_closed`, exact unit-ID set equality, and non-authoritative aggregate counts. |
| D9 | **Frozen.** Closure binds exactly one Q26 `benchmark-note-document/1.0.0` artifact with `artifact_role=pre_render_note`; Q28 does not copy Q26 fields. |
| D10 | **Frozen boundary; measurement pending.** Observation kinds are `omission`, `duplication`, `truncation`, `ordering_loss`, and `internal_contradiction`; Q14/Q8/Q10/Q12 own semantics and formulas. |
| D11 | **Frozen — Option 1.** Inline typed source/Q26/owner mapping references; Q28 validates identity/digest only and never infers semantic support, coverage, or score. |
| D12 | **Frozen.** Existing canonical JSON, external SHA-256, immutable revision, array-order, and compatibility rules apply. |

#### Remaining evidence and numeric pending frontier

This realization intentionally leaves the following pending and does not
encode a default:

- work-unit token, character, byte, or element size;
- overlap token/count/percentage or any equivalent numeric amount;
- merge thresholds, content-similarity rule, merge conflict rule, or
  contradiction detector threshold;
- numeric truncation boundary or ordering-loss tolerance;
- provider/context-capacity threshold or compatibility ceiling, owned by Q29
  and its evidence/configuration boundary;
- Q14 omission, duplication, truncation, ordering, contradiction, alignment,
  metric, scorer, aggregation, and gate-consumption formulas;
- Q15 repeat count, retry/replay/collection semantics, scheduling blocks,
  statistical method, and run membership; and
- Q10/Q12 validity, authority, blocker, quality, and contradiction effects.

Where an implementation needs one of these facts before the owner closes it,
the contract state is `evidence_required` or owner-pending. It must not be
represented as zero, unlimited, absent, successful, or a silently chosen
default.

#### Cross-question compatibility and implementation readiness

- **Q26:** Q28 binds the exact Q26 final `pre_render_note` digest and
  reference-document digest. It does not add work-unit fields to
  `BenchmarkNoteDocument`, change node/citation/locator/lineage identity, or
  treat a rendered projection as the final pre-render artifact.
- **Q29:** Q28 binds the Q29 policy reference and route-decision digest before
  generation. Q28 does not select a mode, copy Q29 input facts, or change
  route-conformance semantics. A Q29 revision invalidates the compatible Q28
  plan binding and requires a new immutable plan revision.
- **Q14:** Q28 observations and source/output references are upstream evidence
  bindings only. Q14 owns alignment, formulas, metric/scorer/result schemas,
  aggregation, and all measurement meaning; Q28 does not produce a score.
- **Q15/Q17/Q21:** Q28 consumes the exact per-work-unit owner receipt in
  section 2.138 and requires independent per-unit output/receipt history and
  terminal traceability, but does not define retry, repeat, scheduling,
  collection, or run membership. The broader runner and collection contracts
  remain owner-controlled; Q28 references them without redefining them.

Q28 is sufficient to begin implementation at its schema and validation
boundary. Implementation must use the frozen D1–D8/D11 representations and
the existing Q26/Q29/Q14/Q15/Q17/Q21 owner interfaces. It remains blocked only
where an owner-dependent numeric, algorithm, measurement, or evidence contract
is still pending; no implementation may invent a default for those facts or
claim that quality, metric, gate, authority, retry, repeat, or capacity policy
is closed.

### 2.138 Q15/Q17/Q21 per-work-unit receipt and history realization

This section resolves the owner-contract dependency left by Q28-D6. It freezes
the minimum owner-controlled artifact that a Q28 closure may reference. It does
not authorize runtime implementation, add a Q28 receipt schema, or decide
provider retry, stochastic repeat, scheduling, collection, quality, authority,
gate, or scoring policy.

#### R1 — split ownership

The contract is intentionally split across the existing owners:

| Owner | Frozen responsibility | Explicit non-responsibility |
| --- | --- | --- |
| Q15 execution topology | Logical run identity, repeat identity, per-work-unit attempt ordinal, retry/resume lineage, append-only history meaning, and the owner selection of a terminal attempt | Receipt serialization, Q28 closure, Q14 measurement, Q11 gates, or collection rewriting |
| Q17 runner receipt realization | The exact per-work-unit receipt envelope, lifecycle-role encoding, canonical bytes, immutable store write, external digest record, and durable lookup | Changing the existing slot-level runner receipt schemas or defining retry/repeat policy |
| Q21 collection materialization | Reconstruction of every work-unit receipt chain and slot/collection view, including failed, invalid, interrupted, and still-open history | Re-owning receipt fields, selecting quality, imputing missing attempts, or changing Q15 run membership |
| Q28 coverage closure | Typed reference and identity/digest validation of the owner receipt; structural closure only | Receipt schema, retry/repeat/terminal authority, history selection semantics, or collection semantics |

Q15 owns the meaning of the lifecycle and attempt relationships. Q17 owns the
serialized receipt artifact that carries those facts. Q21 consumes the
immutable receipt references when it materializes a collection. No owner is
permitted to make Q28 parse a RunPlan slot to infer
`coverage_plan_sha256`, `work_unit_id`, or the work-unit attempt ordinal.

#### R2 — topology review and selection

Three topologies were reviewed:

| Option | Trade-off | Decision |
| --- | --- | --- |
| A. Independent per-work-unit attempt receipt | Gives Q28 a direct, content-addressed lookup; supports multiple work units in one runner slot; keeps retry history append-only through explicit parent links; requires collection materialization to preserve all receipt references. | **Selected.** |
| B. Versioned extension of `runner-terminal-receipt/1.0.0` | Preserves one runner family but cannot safely change a slot-level `plan_sha256` into a coverage-plan binding; it also conflates outer slot attempts with per-unit attempts and would make old readers ambiguous. | Rejected. |
| C. Immutable per-work-unit history wrapper around owner receipts | Makes collection lookup convenient but adds another digest-bearing authority, creates a larger closure lookup surface, and couples Q21 history materialization to the Q17 receipt envelope. It is not needed when each immutable receipt carries an append-only parent link. | Rejected for v1; a future owner revision may add a wrapper without changing the receipt identity contract. |

The selected topology is therefore **A**: one immutable receipt artifact per
per-work-unit lifecycle record, with an append-only Q15 history chain formed by
the receipt parent links. Q21 materializes the chain as collection history;
there is no separate Q28 history artifact and no Q28 receipt schema.

#### R3 — exact owner schema identifier and role

The exact owner schema identifier is:

`benchmark-generation-work-unit-attempt-receipt/1.0.0`

Its only v1 artifact role is `work_unit_attempt_receipt`. The schema is
strict: unknown fields, unknown enum values, missing required fields, and
role/field combinations that violate the rules below are invalid. The
artifact payload does not contain its own digest.

The Q28 `ExternalOwnerRecordRef` for a closure-resolvable receipt must carry:

```json
{
  "schema_version": "benchmark-generation-work-unit-attempt-receipt/1.0.0",
  "sha256": "<receipt-artifact-sha256>",
  "record_type": "work_unit_attempt_receipt",
  "record_id": "<receipt-record-id>"
}
```

`runner-start-receipt/1.0.0`, `runner-terminal-receipt/1.0.0`, a Q15 slot
history reference, a Q21 collection reference, and a reduced or synthetic
record are not substitutes for this owner reference.

#### R4 — exact receipt fields and closed enums

The exact top-level fields of
`benchmark-generation-work-unit-attempt-receipt/1.0.0` are:

| Field | Required contract |
| --- | --- |
| `schema_version` | Literal `benchmark-generation-work-unit-attempt-receipt/1.0.0`. |
| `artifact_role` | Literal `work_unit_attempt_receipt`. |
| `record_id` | Immutable owner record identifier. It is not a digest, RunPlan slot ID, or output ID. |
| `receipt_role` | Closed enum `attempt_started \| attempt_terminal`. |
| `coverage_plan_sha256` | Exact lowercase SHA-256 digest of the Q28 coverage plan. |
| `work_unit_id` | Exact Q28 work-unit identity. |
| `attempt_ordinal` | Positive Q15 per-work-unit attempt ordinal; this is the Q28 D6 ordinal. |
| `work_unit_output_sha256` | Exact digest of the Q28 work-unit output envelope; `null` only for `attempt_started` with lifecycle `started` or `unclosed`, and required for `attempt_terminal`. |
| `lifecycle_status` | Closed enum `started \| complete \| failed \| invalid \| interrupted \| unclosed`, with the role combinations below. |
| `membership` | Closed Q15 run-membership enum `formal_required \| diagnostic`. |
| `logical_run_id` | Immutable identity of one logical Q15 run/repeat for this work unit; retries retain it and a new repeat receives a new value. |
| `execution_id` | Immutable identity of this concrete execution instance; a retry receives a new value. |
| `runner_binding` | Required object containing the outer runner identity fields below. It is lineage, not the Q28 attempt binding authority. |
| `history_id` | Stable owner history identity for `{coverage_plan_sha256, work_unit_id, logical_run_id}`; it does not contain an attempt or receipt digest. |
| `previous_receipt_sha256` | Nullable digest of the immediately preceding immutable receipt record in this history chain. It is `null` only for the first `attempt_started` record. |

`runner_binding` contains exactly:

```json
{
  "runner_plan_sha256": "<diagnostic-run-plan-sha256>",
  "runner_slot_id": "<runner-slot-id>",
  "runner_attempt_ordinal": 1,
  "runner_invocation_id": "<runner-invocation-id>"
}
```

`runner_plan_sha256` is the existing diagnostic RunPlan digest and is
intentionally distinct from `coverage_plan_sha256`. All four runner-binding
fields are required for the current Q17 runner realization. A future owner
contract may define a non-runner execution adapter only through a new
compatible owner revision; Q28 must not infer missing runner fields from a
RunPlan.

The exact lifecycle role combinations are:

| `receipt_role` | Allowed `lifecycle_status` | `work_unit_output_sha256` |
| --- | --- | --- |
| `attempt_started` | `started` or `unclosed` | `null` |
| `attempt_terminal` | `complete`, `failed`, `invalid`, or `interrupted` | Required and must resolve to the same plan/unit/attempt output envelope |

`unclosed` is an owner history state with no terminal outcome. It cannot be a
Q28 terminal binding. `interrupted` is an owner-defined terminal
reconciliation state only when Q17 has durably emitted this per-work-unit
receipt; it does not invent an existing runner terminal package or process exit
code. `complete` is the canonical owner spelling for a successful terminal
outcome; `success` is not an additional enum value. `truncated` is not an owner
lifecycle value: it remains the Q28 `output_condition` and any Q14 measurement
meaning remains outside this contract.

The receipt must also satisfy these direct-binding rules:

1. `coverage_plan_sha256`, `work_unit_id`, and `attempt_ordinal` are serialized
   owner fields, not values reconstructed from `runner_binding`.
2. A terminal receipt's `work_unit_output_sha256` resolves to exactly one
   `benchmark-generation-work-unit-output/1.0.0` artifact with the same
   `coverage_plan_sha256`, `work_unit_id`, and `attempt_ordinal`.
3. `record_id` is unique in the owner store and is immutable. The owner must
   reject a second payload under the same record ID unless it is the exact same
   canonical payload and external digest.
4. `history_id` is stable for one logical run/work-unit history. A new logical
   repeat receives a new `logical_run_id` and `history_id`; a retry does not.
5. `previous_receipt_sha256` resolves to an earlier receipt in the same plan,
   work unit, logical run, and history. A receipt never points forward and
   never points to a closure, output, collection, or higher-level result.

`history_id` is derived from this exact identity-only seed using the existing
canonical JSON rules:

```json
{
  "coverage_plan_sha256": "<plan-digest>",
  "work_unit_id": "<work-unit-id>",
  "logical_run_id": "<logical-run-id>"
}
```

The value is `work-unit-history-` followed by the lowercase SHA-256 hex
digest of those canonical seed bytes. Attempt ordinals, execution IDs,
receipt digests, output content, timestamps, cost, and hardware are not
history identity inputs.

The owner record ID is derived from this identity-only seed so repeated
materialization cannot allocate a different ID for the same lifecycle record:

```json
{
  "coverage_plan_sha256": "<plan-digest>",
  "work_unit_id": "<work-unit-id>",
  "logical_run_id": "<logical-run-id>",
  "attempt_ordinal": 1,
  "receipt_role": "attempt_terminal",
  "execution_id": "<execution-id>"
}
```

The seed uses the existing canonical JSON rules and the record ID is
`work-unit-receipt-` followed by the lowercase SHA-256 hex digest of those
canonical seed bytes. The seed contains no output content, provider response,
timestamp, cost, hardware, or process exit code.

#### R5 — attempt, retry, resume, and repeat identity relationship

The following relationship is frozen without selecting any retry or repeat
count:

| Identity | Owner and relationship |
| --- | --- |
| `runner_attempt_ordinal` | Q17/Q21 outer slot-attempt ordinal under `runner_binding`. It describes the runner slot history and is not a Q28 work-unit attempt ordinal. |
| `attempt_ordinal` | Q15 per-work-unit attempt ordinal. It starts at one within `{coverage_plan_sha256, work_unit_id, logical_run_id}` and increases for each persisted execution of that work unit in that logical run. It is the only ordinal that Q28 D6 binds. |
| Retry ordinal | No independent numeric retry policy is frozen. A retry is an owner-classified new `execution_id` and a new per-work-unit `attempt_ordinal` in the same `logical_run_id`/`history_id`; any Q15 retry label remains owner history metadata and cannot replace `attempt_ordinal`. |
| `logical_run_id` | One logical Q15 run/repeat identity. A retry/resume keeps it; a stochastic repeat receives a new one and starts its work-unit attempt ordinals at one. |
| `execution_id` | One concrete owner execution instance. It is new for a retry, while the logical run remains the same. |

Therefore `runner_attempt_ordinal == attempt_ordinal` is permitted for the
single-pass, one-unit diagnostic case but is not a contract-wide invariant. In
the first-run-fails/resume case, runner attempt two may produce a work-unit
attempt two; a multi-work-unit runner slot may contain several work-unit
receipts with the same runner ordinal and independently numbered work-unit
ordinals. Q28 must reject a binding where the serialized owner
`attempt_ordinal` does not equal the Q28 output/closure attempt ordinal.

The contract does not freeze provider retry count, backoff, timeout, stochastic
repeat count, scheduling cadence, or resource policy. Those policies remain
Q15/Q17/Q21-owned pending decisions.

#### R6 — lifecycle and terminal/history semantics

Q15 is the semantic owner of the lifecycle states; Q17 serializes them in the
receipt; Q21 preserves them in collection history:

- `started` means the owner has durably recorded the beginning of a concrete
  work-unit execution and no terminal outcome is available yet.
- `complete` means the owner has durably recorded a successful terminal
  execution and its output envelope digest.
- `failed` means the owner has durably recorded an execution failure. It is
  not a Q14 quality result and does not imply a truncation threshold.
- `invalid` means the owner contract, input, schema, or digest validation
  rejected the attempt. It is not a Q10 authority or Q12 quality state.
- `interrupted` means the owner has durably recorded an externally interrupted
  attempt through the owner reconciliation path. It does not invent a runner
  terminal package or exit code that was never emitted.
- `unclosed` means the history is still open and has no terminal owner record.

Q28 `coverage_condition` remains exactly `complete | missing | failed |
truncated | invalid`. It is a structural source-coverage condition and never
selects or renames the owner lifecycle status. Q28's
`terminal_attempt_ordinal` is only a pointer to an owner-selected terminal
attempt; Q15/Q17 decide whether an owner record is terminal and eligible. A
Q28 closure cannot use an `attempt_started`/`unclosed` reference as its
terminal receipt.

#### R7 — append-only receipt history and terminal selection

The per-work-unit history is an append-only chain of immutable owner receipt
records:

1. The first `attempt_started` record has `previous_receipt_sha256=null`.
2. A terminal record for that attempt points to the durable start-record
   digest. A later retry start points to the prior attempt's terminal-record
   digest.
3. Every subsequent owner record points to the immediately preceding record in
   the same `{coverage_plan_sha256, work_unit_id, logical_run_id, history_id}`
   chain. Parent identity and digest must validate before append.
4. A failed, invalid, truncated-output, interrupted, or unclosed attempt is
   never deleted, replaced, or relabeled by a later successful attempt.
5. Resume appends a new owner receipt and new output envelope. It never edits
   the old receipt, changes its digest, or reuses its record ID for a new
   attempt.
6. Q15 may select one exact terminal receipt for Q28's
   `terminal_attempt_ordinal`; that selection does not hide the other receipt
   references. Q21 collection materialization must retain the complete chain.
7. A retry does not increase logical run or repeat count. A repeat creates a
   new logical run identity and is not merged into the prior history.

The owner history is therefore reconstructible from immutable receipt digests
without a second authoritative Q28 assignment or history map. If a parent
receipt is missing or not durable, the history is incomplete and Q28 cannot
claim a closed closure.

#### R8 — content-addressed dependency DAG

The required artifact dependency is:

```text
CoveragePlan
  -> WorkUnitOutput
  -> Q17 WorkUnitAttemptReceipt
  -> Q28 CoverageClosure
  -> higher-level GenerationResult / terminal package
  -> Q21 Collection
```

The receipt's `previous_receipt_sha256` is a backward edge to an earlier
immutable receipt in the same owner history chain. The chain is acyclic.
Existing Q17 `StartReceipt` and `TerminalReceipt` remain parallel runner
history artifacts and are not the Q28 receipt edge. Q21 collection may
reference the complete owner chain and the higher-level package, but neither
collection nor a higher-level result is referenced by a receipt or output.

The current implementation state has no `GenerationResult ->
CoverageClosure` edge. This contract records the future compatible lineage
requirement but does not add that edge, change `GenerationResult`, or create a
cycle as part of this documentation-only round.

#### R9 — durability and closure gate

An owner receipt is referenceable only after all of the following have
completed in order:

1. The exact payload has passed owner schema validation and canonical
   serialization.
2. The canonical bytes have been written to the immutable owner store.
3. The external lowercase SHA-256 digest record has been written and resolves
   to those exact bytes.
4. A durable read/identity check confirms the record ID, schema version,
   digest, and core plan/work-unit/attempt bindings.

Q28 may build a candidate closure in memory, but it may set
`coverage_closure_state=closed` only after every referenced owner receipt,
every referenced output, and every required parent history receipt satisfies
this durability rule. Hashing a pending receipt, using a path without an
external digest record, or resolving a synthetic reduced record is
insufficient. If any required receipt is unavailable, the only valid result is
an explicit `not_closed` closure or a contract-dependency rejection; a fake
`receipt_ref` is forbidden.

#### R10 — canonical serialization and revision rules

The owner receipt uses the same canonical serialization family as Q28:

- UTF-8 without BOM;
- compact JSON with deterministic sorted object keys;
- no trailing newline, duplicate keys, NaN, Infinity, or non-integer numeric
  values;
- exact Unicode code points without implicit normalization; and
- external lowercase SHA-256 over the exact canonical bytes.

The payload excludes its own digest. The receipt, every parent receipt, the
Q28 output, the Q28 plan, the Q28 closure, and the Q21 collection each retain
separate immutable digests. A required-field, enum, lifecycle-role,
identity-binding, parent-link, canonicalization, or digest-verification
change requires a new major owner schema version. A compatible optional field
requires a minor version; documentation-only clarification requires a patch
version. Readers reject unknown versions and must not coerce the existing
runner receipt schemas into this schema.

#### Owner-receipt validation boundary for Q28-D6

Before accepting an `AttemptBinding` in a closure, Q28 must verify the
following exact cross-artifact facts:

1. `receipt_ref.schema_version` is
   `benchmark-generation-work-unit-attempt-receipt/1.0.0`, its
   `record_type` is `work_unit_attempt_receipt`, and its `record_id` resolves
   to the durable owner payload.
2. The owner payload is canonical and its external digest equals
   `receipt_ref.sha256`.
3. The owner payload has `receipt_role=attempt_terminal`, a permitted terminal
   lifecycle status, and non-null `work_unit_output_sha256`.
4. The owner payload's `coverage_plan_sha256`, `work_unit_id`, and
   `attempt_ordinal` equal the closure's plan, unit, and attempt binding
   directly.
5. The output digest in the owner payload equals the binding's
   `output_sha256`, and the output artifact independently validates the same
   plan/unit/attempt tuple.
6. The owner parent chain is durable, same-history, acyclic, and retains all
   prior attempts; Q28 does not replace it with a reduced receipt record.

Q28 validates identity, schema, digest, role, and direct binding only. It does
not infer terminal meaning beyond the owner-declared role, reinterpret retry
or repeat semantics, calculate quality, decide authority, or produce an
omission/contradiction judgment. The validation must reject the existing
top-level `runner-terminal-receipt/1.0.0`, a payload with omitted binding
fields, a mismatched runner ordinal used as a work-unit ordinal, a
non-durable reference, and any placeholder or synthetic owner record.

#### Compatibility and implementation boundary

- **Q17 existing runner receipts:**
  `runner-start-receipt/1.0.0` and `runner-terminal-receipt/1.0.0` remain
  unchanged. Their `plan_sha256` continues to mean the diagnostic RunPlan
  digest, and their `attempt_ordinal` continues to mean the outer slot
  attempt. They remain valid runner history but are never Q28
  `AttemptBinding.receipt_ref` values. The new owner receipt is an additive,
  separately versioned artifact, not a versioned extension of either existing
  schema.
- **Q21 topology:** Q21 retains slot membership, logical-run identity,
  retry/resume history, and collection reconstruction. It must preserve all
  per-work-unit receipt digests and their parent chain when materializing a
  collection. It does not own or rewrite the new receipt payload.
- **Q28 D6:** the new owner receipt directly supplies the three required
  bindings and the output digest. Q28 still owns no receipt schema and keeps
  its existing nullable terminal pointer and structural closure semantics.
- **Q29:** the receipt repeats the Q28 coverage-plan digest and remains
  downstream of the Q29 route/execution-contract bindings. It does not alter
  route mode, route decision, conformance, or execution-contract semantics.
- **Q14/Q11/Q10/Q12:** owner lifecycle and Q28 coverage conditions are not
  scores, quality states, gates, blockers, authority states, or adoption
  decisions.
- **Exit semantics:** missing owner receipt realization remains an explicit
  contract dependency or incomplete operational condition under the existing
  `0 | 1 | 2` runner semantics; it is never converted into a quality failure.

This contract is sufficient to implement the owner-controlled per-work-unit
receipt artifact, append-only receipt lineage, Q28 D6 direct binding, and
durability-gated structural closure. It is not sufficient to implement the
still-pending Q15 retry/repeat/scheduling policy or the broader Q21 collection
schema and statistics; those remain separate owner tasks.

#### R1–R10 decision register

| Item | Frozen decision |
| --- | --- |
| R1 | Split ownership: Q15 semantics/topology, Q17 receipt envelope/durability, Q21 collection materialization, Q28 typed validation only. |
| R2 | Option A: independent per-work-unit attempt receipts with an append-only Q15 parent chain; no wrapper and no Q28 receipt schema. |
| R3 | Exact owner schema `benchmark-generation-work-unit-attempt-receipt/1.0.0`, role `work_unit_attempt_receipt`. |
| R4 | Exact strict fields and direct plan/unit/attempt/output bindings as specified; runner binding is explicit lineage, not Q28 authority. |
| R5 | Runner-slot and work-unit ordinals are distinct; retries keep `logical_run_id` and advance per-unit `attempt_ordinal`; repeats receive a new logical run. |
| R6 | Q15 owns lifecycle meaning; Q17 serializes `started`, `complete`, `failed`, `invalid`, `interrupted`, and `unclosed` with closed role combinations; Q28 coverage conditions remain separate. |
| R7 | Receipt history is immutable and append-only through `previous_receipt_sha256`; failed/invalid/truncated/interrupted/unclosed history is never hidden; terminal selection points to an exact receipt. |
| R8 | The content-addressed DAG is plan → output → owner receipt → closure → higher-level package → collection; receipt parent links point only backward within the owner chain. |
| R9 | Canonicalization, immutable-store write, external digest record, and durable identity check precede a `closed` Q28 closure. |
| R10 | Q28 canonical JSON/SHA-256/self-digest/revision rules apply; incompatible owner changes require a major version and old receipts remain immutable. |

#### Remaining pending owner decisions

The following remain deliberately pending and are not encoded by this
contract:

- provider retry count, retry classification details beyond the immutable
  attempt relationship, backoff, timeout, scheduling cadence, and capacity or
  resource thresholds;
- stochastic repeat count, formal run-block design, pairing, and collection
  statistics;
- broader Q21 collection-manifest field/schema realization beyond preserving
  the receipt chain references;
- Q14 omission, duplication, truncation, ordering, contradiction, alignment,
  metric, scorer, aggregation, and measurement formulas;
- Q11 quality/gate constants and Q10/Q12 authority, blocker, and contradiction
  effects; and
- Q28 work-unit sizing, overlap amount, merge algorithm, and numeric
  truncation/contradiction boundaries.

Where a required owner policy is not yet available, the implementation must
remain `evidence_required` or owner-pending. It must not use an outer runner
ordinal as a guessed work-unit ordinal, hash a pending receipt, omit binding
fields, or grant Q28 structural closure through a placeholder record.

### 2.139 Q26/Q27 renderer and capture seam contract

This section freezes the missing renderer/capture boundary required by the
Q27 End-to-end lane. It realizes neither a renderer implementation nor a
quality, alignment, comparison, gate, provider, Notion, retry, or collection
policy. Q26 remains the owner of the note and rendered-projection schemas;
Q27 remains the owner of the two non-compensating End-to-end views.

#### Authority boundary and artifact topology

The Q26 `benchmark-note-document/1.0.0` artifact with
`artifact_role=pre_render_note` is the renderer-neutral Generation boundary.
It is the only input note artifact accepted by this seam. A renderer consumes
that artifact and produces an actual renderer output. The renderer output is a
separate immutable opaque payload artifact, addressed by its external
`renderer_output_sha256`; this contract does not invent a renderer-specific
payload schema or interpret its bytes as a Q26 note.

The benchmark capture of that output is a separate canonical JSON manifest:

`benchmark-renderer-capture/1.0.0`

Its only v1 role is `renderer_capture`. The manifest has exactly these fields:

```json
{
  "schema_version": "benchmark-renderer-capture/1.0.0",
  "artifact_role": "renderer_capture",
  "capture_id": "capture-<64-lowercase-hex>",
  "document_id": "<document-id>",
  "reference_document_sha256": "<reference-document-sha256>",
  "pre_render_note_sha256": "<q26-pre-render-note-sha256>",
  "renderer_output_sha256": "<immutable-renderer-output-sha256>",
  "producer_provenance": {
    "producer_role": "renderer",
    "producer_name": "<renderer-name>",
    "producer_version": "<renderer-version>",
    "configuration_sha256": "<configuration-sha256>",
    "processing_method": "<renderer-method>",
    "processing_stage": "rendered_projection_capture",
    "capture_method": "authoritative_output"
  }
}
```

`capture_method` is closed to `authoritative_output` and
`verified_readback`. `capture_id` is derived from the canonical identity seed
containing `schema_version`, `artifact_role`, `document_id`,
`reference_document_sha256`, `pre_render_note_sha256`,
`renderer_output_sha256`, and the complete `producer_provenance` object. It
does not contain a run ID, attempt ordinal, timestamp, cost, hardware, or
provider response. The manifest is strict: unknown fields, unknown roles,
unknown capture modes, missing bindings, or mismatched provenance are invalid.

The Q26 `benchmark-rendered-note-projection/1.0.0` remains unchanged. Its
`lineage.parent_artifact_role` remains `pre_render_note`, and its
`lineage.parent_artifact_sha256` remains exactly the external digest of the
pre-render note. It does not gain a `capture_sha256` field and it does not
change its parent role to `renderer_capture`. The Q27 End-to-end result/attempt
binding carries both `renderer_capture_sha256` and
`rendered_note_projection_sha256`; that cross-artifact binding is the
authoritative capture-to-projection relationship. Existing Q24 result-store
realization remains the owner of the formal result-package envelope.

The End-to-end binding must also expose the exact pre-render digest and the
existing Parser/Generation parent digests needed to distinguish the full lane
from Parser-reuse or Generation-only execution. It contains references only;
it does not add metric, score, quality, alignment, gate, authority, or
comparison fields. The existing runner attempt and terminal records reference
this immutable End-to-end result package through their unchanged
`result_sha256`. They do not directly receive renderer/capture fields and do
not become renderer receipts.

#### Capture-mode validity

| Mode | Valid only when | Invalid substitute |
| --- | --- | --- |
| `authoritative_output` | The renderer's authoritative output boundary returns the final output bytes/record that the benchmark captures, and the bytes are persisted and digest-verified. | A request, enqueue acknowledgement, callback intention, or status saying that rendering probably succeeded. |
| `verified_readback` | The renderer has completed its target write and an independent readback obtains the final output bytes/record; the readback bytes are persisted and digest-verified. | A successful write response without readback, a stale cache, or a target-side digest not independently verified. |

Both modes require Q26 renderer provenance with
`processing_stage=rendered_projection_capture`. `outgoing_request` is never a
valid mode. A direct copy of `pre_render_note`, reserialization of the note,
or identity pass-through is not a renderer capture. A real renderer may
produce byte-identical output, but the capture is valid only when an actual
renderer execution under the bound contract produced the output; this section
does not create an identity-renderer exception.

Canonical benchmark execution requires a deterministic offline renderer and
capture seam under the bound execution contract and the existing no-egress
boundary. The renderer may be a deterministic local implementation or another
approved offline renderer; this contract does not select a library or define
its rendering algorithm. Provider-backed, remote, or external rendering may
be retained as a separately labeled diagnostic artifact under its own Q15/Q19
execution and provenance contract, but it cannot satisfy the canonical offline
End-to-end binding or be silently substituted for it.

#### Parent, digest, and lineage coherence

For one valid End-to-end binding, all of the following must hold directly:

1. The pre-render note is a durable, Q26-valid artifact.
2. `renderer_capture.document_id` and
   `renderer_capture.reference_document_sha256` equal the pre-render note's
   corresponding bindings.
3. `renderer_capture.pre_render_note_sha256` equals the external digest of
   that exact pre-render note.
4. `rendered_note_projection` is Q26-valid and its
   `lineage.parent_artifact_sha256` equals the same pre-render-note digest.
5. Projection `document_id`, reference digest, renderer provenance, and
   capture mode equal the capture manifest's corresponding values.
6. `renderer_capture.renderer_output_sha256` resolves to the immutable output
   bytes/record from which the projection was materialized.
7. The End-to-end result/attempt binds the capture and projection digests
   together under the same pre-render, reference, document, and execution
   identity; no field is inferred from a runner slot.

Q26 owns `lineage`, `mapping_state`, and the closed mapping shapes in the
projection. `mapping_state=provided` is legal only when the actual renderer
or capture seam supplies explicit source/target node mappings and the Q26
projection contains valid non-empty mapping records. `mapping_state=unavailable`
is legal when the renderer output/readback is valid and durable but the seam
cannot provide mappings; the projection mappings must then be empty. It is a
structural availability state, not a quality or preservation judgment.
`mapping_state=not_applicable` remains legal only on `pre_render_note`, never
on a rendered projection. Q14 owns all future alignment, comparison,
measurement, and scoring meaning of a provided mapping.

#### Immutable ordering and fail-closed rules

The durability sequence is fixed:

1. Canonicalize and durably store the Q26 pre-render note and create/verify
   its external SHA-256 record.
2. Execute the bound real renderer/capture method.
3. Durably store the renderer output/readback bytes or record, create its
   external SHA-256 record, and verify durable identity.
4. Canonicalize and durably store the renderer-capture manifest, then create
   and verify its external SHA-256 record.
5. Materialize, validate, durably store, and digest the Q26 rendered
   projection from the captured output and the exact pre-render parent.
6. Materialize and durably store the End-to-end result/attempt binding with
   all parent digests; only after that may the existing runner attempt/terminal
   package reference the result digest.

The renderer capture manifest and Q26 projection use UTF-8, compact JSON,
deterministic sorted object keys, contract-defined array order, no trailing
newline, and an external SHA-256 over bytes that do not contain their own
digest. Q24 result/attempt artifacts use the existing runner-family newline
contract specified in section 2.140. A digest of pending or merely requested
output is not a durable identity. The capture manifest and projection are
immutable; any changed output, provenance, mapping, parent, or capture mode
creates a new artifact.

The seam fails closed as follows:

- missing renderer output, failed render, unavailable readback, failed
  durable write, or missing external digest record produces no successful
  projection or End-to-end result; it remains an operational/incomplete
  outcome under existing runner exit semantics;
- outgoing-request-only capture, identity-pass-through, malformed capture or
  projection, missing parent, wrong reference/document/output digest,
  mismatched capture/projection provenance, or invalid lineage is a contract
  rejection; it is not a quality failure;
- a non-durable or mismatched renderer output/capture/projection cannot be
  referenced by a successful End-to-end result or runner terminal; and
- no placeholder, synthetic capture, fabricated readback, or direct
  pre-render-to-projection shortcut may grant End-to-end success.

#### Digest DAG and ownership audit

The frozen dependency direction is:

```text
raw source
  -> Parser artifacts / NormalizedDocument
  -> Generation artifacts
  -> Q26 pre_render_note
       -> immutable renderer output bytes/record
       -> benchmark-renderer-capture/1.0.0
       -> Q26 rendered_note_projection
Parser + Generation + pre_render_note + renderer_capture + projection
  -> End-to-end result/attempt binding
  -> existing runner attempt/terminal result_sha256
  -> Q21 collection materialization
```

The projection retains its frozen direct parent to `pre_render_note`; the
capture-to-projection relationship is the End-to-end cross-binding described
above. Neither the projection nor renderer output points back to the result,
attempt, runner receipt, or collection. The capture manifest does not point to
the projection. The End-to-end result points only downstream to its parents.
The graph is therefore acyclic; no digest cycle is introduced.

Q26 owns the projection schema, renderer provenance fields, capture-mode enum,
lineage, and mapping representation. Q27 owns the End-to-end lane identity,
the two non-compensating future views, and the lane binding. Q17 keeps
`runner-start-receipt/1.0.0`, `runner-terminal-receipt/1.0.0`, and existing
runner attempt semantics unchanged; Q21 preserves the resulting immutable
references in collection/history materialization. Q14, Q11, Q12, Q13, Q15,
Q19, Q24, Q28, and Q29 retain their existing measurement, gate, authority,
comparison, retry, provenance, result-store, planning, and routing ownership.

This seam is sufficient for a later D12 renderer/projection implementation
once the renderer adapter is implemented against section 2.140. It does not
by itself authorize a provider, Notion write, metric, or formal adoption
result.

### 2.140 Deterministic offline renderer and Q24 End-to-end result realization

This section resolves the two implementation dependencies left by section
2.139. It freezes a benchmark-only renderer contract and the minimum Q24
End-to-end result/attempt package. It does not implement either runtime, add a
renderer dependency, alter Q26 projection parentage, or define any Q14/Q11/
Q12/Q13/Q15/Q21/Q28 semantics.

#### Repository evidence and renderer selection

The repository has no contract-valid renderer/capture materializer. The
Generation lane's `deterministic_reference_projection` is a Generator
producer, the Q26 rendered-projection builders are test helpers, and the W03
HTML is an offline source fixture rather than a renderer. No existing code
consumes a Q26 `pre_render_note` and emits a durable rendered-output artifact.

The selected smallest defensible seam is therefore a pure standard-library
renderer:

| Field | Frozen value |
| --- | --- |
| renderer identity | `benchmark-deterministic-html-renderer` |
| renderer version | `1.0.0` |
| processing method | `q26_note_to_canonical_html` |
| processing stage | `rendered_projection_capture` |
| canonical capture method | `authoritative_output` |
| dependencies | Python standard library only; no new package, network, provider, browser, or Notion client |

This is a real transformation: it converts the Q26 JSON note model into a
new HTML byte representation with an HTML document wrapper, typed element
tags, escaped text, deterministic attributes, and explicit citation markers.
Copying or reserializing the Q26 JSON is not an implementation of this
renderer.

#### Exact renderer configuration

The renderer configuration projection is the canonical payload for
`benchmark-html-renderer-configuration/1.0.0`:

```json
{
  "schema_version": "benchmark-html-renderer-configuration/1.0.0",
  "renderer_id": "benchmark-deterministic-html-renderer",
  "renderer_version": "1.0.0",
  "document_wrapper": "html5-head-body-article",
  "charset": "utf-8",
  "line_endings": "lf",
  "trailing_newline": false,
  "whitespace": "compact",
  "external_resources": "forbidden",
  "scripts": "forbidden",
  "styles": "forbidden",
  "attribute_escape": "html5-fixed-v1",
  "node_tag_policy": "closed-q26-kind-map-v1",
  "citation_policy": "empty-span-markers-v1",
  "mapping_policy": "data-node-id-one-to-one-v1",
  "unsupported_node_policy": "typed-div"
}
```

The external SHA-256 of the canonical configuration bytes is the
`producer_provenance.configuration_sha256` in both the renderer capture
manifest and Q26 rendered projection. The configuration payload itself has
no self-digest. Its object keys use the existing canonical JSON rules; it has
no arrays whose order is implementation-defined.

#### Exact HTML output byte contract

The renderer accepts only a Q26-valid `benchmark-note-document/1.0.0` with
`artifact_role=pre_render_note`. It emits UTF-8 bytes with no BOM, no
trailing newline, LF line-ending normalization inside text content, no
insignificant whitespace, and no external references. The output has this
exact compact structure, with values HTML-escaped according to
`html5-fixed-v1`:

```html
<!doctype html><html><head><meta charset="utf-8"></head><body><article data-document-id="..." data-reference-document-sha256="..."><h2 data-node-id="..." data-node-kind="heading" data-order="0" data-q26-meta="...">escaped text<span data-citation-id="..." data-reference-document-id="..." data-element-id="..." data-mode="whole_element" data-locator-indexes="0"></span></h2></article></body></html>
```

The root element and attributes are emitted exactly in the shown order.
Every node is a sibling in Q26 `nodes` order; `parent_node_id` is retained in
`data-q26-meta`, so the flat HTML stream never invents a hierarchy. Each node
element has, in order, `data-node-id`, `data-node-kind`, `data-order`, and
`data-q26-meta`; it additionally has `data-parent-node-id` only when the Q26
parent is non-null. `data-q26-meta` is compact canonical JSON containing
exactly `parent_node_id`, `languages`, `list_metadata`,
`table_cell_metadata`, `code_metadata`, and `citations`, with null/empty
values retained according to the Q26 model. The node's `content` is emitted
as escaped text after the attributes.

The closed Q26-kind-to-tag map is:

| Q26 node kind | HTML tag |
| --- | --- |
| `heading` | `h2` |
| `paragraph`, `transcript_segment`, `message` | `p` |
| `list_item`, `table_row`, `table_cell`, `formula` | `div` |
| `quote` | `blockquote` |
| `code_block` | `pre` |
| `table` | `section` |
| `figure` | `figure` |
| `caption` | `figcaption` |

`table`, `table_row`, and any other null-content node emit no text. Each
citation appends one empty `span` after the node content, in Q26 citation
order, with attributes `data-citation-id`,
`data-reference-document-id`, `data-element-id`, `data-mode`, and
`data-locator-indexes`, in that order. Locator indexes are decimal integers
joined by commas. Text escaping replaces `&`, `<`, and `>`; attribute
escaping additionally replaces `"` with `&quot;` and `'` with `&#x27;`.
Unicode code points are otherwise preserved without normalization.

The authoritative renderer return value is these exact output bytes. The
adapter then parses its own returned bytes with a deterministic standard
library HTML parser, verifies the root, node order, node IDs, metadata,
content, citation markers, and reference digest, and materializes the Q26
`rendered_note_projection` from that parsed output. It never materializes the
projection by copying the pre-render model. For a non-empty pre-render note,
the parser emits explicit one-to-one node mappings from each input `node_id`
to the corresponding output `data-node-id`, so the projection uses
`mapping_state=provided` with one Q26-valid mapping record for every
input/output node pair. A valid empty pre-render note that is successfully
rendered and parsed may instead produce `mapping_state=unavailable` with
`mappings=[]` solely because there are no source or target nodes to map. This
is an empty-note exception only; it must not generalize `unavailable` to a
non-empty deterministic HTML projection, which must continue to use provided
one-to-one mappings. The empty projection must still be materialized from the
real HTML output and must not use an identity/direct-copy shortcut. Any
parse, round-trip, node, citation, or metadata mismatch fails closed.

#### Q24 End-to-end result/attempt schemas

The exact Q24 lane artifacts are:

- `benchmark-end-to-end-result/1.0.0`, artifact type
  `parser_note_completeness_end_to_end_result`;
- `benchmark-end-to-end-attempt/1.0.0`, artifact type
  `parser_note_completeness_end_to_end_attempt`.

Both schemas are strict, immutable, and use `operation=execute_end_to_end`
and `status=contract_valid` as their only v1 values. They are lineage and
execution packages, not metric, quality, gate, authority, comparison, or
scoring results.

The exact shared result fields are:

```json
{
  "schema_version": "benchmark-end-to-end-result/1.0.0",
  "runner_version": "parser-note-completeness-runner/1.0.0",
  "artifact_type": "parser_note_completeness_end_to_end_result",
  "operation": "execute_end_to_end",
  "case_id": "<case-id>",
  "raw_source_sha256": "<raw-source-sha256>",
  "parser_result_sha256": "<parser-result-artifact-sha256>",
  "parser_attempt_sha256": "<parser-attempt-artifact-sha256>",
  "parser_output_sha256": "<normalized-document-sha256>",
  "generation_result_sha256": "<generation-result-artifact-sha256>",
  "generation_attempt_sha256": "<generation-attempt-artifact-sha256>",
  "generation_output_sha256": "<pre-render-note-sha256>",
  "pre_render_note_sha256": "<pre-render-note-sha256>",
  "renderer_output_sha256": "<renderer-output-sha256>",
  "renderer_capture_sha256": "<renderer-capture-manifest-sha256>",
  "rendered_note_projection_sha256": "<rendered-projection-sha256>",
  "execution_contract_sha256": "<execution-contract-sha256>",
  "execution_identity": {
    "runner_plan_sha256": "<diagnostic-run-plan-sha256>",
    "runner_slot_id": "<slot-id>",
    "runner_attempt_ordinal": 1,
    "runner_invocation_id": "<invocation-id>",
    "logical_run_id": "<q15-logical-run-id>",
    "membership": "diagnostic"
  },
  "attempt_id": "<end-to-end-attempt-id>",
  "status": "contract_valid"
}
```

The result schema uses its own literal `schema_version` and `artifact_type`
values. The attempt schema has the same fields and values except that
`schema_version` and `artifact_type` are the attempt identifiers and it adds
exactly one field:

```json
"result_sha256": "<end-to-end-result-sha256>"
```

The attempt's `result_sha256` must equal the external SHA-256 of the durable
canonical result bytes. `execution_identity.runner_attempt_ordinal` is the
outer runner slot ordinal. It is never treated as Q15's per-work-unit
`attempt_ordinal`; the latter remains in the owner-controlled work-unit
receipt and is not copied or inferred here. `logical_run_id` is copied from
the owner execution binding and does not define repeat, retry, or scheduling
semantics. Every `*_sha256` field is a lowercase 64-hex digest; runner and
logical IDs use the existing identifier pattern; `runner_attempt_ordinal` is a
positive integer; and `execution_identity.membership` is exactly
`diagnostic` in this v1 diagnostic contract.

#### Direct validation rules and responsibility split

The Q24 validator must directly resolve and validate every referenced digest:

1. `raw_source_sha256` must equal the source digest bound by the Parser
   result; Parser result and attempt must be the exact frozen schemas.
2. `parser_result_sha256` and `parser_attempt_sha256` must resolve to the
   same case, source, candidate, and immutable result/attempt relationship;
   `parser_output_sha256` must equal the Parser result's candidate/output
   digest and the canonical `NormalizedDocument` bytes. Q24 does not infer a
   shared runner identity from Parser fields that do not carry one.
3. `generation_result_sha256` and `generation_attempt_sha256` must resolve to
   the same case, reference/output identity, and execution-contract binding;
   `generation_output_sha256` and `pre_render_note_sha256` must equal the
   Generation candidate and the durable Q26 pre-render note digest. Q24 does
   not reinterpret Generation attempt IDs as E2E runner identity.
4. `renderer_output_sha256` must equal the durable opaque HTML bytes addressed
   by the renderer capture; the capture manifest must bind the same
   pre-render, document, reference, renderer provenance, and configuration.
5. `rendered_note_projection_sha256` must resolve to a Q26-valid projection
   whose parent role is `pre_render_note` and whose parent digest is exactly
   `pre_render_note_sha256`; its renderer provenance and capture mode must
   equal the capture manifest.
6. `execution_contract_sha256` and every field of `execution_identity` must
   equal the existing route/execution and runner evidence. No RunPlan slot
   parsing may be used to infer a missing Q26 or renderer binding.
7. The result must contain no unknown fields, self-digest, metric, score,
   quality, gate, authority, alignment, comparison, retry, repeat, or
   collection-semantic field.

Q24 owns these two immutable lane package schemas, their canonical bytes,
external digest records, and storage placement. Q27 owns their End-to-end lane
meaning and future two-view consumers. Parser, Generation, Q26, Q17, and Q21
remain owners of their referenced artifacts and semantics; Q24 validates
cross-artifact identity but does not rewrite them.

#### Storage, durability, resume, and runner reference

For the current offline diagnostic foundation, Q24 materializes the package
under the existing ignored local run root, without adding a fixture-tree
`receipts/` directory:

```text
local_storage/benchmarks/parser_note_completeness/v1/
  runs/<run-revision>/end_to_end/<case-id>/<runner-slot-id>/
    attempt-<runner-attempt-ordinal>/
      renderer-output.html
      renderer-output.sha256
      renderer-capture.json
      renderer-capture.sha256
      rendered-note-projection.json
      rendered-note-projection.sha256
      result.json
      result.sha256
      attempt.json
      attempt.sha256
```

Parser and Generation artifacts remain in their existing lane-owned
locations; this package stores only their digest references. The path is a
lookup location, never identity. Formal manifests may export the same
immutable bytes to an approved Q24 store without changing their digests and
must not treat a local path as formal authority.

The required write order is: all Parser/Generation/Q26 parent artifacts
durable; renderer output and external digest durable/readable; capture
manifest durable/readable; rendered projection durable/readable; End-to-end
`result.json` and its external digest durable/readable; End-to-end
`attempt.json` and its external digest durable/readable; then existing runner
attempt/terminal materialization. The existing runner terminal's unchanged
`result_sha256` points only to the End-to-end result digest. Existing runner
start/terminal fields are not extended.

Q24 result and attempt bytes use the existing runner-artifact canonical JSON
contract: UTF-8 without BOM, compact JSON, sorted object keys, deterministic
escaping, no NaN/Infinity, exactly one trailing LF, and external SHA-256 over
the exact bytes without a self-digest. The HTML output and Q26 note/projection
artifacts retain their own frozen byte contracts.

Resume never overwrites a result, attempt, renderer output, capture, or
projection. A later successful runner attempt creates a new immutable attempt
directory, new End-to-end result/attempt digests, and a new terminal reference;
previous failed, invalid, interrupted, or incomplete runner/owner history
remains visible. Q15 decides retry/repeat meaning; Q24 only preserves the
lineage. A failed or incomplete End-to-end execution produces no placeholder
Q24 result/attempt package and cannot receive a successful runner
`result_sha256`.

#### Final DAG and readiness

The resulting content-addressed DAG is:

```text
raw source
  -> Parser result/attempt + NormalizedDocument
  -> Generation result/attempt + pre_render_note
  -> deterministic HTML renderer output
  -> benchmark-renderer-capture/1.0.0
  -> rendered_note_projection
  -> benchmark-end-to-end-result/1.0.0
  -> benchmark-end-to-end-attempt/1.0.0
  -> existing runner attempt/terminal
  -> Q21 collection
```

Every arrow points from a parent to a downstream artifact. Renderer output
does not reference the result; the projection references only its frozen
pre-render parent; result and attempt reference parents but no parent
references either of them. The graph has no digest cycle.

The deterministic renderer and Q24 result/attempt contracts are now frozen
for D12 runtime implementation. Runtime work remains pending only for the
implementation of this adapter/materializer and the existing owner-governed
runner integration; no unresolved renderer or Q24 result-package schema gap
remains.

### 2.141 Q14 exact scoring artifact and schema realization

This section realizes the minimum Q14-owned artifact set required for a
deterministic scorer. It implements no scorer runtime and does not select
metric-specific parser formulas, measurement boundaries, Q11 constants, Q12
blockers, Q13 comparison policy, Q15 repeated-run semantics, or a renderer
lane. The v1 formal result payloads realized here are the frozen coverage
state vector and support exact-count representations. A parser metric may not
publish a formal result until its metric-specific unit, formula, applicability,
and evidence slots are separately frozen under Q14.

#### Schema family and strict common rules

The exact Q14-owned schema identifiers are:

| Artifact | `schema_version` | `artifact_role` |
| --- | --- | --- |
| Metric contract | `benchmark-q14-metric-contract/1.0.0` | `metric_contract` |
| Metric registry manifest | `benchmark-q14-metric-registry/1.0.0` | `metric_registry` |
| Scorer contract | `benchmark-q14-scorer-contract/1.0.0` | `scorer_contract` |
| Aggregation contract | `benchmark-q14-aggregation-contract/1.0.0` | `aggregation_contract` |
| Fixture metric result | `benchmark-q14-fixture-metric-result/1.0.0` | `fixture_metric_result` |
| Cohort metric result | `benchmark-q14-cohort-metric-result/1.0.0` | `cohort_metric_result` |

All six schemas are strict: unknown fields, unknown enum values, missing
required fields, duplicate IDs, mismatched references, and invalid
cross-artifact digests fail validation. Every artifact is immutable,
versioned, content-addressed, and stored with an external lowercase SHA-256
record. The canonical payload never contains its own digest. Q14 adds no
scorecard, authority, gate, blocker, comparison, receipt, or collection
schema; existing owner layers bind those records by reference.

The shared reference shapes are:

```json
{
  "metric_contract_ref": {
    "metric_contract_id": "<stable-id>",
    "metric_contract_version": "<contract-version>",
    "sha256": "<64-lowercase-hex>"
  },
  "metric_registry_ref": {
    "registry_id": "<stable-id>",
    "registry_revision": "<revision>",
    "sha256": "<64-lowercase-hex>"
  },
  "scorer_contract_ref": {
    "scorer_contract_id": "<stable-id>",
    "scorer_contract_version": "<contract-version>",
    "sha256": "<64-lowercase-hex>"
  },
  "aggregation_contract_ref": {
    "aggregation_contract_id": "<stable-id>",
    "aggregation_contract_version": "<contract-version>",
    "sha256": "<64-lowercase-hex>"
  }
}
```

An owner-controlled applicability or exclusion record uses the existing
opaque reference boundary and is not redefined by Q14:

```json
{
  "schema_version": "<owner-schema-version>",
  "record_type": "<owner-record-type>",
  "record_id": "<owner-record-id>",
  "sha256": "<64-lowercase-hex>"
}
```

Q14 validates identity and digest resolution for such a reference. It does
not infer, reclassify, or replace Q10/Q12 applicability, exclusions, blocker
states, or authority.

#### Metric contract

`benchmark-q14-metric-contract/1.0.0` has exactly these top-level fields:

```json
{
  "schema_version": "benchmark-q14-metric-contract/1.0.0",
  "artifact_role": "metric_contract",
  "metric_contract_id": "<stable-id>",
  "metric_contract_version": "<contract-version>",
  "metric_kind": "coverage | support",
  "lane": "generation | end_to_end",
  "scoring_unit": "expected_claim | generated_claim",
  "denominator_semantics": "authority_closed_applicable_units | q8_decided_support_units",
  "applicability_consumption": "q12_authoritative_disposition | q8_decided_state_disposition",
  "formula": {
    "formula_id": "<stable-formula-id>",
    "formula_revision": "<formula-revision>",
    "formula_kind": "coverage_state_vector_v1 | support_state_counts_v1"
  },
  "components": [
    {
      "component_id": "<closed-by-formula-kind>",
      "direction": "higher_is_better | lower_is_better | non_directional",
      "canonical_unit": "count | rate",
      "numeric_representation": "integer | exact_rational | canonical_decimal"
    }
  ],
  "required_input_roles": ["<closed-input-artifact-role>"],
  "aggregation_contract_ref": {
    "aggregation_contract_id": "<stable-id>",
    "aggregation_contract_version": "<contract-version>",
    "sha256": "<64-lowercase-hex>"
  }
}
```

`metric_kind=coverage` requires `lane=generation | end_to_end` and
`scoring_unit=expected_claim`,
`denominator_semantics=authority_closed_applicable_units`,
`applicability_consumption=q12_authoritative_disposition`,
`formula_kind=coverage_state_vector_v1`, and exactly the components
`fully_covered`, `partially_covered`, and `not_covered` in that order.
`metric_kind=support` requires `lane=generation | end_to_end` and
`scoring_unit=generated_claim`,
`denominator_semantics=q8_decided_support_units`,
`applicability_consumption=q8_decided_state_disposition`,
`formula_kind=support_state_counts_v1`, and exactly the five decided Q8
components `supported`, `partially_supported`, `unsupported`,
`contradicted_by_source`, and `overstated` in that order. The support
`unresolved` state is represented only in the result audit payload and is not
a decided-state numerator. No component list may contain a combined scalar.

The realized 1.0.0 scoring-unit enum and formula kinds are only the
Generation/End-to-end values above: `expected_claim` with
`coverage_state_vector_v1` and `generated_claim` with
`support_state_counts_v1`. Parser source-side units remain outside the
executable 1.0.0 contract. A parser metric contract is not executable until
its metric-specific formula and evidence requirements are frozen. The
When parser metric formulas are frozen, adding a parser `metric_kind`, formula
kind, component set, or parser-result semantics requires an explicit versioned
Q14 schema revision; parser semantics must not be silently overloaded onto
coverage or support. `canonical_decimal` is permitted by the common schema only
for a
future metric with a genuinely decimal authoritative unit; the v1 coverage
and support contracts use integer or exact rational values.

`lane=parser` is invalid for every realized 1.0.0 metric contract, scorer
compatibility declaration, fixture metric-result, and cohort metric-result.
Future Parser scoring requires an explicit versioned Q14 schema revision; no
Parser metric kind or formula is introduced here.

#### Metric registry manifest

`benchmark-q14-metric-registry/1.0.0` has exactly:

```json
{
  "schema_version": "benchmark-q14-metric-registry/1.0.0",
  "artifact_role": "metric_registry",
  "registry_id": "<stable-id>",
  "registry_revision": "<revision>",
  "benchmark_revision": "<benchmark-revision>",
  "metric_contracts": [
    {
      "metric_contract_id": "<stable-id>",
      "metric_contract_version": "<contract-version>",
      "sha256": "<64-lowercase-hex>"
    }
  ]
}
```

The registry selects exact metric-contract IDs, versions, and digests. Its
entries are ordered by `metric_contract_id`, then
`metric_contract_version`; it contains no formula, denominator, direction,
applicability, scorer, gate, or aggregation semantics. A registry revision
with a changed entry is a new immutable registry artifact.

#### Scorer contract

`benchmark-q14-scorer-contract/1.0.0` has exactly:

```json
{
  "schema_version": "benchmark-q14-scorer-contract/1.0.0",
  "artifact_role": "scorer_contract",
  "scorer_contract_id": "<stable-id>",
  "scorer_contract_version": "<contract-version>",
  "implementation_id": "<stable-id>",
  "implementation_version": "<implementation-version>",
  "implementation_sha256": "<64-lowercase-hex>",
  "configuration_sha256": "<64-lowercase-hex>",
  "supported_metric_contracts": [
    {
      "metric_contract_id": "<stable-id>",
      "metric_contract_version": "<contract-version>",
      "sha256": "<64-lowercase-hex>"
    }
  ],
  "compatible_lanes": ["generation | end_to_end"],
  "deterministic_requirements": {
    "execution_mode": "offline_deterministic",
    "network_egress": "forbidden",
    "randomness": "forbidden",
    "binary_float_authority": "forbidden",
    "input_order": "metric_contract_defined",
    "serialization": "benchmark_canonical_json"
  },
  "fixture_result_schema_version": "benchmark-q14-fixture-metric-result/1.0.0"
}
```

The scorer contract owns implementation identity, supported metric-contract
compatibility, and deterministic execution requirements only. It cannot
override a metric contract's formula, denominator, state, direction, unit,
applicability, or aggregation eligibility. Supported-contract entries are
ordered by metric ID and version. The scorer must reject a contract digest
that differs from the supported entry even when its ID and version match.

#### Aggregation contract and v1 cohort realization

`benchmark-q14-aggregation-contract/1.0.0` has exactly:

```json
{
  "schema_version": "benchmark-q14-aggregation-contract/1.0.0",
  "artifact_role": "aggregation_contract",
  "aggregation_contract_id": "<stable-id>",
  "aggregation_contract_version": "<contract-version>",
  "input_metric_result_schema_version": "benchmark-q14-fixture-metric-result/1.0.0",
  "aggregation_kind": "fixture_vector_only",
  "formal_output": "ordered_fixture_vector"
}
```

This is the only realized v1 aggregation kind. It makes the ordered fixture
vector authoritative and emits no universal macro, weighted or unweighted
overall completeness scalar, formal micro rate, pooled denominator, or
cross-stratum aggregate. Micro/pooled totals may exist only in a separately
labeled diagnostic or audit artifact under its owning policy; they are not
fields of the Q14 formal cohort result. An evidence-approved macro or other
formal aggregation requires a new immutable aggregation contract and the
evidence required by section 2.105; it is not selected here.

#### Fixture metric-result artifact

`benchmark-q14-fixture-metric-result/1.0.0` has exactly:

```json
{
  "schema_version": "benchmark-q14-fixture-metric-result/1.0.0",
  "artifact_role": "fixture_metric_result",
  "result_id": "<derived-stable-id>",
  "benchmark_revision": "<benchmark-revision>",
  "fixture_id": "<fixture-id>",
  "fixture_revision": "<fixture-revision>",
  "lane": "generation | end_to_end",
  "metric_contract_ref": {"metric_contract_id": "<id>", "metric_contract_version": "<version>", "sha256": "<digest>"},
  "metric_registry_ref": {"registry_id": "<id>", "registry_revision": "<revision>", "sha256": "<digest>"},
  "scorer_contract_ref": {"scorer_contract_id": "<id>", "scorer_contract_version": "<version>", "sha256": "<digest>"},
  "formula_ref": {
    "formula_id": "<stable-formula-id>",
    "formula_revision": "<formula-revision>"
  },
  "input_artifacts": [
    {
      "artifact_role": "<closed-input-artifact-role>",
      "sha256": "<64-lowercase-hex>"
    }
  ],
  "applicability_ref": {
    "schema_version": "<owner-schema-version>",
    "record_type": "<owner-record-type>",
    "record_id": "<owner-record-id>",
    "sha256": "<64-lowercase-hex>"
  },
  "exclusion_ref": null,
  "metric_value": {}
}
```

`input_artifact_role` is closed to `raw_source`, `normalized_document`,
`reference_document`, `candidate_output`, `pre_render_note`,
`rendered_note_projection`, `gold`, `item_disposition`, `mapping`,
`projection`, and `alignment`. The array contains each role at most once and
is ordered by this declared role order. The metric contract's
`required_input_roles` must match the result's roles exactly. Thus item,
mapping, projection, and alignment dependencies are direct digest bindings,
not deductions from a RunPlan slot or another artifact. `applicability_ref` is
required; `exclusion_ref` is null only when the authoritative disposition
contains no exclusion record. For a support fixture metric-result,
`exclusion_ref` is always `null`, and the support payload has no excluded-claim
field or candidate-side exclusion mechanism. Coverage may consume a Q12-owned
exclusion reference under its own expected-claim contract. Q14 does not
inspect owner semantics beyond validating the external record identity and
digest.

`metric_value` is a discriminated strict union. For
`result_kind=coverage_state_vector`, it has exactly:

```json
{
  "result_kind": "coverage_state_vector",
  "strata": [
    {
      "stratum": "critical | major | minor",
      "authoritative_expected_claim_ids": ["<claim-id>"],
      "applicable_expected_claim_ids": ["<claim-id>"],
      "excluded_expected_claim_ids": ["<claim-id>"],
      "denominator_count": 0,
      "fully_covered": {"count": 0, "expected_claim_ids": []},
      "partially_covered": {"count": 0, "expected_claim_ids": []},
      "not_covered": {"count": 0, "expected_claim_ids": []},
      "fully_covered_rate": null,
      "partially_covered_rate": null,
      "not_covered_rate": null
    }
  ]
}
```

`strata` contains exactly one entry for each of `critical`, `major`, and
`minor`, in that order. The three state ID sets are disjoint, preserve
authoritative claim order, and exactly partition the applicable claim IDs.
Their counts sum to `denominator_count`. Each defined rate is the exact
lowest-terms rational `{ "numerator": <nonnegative-integer>,
"denominator": <positive-integer> }`, with numerator equal to the state
count and denominator equal to `denominator_count`; a zero-denominator rate
is `null` and is not a formal rate. There is no overall stratum or combined
coverage scalar.

This is the only Q14 v1 realization of section 2.103 importance-stratum
vectors: `critical`, `major`, and `minor` apply to expected-claim coverage
only. They are not support dimensions and do not create an importance field
or denominator copy for generated claims.

For `result_kind=support_state_counts`, `metric_value` has exactly:

```json
{
  "result_kind": "support_state_counts",
  "authoritative_generated_claim_ids": ["<claim-id>"],
  "applicable_generated_claim_ids": ["<claim-id>"],
  "decided_denominator_count": 0,
  "decided_state_counts": {
    "supported": {"count": 0, "generated_claim_ids": []},
    "partially_supported": {"count": 0, "generated_claim_ids": []},
    "unsupported": {"count": 0, "generated_claim_ids": []},
    "contradicted_by_source": {"count": 0, "generated_claim_ids": []},
    "overstated": {"count": 0, "generated_claim_ids": []}
  },
  "unresolved_audit": {"count": 0, "generated_claim_ids": []},
  "candidate_internal_contradiction": {
    "count": 0,
    "relation_ids": []
  },
  "diagnostic_rates": []
}
```

Support has one fixture-level generated-claim vector and has no importance
stratum field. Importance exists only on expected claims and is consumed by
the coverage vector above. Q14 must not derive generated-claim importance from
linked expected claims or duplicate a generated claim across strata. Every
support state ID, every unresolved audit ID, and every applicable ID is a
`generated_claim_id`; an `expected_claim_id` is invalid in any support
payload. `authoritative_generated_claim_ids` and
`applicable_generated_claim_ids` are exactly equal. Decided state IDs are
disjoint and preserve authoritative generated-claim order.
`decided_denominator_count` equals the union count of the five decided state
ID sets and excludes `unresolved_audit`. The five decided states plus
`unresolved_audit` partition the complete authoritative generated-claim set;
`unresolved_audit` is not a decided-state numerator. Each optional
`diagnostic_rates` entry has exactly `state` and `rate`, uses only the five
decided states in Q8 order, uses `decided_denominator_count` as its
denominator, and is explicitly diagnostic-only. It cannot
become a gate, ranking, comparison, quality, or authority input. The
`candidate_internal_contradiction` relation IDs are separate from all Q8
support-state counts and do not change their denominator.

The fixture-result validator treats `metric_kind` and `scoring_unit` as a
discriminant. Coverage results require `scoring_unit=expected_claim` and
validate `authoritative_expected_claim_ids`, applicable expected-claim IDs,
and coverage state IDs only. Support results require
`scoring_unit=generated_claim` and validate
`authoritative_generated_claim_ids`, applicable generated-claim IDs, decided
support state IDs, and unresolved audit IDs only. Cross-unit payloads,
including generated-claim IDs in coverage results or expected-claim IDs in
support results, are invalid; no generic unit-ID field may bypass this check.

#### Cohort metric-result artifact

`benchmark-q14-cohort-metric-result/1.0.0` has exactly:

```json
{
  "schema_version": "benchmark-q14-cohort-metric-result/1.0.0",
  "artifact_role": "cohort_metric_result",
  "cohort_result_id": "<derived-stable-id>",
  "benchmark_revision": "<benchmark-revision>",
  "cohort_id": "<stable-cohort-id>",
  "cohort_revision": "<cohort-revision>",
  "lane": "generation | end_to_end",
  "metric_contract_ref": {"metric_contract_id": "<id>", "metric_contract_version": "<version>", "sha256": "<digest>"},
  "metric_registry_ref": {"registry_id": "<id>", "registry_revision": "<revision>", "sha256": "<digest>"},
  "aggregation_contract_ref": {"aggregation_contract_id": "<id>", "aggregation_contract_version": "<version>", "sha256": "<digest>"},
  "fixture_results": [
    {
      "fixture_id": "<fixture-id>",
      "fixture_revision": "<fixture-revision>",
      "result_sha256": "<fixture-metric-result-digest>"
    }
  ],
  "result_kind": "fixture_vector_only",
  "aggregate": null
}
```

`fixture_results` is both the frozen cohort membership and the authoritative
ordered fixture vector; it uses the preregistered cohort order and contains
no missing, duplicate, imputed, zero-filled, or observation-selected fixture.
Every referenced fixture result must match the cohort lane, benchmark
revision, metric-contract reference, registry reference, and applicable
fixture revision. `aggregate` is required and must remain `null` for this v1
realization. No Q14-owned binding record is needed beyond these direct
references; an existing scorecard/publication layer may bind this cohort
result together with Q10-Q13/Q15 records without copying them.

#### Identity, canonicalization, compatibility, and digest DAG

Contract, registry, scorer, and aggregation IDs are stable opaque IDs whose
payload versions and external digests select their exact immutable content.
`result_id` is derived without a self-digest from the schema version,
benchmark/fixture identity, lane, ordered metric/registry/scorer references,
formula reference, input-artifact digests, applicability/exclusion references,
and canonical metric value. `cohort_result_id` is similarly derived from its
schema version, benchmark/cohort identity, lane, ordered metric/registry/
aggregation references, and ordered fixture-result digests. Replaying the
same payload and references must reproduce both the canonical bytes and
external SHA-256; a changed dependency creates a new immutable result.

All Q14 payloads use the existing benchmark canonical JSON contract: UTF-8
without BOM, compact JSON, sorted object keys, deterministic escaping, no
Unicode normalization, duplicate keys, NaN, Infinity, non-integer numeric
values, or trailing newline. Contract-defined array order is authoritative:
registry and supported-contract references use ID/version order; input roles
use the declared role order; unit IDs preserve gold/owner order; coverage
strata use critical/major/minor; Q8 states use their declared order; and
cohort fixture vectors use preregistered cohort order. Exact rational records are lowest
terms with `0/1` as the canonical zero. Binary floating point is never
formal numeric authority.

The content-addressed dependency DAG is:

```text
owner gold/item/mapping/projection/alignment/applicability/exclusion/input artifacts
  -> metric contract
  -> metric registry
  -> scorer contract
  -> fixture metric-result
aggregation contract -------------------------------> cohort metric-result
fixture metric-results -----------------------------> cohort metric-result
```

The metric contract may reference the aggregation contract, while the
aggregation contract contains no metric-result or metric-contract digest;
this keeps the graph acyclic. The registry and scorer contract reference
metric contracts, fixture results reference all required contract and input
digests, and cohort results reference immutable fixture results plus the
aggregation contract. No parent references a result, and no result embeds
its own digest. Q10 authority, Q11 gates, Q12 blocker/quality, Q13
comparison, Q15 run/collection, and existing publication records remain
downstream owner artifacts rather than new Q14 parents.

#### Replay and revision rules

The frozen replay matrix is:

| Changed dependency | Required work | Re-execute? |
| --- | --- | --- |
| Q11 gate contract or constant | Reevaluate the gate only | No |
| Q13 comparison policy | Recompare compatible results only | No |
| Aggregation contract or cohort membership | Reaggregate compatible fixture results | No |
| Metric registry membership or selected-contract digest | Rebuild affected result bindings; rescore only if the selected metric contract changed | No |
| Metric formula, unit, denominator, state transformation, direction, or canonical unit | Rescore affected fixture results, then rebuild dependent cohorts | No, unless an input became untrusted |
| Gold, item state, mapping, projection, alignment, applicability, or exclusion | Dependency-scoped rescore, then rebuild dependent cohorts | No, unless candidate output is missing/untrusted |
| Scorer implementation, scorer contract, configuration, or compatibility | Rescore compatible trusted inputs | No |
| Candidate output, execution contract, or trusted input bytes | Re-execute, then rescore and rebuild dependents | Yes |
| Unchanged trusted output with only scoring-policy change | Reuse trusted output and apply the scoped work above | No |

Metric-contract, registry, scorer, aggregation, fixture-result, or
cohort-result changes never overwrite an old artifact. A compatible result
requires exact schema version, ID/version, and digest agreement; same ID and
version with a different digest is invalid, not a fallback. A schema field,
enum, canonical-order, numeric-representation, or semantic change requires a
new schema/contract version as applicable. A new registry membership or
contract digest requires a new registry revision. A new scorer implementation
or deterministic requirement requires a new scorer version and digest. Q14
does not reinterpret Q15 retry/repeat history as new metric samples.

#### Ownership and remaining evidence boundary

Q14 owns these six schema families, deterministic formula/state execution
bindings, exact coverage/support result representations, aggregation
eligibility, fixture-vector authority, canonical serialization, digest
validation, and dependency-scoped replay. The metric registry selects but
does not define formulas; the scorer executes but does not redefine metric
semantics. Q10 owns authority, Q11 owns gates and numeric thresholds, Q12
owns applicability/exclusion/blocker/quality decisions, Q13 owns comparison,
Q15 owns repeated-run/statistical/collection semantics, Q26 owns note and
projection schemas, and Q17/Q21 continue to own runner/collection artifacts.

Still pending are CER/WER tokenization and normalization, IoU, temporal
delta, span-overlap, table-alignment distance, formula semantic equivalence,
metric-specific parser unit inventories, evidence-approved formal aggregation
beyond `fixture_vector_only`, numeric Q11 constants, Q12 blocker
classifications, Q13 relative/near-zero/recovery policy, Q15 repeat count,
scheduling, and statistical methods, subjective readability, importance
weights, numeric partial credit, universal macro or formal micro/pooled
aggregation, and any renderer lane. These are not hidden fields in the v1
schemas and cannot be supplied by a scorer implementation.

## 3. Frozen benchmark matrix

All 13 case IDs and their required characteristics are in scope. Q22 records
project-owned creation plans for `P01`-`P04`, `W01`-`W03`, and `Y01`-`Y02`, but
their exact bytes and evidence remain unapproved. Q23 freezes `C01`-`C02` and
`S01`-`S02` as synthetic-only fixtures in separate Chat and Screenshot source
families. No matrix entry is canonical until all applicable Q22-Q25 evidence
and approval requirements close.

| ID | Source family | Required characteristics | Primary lane coverage |
| --- | --- | --- | --- |
| P01 | Native PDF | English technical document; headings, lists, code; at least 8 pages | Parser, generation, end-to-end |
| P02 | Native PDF | Bilingual report; at least two tables and figures | Parser, generation, end-to-end |
| P03 | Scanned PDF | Traditional Chinese; at least 5 pages; skew or noise | Parser, generation, end-to-end |
| P04 | Mixed PDF | Chinese and English; native and scanned pages; formulas and a table | Parser, generation, end-to-end |
| W01 | Static web | Clean technical article with headings, list, and code | Parser, generation, end-to-end |
| W02 | Static web | Article with navigation, advertisements, related links, and comments | Parser, generation, end-to-end |
| W03 | Dynamic web | Main content appears only after JavaScript; deterministic offline snapshot | Parser, generation, end-to-end |
| Y01 | YouTube captions | Manual English captions with chapters | Parser, generation, end-to-end |
| Y02 | YouTube captions | Automatic Traditional Chinese or mixed-language captions | Parser, generation, end-to-end |
| C01 | Chat | Multiple speakers, Markdown, quote, code, and timestamps | Parser, generation, end-to-end |
| C02 | Chat | Bilingual threaded discussion with reply references | Parser, generation, end-to-end |
| S01 | Screenshots | Ordered bilingual UI and table sequence | Parser, generation, end-to-end |
| S02 | Screenshots | Adjacent captures with 20–30% overlap | Parser, generation, end-to-end |

The logical smoke profile is `P01`, `W01`, `Y01`, `C01`, and `S01`. Each entry
references the same canonical fixture revision, exact bytes, snapshot digest,
and compatible dependent artifacts as `full`; there is no reduced or smoke-only
fixture variant. The selection exercises one case from every source family but
does not claim source-subtype coverage or formal authority.

Each case retains authoritative fixture-level metric vectors under Q14. The
matrix creates no cross-source, cross-lane, parser-global, or universal-macro
composite. Formal cohort aggregation exists only where the applicable metric
contract preregisters an evidence-supported disposition.

Q15 treats this matrix as a fixed conformance suite, not a population sample.
Repeated-run collections retain complete fixture and run vectors without
claiming population confidence, statistical significance, or production-
traffic generalization.

## 4. Terms frozen in this round

**Smoke profile**: The non-authoritative logical set `P01`, `W01`, `Y01`,
`C01`, and `S01`, resolved to the same canonical fixture revisions, exact
bytes, digests, and compatible dependent artifacts used by `full`. It has no
reduced or smoke-only fixture variants and makes no subtype-coverage claim.

**Formal baseline**: A result produced by the `full` profile over all 13
canonical fixtures with eligible gold and a validated, versioned scorer
contract. A partial or draft-gold result is not a formal baseline.

**Characterization baseline**: A faithful measurement of current MVP behavior
that may fail unsupported-capability quality gates. It cannot waive benchmark
infrastructure validity.

**Adoption authority**: Permission for a benchmark result to support a decision
to replace or change a parser, generation flow, prompt, schema, or renderer.
Only the frozen `full` profile has this authority.

**Canonical fixture**: A repository-stored, redistribution-safe, privacy-
reviewed, content-addressed fixture eligible for formal scoring.

**Local diagnostic fixture**: A Git-ignored fixture used for investigation
only. It cannot affect an acceptance or adoption result.

**Frozen reference document**: The versioned, content-addressed generation-lane
input shared byte-for-byte by all generation candidates. It is source-faithful
and separate from gold answers.

**NormalizedDocument**: The versioned benchmark representation of source
content, order, structure, locators, availability, and producer provenance. It
is a benchmark boundary, not the current production runtime contract.

**Element identity**: An artifact-local deterministic identity for one
segmented source unit. It is not a cross-parser alignment key.

**Section**: A hierarchical source interval used for navigation and bounded
all-section planning. It does not duplicate its elements' content.

**Locator**: A typed, source-derived position that connects an element to a
page, DOM node/span, caption cue/time, chat message/thread, or screenshot
region. Missing locators are explicit rather than invented.

**Source reference**: A gold pointer to either one complete reference-document
element or one exact Unicode code-point range inside an element. It does not
carry a second authoritative copy of source text.

**Structure assertion**: A versioned gold statement about source hierarchy,
order, table/list organization, or another structural relation. Locator facts
are not structure assertions.

**Locator assertion**: A versioned gold statement about an approved typed
source position or its availability.

**Evidence item**: A gold-local atomic semantic proposition that can be judged
for support independently while retaining all truth-defining conditions.

**Expected claim**: A gold-local statement of content a complete note should
communicate, supported by one or more evidence items but distinct from them.

**Evidence category**: A closed, versioned content-role label on an evidence
item. It is independent from importance and does not create a scoring unit.

**Category applicability**: A fixture-level reviewed audit stating whether a
category is required, optional, absent, or excluded by a preregistered scope
rule. It does not replace evidence-to-claim mappings.

**Importance**: The expected impact of omitting, reversing, or misstating an
expected claim. Formal importance exists only on expected claims.

**Importance rationale**: A human-reviewed counterfactual explanation of how
claim loss or distortion would affect understanding, decisions, process
correctness, or risk.

**Support role**: The `required`, `alternative`, or `context` relationship from
an expected claim to an evidence item. It carries no independent importance.

**Acceptable paraphrase**: Candidate wording that preserves all required
semantic components and truth conditions of an expected claim. Approved
examples are regression anchors, not a complete whitelist.

**Claim coverage**: The degree to which candidate output correctly conveys an
expected claim's required components. It is independent from source support.

**Source support**: The relationship between one generated claim and approved
source evidence, including support, absence of support, contradiction, and
overstatement.

**Semantic component**: A reviewed truth-condition unit such as subject,
condition, quantity, attribution, or modality used to explain and replay claim
matching without creating another scoring unit.

**Support expression**: The normative evidence logic for an expected claim,
using only evidence leaves, `all_of`, and `any_of`.

**Overstatement**: A generated claim that expands source certainty, scope,
frequency, generality, attribution, or resolution status.

**Recurrence evidence**: One evidence item representing source-supported
frequency, trend, agreement, consensus, or explicit emphasis across multiple
occurrences.

**Claim-to-gold match artifact**: A versioned candidate-specific artifact that
freezes claim links, expected-claim coverage, generated-claim support, and
candidate-side relations for deterministic replay without modifying gold.

**Authoritative raw text**: The immutable source or candidate string to which
all code-point spans refer. It is never replaced by a normalized view.

**Comparison projection**: A deterministic, versioned derived text view that
removes only approved presentation differences and retains complete raw-offset
provenance.

**Normalization profile**: A preregistered closed rule set for one content
class, including operation order, forbidden transformations, version, and
abstention conditions.

**Recognition-error correspondence map**: A diagnostic relation between
recognition output and reference content. It cannot correct artifacts, guide a
candidate, act as an automatic match, or grant parser credit.

**Alignment group**: A reviewed or deterministic one-to-one, one-to-many, or
many-to-one relation between reference and candidate units, with all supporting
locator, structure, and decision provenance.

**Alignment conflict**: A case where stronger alignment evidence disagrees.
The matcher cannot discard that evidence and fall back automatically.

**Abstain**: A deterministic rule's explicit refusal to decide because safe
equivalence or alignment cannot be proved. It creates an unresolved record and
has no score or exclusion meaning until Q10.

**Generated claim map**: A versioned, candidate-specific derived artifact that
freezes independently supportable output claims and their original output
spans. It is not part of gold.

**Source-side exclusion**: An explicit, reviewed gold record that removes a
named source unit from only a specified lane and denominator for an approved
reason.

**Approved gold**: A versioned gold artifact in `reviewed` or `adjudicated`
state with no blocking unresolved dispute.

**Source resolution status**: The source's own `resolved`, `unresolved`, or
`not_stated` position on a contradiction. Source-level `unresolved` is
authoritative content, not an unfinished benchmark decision.

**Process unresolved**: An annotation, mapping, normalization, or alignment
decision that deterministic rules cannot safely make and the required human
process has not adjudicated.

**Ownership scope**: The `gold`, `candidate`, or `run` owner of an unresolved
or validity record. It is separate from the set of results affected by that
record.

**Affected scope**: The exact fixtures, candidates, artifacts, objects, lanes,
and named denominators whose authority depends on a record.

**Authority effect**: A versioned-rule-derived conclusion that an unresolved
item blocks its affected formal scope or is a non-blocking diagnostic outside
all formal denominators and closure conditions.

**Provisional result**: A diagnostic result produced while a blocking process
unresolved item remains. It has no formal pass/fail, ranking, baseline-
comparison, or adoption authority.

**Invalid scope**: A result scope whose schema, digest, manifest, required
artifact, or execution contract is invalid. Invalidity is not a semantic
dispute and does not automatically invalidate independent results.

**Unscorable exclusion**: A human-adjudicated source-side exclusion reserved
for a candidate-independent, irrecoverable source defect. It cannot be used
for disagreement, review cost, parser loss, candidate quality, ambiguity, or
unfinished matching.

**No formal evaluation basis**: A fixture/lane state in which approved
exclusions leave a required named denominator with no eligible gold unit or
prevent the fixture from testing its preregistered case purpose.

**Authority closure**: The versioned, deterministic validation that all
required review, unresolved disposition, artifact completeness, version, and
digest conditions are satisfied for a claimed formal scope. It does not decide
quality pass/fail.

**Gate topology**: The frozen set and dependency order of authority
prerequisites, absolute floors, non-regression checks, improvement checks, and
the later adoption decision. It contains no unsupported numeric constant.

**Gate address**: The lane, source type, preregistered subtype, and metric ID
that identify one gate slot in the sparse gate matrix.

**Gate slot**: A versioned location for a possible quality gate. It produces no
formal decision until its metric contract, applicability, comparator, evidence,
and required constants are approved.

**Absolute floor**: A candidate's minimum acceptable quality independent of
baseline quality. Floors are metric-specific and non-compensating.

**Non-regression gate**: A versioned comparison that checks whether a candidate
preserves baseline quality for a preregistered metric and scope.

**Improvement gate**: A versioned comparison against a preregistered candidate
benefit claim. The target lane, cohort, and primary metrics are frozen before
formal candidate execution or output capture.

**Characterization baseline role**: The role of faithfully measuring current
MVP behavior. A characterization baseline may have formal comparison authority
without satisfying future quality floors.

**Formal comparison authority**: Eligibility of a baseline or candidate metric
artifact for direct comparison after full-profile, gold, closure, version, and
digest requirements are met. It is separate from whether quality passes.

**Calibration status**: A gate field with `pending_calibration` or `approved`.
An exact threshold exists only in the approved state.

**Pending calibration**: A gate slot whose exact constant lacks the complete,
independently reviewed evidence required for a formal gate decision.

**Metric-native absolute difference**: The paired candidate-minus-baseline
change expressed in the metric's canonical unit, with direction and comparator
defined by the metric contract.

**Measurement tolerance**: A separately calibrated allowance for demonstrated
measurement behavior. It cannot lower a normative quality requirement and is
not a display-rounding rule.

**Numeric authority**: The canonical integer, rational, or versioned Decimal
representation used for gate evaluation. Display-rounded values are not
authoritative.

**Discrete invariant candidate**: A preregistered non-numeric requirement and
rationale whose blocking role and scope remain unresolved until Q12.

**Result role**: The intended use of a result, `formal` or `diagnostic_only`.
It is independent of Q10 authority status and does not grant authority.

**Quality decision**: The decided quality state `pass`, `hard_blocked`,
`aggregate_gate_failed`, or `not_evaluated`. It does not encode invalidity,
provisional authority, or unresolved governance.

**Hard blocker**: A decided, authoritative item-level quality failure that
propagates from its smallest fixture/lane scope and cannot be compensated by
another metric or lane.

**Aggregate gate failure**: A decided failure of an aggregate quality gate
without an item-level hard blocker identity. It remains distinct from
`hard_blocked`.

**Blocker rule**: A versioned rule mapping one authoritative observed state and
its prerequisites to at most one primary blocking disposition for a scoring
unit.

**Critical dependency**: Required parser evidence, structure, or locator
information derived from a critical expected claim's approved support
expression. Evidence itself receives no importance value.

**Contains hard blocker**: A cohort or lane-bundle marker identifying the
originating blocked fixtures without converting every member outcome into a
failure.

**Partial-state vector**: Separate counts and rates for every coverage or
support state, with no implied numeric partial credit.

**Denominator disposition**: The reviewed reason a unit enters or leaves one
named denominator, including typed handling for `not_applicable`, gold
`unavailable`, approved `unscorable`, and optional content.

**Failure event identity**: An immutable lane-local or metric-local identity
for one observed quality outcome. It is never a global cross-lane root-cause
identity.

**Reviewed causal relation**: A human-approved `caused_by`,
`same_root_cause_as`, or `derived_from` link between independent outcomes. It
does not remove either outcome from scoring.

**Hierarchical gate vector**: A scorecard topology in which item results form
fixture results, fixtures enter source cohorts, and source and lane gates stay
separate instead of becoming a global composite.

**Full-profile absence**: Failure to establish a `full` execution containing
all 13 canonical cases and its complete bundle identity and prerequisites. It
precludes a formal baseline or candidate comparison but does not erase
independently authoritative absolute metric evidence.

**Scoped pair failure**: An invalidity, missing dependency, authority failure,
or incompatibility affecting one `metric × fixture × lane` comparison pair
inside an established full-profile run. Its effect follows Q10's minimal
affected scope.

**Authoritative absolute metric evidence**: A metric result whose own inputs,
validity, authority, representation, and dependencies are complete for its
absolute scope, independently of whether a baseline comparison is eligible.

**Diagnostic pair comparison**: A replayable baseline/candidate calculation
published with `result_role=diagnostic_only`. It cannot support formal
non-regression, improvement, complete-benchmark, or adoption claims.

**Formal pair comparison**: A comparison for one eligible
`metric × fixture × lane` pair whose full-profile and scoped authority,
validity, version, digest, denominator, and contract prerequisites are closed.

**Valid zero-quality result**: An authoritative metric value of exactly zero
produced by a valid execution and complete schema-valid artifact against a
positive formal denominator. It is a quality result, not a zero denominator.

**Comparison closure failure**: Absence or ineligibility of a required paired
comparison dependency. It blocks only dependent comparative outcomes and is
not `no_formal_evaluation_basis`.

**Comparison-policy contract**: The versioned contract selecting approved
metric-native absolute and, when separately authorized, relative comparators,
including their prerequisites, domains, ordered evaluation, and primary-reason
precedence. It is unrelated to the RAG lexical retrieval fallback.

**Absolute comparator subrecord**: The comparison record component describing
absolute applicability, execution, selected comparator, eligibility inputs,
result, and any comparison-specific reason or upstream reference that
prevented execution.

**Relative comparator subrecord**: The orthogonal comparison record component
describing metric-contract permission, policy/domain readiness, relative
disposition, and a result only when performed.

**Recovery-from-zero diagnostic**: Optional derived diagnostic information for
a metric whose approved contract establishes that zero means no desired
success and that the observed movement is favorable. It is not a metric, gate,
authority, blocker, quality decision, or formal improvement conclusion.

**Comparator-result artifact**: An immutable calculation artifact containing
stable pair inputs, dependency references, comparator execution, and absolute
and approved-relative outputs. It owns no authority, gate, quality, receipt, or
self-digest field.

**Governance/authority record**: An immutable, content-addressed, separately
versioned record of review, approval, rationale, lifecycle, and an authority
decision, revised only through a successor.

**Gate-evaluation artifact**: The Q11-owned record applying a versioned gate
contract and approved comparator rule to compatible metric or comparison
evidence. It owns the gate decision, not raw metric scoring or Q10 authority.

**Binding/publication manifest**: An immutable set of references binding
fixture and cohort metric-result artifacts, comparator results, Q10 authority
records, Q12 blocker and quality outcomes, Q11 gate evaluations, Q13 comparison
outcomes, Q15 run-plan manifests, repeated-run collection manifests,
statistical diagnostic artifacts, governance records, receipts, result role,
and publication context. It does not recalculate metrics or statistics or copy,
re-own, or redefine authority, quality, gate, comparison, diagnostic,
governance, or receipt decisions and content.

**Metric contract**: An immutable, versioned, content-addressed definition of
one metric's scoring unit, denominator semantics, applicability, formula,
direction, numeric representation, and aggregation eligibility. It consumes
but cannot create or override Q12 denominator dispositions.

**Metric-registry manifest**: An immutable selection of approved metric-
contract IDs, versions, and digests for one benchmark release. It is not a
mutable catalog and owns no formula.

**Scorer contract**: The versioned identity, supported metric-contract
versions, compatibility declarations, and deterministic execution requirements
of a scorer implementation. It cannot override a metric formula.

**Coverage state-vector metric**: Separate exact counts and exact rational
rates for `fully_covered`, `partially_covered`, and `not_covered`, with no
numeric partial credit or combined scalar.

**Support distribution diagnostic**: Derived rates over Q8 support states used
only to describe a distribution. It cannot independently rank, gate, establish
improvement, pass support quality, or dilute a discrete unsafe claim.

**Parser metric family**: One non-compensating parser measurement dimension
with source-side evidence, span, structure, or locator units. No family is a
parser-global composite.

**Fixture metric-result artifact**: An immutable deterministic calculation for
one fixture, lane, and metric contract containing unit identities, exact counts
or result vectors, denominator provenance, and dependency digests, but no
authority, blocker, quality, gate, or comparison decision.

**Cohort metric-result artifact**: An immutable result that binds compatible
fixture metric results, frozen cohort membership, and an approved aggregation
contract. It owns no item mapping, blocker, quality, gate, or comparison.

**Fixture vector**: The authoritative ordered set of fixture metric results for
a named cohort. It remains available whether or not the metric has an approved
formal aggregate.

**Aggregation disposition**: A preregistered metric-contract choice to retain
only the fixture vector or to use an independently evidence-approved aggregate.
It is a policy choice rather than a gate constant or numeric calibration.

**Audit inventory**: Raw cross-stratum or cohort counts retained to verify
membership and provenance. It does not represent completeness or cross-fixture
quality.

**Fixed conformance suite**: The 13 versioned canonical fixtures treated as a
finite required test set rather than a random sample of a source or production
population.

**Project-owned fixture candidate**: An illustrative creation plan or produced
artifact whose content is intended to be owned by the project. The label grants
no canonical eligibility. Exact bytes, digests, provenance, item-level rights
and privacy evidence, and independent approval must close first.

**Synthetic-only source-family policy**: The Q23 v1 rule that each Chat and
Screenshot fixture is project-owned synthetic material. Chat and Screenshot
remain separate source families; the policy neither combines them into one
cohort nor adds a second real-world or seed-derived cohort.

**Canonical benchmark storage root**: The tracked
`tests/evals/parser_note_completeness/v1/` hierarchy containing fixture bytes,
fixture governance, reference documents, gold, and manifests. It contains no
generic run-receipt directory and cannot reference ignored local diagnostics.

**Artifact-and-scope independence**: A reviewer or approver is independent of
the work they approve within the governed artifact and scope. One person may
hold compatible roles elsewhere, but self-approval never becomes independent
review.

**Runner-controlled terminal outcome**: An outcome for which the runner retains
control long enough to emit its terminal JSON status and package. Externally
forced termination may prevent emission and is represented through preserved
partial history plus later reconciliation or authorized resume.

**Runner terminal package**: The canonical immutable package referenced by a
machine-readable terminal JSON status. Its process exit code summarizes runner
or transport completion only and does not replace Q10-Q15 records. A package or
exit code is never invented for an externally terminated process that emitted
neither.

**Offline scoring and replay boundary**: The externally enforced no-egress OS
or container boundary used for canonical validation, scoring, comparison,
aggregation, and deterministic replay.

**Provider-backed candidate capture**: A preregistered execution that may call
an approved provider to produce candidate output from approved frozen input
bytes. It is separate from offline scoring/replay and cannot acquire canonical
source content dynamically.

**Network-denial conformance record**: An immutable record binding offline
execution identity to the enforcement mechanism, version, policy digest, and
applicable denied network probes. Probe denial supports but does not alone
prove complete no-egress enforcement.

**Replay provenance topology**: The frozen categories and dependency
references needed to identify code, runtime, allowlisted configuration,
contracts, provider/model/seed availability, platform facts, and approved
numeric contexts without persisting unrestricted configuration or secrets.

**Raw resource observation vector**: Complete per-attempt or per-run duration,
size, retry, provider-usage, cost, CPU, memory, and availability facts. It is
receipt evidence and owns no authority, quality, comparison, scoring, or
adoption decision.

**Finite-suite estimand**: A versioned description of a quantity over an exact
suite or cohort, lane, metric, execution contracts, Q13-eligible fixture pairs
when comparative, and repeated-run design. It has no population interpretation.

**Run membership role**: The preregistered Q15 meaning that a logical run is
formal-required or diagnostic. It is not Q13 `result_role` and grants no Q10,
Q12, or Q13 authority.

**Logical run slot**: A preregistered run-plan position with one immutable
logical-run identity and membership role. Attempts append beneath it; retry,
resume, and scoring replay cannot create a replacement slot or increase run
count.

**Scoring replay**: Deterministic reapplication of a Q14 scorer to the same
trusted output bytes. It creates no new run and must reproduce its result and
digest.

**Deterministic system re-execution**: A new execution of a component whose
contract promises deterministic output. A mismatch is conformance or invalidity
evidence, not a stochastic sample.

**Stochastic repeat**: A new independent execution of an explicitly stochastic
component that creates a new immutable output artifact and logical run identity.

**Retry attempt**: A further attempt within one logical run under a
preregistered transient-failure policy. It retains an immutable receipt but
does not increase run count or statistical sample size.

**Run-level pairing authority**: Eligibility to treat baseline and candidate
runs as statistical pairs under a preregistered rule with compatible shared
randomness or seeds, execution block, provider/model revision envelope, and
symmetric conditions. Equal ordinals or nearby scheduling do not grant it.

**Preregistered run-plan manifest**: An immutable pre-capture plan containing
logical run slots, run-membership roles, order or blocks, fixture/lane/candidate
identity, execution-contract references, and planned pairing references. It is
not updated with outputs after capture.

**Repeated-run collection manifest**: An immutable plan-wide binding from one
run-plan revision to every formal or diagnostic slot's complete success,
failure, invalid, missing, or still-unclosed history and referenced records. A
partial revision is audit-only; Q15 separately owns collection completeness.
The manifest calculates no statistic, imputes or replaces no slot, and owns no
referenced authority.

**Statistical diagnostic artifact**: An immutable artifact that applies a
versioned finite-suite diagnostic method to exact referenced inputs. It owns
only its diagnostic calculation, not Q10 authority, Q11 gates, Q12 quality,
Q13 formal comparison, formal improvement, or adoption.

**Collection completeness**: The Q15 membership and binding fact that every
required logical run slot has the records and closure required by its plan. It
is neither a Q10 authority status nor a Q12 quality decision.

**Renderer-neutral note artifact**: The Q26
`benchmark-note-document/1.0.0` artifact with `artifact_role=pre_render_note`,
used before renderer conversion. It preserves applicable note structure, text,
citations, locators, and transformation lineage without becoming a source
document, gold artifact, production proposal, or renderer authorization schema.

**Final rendered-note projection**: The Q26
`benchmark-rendered-note-projection/1.0.0` artifact with
`artifact_role=rendered_note_projection`, captured from authoritative renderer
output or verified readback. It is not an assumption derived solely from an
outgoing renderer request.

**Final rendered-note quality**: The End-to-end view comparing the final
rendered-note projection with approved gold or reference evidence through
applicable Q14 metrics.

**Renderer preservation**: The separate End-to-end view comparing the pre-
render note artifact with the final rendered-note projection for renderer-
origin loss or fabrication.

**Pre-capture coverage plan**: An immutable all-section plan created before
generation, bound to the exact reference, routing policy, and execution
contract, and containing no generated result or answer hint.

**Primary work-unit assignment**: The sole scoring-owning assignment of an
applicable source unit. Declared context overlap does not create another
primary assignment or scoring credit.

**Work-unit execution artifact**: An immutable output or receipt for one
planned long-source unit. Its outcome cannot be silently skipped or replaced.

**Merge and coverage-closure artifact**: The immutable binding from the pre-
capture plan and all work-unit outcomes through ordered merge and evidence
mapping to the final renderer-neutral note artifact and detected coverage or
consistency defects.

**Generation routing policy**: A versioned deterministic pre-generation policy
that selects one generation mode from frozen source, structure, provider, and
capacity facts without inspecting candidate quality or output.

**Route-decision artifact**: The immutable pre-generation record of routing
inputs, policy identity, and selected mode used for formal conformance.

**Forced-mode diagnostic**: A preregistered diagnostic execution under a
separate contract that cannot enter, replace, or be promoted into formal
results after output observation.

## 5. Decision status and remaining frontier

Q1-Q11 are frozen at their stated contract boundaries. Q11 exact constants
remain `pending_calibration`. Q12 blocking and aggregation topology is frozen
with evidence-dependent classifications and numeric formulas pending. Q13
non-numeric baseline-comparison and artifact topology is frozen with metric-
specific policy applicability, schema realization, and numeric calibration
pending. Q14 deterministic-scoring and artifact topology, coverage state-vector
formulas, support exact-count/non-dilution policy, and Q14-owned metric,
registry, scorer, aggregation, fixture-result, and cohort-result schema
realization are frozen in section 2.141. Metric-specific
parser measurement formulas, evidence-supported aggregation selections beyond
the v1 fixture vector, comparison artifact realization, and numeric
calibration remain pending. Q26 note and rendered-projection schema
realization is complete in
section 2.135. The Q15 status is:

`Q15 finite-suite repeated-run, non-inferential statistical-diagnostic, artifact, and adoption-authority topology frozen; formal repeat count and scheduling, execution compatibility, diagnostic-method activation, schema realization, and applicable numeric calibration pending.`

Q16 smoke IDs and reference semantics, Q17 runner/exit/resume topology, Q18
offline-enforcement and provider-capture separation topology, Q19 provenance-
capture topology, Q20 raw resource-observation and non-authority topology, and
Q21 runner-materialization topology are frozen. Q16-Q21 are not fully frozen:
schema realization, execution compatibility, cold/warm applicability,
diagnostic resource methods, retry details not already governed by Q15, and
applicable Q11 numeric ceilings remain pending under their existing owners.

Q22 remains `evidence_required`: its nine project-owned creation plans are
unapproved candidates, and no fixture becomes canonical before exact bytes,
digests, provenance, rights/privacy evidence, and independent approval exist.
Q23 freezes separate synthetic-only Chat and Screenshot v1 fixture families.
Q24 freezes the canonical tracked and ignored-local storage roots and their
record-placement boundaries; its diagnostic End-to-end result/attempt package
is realized in section 2.140, while broader formal collection/store
publication remains pending. Q25 freezes independence by artifact and governed scope plus
the scoped consequences of missing approval. Q26-Q29 freeze their renderer-
neutral artifact, End-to-end gate, exhaustive coverage, and deterministic
routing topologies while preserving the realization and evidence slots stated
below.

The following issues materially affect scoring, cost, reproducibility, or MVP
isolation and require later evidence, calibration, policy, or realization.

### 5.1 Gold ontology and matching governance

Q1-Q10 are frozen. Q10 freezes scoped unresolved ownership, blocking authority,
provisional and invalid results, adjudication, `unscorable`, immutable replay,
and formal-authority closure. It does not define a quality pass/fail gate.

Q11 gate topology and registration protocol are frozen. Its exact constants
remain pending until the Q11 completion evidence exists. Q12 blocker and
aggregation topology, denominator disposition, and causal-reporting governance
are frozen. Q13 freezes full-profile and pair eligibility, valid-zero and
zero-denominator boundaries, absolute-first and exact-zero policy, the ban on
epsilon substitution, restricted recovery diagnostics, missing-pair closure,
orthogonal comparator subrecords, versioned comparison-policy evaluation order,
primary-reason precedence, and artifact ownership, digest, and revision
topology.

Q14 additionally freezes metric-contract, registry, and scorer ownership;
coverage vectors without numeric partial credit; support exact counts with
diagnostic-only rates; parser metric families and source-side units; the three-
lane and readability boundaries; separate importance strata; four-layer metric
artifact ownership; fixture-vector authority; evidence-dependent aggregation
selection; and canonical replay.

Q15 additionally freezes the fixed-suite interpretation, orthogonal uncertainty
taxonomy, fixture-primary pairing, four execution behaviors, run-membership and
anti-selection rules, lane-specific repeated-run topology, run-scoped blocker
non-compensation, complete-vector publication, non-inferential diagnostic
boundary, collection and statistical artifact ownership, and adoption-authority
separation.

The remaining frontier is owned as follows:

- Q11 retains numeric gate constants in `pending_calibration`.
- Q12 retains evidence-dependent blocker classifications, other numeric scoring
  formulas outside Q14's frozen coverage vectors, and the critical-density
  numeric trigger.
- Q13 retains metric-specific relative applicability and valid domains, near-
  zero policy, recovery applicability, and comparison schema realization.
- Q14 exact metric, registry, scorer, aggregation, fixture-result, and
  cohort-result schema realization is frozen in section 2.141. Q14 does not
  own Q26 note or rendered-projection schemas. Q14 retains comparison
  artifact realization, metric-specific parser unit inventories and
  applicability; CER/WER tokenization and
  normalization; IoU, temporal-delta, span-overlap, table-alignment, and
  formula-equivalence contracts; evidence-supported formal aggregation
  selection beyond the v1 fixture vector; genuine measurement-boundary
  calibration where required; and
  scorer compatibility and canonical-replay evidence.
- Q15 retains evidence-dependent formal repeat count, scheduling or block
  design, supported seed policy, execution compatibility, run-level pairing,
  end-to-end dependency mode, metric-specific finite-suite functional form,
  diagnostic-method activation, and schema or manifest realization.
- Q16-Q21 retain exact runner, terminal-package, receipt, conformance,
  provenance, observation, and collection schema realization; execution-
  compatibility and equivalence rules; cold/warm applicability; diagnostic
  resource methods; platform-specific no-egress and probe realization; retry
  details not already governed by Q15; and Q11-owned numeric time, resource,
  and cost ceilings.
- Q22 retains exact candidate bytes, fixture revisions, digests, creation or
  acquisition provenance, item-level rights/privacy evidence, and independent
  approval before canonical eligibility.
- Q24 retains exact formal run-result and run-receipt store realization under
  the existing artifact and schema owners; it is not a generic fixture-tree
  `receipts/` directory.
- Q26 owns the exact renderer-neutral and rendered-projection schemas recorded
  in section 2.135. Q14 retains projection, alignment, and measurement
  formulas plus all metric/scorer/result and aggregation policy.
- Q28 retains work-unit sizing, context-overlap amount, merge and contradiction-
  detection realization, measurements, and applicable boundary evidence. The
  D1–D8 and D11 schema realization is frozen in section 2.137.
- Q29 retains evidence for numeric routing boundaries, provider-capacity and
  execution compatibility, policy/schema realization, and revision approval.

Population inference, population confidence intervals, p-values, statistical
significance, and a formal statistical gate are prohibited in v1 or require a
future benchmark and Q11 gate revision. They are not current Q15 calibration
slots.

Numeric partial credit, importance weights, a universal macro, formal micro or
pooled aggregation, formal support-rate use, subjective readability, and a
renderer lane are not pending v1 decisions.

### 5.2 Scoring and acceptance

11. Gate topology, scope, comparison semantics, registration, and calibration
    protocol are frozen. Exact constants remain `pending_calibration` until the
    required fixtures, gold, metric contracts, formal characterization
    baseline, repeatability evidence, independent review, manifest, and digests
    exist before formal candidate execution or output capture.
12. Blocking and aggregation topology is frozen. Evidence-dependent blocker
    classifications and numeric formulas remain pending. Q12 establishes
    critical and source-support hard blockers, parser critical dependencies,
    scoped propagation, hierarchical gate vectors, typed denominator removal,
    lane-local outcome identity, and immutable rule governance without adding
    partial-credit values, importance weights, or a global composite.
13. Non-numeric baseline-comparison and artifact topology is frozen. Formal
    comparison requires the `full` profile and eligible scoped pairs;
    metric-native absolute comparison is authoritative, exact-zero relative
    comparison is not defined, missing required pairs fail comparison closure,
    and comparator, governance, gate, publication, and receipt ownership stay
    separate. Metric-specific relative and recovery applicability, near-zero
    policy, schema realization, and numeric calibration remain pending.
14. Deterministic-scoring and artifact topology, coverage state-vector
    formulas, and support exact-count/non-dilution policy are frozen. Q14 v1
    forbids numeric partial credit, formal support-rate use, importance
    aggregation, a universal macro, subjective readability scoring, and a
    renderer lane. Metric-specific parser measurement contracts, formal
    aggregation selections, schema realization, and genuine measurement
    calibration remain pending evidence.
15. Finite-suite repeated-run and non-inferential statistical-diagnostic
    topology is frozen. Fixture remains the primary Q13 paired unit; equal run
    ordinals do not create statistical pairs; retries and replays add no sample;
    complete run vectors and collection closure remain visible; blockers do not
    compensate across formal runs; and Q15 diagnostics do not decide adoption.
    Formal repeat count and scheduling, execution compatibility, run-level
    pairing evidence, diagnostic-method activation, schema realization, and
    applicable method parameters remain pending. Bootstrap is not enabled in
    v1, and population CI, p-values, significance claims, and formal statistical
    gates are prohibited or future revisions rather than pending calibration.

### 5.3 Runner and reproducibility

16. Smoke uses `P01`, `W01`, `Y01`, `C01`, and `S01` and references the exact
    canonical full-fixture revisions, bytes, digests, and compatible dependent
    artifacts. Reduced and smoke-only fixture variants are forbidden; smoke
    remains diagnostic and makes no subtype-coverage claim.
17. One versioned runner CLI emits a machine-readable terminal JSON status and
    canonical immutable package for each runner-controlled terminal outcome.
    Exit `0` means schema-valid completion, `1` means operational failure or
    incomplete required work, and `2` means rejected or invalid input/execution
    contract. These codes do not replace Q10-Q15 states. Externally forced
    termination may emit neither package nor exit code; immutable partial
    history is reconciled later. Resume is limited to authorized open slots and
    append-only attempt history under the unchanged plan and contract digests.
18. Canonical validation, scoring, comparison, aggregation, and replay require
    an externally enforced no-egress boundary and conformance record. Separately
    preregistered provider-backed candidate capture is allowed only by its Q15
    execution contract, receives approved frozen input, and is not called
    offline.
19. Replay records bind the approved code/build, dependency/runtime,
    allowlisted configuration, contract, platform, provider/model/seed,
    receipt, and numeric-context provenance categories. Exact schemas and
    execution-equivalence rules remain policy work; unrestricted secret-bearing
    configuration and raw private content are prohibited.
20. Per-attempt and per-run raw duration, size, retry, usage, cost, CPU, memory,
    and availability vectors are retained without requiring v1 percentiles.
    Cold/warm design and diagnostic methods remain policy slots, while all
    numeric time, resource, and cost ceilings remain Q11
    `pending_calibration`.
21. The preregistered plan enumerates every logical slot before capture;
    stochastic repeats have distinct slots, retries append within a slot,
    replay creates no run, and resume cannot change membership. Immutable
    collection manifests preserve every slot and its full history. One
    collection cannot mix Parser reuse and full-pipeline End-to-end execution;
    selecting the mode remains Q15 policy.

The remaining Q16-Q21 work is realization or evidence-dependent policy, not an
invitation to reopen these topologies. Q22 remains evidence-dependent, Q23-Q25
are frozen at the boundaries below, and Q26-Q29 are frozen at the topology
boundaries recorded in section 5.5.

### 5.4 Fixture acquisition and governance

22. `evidence_required`. Nine project-owned creation plans are recorded for
    `P01`-`P04`, `W01`-`W03`, and `Y01`-`Y02`. They are unapproved candidates,
    their working titles are illustrative, and no candidate is canonical until
    exact bytes, digests, provenance, rights/privacy evidence, and independent
    approval exist. Synthetic caption fixtures use typed `unavailable` rather
    than invented YouTube identities and do not score audio or ASR quality.
23. Frozen. `C01`-`C02` and `S01`-`S02` are project-owned synthetic-only v1
    fixtures. Chat and Screenshot remain separate source families, and v1 has
    no second real-world or seed-derived cohort.
24. Frozen. Canonical tracked records use
    `tests/evals/parser_note_completeness/v1/` with `fixtures/`, `governance/`,
    `reference_documents/`, `gold/`, and `manifests/`. Acquisition receipts are
    fixture-governance records; run receipts/results remain separate artifacts.
    Local diagnostics use `local_storage/benchmarks/parser_note_completeness/v1/`
    and cannot be referenced by formal manifests. Exact formal result-store
    realization remains pending.
25. Frozen. Independence is evaluated by artifact and governed scope. A person
    may hold compatible roles elsewhere but cannot independently approve their
    own work. Missing rights/privacy review prevents canonical eligibility;
    missing gold review leaves gold `draft`; missing scorer, gate, or governance
    approval fails applicable closure. Q10-Q15 determine the scoped downstream
    state rather than a blanket `provisional` or `invalid` label.

### 5.5 End-to-end and future handoff

26. Frozen topology. A benchmark-only renderer-neutral pre-render note artifact
    and authoritative rendered-note projection preserve comparable ordered
    structure, content, citation/locator references, and transformation
    lineage. Q26 exact schemas, enums, identity, ordering, citation/locator,
    lineage, and digest semantics are frozen in section 2.135. The separate
    immutable renderer-output/capture seam, durable deterministic HTML
    renderer, Q24 result/attempt schemas, durable ordering, and acyclic
    cross-binding are frozen in sections 2.139-2.140. Renderer loss remains
    End-to-end evidence; projection/comparison, alignment, and Q14 formulas
    remain pending under Q14.
27. Frozen topology. Parser, Generation, and End-to-end close independently.
    End-to-end separately evaluates final rendered-note quality against
    approved evidence and renderer preservation against the pre-render artifact.
    Q10-Q14 retain authority, blocker, metric, gate, and comparison ownership.
28. Frozen contract realization. An immutable
    pre-capture all-section plan, exactly-one primary assignment per source
    element, context-only overlap, separate per-work-unit output/receipt
    history, and a separate merge/coverage-closure artifact prevent silent
    omission or replacement without introducing retrieval. Q28's resolved
    ownership, exact schemas/enums, identity, order, DAG, closure, mapping,
    observation, final-note binding, and digest/revision rules are in section
    2.137. Remaining Q28 work is limited to the explicitly pending numeric,
    algorithm, measurement, and evidence boundaries.
29. Frozen topology. One versioned policy selects the generation mode from
    pre-generation artifact, structure, provider, and capacity facts. Formal
    route conformance is mandatory; forced modes remain preregistered diagnostic
    slots. Numeric routing boundaries, capacity compatibility, schema, and
    supporting evidence remain pending and separate from Q11 constants.

The Q1-Q29 foundation interview is complete at its stated contract and topology
boundaries. Fixture approval, evidence, schemas, metrics, numeric constants,
compatibility decisions, and implementation are not thereby complete.

## 6. Explicit non-decisions

This round does not:

- select or install an external parser, OCR, ASR, browser, renderer, or
  evaluation library; section 2.140 freezes a standard-library-only
  benchmark renderer contract but does not authorize a production renderer;
- establish pending metric-specific parser measurement formulas, measurement
  boundaries, or acceptance thresholds;
- establish a Q15 repeat count, scheduling block, seed policy, execution-
  compatibility rule, run-level pairing rule, diagnostic method, schema, or
  method parameter;
- establish Q16-Q21 schema or enum field names, execution-compatibility or
  equivalence rules, cold/warm policy, diagnostic resource method, retry detail
  beyond existing Q15 governance, platform-specific sandbox implementation, or
  Q11-owned numeric time, resource, or cost ceiling;
- establish Q26 projection/comparison rules, alignment algorithms, or Q14
  measurement formulas, comparison artifact schema, aggregation policy beyond
  the v1 `fixture_vector_only` realization, or numeric thresholds; Q14 metric,
  registry, scorer, aggregation, fixture-result, and cohort-result schema
  identifiers, fields, enums, identity, ordering, and digest rules are frozen
  in section 2.141; Q26 schema identifiers, fields, enums, identity,
  ordering, citation/locator, lineage, and digest semantics are frozen in
  section 2.135, and the renderer/capture plus Q24 result/attempt seam is
  frozen in sections 2.139-2.140;
- establish Q28 work-unit sizing, context-overlap amount, merge algorithm,
  contradiction-detection realization, measurement method, or numeric
  boundary;
- establish Q29 numeric routing boundaries, unsupported provider capacity,
  execution-compatibility treatment beyond existing ownership, schema, or
  evidence approval;
- approve any Q22 fixture candidate or assert that its bytes, digest,
  provenance, item-level rights/privacy evidence, or independent approval
  already exist;
- select an audio-quality or ASR-quality metric, or score either quality;
- establish broader formal collection/store publication semantics beyond the
  diagnostic End-to-end result/attempt package frozen in section 2.140;
- enable bootstrap, population inference, a confidence interval, p-value,
  statistical-significance claim, or formal statistical gate;
- approve any of the three candidate attachments;
- create fixtures, gold annotations, manifests, runners, tests, or baseline
  artifacts;
- modify runtime, production configuration, dependencies, tests, or public
  documentation;
- introduce retrieval, embeddings, relevance ranking, `top_k`, section
  selection, or any Step 100 behavior into long-source generation;
- make `NormalizedDocument`, gold, `SupplementProposalSchema`, or a Notion API
  schema own the renderer-neutral benchmark note artifact;
- decide Step 100 retrieval behavior;
- authorize a commit or push.
