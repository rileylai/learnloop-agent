# Daily Development Log

## Purpose
This file is a concise engineering log for recall.
It captures key implementation progress, decisions, blockers, and verification.

## Writing Rules (Daily Mode)
- Keep one entry per calendar date.
- For more work on the same date, append concise bullet points to that date entry.
- Do not create multiple sections with the same date.
- Keep notes short and high signal.
- Do not include secrets, raw private content, API keys, or long raw logs.

## Daily Entry Template
## YYYY-MM-DD (Short Topic)

### Highlights
- Main changes and outcomes.

### Issues and Decisions
- Problem -> decision/trade-off.

### Verification
- Commands run and key results.

### Next
- Next planned step.

## 2026-08-26 (P03/P04/S02 Baseline Artifact Repair)

### Highlights
- Regenerated only the active P03, P04, and S02 `revision-002` fixture bytes
  with the existing repository-controlled Noto/Pillow recipes.
- Rebound their external digests, normalized references, full-profile
  `revision-002`, and benchmark patch `parser-note-completeness/1.0.1`.
- Preserved all scoring-relevant `revision-001` bytes and the immutable
  `parser-note-completeness/1.0.0` identity.
- Added a C01-only real-artifact Generation/End-to-end Q14 scoring slice that
  persists candidate-specific claim maps, claim-to-gold mappings,
  applicability records, Q14 contracts, and four fixture metric results.
- Added a clearly draft/non-formal C01 gold artifact; no benchmark or adoption
  authority was created.

### Issues and Decisions
- The prior `revision-002` bytes were produced by a different Pillow/FreeType
  rendering environment; the source builders were already correctly bound to
  the controlled font and deterministic recipes.
- The repository security test passes in the real Git checkout; the earlier
  disposable-copy failure remains a verifier execution issue.
- Existing C01 persisted artifacts did not include gold, claim mappings,
  applicability, or Q14 result artifacts, so the new adapter derives and
  freezes only the smallest diagnostic inputs from the existing immutable
  Parser/Generation/End-to-end outputs.

### Verification
- Fixture reproduction tests: 3 passed; parser-note-completeness: 365 passed;
  full offline suite: 989 passed, 3 skipped.
- Security test, benchmark/profile/digest validation, compileall, targeted
  mypy, and `git diff --check` passed. No commit or push was performed.
- C01 real-artifact scoring tests: 5 passed; focused End-to-end/Q14 tests: 29
  passed; replay and mapping-digest fail-closed checks passed.

## 2026-08-25 (Deterministic P03/P04/S02 Fixture Rendering)

### Highlights
- Added the official Noto Sans CJK Traditional Chinese 2.004 Regular font as
  a benchmark-controlled asset with its SIL OFL 1.1 license and provenance.
- Added immutable `revision-002` fixture, governance, reference, and full-profile
  bindings for P03, P04, and S02; `revision-001` remains unchanged.
- Added independent benchmark-release manifests for
  `parser-note-completeness/1.0.0` and the required patch revision
  `parser-note-completeness/1.0.1`; the latter selects full-profile
  `revision-002` without rewriting the former.
- Builders now resolve the repository asset from their own location and reject
  missing or digest-mismatched font bytes before rendering.

### Issues and Decisions
- Replaced the host-controlled macOS Hiragino input while preserving the
  existing raster, mixed-modality, overlap, noise, skew, and content recipes.
- The current supported rendering contract remains locked Pillow 11.3.0 with
  the checked-in font; cross-platform FreeType identity remains unverified.

### Verification
- Focused fixture/profile tests and the offline suite pass (`984 passed, 3
  skipped`); no commit or push has been performed.

## 2026-08-19 (Q28 Exhaustive Long-Source Coverage Contract)

### Highlights
- Realized the Q28 foundation contract boundary in
  `dev_state/parser-note-completeness/02-benchmark-foundation.md`: pre-capture
  bindings, exhaustive source-unit inventory, exactly-one primary assignment,
  context-only overlap, per-work-unit history, closure completeness, final
  Q26 `pre_render_note` binding, neutral observations, and canonical digest/
  revision rules.
- Preserved ownership boundaries: Q29 routing, Q26 note schema, Q14
  measurement/scoring, Q15 run/retry/collection semantics, and Q10/Q12
  authority/contradiction effects were not redefined.
- Fixed Telegram review Accept queue reliability with a dedicated configurable
  timeout while retaining the generic webhook worker, callback acknowledgement
  separation, and visible change-request reconciliation boundary.

### Issues and Decisions
- Final-frozen Q28-D1–D8 and D11 using the selected exact schema, identity,
  assignment, overlap, DAG, attempt-binding, merge-order, closure, and inline
  mapping representations. D9, D10, and D12 remain compatible frozen
  boundaries; Q28 adds no receipt schema.
- Kept work-unit size, overlap amount, merge/truncation/contradiction numeric
  boundaries, provider capacity, Q14 formulas, and Q15 scheduling/retry policy
  pending under their owners.
- Q28 is ready to begin schema/validation implementation. Owner-dependent
  numeric, algorithm, measurement, and evidence contracts remain pending and
  must not receive invented defaults.
- Completed the owner-compatible Q15/Q17/Q21 per-work-unit receipt realization
  contract: Q17 owns the exact independent receipt artifact and durability,
  Q15 owns attempt/lifecycle/history semantics, and Q21 owns collection
  materialization. Existing slot-level runner receipts remain unchanged and
  cannot satisfy Q28 D6.
- Implemented `benchmark-generation-work-unit-attempt-receipt/1.0.0` as a
  separate immutable owner artifact with canonical bytes, external SHA-256,
  append-only history, and direct Q28 plan/work-unit/attempt/output bindings.
  Single-pass generation now emits a durable receipt and can close Q28 only
  after the receipt chain and Q26 final note validate.
- Resume retains failed owner attempts and appends the next per-work-unit
  ordinal; runner-slot ordinal remains a separate lineage field. Missing,
  mismatched, pending, synthetic, or broken-chain receipts fail closed.
- Froze the Q26/Q27 renderer/capture seam in foundation section 2.139:
  separate immutable renderer output and
  `benchmark-renderer-capture/1.0.0`, Q26-preserving projection parentage,
  End-to-end cross-artifact digest coherence, and no digest cycle.
- Resolved the remaining pre-D12 contract gaps in section 2.140: selected the
  standard-library-only `benchmark-deterministic-html-renderer/1.0.0` contract
  for deterministic HTML output and froze Q24
  `benchmark-end-to-end-result/1.0.0` plus
  `benchmark-end-to-end-attempt/1.0.0` packages.
- Implemented D12 deterministic End-to-end wiring: Parser and existing
  Generation artifacts feed the immutable HTML renderer, capture manifest,
  parsed Q26 projection, and Q24 result/attempt package. Existing runner
  start/terminal schemas remain unchanged; terminal `result_sha256` now binds
  the final End-to-end result for this lane.
- Kept Q26's `reference_document` boundary intact: Parser `parser_output`
  remains independently bound in the E2E package and is not relabeled as a
  Q26 reference artifact. Nested Generation owner receipts are discovered by
  a bounded Q15 history adapter, and Q15 work-unit ordinals are derived from
  durable receipt history rather than guessed from runner ordinals.

### Verification
- Focused renderer/E2E plus runner/generation tests: 29 passed; affected
  package: 327 passed; adjacent evals: 144 passed.
- Full offline repository suite: 947 passed, 3 skipped. Modified-package
  compileall passed. Scoped mypy reports only the repository's existing
  transitive diagnostics in runner/routing/parser/normalized-document and
  related modules; the new renderer and E2E modules add no remaining errors.
  `git diff --check` passed.
- Foundation consistency review confirmed the receipt DAG is acyclic and that
  `GenerationResult` currently has no `CoverageClosure` reference. Existing
  profile/reference fixture bytes and digests were not modified.
- Renderer and Q24 artifacts are now materialized only after durable parent,
  HTML, capture, projection, result, and attempt readback checks. Identity
  pass-through and outgoing-request-only capture remain rejected. Profile
  digests remain unchanged.
- Clarified section 2.140's empty-note lineage exception: a successfully
  rendered valid note with zero Q26 nodes may use
  `mapping_state=unavailable` with `mappings=[]` solely because no source or
  target nodes exist; non-empty deterministic projections remain provided
  one-to-one mappings.
- Froze Q14 exact scoring artifact realization in foundation section 2.141:
  metric/registry/scorer/aggregation contracts, fixture and cohort results,
  direct dependency digests, exact coverage/support vectors, and replay
  rules. Cohort v1 is `fixture_vector_only`; no macro, partial-credit scalar,
  support-ratio authority, or new Q10-Q15 binding schema was introduced.
- Documentation-only sanity checks passed for the Q14 identifiers, closed
  enums, canonical ordering, replay matrix, and acyclic digest DAG;
  `git diff --check` passed and no runtime, test, fixture, profile, or ADR
  files were changed.
- Corrected Q14 section 2.141 support ownership: coverage remains over
  `expected_claim`, support now requires `generated_claim`, and support
  denominator/count validation is explicitly generated-claim-only with no
  expected/generated ID mixing. Parser metric extension remains a future
  versioned Q14 schema revision.
- Removed the remaining support importance strata: support is now one
  fixture-level generated-claim vector. Q14 §2.103 strata are explicitly
  coverage-only; generated claims are never assigned or duplicated by linked
  expected-claim importance.
- Closed the final Q14 §2.141 boundaries: realized 1.0.0 contracts are
  Generation/End-to-end only, Parser lanes are invalid until a versioned
  future Q14 schema revision, and support has no candidate exclusion field;
  authoritative and applicable generated-claim IDs must be identical.
- Focused review queue/config/recovery regressions passed (`20 passed`),
  including ordinary/review/full-index timeout selection, neutral queue-timeout
  classification, pending-state recovery, and no duplicate enqueue.
- Affected package and adjacent tests passed (`222 passed`); the full offline
  suite passed (`953 passed, 3 skipped, 1 existing LibreSSL warning`). The
  requested compileall and `git diff --check` checks passed.

### Next
- Keep provider retry counts, backoff, timeout, scheduling, repeat/collection
  policy, Q14 scoring, and Q28 sizing/overlap/merge policy pending under their
  existing owners.
- Review before any later commit; the requested implementation-phase message
  remains `feat(eval): add deterministic end-to-end renderer pipeline`.

## 2026-08-20 (Q14 Deterministic Scoring Foundation)

### Highlights
- Implemented the frozen Q14 v1 Generation/End-to-end metric contract,
  registry, scorer, aggregation, fixture-result, and cohort-result schema
  families in `tests/evals/parser_note_completeness/q14_scoring.py`.
- Added exact coverage state vectors by expected-claim importance stratum and
  generated-claim-only support state vectors with unresolved audit and
  diagnostic-only rational rates.

### Issues and Decisions
- Parser lane remains rejected in Q14 v1; no parser formula or source-side
  scoring unit was introduced.
- Support results have no importance strata or exclusion field. Authoritative
  and applicable generated-claim IDs must match, and five decided states plus
  unresolved audit must partition the complete set.
- Restored the Q8 unresolved state spelling to `unresolved`; Q14 retains
  `unresolved_audit` only as the result field. Fixture/cohort validation now
  binds benchmark revision to the selected metric registry and revalidates
  derived IDs after copy/update paths.
- Narrowed fixture/cohort derived IDs to the exact §2.141 dependency seed
  fields, excluding envelope-only fields. Canonicalization and binding
  validation now centrally revalidate every Q14 model, including mutated
  `model_copy(update=...)` instances, before bytes or SHA-256 are authoritative.
- Public Q14 validation helpers now use the same exact-schema revalidation
  path for existing model instances. Named canonical/SHA helpers enforce their
  artifact type while generic Q14 canonicalization remains six-schema capable.

### Verification
- Focused Q14 tests: 21 passed.
- Parser-note-completeness package: 350 passed; adjacent evals: 494 passed;
  full offline suite: 972 passed, 3 skipped, 1 existing LibreSSL warning.
- Compileall, scoped Q14 mypy, and `git diff --check` passed.
- The new Q14 module has no scoped mypy diagnostics; repository baseline still
  contains existing diagnostics in unrelated modules.

## 2026-08-12 (Step 98 Closure and Step 99 Hybrid Evaluation)

### Highlights
- Completed the documentation-only Parser & Note Completeness Discovery across
  PDF, URL, YouTube, chat text, and screenshot ingestion. The report traces the
  flat-source single-call proposal flow, ranks evidence-backed loss points,
  compares maintained local-first parser candidates, and defines a fixed
  13-sample benchmark plus generation-flow gates.
- Recorded explicit approval for the single bounded `step98-exp-002` Phase B
  capture and completed the no-network capture-contract preflight.
- Revalidated manifest digest
  `45e5073bd78255717b694486ede2f23827c13ab11b8839081ccfef54c2795526`
  and request-plan digest
  `07d919b07e91f7857f4fb24632ca075324ded40b3c4ccb119519d74a79701bfc`.
- Confirmed 15 logical requests, 396 inputs, `text-embedding-3-small`, 1536
  dimensions, a 217,806-token conservative bound, and a USD 0.00435612 cost
  bound under the frozen budgets.
- Confirmed Docker Compose PostgreSQL was healthy on the configured host port;
  the prior refusal occurred while the existing container was not accepting
  host connections. The existing restart policy restored it without rebuild.
- Completed the sole Phase B capture: 15 attempts, zero retries, 46,986
  provider tokens, USD 0.00093972 estimated cost, and a complete vector bundle.
- Ran Phase C and preserved its first canonical `no_adoption` artifact, then
  closed Step 98 `inconclusive` after required replay and pgvector gates failed.
- Preregistered Step 99 before scoring and reused only the complete Step 98
  body-only capture: 18 pages, 108 chunks, 72 queries, and no new embeddings.
- Completed `step99-exp-003`; tuning selected weighted RRF vector `0.65` /
  keyword `0.35`, and a separate replay reproduced the canonical result digest.
- Closed Step 99 as `maintain_vector_primary` and added ADR-0008. Production
  remains exact body-only with vector-primary retrieval and lexical fallback.
- Completed the final closure audit: clarified keyword-only's comparison-only
  role, invalid-to-qrel terminology, and the absence of production-scale
  keyword/hybrid evidence without changing frozen or canonical artifacts.
- Guarded the formal replay tests for clean checkouts: they run when all ignored
  local evidence exists and skip explicitly when that evidence is unavailable.

### Issues and Decisions
- Confirmed proposal generation does not use QA top-k or source chunks: it sends
  the whole persisted source in one 1,400-token-output call, while the schema
  caps notes at 12. Recommended a combined section-aware generation redesign
  and benchmark-gated parser improvements; no library was selected or installed.
- The required disposable pgvector admin target was not configured, and the
  configured local PostgreSQL endpoint refused the preflight connection.
- Stopped before the first live embedding request as required. No provider,
  Notion, Telegram, production index, or database mutation occurred.
- The later full preflight passed with application/maintenance database
  separation, matching server identity, pgvector availability, and disposable
  database privilege. No secret or connection string was recorded.
- The frozen pgvector fixture seeds `page-a` and `page-b`, while the frozen
  production repository excludes both known synthetic ids. Two filter/top-k
  cases failed and one source-kind exclusion case passed; all disposable
  databases were cleaned up.
- Same-contract Phase C replay reported `non_deterministic_result`: the result
  digest matched, but canonical JSON lists were compared with in-memory tuples.
  The frozen harness was not modified or bypassed.
- Step 99 exp-001 stopped before scoring on disposable fixture seed order;
  exp-002 stopped before scoring on the inherited vector-digest algorithm.
  Both aborts were preserved, and corrected contracts received new ids.
- Formal Step 99 weighted RRF gained 4 Hit@3 queries with 0 losses, but its
  reciprocal-rank sum improved only `+2.666666666666` against the frozen
  `+2.700` gate. The decision was therefore `maintain_vector_primary`.

### Verification
- Parser discovery used a current five-image public-safe fixture and a real
  schema probe; 13 grounded notes were deterministically rejected by the
  current 12-note maximum. `git diff --check` passed. No runtime, test,
  dependency, production configuration, external provider, or Notion change
  was made.
- Phase A same-digest validation: passed.
- Phase B frozen-plan validation and full in-memory input/budget preflight:
  passed.
- Disposable PostgreSQL target connectivity: blocked before database creation;
  external embedding attempts remained `0` and no Step 98 artifact was created.
- Repeated Phase A/plan/budget/isolation preflight: passed without digest or
  budget drift and with zero external attempts before capture.
- Phase B capture: passed; 15/15 requests, zero retries, complete artifacts.
- First Phase C scoring completed; both candidates failed frozen quality and
  decision-set citation gates. Independent citation/golden and deterministic
  repository safety gates passed.
- Disposable pgvector adapter: two failed, one passed; cleanup passed with zero
  remaining `learnloop_step98_*` databases.
- Same-contract Phase C replay: failed closed as `non_deterministic_result`.
- Focused deterministic closure suite: 50 passed; `git diff --check` passed.
- Step 99 citation, repository safety, disposable pgvector, and replay gates:
  passed. Disposable database cleanup left zero `learnloop_step99_*` databases.
- Step 99 focused evaluation/citation/safety tests: 36 passed.
- Full deterministic suite: 620 passed, 3 skipped, 1 existing LibreSSL warning.
- Separate CLI replay, compileall with a sandbox-safe bytecode cache, and
  `git diff --check`: passed.
- Final closure verification repeated the full suite (`620 passed, 3 skipped,
  1 existing LibreSSL warning`), compileall, scope review, and diff check.

### Next
- Keep production exact body-only and vector-primary. Step 100 remains deferred
  and is not authorized by the Step 99 result.

## 2026-08-07 (Telegram Full-index Queue Reliability)

### Highlights
- Confirmed the root cause: the generic Telegram RQ job used RQ 2.8.0's
  implicit 180-second execution bound while `/index-full` was still reading
  the first large page.
- The isolated read evidence was 366 Notion HTTP requests in 317.457 seconds;
  all responses were HTTP 200 and there were zero retries.
- Completed the explicit ordinary timeout of 180 seconds and dedicated
  full-index timeout of 10800 seconds, durable workflow reuse, and the module-
  level `process_telegram_full_index_job` with no automatic retry.
- Preserved page-level atomic replacement and existing Notion retry semantics.

### Issues and Decisions
- `JobTimeoutException` inherits from `Exception` and was previously swallowed
  by the Notion adapter as `NOTION_BLOCK_FETCH_FAILED`.
- RQ-specific timeout handling now crosses the composition boundary as a
  neutral infrastructure failure; the durable workflow reason is the safe,
  content-free `QUEUE_JOB_TIMEOUT`.
- The 10800-second value is a configurable deployment safety bound, not a
  latency SLA. Live full-index verification was not run, and the 98 retrieval
  experiment remains paused pending explicit continuation.

### Verification
- Targeted deterministic suite: 78 passed.
- Full deterministic suite: 613 passed, 3 skipped.
- `python -m compileall src tests`: passed.
- Deterministic preflight: pass, 27 passes, 9 expected warnings, 0 failures.
- `git diff --check`: passed.
- No live Notion/OpenAI/Telegram calls, SQL mutation, or Redis cleanup.

### Next
- Keep live `/index-full` as a separately approved guarded post-closure
  verification. Keep the 98 retrieval experiment paused until explicitly
  resumed.

## 2026-08-06 (Large-page Reliability Roadmap Amendment)

### Highlights
- Added Large-page Indexing Reliability Steps 96-97 and deferred Retrieval
  Optimization Steps 98-100; moved the roadmap pointer to Step 96.
- Added the Step 98 `ready-for-agent` implementation spec for a three-variant,
  deterministic context-aware embedding-input experiment. Production remains
  body-only; no runtime code, database state, or index was changed.
- Revised the Step 98 spec to `review-required` after grill review. Added
  mechanically validated preregistration/capture/evaluation phases, exact
  denominators and integer gates, and independent citation and production
  repository safety evidence. Step 98 remains `todo`.
- Applied the final minimal Step 98 spec revision: the first create-if-absent
  `manifest.sha256` receipt now freezes the experiment immediately; ambiguity
  metrics use one complete-ranking formula and paired query-id sets. Added
  same-contract deterministic replay and an exact mutually exclusive length
  partition. Step 98 remains `todo` and `review-required`.
- Added the executable Step 96 failure-diagnostics spec with safe typed error,
  observability, deterministic matrix, bounded live matrix, acceptance, and
  documentation requirements.
- Recorded parent-child retrieval as a separate non-executable future candidate.
- Implemented typed, sanitized Notion and embedding HTTP/transport diagnostics,
  versioned embedding request-shape estimates, and local empty-input validation.
- Added a triple-gated, read-only Step 96 live diagnostic command with
  sequential single/small/progressively bounded cases, explicit request and
  size budgets, a diagnostic-only 30-second read timeout, and no persistence,
  retry, or production batching.
- Added deterministic Phase A shape-only support that reads/chunks the approved
  page without an embedding client and reports only full-request distribution
  metrics and a safe largest-input ordinal.
- Completed Step 96 and moved the roadmap pointer to Step 97 (`todo`) without
  starting Step 97 implementation.
- Added the Step 97 `ready-for-agent` implementation spec and accepted
  ADR-0006 for bounded, sequential, all-or-nothing indexing-time embedding
  execution. No runtime code was changed.
- Implemented Step 97 configurable Notion read timeout/retry, reviewed OpenAI
  capability profile, bounded sequential embedding execution, response-index
  validation, aggregate usage/cost handling, and complete-result-only page
  replacement.
- Added a triple-gated, target-scoped Step 97 live verification harness. Its
  default path makes zero external requests; the live path reuses one captured
  Notion snapshot, preflights worst-case request/token budgets, and discloses
  that it replaces the selected page's local derived snapshot.
- Closed Step 97 after the separately approved bounded single-page live
  dependency verification passed; moved the roadmap pointer to Step 98
  (`todo`) without starting its implementation.
- Implemented the deterministic portion of Step 98: preregistration and
  manifest validation, versioned contextual-input builders, frozen fixture
  validation, bounded capture planning/artifact checks, deterministic ranking,
  gate and replay logic, independent citation projection, and production
  repository safety regressions.
