# Parser & Note Completeness Human Review Workbook

This workbook is a review aid, not an approval record. Complete the companion
`human-review-result-template.json` and publish successor immutable governance
and Gold artifacts only after review. Do not edit the current draft packets in
place.

## What the reviewer is approving

For each case, the reviewer must separately decide:

1. the exact selected source bytes were created/acquired as described;
2. the project owns or may redistribute those bytes;
3. the privacy disposition is acceptable;
4. the reference document faithfully represents source text, order, structure,
   languages, and locators;
5. the expected evidence/claims are complete and atomic, with conditions,
   qualifiers, exceptions, quantities, and attribution preserved;
6. category applicability and critical/major/minor rationales are justified;
7. locator and structure assertions are correct;
8. claims are neither duplicated nor incorrectly split/merged;
9. every dispute is resolved or explicitly remains unresolved;
10. the primary annotator and reviewer satisfy Q25 independence for the exact
    scope.

An approval of source ownership does not approve Gold. An approval of Gold does
not approve the scorer, gate, or formal execution contract.

## Exact selected cases

All paths below are relative to
`tests/evals/parser_note_completeness/v1/`. Compare the source directly with the
reference; the short excerpts are navigation aids only.

| Case | Revision | Source / SHA-256 | Reference / SHA-256 | Review packet | Content and locator inventory | Bounded navigation excerpts |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | revision-001 | `fixtures/P01/revision-001/source.pdf` / `2ec844a220a426e14eca5a60a9d19767751bee022b67cb3998a110cdf382b973` | `reference_documents/P01/revision-001/normalized_document.json` / `a6a86086598084f9557bda254857439511237aa07117eecbefb8db5d08c22db3` | `governance/P01/revision-001/gold-review-packet.json` | 45 elements; headings, prose, lists, code; PDF locators | first: “Reliable Queue Workers”; last: `./worker --print-lease-policy` |
| P02 | revision-001 | `fixtures/P02/revision-001/source.pdf` / `5ee241278ce972aa4157b18d51a8282be59bf4abbfab6bfe1923b12364d70816` | `reference_documents/P02/revision-001/normalized_document.json` / `70bbca910c764daf4423e793962d8509aa4ab6900ba3015746c8758156277e6e` | `governance/P02/revision-001/gold-review-packet.json` | 50 elements; bilingual prose, table, figure/caption; PDF locators | first: “雙語資料系統報告 / Bilingual Data Systems Report”; last discusses two vector figures |
| P03 | revision-002 | `fixtures/P03/revision-002/source.pdf` / `a5fceec1d03317f6c7ca7dab576ef18b54124d31a1ef68b53511ed36741b4e26` | `reference_documents/P03/revision-002/normalized_document.json` / `2fb7ffd00853c4973184f85fb12b148bbfbcb0e1c48ca21dd8e0bd927768f13e` | `governance/P03/revision-002/gold-review-packet.json` | 15 OCR-region elements; PDF page and geometry locators | first: “第一頁：穩定資料流程”; last describes deterministic bytes |
| P04 | revision-002 | `fixtures/P04/revision-002/source.pdf` / `c3ead34126004b0639ed1366e85bfb1af1691c04e92c949403cfad9e94fecd0e` | `reference_documents/P04/revision-002/normalized_document.json` / `c5bdcd64d595634a565e16c8d555f0e356a5fe6d2ff63d7d643358799b26a159` | `governance/P04/revision-002/gold-review-packet.json` | 26 elements; mixed native/raster, formula, table; partial geometry | first: “公式與表格 / Formula and Table”; last discusses normalized geometry |
| W01 | revision-001 | `fixtures/W01/revision-001/source.html` / `1ab20dc2725df5d5066e2d6113487b4f9ae16973db9709f3bd66e53e4e52f43b` | `reference_documents/W01/revision-001/normalized_document.json` / `999839f1e79da04a5c7dd50ca8c6743aacf25b638712ad6095d9e0b044232747` | `governance/W01/revision-001/gold-review-packet.json` | 5 elements; prose, list, code; Web locators | first: “Parser Completeness Slice”; last is a two-line `normalize` function |
| W02 | revision-001 | `fixtures/W02/revision-001/source.html` / `368f3bf9192bb7c9099e83f95e8d0b72cffbc0dab3ee04ac81e4415fcca32e51` | `reference_documents/W02/revision-001/normalized_document.json` / `a56bde702d26ed1b0e2d0b0693bdf5bc60176097bd394ab72050df693c392ad1` | `governance/W02/revision-001/gold-review-packet.json` | 37 elements; bilingual hierarchy, list, table, figure/caption, code, UI noise; Web locators | first: “可追蹤的資料流程 / Traceable Data Workflows”; last is a synthetic footer |
| W03 | revision-001 | `fixtures/W03/revision-001/source.html` / `a6b8495a77d7d5fd95fb4ba9ca98aa56e9043c09447f42b15090bd1dc134f2df` | `reference_documents/W03/revision-001/normalized_document.json` / `7f487bccc28484982f71f4f24ea1a501724c9adb2797cd35bcd0e16ef394832f` | `governance/W03/revision-001/gold-review-packet.json` | 28 elements; article hierarchy, list, table, figure/caption; Web locators | first: “離線文章快照 / Offline Article Snapshot”; last says every element comes from fixed bytes |
| Y01 | revision-001 | `fixtures/Y01/revision-001/source_snapshot.json` / `66765dcc81f041b8d20c1484db4651f063d9ed53cac82d3bc900123ea97d873a` | `reference_documents/Y01/revision-001/normalized_document.json` / `c1937ce21c5baba204428eabbeae4d5b52945ca7a06220b9012ade17ba7e6251` | `governance/Y01/revision-001/gold-review-packet.json` | 12 chapter/cue elements; cue/timing locators; platform identities unavailable by policy | first: “Contract Before Code”; last describes recovery reconciliation |
| Y02 | revision-001 | `fixtures/Y02/revision-001/source_snapshot.json` / `a3b1b53f0450ac63bf6ad327d1adfad066ff9a4c706b2614db8a03b96b1f97ec` | `reference_documents/Y02/revision-001/normalized_document.json` / `e018e28558b6b69604ab6249be99e57bb25729eb878dadad40c7e59e84d8c2d6` | `governance/Y02/revision-001/gold-review-packet.json` | 11 bilingual chapter/cue elements; cue/timing locators; platform identities unavailable by policy | first: “契約 / Contract”; last labels the draft development-only |
| C01 | revision-001 | `fixtures/C01/revision-001/source.json` / `d0f4543a2e71526ec208dbd5b3f645bedc074145ec3e91de5c017276f9fd6288` | `reference_documents/C01/revision-001/normalized_document.json` / `0be80f1cdd163fc0aaeefce69b127aa27d5661c496ab65a0083ab0f91263f390` | `governance/C01/revision-001/gold-review-packet.json` | 3 messages; message/thread/reply/sequence locators | first asks to capture the parser contract; last says not to invent authority |
| C02 | revision-001 | `fixtures/C02/revision-001/source.json` / `7ac22d5006e724078d5db448768f8e85b704d4ef17ebaebd74f7d148eeb4a77e` | `reference_documents/C02/revision-001/normalized_document.json` / `ce6d935830bd56d3b55a56f1b547dac78c798ab8249d224f7b0f19ac179e3e0e` | `governance/C02/revision-001/gold-review-packet.json` | 8 bilingual messages/quote/code elements; two threads and reply relations | first is Alice's bilingual contract message; last confirms thread independence |
| S01 | revision-001 | `fixtures/S01/revision-001/source.png` / `d0c61b0f04a224d0c32f55fedfab7d5bb63c6a30d0d40430ca7c255c2125f0bd` | `reference_documents/S01/revision-001/normalized_document.json` / `b68a8ca56d829880a175b25d23c9ddca4d501a08600702fd6192f39752c73057` | `governance/S01/revision-001/gold-review-packet.json` | 3 UI-text regions; image identity and geometry locators | first: “Synthetic Study Board”; last: “No external assets” |
| S02 | revision-002 | `fixtures/S02/revision-002/source_manifest.json` / `34ac32424526527808db6c54f615ff9b5e2f2594a89590102902c1cb8ecaeb30` | `reference_documents/S02/revision-002/normalized_document.json` / `e5f58120026419c284a9a8bbbf90d31b122c19aa68daaece0f6138fcb33ed98f` | `governance/S02/revision-002/gold-review-packet.json` | 6 UI-text regions across two ordered overlapping images; image identity and geometry | first: “畫面一 / Screen One”; last: “後續狀態 / Follow-up State” |

