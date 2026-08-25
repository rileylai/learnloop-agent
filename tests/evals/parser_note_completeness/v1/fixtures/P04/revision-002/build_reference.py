"""Build the canonical-serialization reference document for P04."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(PROJECT_ROOT))

from tests.evals.parser_note_completeness.normalized_document import NormalizedDocument, canonical_normalized_document_bytes


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "fixtures" / "P04" / "revision-002"
GOVERNANCE = ROOT / "governance" / "P04" / "revision-002"
REFERENCE = ROOT / "reference_documents" / "P04" / "revision-002"
LANGUAGES = ("zh-Hant", "en")


def _geometry(x: int, y: int, width: int, height: int) -> dict[str, Any]:
    return {"coordinate_space": "normalized_top_left_0_1000000", "x": x, "y": y, "width": width, "height": height}


def _locator(page: int, geometry: dict[str, Any] | None = None) -> dict[str, Any]:
    locator: dict[str, Any] = {"locator_type": "pdf", "status": "available", "page": page, "geometry": geometry}
    return locator


def _element(
    *,
    element_id: str,
    kind: str,
    order: int,
    section_id: str,
    page: int,
    content: str | None = None,
    languages: tuple[str, ...] = LANGUAGES,
    geometry: dict[str, Any] | None = None,
    parent_element_id: str | None = None,
    table_cell_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "element_id": element_id,
        "kind": kind,
        "order": order,
        "section_id": section_id,
        "parent_element_id": parent_element_id,
        "content": content,
        "languages": list(languages),
        "locators": [_locator(page, geometry)],
        "list_metadata": None,
        "table_cell_metadata": table_cell_metadata,
        "code_metadata": None,
    }


def _add_table(elements: list[dict[str, Any]], page: int) -> None:
    section_id = f"p04-page-{page}"
    table_id = "p04-table-1"
    elements.append(_element(element_id=table_id, kind="table", order=len(elements), section_id=section_id, page=page))
    rows = (("Measure", "Value", "Unit"), ("Force", "12", "N"), ("Mass", "3", "kg"))
    for row_index, row in enumerate(rows):
        row_id = f"{table_id}-row-{row_index}"
        elements.append(_element(element_id=row_id, kind="table_row", order=len(elements), section_id=section_id, page=page, parent_element_id=table_id))
        for column_index, content in enumerate(row):
            elements.append(
                _element(
                    element_id=f"{row_id}-cell-{column_index}",
                    kind="table_cell",
                    order=len(elements),
                    section_id=section_id,
                    page=page,
                    content=content,
                    parent_element_id=row_id,
                    table_cell_metadata={
                        "row_index": row_index,
                        "column_index": column_index,
                        "row_span": None,
                        "column_span": None,
                        "header_role": "row" if row_index == 0 else None,
                    },
                )
            )


def _add_page(elements: list[dict[str, Any]], sections: list[dict[str, Any]], page: int, title: str, paragraphs: tuple[str, ...], *, scanned: bool, languages: tuple[str, ...] = LANGUAGES) -> None:
    section_id = f"p04-page-{page}"
    start = len(elements)
    geometry = _geometry(85000, 80000, 700000, 65000) if scanned else None
    elements.append(_element(element_id=f"{section_id}-heading", kind="heading", order=len(elements), section_id=section_id, page=page, content=title, languages=languages, geometry=geometry))
    for index, paragraph in enumerate(paragraphs, start=1):
        paragraph_geometry = _geometry(85000, 220000 + index * 95000, 800000, 65000) if scanned else None
        elements.append(_element(element_id=f"{section_id}-paragraph-{index}", kind="paragraph", order=len(elements), section_id=section_id, page=page, content=paragraph, languages=languages, geometry=paragraph_geometry))
    sections.append({"section_id": section_id, "parent_section_id": None, "heading_element_id": f"{section_id}-heading", "start_order": start, "end_order": len(elements) - 1})


def build_document() -> NormalizedDocument:
    source_digest = hashlib.sha256((FIXTURE / "source.pdf").read_bytes()).hexdigest()
    configuration_digest = hashlib.sha256((GOVERNANCE / "producer_configuration.json").read_bytes()).hexdigest()
    elements: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []
    _add_page(elements, sections, 1, "公式與表格 / Formula and Table", ("Native text records the English measurement note and its Chinese label.",), scanned=False)
    elements.append(_element(element_id="p04-page-1-formula", kind="formula", order=len(elements), section_id="p04-page-1", page=1, content="F = m * a", languages=("en",)))
    _add_table(elements, 1)
    sections[0]["end_order"] = len(elements) - 1
    _add_page(elements, sections, 2, "第二頁：掃描觀測", ("這一頁以固定 recipe 產生掃描影像與輕微傾斜。", "區域文字保留原始檢閱位置。"), scanned=True, languages=("zh-Hant",))
    _add_page(elements, sections, 3, "雙語處理 / Bilingual Processing", ("Native paragraphs remain selectable while scanned pages retain image regions.", "中文與 English 可以在同一份 mixed PDF 中並存。", "The source modality changes at the page boundary, not in the profile contract."), scanned=False)
    _add_page(elements, sections, 4, "第四頁：檢閱 Review", ("這一頁是 scanned page，包含中文說明與 English review label。", "影像區域可由 normalized geometry 回到來源。"), scanned=True)
    return NormalizedDocument.model_validate(
        {
            "schema_version": "normalized-document/1.0.0",
            "artifact_role": "reference_document",
            "document_id": "P04",
            "source": {
                "source_type": "pdf",
                "source_identity": "p04-mixed-bilingual-revision-002",
                "display_name": "混合原生與掃描雙語報告 / Mixed Bilingual Report",
                "source_snapshot_sha256": source_digest,
                "languages": list(LANGUAGES),
            },
            "capabilities": {
                "hierarchy": {"status": "partial", "reason": "page_sections_only"},
                "language_identification": {"status": "available", "reason": None},
                "geometry": {"status": "partial", "reason": "native_text_geometry_not_captured"},
                "table_structure": {"status": "available", "reason": None},
                "code_metadata": {"status": "not_applicable", "reason": None},
                "source_modality": {"status": "available", "reason": None},
                "typed_locators": {"status": "available", "reason": None},
            },
            "sections": sections,
            "elements": elements,
            "producer_provenance": {
                "producer_name": "learnloop-project-authored-reference",
                "producer_version": "1.0.0",
                "configuration_sha256": configuration_digest,
                "segmentation_semantics": "pdf-mixed-native-raster-v1",
                "processing_method": "project_authored_mixed_native_and_raster_pdf",
                "processing_stage": "fixture_build_and_reference_authoring",
                "parser_model": None,
                "ocr_model": None,
                "asr_model": None,
            },
        }
    )


def main() -> None:
    data = canonical_normalized_document_bytes(build_document())
    REFERENCE.mkdir(parents=True, exist_ok=True)
    (REFERENCE / "normalized_document.json").write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    (REFERENCE / "normalized_document.sha256").write_text(f"{digest}  normalized_document.json\n", encoding="ascii")


if __name__ == "__main__":
    main()
