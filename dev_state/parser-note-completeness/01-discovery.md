# Parser & Note Completeness Discovery

Query date for time-sensitive external information: **2026-08-12**.

## 1. Executive summary

The recommended decision is a **combined approach**, sequenced as follows:

1. Redesign long-source generation around bounded, section-complete evidence.
2. Preserve source structure and locators in a common normalized-document model.
3. Improve only the parsers that fail the fixed benchmark.

The strongest current finding is not a QA `top_k` problem. Proposal generation
does not retrieve source chunks at all. It sends the complete persisted
`SourceDocument.raw_text` to one Chat Completions request with a fixed
`max_tokens=1400` (`SupplementProposeOrchestrator.propose_change_request`,
`src/orchestrators/supplement_propose_orchestrator.py:260-314`). A PDF or OCR
source may contain up to 200,000 characters, but the prompt prefers 6-10 notes
and the schema rejects more than 12 notes. A deterministic probe confirmed that
13 valid, source-supported notes fail schema validation.

Content starts being lost at two different layers:

- **Extraction:** PDF, URL, YouTube, and OCR adapters flatten content to plain
  text and discard most layout and locator metadata. Scanned PDFs are rejected.
- **Generation:** every source, regardless of length, is compressed in one call
  into `title`, `summary`, `concepts`, and at most 12 flat notes. There is no
  section coverage record, completeness verifier, dynamic output budget, or
  source locator in generated claims.

The Notion append layer does not trim text, but it flattens concepts into one
paragraph and renders every note as a paragraph whose text begins with `- `.
It cannot preserve nested lists, tables, code blocks, quotations, or per-claim
source locators.

This discovery did not modify runtime code, tests, dependencies, lock files, or
production configuration. It made no provider, YouTube, Notion, or Telegram
call and performed no commit or push.

## 2. Evidence standard and classification

Capability labels in this report mean:

1. **Implemented + tested**: concrete production symbol and relevant test.
2. **Implemented, weak validation**: code exists, but tests use mocks or do not
   represent the requested layout/language/failure case.
3. **Documented claim, insufficient code evidence**.
4. **Unsupported**.

README statements are not treated as evidence. The main implementation evidence
is the adapter, orchestrator, schema, configuration, and test code referenced in
each row.

## 3. Current capability matrix

### 3.1 PDF

Current stack: `pypdf 6.12.1`; 10 MiB, 100 pages, and 200,000 extracted
characters. `PyPDFParserClient` loops through every page, calls
`page.extract_text()`, removes empty pages, and joins non-empty page text with
two newlines (`src/tools/pdf_parser_tool.py:38-92`).

| Requested capability | Level | Code/test evidence | Preserved | Lost or limited |
| --- | --- | --- | --- | --- |
| Native-text PDF | 2 | Real `PdfReader` code; `tests/test_pdf_parser_tool.py` tests only a fake parser | final text, total page count, filename outside parser | page boundary/number, bbox, font, heading, reading order metadata |
| Scanned PDF | 4 | Empty text layer raises `No extractable text`; no OCR routing | none | all image text and layout |
| Chinese/English mixed | 2 | Unicode strings pass through, but no representative real mixed PDF test | characters returned by pypdf | no quality/CER/reading-order evidence |
| Tables/images/code | 4 for structure; 2 for incidental text | only `extract_text()` | incidental glyph text may survive | cells, image identity/caption, code block boundary |
| Headings/lists | 2 | plain-text extraction only | visual line text when pypdf emits it | semantic block type and hierarchy |
| Fallback | 4 | no OCR/layout fallback | — | scanned or damaged text-layer PDF fails closed |

The persisted `SourceDocument` stores only source type, display filename,
content hash, and flat text (`src/db/models.py:62-79`). `page_count` appears in
ingestion workflow metadata but is not available to proposal generation.

### 3.2 Web pages

Current stack: `urllib` fetch plus `trafilatura 2.0.0`; 5 MiB response, five
redirects, 30-second timeout, public HTTP(S) destinations only. The parser calls
`trafilatura.extract(html)` with defaults and persists only returned plain text
and the original URL (`src/tools/url_article_parser_tool.py:198-239`).

| Requested capability | Level | Evidence | Preserved | Lost or limited |
| --- | --- | --- | --- | --- |
| Static HTML | 2 | production fetch/extract code; tests focus on safety and fake extracted text | original URL, main extracted text | title/byline/date/link locators not persisted |
| JavaScript dynamic page | 4 | no browser or JS runtime | initial HTML only | rendered DOM and lazy-loaded content |
| Main-content extraction | 2 | Trafilatura call exists | selected main text | no representative precision/recall fixture |
| Nav/ad/comment noise | 2 | delegated to Trafilatura defaults | likely reduced | no repo benchmark or explicit settings |
| Heading/list/table/code structure | 4 | default text output, no Markdown/element result | visible words may survive | semantic structure and DOM/CSS locator |
| Fallback | 4 | no readability or browser fallback | — | extraction failure is terminal |

