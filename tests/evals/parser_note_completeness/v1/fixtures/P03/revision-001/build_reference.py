"""Build the canonical-serialization reference document for P03."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(PROJECT_ROOT))

from tests.evals.parser_note_completeness.normalized_document import NormalizedDocument, canonical_normalized_document_bytes


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "fixtures" / "P03" / "revision-001"
GOVERNANCE = ROOT / "governance" / "P03" / "revision-001"
REFERENCE = ROOT / "reference_documents" / "P03" / "revision-001"

PAGES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("第一頁：穩定資料流程", ("固定角度與微量雜訊保留掃描來源的真實形狀。", "本頁說明資料如何從來源進入處理流程。")),
    ("第二頁：分段與順序", ("每一頁都依照原始閱讀順序保存，段落不重新排列。", "分段記錄讓後續轉錄能回到影像區域。")),
    ("第三頁：錯誤與重試", ("失敗必須被記錄，重試不能掩蓋原始的處理結果。", "雜訊不代表內容遺失，而是掃描條件的一部分。")),
    ("第四頁：檢閱與來源", ("檢閱者可以使用頁碼與區域定位原始文字。", "這份專案草稿不包含外部連結或私人資料。")),
    ("第五頁：恢復與結論", ("恢復程序保留每一頁的來源影像與轉錄順序。", "固定配方讓每次建置得到相同的檔案位元組。")),
)


def _geometry(x: int, y: int, width: int, height: int) -> dict[str, Any]:
    return {"coordinate_space": "normalized_top_left_0_1000000", "x": x, "y": y, "width": width, "height": height}


def _element(element_id: str, kind: str, order: int, section_id: str, page: int, content: str, geometry: dict[str, Any]) -> dict[str, Any]:
    return {
        "element_id": element_id,
        "kind": kind,
        "order": order,
        "section_id": section_id,
        "parent_element_id": None,
        "content": content,
        "languages": ["zh-Hant"],
        "locators": [{"locator_type": "pdf", "status": "available", "page": page, "geometry": geometry}],
        "list_metadata": None,
        "table_cell_metadata": None,
        "code_metadata": None,
    }


def build_document() -> NormalizedDocument:
    source_digest = hashlib.sha256((FIXTURE / "source.pdf").read_bytes()).hexdigest()
    configuration_digest = hashlib.sha256((GOVERNANCE / "producer_configuration.json").read_bytes()).hexdigest()
    elements: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []
    for page, (title, paragraphs) in enumerate(PAGES, start=1):
        section_id = f"p03-page-{page}"
        start = len(elements)
        elements.append(_element(f"{section_id}-heading", "heading", len(elements), section_id, page, title, _geometry(85000, 80000, 650000, 65000)))
        for index, paragraph in enumerate(paragraphs, start=1):
            elements.append(_element(f"{section_id}-paragraph-{index}", "paragraph", len(elements), section_id, page, paragraph, _geometry(85000, 220000 + index * 90000, 780000, 60000)))
        sections.append({"section_id": section_id, "parent_section_id": None, "heading_element_id": f"{section_id}-heading", "start_order": start, "end_order": len(elements) - 1})
    return NormalizedDocument.model_validate(
        {
            "schema_version": "normalized-document/1.0.0",
            "artifact_role": "reference_document",
            "document_id": "P03",
            "source": {
                "source_type": "pdf",
                "source_identity": "p03-traditional-chinese-scan-revision-001",
                "display_name": "繁中掃描資料流程",
                "source_snapshot_sha256": source_digest,
                "languages": ["zh-Hant"],
            },
            "capabilities": {
                "hierarchy": {"status": "partial", "reason": "page_sections_only"},
                "language_identification": {"status": "available", "reason": None},
                "geometry": {"status": "available", "reason": None},
                "table_structure": {"status": "not_applicable", "reason": None},
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
                "segmentation_semantics": "pdf-scanned-page-regions-v1",
                "processing_method": "project_authored_deterministic_raster_scan",
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
