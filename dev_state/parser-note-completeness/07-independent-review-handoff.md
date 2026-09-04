# Human Independent Review Bundle — Parser & Note Completeness v1

Status: **independent review pending**. This is a bounded review aid. It is
not Gold, a benchmark contract, a scorer decision, a formal authority record,
or a baseline publication.

This bundle is the reviewer-facing extension of the existing independent
review handoff. It is intentionally self-contained: a reviewer can use the
case sections below without reading raw governance JSON or understanding the
benchmark interview history.

## How to use this bundle

For each case, open the frozen source first, then the normalized reference,
then use the claim table and the exact Gold path for spot checks. The excerpts
below are bounded navigation aids only. They do not replace inspection of the
frozen source bytes.

Review three independent questions:

- **Fixture:** Are the exact source bytes genuinely project-owned or cleared
  for redistribution, free of private/personal material, and described by the
  recorded provenance?
- **Reference and Gold:** Does the reference faithfully represent the source,
  and are the listed claims atomic, complete, correctly qualified, categorized,
  located, and neither duplicated nor silently excluded?
- **Optional parser-contract review:** If the review assignment includes the
  parser contract, record only a human decision in the result template. This
  bundle does not propose or authorize any contract/scorer change.

Every decision is blank by design. The current owner-primary records remain
`independent_review=pending`, `formal_authority=false`, and
`formal_baseline_ready=false`.

## Binding records for this bundle

The selection is resolved from these exact records:

- Owner-primary selection index:
  `tests/evals/parser_note_completeness/v1/governance/owner-primary/revision-001/manifest.json`
  — SHA-256 `c7603013eb5db52fa265cdfb08854d73a2d280b09cee22a9ad72dd719b42468a`.
- Bound benchmark manifest:
  `tests/evals/parser_note_completeness/v1/manifests/benchmark/1.0.2/manifest.json`
  — SHA-256 `bf6a50e131d6f2b922717f25efafb1452d2de8a94b5180a3af424cfa5693811f`.
- Bound full diagnostic profile:
  `tests/evals/parser_note_completeness/v1/manifests/full/revision-003/profile.json`
  — SHA-256 `45a00105debf8b452bdc18f045fe48a2e75fd2ebaeb94f20a71c1ca877187039`.
- Simple result file to fill:
  `dev_state/parser-note-completeness/human-review-result-template.json`.

The owner-primary index is authoritative for selecting the 13 owner-approved
pending records for this review package. It does not itself grant formal
authority.

## Exact 13-case inventory

All paths are repository-relative. SHA-256 values are over the exact file at
the listed path. For S02, the profile-bound source artifact is the manifest;
the two image files are the visual source bytes it names. For Y01/Y02, the
profile-bound source artifact is the snapshot manifest; the VTT and chapter
files are the frozen transcript components it names.