The tests in `tests/test_url_article_parser_tool.py` strongly cover SSRF,
redirect, content-type, and response-size safety; they do not measure article
coverage or boilerplate rate.

### 3.3 YouTube

Current stack: `youtube-transcript-api 1.2.4`. The adapter asks for `languages=["en"]`,
tries new and legacy library interfaces, then joins only snippet text with
newlines (`src/tools/youtube_transcript_tool.py:72-140`).

| Requested capability | Level | Evidence | Preserved | Lost or limited |
| --- | --- | --- | --- | --- |
| Manual captions | 2 | library fetch path exists; fake-client test only | transcript text, video ID | manual/automatic provenance |
| Automatic captions | 2 | dependency can provide them, but implementation does not select/report track type | text if chosen by library | confidence and generated status |
| Non-English captions | 4 | hard-coded English request | — | all other languages unless exposed as English track |
| No-caption video | 4 | returns `YOUTUBE_TRANSCRIPT_NOT_FOUND` | explicit failure | no audio download/ASR fallback |
| Timestamps | 4 | `_extract_text` discards snippet start/duration | — | segment and timestamp locators |
| Paragraph/section splitting | 4 | one line per API snippet only | API order | semantic paragraphs and chapters |
| Fetch fallback | 2 | client API compatibility fallback only | same English text | no `yt-dlp`, audio, or ASR fallback |

`tests/test_youtube_transcript_tool.py` validates URL handling and fake text, not
the real client, language selection, manual/automatic preference, timestamps,
or failure recovery.

### 3.4 Chat text

Current stack: no parser. `ChatTextIngestionOrchestrator` trims leading/trailing
whitespace, rejects empty input and content above 10,000 characters, hashes and
persists the remainder verbatim (`src/orchestrators/chat_text_ingestion_orchestrator.py:54-105`).

| Requested capability | Level | Evidence | Preserved | Lost or limited |
| --- | --- | --- | --- | --- |
| Speaker/order/time/thread | 2 | raw input is preserved verbatim | any labels/order/times explicitly pasted | no parsed fields or validation |
| Markdown/code/quotes | 2 | no transformation beyond outer `.strip()` | literal source characters | no semantic block type/locator |
| Structured chat import | 4 | API accepts one string only | — | message IDs, reply edges, attachments |
| Tests | 1 for verbatim short text and length bound | `tests/test_source_ingest_api.py` | exact stored text | no representative multi-speaker/thread fixture |

### 3.5 Multiple screenshots

Current stack: Pillow 11.3.0, pytesseract 0.3.13, system Tesseract 5.5.0 with
`eng`, `chi_tra`, and `chi_sim`. Each image is grayscaled and autocontrasted,
then OCRed with `eng+chi_tra+chi_sim --psm 6`. Non-empty results are joined with
`[Image N: filename]` markers (`src/tools/image_ocr_tool.py:49-121`). Limits are
10 images, 5 MiB each, 20 MiB total, and 40 million pixels per image.

| Requested capability | Level | Evidence | Preserved | Lost or limited |
| --- | --- | --- | --- | --- |
| Image order/merge | 1 for API order; 1 for Telegram order | tool preserves input order; media group sorts by `message_id`; tests assert order | image ordinal and filename | capture timestamp and visual coordinates |
| Chinese/English OCR | 1 for configuration, 2 for quality | tests assert exact language/config; no real CER fixture | OCR characters | no measured CER/WER or confidence |
| Overlap deduplication | 4 | no text/image overlap detection | all OCR text | repeated adjacent content remains |
| Table/UI/context continuity | 2 | one shared source text and one proposal call; browser-chrome line filter | batch context and image markers | cells, regions, UI hierarchy, cross-image stitching |
| Failure behavior | 2 | blank individual image is skipped; batch succeeds if any image has text | non-empty images | partial OCR can silently produce a smaller successful source |

The screenshot grounding/repair suite is materially stronger than other parser
tests, but fixtures contain prewritten OCR strings, not actual screenshot
pixels. It verifies order, browser-chrome filtering, Traditional Chinese
language rules, and grounded output; it cannot establish OCR accuracy.

## 4. Evidence-backed pipeline trace

### 4.1 Actual production flow

```text
source
  -> source-specific adapter
  -> flat raw_text
  -> SourceDocument(raw_text)
  -> [no normalized document object]
  -> [no source chunks]
  -> entire raw_text selected
  -> one supplement_proposal_v7 call (temperature 0.2, max_tokens 1400)
  -> strict title/summary/concepts/notes schema
  -> pending ChangeRequest.proposal_json
  -> human accept
  -> flat Notion toggle + paragraph blocks
```