- Froze `step98-exp-001` at manifest digest
  `60ce9c5375f2e7aa480c560ab6f50d0ea94dacc783e1364ee5e2a405dafa8577`.
  The fixture contains exactly 18 pages, 108 chunks, 72 unique queries, and
  144 query/hard-negative pairs. Step 98 is `doing` pending approved Phase B.
- Preserved `step98-exp-001` without modification as
  `aborted_pre_capture_contract_gap`: external request attempts were `0`, no
  canonical capture artifact was created, and its frozen harness could not
  mechanically guarantee the approved capture contract.
- Created and first-write froze `step98-exp-002` at canonical manifest digest
  `45e5073bd78255717b694486ede2f23827c13ab11b8839081ccfef54c2795526`.
  It reuses the exact source/chunk/query/label/gate decision set, has request-plan
  digest `07d919b07e91f7857f4fb24632ca075324ded40b3c4ccb119519d74a79701bfc`,
  and does not replace exp-001 evidence.
- Added the exp-002 global 16-attempt pre-call budget, atomic immutable capture
  directory and safe failure receipt contract, full preflight, provenance-rich
  success metadata, deterministic citation/repository gates, guarded disposable
  pgvector evidence, and a default-offline Phase C artifact CLI. No live capture
  or canonical Phase C result was run.

### Issues and Decisions
- Step 98 freezes body-only as the exact current `chunk_text` input and compares
  title/body and title/nearest-heading/body through one isolated retrieval
  seam. Adoption requires predeclared metric gains with zero citation, golden,
  production-RAG exclusion, or scope regressions; a failed or inconclusive gate
  closes the step without adoption.
- A passing Step 98 result identifies only an ADR candidate. Production wiring,
  persistence provenance, rollback, and re-index/backfill require a new ADR and
  a separate rollout step. Any real embedding capture requires explicit bounded
  approval and public-safe fixtures.
- The original Step 98 gate is fixed at 72 unique queries across nine mutually
  exclusive intent/language cells. Phase B and C must validate the tracked
  Phase A manifest digest; any managed change or cross-session vector mix makes
  the gate invalid or inconclusive rather than tunable.
- Phase A now permits only first-write receipt creation or same-digest
  idempotent validation. All ambiguity regressions are paired by identical
  query ids; aggregate counts alone cannot satisfy the gate.
- The frozen capture plan has 15 sequential requests: three query batches
  generated once, followed by twelve interleaved document batches across the
  three variants. The plan digest is
  `0329ef70e6d8db9a91d6376027a105b8bad50c6bfa4f6d8f884ef5d6abf04899`.
- The replacement exp-002 plan retains the same 15 logical requests and frozen
  schedule but uses its own request-plan digest
  `07d919b07e91f7857f4fb24632ca075324ded40b3c4ccb119519d74a79701bfc`.
  A capture run gets at most 16 global external attempt slots, persisted before
  each provider call; failure consumes the experiment's sole capture session.
- No Step 98 quality/adoption outcome exists before Phase B vectors. The
  deterministic scorer, vetoes, result digest, and replay checks are ready;
  production remains exact body-only. PostgreSQL/pgvector adapter integration
  remains a separate adoption gate after an approved capture.
- The production-equivalent request contained 2,483 inputs, exceeding the
  documented 2,048-input request limit. This is the supported primary root
  cause of the original HTTP 400. The original provider error body was not
  captured, so there is no direct provider error-code confirmation.
- Embedding batch concurrency is fixed at `1` for Step 97. Context-aware input
  and hybrid retrieval remain eval/ADR gated.
- The existing uncommitted hardcoded 30-second Notion timeout diagnostic was
  preserved during implementation and converted into the documented runtime
  setting.
- The user-executed guarded matrix passed 1, 4, 8, 16, 32, and 64 inputs. The
  largest request was 24,916 bytes / 6,254 estimated tokens; no provider error
  category or failure boundary appeared in that matrix.
- Phase A measured 2,483 inputs, zero empty inputs, 886,852 bytes, and 222,642
  estimated tokens; the token value is not the diagnosed cause. Phase B was
  cancelled as unnecessary.
- HTTP status takes precedence over allowlisted provider-category refinement
  except for generic HTTP 400; unsafe exception causes are suppressed, and
  budget exhaustion is inconclusive with a nonzero exit.
- Step 97 ownership is locked: the provider adapter performs one classified
  request and exposes reviewed model capability, `EmbeddingBatchService` owns
  planning/retry/validation/reassembly, and the orchestrator owns the complete
  prepared-snapshot and replacement gate.
- Provider profiles supply hard ceilings; settings may only narrow them.
  Planning uses stable contiguous batches with concurrency fixed at `1`, and
  missing provider usage keeps page cost unknown rather than undercounted.
- A conservative versioned estimator is used for operational token gating
  without runtime tokenizer downloads. Provider-reported usage remains the
  only billing/cost source, and any retry keeps usage/cost unknown because the
  failed attempt's consumption cannot be recovered safely.
- The Step 97 live run's 707,454-token conservative planning estimate is
  operational gating metadata, not actual usage. OpenAI separately reported
  289,651 input tokens, which is the value used for the cost estimate.

### Verification
- Step 98 specification authoring performed no runtime change, external
  request, database mutation, Notion read/write, Telegram send, or re-index.
- The grill-review revision likewise changed documentation only. No experiment
  code, embedding capture, PostgreSQL adapter gate, production re-index, or Step
  99 work was started.
- The final focused revision also changed documentation only; it did not create
  a preregistration receipt or canonical experiment artifact.
- Inspected the pre-existing git diff before documentation changes.
- `git diff --check` passed; roadmap/spec structure and required sections were
  checked with targeted searches.
- Focused provider, Notion adapter, tool, diagnostic, index atomicity, QA, and
  supplement regressions passed (`104 passed`); review-fix tests passed
  (`37 passed`).
- The default diagnostic guard returned `skipped` with zero live cases.
- User-provided live-dependency evidence recorded the passing matrix through
  64 inputs; no private content, page identity, payload, or raw error was added
  to repository evidence.
- Phase A focused shape, provider, Notion adapter/tool, and page-index
  atomicity regressions passed (`83 passed`); compileall and `git diff --check`
  passed. The default `--shape-only` guard returned `skipped` with no live read.
- Standards and spec reviews passed after resolving exception-chain, status
  precedence, diagnostic-budget, 30-second traversal, and diagnosis-state
  findings.
- Step 96 closure standards/spec reviews passed after reconciling historical
  adapter wording and the documented-hard-contract evidence path.
- Step 97 focused service, adapter, configuration, transaction, full-index,
  legacy-fake, and guarded-harness regressions passed. First/middle/last and
  new-page batch failures opened no replacement transaction; successful
  multi-batch execution used one replacement transaction.
- The first full-suite attempt exposed legacy deterministic embedding fakes
  missing the new capability/index contract. After updating those fakes, the
  affected regression set passed (`47 passed`) and the full deterministic suite
  passed (`556 passed, 3 skipped, 1 existing LibreSSL warning`).
- User-provided bounded live dependency evidence passed: 2,483 inputs in five
  sequential batches (`512/512/512/512/435`), zero retries, 16,573 indexed
  blocks, 2,483 chunks, 2,483 vectors, and one committed page replacement.
  Duration was 102.9 seconds and provider-reported usage produced the recorded
  USD 0.00579302 estimated cost. No full index was run.
- The final full deterministic suite passed (`498 passed, 3 skipped`); the
  skips remain opt-in live PostgreSQL tests. One existing LibreSSL warning was
  emitted by `urllib3` during the adapter smoke fixture.
- This implementation session performed no external request, Notion write,
  live embedding call, database mutation, Telegram send, or full-index run.
- Step 97 spec/ADR documentation consistency checks and `git diff --check`
  passed; spec authoring performed no test-network request or runtime change.
- Step 98 focused verification passed (`28 passed`); the final full
  deterministic suite passed (`584 passed, 3 skipped, 1 existing LibreSSL
  warning`). The independent repository safety matrix contributed 10 passing
  pending/rejected/non-Notion/wrong-page/wrong-section cases, and citation
  projection covered 8 passing cases.
- Step 98 Phase A first-write freeze and same-digest validation passed; Phase B
  planning returned 15 requests and the expected request-plan digest. The
  live-capture command's default guard returned `skipped` with zero external
  requests. Compileall passed with a temporary pycache prefix.
- Exp-002 focused verification passed (`46 passed, 3 skipped`); the full
  deterministic suite passed (`606 passed, 3 skipped, 1 existing LibreSSL
  warning`). Compileall and `git diff --check` passed. Phase A same-digest
  validation and Phase B planning passed after freeze; Phase B and disposable
  pgvector default guards reported zero external/DB operations and created no
  artifact. Focused standards/spec reviews found no remaining P1 blocker.
- One earlier full-suite attempt hit a transient local process-fork resource
  failure in an existing security subprocess test. That test passed alone and
  the final full suite passed without a test failure.
- The final documentation-state run also observed one transient failure in the
  existing SQLite concurrent idempotency ownership test. The test passed alone,
  and the immediate full-suite rerun passed (`584 passed, 3 skipped`). No
  unrelated idempotency code was changed.

### Next
- Request explicit approval for the bounded `step98-exp-002` Phase B capture.
  Until
  approved, do not call the provider, change the production database, re-index,
  decide adoption, or begin Step 99.

## 2026-08-01 (Repository-Evidence Documentation Audit — Completed)

### Highlights
- Audited `docs/` against current runtime wiring, SQLAlchemy models, Alembic
  head, tests, eval scripts, runbooks, and recorded Step 82/83/87 canaries.
- Replaced the idealized database design with the actual nine-table schema and
  documented the current Route/Orchestrator/Provider/Tool/Queue/Repository
  boundaries, memory ownership, concurrency protections, and append/re-index
  transaction boundary.
- Corrected Telegram, RAG, ingestion, API, observability, and deployment status;
  added a shared verification vocabulary and kept deterministic, adapter,
  bounded live dependency, and live E2E evidence separate.
- Updated evaluation and recovery documentation, including the dry-run-first
  committed Telegram preview recovery path. No production code, test,
  migration, schema, prompt, or roadmap file was changed.

### Issues and Decisions
- Step 82/83/87 remain bounded historical live evidence, not general release or
  production-workspace proof. Step 88 remains `doing`; the complete Telegram
  live E2E is still missing.
- Current OCR preflight and the real Tesseract fixture now pass with `eng`,
  `chi_tra`, and `chi_sim`, superseding the older host-dependency observation.
  A real user-screenshot/Telegram live retest is still not verified.
- The `audit_logs` table exists but has no current runtime write path;
  `workflow_runs`, safe metadata, metrics, and structured logs are the active
  observability path.

### Verification
- Test and OCR preflight profiles: passed; live Redis, OpenAI, Telegram, auth,
  and cost settings remained unconfigured warnings in the test profile.
- Deterministic evals: golden set loaded; retrieval hit rate `3/3`; citation
  accuracy `3/3`; vector, write-safety, manual-sync, and prompt-injection evals
  all passed.
- Adapter smoke matrix: PDF, OCR, and URL fixtures passed; YouTube, OpenAI,
  PostgreSQL, and Telegram live checks skipped because live mode was disabled.
- Full suite: `399 passed, 3 skipped`, with the three opt-in live PostgreSQL
  tests skipped and one local LibreSSL compatibility warning.

### Next
- Continue Step 88 only with the guarded live resources and explicit release
  procedure. Do not mark it done until the full live E2E criteria pass.

## 2026-08-02 (Telegram Notion Hierarchy UI — Deterministic Verification)

### Highlights
- Audited the live runtime path from Notion reader payloads through indexing,
  `notion_pages`, Telegram `/pages`, upload callbacks, and Change Target.
- Added nullable canonical `parent_notion_page_id` persistence and Alembic
  revision `9c5e7b1a2d4f`; the unique external `notion_page_id` identity is
  unchanged.
- Added deterministic tree construction with safe roots, cycle protection,
  stable ordering, duplicate-title breadcrumbs, bounded `/pages` messages, and
  one progressive picker shared by upload and Change Target.
- Navigation callbacks remain opaque `ll:<token>` mappings and are side-effect
  free; final selection alone enters the existing target claim and proposal
  workflow.

### Issues and Decisions
- The live Notion reader already exposes real page parents only for
  `parent.type=page_id`; workspace, database, block, and unknown parents are
  persisted as `NULL` and therefore safe roots. Titles and paths are never used
  to infer parentage.
- Live Telegram send, Redis cleanup, Notion writes, Accept, and SQL data
  mutations were not run. Step 88 remains `doing` pending user restart and
  human live verification.

### Verification
- Focused hierarchy, reader, repository, migration, indexing, and Telegram UX
  tests passed (`61 passed` in the final focused command).
- Full deterministic suite passed (`411 passed, 3 skipped`); compileall,
  Alembic head/history inspection, and `git diff --check` passed. The only
  warning was the existing macOS LibreSSL/urllib3 warning.

### Next
- Restart the API/worker and perform the separately approved live Telegram
  hierarchy/picker retest; do not mark Step 88 done before it passes.

### UI Feedback Follow-up (2026-08-02)

- Removed `notion_path` from `/pages` presentation while retaining canonical
  ids, numbering, deterministic ordering, and database/runtime paths.
- Fixed cumulative tree indentation/connectors for three-level hierarchy.
- Removed new picker pagination and page indicators. Every picker level now
  renders all direct children; old pagination callback mappings remain
  TTL-bound compatibility inputs and do not produce new pagination buttons.
- No schema, Notion persistence, OCR, LLM, proposal, review, append, RAG, or
  transaction behavior changed.
- Final focused UI/navigation suite passed (`30 passed`); full deterministic
  suite passed (`413 passed, 3 skipped`). Compileall and `git diff --check`
  also passed; only the existing macOS LibreSSL/urllib3 warning remained.

### Screenshot Proposal Contract Follow-up (2026-08-02)

### Highlights
- Changed screenshot summary sentence count from a hard 1–2 rejection to a
  soft 2–4 generation preference; sentence splitting still validates every
  grounding unit, while schema/field/total text bounds remain hard limits.
- Added source-anchored title repair/fallback eligibility for matched source
  anchors after `UNMATCHED_PRODUCT_NAME`; unmatched products, identifiers,
  numbers, and insufficient anchors still fail closed.
- Added bounded note quality checks: 1–12 notes, normalized concept coverage,
  duplicate detection, and a small concept-tied enterprise/backend context
  vocabulary. Added a public-safe four-image SQL fixture covering Index,
  EXPLAIN, query rewrite, pagination, and title recovery.
- Bumped the active proposal prompt to `supplement_proposal_v7` and versioned
  screenshot title/summary/body repair prompts. Telegram notes now use bounded
  bullets; Notion notes render as separate append-only blocks while preserving
  fixed labels and durable identity.

### Issues and Decisions
- The live fallback was false because the orchestrator only admitted
  `INSUFFICIENT_MATCHED_ANCHORS` with no unmatched high-specificity anchor;
  `UNMATCHED_PRODUCT_NAME` therefore skipped the deterministic source-only
  fallback even when matched source anchors were sufficient.
- The repair order remains bounded: full proposal, at most one title repair and
  eligible fallback, then at most one summary or body repair. Sentence count
  alone never starts an LLM call. No OCR, hierarchy, routing, append policy,
  RAG, transaction, or retry identity behavior was changed.

### Verification
- Focused schema, screenshot eval/contract, prompt, supplement API, Notion
  writer, Telegram preview/recovery/retry/UX tests passed (`113 passed`).
  Preview bullet and bounded truncation tests were added.
- Compile checks and `git diff --check` are pending the final deterministic
- Full deterministic suite passed (`424 passed, 3 skipped`) with the existing
  LibreSSL warning. `compileall`, `git diff --check`, and Alembic heads check
  passed; no live Telegram send, Notion write, Accept, SQL mutation, Redis
  cleanup, or live retry was run.

### Source Schema Ownership Follow-up

### Highlights
- Separated provider-generated proposal content from the final business
  proposal schema. The backend now builds `source` from persisted
  SourceDocument state and derives target fields before final validation.
- Added a public-safe seven-attachment regression fixture for legacy
  display-string `source` output and corrected the active title repair
  filename/version wiring drift.

### Issues and Decisions
- Legacy `source`, target, and citation keys are explicitly dropped only at
  the provider boundary; arbitrary unknown keys remain strict failures. No
  source display string is parsed into identity, and repair scopes cannot
  mutate source or target.
- The live source schema failure occurred before grounding/repair because the
  old prompt asked the provider to return final-schema `source`. Retry source
  reuse remains unchanged.

### Verification
- Focused provider schema, supplement API, prompt-loader, and source ownership
  tests passed after implementation. Full deterministic verification remains
  the next step; no live provider, Telegram, Notion, SQL, or Redis operation
  was run.

### Step 88 Completion Confirmation (2026-08-02)

#### Highlights
- The user explicitly confirmed that the guarded Telegram live E2E flow was
  completed, so Step 88 is now recorded as `done`.
- Historical Step 88 entries above remain unchanged; their earlier
  "等待 live retest" statements describe the state at those points in time.
- Added the next `Telegram Operations + Knowledge Maintenance` phase with
  Steps 89–95, all initially `todo`, and moved the Current Pointer to Step 89.

#### Issues and Decisions
- This documentation record contains no workflow identifiers, credentials,
  private content, cost, latency, test-count, or release-report figures.
- Step 88 completion is bounded guarded live evidence and does not claim cloud
  deployment, always-on Notion sync, live restore, or production-wide
  readiness.

#### Verification
- Documentation-only update; no Telegram send, OpenAI call, Notion read/write,
  indexing, Accept, SQL mutation, Redis cleanup, or other external operation
  was performed.

## 2026-08-03 (Telegram Operator Command Contracts — Completed)

### Highlights
- Completed Step 89 by defining the Telegram operator contract for `/sync`,
  `/index-full`, `/index-status`, `/cost`, `/pending`, `/workflow`, `/status`,
  `/stats`, and updated `/help`.
- Added typed server-side callback families, exact chat/user ownership,
  confirmation gates, bounded safe output, duplicate handling, and the
  `API Route -> Orchestrator -> Service / Tool / Repository` plus
  `QueueClient` boundaries in `docs/11-telegram-operator-contract.md`.
- Cross-referenced the contract in the design, workflow, guardrail,
  observability, and API contract docs. No external operation was added in
  this contract-only portion; Step 90 implementation is recorded below.

### Issues and Decisions
- `/sync` and `/index-full` are derived-index mutations only; they never write
  Notion. `/index-full` requires an opaque confirmation callback and `/sync`
  requires final selection confirmation.
- Operator callbacks use a distinct server-side `operator` family so they
  cannot fall through to existing upload picker or proposal review branches.
- Unknown cost remains `unknown`; operator output excludes raw source/OCR,
  prompts, embeddings, tokens, secrets, raw exceptions, and private metadata.

### Verification
- Full deterministic suite: `435 passed, 3 skipped`.
- `python -m compileall -q src tests`: passed.
- `git diff --check`: passed.
- Documentation contract keyword check: passed.

### Next
- Execute Step 90: add selected-page `/sync` discovery, bounded hierarchy
  selection, and partial-failure-safe incremental indexing.

### Step 90 Follow-up

#### Highlights
- Implemented Telegram `/sync` as a live Notion page-discovery and bounded
  parent/child multi-select flow with explicit `sync_confirm` confirmation.
- Added TTL-bound chat/user-owned sync sessions and opaque operator callbacks;
  only the new operator callback family uses one-shot atomic claims, preserving
  existing upload/review callback compatibility.
- Reused `NotionIncrementalIndexOrchestrator` and page-level replacement so
  selected pages are derived-index-only and earlier commits survive a later
  page failure.

#### Issues and Decisions
- The Telegram outer workflow reports only sync status and bounded counts;
  canonical page ids remain in server-side session/callback mappings and the
  existing child indexing workflow metadata.
- `/sync` discovers pages through `ToolRegistry` and the read-only Notion
  reader; it never invokes the Notion writer or edits `AI Supplement Zone`.

#### Verification
- Focused Step 90 regression suite: `48 passed`.
- Full deterministic suite: `437 passed, 3 skipped, 1 warning`.
- `python -m compileall -q src tests`: passed.
- `git diff --check`: passed.

### Next
- Execute Step 91: add guarded `/index-full` and `/index-status`.

### Step 91 Follow-up

#### Highlights
- Implemented a guarded `/index-full` warning flow with TTL-bound,
  chat/user-owned sessions and opaque `index_full_confirm`/
  `index_full_cancel` callbacks.
- Reused `NotionFullIndexOrchestrator` for the confirmed full derived-index
  run; cancel, expired, duplicate, and cross-user callbacks do not start work.
- Added read-only `/index-status [workflow_id]` using persisted workflow
  observability, with bounded counts, stale state, deterministic failure, and
  known-or-unknown embedding cost output.

#### Issues and Decisions
- `/index-status` never invokes Notion discovery, embeddings, or indexing; it
  filters workflow metadata to safe page counts and status fields.
- Full-index warning and callback state is ephemeral; indexing workflow and
  page-level derived-index commits remain durable. No Notion writer path was
  added.

#### Verification
- Focused Step 91 regression suite: `44 passed`.
- Full deterministic suite: `439 passed, 3 skipped, 1 warning`.
- `python -m compileall -q src tests`: passed.
- `git diff --check`: passed.

### Next
- Execute Step 92: add `/cost` and `/workflow`.

### Step 92 Follow-up

#### Highlights
- Implemented Telegram `/cost` with bounded `today`, rolling `7d`, calendar
  `month`, and `workflow <workflow_id>` scopes.
- Extended backend cost aggregation to separate recorded LLM/proposal/QA and
  embedding/indexing costs, preserve unknown pricing, and report daily/workflow
  budget state without inferring costs from token counts or workflow type.
- Implemented read-only `/workflow` recent summaries and requested workflow
  detail through a fixed safe metadata allowlist; no rerun or reconciliation
  controls were added.

#### Issues and Decisions
- `/workflow` without an id is bounded to five recent persisted rows. With an
  id it returns only safe status, age, stale state, failure reason, operation,
  bounded counts, and known or `unknown` recorded cost.