| Case | Source type | Fixture revision | Selected source artifact | Source SHA-256 | Selected reference | Reference SHA-256 | Owner-primary Gold exact path | Gold revision / SHA-256 | Claims |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| P01 | PDF | revision-001 | `fixtures/P01/revision-001/source.pdf` | `2ec844a220a426e14eca5a60a9d19767751bee022b67cb3998a110cdf382b973` | `reference_documents/P01/revision-001/normalized_document.json` | `a6a86086598084f9557bda254857439511237aa07117eecbefb8db5d08c22db3` | `governance/P01/revision-002/owner-primary-gold.json` | revision-002 / `505245767805de65e238713e652a1e7087025b460830519ddcc0556646503a6f` | 12 |
| P02 | PDF | revision-002 | `fixtures/P02/revision-002/source.pdf` | `557f0ff7047a6399359c12ff84c4d8a0d7d534427faa8ace2d246653d63ab41f` | `reference_documents/P02/revision-002/normalized_document.json` | `761f503f60114b90834051c36aaf2fb665fb0738070edd72977fc821dfc32541` | `governance/P02/revision-003/owner-primary-gold.json` | revision-003 / `93f7264410e5ba9411308edfd69f1d021e6e1fafc5ce7164f3e8b4760d1ba230` | 8 |
| P03 | PDF | revision-003 | `fixtures/P03/revision-003/source.pdf` | `a5fceec1d03317f6c7ca7dab576ef18b54124d31a1ef68b53511ed36741b4e26` | `reference_documents/P03/revision-003/normalized_document.json` | `75129a78bb1178300c9f8c75e6a3cca987f1a62ff1fb6d46661b7b783157fb48` | `governance/P03/revision-004/owner-primary-gold.json` | revision-004 / `1d394c418f25a2b03dcf3d4c595ef01e81f455a18fee7e3bb98461581c7f33ed` | 5 |
| P04 | PDF | revision-003 | `fixtures/P04/revision-003/source.pdf` | `055115cf9f24f8116366399c07d43dc88ce2f48966339c7cc3dea096ca1e566d` | `reference_documents/P04/revision-003/normalized_document.json` | `bb205531ab92477ea847dbc36302c89f73307395161b3d9b74941a8d6d39dfa1` | `governance/P04/revision-004/owner-primary-gold.json` | revision-004 / `67762fe91105ede7656926b5936be43c0c1588ec02894f54cf063491db9d7fff` | 6 |
| W01 | Web | revision-001 | `fixtures/W01/revision-001/source.html` | `1ab20dc2725df5d5066e2d6113487b4f9ae16973db9709f3bd66e53e4e52f43b` | `reference_documents/W01/revision-001/normalized_document.json` | `999839f1e79da04a5c7dd50ca8c6743aacf25b638712ad6095d9e0b044232747` | `governance/W01/revision-002/owner-primary-gold.json` | revision-002 / `9d275c96d2930864ecc920a53e1c57cb773a6bf59c5bb1b5a9f80b04f375029e` | 4 |
| W02 | Web | revision-002 | `fixtures/W02/revision-002/source.html` | `368f3bf9192bb7c9099e83f95e8d0b72cffbc0dab3ee04ac81e4415fcca32e51` | `reference_documents/W02/revision-002/normalized_document.json` | `847de8b00366be9059c0f732e6e11f108de3ba8e8e268f1249793af140315dd9` | `governance/W02/revision-003/owner-primary-gold.json` | revision-003 / `8148b18d3b327c5944ab0b39d4d59a9559cc10a2bb54bf52ced0c0d94b60fd5a` | 11 |
| W03 | Web | revision-002 | `fixtures/W03/revision-002/source.html` | `a6b8495a77d7d5fd95fb4ba9ca98aa56e9043c09447f42b15090bd1dc134f2df` | `reference_documents/W03/revision-002/normalized_document.json` | `f63a94e5d3061c9c116afa07fef7c666a3e6f1249b8d34f3b280b1d307f0647b` | `governance/W03/revision-003/owner-primary-gold.json` | revision-003 / `720776643ac1d60b0bcad50a53e0aac9135e798550278b3be99791b55173e53c` | 8 |
| Y01 | YouTube transcript | revision-001 | `fixtures/Y01/revision-001/source_snapshot.json` | `66765dcc81f041b8d20c1484db4651f063d9ed53cac82d3bc900123ea97d873a` | `reference_documents/Y01/revision-001/normalized_document.json` | `c1937ce21c5baba204428eabbeae4d5b52945ca7a06220b9012ade17ba7e6251` | `governance/Y01/revision-002/owner-primary-gold.json` | revision-002 / `6e1f8d740028b75ea65c87a42c1517ac42935e832b8e3289e617bc3f4be82a3a` | 3 |
| Y02 | YouTube transcript | revision-001 | `fixtures/Y02/revision-001/source_snapshot.json` | `a3b1b53f0450ac63bf6ad327d1adfad066ff9a4c706b2614db8a03b96b1f97ec` | `reference_documents/Y02/revision-001/normalized_document.json` | `e018e28558b6b69604ab6249be99e57bb25729eb878dadad40c7e59e84d8c2d6` | `governance/Y02/revision-002/owner-primary-gold.json` | revision-002 / `3ff5e657385f93337762555a783b65f8af525e1cd914705866ae9b53c063e2e2` | 8 |
| C01 | Chat | revision-001 | `fixtures/C01/revision-001/source.json` | `d0f4543a2e71526ec208dbd5b3f645bedc074145ec3e91de5c017276f9fd6288` | `reference_documents/C01/revision-001/normalized_document.json` | `0be80f1cdd163fc0aaeefce69b127aa27d5661c496ab65a0083ab0f91263f390` | `governance/C01/revision-002/owner-primary-annotation.json` | revision-002 / `bd1b9d409dd7111022336cd5c0bc57c400ee677f242eff27241e6aa69034802c` | 3 |
| C02 | Chat | revision-001 | `fixtures/C02/revision-001/source.json` | `7ac22d5006e724078d5db448768f8e85b704d4ef17ebaebd74f7d148eeb4a77e` | `reference_documents/C02/revision-001/normalized_document.json` | `ce6d935830bd56d3b55a56f1b547dac78c798ab8249d224f7b0f19ac179e3e0e` | `governance/C02/revision-003/owner-primary-gold.json` | revision-003 / `afe7f9506303731f4ce9ca519b9840ddedce5d5c41e54c31283527d23a238e89` | 6 |
| S01 | Screenshot | revision-001 | `fixtures/S01/revision-001/source.png` | `d0c61b0f04a224d0c32f55fedfab7d5bb63c6a30d0d40430ca7c255c2125f0bd` | `reference_documents/S01/revision-001/normalized_document.json` | `b68a8ca56d829880a175b25d23c9ddca4d501a08600702fd6192f39752c73057` | `governance/S01/revision-002/owner-primary-gold.json` | revision-002 / `3f011425f009bf986428ebf63c315b8d64b8f99ee20cf8f98c8e4d9df0efa576` | 3 |
| S02 | Screenshot | revision-002 | `fixtures/S02/revision-002/source_manifest.json` | `34ac32424526527808db6c54f615ff9b5e2f2594a89590102902c1cb8ecaeb30` | `reference_documents/S02/revision-002/normalized_document.json` | `e5f58120026419c284a9a8bbbf90d31b122c19aa68daaece0f6138fcb33ed98f` | `governance/S02/revision-003/owner-primary-gold.json` | revision-003 / `34bf3c160ede8692501bc77b731b47fea14bfec2b67bdb30052890c6323f2d5c` | 5 |

## Case review sections

### P01 — Reliable Queue Workers