Important distinctions:

- The Notion indexing chunker in `src/rag/chunker.py` is for indexed Notion
  content. It is not called by source ingestion or proposal generation.
- QA `top_k` is not reused by proposals. `SupplementProposeOrchestrator`
  performs duplicate checks against indexed Notion knowledge, then supplies
  the entire source text to the proposal prompt.
- There is no explicit input token preflight. The 200,000-character extraction
  limit is not a model context limit. Model-dependent over-context behavior is
  therefore not deterministically controlled by the backend.
- The OpenAI adapter uses Chat Completions and a JSON-only instruction, but does
  not send `response_format` or a provider-native JSON Schema. Pydantic validates
  the returned text only after generation (`src/providers/llm.py:61-100`).
- The provider records `finish_reason`, but the proposal orchestrator neither
  checks it nor treats `finish_reason="length"` as incomplete. Invalid truncated
  JSON will fail, but a valid short JSON response can be accepted as success.

### 4.2 Fixed existing-fixture trace

Fixture: `live_shaped_mysql_five_image_batch` in
`tests/fixtures/screenshot_proposal_fixtures.json`. This is the most
representative existing multi-image, Traditional Chinese fixture. It contains
five OCR sections, explicit order, headings/fields, and a complete expected
proposal.

| Stage | Observed value |
| --- | ---: |
| Pages / images / subtitle segments | 0 / 5 / 0 |
| Raw fixture OCR | 212 characters; 53 token conservative estimate |
| Screenshot-normalized source | 186 characters; 47 token estimate |
| Normalized-document elements | not implemented |
| Source chunks | 0 |
| Selected chunks | 0; selection mode is whole source |
| Rendered system + user input | 3,627 characters; 907 token estimate |
| LLM calls | 1 main call; repair only after diagnosed screenshot validation failure |
| Configured main output budget | 1,400 tokens |
| Fixture proposal JSON | 485 characters; 122 token estimate |
| Proposal concepts / notes | 5 / 4 |
| Live Notion blocks | 11 if zone/date exist; 13 if both must be created |

Token estimates above are explicitly `ceil(characters / 4)`, not provider
billing tokens. The fixture output is an expected test artifact, not a recorded
live model response. Existing parser tests use fake clients and the repository
contains no real PDF/HTML/image/YouTube binary fixtures; current extraction
coverage, latency, and memory therefore remain unmeasured.

### 4.3 Red-capable completeness probe

The following command was run against the real schema without modifying tests:

```text
rtk uv run --no-env-file --frozen python -c '<validate 13 grounded notes>'
RED_CAPABLE expected completeness failure: notes List should have at most 12 items after validation, not 13
```

The probe is deterministic and catches the exact class of failure: a source
requiring more than 12 distinct notes cannot be represented, even when every
note is grounded. It does not prove that every short note is caused by the
schema; it proves the schema is a hard completeness ceiling.

### 4.4 Structured output and Notion conversion

Schema limits in `src/proposal_limits.py` are title 240 characters, summary
2,400, each concept 180, each note 1,400, 30 concepts, 12 notes, and 16,000 total
text characters. `SupplementProposalGeneratedSchema` requires only one concept
and one note (`src/orchestrators/supplement_proposal_schema.py:108-139`). It has
no fields for sections, procedures, examples, data, limitations, unresolved
questions, or source locators.

The backend owns citations, but ordinary non-duplicate proposal generation
merges an empty citation list. Parser locators do not exist to attach. The
Notion writer joins all concepts with semicolons and creates each rendered line
as a paragraph (`src/tools/notion_api_writer_client.py:226-258`). It does not
drop long text: Notion rich text is split into 2,000-character fragments inside
the same block. It does flatten structure.

## 5. Ranked root-cause hypotheses