- `/cost` and `/workflow` never call Notion, providers, Redis directly, or
  expose prompts, OCR/source text, secrets, raw exceptions, page ids, or
  private metadata.

#### Verification
- Focused Step 92 operator/observability suite: `45 passed`.
- Full deterministic suite: `441 passed, 3 skipped, 1 warning`.
- `python -m compileall -q src tests`: passed.
- `git diff --check`: passed.

### Next
- Execute Step 93: add `/pending` review inbox.

### Step 93 Follow-up

#### Highlights
- Implemented Telegram `/pending` with a bounded PostgreSQL-backed inbox that
  renders safe proposal title/summary, source display name, and current target
  path fields.
- Added opaque one-shot `pending_view` operator callbacks. View is read-only;
  Accept, Reject, and Change target reuse the existing review callback family
  and `SupplementReviewOrchestrator`.
- Preserved targetless-proposal safety by omitting Accept until a target exists;
  pending and rejected requests remain outside production RAG.
- Updated the design, workflow, guardrail, observability, API, and Telegram
  operator contract docs for the executable Step 93 behavior.

#### Issues and Decisions
- `/pending` uses `SupplementQueryOrchestrator` and repositories only; it does
  not call Notion, providers, Redis clients, the writer, or the indexer.
- The outer Telegram workflow records only bounded review fields and
  `pending_count`; callback tokens and canonical ids remain server-side.
- Cross-user, expired, and duplicate View callbacks fail closed through the
  existing callback ownership and one-shot claim rules.

#### Verification
- Focused Step 93 regression suite: `3 passed`.
- Existing operator/API/review regression suite: `39 passed`.
- Full deterministic suite: `442 passed, 3 skipped, 1 warning`.
- `python -m compileall -q src tests`: passed.
- `uv run python scripts/preflight.py --profile test`: passed with 9 expected
  local-configuration warnings.
- `git diff --check`: passed.

### Next
- Execute Step 94: add `/status` and `/stats`.

### Step 94 Follow-up

#### Highlights
- Implemented Telegram `/status` with separate liveness/readiness reporting
  and fixed safe checks for database, migration, pgvector, provider, Notion,
  Redis, and the RQ scheduler.
- Implemented Telegram `/stats` through
  `KnowledgeStatsService -> KnowledgeStatsRepository`, returning only page,
  block, chunk, vector, and proposal aggregates plus safe UTC timestamps for
  the latest successful full index and manual incremental sync.
- Updated design, architecture, API, observability, and Telegram operator
  contract docs for the executable Step 94 behavior.

#### Issues and Decisions
- Readiness failures remain distinct from process liveness; `/status` can
  report `not_ready` while the read-only Telegram operation itself succeeds.
- Aggregate statistics never inspect or format note content, vectors, page
  ids, paths, proposal JSON, credentials, or raw dependency exceptions.
- Live Telegram/Notion/Redis/OpenAI verification was not run.

#### Verification
- Focused Step 94 readiness/operator/API suite: `50 passed`.
- Full deterministic suite: `445 passed, 3 skipped, 1 warning`.
- `python -m compileall -q src tests`: passed.
- `uv run python scripts/preflight.py --profile test`: passed with 9 expected
  local-configuration warnings.
- `git diff --check`: passed.

### Next
- Execute Step 95: Telegram operator UX regression and guarded verification.

### Step 95 Follow-up

#### Highlights
- Completed the deterministic Telegram operator regression matrix across
  parsing, authorization, callback ownership, expiry, idempotency,
  confirmation gates, redaction, review safety, readiness/liveness, stats,
  help output, ingestion, review, queue, worker, and update-ledger paths.
- Added explicit `/help` coverage for `/status` and `/stats`, plus exact parser
  rejection coverage for extra arguments to both read-only commands.
- Updated the design, API, observability, deployment, and Telegram operator
  contract docs with the Step 95 verification boundary.

#### Issues and Decisions
- Live Telegram/Notion/Redis/OpenAI verification was not run. It remains a
  separately opt-in check using dedicated resources, redacted evidence, and no
  default full-index, append, Accept, or Telegram-send mutation.

#### Verification
- Focused Telegram/operator regression matrix: `70 passed`.
- Full deterministic suite: `446 passed, 3 skipped, 1 warning`.
- `python -m compileall -q src tests`: passed.
- `uv run python scripts/preflight.py --profile test`: passed with 9 expected
  local-configuration warnings and 0 failures.
- `git diff --check`: passed.

### README Product Documentation Follow-up

#### Highlights
- Rewrote the root README as a third-party-facing technical product document.
- Reframed the product around the learning knowledge lifecycle, proposal-first
  governance, append-only `AI Supplement Zone` writes, grounded QA, and the
  implemented route/orchestrator/provider/tool/repository/queue boundaries.
- Removed the former readiness, demo-status, roadmap, and internal verification
  narrative from the opening sections while keeping concise local run guidance
  and links to detailed engineering documents.

#### Issues and Decisions
- Kept current-runtime facts only: OpenAI is the concrete provider, local tools
  are MCP-oriented rather than a standalone MCP server, and live Notion is an
  explicit adapter configuration rather than an implied default.

#### Verification
- Reviewed the rewritten README against the current runtime wiring, API route
  declarations, SQLAlchemy models, Alembic revisions, and required design docs.
- `git diff --check`: passed.

### Next
- No remaining todo step; future work requires an explicit roadmap amendment.

## 2026-07-31 (Telegram Proposal Review Callback Routing — Completed)

### Highlights
- Added explicit server-side Telegram callback kinds for `review` and
  `picker`, with legacy Redis mapping normalization.
- Review callbacks now dispatch before generic picker/session handling. Inline
  Accept reuses `TelegramReviewOrchestrator` and the existing
  `SupplementReviewOrchestrator`; Reject remains Notion-write-free and Change
  target returns to the picker.
- Normal review targets remain change-request-derived; the canary page
  environment variable is not a runtime target fallback.
- Enabled RQ's embedded scheduler in `scripts/run_worker.py` so delayed
  upload-settle jobs and interval retries leave `ScheduledJobRegistry` when
  due; startup reports queue, worker, and scheduler state without secrets.
- Added versioned Telegram media settlement with message-id ordering,
  duplicate file identity handling, stale-job skips, and one-picker/one-batch
  behavior for screenshot media groups.
- Improved screenshot proposal quality with OCR browser-chrome filtering,
  source-language prompting, Traditional Chinese checks, deterministic
  grounding/shape validation, and one-call batch eval coverage. The grounding
  contract now accepts bounded lexical paraphrase while rejecting unsupported
  advice, conclusions, products, numbers, commands, URLs, and technical atoms.
- Fixed title-only false positives with normalized CJK/technical source
  anchors, deterministic heading/keyword fallback, and `/retry-proposal` reuse
  of persisted source documents without re-download or duplicate source rows.
- Added redacted screenshot latency metadata for download, OCR, LLM, persist,
  preview delivery, and total business time.
- Refreshed media-group debounce on every update, removed misleading interim
  file counts, and made failed proposal picker callbacks reuse the persisted
  source without re-download or OCR.
- Added redacted validation-stage metadata (`failure_stage`, `validation_field`,
  source id, session state/count, and retry availability) for proposal failures.
- Title grounding now joins OCR-inserted spaces inside CJK words before anchor
  scoring.
- Confirmed the real failure split: OCR media-group aggregation and persisted
  source identity are intact; outer Telegram workflow metadata was dropping the
  inner proposal validation metadata.
- Added one shared screenshot source snapshot for prompt and validator, claim-
  level grounding diagnostics, and allowlisted metadata propagation. Digests
  are equal and diagnostics never contain OCR or proposal text.
- Added a public-safe four-screenshot MySQL/EXPLAIN Traditional Chinese eval
  with OCR CJK spacing noise and a faithful paraphrase, plus an outer-workflow
  metadata regression for a summary grounding failure.
- Fixed the remaining title contract: title noun phrases now use independent
  normalized technical/CJK anchor scoring with separate title/numeric
  diagnostics. A title-only repair prompt is bounded to one provider call and
  reuses the persisted screenshot source snapshot.
- Fixed the deterministic title false negative: unmatched general CJK
  paraphrase anchors no longer hard-fail when matched high-specificity or
  sufficient general anchors, while unmatched products, technical
  identifiers, and numbers remain fail-closed.
- Added fixed redacted title failure diagnostics, a source-snapshot-derived
  repair allowlist, and one validated extractive fallback after a general-CJK
  repair failure. Added a four-image Traditional Chinese MySQL/SQL/EXPLAIN
  fixture matching the 20–40 character, no-number live shape.
- Fixed summary/concepts/notes claim diagnostics and grounding: all extracted
  claims are analyzed before fail-closed validation, source-faithful paraphrase
  remains bounded, and a summary-only repair is limited to one same-snapshot
  call.
- Diagnosed workflows 252/255: the 15/16 counts covered the whole proposal
  body, while `failed_field_count` counted unique summary/concept/note item
  paths. Historical raw candidate claims were intentionally not persisted.
- Added sentence/full-list-item validation granularity, unambiguous validation
  unit and logical-region metadata, private in-process claim evidence, and
  public-safe 15/16-unit regression fixtures matching the live count shape.
- Added one bounded body-only repair for safe lexical failures and fixed the
  title-repair transition so a grounded repaired title remains successful when
  subsequent body validation fails. Added title fallback attempted/succeeded
  metadata and the extractive `supplement_proposal_v5` prompt.
- Confirmed the upstream Chinese screenshot failure: production Tesseract used
  its English default because the adapter omitted `lang`, while the local
  runtime exposed only `eng`, `osd`, and `snum`. Sources 28 and 29 both had
  four image markers and zero persisted CJK characters.
- Required `eng+chi_tra+chi_sim` for screenshot OCR, added an adapter-level
  traineddata check with no English fallback, and extended the stdlib-only OCR
  preflight to inspect `tesseract --list-langs` through a bounded subprocess.

### Issues and Decisions
- The routing contract previously relied on an untyped action mapping and
  branch order. A restored review callback could therefore fall into the
  generic picker/ready-for-review response. Callback family is now explicit,
  while old mappings are inferred only from an allowlisted action.
- Reject callbacks supply a deterministic non-sensitive reason because the
  inline button has no reason input. No live Telegram, Notion, SQL mutation,
  or data deletion was run.
- Readiness now fails with `RQ_SCHEDULER_NOT_RUNNING` when Redis responds but
  the Telegram scheduler lock is absent. Existing scheduled jobs are retained
  for normal scheduler promotion and inspected through a read-only operator
  script.
- Kept the screenshot quality gate deterministic; no second LLM judge and no
  live `/accept`, Notion append, SQL mutation, Redis cleanup, or deletion was
  run.
- Narrowed advice detection so descriptive `use` wording is not treated as an
  instruction, while imperative/recommendation wording remains guarded.
- Kept title grounding and media-group/session behavior unchanged. Summary
  repair is disabled for new numbers, products, technical identifiers, advice,
  comparisons, results, or any additional failing field; no OCR/proposal text
  is written to diagnostics.
- Kept deterministic grounding thresholds and hard-fail categories unchanged.
  Body repair is eligible only for `INSUFFICIENT_SOURCE_ANCHORS` or
  `PARAPHRASE_NOT_GROUNDED`, runs once against the same snapshot, and must pass
  the same validator. The two-stage fact pipeline remains deferred pending a
  live retest and a separate fact-schema/ADR decision.
- Source 28 aggregate OCR inspection found four image markers, no Unicode
  replacement characters, and matching snapshot digest. This is structural
  evidence only; semantic OCR accuracy still requires visual/live retest.
- OCR language data is a runtime prerequisite rather than an application
  download. The current machine still lacks `chi_tra` and `chi_sim`; no package
  installation, service restart, Telegram request, or live OCR was run.
- Existing English-only sources remain immutable. Verifying the OCR fix
  requires a new four-image upload and a new source document; proposal retry
  intentionally reuses the old snapshot and cannot validate this change.

### Verification
- Targeted callback, Redis/session, Change target, ack-failure, preview
  recovery, and idempotency tests passed (`9 passed`).
- Added regression coverage for callback Accept, Reject, ready-for-review
  state, legacy callback mapping, duplicate update, and callback ack failure.
- Queue, readiness, worker startup, queue inspection, media-group idempotency,
  and three-screenshot RQ integration tests passed (`41 passed`); the full
  suite passed (`355 passed, 3 skipped`). Screenshot quality eval passed
  (`14 passed`) and focused Telegram/proposal tests passed (`35 passed`). Added
  title-anchor, title-fallback, and existing-source retry coverage.
- Grounding/metadata focused regression passed (`69 passed`), including
  source/prompt/validator digest equality, four-image synthetic OCR ordering,
  outer Telegram failure metadata, and no-change-request-on-invalid-output.
- Added a five-image live-shaped MySQL/EXPLAIN title fixture, title rejection
  cases for Redis, 分庫分表, and an unsupported percentage, plus bounded repair
  and second-failure tests.
- Title diagnostics, bounded repair allowlist, and general-CJK fallback tests
  passed; the focused screenshot eval passed (`29 passed`) and title repair
  API tests passed (`3 passed`).
- Added five-image 100–180 character summary fixtures, fixed-reason claim
  diagnostics, no-early-return coverage, summary-only repair, and bounded
  second-failure tests.
- Final summary-focused regression passed (`62 passed`); final full suite
  passed (`372 passed, 3 skipped`) with only the existing LibreSSL warning.
- Final proposal-validator, supplement API, and Telegram metadata focused
  regression passed (`67 passed`).
- Final full suite passed (`386 passed, 3 skipped`) with only the existing
  LibreSSL warning. Compileall, test-profile preflight, and `git diff --check`
  passed.
- OCR adapter, preflight, and persistence focused tests passed (`33 passed`).
- Final deterministic suite passed (`399 passed, 3 skipped`) with only the
  existing LibreSSL warning. Compileall and `git diff --check` passed.

### Next
- Restarted the API/worker with the title-contract changes and verified
  `/health` and `/ready`; the authenticated `/retry-proposal` reached the
  worker but the persisted source-27 Telegram session had expired. No upload,
  Accept, Notion append, SQL mutation, or Redis cleanup was run.
- A direct existing-source LLM retest remains pending explicit approval after
  the `/retry-proposal` session expiry.
- The user will install `tesseract-lang`, verify `eng`, `chi_tra`, and
  `chi_sim`, restart API/worker, and create a new source by re-uploading the
  screenshots. No live action is delegated to this implementation session.

## 2026-07-30 (Step 84 Operator Observability and Reconciliation — Completed)

### Highlights
- Added repository/service-backed operator observability: Prometheus-compatible
  `/metrics`, protected workflow status list/detail, protected cost-budget
  status, and stale-running reconciliation API.
- Added recursively redacted workflow metadata views and fixed failure metrics
  so operator surfaces never expose source text, tokens, or driver exceptions.
- Added `scripts/reconcile_workflow.py`, which is dry-run by default and
  requires `--apply` before reconciling a stale running workflow.
- Added optional `MAX_WORKFLOW_COST_USD`, `MAX_DAILY_COST_USD`, and
  `WORKFLOW_STALE_AFTER_SECONDS` settings plus related documentation.

### Issues and Decisions
- Reconciliation requires a running workflow older than the configured stale
  threshold and transitions it exactly once; it never reruns business work.
- Unknown model pricing remains `unknown` and is not guessed. Cost budgets are
  deterministic operator alerts and do not alter existing provider behavior.
- `/metrics` remains public for scraping; `/api/ops/*` uses the existing API
  bearer trust boundary.

### Verification
- Step 84 focused tests: `14 passed`.
- Full suite: `286 passed, 3 skipped`.
- `compileall`, preflight (`32` checks, pass), CLI guard/help smoke, and
  `git diff --check` passed.

### Next
- Step 85: add backup, restore, migration, and incident runbooks.

## 2026-07-30 (Step 85 Backup, Restore, Migration, and Incident Runbooks — Completed)

### Highlights
- Added a guarded PostgreSQL restore drill that is dry-run by default and
  requires explicit disposable-target confirmation before creating temporary
  databases, applying Alembic migrations, running `pg_dump`/`pg_restore`, and
  verifying a restore sentinel.
- Added a deterministic Notion/PostgreSQL recovery checklist covering restored
  databases, manual Notion edits, uncertain append identity, and stale
  workflow reconciliation without adding Notion write capabilities.
- Added backup/restore, migration, and incident runbooks plus deployment,
  workflow, observability, and design documentation for Step 85.

### Issues and Decisions
- The local environment has PostgreSQL client binaries but no responding
  server (`pg_isready` returned no response); Docker daemon access was also
  unavailable. The live restore drill was therefore not executed against any
  database. Dry-run and confirmation guards were verified without external
  writes.
- Notion remains the source of truth. Recovery stops when append identity is
  unavailable and never performs a direct edit, delete, move, or manual append.
- Restored PostgreSQL state is rebuilt through full or page-scoped Notion
  indexing before mutations resume.

### Verification
- Step 85 focused tests: `8 passed`.
- Full suite: `294 passed, 3 skipped`.
- Restore dry-run JSON, live confirmation/admin-URL guards, recovery plan
  output, compileall with an isolated pycache prefix, API preflight (`32`
  checks, pass), and `git diff --check` passed.
- `pg_isready -h localhost -p 5432` reported no response; no database or
  Notion write was attempted.

### Next
- Step 86: establish the release gate.

### Step 87 Update

#### Highlights
- Audited `mock_data/`: retained the three JSON pages used by the mock demo,
  tests, and eval fixtures; removed only the unused `.DS_Store` artifact.
- Added a fixed synthetic page-id policy, repository-backed dry-run/apply
  cleanup operator, PostgreSQL mock-source persistence guard, and fail-closed
  release gate. The cleanup command never connects to Notion and never accepts
  arbitrary ids.
- Updated README and design, architecture, RAG, API, evaluation, deployment,
  and observability docs so persistent PostgreSQL is not presented as a mock
  demo target.

#### Issues and Decisions
- `page-nlp-week5` and other synthetic pages remain valid test/demo inputs but
  are not production retrieval evidence. The mock demo uses ephemeral SQLite;
  PostgreSQL mock indexing fails with `SYNTHETIC_DATA_NOT_ALLOWED` before DB
  persistence.
- Human-confirmed live PostgreSQL evidence now closes the blocker: cleanup was
  reviewed and applied only after explicit confirmation, and the release gate
  passed with all synthetic counts at zero. No new live Notion write or Telegram
  E2E was run in this closeout session.

#### Verification
- Focused hygiene, mock-reader/demo, and live-vector unit tests: `14 passed`.
- Full suite: `300 passed, 3 skipped`, with one LibreSSL warning from the
  existing urllib3 runtime.
- Mock demo: pass. Preflight: `32` checks, pass. Compileall and
  `git diff --check`: pass.
- The initial local cleanup dry-run and release gate failed closed with
  `DATABASE_INSPECTION_FAILED` because `pg_isready -h localhost -p 5432`
  reported no response; the later human-confirmed run against the intended
  PostgreSQL database passed as recorded below.
- Human-confirmed live database evidence: Alembic `8a4d1f0c2b3e` at head;
  preflight passed; cleanup dry-run `1` page / `12` blocks / `5` chunks /
  `5` production chunks / `0` vector chunks; cleanup apply removed `1/12/5`
  and left all counts at `0`; release gate `synthetic_database_data` passed.

#### Next
- Step 87 is done. Step 88 is doing: fix the Telegram RQ worker import blocker,
  then perform a separately approved live retest. Keep default no-network/no-
  write, with explicit opt-in for every live Telegram send and Notion write.

### Step 88 Update (Telegram RQ Worker Import Blocker — In Progress)

#### Highlights
- Diagnosed the live failure after webhook `202` and Redis/RQ enqueue: RQ
  persisted `src.worker.telegram.process_telegram_webhook_job`, but the worker
  process had no repository root in `sys.path`.
- Updated `scripts/run_worker.py` to derive the repository root from its own
  file path, fail-fast through RQ `import_attribute()`, and preserve the
  webhook -> ledger -> RQ -> worker flow.
- Added a canonical module-level Telegram job path and qualified callable
  metadata, plus fresh-process/non-repo-cwd/RQ-resolution/enqueue regressions.

#### Issues and Decisions
- General import succeeded because the diagnostic ran with the project root
  available; the worker was launched from a context where `src` was not
  importable. RQ therefore raised `Invalid attribute name` while resolving the
  stored dotted path.
- The failed update is not re-run, and no raw SQL or ledger mutation was used.
  The durable `telegram_update_ledger` outcome remains the safe source of truth;
  recovery requires an explicit operator decision after inspection.
- No Telegram live send, Notion append, `/accept`, or cleanup apply was run.

#### Verification
- Focused Telegram/RQ tests: `28 passed`.
- Fresh subprocess import and non-repo-cwd worker resolution passed.
- RQ `import_attribute()` and persisted `job.func_name` matched the canonical
  `src.worker.telegram.process_telegram_webhook_job` path.

#### Next
- Run full pytest, compileall, preflight, and diff checks. Then restart API and
  worker and perform a separately approved live retest; Step 88 remains `doing`.

### Step 88 Update (macOS RQ SpawnWorker Blocker — In Progress)

#### Highlights
- Confirmed the locked environment uses RQ `2.8.0`, which provides
  `rq.worker.SpawnWorker`.
- Updated `scripts/run_worker.py` with an explicit, testable worker-class
  policy: `auto` selects `SpawnWorker` on Darwin/macOS and standard `Worker`
  on Linux. macOS rejects the fork-based override, with no
  `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` requirement.
- Added a safe worker-class startup log and `--burst` for an empty disposable
  smoke queue; the webhook -> ledger -> Redis/RQ -> worker path is unchanged.
- Added a queue-backed regression that resolves the persisted callable and
  enters a gateway stub without Telegram send or Notion append.

#### Issues and Decisions
- The live work-horse signal `6` was caused by macOS Objective-C runtime fork
  safety in RQ's default `Worker`; it was not an application callable or queue
  serialization failure.
- The prior failed update is not replayed and was not changed with raw SQL.
  Its durable ledger state remains the source of truth; retest must use a new
  `update_id` after the user restarts the API and worker.
- No Telegram live send, Notion append, `/accept`, or cleanup apply was run.