## Provenance evidence already in the repository

The current candidate and producer-configuration records consistently describe
project-authored synthetic sources. Git history records the selected source
addition under these commits: P01 `759334c`; P02 `d2e0764`; P03/P04/S02
`533ace2`; W01 `0eca68d`; W02/W03/Y02/C02 `b54d3ac`; Y01 `60d9709`; and
C01/S01 `18c995e`. This is useful creation history, but it is not by itself an
ownership, redistribution, privacy, or independent-review decision.

Proposed fixture decision, if the owner can truthfully attest it: “The exact
selected bytes are project-authored synthetic fixtures, may be redistributed
with this repository, contain no private or personal source material, and match
the recorded creation method.” The human is approving that factual and legal
statement, not merely acknowledging that the files exist.

Riley Lai approved that owner statement for all 13 exact selected bindings on
2026-08-31 (`1A 2A 3A`). The binding is recorded in
`human-review-intake.json`. This closes only the human-owner decision; Q25
independent fixture rights/privacy review remains pending for every case.

## Case review worksheet

Repeat this checklist for every case and record exact IDs in the companion JSON:

- [ ] Source digest matches the table and external digest file.
- [ ] Creation/acquisition provenance is accurate and complete.
- [ ] Ownership or redistribution permission is evidenced.
- [ ] Privacy disposition is evidenced.
- [ ] Every reference element is faithful to source text and modality.
- [ ] Element order, section hierarchy, kinds, languages, and locators are correct.
- [ ] Expected evidence items preserve all truth conditions and qualifiers.
- [ ] Expected claims are complete, atomic, and not duplicated.
- [ ] Category applicability is decided before candidate scores are viewed.
- [ ] Critical/major/minor decisions have counterfactual rationales.
- [ ] Structure and locator assertions are complete where semantically needed.
- [ ] Exclusions are explicit and Q12-owned, not silently removed.
- [ ] Disputes and unresolved items are listed.
- [ ] Primary annotator and independent reviewer identities are recorded.
- [ ] The reviewer did not approve their own work for the same governed scope.