| Rank | Hypothesis | Evidence and falsifiable prediction | Impact |
| ---: | --- | --- | --- |
| 1 | Fixed single-pass representation forces compression | one call, 1,400 output tokens, prompt prefers 6-10 notes, schema max 12; raising source information density will not raise notes above 12 | Critical across long sources |
| 2 | Source flattening loses evidence before generation | four adapters persist plain text with almost no locators/structure; a layout-aware benchmark should improve structure/locator scores even with the same generator | Critical for tables, scans, code, citations |
| 3 | No bounded all-section processing | zero source chunks and no section coverage map; adding section evidence should improve key-point recall especially for late/middle sections | Critical for long sources |
| 4 | Parser-specific omissions | scanned PDF unsupported; JS unsupported; YouTube English-only/no ASR; screenshot partial blank images accepted | High but source-dependent |
| 5 | Prompt encourages brevity and has an underspecified coverage taxonomy | 6-10 preference, “concise,” and only generic `concepts`/`notes`; a coverage-checklist prompt should improve category recall on short sources | Medium/high |
| 6 | Notion conversion flattens structure | all generated material becomes paragraphs; a structure-aware renderer should improve structural fidelity without changing text recall | Medium |
| 7 | Valid short fallback/termination can look successful | `finish_reason` ignored; partial OCR image skipped; duplicate branch intentionally emits two notes | Medium; observable by new completeness/partial-source status |
| 8 | Post-processing trims content | only whitespace normalization and screenshot noise filtering found; no general proposal trim/dedup | Low based on current evidence |

The first three hypotheses should be tested before adopting a new library.

## 6. External library and open-source comparison

All maintenance and release observations below were checked on 2026-08-12.
Project benchmarks are treated as vendor/project evidence unless an independent
paper is linked; they are not assumed to predict LearnLoop results.

### 6.1 PDF, layout, and OCR

