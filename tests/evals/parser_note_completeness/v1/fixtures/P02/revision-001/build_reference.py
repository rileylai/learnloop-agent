"""Build the canonical-serialization reference document for P02."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(PROJECT_ROOT))

from tests.evals.parser_note_completeness.normalized_document import NormalizedDocument, canonical_normalized_document_bytes


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "fixtures" / "P02" / "revision-001"
GOVERNANCE = ROOT / "governance" / "P02" / "revision-001"
REFERENCE = ROOT / "reference_documents" / "P02" / "revision-001"
LANGUAGES = ("zh-Hant", "en")


def _locator(page: int) -> dict[str, Any]:
    return {"locator_type": "pdf", "status": "available", "page": page}


def _element(
    *,
    element_id: str,
    kind: str,
    order: int,
    section_id: str,
    page: int,
    content: str | None = None,
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
        "languages": list(LANGUAGES),
        "locators": [_locator(page)],
        "list_metadata": None,
        "table_cell_metadata": table_cell_metadata,
        "code_metadata": None,
    }


def _add_page(elements: list[dict[str, Any]], page: int, title: str, paragraphs: Iterable[str]) -> tuple[str, int, int]:
    section_id = f"p02-page-{page}"
    start = len(elements)
    heading_id = f"{section_id}-heading"
    elements.append(_element(element_id=heading_id, kind="heading", order=len(elements), section_id=section_id, page=page, content=title))
    for index, paragraph in enumerate(paragraphs, start=1):
        elements.append(_element(element_id=f"{section_id}-paragraph-{index}", kind="paragraph", order=len(elements), section_id=section_id, page=page, content=paragraph))
    return section_id, start, len(elements) - 1


def _add_table(elements: list[dict[str, Any]], page: int, table_number: int, rows: tuple[tuple[str, ...], ...]) -> None:
    section_id = f"p02-page-{page}"
    table_id = f"p02-table-{table_number}"
    elements.append(_element(element_id=table_id, kind="table", order=len(elements), section_id=section_id, page=page))
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


def _add_figure(elements: list[dict[str, Any]], page: int, number: int) -> None:
    section_id = f"p02-page-{page}"
    figure_id = f"p02-figure-{number}"
    elements.append(_element(element_id=figure_id, kind="figure", order=len(elements), section_id=section_id, page=page))
    elements.append(
        _element(
            element_id=f"{figure_id}-caption",
            kind="caption",
            order=len(elements),
            section_id=section_id,
            page=page,
            content=f"圖{number} / Figure {number}: vector processing view",
        )
    )


def build_document() -> NormalizedDocument:
    source_digest = hashlib.sha256((FIXTURE / "source.pdf").read_bytes()).hexdigest()
    configuration_digest = hashlib.sha256((GOVERNANCE / "producer_configuration.json").read_bytes()).hexdigest()
    elements: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []
    pages = (
        (1, "雙語資料系統報告 / Bilingual Data Systems Report", ("本報告以專案自有內容說明可追蹤的資料處理流程。", "This project-owned report describes an observable data workflow.")),
        (2, "表一 / Table One: 事件延遲 / Event Latency", ("第一張表格比較不同處理階段的延遲。", "The first table compares latency across processing stages.")),
        (3, "表二 / Table Two: 來源覆蓋 / Source Coverage", ("第二張表格保留中英文欄位名稱與數值。", "The second table preserves bilingual labels and values.")),
        (4, "結論 / Conclusion", ("圖一與圖二以向量線條呈現，不依賴外部影像資產。", "Figure One and Figure Two use vector paths without external images.")),
    )
    for page, title, paragraphs in pages:
        section_id, start, end = _add_page(elements, page, title, paragraphs)
        if page == 2:
            _add_table(elements, page, 1, (("欄位 Field", "值 Value", "負責人 Owner"), ("Parse / 解析", "18", "Parser"), ("Index / 索引", "42", "Indexer"), ("Review / 審核", "75", "Operator")))
            _add_figure(elements, page, 1)
        elif page == 3:
            _add_table(elements, page, 2, (("Source / 來源", "Native / 原生", "Reviewed / 已審核"), ("PDF", "yes / 是", "pending / 待處理"), ("Web", "yes / 是", "pending / 待處理"), ("Scan", "image / 影像", "pending / 待處理")))
            _add_figure(elements, page, 2)
        sections.append({"section_id": section_id, "parent_section_id": None, "heading_element_id": f"{section_id}-heading", "start_order": start, "end_order": len(elements) - 1})
    return NormalizedDocument.model_validate(
        {
            "schema_version": "normalized-document/1.0.0",
            "artifact_role": "reference_document",
            "document_id": "P02",
            "source": {
                "source_type": "pdf",
                "source_identity": "p02-bilingual-report-revision-001",
                "display_name": "雙語資料系統報告 / Bilingual Data Systems Report",
                "source_snapshot_sha256": source_digest,
                "languages": list(LANGUAGES),
            },
            "capabilities": {
                "hierarchy": {"status": "partial", "reason": "page_sections_only"},
                "language_identification": {"status": "available", "reason": None},
                "geometry": {"status": "unavailable", "reason": "not_captured"},
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
                "segmentation_semantics": "pdf-bilingual-tables-figures-v1",
                "processing_method": "project_authored_native_pdf",
                "processing_stage": "fixture_build_and_reference_authoring",
                "parser_model": None,
                "ocr_model": None,
                "asr_model": None,
            },
        }
    )


def main() -> None:
    document = build_document()
    data = canonical_normalized_document_bytes(document)
    REFERENCE.mkdir(parents=True, exist_ok=True)
    (REFERENCE / "normalized_document.json").write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    (REFERENCE / "normalized_document.sha256").write_text(f"{digest}  normalized_document.json\n", encoding="ascii")


if __name__ == "__main__":
    main()