#### Verification
- RQ version/API probe: `2.8.0`, `SpawnWorker` available.
- Focused Telegram/RQ tests: `15 passed`.
- Full suite: `309 passed, 3 skipped`, with the existing macOS
  LibreSSL/urllib3 warning.
- Darwin/Linux worker policy, fresh-process import, RQ resolution, enqueue
  path, gateway-stub, queue, ledger, and `202` tests passed.
- Compileall with an isolated `/private/tmp` pycache prefix, API preflight,
  and `git diff --check` passed.
- Disposable Redis smoke on port `6391` and empty queue
  `step88-empty-smoke` showed `worker_class=SpawnWorker`, RQ `2.8.0`, and
  `Listening on step88-empty-smoke`; the instance was shut down afterward.

#### Next
- Complete focused/full deterministic verification, compileall, preflight, and
  diff checks. User then runs the separately approved live retest; Step 88
  remains `doing`.

### Step 88 Update (Telegram Ingestion UX Redesign — In Progress)

#### Highlights
- Added chat/user-isolated Redis TTL upload sessions with media-group
  aggregation, attachment deduplication, and opaque Redis-backed callback
  tokens that resolve to canonical external Notion page ids.
- Reworked the primary Telegram flow to acknowledge PDF/image uploads, show
  parent and child hierarchy-path buttons, create a target-aware pending
  proposal only after selection, and expose explicit Accept/Reject/Change
  target review actions.
- Added caption parsing, callback payloads, target-change routing, preview
  idempotency claims, and deterministic tests for PDF, image, media group,
  caption, parent/child selection, expiry, duplicate updates, invalid
  callbacks, and target-set proposals.
- Fixed Redis target-picker restoration: session identity is passed separately
  from `target_notion_page_id`, so the selected target survives API enqueue and
  RQ worker reconstruction through ingestion and pending proposal creation.
- Fixed selected-page proposal target contract: the backend now derives the
  exact `<canonical notion_path>/AI Supplement Zone`, normalizes only harmless
  slash/whitespace formatting, and rejects cross-page, child, or missing-zone
  model targets before creating a change request.
- Updated the versioned supplement prompt with the exact backend target and
  added a redacted Telegram callback reply for `LLM_OUTPUT_INVALID`.

#### Issues and Decisions
- The callback path initially parsed an empty message text before dispatching
  the callback action; the parser now treats empty input as `unknown` so inline
  callbacks remain independent of message text.
- Media-group OCR/proposal work remains behind the existing queue and atomic
  session claims; no synchronous or automatic Accept path was introduced.
- Redis-backed callback/session failures now use specific redacted reasons
  instead of falling through to `UNKNOWN_ERROR`.
- A failed proposal can leave one persisted source document and zero change
  requests; the failed session and update ledger prevent retrying the same
  callback from creating duplicates.
- No live Telegram send, `/accept`, Notion append, or cleanup apply was run.

#### Verification
- Telegram UX/gateway/API/queue focused coverage: `25 passed`.
- Added a real RQ + fakeredis regression covering upload, page picker,
  callback selection, worker session restore, ingestion, and one pending
  target-aware change request.
- Full suite: `319 passed, 3 skipped`, with the existing macOS
  LibreSSL/urllib3 warning.
- Target contract/prompt/Telegram regression coverage: `43 passed`.
- Non-write full regression excluding accept/append/cleanup tests:
  `303 passed, 3 skipped, 23 deselected`.
- Compileall with an isolated `/private/tmp` pycache prefix, API/test
  preflight, and `git diff --check` passed.

#### Next
- User restarts the API and macOS worker and supplies a new `/help` for the
  separately approved live retest; Step 88 remains `doing`.

#### Step 88 Callback Consistency Fix (2026-07-30)
- Root cause confirmed: the gateway ran OCR/proposal/preview before
  `answerCallbackQuery`, then mapped acknowledgement failure to
  `TELEGRAM_SEND_FAILED` and finalized both workflow and update ledger as
  failed after source document/change request commit.
- Moved valid callback acknowledgement before long work, separated business,
  callback-ack, and preview-delivery state, and added
  `TELEGRAM_CALLBACK_ACK_FAILED` plus
  `TELEGRAM_PREVIEW_DELIVERY_FAILED` classifications.
- Added explicit dry-run-first recovery service/CLI for existing committed
  outcomes; it verifies source 11/change request 6 without OCR/LLM/recreation.
- No live Telegram send, `/accept`, Notion append, cleanup apply, deletion, or
  mutation of existing pending data was run.

#### Verification
- Targeted Telegram/session/idempotency/API tests: `36 passed` including
  callback acknowledgement timeout, preview delivery recovery, duplicate
  update replay, expired picker fail-closed, and existing-row reconciliation.
- Exact recovery dry-run invocation returned the redacted
  `TELEGRAM_RECOVERY_STORAGE_UNAVAILABLE` because local PostgreSQL access was
  unavailable in this environment; no Telegram or business mutation occurred.

## 2026-07-29 (Step 82 Guarded Notion Read/Index/QA Canary — Completed)

### Highlights
- Added an opt-in Step 82 canary that uses the real read-only Notion adapter,
  runs full and incremental indexing plus scoped cited QA, and stores derived
  state only in ephemeral SQLite.
- Added a recording transport that blocks non-reader Notion operations before
  dispatch and emits only redacted operation classes.
- Added deterministic local embedding and answer adapters so the canary does
  not require an OpenAI key or production database.
- Updated design, RAG, evaluation, observability, and deployment docs with the
  Step 82 contract.

### Issues and Decisions
- The first live run exposed a persistence integrity failure because a parent
  tree inlined the same `child_page` blocks that full discovery indexed again.
  The reader now keeps page-reference blocks without inlining their children.
- The second live run exposed compact-versus-hyphenated Notion page IDs. A
  shared canonicalization helper now keeps full indexing, incremental indexing,
  and QA scope aligned.
- No Notion write request was sent; the recording transport remained active for
  every live run.

### Verification
- Focused reader/canary tests: `14 passed`.
- Full suite: `274 passed, 3 skipped`.
- Live canary JSON: `2` indexed pages, `11` indexed blocks, `4` indexed
  chunks, `1` incremental page, `1` citation, `9` read-only requests, and `0`
  write attempts.
- `compileall`, `scripts/preflight.py --json`, and `git diff --check` passed.

### Next
- Step 82 is complete. Wait for explicit human approval and a separate append
  canary decision before starting Step 83.

### Step 83 Update

#### Highlights
- Added an explicitly gated append/re-index canary that reuses the existing
  human accept orchestrator, durable change-request identity verification, and
  scoped QA citation path.
- Added a transport allowlist for page/block reads and append-only block-child
  PATCH requests, plus redacted operation/count reporting.
- Updated design, workflow, guardrail, permission, and observability docs with
  the Step 83 contract.

#### Issues and Decisions
- The canary requires both `--live` and `--approve`; derived state is ephemeral
  SQLite and the live target must be a dedicated sandbox page.
- The initial local attempt had no configured Notion token or sandbox page id,
  so it stopped at configuration and sent zero Notion requests. A later
  human-confirmed run completed the dedicated sandbox append canary; its
  bounded evidence is reflected in the Step 83 roadmap row and Step 87 closeout.

#### Verification
- Step 83 focused canary tests: `4 passed`.
- Step 82 + Step 83 focused tests: `10 passed`.
- Full suite: `278 passed, 3 skipped`.
- Deterministic live-command guard: configuration failure with `0` Notion
  requests; no write was attempted.
- `compileall`, `scripts/preflight.py --json`, and `git diff --check` passed.

#### Next
- Step 83 is complete. Keep the append canary opt-in and sandbox-scoped; the
  next planned work is Step 87 synthetic-data cleanup and release-gate closure.

## 2026-07-28 (Steps 74-76 Release Hardening)

### Highlights
- Completed roadmap Step 74 with deterministic trust boundaries for configured
  API bearer tokens, Telegram webhook secrets, and Telegram chat allowlists.
- Completed roadmap Step 75 with a persistent unique Telegram `update_id`
  ledger and gateway replay behavior for running, succeeded, and failed
  updates.
- Added the Alembic migration, repository/service boundary, and deterministic
  sequential/concurrent duplicate-update coverage.
- Protected all non-Telegram `/api` routers while keeping `/health` and `/ready`
  public; forged Telegram requests are rejected before workflow creation.
- Added redacted preflight/configuration reporting, focused caller-matrix tests,
  and updated architecture, workflow, guardrail, observability, and API docs.
- Completed Step 76 with a persistent API idempotency ledger and
  `Idempotency-Key` middleware for ingestion and supplement POST mutations.
- Added same-key replay for running/succeeded/failed outcomes, canonical JSON
  and normalized multipart fingerprints, and deterministic 409 payload conflicts.
- Completed Step 77 by routing configured Telegram webhook work through
  `QueueClient`/RQ with a fast `202` ACK, an importable worker job, and the
  `scripts/run_worker.py` entrypoint.
- Added bounded Telegram retries, Redis-backed readiness checks, duplicate
  enqueue prevention, and deterministic queue/readiness regressions.
- Completed Step 78 with shared upload limits across API routes, ingestion
  orchestrators, PDF/OCR tools, and Telegram download paths.
- Added bounded reads and deterministic rejection for MIME, file count, bytes,
  PDF pages, image pixels, and extracted text.
- Completed Step 79 with guarded URL ingestion: syntax and credential checks,
  public IPv4/IPv6 DNS validation, bounded manual redirects, response type
  allowlisting, and bounded response reads.

### Issues and Decisions
- Kept the new credentials optional for local/test compatibility. Preflight
  warns when they are absent; production-like runs should configure all three
  trust-boundary settings.
- Used constant-time comparisons for bearer and Telegram secret checks, and
  kept authorization decisions in backend services rather than the LLM flow.
- Stored only request scope, SHA-256 fingerprint, and safe response replay
  fields; raw request payloads are not logged or persisted in the ledger.
- A unique scope/key constraint plus retry-on-integrity-race ensures one
  concurrent owner. No new secret or API key is required for this step.
- Preserved synchronous local/test compatibility when `REDIS_URL` is absent;
  release-style local readiness now fails closed until Redis is configured and
  reachable. Expected Telegram failures are terminal; unexpected worker
  crashes remain eligible for bounded RQ retry.
- Parser limits are enforced again below the HTTP boundary so Telegram and
  direct callers cannot bypass resource protection. Limit failures never log
  upload bytes or raw extracted text.
- URL HTTP stays behind the tool adapter with injected transport/resolver
  seams for deterministic tests; sanitized failure codes avoid exposing
  upstream exception bodies.
- Completed Step 80 with v2 QA/supplement prompts, explicit untrusted-content
  boundaries, page-scoped proposal target validation, and deterministic
  English/Traditional Chinese adversarial checks.
- Workflow metadata now records `prompt_safety_version`; backend-derived
  citations and append-only write/target rules remain authoritative.
- Completed Step 81 with a redacted real-library adapter smoke matrix for
  controlled PDF/OCR/URL fixtures plus opt-in YouTube/OpenAI/PostgreSQL/
  Telegram checks. The default matrix is local-only and performs no Notion
  access or writes.

### Verification
- Focused Step 74 tests passed (`11 passed`).
- API/Telegram regression tests passed (`56 passed`).
- Full deterministic suite passed (`232 passed, 3 skipped`).
- Step 75 focused and migration tests passed (`20 passed`); full suite passed
  (`236 passed, 3 skipped`).
- Step 76 focused tests passed (`32 passed`); full suite passed
  (`240 passed, 3 skipped`).
- Compileall, preflight, and `git diff --check` passed.
- Step 77 focused queue/Telegram/readiness tests passed; the full suite passed
  (`245 passed, 3 skipped`). Compileall, API preflight, and
  `git diff --check` passed.
- Step 78 focused upload/parser/API tests passed (`39 passed`); the full suite
  passed (`251 passed, 3 skipped`). Compileall, API preflight, and
  `git diff --check` passed.
- Step 79 URL/API focused tests passed (`22 passed`); the full suite passed
  (`257 passed, 3 skipped`). Compileall, API preflight, and `git diff --check`
  passed.
- Step 80 focused tests passed (`28 passed`); prompt-injection eval passed
  (`5/5`), golden retrieval/citation evals passed (`3/3` each), write-safety
  eval passed (`4/4`), full suite passed (`264 passed, 3 skipped`), and
  compileall, API preflight, and `git diff --check` passed.
- Step 81 focused matrix tests passed (`2 passed`); the default redacted
  matrix passed (`3 passed, 4 skipped`); full suite passed
  (`266 passed, 3 skipped`), compileall, preflight, and `git diff --check`
  passed. The first compileall/uv invocations hit sandbox cache permissions;
  reruns used writable temporary cache paths or the bundled virtualenv.

### Next
- Completed Step 81. Wait for explicit approval before executing Step 82:
  `Run a guarded Notion read/index/QA canary`.

## 2026-07-27 (Step 56 Workflow Audit Session Isolation)

### Highlights
- Completed roadmap Step 56 by adding a DB session-factory dependency beside
  the existing request DB-session dependency.
- Refactored `WorkflowRunService` so every workflow audit create/update opens
  its own fresh SQLAlchemy session, writes through `WorkflowRunRepository`,
  and closes the session after the audit write.
- Rewired Notion indexing, source ingestion, supplement, QA, and Telegram route
  builders so business repositories keep using the request session while
  workflow audit writes use the session factory.
- Added regression coverage proving an audit commit does not commit an
  uncommitted business `SourceDocument`.
- Updated API tests and standalone eval helpers to provide the same SQLite
  session factory to the new audit dependency.
- Moved the roadmap current pointer to Step 57:
  `Introduce fresh-session business Unit of Work`.
- Completed roadmap Step 57 by adding `SqlAlchemyUnitOfWork` with fresh
  business sessions, begin-on-enter behavior, auto-commit on successful exit,
  rollback on exception, and close-on-exit cleanup.
- Exposed business repository accessors through the UoW for page, block,
  chunk, source-document, and change-request repositories.
- Added a UoW factory dependency surface beside the existing DB session
  dependencies so future orchestrator wiring can receive fresh UoWs.
- Added focused UoW tests for fresh sessions, repository accessors,
  rollback/commit behavior, closed sessions, inactive access, nested entry
  rejection, and absence of a manual `commit()` API.
- Moved the roadmap current pointer to Step 58:
  `Migrate page-indexing repositories from commit to flush and update indexing
  call sites`.
- Completed roadmap Step 58 by changing page-indexing repositories
  (`NotionPageRepository`, `NotionBlockRepository`, and `ChunkRepository`) from
  repository-owned `commit()` to caller-owned `flush()` behavior.
- Rewired `NotionPageIndexOrchestrator` so page-index persistence runs through
  a fresh UoW transaction while Notion reads, path building, chunk drafting,
  and embedding generation remain outside the DB transaction.
- Updated Notion indexing, supplement accept, Telegram accept, mock reader,
  manual sync eval, and live smoke builder paths to provide UoW-backed page
  indexing.
- Added repository tests proving page, block, chunk upsert/delete methods
  flush without committing.
- Moved the roadmap current pointer to Step 59:
  `Make one-page indexing one short atomic DB transaction`.
- Completed roadmap Step 59 by making the page-index persistence return a pure
  `NotionIndexedPageSnapshot` after the short UoW transaction exits.
- Added rollback-injection coverage for failures after old chunk deletion,
  after block replacement, and during chunk insertion.
- Moved the roadmap current pointer to Step 60:
  `Migrate remaining business-write repositories to flush and add matching
  explicit UoW boundaries`.
- Completed roadmap Step 60 by changing the remaining source-document and
  change-request business-write repository methods to `flush()` only.
- Added explicit fresh UoW boundaries for generic, PDF, URL, YouTube, OCR,
  chat-text, and Telegram source ingestion, plus supplement proposal and
  review status writes. Result fields are captured before UoW session close.
- Added direct repository flush/rollback coverage in
  `tests/test_business_write_repositories.py`.
- Moved the roadmap current pointer to Step 61:
  `Make incremental sync one transaction per page with accurate batch
  reporting`.
- Completed roadmap Step 61 by making incremental-sync failure bookkeeping
  deterministic with `enumerate()`-based page positions.
- Failed batches now record succeeded, failed, and remaining page identifiers
  and counts while preserving earlier page commits and the unchanged API
  response shape.
- Updated `docs/08-observability.md` with the incremental-sync transaction and
  failure metadata contract.
- Moved the roadmap current pointer to Step 62:
  `Add same-page concurrency protection and stale snapshot rejection`.
- Completed roadmap Step 62 by adding PostgreSQL transaction-scoped advisory
  locking keyed by stable Notion page id and deterministic UTC stale-snapshot
  rejection before page block/chunk replacement.
- Extended the Notion reader contract, mock JSON loader, index payload, and
  immutable index result with nullable `last_edited_time` support.
- Added migration inspection, NULL compatibility, advisory-lock, reader, and
  end-to-end stale-payload regressions; updated workflow, RAG, and observability
  docs with the snapshot safety contract.
- Moved the roadmap current pointer to Step 63:
  `Make accept durable with append verification, retry detection, and
  in-transaction pending revalidation`.
- Completed roadmap Step 63 by adding a visible deterministic
  `LearnLoop Change Request: change-request-<id>` identity to accepted
  supplements and bounded read-after-write verification in the writer tool.
- Added durable retry detection that scans the Notion-visible supplement
  identity across fresh writer/client instances, plus `FOR UPDATE` change
  request revalidation before accept commits.
- Refactored accept re-indexing so preparation stays outside the DB transaction
  while page/block/chunk persistence and `pending -> accepted` share one UoW
  transaction. Re-index failure rolls back the DB state and leaves the request
  retryable without duplicating the Notion append.
- Added focused regressions for fresh-client durable append detection and
  append-success/re-index-failure/retry behavior.
- Moved the roadmap current pointer to Step 64:
  `Add workflow audit reconciliation for final audit-update failure`.
- Completed roadmap Step 64 by separating final workflow audit updates from
  business exception handling. A success-audit failure now raises the distinct
  `WORKFLOW_AUDIT_UPDATE_FAILED` error without rolling back or rerunning the
  committed business transaction.
- Made failure-audit updates best-effort so an audit write failure never hides
  the original business exception; added sanitized structured audit failure
  logs and a running-only stale workflow reconciliation service path.
- Added regressions for committed business work with failed success audit,
  original business exception preservation, and reconciliation state guards.
- Updated workflow, design, and observability docs with the reconciliation
  contract and audit failure semantics.
- Completed roadmap Step 65 by reconciling the release-readiness audit with
  repository documentation without changing production code.
- Corrected Steps 59, 63, and 64 to `done` in the roadmap summary and added
  dependency-ordered Steps 65-86 under
  `Real-World Usability + Release Hardening`.
- Updated README plus architecture, workflow, guardrail, permission,
  evaluation, observability, API, and deployment docs to distinguish
  deterministic mock evidence, bounded live-dependency evidence, missing
  real-user paths, and deferred scope.
- Completed roadmap Step 66 with a stdlib-only redacted preflight checker,
  missing-dependency matrix tests, and a portable repo-relative API entrypoint.
- Completed roadmap Step 67 with dependency-aware `/ready`, isolated shallow
  `/health`, mode-specific OpenAI configuration checks, and stabilized Alembic
  logging so pytest handlers are preserved.
- Completed roadmap Step 68 with a read-only Notion REST adapter behind
  `NotionReaderTool`, including page metadata, paginated root/nested block
  reads, deterministic citation paths, and safe HTTP error mapping.
- Added injected fake-transport coverage for authorization, missing pages,
  pagination, nested blocks, malformed responses, and secret/private-body
  redaction. Runtime wiring remains mock-backed until Step 71's explicit
  `NOTION_BACKEND` switch.
- Completed roadmap Step 69 with paginated Notion page discovery,
  `/api/notion/index/full`, and `/api/notion/index/status`.
- Full indexing discovers external page ids through `NotionReaderTool`, then
  reuses page-level replacement and embedding persistence for each page.
- Added multi-page, repeated-index, stale-block removal, external-id, and
  workflow-status regression coverage.
- Completed roadmap Step 70 with `NotionAPIWriterClient`, an append-only REST
  adapter behind `NotionWriterTool` for locating/creating the supplement
  hierarchy, appending content, and verifying durable identity.
- Added fake-transport tests proving the HTTP allowlist, auth/error redaction,
  retry identity, read-after-write verification, and existing accept/re-index
  compatibility.

### Issues and Decisions
- Kept business repository commit behavior unchanged; UoW and repository
  flush-only migration remain future steps.
- Included QA route wiring even though Step 56 examples focused on Notion,
  supplement, source ingest, and Telegram, because QA also creates workflow
  audit records.
- Kept repository-owned `commit()` behavior unchanged in Step 57; page
  indexing and remaining business-write commit ownership remain Step 58 and
  Step 60 work.
- Chose not to expose the raw SQLAlchemy session from the UoW. Business access
  stays repository-based.
- Kept `SourceDocumentRepository` and `ChangeRequestRepository` commit
  behavior unchanged, as required by Step 58 non-goals.
- Left broader rollback-injection coverage for Step 59; Step 58 focused on
  commit ownership and UoW wiring for page-indexing call sites.
- Kept Step 59 failure injection in tests by wrapping the real
  `SqlAlchemyUnitOfWork`; no production-only test hook was added.
- Confirmed Notion reads, path building, chunk drafting, and embeddings stay
  outside the business DB transaction.
- Kept workflow audit writes on their existing fresh-session service path;
  business UoWs now own only the short persistence mutations.
- Added an app dependency that derives business UoW factories from the
  configured session factory so SQLite API overrides remain isolated and
  deterministic.
- Kept batch-level audit persistence on the fresh workflow session while each
  page mutation remains owned by the page-index UoW.
- Kept PostgreSQL-only advisory SQL inside the page repository; SQLite remains
  deterministic through a no-op lock path while sharing stale timestamp logic.
- Preserved stored timestamps when a legacy reader returns NULL, preventing an
  older contract from weakening future stale-snapshot protection.
- Kept Notion append and PostgreSQL commits explicitly non-atomic; durable
  visible identity plus bounded verification provides retry safety without
  claiming cross-system atomicity.