## C01 proposed decisions requiring review

C01 is the only case with draft scorable Gold. It proposes three expected
claims bound one-to-one to the three message elements, with importance
`critical`, `major`, `critical` in source order. A reviewer must decide:

- whether each full message is one atomic evidence item and one expected claim;
- whether the two `critical` classifications satisfy the Q7 counterfactual bar;
- whether “keep chat and screenshot separate” is properly `major`;
- whether message order, thread identity, and two reply edges need explicit
  structure/locator assertions;
- whether every category is applicable or not applicable;
- whether any claim needs splitting, merging, additional qualifier text, or an
  exclusion;
- whether the diagnostic generated-claim mappings remain correct after Gold is
  reviewed.

The proposed answer is to retain three claims and the source order, but to
withhold all importance and authority approval until the reviewer supplies the
required rationales and Q25 evidence.

## Agent pre-review findings

The following are bounded source/reference discrepancies found before human
review. They narrow the review scope; they are not approvals.

- **P02:** do not approve the current reference. Its native Chinese font is not
  embedded and does not render faithfully in the independent PDF render. Four
  source paragraphs are absent, the first table's three header cells do not
  match the source, and two figure captions contain text not present in the
  source.
- **P03:** decide whether the five `掃描頁碼 N` labels and ten `區域甲`/`區域乙`
  labels belong in the reference or in explicit Q12 exclusions. They cannot be
  silently absent from OCR/text measurement.
- **P04:** do not approve the current reference. Native Chinese has the same
  non-embedded-font problem; one page-1 paragraph and four raster-region labels
  are absent. The formula label also needs an explicit keep/exclude decision.