**1. Case ID / source type:** `P01` / PDF. The reference has 45 elements in
8 page sections.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/P01/revision-001/source.pdf`
(open the PDF directly).

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/P01/revision-001/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/P01/revision-002/owner-primary-gold.json`
(Gold revision-002; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:**

- PDF pages 1–3: “Use a stable job identifier for every unit of work”; “The
  worker may claim a job, but it must not claim success before durable
  completion”; and “Persist the job key with the effect”.
- PDF page 4: “Retries are bounded observations of a failure” and exhausted
  work goes to an explicit review path.
- PDF pages 5–6: progress is visible “without logging private payloads” and
  “Never convert an interrupted attempt into a fabricated success.”
- PDF pages 7–8: “Replay the same job key and verify one durable effect” and
  “Confirm terminal receipts cannot be overwritten.”

**6. Expected claims (12):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| P01-EC01 | Every job has a stable ID, is safe to replay after process loss, and records each terminal reason. | critical | PDF p.1 `p01-page-1-element-3..5` | Every unit; after process loss; every terminal outcome. | procedure; recommendation |
| P01-EC02 | A queue contract identifies work, owner, and acknowledgement boundary; claiming work is not claiming success. | critical | PDF p.2 `p01-page-2-element-1..2` | Success only after durable completion. | definition |
| P01-EC03 | Version payloads before enqueueing, expose lease expiry/renewal, and acknowledge after the durable write. | critical | PDF p.2 `p01-page-2-element-3..5` | Before queue entry; visible expiry; acknowledgement follows durable write. | procedure; recommendation |
| P01-EC04 | Idempotency makes replay a safe observation by atomically tying the job key to its effect. | critical | PDF p.3 `p01-page-3-element-1..3` | If key was already applied, return `already-applied`; otherwise apply once and return `applied`; same transaction. | mechanism; condition |
| P01-EC05 | Retries are bounded observations of failure, not an eventual-success guarantee. | major | PDF p.4 `p01-page-4-element-1` | Bounded retry observation; no promise of eventual success. | limitation |
| P01-EC06 | Classify failures before retry, increase delay visibly, and route exhausted work to review. | major | PDF p.4 `p01-page-4-element-2..5` | Attempt count remains visible; example uses `attempt=2` and `delay=attempt*5`. | procedure; recommendation |
| P01-EC07 | Show ownership/progress without logging private payloads; heartbeat describes the lease, not job contents. | critical | PDF p.5 `p01-page-5-element-1..2` | No private payload logging; heartbeat scope is lease-only. | condition; risk |
| P01-EC08 | Expose heartbeat age, queue depth/age, and bounded provider/host receipts as raw operational facts. | major | PDF p.5 `p01-page-5-element-3..5` | Last accepted heartbeat; raw facts; bounded receipts. | procedure |
| P01-EC09 | Graceful shutdown stops claims, drains safe work, and records open leases. | critical | PDF p.6 `p01-page-6-element-1, element-3` | Ordered shutdown: stop claiming → drain safe work → record open leases. | procedure; recommendation |
| P01-EC10 | Recovery distinguishes closed work from disappearance mid-attempt and never fabricates success. | critical | PDF p.6 `p01-page-6-element-2, element-4` | Interrupted attempt remains distinguishable from closed result. | condition; risk |
| P01-EC11 | Tests cover queue/application boundaries, replay, interruption, malformed payload rejection, and the stated commands. | major | PDF p.7 `p01-page-7-element-1..5` | Replay must yield one durable effect; malformed payloads are rejected before handler execution. | procedure; recommendation |
| P01-EC12 | Use the local-worker checklist to verify contract, non-overwritable receipts, and distinguishable failures before enabling. | major | PDF p.8 `p01-page-8-element-1..5` | Before enabling a new local worker; failures remain distinct from incomplete work. | recommendation; procedure |

**7. Known exclusion / duplicate / unresolved:** No source exclusions,
duplicate occurrences, or unresolved items are recorded in the selected Gold.
Headings are navigation structure, not additional expected claims.

**8. Reference fidelity review:** [ ] text and page order faithful  [ ]
headings/paragraphs/code kinds faithful  [ ] PDF page locators and section
membership faithful  [ ] no visible queue/retry/recovery content omitted.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] selected PDF and revision match the
recorded binding.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### P02 — Bilingual Data Systems Report

**1. Case ID / source type:** `P02` / PDF. The reference has 54 elements in
4 page sections.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/P02/revision-002/source.pdf`
(open the PDF directly).

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/P02/revision-002/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/P02/revision-003/owner-primary-gold.json`
(Gold revision-003; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:**

- PDF page 1 `p02-page-1-paragraph-1..4`: “專案自有內容” / “project-owned”
  and “Text, tables, and vector figures remain in one native-text PDF.”
- PDF page 2 `p02-table-1`: `Parse | 18 | Parser`, `Index | 42 | Indexer`,
  and `Review | 75 | Operator`; inspect header cells and row relations.
- PDF page 3 `p02-table-2`: `PDF | yes | pending`, `Web | yes | pending`, and
  `Scan | image | pending`.
- PDF page 4 `p02-page-4-paragraph-1..4`: “without external images” and “for
  development validation only.”

**6. Expected claims (8):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| P02-EC01 | The project-owned report describes an observable workflow whose text, tables, and vector figures share one native-text PDF. | minor | PDF p.1 `p02-page-1-paragraph-1..4` | Project-owned; native-text PDF; all three content forms retained together. | background_context |
| P02-EC02 | Parse median latency is 18 ms and its owner is Parser. | major | PDF p.2 `p02-table-1-row-0-cell-0..2` + `row-1-cell-0..2` | Interpret `18` under `Median ms`; preserve Stage/Owner headers. | quantitative_result |
| P02-EC03 | Index median latency is 42 ms and its owner is Indexer. | major | PDF p.2 `p02-table-1-row-0-cell-0..2` + `row-2-cell-0..2` | Interpret `42` under `Median ms`; preserve Stage/Owner headers. | quantitative_result |
| P02-EC04 | Review median latency is 75 ms and its owner is Operator. | major | PDF p.2 `p02-table-1-row-0-cell-0..2` + `row-3-cell-0..2` | Interpret `75` under `Median ms`; preserve Stage/Owner headers. | quantitative_result |
| P02-EC05 | The coverage table records PDF as native, with review still pending. | major | PDF p.3 `p02-table-2-row-0-cell-0..2` + `row-1-cell-0..2` | `Native=yes`; `Reviewed=pending`. | conclusion |
| P02-EC06 | The coverage table records Web as native, with review still pending. | major | PDF p.3 `p02-table-2-row-0-cell-0..2` + `row-2-cell-0..2` | `Native=yes`; `Reviewed=pending`. | conclusion |
| P02-EC07 | The coverage table records Scan as image, with review still pending. | major | PDF p.3 `p02-table-2-row-0-cell-0..2` + `row-3-cell-0..2` | `Native=image`; `Reviewed=pending`. | conclusion |
| P02-EC08 | Both figures use vector paths without external images, and this draft is for development validation only. | major | PDF p.4 paragraphs 1–4; captions `p02-figure-1-caption`, `p02-figure-2-caption` | No external image assets; not an adoption/production claim. | limitation |

**7. Known exclusion / duplicate / unresolved:** No exclusions, duplicate
occurrences, or unresolved items are recorded. Table headers, row/column
relations, captions, and vector figures must be checked rather than treated as
plain paragraph text.

**8. Reference fidelity review:** [ ] Chinese and English text faithful  [ ]
all 3 table headers and 6 data rows faithful  [ ] figure/caption relations and
page order faithful  [ ] native/vector modality and development-only qualifier
faithful.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] corrected revision-002 PDF is the
reviewed byte set.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### P03 — Traditional Chinese Raster Scan