- Kept Step 65 documentation-only. No source, migration, configuration, test,
  script, or runtime behavior was changed.
- Documented that `NOTION_TOKEN` currently has no live-client effect,
  server-backed indexing requires OpenAI embeddings, Redis/RQ is not wired
  into request execution, and Telegram ingest cannot currently select a
  target page.
- Kept all append-only, human acceptance, production-RAG exclusion, and
  deterministic backend guardrails unchanged.
- Kept preflight connectivity-free: database, Redis, migration, vector, and
  external-service checks remain outside Step 66 and are reserved for `/ready`
  work in Step 67.
- Added `--no-env-file` to the portable entrypoint because `uv run` can load a
  local `.env`; users must continue to explicitly export or source runtime
  configuration.
- Kept Redis out of `/ready` because runtime requests do not use the queue until
  the Step 77 worker wiring; no false queue readiness is reported.
- Kept readiness checks deterministic and redacted: raw database exceptions,
  connection URLs, provider credentials, and private content are never exposed.
- Kept the live Notion adapter read-only and SDK-free, using stdlib HTTP plus a
  transport interface so pagination and error contracts remain deterministic.
- Kept live backend selection out of this step; Step 71 owns fail-closed
  `NOTION_BACKEND=mock|live` wiring after discovery and writer work.
- Kept full indexing synchronous and sequential for deterministic per-page
  transactions; earlier successful pages remain committed when a later page
  fails, with safe identifiers and counts persisted in workflow metadata.
- Kept `/api/notion/index/status` read-only against workflow storage; it does
  not contact Notion or expose page content.
- Kept the live writer limited to `GET` locate/verify and `PATCH` children
  append calls; no update, delete, move, or original-note method was added.
- Kept runtime writer selection deferred to Step 71's explicit fail-closed
  `NOTION_BACKEND` wiring.

### Verification
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_workflow_run_repository.py tests/test_workflow_run_service.py
  tests/test_notion_index_page_api.py tests/test_source_ingest_api.py
  tests/test_supplement_api.py tests/test_telegram_api.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_qa_api.py tests/test_qa_orchestrator.py
  tests/test_mock_notion_reader_client.py tests/evals/test_live_vector_smoke.py
  -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  tests/evals/manual_sync_eval.py`
- Completed local verification:
  `git diff --check`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_notion_page_block_repository.py tests/test_notion_reader_tool.py
  tests/test_notion_index_page_api.py tests/test_mock_notion_reader_client.py
  tests/test_pgvector_migration.py -q` (`26 passed`).
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest -q`
  (`186 passed, 3 skipped`; one pre-existing `tests/test_health.py` logging
  capture failure after embedded Alembic logging configuration).
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_health.py -q` and compile/diff checks after the full-suite result.
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_unit_of_work.py tests/test_db_session.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_workflow_run_repository.py tests/test_workflow_run_service.py
  tests/test_notion_index_page_api.py tests/test_source_ingest_api.py
  tests/test_supplement_api.py tests/test_telegram_api.py tests/test_qa_api.py
  -q`
- Completed local verification:
  `git diff --check`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_notion_page_block_repository.py tests/test_chunk_repository.py
  tests/test_notion_index_page_api.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_supplement_api.py tests/test_telegram_api.py
  tests/test_mock_notion_reader_client.py tests/evals/test_live_vector_smoke.py
  -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_unit_of_work.py tests/test_db_session.py
  tests/test_notion_page_block_repository.py tests/test_chunk_repository.py
  tests/test_notion_index_page_api.py tests/test_supplement_api.py
  tests/test_telegram_api.py tests/test_mock_notion_reader_client.py
  tests/evals/test_live_vector_smoke.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  tests/evals/manual_sync_eval.py`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_notion_index_page_api.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_business_write_repositories.py tests/test_source_ingest_api.py
  tests/test_supplement_api.py tests/test_telegram_api.py
  tests/test_unit_of_work.py -q` (`43 passed`).
- Completed local verification:
  `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-pycache python3 -m compileall
  -q src tests`.
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/evals/test_manual_sync_eval.py tests/evals/test_live_vector_smoke.py
  tests/test_mock_notion_reader_client.py tests/test_mock_demo_script.py -q`
  (`10 passed`).
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  tests/evals/manual_sync_eval.py` (`4/4` checks passed).
- Completed local verification: full suite excluding the existing Alembic
  logging-capture interaction passed (`181 passed, 3 skipped`), and
  `tests/test_health.py` passed independently (`2 passed`). A combined full
  run still has one pre-existing `test_health_logs_workflow_id` failure after
  embedded Alembic `fileConfig` resets the request logger capture; this step
  does not change Alembic logging behavior.
- Completed local verification: `git diff --check`.
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_notion_index_page_api.py tests/test_unit_of_work.py
  tests/test_notion_page_block_repository.py tests/test_chunk_repository.py
  tests/evals/test_manual_sync_eval.py -q` (`27 passed`).
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  tests/evals/manual_sync_eval.py` (`4/4` checks passed).
- Completed local verification:
  `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-pycache python3 -m compileall
  -q src tests` and `git diff --check`.
- Completed local verification: full regression excluding the existing
  Alembic logging-capture interaction passed (`181 passed, 3 skipped`), and
  `tests/test_health.py` passed independently (`2 passed`).
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_unit_of_work.py tests/test_db_session.py
  tests/test_notion_page_block_repository.py tests/test_chunk_repository.py
  tests/test_supplement_api.py tests/test_telegram_api.py
  tests/test_mock_notion_reader_client.py tests/test_mock_demo_script.py
  tests/evals/test_live_vector_smoke.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_notion_writer_tool.py tests/test_supplement_api.py
  tests/test_telegram_api.py tests/test_notion_index_page_api.py -q`
  (`41 passed`).
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest -q`
  (`188 passed, 3 skipped`; one known combined `test_health_logs_workflow_id`
  logging-capture interaction remains), plus standalone `tests/test_health.py`
  (`2 passed`).
- Completed local verification:
  `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-pycache python3 -m compileall
  -q src tests` and `git diff --check`.
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache PYTHONPYCACHEPREFIX=/private/tmp/learnloop-pycache uv run --frozen pytest tests/test_workflow_audit_reconciliation.py tests/test_workflow_run_service.py tests/test_workflow_run_repository.py tests/test_source_ingest_api.py tests/test_supplement_api.py tests/test_telegram_api.py tests/test_qa_api.py tests/test_qa_orchestrator.py tests/test_notion_index_page_api.py tests/test_unit_of_work.py -q` (`72 passed`).
- Completed local verification: full suite (`191 passed, 3 skipped`; the known combined `test_health_logs_workflow_id` logging-capture interaction remains), standalone `tests/test_health.py` (`2 passed`), compileall, and `git diff --check`.
- Step 65 documentation acceptance checks passed for corrected OpenAI/Notion
  statements, roadmap Steps 65-86, completed Steps 59/63/64, balanced Markdown
  fences, tracked diff scope, and `git diff --check`.
- `UV_CACHE_DIR=/private/tmp/learnloop-step65-uv-cache
  PYTHONPYCACHEPREFIX=/private/tmp/learnloop-step65-pycache uv run --frozen
  pytest tests/test_config.py tests/test_mock_demo_script.py
  tests/test_health.py -q` passed (`5 passed`).
- `UV_CACHE_DIR=/private/tmp/learnloop-step65-uv-cache
  PYTHONPYCACHEPREFIX=/private/tmp/learnloop-step65-pycache uv run --frozen
  python scripts/run_mock_demo.py` passed.
- Completed roadmap Step 66 by adding stdlib-only
  `scripts/preflight.py` with `api`, `test`, and `ocr` dependency profiles,
  redacted configuration status, and no-secret-output coverage.
- Replaced the user-specific `scripts/run_live.sh` wrapper with a portable
  repo-relative entrypoint that uses the locked `uv` environment and
  `--no-env-file` before starting Uvicorn.
- Updated README and deployment documentation with the preflight contract and
  kept dependency/connectivity readiness checks deferred to Step 67.
- `env -u DATABASE_URL -u REDIS_URL -u OPENAI_API_KEY -u NOTION_TOKEN
  -u TELEGRAM_BOT_TOKEN UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run
  --no-env-file --frozen pytest tests/test_preflight.py tests/test_config.py
  tests/test_security_review.py -q` passed (`7 passed`).
- The mock demo regression passed independently (`1 passed`); `tests/test_preflight.py`
  also verifies the repo-relative entrypoint and no-secret output.
- Locked-environment JSON preflight passed with `--profile api
  --require-command uv`; `bash -n scripts/run_live.sh` and `git diff --check`
  passed.
- Full suite passed `195 passed, 3 skipped` except the known combined
  `test_health_logs_workflow_id` Alembic logging-capture interaction; standalone
  `tests/test_health.py` remains passing.
- `env -u DATABASE_URL -u REDIS_URL -u OPENAI_API_KEY -u NOTION_TOKEN
  -u TELEGRAM_BOT_TOKEN UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run
  --no-env-file --frozen pytest tests/test_readiness.py tests/test_health.py -q`
  passed (`8 passed`).
- Full suite passed twice with
  `env -u DATABASE_URL -u REDIS_URL -u OPENAI_API_KEY -u NOTION_TOKEN
  -u TELEGRAM_BOT_TOKEN UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run
  --no-env-file --frozen pytest -q` (`202 passed, 3 skipped` each run).
- `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-pycache python3 -m compileall
  -q src alembic tests` and `git diff --check` passed.
- `uv run --no-env-file --frozen pytest -q tests/test_notion_api_reader_client.py
  tests/test_notion_reader_tool.py tests/test_mock_notion_reader_client.py
  tests/test_notion_index_page_api.py` passed (`24 passed`).
- `uv run --no-env-file --frozen pytest -q` passed (`207 passed, 3 skipped`).
- `git diff --check` passed.
- `uv run --no-env-file --frozen pytest -q tests/test_notion_api_reader_client.py
  tests/test_notion_reader_tool.py tests/test_mock_notion_reader_client.py
  tests/test_notion_full_index_api.py tests/test_notion_index_page_api.py`
  passed (`29 passed`).
- `uv run --no-env-file --frozen pytest -q` passed (`212 passed, 3 skipped`).
- `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-step69-pycache python3 -m
  compileall -q src tests/test_notion_api_reader_client.py
  tests/test_notion_reader_tool.py tests/test_notion_full_index_api.py` and
  `git diff --check` passed.
- `uv run --no-env-file --frozen pytest -q tests/test_notion_api_writer_client.py
  tests/test_notion_writer_tool.py tests/test_supplement_api.py
  tests/test_telegram_api.py` passed (`31 passed`).
- `uv run --no-env-file --frozen pytest -q` passed (`214 passed, 3 skipped`).
- `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-step70-pycache python3 -m
  compileall -q src tests/test_notion_api_writer_client.py` and
  `git diff --check` passed.
- Completed roadmap Step 71 by adding explicit `NOTION_BACKEND=mock|live`
  configuration with mock as the safe default.
- Wired mock reader and writer from the same page dataset, and wired live
  reader/writer REST adapters together behind `NotionReaderTool` and
  `NotionWriterTool`.
- Live mode now requires `NOTION_TOKEN` and invalid or incomplete live
  configuration fails closed without falling back to mock data.
- Updated README, deployment, architecture, workflow, permission, and API
  contract docs plus `.env.example` and preflight reporting.
- Added configuration, backend wiring, and preflight matrix tests.
- `uv run pytest tests/test_config.py tests/test_notion_backend_wiring.py
  tests/test_preflight.py tests/test_preflight_notion_backend.py` passed
  (`17 passed`).
- `uv run pytest` passed (`225 passed, 3 skipped`).
- `uv run --no-env-file --frozen python -m compileall -q src tests`,
  `uv run --no-env-file --frozen python scripts/preflight.py --profile api`,
  and `git diff --check` passed.
- Completed roadmap Step 72 with read-only pending proposal list/detail APIs,
  deterministic proposal content/citation responses, and external Notion page
  target resolution before internal FK persistence.
- Added fail-closed unknown-target handling and kept review reads separate from
  the existing human accept/reject/write workflow.
- Added reviewable proposal and target-resolution regressions; full suite passed
  (`227 passed, 3 skipped`), compileall, and `git diff --check` passed.
- Completed roadmap Step 73 with Telegram `/pages`, target-aware
  `/ingest --page <external_page_id>`, deterministic proposal previews, and a
  select-to-accept flow that reuses append-only review and immediate re-index.
- Preserved backward compatibility for unscoped `/ingest`; missing targets
  remain blocked by the existing accept write-policy guardrail.
- Added deterministic Telegram E2E coverage; focused Telegram/review tests
  passed (`29 passed`), full suite passed (`228 passed, 3 skipped`), compileall,
  and `git diff --check` passed.

### Next
- Wait for explicit approval before executing Step 74:
  `Add API and Telegram trust boundaries`.

## 2026-06-20 (Steps 53-54 Query Embedding QA + Vector Regression Coverage)

### Highlights
- Completed roadmap Step 53 by wiring QA through query embeddings before
  retrieval in `src/orchestrators/qa_orchestrator.py`.
- Updated QA retrieval so successful pgvector requests stay semantic-only,
  while query-time degradation uses deterministic lexical fallback instead of
  mixing local embedding scores into QA fallback ranking.
- Added QA workflow metadata for `retrieval_mode`,
  `retrieval_fallback_reason`, `embedding_provider`,
  `embedding_model`, `embedding_dimensions`, and
  `vector_distance_metric`.
- Wired the new QA embedding dependency through both `/api/qa` and Telegram
  `/ask` route construction paths.
- Added deterministic tests for QA orchestrator vector-path behavior,
  citation de-duplication, lexical fallback reasons, QA API fallback
  behavior, Telegram QA regression, and mock demo regression.
- Updated `docs/00-design-doc.md`, `docs/05-rag-design.md`, and
  `docs/08-observability.md` to reflect Step 53 runtime behavior.
- Moved the roadmap current pointer to Step 54:
  `Add deterministic vector retrieval regression coverage`.
- Completed roadmap Step 54 by adding a standalone deterministic vector
  retrieval regression eval:
  `tests/evals/vector_retrieval_eval.py`.
- Added focused eval coverage in
  `tests/evals/test_vector_retrieval_eval.py` for semantic ranking,
  lexical fallback reasons, citation de-duplication, and production-RAG
  exclusion.
- Added one more retriever regression in `tests/test_retriever.py` so
  QA-style lexical fallback explicitly stays off the old local embedding-score
  mixing path.
- Updated `docs/07-evaluation-plan.md` to document the Step 54 standalone
  vector retrieval regression command and expected output.
- Moved the roadmap current pointer to Step 55:
  `Run opt-in live PostgreSQL + OpenAI smoke verification`.
- Completed roadmap Step 55 by adding the standalone opt-in live smoke
  command `tests/evals/live_vector_smoke.py`.
- Added live smoke coverage for shared indexing with real embeddings,
  PostgreSQL-side pgvector retrieval, citation de-duplication,
  insufficient-info behavior, and duplicate-safe page re-index.
- Added deterministic smoke-helper coverage in
  `tests/evals/test_live_vector_smoke.py` so fixture shape and config gating
  stay tested without requiring live credentials.
- Updated `docs/07-evaluation-plan.md` and `docs/10-deployment.md` with the
  Step 55 prerequisites, command, temp-database behavior, and debug option.
- Marked the roadmap complete through Step 55 with no remaining todo step.

### Issues and Decisions
- Kept query-time fallback as workflow `status=succeeded` with
  `retrieval_fallback_reason` metadata instead of mapping safe degradation to
  workflow `failure_reason`.
- Preserved old local embedding scoring support only for direct retriever
  callers and non-QA deterministic fixtures; the QA path now explicitly
  disables that legacy mixed scoring during lexical fallback.
- Used fake retrievers and fake embedding clients for vector-success coverage
  because default deterministic tests run on SQLite, not PostgreSQL +
  pgvector.
- For Step 54, chose a standalone offline eval with a fake embedding fixture
  and fake vector-capable repository fixture instead of trying to force real
  pgvector into the default regression suite.
- Kept the existing golden-question retrieval and citation evals unchanged as
  lexical/production-safety baselines, then added the new vector eval beside
  them instead of overloading their SQLite-only fixture.
- Kept Step 55 focused on the live vector path only: real OpenAI embeddings
  and real PostgreSQL + pgvector are exercised, but the answer provider stays
  deterministic and local so the smoke result is about storage/retrieval
  safety rather than chat-output variance.
- Reused the existing live pgvector temp-database pattern so the smoke command
  does not pollute the persistent local `learnloop` database.
- Left the live smoke run opt-in and out of the default suite because the
  local environment did not have `OPENAI_API_KEY`, and the roadmap requires
  live provider calls to remain separate from default regression coverage.

### Verification
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_qa_orchestrator.py tests/test_retriever.py tests/test_qa_api.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_telegram_api.py tests/test_mock_demo_script.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_retriever.py tests/evals/test_retrieval_eval.py
  tests/evals/test_citation_accuracy_eval.py
  tests/evals/test_vector_retrieval_eval.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  tests/evals/vector_retrieval_eval.py`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  tests/evals/retrieval_eval.py`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  tests/evals/citation_accuracy_eval.py`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/evals/test_live_vector_smoke.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  tests/evals/live_vector_smoke.py --help`
- Completed local verification:
  `git diff --check`

### Next
- No roadmap todo step remains. Next work should define a new roadmap phase or
  switch to release hardening using the new live smoke command when
  credentials are available.

## 2026-06-21 (Step 55 Live Smoke Schema Fix)

### Highlights
- Fixed `tests/evals/live_vector_smoke.py` so the temporary smoke database now
  applies the real Alembic migrations to `head` instead of manually creating a
  partial table subset.
- Kept the smoke flow isolated: it still creates a temporary database and
  drops it after the run unless debug retention is requested.
- Added deterministic coverage in `tests/evals/test_live_vector_smoke.py` to
  verify the migration-backed setup creates `source_documents` and the
  `knowledge_chunks` foreign-key dependencies.
- Updated `docs/07-evaluation-plan.md`, `docs/10-deployment.md`, and the
  Step 55 roadmap verification notes to reflect the migration-backed schema
  setup.

### Issues and Decisions
- The live smoke failure came from partial `Base.metadata.create_all()` setup:
  `knowledge_chunks` was created without the full dependency chain from the
  real schema path.
- Chose Alembic `upgrade head` for the temporary smoke DB instead of adding
  more manual table-registration code, so the smoke contract stays aligned
  with production schema behavior.
- Did not run `./scripts/run_live.sh live-tests` locally because this fix only
  needed deterministic verification and the live path must remain opt-in.