- **W02/W03:** each reference omits the visible text inside its relationship
  figure. Add the text or record an explicit exclusion.
- **C02:** decide whether stable source `speaker_id` is an applicable Chat
  identity assertion. The reference preserves speaker display names only as
  message text.
- **P01/W01/Y01/Y02/C01/S01/S02:** no obvious discrepancy was found in the
  bounded pre-review. Human fidelity and Gold approval are still required.

Recommended disposition: correct the repository-demonstrable P02/P04 fixture
rendering and reference omissions in successor revisions; ask a human only for
the genuine inclusion/exclusion and speaker-identity choices. Do not approve
the current drafts in place.

## Batched authority checkpoint

1. **Fixtures — all 13 cases.** Decide ownership/redistribution, privacy,
   provenance accuracy, and independent fixture approval for each exact digest.
   YES makes only the fixture eligible for the next governed revision; NO blocks
   only the affected case, which blocks the full 13-case baseline because full
   membership is fixed.
2. **Reference and Gold — all 13 cases.** Decide fidelity, evidence/claim
   completeness, applicability, importance, locators/structure, duplication,
   disputes, and independent review. YES authorizes successor Gold/governance
   artifacts; NO returns the affected case for correction and blocks the full
   baseline.
3. **Q25 roles — benchmark-wide and artifact-scoped.** Supply primary annotator,
   independent reviewer, fixture approver, scorer approver, and governance
   approver identities/scopes. This blocks the governed scope; missing fixture
   or Gold independence for any case blocks the full baseline.
4. **Parser contract — benchmark-wide.** Approve or revise the raw-measurement
   decisions in `04-formal-baseline-readiness.md`. This blocks every applicable
   Parser result and therefore the whole baseline.
5. **Formal execution — benchmark-wide.** Approve the minimal formal manifest,
   plan/provenance/store/publication semantics and the OS/container no-egress
   mechanism described in the readiness audit. This blocks the whole baseline.

Local audit recommendation for no-egress: use a pinned Linux benchmark image
under Docker Desktop with `--network none`, read-only root, dropped capabilities,
no credentials or Docker socket, explicit mounts, outer `docker inspect`
verification, three denied DNS/socket/HTTP probes, and an outer-launcher-issued
attestation bound to the invocation and terminal package. Do not use missing
credentials, mocks, `sandbox-exec`, or host-wide `pfctl` as the formal proof.

Codex cannot decide items 1–3 because they require factual/legal/privacy and
independent human authority. It cannot decide items 4–5 because the frozen Q14
and Q16–Q24 owners explicitly leave those semantics pending.

## Owner decisions and successor preparation — 2026-08-31

Riley Lai selected `4A 5A 6A 7A`. The exact owner decisions are recorded in
`human-review-intake.json`; they do not count as independent review.

- P02/P03/P04/W02/W03: all identified visible content is retained; no Q12
  exclusion was approved. Corrected successor references were built. P02
  `revision-002` and P04 `revision-003` also replace the non-self-contained
  native font path with selectable Type 3 glyph programs derived from the
  digest-locked repository Noto font. Every final PDF page was rendered and
  visually inspected.
- C02: the six stable source `speaker_id` values are applicable identity
  assertions. The owner record is
  `governance/C02/revision-002/owner-speaker-identity-assertions.json`; it
  authorizes raw missing/incorrect reporting only, not a threshold or parser
  change.
- C01: the owner approved three atomic claims in source order with importance
  `critical`, `major`, `critical`, three message identities, one shared thread,
  canonical order, and two reply edges. The owner-primary record is
  `governance/C01/revision-002/owner-primary-annotation.json`. It uses only the
  frozen Q7 enums and remains independent-review pending.
- P01/W01/Y01/Y02/C01/S01/S02: bounded reference fidelity is owner-approved;
  independent review remains pending.

P03/W02/W03 successor sources are byte-identical to the already owner-approved
sources. P02 and P04 necessarily have new exact source digests after the font
and layout correction, so their factual rights/privacy binding requires one
owner re-confirmation before a successor full profile may treat them as
owner-approved.