| Candidate | Mixed Chinese/English and structure | Local compute / integration | License and maintenance | Discovery judgment |
| --- | --- | --- | --- | --- |
| [Docling](https://github.com/docling-project/docling) | layout, reading order, tables, code, formulas, images, OCR; unified JSON/Markdown | local CPU/GPU; Python/Docker; materially larger model stack | MIT code; individual model licenses must be checked; active 1,300+ commit repo | Strong layout benchmark candidate, not an automatic dependency choice |
| [Marker](https://github.com/datalab-to/marker) | OCR, math, tables, multi-column; project publishes FinTabNet-like benchmark | Python 3.10+, PyTorch; GPU preferred for throughput; optional LLM may send data depending on backend | GPL code plus restricted model-weight terms and commercial threshold | Technical candidate, legal/product-fit risk; do not shortlist for adoption without review |
| [MinerU](https://github.com/opendatalab/MinerU) | 109-language claim, scanned docs, formulas, tables, reading order, header/footer removal | offline CPU/GPU pipeline and heavier VLM modes; Docker available | custom MinerU license based on Apache 2.0 with extra conditions; 3.4 released 2026-06-18 | High-value Chinese/layout benchmark candidate; legal review required |
| [PyMuPDF4LLM](https://github.com/pymupdf/pymupdf4llm) | Markdown/JSON, page metadata, tables, images, OCR, multi-column | light CPU path compared with model pipelines; low integration cost | AGPL-3.0 or commercial license; 0.3.4 released 2026-02-14 | Good technical control, but incompatible with casual proprietary adoption |
| [Unstructured](https://github.com/Unstructured-IO/unstructured) | typed elements, page metadata, OCR and hi-res table/layout modes | fast mode lighter; hi-res adds inference/model dependencies; broad integration surface | Apache-2.0 repository, active | Useful broad baseline; dependency size and mode-specific quality must be measured |
| [PaddleOCR](https://www.paddleocr.ai/main/en/index/) | strong Chinese/English; OCR, layout, table, formula, unwarping modules | CPU/GPU; Paddle/PaddleX stack can be large; local | Apache-2.0; current docs and 2026 releases show active development | Primary OCR/layout comparator for Chinese-heavy samples |
| [Surya](https://github.com/datalab-to/surya) | OCR/layout/reading order/tables in 90+ languages | PyTorch, CPU or GPU; model download and memory overhead | GPL code plus restricted model-weight/commercial terms; active releases | Useful research comparator; adoption blocked pending license review |
| [RapidOCR](https://github.com/RapidAI/RapidOCR) | default Chinese/English; multiple multilingual ONNX models | ONNX/OpenVINO/Paddle backends; lighter CPU deployment | Apache-2.0; v3.8.1 released 2026-04-11 | Strong lightweight screenshot OCR comparator |
| [docTR](https://github.com/mindee/doctr) | detection + recognition, multilingual model-dependent; returns geometry | PyTorch or TensorFlow; GPU beneficial; medium/heavy | Apache-2.0; ongoing maintenance stated by repo | OCR geometry candidate, weaker default Chinese certainty than Paddle/RapidOCR; benchmark it |
| [Tesseract](https://github.com/tesseract-ocr/tesseract) | 100+ languages, including installed Traditional/Simplified Chinese; weak complex layout by itself | CPU, small operational footprint, already installed | Apache-2.0; v5 stable line active | Keep as baseline/fallback, not sole complex-layout OCR solution |

No public benchmark above is directly comparable to LearnLoop's five-source
end-to-end completeness metric. “Quantifiable improvement” therefore means a
paired gain on the fixed dataset in section 7, not a project README score.

Cross-cutting deployment assessment:

| Family | Dependency/CPU/GPU profile | FastAPI/RQ/Docker cost | Privacy boundary |
| --- | --- | --- | --- |
| pypdf, pdfplumber, Trafilatura, readability-lxml | small CPU-oriented libraries | low | fully local |
| PyMuPDF4LLM, Camelot, RapidOCR | native/ONNX assets; moderate CPU and image growth | low-medium | fully local after model/assets are present |
| Docling, Unstructured hi-res, PaddleOCR, docTR | model runtimes and larger images; CPU works for some modes, GPU improves throughput | medium-high; warm worker strongly preferred | fully local if model downloads are pre-staged |
| Marker, Surya, MinerU VLM modes | PyTorch/VLM stacks; highest RAM/VRAM and cold-start risk | high; separate worker/container recommended | local modes exist; optional hosted/LLM modes must remain disabled for private sources |
| Playwright/Crawl4AI | browser binaries and per-page browser memory | medium-high; isolate browser worker and enforce egress policy | page content remains local, but browsing necessarily contacts the source site |
| faster-whisper/WhisperX | model-size-dependent CPU/GPU, RAM/VRAM and disk | high for cold jobs; queued warm ASR worker | local transcription after permitted audio acquisition |

Exact cold/warm latency, peak memory, download size, and throughput are marked
**unknown for LearnLoop** until the fixed benchmark runs. Project-published
numbers are not substituted for measurements on the target macOS/Docker CPU and
optional GPU profiles.

### 6.2 Web extraction

| Candidate | Capability | Cost / license / maintenance | Judgment |
| --- | --- | --- | --- |
| [Trafilatura](https://github.com/adbar/trafilatura) | main content and metadata; current implementation uses only default plain text | Apache-2.0; lightweight and already present; published 500-document boilerplate benchmark exists | Keep as static baseline; first test structured/metadata options before replacement |
| [readability-lxml](https://pypi.org/project/readability-lxml/) | title + main HTML cleanup | Apache-2.0; tiny; 0.8.4.1 released 2025-05-03 after a yanked CJK-broken build | Cheap fallback/control, not enough for JS pages |
| [Crawl4AI](https://github.com/unclecode/crawl4ai) | Playwright rendering, scrolling and structured extraction | browser/runtime overhead; Apache-2.0 with required attribution clause since 0.5; active 0.9 line | Broad but high-integration option; likely excessive for simple fallback |
| [Playwright Python](https://github.com/microsoft/playwright-python) + Trafilatura | deterministic rendered DOM, explicit wait/scroll policy, then existing main-content extractor | Apache-2.0; active v1.60+; browser binaries and system deps increase image size/memory | Preferred narrowly scoped JS fallback benchmark |

Playwright is a browser, not a main-content extractor. It should remain behind
the URL tool boundary with SSRF validation before every navigation/redirect and
strict time, byte, resource, and private-network controls.

### 6.3 YouTube and speech

| Candidate | Capability | Cost / license / maintenance | Judgment |
| --- | --- | --- | --- |
| [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) | manual and generated captions; manual preferred when both exist; languages and timestamps available | MIT; light; active, but dependent on undocumented YouTube behavior | Keep primary caption path; stop discarding track metadata and timestamps |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | lists/downloads manual and automatic subtitles and audio | wheel/source is Unlicense; bundled executables have additional licenses; very active, frequent YouTube fixes | Good secondary subtitle/audio acquisition candidate, operationally volatile |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | local Whisper ASR with segment/word timestamps; quantized CPU/GPU modes | MIT; CTranslate2 and model weights; model size, latency, RAM/VRAM depend on model/quantization | Preferred no-caption ASR benchmark for local-first use |
| [WhisperX](https://github.com/m-bain/whisperX) | word alignment and optional diarization | BSD-family code; heavier GPU/alignment/pyannote stack and model terms | Use only if word timing/speaker separation passes a demonstrated need |

Audio download and transcription must be opt-in within a bounded worker job and
must not upload source audio to third parties. Local model downloads, licenses,
and disk footprint require a separate adoption decision.

### 6.4 Tables

| Candidate | Best fit | Constraints | Judgment |
| --- | --- | --- | --- |
| [Camelot](https://github.com/camelot-dev/camelot) | native-text ruled/whitespace tables; five parser modes in current project | not an OCR solution; table-focused, separate reading-order merge required; MIT | Add as a native-table specialist benchmark, not the document parser |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | character geometry, lines, rectangles, tables, visual debugging | native text only unless paired with OCR; manual settings often required; MIT | Strong diagnostic/control tool and table baseline |
| Docling / MinerU / PaddleOCR PP-Structure | tables embedded in document layout and reading order | heavier model pipelines | Prefer when whole-document order matters |

## 7. Fixed benchmark design: `parser-note-completeness-v1`

### 7.1 Frozen sample set

Freeze exact files, URLs, video IDs, rendered DOM snapshots, expected text, and
SHA-256 digests before comparing candidates. Network is acquisition-only;
scoring must replay local artifacts. Private material must not be used.

| ID | Source | Required characteristics | Gold annotation |
| --- | --- | --- | --- |
| P01 | native PDF | English technical paper, headings/lists/code, >=8 pages | page text, order, blocks, key facts, locators |
| P02 | native PDF | bilingual report with at least two tables and figures | same plus table cells/captions |
| P03 | scanned PDF | Traditional Chinese scan, >=5 pages, skew/noise | transcription, regions, reading order |
| P04 | mixed PDF | Chinese/English, native + scanned pages, formulas/table | modality per page, text/structure gold |
| W01 | static page | clean technical article with headings/list/code | DOM main-content gold and CSS/XPath anchors |
| W02 | static page | article with nav, ads, related links, comments | content/noise labels |
| W03 | dynamic page | main body appears only after JS; deterministic snapshot | rendered DOM, wait condition, main content |
| Y01 | YouTube | manual English captions with chapters | caption kind/language/start/duration/text |
| Y02 | YouTube | automatic Traditional Chinese or mixed captions | same, with ASR errors annotated |
| C01 | chat | multi-speaker Markdown, quote, code, timestamp | message/thread/order/block gold |
| C02 | chat | bilingual threaded discussion with reply references | same plus unresolved questions |
| S01 | screenshots | ordered bilingual UI/table sequence | OCR text, regions, image order, continuity |
| S02 | screenshots | adjacent captures with 20-30% overlap | same plus duplicate spans and merged gold |

P01/P02 and W01/W02 should be openly licensed stable artifacts. W03 must store
both initial HTML and rendered DOM. Y01/Y02 must store downloaded subtitle files
and only IDs/metadata allowed by their terms. Screenshot and chat cases should
be purpose-built synthetic fixtures to make exact gold redistribution safe.

### 7.2 Parser metrics

| Metric | Calculation |
| --- | --- |
| Text extraction coverage | matched normalized gold characters/words divided by gold total; also report per page/segment |
| OCR CER/WER | Levenshtein character/word edits divided by gold length; report Chinese CER and English WER separately |
| Structure preservation | micro/macro F1 over heading, list, table, code, quote, speaker, and paragraph block labels |
| Reading-order accuracy | 1 minus normalized pairwise ordering inversions over gold blocks |
| Duplicate rate | duplicated output tokens attributable to one gold span divided by output tokens |
| Noise rate | output tokens mapped to gold noise regions divided by output tokens |
| Locator coverage | supported extracted units with correct page/timestamp/image/DOM locator divided by supported units |
| Unsupported extraction | output semantic units not alignable to source; must be reported separately from OCR error |

### 7.3 Note-generation metrics

Gold evidence units are annotated into background, concepts, steps, examples,
data, definitions, constraints/risks/exceptions, conclusions, open questions,
and counterpoints. Each has importance (`critical`, `major`, `minor`) and one or
more source locators.

| Metric | Calculation |
| --- | --- |
| Key-point recall | weighted covered gold evidence / weighted gold evidence |
| Final-note completeness | macro-average recall over applicable evidence categories, then sample average |
| Unsupported-claim rate | unsupported atomic claims / all generated atomic claims |
| Citation precision/recall | supported claims with correct locator / cited claims; cited supported claims / supported claims |
| Redundancy | semantically duplicate note/evidence units / all output units |
| Readability | deterministic length/heading/list checks plus blinded human 1-5 score; no LLM-as-judge |

Parser metrics must be scored once on extracted artifacts. Generator variants
must then consume the exact same frozen parser output, so parser quality and
note-generation quality are not conflated.

### 7.4 Resource metrics

Capture wall time, CPU time, peak RSS, peak GPU memory, model/download disk
size, parser output bytes, LLM input/output tokens, call count, retry count, and
estimated cost. Report p50/p95 over three warm runs and one cold run. No source
text belongs in general logs; benchmark artifacts live in an explicitly safe
fixture directory.

### 7.5 Preregistered success criteria

Before any candidate adoption:

- no regression in security, write policy, or production-RAG exclusion;
- native PDF and static web text coverage >= 0.95;
- scanned/mixed PDF and screenshot Chinese CER improves at least 20% relative
  to Tesseract/pypdf baseline, or reaches <= 0.08;
- structure F1 improves at least 0.15 absolute on applicable samples;
- reading-order accuracy >= 0.95;
- duplicate/noise rate <= 0.05 each;
- locator coverage >= 0.95 for supported content;
- critical evidence recall = 1.00 and weighted key-point recall >= 0.90;
- unsupported-claim rate <= 0.01;
- final-note category completeness >= 0.85;
- no sample may lose more than 0.05 completeness versus current baseline;
- p95 latency, peak RSS, disk size, and per-source cost must be reported, not
  silently traded for quality.

With only 13 samples these are engineering gates, not statistically general
claims. Any parser adoption requires expansion around the observed failure
mode.

## 8. Prompt and generation-flow alternatives

### Candidate A: coverage-guided single pass for short sources

Use only when the complete normalized source plus prompt fits a conservative
input budget and has <=8 sections. Ask for source-derived evidence categories,
allow a dynamic number of notes, require a locator per important claim, and set
output budget from source evidence count within a hard cost ceiling.

Advantages: lowest implementation and latency cost. Limit: long-context
position effects and fixed output representations still make it unsafe for
large sources.

### Candidate B: section-aware bounded evidence map + synthesis

1. Deterministically segment by parser structure, page, timestamp, speaker, or
   image boundary.
2. Process every section exactly once under bounded input budgets.
3. Extract atomic evidence records: category, statement, importance, locator,
   and uncertainty. Do not write prose notes yet.
4. Deterministically deduplicate evidence while retaining all locators.
5. Synthesize readable notes from the complete evidence set.
6. Compare covered evidence IDs with the full map; generate only missing
   sections if a gap remains.

This is the recommended default. It uses bounded all-section processing rather
than QA relevance `top_k`. It is consistent with the multi-stage rationale in
[SummN](https://aclanthology.org/2022.acl-long.112/) while keeping LearnLoop's
grounding and state rules deterministic.

### Candidate C: hierarchical generation + independent completeness verifier

For exceptionally long sources, group section evidence into chapters, produce
chapter notes, merge them hierarchically, then run a verifier against the
evidence manifest. The verifier may identify missing evidence IDs but cannot
invent prose or approve unsupported claims. Regeneration is scoped only to
missing chapters/categories.

Advantages: scales beyond one context window and preserves chapter balance.
Costs: more calls, merge errors, higher latency, more resumable workflow state,
and a larger rollback/migration surface. Use only when Candidate B exceeds its
evidence-synthesis budget.

### Shared prompt contract

All candidates must:

- treat source text as untrusted data;
- never add facts not present in evidence;
- preserve cases, conditions, data, limitations, exceptions, counterpoints,
  conclusions, and unresolved questions when present;
- attach at least one source locator to every critical/major claim;
- label unclear source evidence as unclear;
- derive output length from evidence count, not a fixed item count;
- avoid duplicate evidence and empty generic commentary;
- apply source-specific instructions for PDF layout, web DOM, transcript time,
  chat speaker/thread, and screenshot image/region/overlap.

### Paired comparison

Run current v7, Candidate A, and Candidate B on the same frozen parser outputs.
Add Candidate C only for samples that exceed B's synthesis budget. Select by
the preregistered gates in section 7.5, not by subjective reading or note
length. Record evidence recall before prose generation and final completeness
after rendering.

## 9. Recommended minimal improvement

This is a future implementation proposal, not a change made in this discovery:

1. Introduce a normalized source manifest with stable section IDs and locators,
   initially populated using current parsers.
2. Restrict improved single-pass generation to short sources.
3. Replace the 6-10 preference and 12-note hard ceiling with a dynamic evidence
   budget bounded by total characters/tokens/cost.
4. Add explicit coverage categories and `evidence_ids` to structured output.
5. Reject `finish_reason="length"` and any missing critical evidence as
   incomplete, not successful.
6. Render locator-bearing headings/lists in Notion without changing append-only
   review safety.

This can improve generation completeness without immediately adopting a new
parser. It will not solve scanned PDFs, JS pages, non-English YouTube, OCR
quality, or lost layout.

## 10. Recommended stronger redesign

Adopt Candidate B with a common model such as:

```text
NormalizedDocument
  source_id
  source_type
  language(s)
  elements[]:
    element_id, type, text, order, hierarchy
    locator(page/timestamp/image/message/dom)
    geometry/table/code metadata when available

EvidenceRecord
  evidence_id, element_ids, category, importance
  grounded statement, locators[], uncertainty
```

Parser adapters create the normalized document. A section planner guarantees
bounded all-section coverage. Evidence extraction and deterministic validation
precede synthesis. A completeness service compares evidence IDs, then the
existing Change Request and human acceptance flow persists the final proposal.
Queue access remains behind `QueueClient`, LLM calls remain behind the provider
router, and parser/ASR/OCR remain tools. No LangChain/LangGraph or LLM-owned
permission/state/citation decision is required.

Selected parser improvements are gated by benchmark results:

- PDF: compare current pypdf against Docling, MinerU, Unstructured, and a light
  PyMuPDF4LLM control; do not adopt AGPL/custom-weight candidates without legal
  approval.
- OCR: compare Tesseract against PaddleOCR and RapidOCR first.
- Web: retain Trafilatura for static pages; add a bounded Playwright-rendered
  DOM fallback only for detected JS insufficiency.
- YouTube: retain caption API, preserve language/type/timestamps; benchmark
  yt-dlp acquisition plus local faster-whisper only for missing captions.

## 11. Risks, migration cost, and rollback

| Risk | Mitigation |
| --- | --- |
| Larger models increase image size, cold start, RAM/VRAM | isolate adapters; benchmark CPU profile; lazy load; declare readiness and resource budgets |
| New licenses conflict with product distribution | legal gate before dependency selection; retain pypdf/Tesseract/Trafilatura fallbacks |
| More LLM calls increase cost/latency | section budgets, resumable evidence cache, deterministic completeness gate, hard workflow cost cap |
| New output schema breaks pending proposals | version normalized/evidence/proposal schemas; read old proposal JSON unchanged |
| Parser changes alter content hashes/duplicates | version parser provenance; do not reinterpret old sources silently; explicit re-ingest/migration |
| More structure could weaken append safety | keep target, identity, citations, acceptance, and writes backend-owned |
| Fallback produces deceptively partial success | persist `complete/partial/unsupported` extraction status and missing section/image/page counts |

Rollback should be feature-versioned per source type and per generation flow.
Keep current adapters and `supplement_proposal_v7` callable for newly submitted
sources during rollout, never rewrite old Change Requests or old AI supplement
blocks, and roll back by routing new jobs to the previous version. Evidence and
normalized documents are additive durable records; accepted Notion content is
never automatically removed.

## 12. Proposed implementation steps

1. Freeze the 13 benchmark artifacts, gold annotations, hashes, and scoring
   script contract.
2. Capture the true current baseline with current pinned dependencies and no
   live LLM where a deterministic replay is possible; separately approve a
   bounded provider capture for generation variants.
3. Add versioned normalized-document and locator schemas behind source tools.
4. Instrument safe counts only: pages/images/segments/elements/chunks, estimated
   and provider tokens, evidence/notes/blocks, partial status, latency, memory,
   and cost. Never log raw source text.
5. Implement Candidate A and B behind flow-version selection, with current
   behavior unchanged by default.
6. Run paired benchmark and choose generation flow by preregistered gates.
7. Run parser/OCR/browser/ASR candidates out of process against the same assets;
   select only measured winners with acceptable license/resources.
8. Add structure-aware Notion rendering while preserving the existing append,
   identity verification, and re-index contract.
9. Roll out by source type with shadow evidence generation, human review, and a
   version switch for rollback.

## 13. Matters still unconfirmed

- No real production source/proposal pair was available, so the frequency and
  magnitude of short notes in actual use are not quantified.
- Existing fixtures do not include real PDF, HTML, screenshot pixels, or saved
  YouTube responses. Current extraction coverage, OCR CER/WER, memory, and
  latency cannot be claimed.
- No live provider call was authorized. Model context behavior, true token
  count, `finish_reason` distribution, and actual output-length distribution
  remain unknown.
- It is unknown whether past short proposals came from the early/late duplicate
  branch, a main call, or screenshot repair without workflow IDs and redacted
  metadata.
- The system Tesseract installation has all required languages today, but
  deployment image parity has not been inspected.
- Trafilatura default extraction quality on the user's target sites and
  anti-bot/consent behavior are unknown.
- Caption availability, geographic restrictions, rate limiting, and YouTube
  library reliability need guarded live fixtures.
- Candidate model weight licenses and transitive dependencies require formal
  legal review; this report is not legal advice.
- Proposed metric thresholds need calibration after the first blinded human
  annotation pass.

## 14. Final decision

**Choose the combined approach: redesign long-source generation first, then
improve selected parsers based on the frozen benchmark.**

Keeping current parsers and only changing the prompt cannot recover scanned PDF
text, dynamic DOM content, non-English/missing captions, table geometry, or
locators. Replacing parsers alone cannot overcome the one-call 1,400-token,
12-note ceiling. A long-source redesign without parser improvements would still
synthesize from flattened or missing evidence. The code evidence and the
red-capable schema probe therefore rule out all three single-axis decisions.

The minimum adoption target is Candidate B plus the existing parsers. Parser
replacement follows only where the paired parser benchmark demonstrates a
material gain and acceptable license, local-first privacy, latency, memory,
dependency size, and Docker/RQ integration cost.