### Verification
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/evals/test_live_vector_smoke.py tests/test_pgvector_migration.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  tests/evals/live_vector_smoke.py --help`
- Completed local verification:
  `git diff --check`

### Next
- Manually run
  `LEARNLOOP_RUN_LIVE_VECTOR_SMOKE=1 ./scripts/run_live.sh live-tests`
  in a credentialed environment to confirm the repaired live path end to end.

## 2026-06-19 (Roadmap Planning + Steps 48-49 Vector Rollout Foundation)

### Highlights
- Added a new roadmap phase, `Wire Live Embeddings + pgvector Retrieval`, to
  `dev_state/PROJECT_ROADMAP.md`.
- Added Steps 48-55 with table rows plus a detailed todo section so each step
  now includes title, status, purpose, scope, success criteria, verification,
  documentation impact, and dependencies.
- Moved the roadmap current pointer to Step 48:
  `Decide live embedding and pgvector retrieval contract`.
- Completed Step 48 by auditing the current embedding and retrieval code paths
  and documenting the live vector contract in
  `docs/decisions/0003-live-embedding-pgvector-contract.md`.
- Updated `docs/05-rag-design.md`, `docs/08-observability.md`, and
  `docs/10-deployment.md` so the contract is reflected in RAG, fallback,
  observability, and rollout notes.
- Moved the roadmap current pointer to Step 49:
  `Add real pgvector schema support safely`.
- Completed Step 49 by adding a reusable `Vector` SQLAlchemy type,
  a new Alembic revision for pgvector rollout foundation, and deterministic
  migration coverage for fresh and populated databases.
- Updated `src/db/models.py` so `knowledge_chunks` now has nullable live
  `embedding` storage while preserving legacy `embedding_text`.
- Updated `docs/00-design-doc.md` and `docs/10-deployment.md` with rollout
  notes for transitional storage, indexes, extension handling, and downgrade
  behavior.
- Moved the roadmap current pointer to Step 50:
  `Generate and store chunk vectors in the shared indexing path`.
- Completed Step 50 by wiring page indexing, manual incremental sync, and
  auto-after-accept re-index through `EmbeddingClient` before chunk
  persistence.
- Updated `src/orchestrators/notion_page_index_orchestrator.py` to fail
  closed when embeddings cannot be generated and to record embedding provider,
  model, dimensions, token usage, and estimated cost in indexing workflow
  metadata.
- Updated `src/repositories/chunk_repository.py` so successful re-index now
  stores both live `embedding` vectors and transitional `embedding_text`.
- Updated route wiring, demo support, and deterministic tests so the shared
  indexing path stays at
  `Indexing Orchestrator -> EmbeddingClient -> ChunkRepository`.
- Moved the roadmap current pointer to Step 51:
  `Define safe legacy chunk backfill behavior`.
- Completed Step 51 by documenting that legacy NULL-vector chunks are repaired
  through page-scoped re-index, not startup-wide automatic backfill.
- Updated `docs/05-rag-design.md` and `docs/10-deployment.md` so the rollout
  behavior is explicit: current production QA remains lexical-only until later
  query-embedding steps, and future maintenance backfill must still reuse the
  shared page indexing flow page by page.
- Added deterministic mixed-fixture coverage for Step 51:
  lexical retrieval remains safe when some chunks have vectors and some do
  not, and manual incremental sync backfills only the requested legacy page.
- Moved the roadmap current pointer to Step 52:
  `Implement repository-owned PostgreSQL pgvector top-k retrieval`.
- Completed Step 52 by moving semantic top-k ranking into
  `ChunkRepository.list_production_chunks_by_vector()` so PostgreSQL +
  pgvector now owns cosine-distance ordering while keeping production-safe
  filtering deterministic.
- Updated `src/rag/retriever.py` so semantic retrieval delegates to the
  repository-owned pgvector path when PostgreSQL is available, while existing
  non-PostgreSQL lexical behavior remains the deterministic fallback for
  local test fixtures and pre-Step-53 QA.
- Added opt-in live repository coverage in
  `tests/test_chunk_repository_pgvector_live.py` for page-filter-before-top-k,
  section-filter-before-top-k, production-safe source-kind scope, and
  NULL-vector exclusion.
- Updated `docs/01-architecture.md` and `docs/05-rag-design.md` to record
  the repository-owned retrieval boundary and to keep QA lexical-only until
  Step 53 starts generating query embeddings.
- Moved the roadmap current pointer to Step 53:
  `Switch QA to query embeddings with deterministic fallback`.

### Issues and Decisions
- Step 48 stayed documentation-only, but Step 49 added schema, migration, and
  deterministic test coverage for the rollout foundation.
- Earlier roadmap planning left Step 48 intentionally undecided for embedding
  model, dimensions, distance metric, vector index, and fallback policy so
  those choices would be made explicitly here instead of being assumed.
- Audited current implementation and confirmed the live vector path is not
  wired yet: indexing does not call `EmbeddingClient`, `knowledge_chunks`
  still stores `embedding_text`, and QA is lexical-only by default.
- Locked the live contract to OpenAI `text-embedding-3-small` with explicit
  `dimensions=1536`, cosine distance, exact filtered pgvector search as the
  correctness baseline, and HNSW as the approved acceleration path.
- Chose deterministic lexical fallback for query-time vector failures or
  missing vectors, while keeping future indexing-time embedding failures
  fail-closed instead of silently writing mixed vector state.
- Kept the Python side dependency-light for now by implementing a local vector
  SQLAlchemy type instead of adding a new package just for Step 49.
- Chose a PostgreSQL-only partial HNSW cosine index plus general B-tree filter
  indexes, while making the migration deterministic on SQLite for test
  coverage by skipping Postgres-only operations there.
- Kept `embedding_text` during rollout and made the new `embedding` column
  nullable so existing rows survive upgrade without forced backfill.
- For Step 50, moved embedding generation ahead of block and chunk replacement
  so missing provider configuration or embedding failures stop the indexing
  workflow before page content is partially rewritten.
- Kept rollout compatibility by writing both `embedding` and `embedding_text`
  on successful indexing instead of changing retrieval storage in the same
  step.
- For Step 51, chose page-scoped re-index as the only approved MVP repair
  path for legacy NULL-vector chunks instead of inventing a startup job or raw
  SQL backfill path.
- Kept current QA behavior explicit: mixed vector state is safe today because
  production QA still uses deterministic lexical retrieval until later steps
  enable query embeddings.
- For Step 52, kept DB-side semantic ranking inside the repository instead of
  moving pgvector SQL into the retriever or orchestrator, preserving the
  repository boundary from `AGENTS.md`.
- Used repository-owned filter-before-top-k semantics for page and section
  scope so future QA embeddings cannot widen retrieval beyond the caller's
  deterministic scope.
- Kept Step 52 intentionally short of QA query embeddings; Step 53 remains the
  first step that changes QA request behavior.

### Verification
- Completed local verification:
  `git diff --check`
- Completed local verification:
  `git diff -- docs/05-rag-design.md docs/08-observability.md
  docs/10-deployment.md docs/decisions/0003-live-embedding-pgvector-contract.md
  dev_state/PROJECT_ROADMAP.md dev_state/DAILY_LOG.md`
- Completed local verification:
  `git status --short`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_db_vector_type.py tests/test_pgvector_migration.py
  tests/test_chunk_repository.py tests/test_retriever.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_notion_index_page_api.py tests/test_qa_api.py -q`
- Completed local verification:
  `docker compose up -d postgres`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen alembic upgrade head`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen alembic current`
- Completed local verification:
  `docker compose exec -T postgres psql -U learnloop -d learnloop -c
  "SELECT column_name, udt_name FROM information_schema.columns WHERE table_name = 'knowledge_chunks' ORDER BY ordinal_position;"`
- Completed local verification:
  `docker compose exec -T postgres psql -U learnloop -d learnloop -c
  "SELECT indexname FROM pg_indexes WHERE tablename = 'knowledge_chunks' ORDER BY indexname;"`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_chunk_repository.py tests/test_notion_index_page_api.py
  tests/test_supplement_api.py tests/test_telegram_api.py
  tests/test_mock_notion_reader_client.py tests/evals/test_manual_sync_eval.py
  tests/test_mock_demo_script.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_retriever.py tests/test_notion_index_page_api.py
  tests/test_qa_api.py -q`
- Completed local verification:
  `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_chunk_repository.py tests/test_retriever.py
  tests/test_notion_index_page_api.py tests/test_qa_api.py -q`
- Completed local verification:
  `docker compose up -d postgres`
- Completed local verification:
  `LEARNLOOP_RUN_PGVECTOR_TESTS=1 UV_CACHE_DIR=/private/tmp/learnloop-uv-cache
  uv run --frozen pytest tests/test_chunk_repository_pgvector_live.py -q`
- Completed local verification:
  `git diff --check`

### Next
- Execute Step 53 by generating query embeddings in QA, routing retrieval
  through the repository-owned pgvector path, and preserving deterministic
  lexical fallback plus grounded citation behavior.

## 2026-06-18 (Step 47 Security Review)

### Highlights
- Completed Step 47 by adding shared sensitive-text redaction for structured
  log events and surfaced external error strings:
  `src/observability/redaction.py`.
- Wired request-log formatting to sanitize secrets and private-text markers
  before JSON output:
  `src/observability/logger.py`.
- Hardened Telegram and provider external error paths so bearer tokens, bot
  tokens, and `raw_text` or `source_text` values are redacted before they can
  reach tool failures or API responses:
  `src/tools/telegram_bot_tool.py`, `src/providers/llm.py`,
  `src/providers/embedding.py`, and
  `src/orchestrators/telegram_gateway_orchestrator.py`.
- Added focused regression coverage for log redaction, Telegram failure-path
  redaction, and `.env*` Git tracking checks:
  `tests/test_logger.py`, `tests/test_telegram_bot_tool.py`, and
  `tests/test_security_review.py`.
- Added a short security checklist and local secret-handling rules to the
  guardrails, observability, and deployment docs:
  `docs/03-guardrails.md`, `docs/08-observability.md`, and
  `docs/10-deployment.md`.
- Updated roadmap current pointer and Step 47 status:
  `dev_state/PROJECT_ROADMAP.md`.

### Issues and Decisions
- Kept the hardening scope narrow: sanitize surfaced text at shared
  observability and external-client boundaries instead of refactoring
  orchestrator behavior.
- Added defense in depth by sanitizing both the structured log formatter and
  Telegram/provider error propagation, so future logging or API wiring has a
  smaller leak surface.
- Left business behavior unchanged; this step only tightens secret and private
  text exposure paths.

### Verification
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_logger.py tests/test_telegram_bot_tool.py
  tests/test_security_review.py tests/test_health.py tests/test_telegram_api.py -q`
  passed (`21 passed`).
- `git ls-files '.env' '.env.*'` returned only `.env.example`.
- `git diff --check` passed.

### Next
- Roadmap has no remaining todo steps. Next work should be user-directed polish,
  packaging, or release/demo preparation.

## 2026-06-17 (Ignore Local History)

### Highlights
- Added `.history/` to `.gitignore` so local editor history is not committed.
- Removed previously tracked `.history` files from the Git index with
  `git rm --cached -r .history`.
- Completed Step 42 by rewriting `README.md` with a real local setup flow for
  `uv`, environment variables, Docker Compose, Alembic migration, `/health`,
  and bundled mock Notion demo QA.
- Documented that the app currently reads process environment variables
  directly, so `.env` must be loaded into the shell before running API or
  Alembic commands.
- Added README demo examples for indexing `page-nlp-week5` and asking grounded
  QA over bundled synthetic mock data.
- Updated roadmap current pointer and Step 42 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 43 by adding a Mermaid architecture diagram to `README.md`
  so the route/orchestrator/provider/tool/repository flow is visible in one
  place.
- Added deterministic demo script `scripts/run_mock_demo.py` that exercises
  `/health`, `POST /api/notion/index/page`, and `POST /api/qa` through the
  FastAPI app using bundled mock pages, in-memory SQLite, and a fake provider.
- Added focused regression coverage for the demo script:
  `tests/test_mock_demo_script.py`.
- Updated roadmap current pointer and Step 43 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 44 by adding versioned runtime prompt bundles under
  `docs/prompts/` for QA and supplement proposal flows.
- Added `PromptTemplateLoader` so orchestrators load prompt bundles through a
  service boundary instead of hard-coded inline prompt strings:
  `src/services/prompt_template_loader.py`.
- Wired QA, supplement proposal, and Telegram reuse paths to record
  `provider_name`, `model`, `prompt_id`, and `prompt_version` in workflow
  metadata.
- Added focused prompt loader coverage and extended QA/supplement workflow
  tests to assert prompt metadata:
  `tests/test_prompt_template_loader.py`, `tests/test_qa_api.py`, and
  `tests/test_supplement_api.py`.
- Updated roadmap current pointer and Step 44 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 45 by expanding the shared workflow `failure_reason`
  taxonomy for provider and Telegram external failures.
- Updated QA, supplement proposal, and Telegram failure mapping so
  deterministic external failures no longer collapse to `UNKNOWN_ERROR`.
- Added focused regression coverage for `PROVIDER_NOT_FOUND`,
  `LLM_PROVIDER_ERROR`, `TELEGRAM_NOT_CONFIGURED`, and
  `TELEGRAM_FILE_DOWNLOAD_FAILED`:
  `tests/test_qa_api.py`, `tests/test_supplement_api.py`, and
  `tests/test_telegram_api.py`.
- Updated observability and API contract docs to reflect the standardized
  failure taxonomy:
  `docs/00-design-doc.md`, `docs/08-observability.md`, and
  `docs/09-api-contract.md`.
- Updated roadmap current pointer and Step 45 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 46 by adding a shared `CostTracker` service for estimated LLM
  and embedding cost calculation:
  `src/services/cost_tracker.py`.
- Wired QA, supplement proposal, and Telegram-delegated QA/proposal flows to
  record `estimated_cost` alongside `token_input` and `token_output` in
  workflow metadata when token usage is available.
- Preserved fail-safe behavior for unknown models by recording
  `estimated_cost=null` instead of inventing a price.
- Added focused cost tracker and workflow metadata regression coverage:
  `tests/test_cost_tracker.py`, `tests/test_qa_api.py`,
  `tests/test_supplement_api.py`, and `tests/test_telegram_api.py`.
- Updated workflow and observability docs for cost metadata behavior:
  `docs/00-design-doc.md`, `docs/02-workflows.md`, and
  `docs/08-observability.md`.
- Updated roadmap current pointer and Step 46 status:
  `dev_state/PROJECT_ROADMAP.md`.

### Issues and Decisions
- Kept local `.history` files on disk and removed them from Git tracking only.
- Left unrelated working tree changes untouched.
- Kept Step 42 scoped to documentation and local verification instead of
  expanding runtime behavior.
- Used the already bundled mock Notion reader path for the README demo so the
  setup flow stays inside the existing tool boundary and does not require a
  real Notion token.
- Docker daemon access was unavailable in this environment, so runtime setup
  verification used focused tests plus an API-level smoke check with a fake
  provider instead of a live Docker/Postgres run.
- Kept the new demo script deterministic and architecture-aligned by routing
  through FastAPI endpoints with dependency overrides instead of calling
  repositories or tools directly.
- Suppressed request-log noise inside the demo script so README output stays
  clean and portfolio-friendly.
- Kept runtime prompts under `docs/prompts/*.md` and made them live only when
  code explicitly loads them, so development docs remain separate from runtime
  retrieval by default.
- Passed prompt loading into orchestrators as a service dependency instead of
  reading files directly in routes or provider adapters.
- Kept internal validation and state-transition failures on `UNKNOWN_ERROR`
  for now, and only standardized external/tool/provider failures covered by
  the current design and workflow docs.
- Kept cost estimation inside a dedicated service so routes still only compose
  dependencies and orchestrators stay responsible for workflow metadata.
- Recorded `estimated_cost` only when a workflow has deterministic model
  pricing. Unknown models remain explicit `null` so the backend does not guess.

### Verification
- Checked `git ls-files` before cleanup and confirmed tracked `.history` files
  existed.
- Re-checked `git status --short` after cleanup to confirm `.history` is staged
  for removal and new `.history` files are ignored.
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_health.py tests/test_mock_notion_reader_client.py
  tests/test_notion_index_page_api.py tests/test_qa_api.py -q` passed
  (`14 passed`).
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_config.py -q` passed (`2 passed`).
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python - <<'PY'`
  smoke check passed for `/health`, `POST /api/notion/index/page`, and
  `POST /api/qa` using bundled mock data plus a fake provider.
- `git diff --check` passed.
- `docker compose ps` could not run inside the default sandbox because Docker
  daemon access was not permitted.
- Escalated `docker compose up -d` confirmed the environment still had no
  running Docker daemon, so live Compose/Postgres verification was not
  available in this session.
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_mock_demo_script.py tests/test_health.py
  tests/test_mock_notion_reader_client.py tests/test_notion_index_page_api.py
  tests/test_qa_api.py -q` passed (`15 passed`).
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  scripts/run_mock_demo.py` passed and printed the demo summary with indexed
  page, provider/model, citation path, and grounded answer.
- `git diff --check` passed after Step 43.
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_prompt_template_loader.py tests/test_qa_api.py
  tests/test_supplement_api.py tests/test_telegram_api.py
  tests/test_mock_demo_script.py -q` passed (`27 passed`).
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  scripts/run_mock_demo.py` passed after prompt-loader wiring and still printed
  the expected demo summary.
- `git diff --check` passed after Step 44.
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_workflow_run_service.py tests/test_qa_api.py
  tests/test_supplement_api.py tests/test_telegram_api.py -q` passed
  (`32 passed`).
- `git diff --check` passed after Step 45.
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_cost_tracker.py tests/test_qa_api.py tests/test_supplement_api.py
  tests/test_telegram_api.py tests/test_mock_demo_script.py -q` passed
  (`31 passed`).
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen python
  scripts/run_mock_demo.py` passed after cost-tracker wiring.
- `git diff --check` passed after Step 46.

### Next
- Execute Step 47: perform security review and final pre-demo safety pass.

## 2026-06-16 (Steps 37-41 Evaluation Scripts and Demo Data)

### Highlights
- Completed Step 37 by adding deterministic retrieval hit-rate evaluation:
  `tests/evals/retrieval_eval.py`.
- Added focused tests for full-hit output, missing expected path behavior, and
  non-production chunk exclusion:
  `tests/evals/test_retrieval_eval.py`.
- Updated `docs/07-evaluation-plan.md` with exact-match top-k hit-rate rules,
  synthetic fixture scope, and standalone command output.
- Updated roadmap current pointer and Step 37 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 38 by adding deterministic citation accuracy evaluation:
  `tests/evals/citation_accuracy_eval.py`.
- Added focused citation accuracy tests for full accuracy, missing expected
  path behavior, threshold handling, invalid threshold validation, and
  non-production path exclusion:
  `tests/evals/test_citation_accuracy_eval.py`.
- Updated `docs/07-evaluation-plan.md` with exact-match citation accuracy
  rules, threshold behavior, and standalone command output.
- Updated roadmap current pointer and Step 38 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 39 by adding deterministic write-safety evaluation:
  `tests/evals/write_safety_eval.py`.
- Added focused write-safety tests for summary output and all safety checks:
  `tests/evals/test_write_safety_eval.py`.
- Updated `docs/07-evaluation-plan.md` with write-safety invariants and
  standalone command output.
- Updated roadmap current pointer and Step 39 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 40 by adding deterministic manual sync reconciliation
  evaluation:
  `tests/evals/manual_sync_eval.py`.
- Added focused manual sync eval tests:
  `tests/evals/test_manual_sync_eval.py`.
- Fixed page replacement ordering so old Notion chunks are deleted before
  replacing page blocks:
  `src/repositories/chunk_repository.py` and
  `src/orchestrators/notion_page_index_orchestrator.py`.
- Added repository coverage for page-scoped chunk deletion:
  `tests/test_chunk_repository.py`.
- Updated `docs/07-evaluation-plan.md` with manual sync reconciliation rules
  and standalone command output.
- Updated roadmap current pointer and Step 40 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 41 by adding safe mock Notion demo pages under
  `mock_data/notion_pages/` for NLP, ISO 9001, and RAG examples.
- Added a JSON-backed mock Notion reader adapter so local tool wiring can load
  demo pages through the existing read-only tool boundary:
  `src/tools/mock_notion_reader_client.py`.
- Wired the default local tool registry to load bundled mock pages when present
  and added explicit settings support for `MOCK_NOTION_DATA_DIR`:
  `src/app/dependencies.py`, `src/app/config.py`, and `.env.example`.
- Added focused tests for mock page loading, safety metadata validation, demo
  page indexing, and config loading:
  `tests/test_mock_notion_reader_client.py` and `tests/test_config.py`.
- Updated roadmap current pointer and Step 41 status:
  `dev_state/PROJECT_ROADMAP.md`.

### Issues and Decisions
- Used a synthetic in-memory SQLite fixture derived from golden questions so
  Step 37 is deterministic before public mock Notion data exists.
- Exercised the real repository and retriever path:
  `ChunkRepository -> ProductionChunkRetriever`.
- Kept matching exact by Notion path and kept the eval scoped to
  `source_kind="notion"`.
- Added a standalone script path fix so `python tests/evals/retrieval_eval.py`
  works outside pytest package import mode.
- Reused the synthetic retrieval fixture for citation evaluation so Step 38
  exercises the same production-safe retriever boundary.
- Counted a citation as accurate only when a returned citation path exactly
  matches at least one expected golden source path.
- Kept citation evaluation deterministic and answer-text-free; no LLM-as-judge.
- Used the in-memory Notion writer client for write-safety evaluation so no
  real Notion write is performed.
- Checked append-only behavior at the tool boundary: original/manual blocks
  unchanged, only `append_ai_supplement_zone` operations recorded, target paths
  stay under `AI Supplement Zone`, retries are idempotent, and policy
  violations perform no write.
- Used an in-memory Notion reader and SQLite fixture for manual sync
  reconciliation so no real Notion read/write is performed.
- Exercised the real path:
  `NotionIncrementalIndexOrchestrator -> NotionPageIndexOrchestrator ->
  repositories -> ProductionChunkRetriever`.
- Deleted old page chunks before block replacement to avoid stale orphan chunks
  being retrieved globally after manual deletion.
- Checked both raw chunk storage and production retrieval for the deleted AI
  supplement marker.
- Chose explicit `demo_metadata` safety flags inside each mock page so the
  public demo dataset self-declares synthetic-only, public-safe content.
- Reused `build_block_paths()` when loading mock JSON so demo pages follow the
  same deterministic path-building logic as indexed Notion content.
- Loaded bundled mock pages through the Notion reader client boundary instead
  of seeding repositories directly, so the demo path stays aligned with the
  architecture rule.

### Verification
- `uv run --frozen python tests/evals/retrieval_eval.py` passed and printed
  `retrieval_hit_rate: 1.000 (3/3)`.
- `uv run --frozen pytest tests/evals/test_retrieval_eval.py -q` passed
  (`3 passed`).
- `uv run --frozen pytest tests/evals -q` passed (`5 passed`).
- `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-pycache uv run --frozen python -m
  compileall -q tests/evals` passed.
- `uv run --frozen pytest -q` passed (`121 passed`).
- `git diff --check` passed.
- `uv run --frozen python tests/evals/citation_accuracy_eval.py` passed and
  printed `citation_accuracy: 1.000 (3/3)`.
- `uv run --frozen pytest tests/evals/test_citation_accuracy_eval.py -q`
  passed (`5 passed`).
- `uv run --frozen pytest tests/evals -q` passed (`10 passed`).
- `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-pycache uv run --frozen python -m
  compileall -q tests/evals` passed.
- `uv run --frozen pytest -q` passed (`126 passed`).
- `git diff --check` passed after Step 38.
- `uv run --frozen python tests/evals/write_safety_eval.py` passed and printed
  `write_safety: pass (4/4)`.
- `uv run --frozen pytest tests/evals/test_write_safety_eval.py -q` passed
  (`2 passed`).
- `uv run --frozen pytest tests/evals -q` passed (`12 passed`).
- `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-pycache uv run --frozen python -m
  compileall -q tests/evals` passed.
- `uv run --frozen pytest -q` passed (`128 passed`).
- `git diff --check` passed after Step 39.
- `uv run --frozen python tests/evals/manual_sync_eval.py` passed and printed
  `manual_sync_reconciliation: pass (4/4)`.
- `uv run --frozen pytest tests/evals/test_manual_sync_eval.py -q` passed
  (`2 passed`).
- `uv run --frozen pytest tests/evals -q` passed (`14 passed`).
- `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-pycache uv run --frozen python -m
  compileall -q tests/evals` passed.
- `uv run --frozen pytest -q` passed (`131 passed`).
- `git diff --check` passed after Step 40.
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_mock_notion_reader_client.py -q` passed (`3 passed`).
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest
  tests/test_config.py tests/test_notion_index_page_api.py -q` passed
  (`8 passed`).
- `UV_CACHE_DIR=/private/tmp/learnloop-uv-cache uv run --frozen pytest -q`
  passed (`134 passed`).
- `git diff --check` passed after Step 41.

### Next
- Execute Step 42: document the local setup flow for `/health` and mock QA.

## 2026-06-04 (Steps 34-36 Telegram and Golden Evaluation Set)

### Highlights
- Completed Step 34 by adding Telegram `/ask` QA command support.
- Added `TelegramQAOrchestrator` to parse optional `--page` and `--section`
  scope flags, delegate to the existing `QAOrchestrator`, and format Notion
  path citations:
  `src/orchestrators/telegram_qa_orchestrator.py`.
- Extended Telegram gateway and route wiring to reuse production RAG QA while
  keeping retrieval/provider logic out of the gateway:
  `src/orchestrators/telegram_gateway_orchestrator.py` and
  `src/app/api/routes/telegram.py`.