**1. Case ID / source type:** `P03` / PDF. The reference has 30 elements in
5 page sections.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/P03/revision-003/source.pdf`
(open the PDF directly; inspect the scan labels and regions visually).

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/P03/revision-003/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/P03/revision-004/owner-primary-gold.json`
(Gold revision-004; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:**

- PDF pages 1–2: “固定角度與微量雜訊” and “段落不重新排列”; segmentation
  lets transcription return to the image region.
- PDF page 3: “失敗必須被記錄” and “雜訊不代表內容遺失”.
- PDF page 4: “使用頁碼與區域定位原始文字” and “不包含外部連結或私人資料”.
- PDF page 5: “保留每一頁的來源影像與轉錄順序” and “相同的檔案位元組”.

**6. Expected claims (5):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| P03-EC01 | Fixed angle and light noise preserve the scan's source shape while showing entry into processing. | major | PDF p.1 `p03-page-1-paragraph-1..2` | Noise is part of the scan condition; source shape is retained. | mechanism |
| P03-EC02 | Each page preserves original reading order, and segmentation permits return to the image region. | critical | PDF p.2 `p03-page-2-paragraph-1..2` | Paragraphs are not reordered; region traceability is required. | condition |
| P03-EC03 | Failures are recorded; retries do not hide the original result; noise is not content loss. | critical | PDF p.3 `p03-page-3-paragraph-1..2` | Preserve original processing result; distinguish scan noise from missing content. | condition |
| P03-EC04 | Reviewers can locate original text by page and region, and the draft has no external links or private data. | major | PDF p.4 `p03-page-4-paragraph-1..2` | Page/region locator; project draft scope. | procedure |
| P03-EC05 | Recovery retains each page's source image and transcription order, and a fixed recipe produces identical bytes. | critical | PDF p.5 `p03-page-5-paragraph-1..2` | Per-page source/order retention; deterministic rebuild. | mechanism |

**7. Known exclusion / duplicate / unresolved:** No exclusions, duplicate
occurrences, or unresolved items are recorded. The five `掃描頁碼 N` labels and
ten `區域甲`/`區域乙` labels are retained Parser text/locator units; they are
not separate Generation claims and must not be silently omitted.

**8. Reference fidelity review:** [ ] all Traditional Chinese paragraphs
faithful  [ ] five scan labels retained  [ ] ten region labels retained  [ ]
page order and page/geometry locators faithful  [ ] noise and no-private-data
qualifiers preserved.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] selected revision-003 PDF is the
reviewed byte set.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### P04 — Mixed Native / Scanned PDF

**1. Case ID / source type:** `P04` / PDF. The reference has 31 elements in
4 page sections.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/P04/revision-003/source.pdf`
(open the PDF directly; inspect both selectable and scanned pages).

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/P04/revision-003/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/P04/revision-004/owner-primary-gold.json`
(Gold revision-004; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:**

- PDF page 1: “公式 / Formula: F = m * a” and the `Measure | Value | Unit`
  table.
- PDF page 2: “固定 recipe” with “輕微傾斜”; region text retains its review
  position.
- PDF page 3: “Native paragraphs remain selectable” and “中文與 English” can
  coexist in the mixed PDF; modality changes at the page boundary.
- PDF page 4: a scanned page with Chinese explanation, an English review label,
  and regions recoverable through “normalized geometry”.

**6. Expected claims (6):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| P04-EC01 | Native and scanned content coexist in one mixed PDF, with modality changing at page boundaries while table units remain locatable. | major | PDF pp.1 and 3 `p04-page-1-paragraph-1..2`, `p04-page-3-paragraph-1..3` | Native paragraphs remain selectable; scanned pages retain image regions; page boundary, not profile contract, changes modality. | mechanism |
| P04-EC02 | The source formula is `F = m * a`. | critical | PDF p.1 `p04-page-1-formula` | Preserve the formula label and exact expression. | core_concept |
| P04-EC03 | Force equals 12 N under the Measure/Value/Unit table. | major | PDF p.1 table headers + `p04-table-1-row-1-cell-0..2` | `Force`; value `12`; unit `N`. | quantitative_result |
| P04-EC04 | Mass equals 3 kg under the Measure/Value/Unit table. | major | PDF p.1 table headers + `p04-table-1-row-2-cell-0..2` | `Mass`; value `3`; unit `kg`. | quantitative_result |
| P04-EC05 | The page-2 scan uses a fixed recipe with slight tilt and retains original review-region position. | major | PDF p.2 `p04-page-2-paragraph-1..2` | Scan recipe and region position are source conditions. | mechanism |
| P04-EC06 | Page 4 is a scanned bilingual review page whose image regions can be recovered through normalized geometry. | major | PDF p.4 `p04-page-4-paragraph-1..2` | Scanned page; Chinese explanation plus English label; geometry returns to source. | mechanism |

**7. Known exclusion / duplicate / unresolved:** No exclusions, duplicate
occurrences, or unresolved items are recorded. Four `區域 A`/`Review B` labels
remain Parser text/locator units and do not create separate Generation claims;
the formula, table structure, page modality, and raster geometry remain in
scope.

**8. Reference fidelity review:** [ ] selectable native text faithful  [ ]
formula exact  [ ] table headers/rows/units exact  [ ] scanned regions and four
labels present  [ ] page-boundary modality and normalized geometry faithful.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] corrected revision-003 PDF is the
reviewed byte set.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### W01 — Minimal Web Slice

