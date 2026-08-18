"""Build the canonical-serialization reference document for W03."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(PROJECT_ROOT))

from tests.evals.parser_note_completeness.normalized_document import (  # noqa: E402
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "fixtures" / "W03" / "revision-001"
GOVERNANCE = ROOT / "governance" / "W03" / "revision-001"
REFERENCE = ROOT / "reference_documents" / "W03" / "revision-001"
LANGUAGES = ("zh-Hant", "en")


def _locator(snapshot_digest: str, dom_path: str) -> dict[str, Any]:
    return {
        "locator_type": "web",
        "status": "available",
        "reason": None,
        "snapshot_sha256": snapshot_digest,
        "dom_path": dom_path,
        "text_span": None,
    }


def _element(
    *,
    elements: list[dict[str, Any]],
    snapshot_digest: str,
    element_id: str,
    kind: str,
    section_id: str,
    dom_path: str,
    content: str | None = None,
    languages: tuple[str, ...] = LANGUAGES,
    parent_element_id: str | None = None,
    list_metadata: dict[str, Any] | None = None,
    table_cell_metadata: dict[str, Any] | None = None,
) -> None:
    elements.append(
        {
            "element_id": element_id,
            "kind": kind,
            "order": len(elements),
            "section_id": section_id,
            "parent_element_id": parent_element_id,
            "content": content,
            "languages": list(languages),
            "locators": [_locator(snapshot_digest, dom_path)],
            "list_metadata": list_metadata,
            "table_cell_metadata": table_cell_metadata,
            "code_metadata": None,
        }
    )


def _cell_metadata(row_index: int, column_index: int) -> dict[str, Any]:
    return {
        "row_index": row_index,
        "column_index": column_index,
        "row_span": None,
        "column_span": None,
        "header_role": "column" if row_index == 0 else None,
    }


def build_document() -> NormalizedDocument:
    source_digest = hashlib.sha256((FIXTURE / "source.html").read_bytes()).hexdigest()
    configuration_digest = hashlib.sha256(
        (GOVERNANCE / "producer_configuration.json").read_bytes()
    ).hexdigest()
    elements: list[dict[str, Any]] = []

    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-title",
        kind="heading",
        section_id="w03-root",
        dom_path="/html/body/div/main/article/header/h1",
        content="離線文章快照 / Offline Article Snapshot",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-intro",
        kind="paragraph",
        section_id="w03-root",
        dom_path="/html/body/div/main/article/header/p",
        content="這份 DOM snapshot 模擬已完成渲染的文章，不需要瀏覽器或網路。 This DOM snapshot models a rendered article without a browser or network.",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-overview-heading",
        kind="heading",
        section_id="w03-overview",
        dom_path="/html/body/div/main/article/section[1]/h2",
        content="導讀 / Overview",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-overview-paragraph",
        kind="paragraph",
        section_id="w03-overview",
        dom_path="/html/body/div/main/article/section[1]/p",
        content="巢狀區段保留文章脈絡。 Nested sections preserve the article context.",
    )
    for index, content in enumerate(
        (
            "讀取固定的 rendered DOM / Read the fixed rendered DOM.",
            "保留中英文段落 / Preserve Chinese and English paragraphs.",
        ),
        start=1,
    ):
        _element(
            elements=elements,
            snapshot_digest=source_digest,
            element_id=f"w03-overview-item-{index}",
            kind="list_item",
            section_id="w03-overview",
            dom_path=f"/html/body/div/main/article/section[1]/ul/li[{index}]",
            content=content,
            list_metadata={"list_kind": "unordered", "nesting_level": 0, "ordinal": None},
        )

    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-details-heading",
        kind="heading",
        section_id="w03-details",
        dom_path="/html/body/div/main/article/section[2]/h2",
        content="細節 / Details",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-details-paragraph",
        kind="paragraph",
        section_id="w03-details",
        dom_path="/html/body/div/main/article/section[2]/p",
        content="下面的子區段以相同 snapshot identity 綁定表格與圖形。 Child sections bind the table and figure to one snapshot identity.",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-table-heading",
        kind="heading",
        section_id="w03-table",
        dom_path="/html/body/div/main/article/section[2]/section[1]/h3",
        content="資料表 / Data Table",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-table-caption",
        kind="caption",
        section_id="w03-table",
        dom_path="/html/body/div/main/article/section[2]/section[1]/table/caption",
        content="表二：快照狀態 / Table 2: Snapshot states",
    )
    table_id = "w03-snapshot-table"
    table_path = "/html/body/div/main/article/section[2]/section[1]/table"
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id=table_id,
        kind="table",
        section_id="w03-table",
        dom_path=table_path,
    )
    rows = (
        ("狀態 State", "保留 Retained", "備註 Note"),
        ("Rendered / 已渲染", "yes / 是", "固定 DOM / Fixed DOM"),
        ("Network / 網路", "no / 否", "離線建置 / Offline build"),
    )
    for row_index, row in enumerate(rows):
        row_id = f"{table_id}-row-{row_index}"
        row_path = f"{table_path}/tbody/tr[{row_index}]" if row_index else f"{table_path}/thead/tr"
        _element(
            elements=elements,
            snapshot_digest=source_digest,
            element_id=row_id,
            kind="table_row",
            section_id="w03-table",
            dom_path=row_path,
            parent_element_id=table_id,
        )
        for column_index, content in enumerate(row):
            cell_tag = "th" if row_index == 0 else "td"
            _element(
                elements=elements,
                snapshot_digest=source_digest,
                element_id=f"{row_id}-cell-{column_index}",
                kind="table_cell",
                section_id="w03-table",
                dom_path=f"{row_path}/{cell_tag}[{column_index + 1}]",
                content=content,
                parent_element_id=row_id,
                table_cell_metadata=_cell_metadata(row_index, column_index),
            )

    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-figure-heading",
        kind="heading",
        section_id="w03-figure",
        dom_path="/html/body/div/main/article/section[2]/section[2]/h3",
        content="關聯圖 / Relationship Figure",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-figure",
        kind="figure",
        section_id="w03-figure",
        dom_path="/html/body/div/main/article/section[2]/section[2]/figure",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-figure-caption",
        kind="caption",
        section_id="w03-figure",
        dom_path="/html/body/div/main/article/section[2]/section[2]/figure/figcaption",
        content="圖二：DOM 到 reference / Figure 2: DOM to reference.",
        parent_element_id="w03-figure",
    )

    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-conclusion-heading",
        kind="heading",
        section_id="w03-conclusion",
        dom_path="/html/body/div/main/article/section[3]/h2",
        content="結語 / Conclusion",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w03-conclusion-paragraph",
        kind="paragraph",
        section_id="w03-conclusion",
        dom_path="/html/body/div/main/article/section[3]/p",
        content="所有內容都來自固定 bytes。 Every element comes from fixed bytes.",
    )

    sections = [
        {
            "section_id": "w03-root",
            "parent_section_id": None,
            "heading_element_id": "w03-title",
            "start_order": 0,
            "end_order": len(elements) - 1,
        },
        {
            "section_id": "w03-overview",
            "parent_section_id": "w03-root",
            "heading_element_id": "w03-overview-heading",
            "start_order": 2,
            "end_order": 5,
        },
        {
            "section_id": "w03-details",
            "parent_section_id": "w03-root",
            "heading_element_id": "w03-details-heading",
            "start_order": 6,
            "end_order": 25,
        },
        {
            "section_id": "w03-table",
            "parent_section_id": "w03-details",
            "heading_element_id": "w03-table-heading",
            "start_order": 8,
            "end_order": 22,
        },
        {
            "section_id": "w03-figure",
            "parent_section_id": "w03-details",
            "heading_element_id": "w03-figure-heading",
            "start_order": 23,
            "end_order": 25,
        },
        {
            "section_id": "w03-conclusion",
            "parent_section_id": "w03-root",
            "heading_element_id": "w03-conclusion-heading",
            "start_order": 26,
            "end_order": 27,
        },
    ]

    return NormalizedDocument.model_validate(
        {
            "schema_version": "normalized-document/1.0.0",
            "artifact_role": "reference_document",
            "document_id": "W03",
            "source": {
                "source_type": "web",
                "source_identity": "w03-offline-rendered-dom-revision-001",
                "display_name": "離線文章快照 / Offline Article Snapshot",
                "source_snapshot_sha256": source_digest,
                "languages": list(LANGUAGES),
            },
            "capabilities": {
                "hierarchy": {"status": "available", "reason": None},
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
                "segmentation_semantics": "html-rendered-dom-sections-v1",
                "processing_method": "project_authored_rendered_dom_snapshot",
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
    (REFERENCE / "normalized_document.sha256").write_text(
        f"{digest}  normalized_document.json\n", encoding="ascii"
    )


if __name__ == "__main__":
    main()