- Extended Telegram webhook response fields with QA workflow id,
  insufficient-info status, and citation paths:
  `src/app/schemas/telegram.py`.
- Added Telegram API tests for scoped citation output, missing-question usage,
  and provider failure mapping:
  `tests/test_telegram_api.py`.
- Updated design, workflow, and API contract docs:
  `docs/00-design-doc.md`, `docs/02-workflows.md`, and
  `docs/09-api-contract.md`.
- Updated roadmap current pointer and Step 34 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 35 by adding Telegram `/accept` and `/reject` review commands.
- Added `TelegramReviewOrchestrator` to parse command arguments, derive a
  deterministic Telegram reviewer identity, and delegate to the existing
  `SupplementReviewOrchestrator`:
  `src/orchestrators/telegram_review_orchestrator.py`.
- Extended Telegram gateway and route composition with review result fields:
  `src/orchestrators/telegram_gateway_orchestrator.py`,
  `src/app/api/routes/telegram.py`, and `src/app/schemas/telegram.py`.
- Added Telegram API tests for accept append + immediate re-index, reject
  no-write, accept write-policy fail-closed, and missing reject reason usage:
  `tests/test_telegram_api.py`.
- Updated design, workflow, and API contract docs for Telegram review:
  `docs/00-design-doc.md`, `docs/02-workflows.md`, and
  `docs/09-api-contract.md`.
- Updated roadmap current pointer and Step 35 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 36 by adding the versioned synthetic golden question set:
  `tests/evals/golden_questions.yaml`.
- Added a strict YAML loader and focused tests covering NLP, ISO 9001, and
  accepted `AI Supplement Zone` examples:
  `tests/evals/golden_questions.py` and
  `tests/evals/test_golden_questions.py`.
- Added PyYAML as a locked development dependency and expanded
  `docs/07-evaluation-plan.md` with the golden set contract and deterministic
  evaluation rules.
- Updated roadmap current pointer and Step 36 status:
  `dev_state/PROJECT_ROADMAP.md`.

### Issues and Decisions
- Chose explicit, repeatable scope flags:
  `/ask [--page <page_id>] [--section <notion/path>] <question>`.
- Reused `QAOrchestrator` so Telegram QA keeps the existing production-only
  retrieval policy and deterministic provider failure behavior.
- Kept private question text and citation paths out of Telegram workflow
  metadata; metadata records citation count only.
- `/ask` without a question returns usage text without starting a QA workflow.
- Reused `SupplementReviewOrchestrator` so Telegram accept keeps the existing
  append-only and immediate re-index safety rules.
- Chose `/accept <change_request_id>` and
  `/reject <change_request_id> <reason>` command syntax.
- Telegram chat id is stored as reviewer identity; gateway metadata does not
  store reject reason.
- Kept inline review buttons deferred.
- Kept golden questions synthetic and limited production retrieval scope to
  Notion content.
- Distinguished manual-note expected paths from accepted AI supplement paths;
  pending and rejected content remain forbidden expected results.
- Kept the loader inside the evaluation test harness so no evaluation-only
  dependency or logic enters production runtime.

### Verification
- `uv run pytest tests/test_telegram_api.py -q` passed (`8 passed`).
- `uv run pytest tests/test_qa_api.py tests/test_retriever.py -q` passed
  (`8 passed`).
- `uv run python -m compileall -q src tests/test_telegram_api.py` passed.
- `uv run pytest -q` passed (`112 passed`).
- `git diff --check` passed.
- `uv run pytest tests/test_telegram_api.py -q` passed (`12 passed`).
- `uv run pytest tests/test_supplement_api.py tests/test_notion_writer_tool.py -q`
  passed (`13 passed`).
- `uv run python -m compileall -q src tests/test_telegram_api.py` passed.
- `uv run pytest -q` passed (`116 passed`).
- `git diff --check` passed after Step 35.
- `uv run --frozen python tests/evals/golden_questions.py` loaded 3 golden
  questions successfully.
- `uv run --frozen pytest tests/evals/test_golden_questions.py -q` passed
  (`2 passed`).
- `PYTHONPYCACHEPREFIX=/private/tmp/learnloop-pycache uv run --frozen python -m
  compileall -q tests/evals` passed.
- `uv run --frozen pytest -q` passed (`118 passed`).
- `git diff --check` passed after Step 36.

### Next
- Execute Step 37: measure retrieval hit rate.

## 2026-06-02 (Step 32 Telegram Entrypoint)

### Highlights
- Completed Step 32 by adding Telegram webhook entrypoint:
  `POST /api/telegram/webhook`.
- Added Telegram gateway orchestrator with deterministic command routing for `/help` and `/health`:
  `src/orchestrators/telegram_gateway_orchestrator.py`.
- Added Telegram send-message local tool adapter and clients:
  `src/tools/telegram_bot_tool.py`.
- Wired Telegram tool into shared tool registry with env-based client selection:
  `src/app/dependencies.py`.
- Added Telegram API schemas and route wiring:
  `src/app/schemas/telegram.py`,
  `src/app/api/routes/telegram.py`,
  `src/app/api/routes/__init__.py`,
  `src/app/api/__init__.py`,
  and `src/app/main.py`.
- Added config/env support for `TELEGRAM_BOT_TOKEN`:
  `src/app/config.py`, `.env.example`, and `tests/test_config.py`.
- Added Step 32 API tests:
  `tests/test_telegram_api.py`.
- Updated workflow/design/API docs and roadmap pointer:
  `docs/00-design-doc.md`, `docs/02-workflows.md`, `docs/09-api-contract.md`, and `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 33 by adding Telegram ingestion command support on the same webhook entrypoint:
  `/ingest` now supports PDF document and screenshot batch ingestion.
- Added Telegram ingestion orchestrator to route media uploads into existing ingestion + supplement proposal flows:
  `src/orchestrators/telegram_ingestion_orchestrator.py`.
- Extended Telegram gateway orchestrator to route `/ingest` and media uploads while keeping Telegram API access behind tools:
  `src/orchestrators/telegram_gateway_orchestrator.py`.
- Extended Telegram bot local tool adapter with deterministic file download action:
  `src/tools/telegram_bot_tool.py` and `src/tools/__init__.py`.
- Extended Telegram route/schema wiring for caption/document/photo payloads and ingestion result fields:
  `src/app/api/routes/telegram.py`,
  `src/app/schemas/telegram.py`,
  and `src/app/schemas/__init__.py`.
- Added Step 33 API tests for PDF and screenshot ingestion to pending change requests:
  `tests/test_telegram_api.py`.

### Issues and Decisions
- Kept bot gateway scope minimal in Step 32: only command parsing and reply dispatch, no ingestion/QA/review business logic.
- Used `ToolRegistry -> TelegramBotTool` for Telegram API calls to keep route/orchestrator decoupled from external client code.
- Chose deterministic skip behavior for non-text updates (`handled=false`, `skipped_reason=NO_TEXT_MESSAGE`).
- Chose deterministic fail path for missing bot token via `TELEGRAM_NOT_CONFIGURED`.
- Kept gateway boundary clean by delegating ingestion/proposal business logic to a dedicated Telegram ingestion orchestrator.
- Reused existing ingestion and supplement orchestrators instead of creating Telegram-specific duplicate business logic.
- Deduplicated photo variants by `file_unique_id` and batched screenshot ingestion into one source document.

### Verification
- `uv run pytest tests/test_telegram_api.py -q` passed (`3 passed`).
- `uv run pytest tests/test_config.py -q tests/test_health.py -q` passed (`4 passed`).
- `uv run pytest -q` passed (`107 passed`).
- `uv run pytest tests/test_telegram_api.py -q` passed (`5 passed`).
- `uv run pytest tests/test_source_ingest_api.py -q tests/test_supplement_api.py -q` passed (`22 passed`).
- `uv run pytest -q` passed (`109 passed`).

### Next
- Execute Step 34: support Telegram QA commands (`/ask` with citation output).

## 2026-06-01 (Step 31 Accept + Append + Re-index Loop)

### Highlights
- Completed Step 31 by wiring supplement accept workflow to safe append + immediate re-index:
  `pending` review accept now executes append under `AI Supplement Zone` through `NotionWriterTool`,
  triggers immediate page re-index,
  then commits change request status to `accepted`.
- Extended supplement review orchestrator with deterministic follow-up logic:
  `src/orchestrators/supplement_review_orchestrator.py`.
- Added support for page re-index sync mode `auto_after_accept`:
  `src/orchestrators/notion_page_index_orchestrator.py`.
- Added Notion page repository lookup by db id for accept target resolution:
  `src/repositories/notion_page_repository.py`.
- Updated supplement route dependency wiring for Step 31 orchestration path:
  `src/app/api/routes/supplement.py`.
- Added Step 31 API tests:
  `tests/test_supplement_api.py` (accept append+re-index success and write-policy fail-closed path).
- Updated workflow and API docs for Step 31 behavior:
  `docs/02-workflows.md` and `docs/09-api-contract.md`.
- Updated roadmap current pointer and Step 31 status:
  `dev_state/PROJECT_ROADMAP.md`.

### Issues and Decisions
- Chose fail-closed behavior for accept without `target_notion_page_id`:
  return `WRITE_POLICY_VIOLATION` and keep change request `pending`.
- Chose to mark change request `accepted` only after append + re-index both succeed, to avoid non-retryable partial accept state.
- Kept reject/edit-later behavior unchanged and no Notion write calls on those paths.
- Re-index is triggered as an indexing workflow with metadata `sync_mode=auto_after_accept`.

### Verification
- `uv run pytest tests/test_supplement_api.py -q` passed (`9 passed`).
- `uv run pytest tests/test_notion_writer_tool.py -q` passed (`4 passed`).
- `uv run pytest -q` passed (`104 passed`).

### Next
- Execute Step 32: add Telegram entrypoint (`Telegram Bot Integration` phase).

## 2026-05-27 (Step 29-30 Review + Safe Append Tooling)

### Highlights
- Completed Step 29 by adding supplement review state transition APIs:
  `POST /api/supplement/accept`,
  `POST /api/supplement/reject`,
  and `POST /api/supplement/edit-later`.
- Added review orchestrator for deterministic transition checks:
  `src/orchestrators/supplement_review_orchestrator.py`.
- Extended supplement route and schemas for review payloads/responses:
  `src/app/api/routes/supplement.py`,
  `src/app/schemas/supplement.py`,
  and `src/app/schemas/__init__.py`.
- Extended change request repository with read/update helpers:
  `src/repositories/change_request_repository.py`.
- Exported new orchestrator interfaces:
  `src/orchestrators/__init__.py`.
- Added Step 29 API tests:
  `tests/test_supplement_api.py` (accept/reject/edit-later success, invalid transition, not found).
- Updated docs for review workflow and API contract:
  `docs/00-design-doc.md`,
  `docs/02-workflows.md`,
  and `docs/09-api-contract.md`.
- Updated roadmap current pointer and Step 29 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 30 by adding append-only Notion writer local tool adapter:
  `src/tools/notion_writer_tool.py`.
- Added in-memory Notion writer client with idempotency behavior for safe retry:
  `InMemoryNotionWriterClient`.
- Registered and exported the new writer tool:
  `src/tools/__init__.py` and `src/app/dependencies.py`.
- Added Step 30 tool tests:
  `tests/test_notion_writer_tool.py` (append-only path, unchanged original blocks, idempotent retry, not-found, argument validation).
- Updated workflow/API docs for Step 30 tooling behavior:
  `docs/02-workflows.md` and `docs/09-api-contract.md`.
- Updated roadmap current pointer and Step 30 status:
  `dev_state/PROJECT_ROADMAP.md`.

### Issues and Decisions
- Current MVP schema has no dedicated reviewer/reject_reason columns, so Step 29 stores reviewer/reason in workflow metadata while keeping status transitions deterministic.
- Enforced legal transitions as pending-only for review actions to prevent accidental re-review of accepted/rejected requests.
- Kept reject flow no-write by limiting Step 29 to change request status updates only and no Notion writer calls.
- Kept Step 30 scope focused on tool-layer append safety and idempotency only; deferred accept->append->re-index orchestration wiring to Step 31.
- Kept fixed supplement output labels (`Source`, `Summary`, `Key Concepts`, `Notes`) inside tool output to match `AI Supplement Zone` layout rules.

### Verification
- `uv run pytest tests/test_supplement_api.py -q` passed (`8 passed`).
- `uv run pytest tests/test_notion_writer_tool.py -q` passed (`4 passed`).
- `uv run pytest -q` passed (`103 passed`).

### Next
- Execute Step 31: complete accept, append, and immediate page re-index loop.

## 2026-05-26 (Step 26-28 Supplement Proposal Foundation)

### Highlights
- Completed Step 26 by adding deterministic LLM supplement proposal JSON validation.
- Added proposal schema and parser module:
  `src/orchestrators/supplement_proposal_schema.py`.
- Added strict field validation for proposal payload shape:
  `title`, `target_path`, `source`, `summary`, `concepts`, `notes`.
- Added deterministic error mapping for invalid model output via
  `SupplementProposalValidationError` with `error_code/failure_reason=LLM_OUTPUT_INVALID`.
- Added tests for valid JSON, fenced JSON, and invalid output paths:
  `tests/test_supplement_proposal_schema.py`.
- Exported proposal schema utilities from orchestrator package:
  `src/orchestrators/__init__.py`.
- Updated roadmap current pointer and Step 26 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 27 by adding duplicate knowledge detection service:
  `src/services/duplicate_checker.py`.
- Added deterministic duplicate result shape with citation return:
  `DuplicateCheckResult` and `DuplicateMatch` (`chunk_id`, `notion_path`, score, match type).
- Added hash + similarity duplicate checks over production chunks via repository scope filters:
  exact hash match first, then similarity threshold fallback.
- Added duplicate checker tests:
  `tests/test_duplicate_checker.py` (hash match, similarity match, unrelated text, page scope).
- Exported duplicate checker utilities from service package:
  `src/services/__init__.py`.
- Updated roadmap current pointer and Step 27 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 28 by adding supplement proposal API endpoint:
  `POST /api/supplement/propose`.
- Added supplement propose workflow layers:
  `src/orchestrators/supplement_propose_orchestrator.py`,
  `src/app/api/routes/supplement.py`,
  and `src/app/schemas/supplement.py`.
- Added change request repository and wiring:
  `src/repositories/change_request_repository.py`,
  `src/repositories/__init__.py`,
  and `src/repositories/source_document_repository.py`.
- Registered supplement route in API/app wiring:
  `src/app/api/routes/__init__.py`,
  `src/app/api/__init__.py`,
  and `src/app/main.py`.
- Added Step 28 API tests:
  `tests/test_supplement_api.py` (pending creation success, duplicate citation path, invalid LLM JSON failure).
- Updated docs for supplement propose API/workflow:
  `docs/09-api-contract.md` and `docs/02-workflows.md`.
- Updated roadmap current pointer and Step 28 status:
  `dev_state/PROJECT_ROADMAP.md`.

### Issues and Decisions
- `source` and `notes` detail in docs is still high-level, so used a minimal strict schema that is immediately testable and deterministic.
- Accepted JSON wrapped in Markdown code fences to reduce brittle failures with common LLM formatting.
- Kept validation logic in backend code (not prompt-only constraints) to match deterministic guardrail requirements.
- Kept duplicate detection in deterministic backend service layer and used repository-driven production chunk reads only.
- Chose deterministic ranking and tiebreak by `chunk_id` when multiple similarity matches pass threshold.
- Reused duplicate checker in proposal flow so duplicate sources create citation-first pending proposals instead of rewritten content.
- Kept proposal generation no-write by limiting Step 28 to `change_requests` persistence and no Notion write adapter calls.

### Verification
- `uv run pytest tests/test_supplement_proposal_schema.py -q` passed (`5 passed`).
- `uv run pytest -q` passed (`87 passed`).
- `uv run pytest tests/test_duplicate_checker.py -q` passed (`4 passed`).
- `uv run pytest -q` passed (`91 passed`).
- `uv run pytest tests/test_supplement_api.py -q` passed (`3 passed`).
- `uv run pytest -q` passed (`94 passed`).

### Next
- Execute Step 29: add review state transition APIs.

## 2026-05-25 (Step 23-25 Source Ingestion)

### Highlights
- Completed Step 23 by adding YouTube transcript ingestion endpoint:
  `POST /api/ingest/youtube`.
- Added YouTube ingestion workflow layers:
  `src/orchestrators/youtube_ingestion_orchestrator.py`,
  `src/app/api/routes/source_ingest.py`,
  and `src/app/schemas/source_ingest.py`.
- Added transcript parser tool and default adapter:
  `src/tools/youtube_transcript_tool.py`.
- Registered the tool in dependency wiring:
  `src/app/dependencies.py` and `src/tools/__init__.py`.
- Added tests for the new tool and API behavior:
  `tests/test_youtube_transcript_tool.py` and updated
  `tests/test_source_ingest_api.py`.
- Updated ingestion API contract for `/api/ingest/youtube`:
  `docs/09-api-contract.md`.
- Updated roadmap current pointer and Step 23 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 24 by adding image OCR ingestion endpoint:
  `POST /api/ingest/image-ocr`.
- Added image OCR ingestion workflow layers:
  `src/orchestrators/image_ocr_ingestion_orchestrator.py` and
  `src/app/api/routes/source_ingest.py`.
- Added OCR parser tool and default adapter:
  `src/tools/image_ocr_tool.py`.
- Registered the tool in dependency wiring:
  `src/app/dependencies.py` and `src/tools/__init__.py`.
- Added tests for the new tool and API behavior:
  `tests/test_image_ocr_tool.py` and updated
  `tests/test_source_ingest_api.py`.
- Updated ingestion API contract for `/api/ingest/image-ocr`:
  `docs/09-api-contract.md`.
- Updated roadmap current pointer and Step 24 status:
  `dev_state/PROJECT_ROADMAP.md`.
- Completed Step 25 by adding chat text ingestion endpoint:
  `POST /api/ingest/chat-text`.
- Added chat text ingestion workflow layer:
  `src/orchestrators/chat_text_ingestion_orchestrator.py`.
- Extended source ingest route and schemas for chat text payload:
  `src/app/api/routes/source_ingest.py`,
  `src/app/schemas/source_ingest.py`,
  and `src/app/schemas/__init__.py`.
- Added Step 25 API tests:
  `tests/test_source_ingest_api.py` (short-text success + over-limit validation error).
- Updated ingestion API contract for `/api/ingest/chat-text`:
  `docs/09-api-contract.md`.
- Updated roadmap current pointer and Step 25 status:
  `dev_state/PROJECT_ROADMAP.md`.

### Issues and Decisions
- Kept architecture boundary strict: route -> orchestrator -> tool/repository.
- Kept transcript retrieval behind `ToolRegistry` so orchestrator does not call external SDK directly.
- Mapped transcript unavailability to deterministic `YOUTUBE_TRANSCRIPT_NOT_FOUND`.
- Used transcript-derived display name format `YouTube transcript (<video_id>)` to satisfy source display naming rules when video title is unavailable.
- Kept MVP scope: no speech-to-text fallback for videos without transcript.
- Kept image OCR path behind `ToolRegistry` so route/orchestrator do not call OCR libraries directly.
- Mapped OCR failures to deterministic `OCR_FAILED` and kept failure metadata free of raw OCR content.
- Preserved screenshot order by passing uploaded files to OCR parsing in request order and combining text in that order.
- Used deterministic screenshot source display name format `Screenshot batch (<n> images)`.
- Kept chat text ingestion as route -> orchestrator -> repository with deterministic backend length validation.
- Set MVP chat text limit to `10000` characters and mapped over-limit to `INVALID_ARGUMENT` before workflow creation.
- Preserved chat source display rule by accepting explicit `source_display_name` and defaulting to `Chat text`.

### Verification
- `uv run pytest tests/test_youtube_transcript_tool.py -q` passed (`3 passed`).
- `uv run pytest tests/test_source_ingest_api.py -q` passed (`9 passed`).
- `uv run pytest -q` passed (`75 passed`).
- `uv run pytest tests/test_image_ocr_tool.py -q` passed (`3 passed`).
- `uv run pytest tests/test_source_ingest_api.py -q` passed (`11 passed`).
- `uv run pytest -q` passed (`80 passed`).
- `uv run pytest tests/test_source_ingest_api.py -q` passed (`13 passed`).
- `uv run pytest -q` passed (`82 passed`).

### Next
- Execute Step 26: validate supplement proposal JSON and return `LLM_OUTPUT_INVALID` for invalid model output.

## 2026-05-24 (Step 16-22 Indexing + QA + Source Ingestion)

### Highlights
- Completed Step 16 by adding manual incremental sync endpoint:
  `POST /api/notion/index/incremental`.
- Added incremental sync orchestrator:
  `src/orchestrators/notion_incremental_index_orchestrator.py`.
- Refactored page index orchestrator to expose shared page snapshot indexing and integrated chunk replacement in page indexing:
  `src/orchestrators/notion_page_index_orchestrator.py`.
- Updated Notion index API route and schemas for incremental request/response:
  `src/app/api/routes/notion_index.py`,
  `src/app/schemas/notion_index.py`,
  and `src/app/schemas/__init__.py`.
- Added incremental sync API tests in `tests/test_notion_index_page_api.py`:
  manual deletion reconciliation and missing-page failure path.
- Updated docs for incremental sync behavior:
  `docs/05-rag-design.md` and `docs/09-api-contract.md`.
- Completed Step 17 by adding production chunk retriever:
  `src/rag/retriever.py`.
- Extended chunk repository read path for scoped retrieval:
  `ChunkRepository.list_production_chunks(...)`.
- Added retrieval tests:
  `tests/test_retriever.py` (page/section/source scope and embedding-only query).
- Updated RAG design doc with Step 17 retrieval rules:
  `docs/05-rag-design.md`.
- Completed Step 18 by adding LLM provider abstraction implementation:
  `src/providers/llm.py` (`BaseLLMClient`, `OpenAIClient`, `LLMClientError`).
- Updated provider exports:
  `src/providers/__init__.py`.
- Added LLM client tests:
  `tests/test_llm_client.py` (mock transport + router compatibility).
- Updated architecture doc implementation status:
  `docs/01-architecture.md`.
- Completed Step 19 by adding QA endpoint:
  `POST /api/qa`.
- Added QA orchestrator:
  `src/orchestrators/qa_orchestrator.py`.
- Added QA API route and request/response schemas:
  `src/app/api/routes/qa.py` and `src/app/schemas/qa.py`.
- Added provider router dependency wiring and router registration updates:
  `src/app/dependencies.py`, `src/app/main.py`, `src/app/api/__init__.py`,
  `src/app/api/routes/__init__.py`, `src/orchestrators/__init__.py`,
  and `src/app/schemas/__init__.py`.
- Added QA API tests:
  `tests/test_qa_api.py`.
- Updated API and RAG docs for Step 19 behavior:
  `docs/09-api-contract.md` and `docs/05-rag-design.md`.
- Completed Step 20 by adding source document creation workflow:
  `POST /api/ingest/source`.
- Added source document workflow layers:
  `src/repositories/source_document_repository.py`,
  `src/orchestrators/source_document_orchestrator.py`,
  `src/app/api/routes/source_ingest.py`,
  `src/app/schemas/source_ingest.py`.
- Updated router/schema wiring for source ingestion endpoint:
  `src/app/main.py`, `src/app/api/__init__.py`, `src/app/api/routes/__init__.py`,
  `src/app/schemas/__init__.py`, `src/orchestrators/__init__.py`,
  and `src/repositories/__init__.py`.
- Added Step 20 API tests:
  `tests/test_source_ingest_api.py` (all supported source types + invalid input paths).
- Updated ingestion API docs:
  `docs/09-api-contract.md` and `docs/00-design-doc.md`.
- Completed Step 21 by adding PDF ingestion endpoint:
  `POST /api/ingest/document`.
- Added PDF ingestion orchestrator and parser tool:
  `src/orchestrators/document_ingestion_orchestrator.py` and
  `src/tools/pdf_parser_tool.py`.
- Updated tool registry wiring to register `PDFParserTool` by default:
  `src/app/dependencies.py` and `src/tools/__init__.py`.
- Extended source ingest route to support multipart PDF uploads while keeping route thin:
  `src/app/api/routes/source_ingest.py`.
- Added PDF ingestion tests:
  `tests/test_source_ingest_api.py` (successful upload + parse failure),
  and `tests/test_pdf_parser_tool.py`.
- Updated API contract for `/api/ingest/document` and added runtime dependencies:
  `docs/09-api-contract.md`, `pyproject.toml`, and `uv.lock`.
- Completed Step 22 by adding URL ingestion endpoint:
  `POST /api/ingest/url`.
- Added URL ingestion orchestrator and parser tool:
  `src/orchestrators/url_ingestion_orchestrator.py` and
  `src/tools/url_article_parser_tool.py`.
- Updated tool registry wiring to register `URLArticleParserTool` by default:
  `src/app/dependencies.py` and `src/tools/__init__.py`.
- Extended source ingest route and schemas for URL payload handling:
  `src/app/api/routes/source_ingest.py`,
  `src/app/schemas/source_ingest.py`,
  `src/app/schemas/__init__.py`,
  and `src/orchestrators/__init__.py`.
- Added URL ingestion tests:
  `tests/test_source_ingest_api.py` (success + `URL_FETCH_FAILED`) and
  `tests/test_url_article_parser_tool.py`.
- Updated API contract for `/api/ingest/url` and URL extraction dependency:
  `docs/09-api-contract.md`, `pyproject.toml`, and `uv.lock`.

### Issues and Decisions
- Kept architecture flow as route -> orchestrator -> tool/repository.
- Implemented page-level replacement reconciliation for both blocks and notion chunks so stale derived state is removed per changed page.
- Made incremental sync deterministic: first page failure ends workflow with mapped `failure_reason` and workflow id.
- Kept Notion writes disabled; this step only reads and reconciles derived local state.
- Kept retrieval path as `RAG retriever -> repository` boundary (no direct SQL in higher layers).
- Enforced production scope in retriever by limiting current MVP retrieval to `source_kind="notion"`.
- Added deterministic lexical ranking with optional embedding-score combination as fallback until full QA flow integration.
- Kept LLM boundary behind provider interface and router; no orchestrator or route direct SDK coupling introduced.
- Used transport injection in `OpenAIClient` to keep tests deterministic and network-free.
- Kept error behavior deterministic with `LLMClientError` for invalid payload/schema cases.
- Kept QA flow layered as route -> orchestrator -> retriever/provider router/repositories.
- Implemented deterministic insufficient-info fallback when retrieval has no safe citation output.
- Preserved production-RAG rule by reusing production chunk retrieval path (`source_kind=\"notion\"` scope).
- Kept source-document flow layered as route -> orchestrator -> repository and workflow service, with no direct external SDK calls in route/orchestrator.
- Stored ingestion workflow metadata with source type, display name, and raw-text length only, and avoided logging raw source text content.
- Kept PDF parsing behind `ToolRegistry -> PDFParserTool` so orchestrator does not call parsing libraries directly.
- Mapped parser failures to deterministic `PDF_PARSE_FAILED` and kept failure metadata free of raw PDF text.
- Enforced source display rule for PDFs by always using the uploaded filename as `source_display_name`.
- Kept URL extraction behind `ToolRegistry -> URLArticleParserTool` so orchestrator does not call network/parsing libraries directly.
- Mapped URL fetch/extraction failures to deterministic `URL_FETCH_FAILED` and kept failure metadata free of raw article text.
- Preserved full URL in source metadata by using the URL string as `source_display_name`.