**1. Case ID / source type:** `W01` / Web. The frozen HTML has 5 reference
elements in one section.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/W01/revision-001/source.html`
(this frozen HTML is the source; do not open or use a live URL).

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/W01/revision-001/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/W01/revision-002/owner-primary-gold.json`
(Gold revision-002; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:** `w01-element-0..4` in source order:
“Parser Completeness Slice”; “Preserve headings”; “Preserve code blocks”; and
the `def normalize(value): return value.strip()` example.

**6. Expected claims (4):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| W01-EC01 | This project-authored page is a minimal web-source slice. | minor | Frozen HTML `w01-element-1` | Project-authored; minimal web scope. | background_context |
| W01-EC02 | Headings must be preserved. | critical | Frozen HTML `w01-element-2` | Explicit preservation requirement. | recommendation |
| W01-EC03 | Code blocks must be preserved. | critical | Frozen HTML `w01-element-3` | Explicit preservation requirement. | recommendation |
| W01-EC04 | The concrete normalization example strips surrounding whitespace. | major | Frozen HTML `w01-element-4` | `return value.strip()`; code language/source metadata is part of the locator review. | procedure |

**7. Known exclusion / duplicate / unresolved:** No exclusions, duplicate
occurrences, or unresolved items are recorded.

**8. Reference fidelity review:** [ ] exact HTML text/order faithful  [ ]
heading and list-item kind faithful  [ ] code block and source-supplied
metadata faithful  [ ] DOM locator identity faithful.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] frozen HTML, not a live page, was
reviewed.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### W02 — Traceable Data Workflows

**1. Case ID / source type:** `W02` / Web. The frozen HTML has 38 reference
elements in five sections.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/W02/revision-002/source.html`
(this frozen HTML is the source; do not use a live URL).

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/W02/revision-002/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/W02/revision-003/owner-primary-gold.json`
(Gold revision-003; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:**

- `w02-lede` and `w02-overview-paragraph`: “可追蹤的資料流程” / “keep data
  processing traceable” and one context across Chinese and English.
- `w02-overview-unordered-1..3` and `w02-overview-ordered-1..2`: “Preserve
  heading and paragraph hierarchy”, “Treat list items as locatable content”,
  and “Freeze the source snapshot first” → “Then author the reference”.
- `w02-event-table` headers/rows: `Parse | 18 ms | Read structure`,
  `Review | 42 ms | Keep context`, and `Publish | 75 ms | Await decision`.
- `w02-code`: `return value.strip()`; `w02-figure-text` and caption:
  `[Input] → [Normalize] → [Review]`.
- `w02-aside`: “development validation 草稿，不代表正式採用”.

**6. Expected claims (11):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| W02-EC01 | Clear source boundaries preserve one traceable context across Chinese and English content. | major | Frozen HTML `w02-lede`, `w02-overview-paragraph` | Bilingual context remains one bounded source. | mechanism |
| W02-EC02 | Preserve heading and paragraph hierarchy. | critical | `w02-overview-unordered-1` | Structure is a preservation requirement. | recommendation |
| W02-EC03 | Treat list items as locatable content. | major | `w02-overview-unordered-2` | List-item identity/location must remain available. | recommendation |
| W02-EC04 | Keep boilerplate distinct from article body. | major | `w02-overview-unordered-3` | Distinction prevents source/noise conflation. | recommendation |
| W02-EC05 | Freeze the source snapshot before authoring the reference. | critical | `w02-overview-ordered-1..2` | Order is snapshot first, reference second. | procedure |
| W02-EC06 | Parse event is 18 ms with note “Read structure”. | major | Table headers + `w02-event-table-row-1-cell-0..2` | Preserve Field/Value/Note relation; value includes `ms`. | quantitative_result |
| W02-EC07 | Review event is 42 ms with note “Keep context”. | major | Table headers + `w02-event-table-row-2-cell-0..2` | Preserve Field/Value/Note relation; value includes `ms`. | quantitative_result |
| W02-EC08 | Publish event is 75 ms with note “Await decision”. | major | Table headers + `w02-event-table-row-3-cell-0..2` | Preserve Field/Value/Note relation; value includes `ms`. | quantitative_result |
| W02-EC09 | Normalize source text stably before reference authoring by stripping surrounding whitespace. | major | `w02-code` | The comment says source text stays stable before authoring. | procedure |
| W02-EC10 | The workflow is Input → Normalize → Review. | critical | `w02-figure-text`, `w02-figure-caption` | Preserve figure text and caption-to-figure relation. | procedure |
| W02-EC11 | The artifact is a development-validation draft, not a formal adoption decision. | major | `w02-aside` | Development-only; non-adoption scope. | limitation |

**7. Known exclusion / duplicate / unresolved:** The selected Gold records
three source-noise exclusions for generation and end-to-end expected-claim
denominators only: `w02-header-brand`, `w02-navigation`, and `w02-footer`.
They remain Parser text/noise units. No duplicate occurrences or unresolved
items are recorded. The figure's visible text is in scope as `w02-figure-text`.

**8. Reference fidelity review:** [ ] article text and bilingual order faithful
 [ ] nested sections/list order faithful  [ ] table headers/rows faithful  [ ]
code and figure text/caption faithful  [ ] the three noise elements are
present and scoped exactly as stated  [ ] DOM locators faithful.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] frozen revision-002 HTML, not a live
page, was reviewed.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### W03 — Offline Rendered DOM

**1. Case ID / source type:** `W03` / Web. The frozen HTML has 29 reference
elements in six nested sections.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/W03/revision-002/source.html`
(this frozen HTML is the source; do not use a live URL).

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/W03/revision-002/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/W03/revision-003/owner-primary-gold.json`
(Gold revision-003; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:** `w03-intro` says the rendered article
needs “without a browser or network”; `w03-overview-paragraph` says “Nested
sections preserve the article context”; the table says `Rendered | yes | Fixed
DOM` and `Network | no | Offline build`; the figure is `[Snapshot] → [Structure]
→ [Reference]`; the conclusion says “Every element comes from fixed bytes.”

**6. Expected claims (8):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| W03-EC01 | The rendered article is a fixed DOM snapshot that needs neither browser nor network. | critical | Frozen HTML `w03-intro` | Offline/browser-independent condition. | definition |
| W03-EC02 | Nested sections preserve article context. | major | `w03-overview-paragraph` | Section hierarchy is meaningful context. | mechanism |
| W03-EC03 | Read fixed rendered DOM and preserve Chinese and English paragraphs. | critical | `w03-overview-item-1..2` | Fixed DOM; bilingual content retained. | procedure |
| W03-EC04 | Child sections bind the table and figure to one snapshot identity. | major | `w03-details-paragraph` | One snapshot identity across child sections. | mechanism |
| W03-EC05 | The snapshot records Rendered=yes with Fixed DOM. | major | Table headers + `w03-snapshot-table-row-1-cell-0..2` | Preserve State/Retained/Note relation. | conclusion |
| W03-EC06 | The snapshot records Network=no with Offline build. | critical | Table headers + `w03-snapshot-table-row-2-cell-0..2` | Network is explicitly absent; offline build is the condition. | limitation |
| W03-EC07 | The relationship is Snapshot → Structure → Reference. | critical | `w03-figure-text`, `w03-figure-caption` | Preserve figure text and caption relation. | procedure |
| W03-EC08 | Every element comes from fixed bytes. | critical | `w03-conclusion-paragraph` | Fixed-byte provenance; no live refresh. | conclusion |

**7. Known exclusion / duplicate / unresolved:** No exclusions, duplicate
occurrences, or unresolved items are recorded.

**8. Reference fidelity review:** [ ] offline/browser-independent wording
faithful  [ ] nested sections and bilingual list faithful  [ ] table/caption
relations faithful  [ ] figure text is present  [ ] Rendered/Network states and
fixed-byte conclusion faithful  [ ] DOM identity/order faithful.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] frozen revision-002 HTML, not a live
page, was reviewed.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### Y01 — Queue-worker Frozen Transcript