### Verification
- `uv run pytest tests/test_notion_index_page_api.py -q` passed (`6 passed`).
- `uv run pytest tests/test_chunk_repository.py -q` passed (`3 passed`).
- `uv run pytest -q` passed (`44 passed`).
- `uv run pytest tests/test_retriever.py -q` passed (`5 passed`).
- `uv run pytest tests/test_chunk_repository.py -q` passed (`3 passed`).
- `uv run pytest -q` passed (`49 passed`).
- `uv run pytest tests/test_llm_client.py -q` passed (`5 passed`).
- `uv run pytest tests/test_provider_router.py -q` passed (`3 passed`).
- `uv run pytest -q` passed (`54 passed`).
- `uv run pytest tests/test_qa_api.py -q` passed (`3 passed`).
- `uv run pytest tests/test_llm_client.py -q` passed (`5 passed`).
- `uv run pytest tests/test_notion_index_page_api.py -q` passed (`6 passed`).
- `uv run pytest -q` passed (`57 passed`).
- `uv run pytest tests/test_source_ingest_api.py -q` passed (`3 passed`).
- `uv run pytest -q` passed (`60 passed`).
- `uv run pytest tests/test_pdf_parser_tool.py -q` passed (`3 passed`).
- `uv run pytest tests/test_source_ingest_api.py -q` passed (`5 passed`).
- `uv run pytest -q` passed (`65 passed`).
- `uv run pytest tests/test_url_article_parser_tool.py -q` passed (`3 passed`).
- `uv run pytest tests/test_source_ingest_api.py -q` passed (`7 passed`).
- `uv run pytest -q` passed (`70 passed`).

### Next
- Execute Step 23: Ingest YouTube transcript sources.

## 2026-05-23 (Step 11-15 Notion Indexing + RAG Foundation)

### Highlights
- Completed Step 11 by implementing one-page indexing endpoint:
  `POST /api/notion/index/page`.
- Added route -> orchestrator -> tool/repository flow:
  `src/app/api/routes/notion_index.py`,
  `src/orchestrators/notion_page_index_orchestrator.py`,
  `src/repositories/notion_page_repository.py`,
  `src/repositories/notion_block_repository.py`.
- Added API schemas and dependencies:
  `src/app/schemas/notion_index.py`,
  `src/app/dependencies.py`,
  and router wiring in `src/app/main.py`.
- Added API integration tests:
  `tests/test_notion_index_page_api.py` for
  nested block persistence, re-index replacement, and page-not-found failures.
- Updated API contract doc:
  `docs/09-api-contract.md` with request/response/error examples for `/api/notion/index/page`.
- Completed Step 12 by adding deterministic citation path builder:
  `src/rag/block_path_builder.py`.
- Connected Step 12 builder into indexing orchestrator so block paths are built from hierarchy during page indexing, not copied from external path text.
- Added path-specific tests:
  `tests/test_block_path_builder.py` and updated `tests/test_notion_index_page_api.py`
  with mixed heading/toggle/child-page hierarchy assertions.
- Updated `docs/05-rag-design.md` with Step 12 citation path builder rules and examples.
- Completed Step 13 by adding Notion chunk conversion module:
  `src/rag/chunker.py`.
- Added chunk models and exports for reuse:
  `ChunkerPage`, `ChunkerBlock`, `NotionChunkDraft`, and `chunk_notion_page`.
- Added `tests/test_chunker.py` to validate
  page/toggle/heading/child-page boundary chunking,
  chunk size split behavior, and invalid chunk-size handling.
- Updated `docs/05-rag-design.md` with Step 13 chunking rules and chunk metadata fields.
- Completed Step 14 by adding embedding abstraction module:
  `src/providers/embedding.py`.
- Added `EmbeddingClient`, `EmbeddingRequest`, `EmbeddingResponse`,
  and `OpenAIEmbeddingClient` with injectable transport for deterministic tests.
- Exported embedding interfaces from `src/providers/__init__.py`.
- Added `tests/test_embedding_client.py` covering mock payload mapping,
  request-model override, dimensions forwarding, invalid response handling,
  and empty API key rejection.
- Updated `docs/05-rag-design.md` with Step 14 embedding provider abstraction notes.
- Completed Step 15 by adding chunk upsert repository:
  `src/repositories/chunk_repository.py`.
- Added `NotionChunkUpsert` payload model and
  `ChunkRepository.upsert_chunks()` with page-level replacement semantics.
- Added `tests/test_chunk_repository.py` to cover:
  same-page replacement without duplicates, cross-page isolation, and block mapping errors.
- Updated `docs/05-rag-design.md` with Step 15 chunk upsert and page replacement rules.

### Issues and Decisions
- Kept architecture boundary strict:
  API route calls orchestrator only, and orchestrator calls `ToolRegistry` -> `NotionReaderTool`.
- Kept Notion interaction read-only in this step; no Notion write path added.
- Added sqlite ID allocation fallback for new page/block repositories to keep in-memory sqlite tests deterministic with `BigInteger` primary keys.
- Mapped tool error codes to standardized workflow `failure_reason`, defaulting unknown codes to `UNKNOWN_ERROR`.
- Kept path-building logic deterministic and backend-owned for citation traceability.
- Treated empty block text as parent-path inheritance to avoid unstable empty path segments.
- Kept Step 13 as deterministic backend transformation only (no direct DB write or API contract change in this step).
- Kept citation traceability in chunk output via `notion_path` and `citation_meta` block/page identifiers.
- Kept embedding integration SDK-agnostic at orchestrator boundary by introducing an abstract embedding client interface first.
- Used transport injection in OpenAI adapter tests to avoid real network calls in unit tests.
- Kept vector upsert inside repository boundary so page-level replacement remains deterministic backend DB logic.
- Kept deletion scope constrained to target-page notion chunks (`source_kind=\"notion\"`) to avoid accidental cross-page deletion.

### Verification
- `uv run pytest tests/test_notion_index_page_api.py -q` passed (`3 passed`).
- `uv run pytest -q` passed (`29 passed`).
- `uv run pytest tests/test_block_path_builder.py -q` passed (`2 passed`).
- `uv run pytest tests/test_notion_index_page_api.py -q` passed (`4 passed`).
- `uv run pytest -q` passed (`32 passed`).
- `uv run pytest tests/test_chunker.py -q` passed (`3 passed`).
- `uv run pytest tests/test_block_path_builder.py -q` passed (`2 passed`).
- `uv run pytest -q` passed (`35 passed`).
- `uv run pytest tests/test_embedding_client.py -q` passed (`4 passed`).
- `uv run pytest -q` passed (`39 passed`).
- `uv run pytest tests/test_chunk_repository.py -q` passed (`3 passed`).
- `uv run pytest -q` passed (`42 passed`).

### Next
- Execute Step 16: Support manual incremental sync (`POST /api/notion/index/incremental`).

## 2026-05-20 (Step 6.2-10 MCP + Core Backend Foundations)

### Highlights
- Completed Step 6.2 by adding `src/tools/` skeleton:
  `models.py` (`ToolSpec`, `ToolContext`, `ToolResult`, `ToolError`),
  `base.py` (`Tool`), and `registry.py` (`ToolRegistry` + deterministic registry errors).
- Added `tests/test_tool_registry.py` with fake tool registration/call coverage and deterministic duplicate/missing-tool error checks.
- Completed Step 6.3 by updating `docs/01-architecture.md` with implemented provider/tool skeleton boundaries and post-MVP MCP extraction scope.
- Updated ADR `docs/decisions/0002-mcp-oriented-architecture.md` with implementation notes and explicit non-transferable deterministic backend ownership.
- Completed Step 7 by adding repository layer for workflow run persistence:
  `src/repositories/workflow_run_repository.py` and `src/repositories/__init__.py`.
- Added `tests/test_workflow_run_repository.py` to verify create, read, and update on one workflow run entity.
- Completed Step 8 by adding queue abstraction layer:
  `src/queue/base.py` (`QueueClient`),
  `src/queue/rq_queue_client.py` (`RQQueueClient`),
  `src/queue/fake_queue_client.py` (`FakeQueueClient`),
  and `src/queue/models.py` (`EnqueuedJob`).
- Added `tests/test_queue_client.py` to verify fake enqueue and local RQ enqueue using `fakeredis`.
- Completed Step 9 by adding workflow run status service:
  `src/services/workflow_run_service.py` and `src/services/__init__.py`.
- Added `tests/test_workflow_run_service.py` to cover running/succeeded/failed paths,
  standardized `failure_reason` validation, and not-found behavior.
- Updated `src/repositories/workflow_run_repository.py` with sqlite ID allocation fallback
  so service/repository tests can persist workflow rows in local sqlite test runs.
- Completed Step 10 by adding read-only `NotionReaderTool`:
  `src/tools/notion_reader_tool.py` with local read client, page tree/block tree models,
  deterministic error codes, and printable block-path tree output.
- Added `tests/test_notion_reader_tool.py` covering successful tree/path output,
  missing page behavior, invalid argument behavior, and fetch failure behavior.
- Expanded `docs/03-guardrails.md` and `docs/06-notion-permission-model.md`
  from placeholders into actionable Notion write-safety and permission specs.

### Issues and Decisions
- Kept tool input/output schema-friendly for future MCP Client compatibility.
- Kept this step SDK-free (no MCP SDK/server dependency) and local-adapter-first.
- Clarified that MCP servers can host adapters later, but policy checks and state transitions stay in backend deterministic logic.
- Kept repository methods focused on DB access only; no workflow policy logic in repository layer.
- Kept queue backend details behind `QueueClient` so business logic can depend only on the abstraction.
- Kept workflow status transitions in a dedicated service layer above repository.
- Enforced standardized `failure_reason` values with deterministic validation in service logic.
- Kept Notion integration read-only for this step; no write path added to the tool.
- Kept guardrails based on existing design docs and repo rules only; no new product behavior was invented.
- Clarified that Notion write safety, RAG exclusion, and permission checks stay in deterministic backend logic,
  not in LLM prompts, provider adapters, tool adapters, or future MCP servers.

### Verification
- `uv run pytest` passed (`13 passed`), including new tool registry tests.
- `uv run pytest` passed (`15 passed`), including new workflow run repository tests.
- `uv run pytest` passed (`17 passed`), including queue client tests.
- `uv run pytest` passed (`22 passed`), including workflow run service tests.
- `uv run pytest` passed (`26 passed`), including Notion reader tool tests.
- Documentation acceptance checks passed for `AI Supplement Zone`, append-only flow,
  `pending`/`rejected` RAG exclusion, `/api/notion/index/incremental`,
  `WRITE_POLICY_VIOLATION`, deterministic backend ownership, and MCP/provider/tool boundaries.
- Reviewed `git diff -- docs/03-guardrails.md docs/06-notion-permission-model.md dev_state/DAILY_LOG.md`.

### Next
- Execute Step 11: Index One Notion Page.

## 2026-05-19 (Documentation Execution Gate)

### Highlights
- Added a Task Start Rule to `AGENTS.md` so implementation work must read the main design doc, local dev state, and task-related docs before code changes.
- Added a Documentation Timing Rule to `dev_state/PROJECT_ROADMAP.md`.
- Inserted new Step 6 for documentation execution rules and shifted repository pattern work to Step 7.
- Documented the difference between development harness and runtime agent harness in `docs/00-design-doc.md`.
- Added MCP-oriented architecture docs and ADR while keeping standalone MCP servers out of MVP.
- Added roadmap Steps 6.1, 6.2, and 6.3 for provider router, tool registry, and future MCP boundary documentation.
- Completed Step 6.1 by adding `src/providers/` skeleton:
  `models.py` (`LLMMessage`, `LLMRequest`, `LLMResponse`),
  `base.py` (`LLMProvider`), and `router.py` (`ProviderRouter` + deterministic router errors).
- Added `tests/test_provider_router.py` with fake provider registration, routing, duplicate-name, and missing-provider coverage.

### Issues and Decisions
- Project docs stay development and maintenance context by default.
- Production user QA must use indexed Notion content unless a future ADR explicitly approves project docs as runtime retrieval content.
- `AGENTS.md` is development-agent guidance, not the LearnLoop runtime system prompt.
- OpenAI remains first, but provider/tool boundaries should allow future Claude and Gemini adapters.
- Safety checks, RAG inclusion, output validation, and state transitions stay deterministic backend logic.
- Kept this step SDK-free (no OpenAI/Claude/Gemini imports) to preserve provider-agnostic boundary at orchestrator side.

### Verification
- Documentation acceptance checks were run for task-start rules, roadmap IDs, MCP-oriented architecture terms, and whitespace safety.
- `uv run pytest` passed (`10 passed`), including new provider router tests.

### Next
- Execute Step 6.2: MCP-Compatible Local Tool Interface and Registry.

## 2026-05-17 (Local Workflow + Phase 1 Step 1-2)

### Highlights
- Switched local working memory to `dev_state/` and ignored it in Git.
- Added executable roadmap at `dev_state/PROJECT_ROADMAP.md`.
- Completed Phase 1 Step 1 backend skeleton:
  `pyproject.toml`, `src/app/main.py`, `tests/test_health.py`.
- Completed Phase 1 Step 2 config foundation:
  `src/app/config.py`, `.env.example`, `tests/test_config.py`.
- Completed Phase 1 Step 3 observability foundation:
  `src/observability/logger.py`, request logging middleware, logging tests.
- Completed Phase 2 Step 4 local infra bootstrap:
  `docker-compose.yml` with Postgres (pgvector) and Redis.

### Issues and Decisions
- `uv sync` editable-build error on early skeleton:
  set `tool.uv.package = false` to avoid premature packaging requirements.
- `pytest` crashed with exit `139` under Anaconda Python (`readline` segfault):
  standardized local sync with `uv sync --python /usr/bin/python3`.
- Python 3.9 + Pydantic could not evaluate `str | None`:
  changed to `Optional[str]` in settings model.
- `uvicorn src.app.main:app` import mismatch between runtime and tests:
  standardized imports to `src.*` and set pytest `pythonpath = ["."]`.
- First `docker compose ps` check returned no running rows immediately after startup:
  re-checked with `docker compose ps -a` and then `docker compose ps` after warm-up.

### Verification
- `git status` does not show `dev_state/`; root `DAILY_LOG.md` is no longer tracked.
- `uv sync --python /usr/bin/python3` succeeded.
- `uv run pytest` passed (`5 passed`).
- `uv run uvicorn src.app.main:app --reload` + `curl http://localhost:8000/health` returned `{"status":"ok"}`.
- Runtime request log includes JSON with `workflow_id`, `path`, and `status_code` for `/health`.
- `.env.example` contains placeholders only:
  `APP_ENV`, `LOG_LEVEL`, `DATABASE_URL`, `REDIS_URL`, `NOTION_TOKEN`, `OPENAI_API_KEY`.
- `docker compose up -d` succeeded; `docker compose ps` shows both
  `learnloop-postgres` and `learnloop-redis` `Up (healthy)`.

### Next
- Execute Phase 2 Step 5: Database Layer + Alembic.

## 2026-05-18 (Phase 2 Step 5 DB Layer and Alembic)

### Highlights
- Added DB foundation under `src/db`:
  `base.py`, `models.py`, `session.py`.
- Initialized Alembic (`alembic.ini`, `alembic/env.py`, `alembic/versions/`).
- Generated initial schema migration for:
  `notion_pages`, `notion_blocks`, `source_documents`, `knowledge_chunks`,
  `change_requests`, `audit_logs`, `workflow_runs`.

### Issues and Decisions
- Alembic autogenerate initially failed (`localhost:5432` connection refused):
  restarted local infra with `docker compose up -d` before generating revision.
- Standardized Alembic metadata wiring via `src.db.base.Base.metadata`
  and DB URL from `src.db.session.get_database_url()`.

### Verification
- `uv run alembic revision --autogenerate -m "initial schema"` succeeded.
- `uv run alembic upgrade head` succeeded.
- `docker exec learnloop-postgres psql -U learnloop -d learnloop -c "\dt"`
  shows `alembic_version` + 7 expected tables.
- `uv run pytest` passed (`7 passed`).

### Next
- Execute Phase 2 Step 6: Repository Pattern.

## 2026-05-15 (Documentation and GitHub Foundation)

### Highlights
- Built docs harness: `AGENTS.md`, `README.md`, and docs skeleton (`docs/01` to `docs/12`).
- Finalized design doc v1.1 guardrails and sync model.
- Initialized Git branch and completed first docs push flow.

### Issues and Decisions
- Needed a stable project constitution before backend implementation.
- Enforced write flow:
  `Change Request -> Human Accept -> Append to AI Supplement Zone`.
- Kept direct Notion edits disabled for MVP.

### Verification
- Core docs and design constraints existed and matched repo navigation.
- No backend code had been implemented at that date.

### Next
- Start backend skeleton by documented architecture boundaries.