**1. Case ID / source type:** `Y01` / YouTube transcript. The 12 reference
elements cover three chapters, nine cues, and their cue timing locators.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/Y01/revision-001/source_snapshot.json`.
Inspect these exact frozen components named by it: `fixtures/Y01/revision-001/captions.vtt`
(SHA-256 `fcba02596d324e983b2a38fd99855065ce5bffb2bcfbb33ded1c433c8b821c3f`)
and `fixtures/Y01/revision-001/chapters.json` (SHA-256
`eb42210bf3e91a3ce99a6f59594f6e116a01c6c105964a2000bcdf3593855f86`). Do not
use a live video or live captions.

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/Y01/revision-001/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/Y01/revision-002/owner-primary-gold.json`
(Gold revision-002; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:**

- Chapter 1 cues 0–2: “A reliable worker starts with a clear queue contract”;
  name owner/lease/ack before code.
- Chapter 2 cues 3–5: “An idempotency key makes a replay safe to inspect” and a
  second attempt observes the first result.
- Chapter 3 cues 6–8: heartbeats expose ownership; shutdown preserves open
  attempts; recovery reconciles what the worker finished.

**6. Expected claims (3):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| Y01-EC01 | A reliable worker starts with an explicit queue contract covering owner, lease, acknowledgement, and written-before-code facts. | critical | Frozen VTT cues 0–2; reference `y01-chapter-1-cue-0..2` | Contract facts are fixed before code begins. | procedure |
| Y01-EC02 | Persist the idempotency key with the durable effect so a second attempt safely observes the first result. | critical | Frozen VTT cues 3–5; reference `y01-chapter-2-cue-3..5` | Key/effect persistence is the condition for safe replay observation. | mechanism |
| Y01-EC03 | Heartbeats expose ownership, shutdown preserves open attempts, and recovery reconciles what was actually finished. | critical | Frozen VTT cues 6–8; reference `y01-chapter-3-cue-6..8` | Open work remains distinguishable from finished work. | procedure |

**7. Known exclusion / duplicate / unresolved:** No exclusions, duplicate
occurrences, or unresolved items are recorded. Chapter headings are navigation
only, not claims. Platform/video identity is unavailable by policy and must not
be invented; cue identity, order, chapter, and start/end timing remain in scope.

**8. Reference fidelity review:** [ ] VTT text faithful  [ ] cue order and
start/end timing faithful  [ ] chapter membership faithful  [ ] no platform
identity invented  [ ] reference distinguishes chapter headings from cues.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance/acquisition record is accurate  [ ] redistribution is
permitted  [ ] no private or personal source material  [ ] frozen VTT and
chapter JSON, not live YouTube content, were reviewed.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### Y02 — Bilingual Offline Captions

**1. Case ID / source type:** `Y02` / YouTube transcript. The 11 reference
elements cover three chapters and eight bilingual cues.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/Y02/revision-001/source_snapshot.json`.
Inspect these exact frozen components beside it:
`fixtures/Y02/revision-001/captions.vtt` (SHA-256
`00e026765c4e166395bcc976cc86d51c723069d035b5c8d360cf72abcb360381`) and
`fixtures/Y02/revision-001/chapters.json` (SHA-256
`a2da21a2ca3abbaf0352dfa061f0f9268318036df47c128d9f41dd5c5160fa96`). Do not
use a live video or live captions.

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/Y02/revision-001/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/Y02/revision-002/owner-primary-gold.json`
(Gold revision-002; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:**

- Cue 0: “先固定契約，再開始實作” / “Freeze the contract before
  implementation.”
- Cue 1: “Chinese and English captions share one cue.”
- Cues 2–4: traceable time boundaries; chapters “without inventing platform
  identity”; and an offline snapshot that reproduces the same bytes.
- Cues 5–7: project-owned content; cue order/millisecond ranges; and
  development-validation-only scope.

**6. Expected claims (8):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| Y02-EC01 | Freeze the contract before implementation. | critical | Frozen VTT cue 0; `y02-chapter-1-cue-0` | Contract first; implementation second. | recommendation |
| Y02-EC02 | Chinese and English captions share one cue identity. | major | Frozen VTT cue 1; `y02-chapter-1-cue-1` | Bilingual text is one cue, not two independent cues. | mechanism |
| Y02-EC03 | Each segment keeps traceable time boundaries. | critical | Frozen VTT cue 2; `y02-chapter-2-cue-2` | Preserve exact cue start/end boundaries. | condition |
| Y02-EC04 | Chapters guide reading but do not establish platform identity. | critical | Frozen VTT cue 3; `y02-chapter-2-cue-3` | Do not infer unavailable platform identity. | limitation |
| Y02-EC05 | An offline snapshot reproduces the same bytes. | critical | Frozen VTT cue 4; `y02-chapter-2-cue-4` | Offline/fixed-byte reproduction. | mechanism |
| Y02-EC06 | The caption source is project-owned content. | minor | Frozen VTT cue 5; `y02-chapter-3-cue-5` | Provenance context, not a platform claim. | background_context |
| Y02-EC07 | Preserve cue order and millisecond ranges. | critical | Frozen VTT cue 6; `y02-chapter-3-cue-6` | Exact order and millisecond ranges. | procedure |
| Y02-EC08 | This draft is for development validation only. | major | Frozen VTT cue 7; `y02-chapter-3-cue-7` | Development-only; no formal adoption implication. | limitation |

**7. Known exclusion / duplicate / unresolved:** No exclusions, duplicate
occurrences, or unresolved items are recorded. Chapter headings are navigation
only; cue identity/order/timing remain in scope; platform identity remains
unavailable by policy.

**8. Reference fidelity review:** [ ] bilingual cue text faithful  [ ] cue
order and millisecond ranges faithful  [ ] chapter boundaries faithful  [ ]
offline and development-only qualifiers faithful  [ ] no platform identity
invented.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance/acquisition record is accurate  [ ] redistribution is
permitted  [ ] no private or personal source material  [ ] frozen VTT and
chapter JSON, not live YouTube content, were reviewed.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### C01 — Three-message Review Boundary Chat

**1. Case ID / source type:** `C01` / Chat. The reference has 3 message
elements in one thread, with canonical order and two reply edges.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/C01/revision-001/source.json`
(the frozen structured conversation; do not use a live chat export).

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/C01/revision-001/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/C01/revision-002/owner-primary-annotation.json`
(owner-primary annotation revision-002; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:**

- `c01-message-001`, sequence 0: “Capture the parser contract before
  implementation.”
- `c01-message-002`, sequence 1, reply to message 001: “Keep chat and
  screenshot sources as separate families.”
- `c01-message-003`, sequence 2, reply to message 002: “Record unresolved
  evidence without inventing authority.”

**6. Expected claims (3):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| C01-EC01 | Capture the parser contract before implementation. | critical | Chat message `c01-message-001`, sequence 0 | Contract precedes implementation. | recommendation |
| C01-EC02 | Keep chat and screenshot sources as separate families. | major | Chat message `c01-message-002`, sequence 1, reply edge | Family distinction must be retained. | recommendation |
| C01-EC03 | Record unresolved evidence without inventing authority. | critical | Chat message `c01-message-003`, sequence 2, reply edge | Unresolved remains unresolved; no authority is inferred. | recommendation; uncertainty |

**7. Known exclusion / duplicate / unresolved:** No exclusions, duplicate
occurrences, or unresolved items are recorded in the current owner-primary
annotation. The messages are one thread; the two reply edges and message IDs
are structural evidence, not extra claims.

**8. Reference fidelity review:** [ ] all three messages exact  [ ] message
order and IDs faithful  [ ] one thread preserved  [ ] both reply edges faithful
 [ ] “unresolved” is not converted into a decision.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] frozen structured chat JSON was
reviewed.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### C02 — Structured Multi-speaker Chat

**1. Case ID / source type:** `C02` / Chat. The reference has 8 elements in
two threads: six messages, one quote, and one code part.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/C02/revision-001/source.json`
(the frozen structured conversation; do not use a live chat export).

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/C02/revision-001/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/C02/revision-003/owner-primary-gold.json`
(Gold revision-003; SHA-256 in the inventory above).

Additional locator/identity artifact:
`tests/evals/parser_note_completeness/v1/governance/C02/revision-002/owner-speaker-identity-assertions.json`
— SHA-256 `bfabff5fa7bf9ce6ae5380065151b08a5c5b8da1e7f845d2cd74ed149e7ab424`.
It is owner-approved and independent-review pending; it records raw speaker
identity assertions only and does not authorize a threshold or score.

**5. Bounded source evidence / locator:**

- Messages 001–004 in `c02-thread-main`: “Freeze the parser contract before
  implementation”, “keep the source binding”, fixed-byte digest verification,
  and “review evidence without changing the contract”.
- Message 002 quote: deliberate recurrence of message 001's contract rule.
- Messages 005–006 in `c02-thread-followup`: “preserve the original bilingual
  order” and “this thread remains independent”.
- Chat locators retain message ID, sequence, thread, reply-to ID, speaker
  identity, and part kind. The code part is `digest = sha256(source_bytes).hexdigest()`.

**6. Expected claims (6):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| C02-EC01 | Freeze the parser contract before implementation. | critical | `c02-message-001-element`; supporting quote `c02-message-002-quote-1` | The quote is recurrence, not a new claim. | recommendation |
| C02-EC02 | Keep the source binding first. | major | `c02-message-002-element`, message 002, reply to 001 | Source binding is preserved before later steps. | recommendation |
| C02-EC03 | Verify the digest using fixed source bytes. | critical | `c02-message-003-element` + code part `c02-message-003-code-1` | Exact operation is `sha256(source_bytes).hexdigest()`. | procedure |
| C02-EC04 | Review should inspect evidence without changing the contract. | critical | `c02-message-004-element`, reply to 003 | Review boundary is evidence-only; no contract mutation. | condition |
| C02-EC05 | Preserve the original bilingual order. | major | `c02-message-005-element`, thread follow-up | Chinese/English order remains source order. | recommendation |
| C02-EC06 | The follow-up thread remains independent. | major | `c02-message-006-element`, reply to 005 | Applies to `c02-thread-followup`, separate from main thread. | conclusion |

**7. Known exclusion / duplicate / unresolved:** One duplicate occurrence is
recorded: `c02-message-002-quote-1` repeats the claim in message 001, creates
no new expected claim, and remains retained for Parser measurement. The code
part is supporting evidence, not a separate claim. No exclusions or unresolved
items are recorded. Stable source `speaker_id` is an additional owner-approved
identity assertion to review at the linked artifact; it is not hidden or
derived from display names.

**8. Reference fidelity review:** [ ] all six messages exact  [ ] quote and
code part kinds faithful  [ ] message order/sequence faithful  [ ] two thread
memberships and reply edges faithful  [ ] speaker IDs match the linked identity
record  [ ] bilingual order faithful.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] frozen structured chat JSON was
reviewed.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### S01 — Synthetic Study Board

**1. Case ID / source type:** `S01` / Screenshot. The reference has 3 UI-text
regions in one image/frame section.

**2. Source:**
`tests/evals/parser_note_completeness/v1/fixtures/S01/revision-001/source.png`
(open the image directly).

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/S01/revision-001/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/S01/revision-002/owner-primary-gold.json`
(Gold revision-002; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:** Inspect the image in reading order:
`s01-element-0` “Synthetic Study Board”, `s01-element-1` “Parser lane ready”,
and `s01-element-2` “No external assets”. The reference records exact image
identity and normalized geometry for each UI-text region.

**6. Expected claims (3):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| S01-EC01 | The board is titled “Synthetic Study Board”. | minor | Image region `s01-element-0` | Board identity is context. | background_context |
| S01-EC02 | The displayed status is “Parser lane ready”. | major | Image region `s01-element-1` | Visible UI status; do not generalize beyond the image. | conclusion |
| S01-EC03 | The board states “No external assets”. | major | Image region `s01-element-2` | Visible provenance-scope statement. | limitation |

**7. Known exclusion / duplicate / unresolved:** No exclusions, duplicate
occurrences, or unresolved items are recorded.

**8. Reference fidelity review:** [ ] all three visible texts exact  [ ] image
identity exact  [ ] UI-text kinds and reading order faithful  [ ] normalized
geometry points to the correct regions.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] selected PNG is the reviewed image.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

### S02 — Ordered Overlapping Screenshot Set

**1. Case ID / source type:** `S02` / Screenshot. The reference has 6 UI-text
regions across two ordered images.

**2. Source:** The profile-bound source manifest is
`tests/evals/parser_note_completeness/v1/fixtures/S02/revision-002/source_manifest.json`.
Open the actual visual source files directly, in this order:

- `tests/evals/parser_note_completeness/v1/fixtures/S02/revision-002/source-001.png`
  — image 1, SHA-256 `47617d8a01d6d7d3e47fc8b521c96b677bd5f18d170eeeaf8f4eacc18fc7c5ad`.
- `tests/evals/parser_note_completeness/v1/fixtures/S02/revision-002/source-002.png`
  — image 2, SHA-256 `90ad2a83c837d12586c76d72bddd11293fd2ed6e3c705addb04cb2d794770c4e`.

**3. Reference:**
`tests/evals/parser_note_completeness/v1/reference_documents/S02/revision-002/normalized_document.json`.

**4. Gold:**
`tests/evals/parser_note_completeness/v1/governance/S02/revision-003/owner-primary-gold.json`
(Gold revision-003; SHA-256 in the inventory above).

**5. Bounded source evidence / locator:** Review image 1 before image 2. Image
1 shows “畫面一 / Screen One”, “共同內容 / Shared Content”, and
“重疊標籤 / Overlay Badge”; image 2 shows “畫面二 / Screen Two”, the repeated
“共同內容 / Shared Content”, and “後續狀態 / Follow-up State”. The reference
maps `s02-element-0..2` to image 1, `s02-element-3..5` to image 2, and records
normalized top-left geometry plus image SHA-256. “Shared Content” is
intentionally one claim with two supporting locators.

**6. Expected claims (5):**

| ID | Claim / semantic meaning | Importance | Supporting source locator | Qualifier / condition / exception | Category |
| --- | --- | --- | --- | --- | --- |
| S02-EC01 | Image 1 is labeled “畫面一 / Screen One”. | minor | Image 1 region `s02-element-0` | Sequence context. | background_context |
| S02-EC02 | “共同內容 / Shared Content” occurs across both images. | major | Image 1 `s02-element-1`; image 2 `s02-element-4` | Same visible content across two ordered images; one claim, two supports. | core_concept |
| S02-EC03 | Image 1 contains the “重疊標籤 / Overlay Badge” region. | major | Image 1 region `s02-element-2` | Distinct visible overlap condition. | condition |
| S02-EC04 | Image 2 is labeled “畫面二 / Screen Two”. | minor | Image 2 region `s02-element-3` | Sequence context. | background_context |
| S02-EC05 | Image 2 contains the “後續狀態 / Follow-up State” region. | major | Image 2 region `s02-element-5` | Final displayed status in the ordered set. | conclusion |

**7. Known exclusion / duplicate / unresolved:** No exclusions, duplicate
occurrences, or unresolved items are recorded. The second Shared Content
occurrence is additional support for S02-EC02, not a separate claim and not an
exclusion.

**8. Reference fidelity review:** [ ] image order is source-001 then source-002
 [ ] all six visible texts exact  [ ] image identity/SHA bindings exact  [ ]
normalized geometry points to the right regions  [ ] shared-content recurrence
is represented as one claim with two supports.

**9. Fixture provenance / rights / privacy review:** [ ] project-authored
synthetic provenance is accurate  [ ] redistribution is permitted  [ ] no
private or personal source material  [ ] both PNGs and the source manifest were
reviewed.

**10. Case decision:** [ ] Approve  [ ] Reject  [ ] Changes Required

**11. Reviewer notes:**

______________________________________________________________________________

## Cross-case reviewer completion

The reviewer may use this short final pass after all 13 sections:

- [ ] I opened each selected frozen source artifact and, where applicable,
  each visual component (PDF, PNG, VTT, HTML, or structured JSON).
- [ ] I compared each selected source against its selected normalized
  reference, including text, order, structure, language, and typed locator
  details relevant to that source type.
- [ ] I reviewed all 82 claim rows without viewing candidate scores.
- [ ] I checked every importance, qualifier/condition/exception, category,
  locator, structure relation, exclusion, duplicate, and unresolved disposition.
- [ ] I reviewed provenance, redistribution rights, and privacy as factual
  human attestations; repository history alone is not sufficient evidence.
- [ ] I did not approve my own primary work for the same governed scope.
- [ ] I recorded every decision in the result template only after checking the
  frozen source, reference, and exact owner-primary Gold binding.

Record the final per-case results in
`dev_state/parser-note-completeness/human-review-result-template.json`. That
file intentionally contains only the requested machine-readable fields. It is
an intake/result aid, not a formal authority artifact.
