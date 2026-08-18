"""Build the canonical-serialization reference document for W02."""

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
FIXTURE = ROOT / "fixtures" / "W02" / "revision-001"
GOVERNANCE = ROOT / "governance" / "W02" / "revision-001"
REFERENCE = ROOT / "reference_documents" / "W02" / "revision-001"
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
    code_metadata: dict[str, Any] | None = None,
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
            "code_metadata": code_metadata,
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
        element_id="w02-title",
        kind="heading",
        section_id="w02-root",
        dom_path="/html/body/main/article/h1",
        content="可追蹤的資料流程 / Traceable Data Workflows",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-lede",
        kind="paragraph",
        section_id="w02-root",
        dom_path="/html/body/main/article/p[1]",
        content="這篇專案自有文章說明如何讓資料處理保持可追蹤。 This project-owned article explains how to keep data processing traceable.",
    )

    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-overview-heading",
        kind="heading",
        section_id="w02-overview",
        dom_path="/html/body/main/article/section[1]/h2",
        content="摘要 / Overview",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-overview-paragraph",
        kind="paragraph",
        section_id="w02-overview",
        dom_path="/html/body/main/article/section[1]/p",
        content="清楚的邊界讓讀者能在中英文內容之間建立同一條脈絡。 Clear boundaries preserve one context across Chinese and English content.",
    )
    overview_items = (
        "保留 heading 與段落階層 / Preserve heading and paragraph hierarchy.",
        "把清單項目視為可定位的內容 / Treat list items as locatable content.",
        "讓 boilerplate 與文章主體保持可區分 / Keep boilerplate distinct from the article body.",
    )
    for index, content in enumerate(overview_items, start=1):
        _element(
            elements=elements,
            snapshot_digest=source_digest,
            element_id=f"w02-overview-unordered-{index}",
            kind="list_item",
            section_id="w02-overview",
            dom_path=f"/html/body/main/article/section[1]/ul/li[{index}]",
            content=content,
            list_metadata={"list_kind": "unordered", "nesting_level": 0, "ordinal": None},
        )
    for index, content in enumerate(
        (
            "先固定 source snapshot / Freeze the source snapshot first.",
            "再建立 reference / Then author the reference.",
        ),
        start=1,
    ):
        _element(
            elements=elements,
            snapshot_digest=source_digest,
            element_id=f"w02-overview-ordered-{index}",
            kind="list_item",
            section_id="w02-overview",
            dom_path=f"/html/body/main/article/section[1]/ol/li[{index}]",
            content=content,
            list_metadata={"list_kind": "ordered", "nesting_level": 0, "ordinal": index - 1},
        )

    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-table-heading",
        kind="heading",
        section_id="w02-table",
        dom_path="/html/body/main/article/section[2]/h2",
        content="事件表 / Event Table",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-table-caption",
        kind="caption",
        section_id="w02-table",
        dom_path="/html/body/main/article/section[2]/table/caption",
        content="表一：處理事件欄位 / Table 1: Processing event fields",
    )
    table_id = "w02-event-table"
    table_path = "/html/body/main/article/section[2]/table"
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id=table_id,
        kind="table",
        section_id="w02-table",
        dom_path=table_path,
    )
    rows = (
        ("欄位 Field", "值 Value", "說明 Note"),
        ("Parse / 解析", "18 ms", "讀取結構 / Read structure"),
        ("Review / 審核", "42 ms", "保留脈絡 / Keep context"),
        ("Publish / 發布", "75 ms", "等待決策 / Await decision"),
    )
    for row_index, row in enumerate(rows):
        row_id = f"{table_id}-row-{row_index}"
        row_path = f"{table_path}/tbody/tr[{row_index}]" if row_index else f"{table_path}/thead/tr"
        _element(
            elements=elements,
            snapshot_digest=source_digest,
            element_id=row_id,
            kind="table_row",
            section_id="w02-table",
            dom_path=row_path,
            parent_element_id=table_id,
        )
        for column_index, content in enumerate(row):
            cell_tag = "th" if row_index == 0 else "td"
            cell_path = f"{row_path}/{cell_tag}[{column_index + 1}]"
            _element(
                elements=elements,
                snapshot_digest=source_digest,
                element_id=f"{row_id}-cell-{column_index}",
                kind="table_cell",
                section_id="w02-table",
                dom_path=cell_path,
                content=content,
                parent_element_id=row_id,
                table_cell_metadata=_cell_metadata(row_index, column_index),
            )

    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-code-heading",
        kind="heading",
        section_id="w02-code",
        dom_path="/html/body/main/article/section[3]/h2",
        content="程式片段 / Code Example",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-code",
        kind="code_block",
        section_id="w02-code",
        dom_path="/html/body/main/article/section[3]/pre/code",
        content="def normalize(value):\n    # Keep source text stable before reference authoring.\n    return value.strip()\n",
        languages=("en",),
        code_metadata={"language_hint": "python", "source_supplied": True},
    )

    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-figure-heading",
        kind="heading",
        section_id="w02-figure",
        dom_path="/html/body/main/article/section[4]/h2",
        content="流程圖 / Workflow Figure",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-figure",
        kind="figure",
        section_id="w02-figure",
        dom_path="/html/body/main/article/section[4]/figure",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-figure-caption",
        kind="caption",
        section_id="w02-figure",
        dom_path="/html/body/main/article/section[4]/figure/figcaption",
        content="圖一：固定流程 / Figure 1: A fixed processing flow.",
        parent_element_id="w02-figure",
    )

    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-header-brand",
        kind="ui_text",
        section_id="w02-root",
        dom_path="/html/body/header/div",
        content="LearnLoop / 學習循環",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-navigation",
        kind="ui_text",
        section_id="w02-root",
        dom_path="/html/body/header/nav",
        content="文章 Articles 方法 Methods 附錄 Appendix",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-aside",
        kind="ui_text",
        section_id="w02-root",
        dom_path="/html/body/main/aside",
        content="備註 Note：這是 development validation 草稿，不代表正式採用。",
    )
    _element(
        elements=elements,
        snapshot_digest=source_digest,
        element_id="w02-footer",
        kind="ui_text",
        section_id="w02-root",
        dom_path="/html/body/footer",
        content="頁尾資訊 / Footer information · project-owned synthetic content",
    )

    sections = [
        {
            "section_id": "w02-root",
            "parent_section_id": None,
            "heading_element_id": "w02-title",
            "start_order": 0,
            "end_order": len(elements) - 1,
        },
        {
            "section_id": "w02-overview",
            "parent_section_id": "w02-root",
            "heading_element_id": "w02-overview-heading",
            "start_order": 2,
            "end_order": 8,
        },
        {
            "section_id": "w02-table",
            "parent_section_id": "w02-root",
            "heading_element_id": "w02-table-heading",
            "start_order": 9,
            "end_order": 27,
        },
        {
            "section_id": "w02-code",
            "parent_section_id": "w02-root",
            "heading_element_id": "w02-code-heading",
            "start_order": 28,
            "end_order": 29,
        },
        {
            "section_id": "w02-figure",
            "parent_section_id": "w02-root",
            "heading_element_id": "w02-figure-heading",
            "start_order": 30,
            "end_order": 32,
        },
    ]

    return NormalizedDocument.model_validate(
        {
            "schema_version": "normalized-document/1.0.0",
            "artifact_role": "reference_document",
            "document_id": "W02",
            "source": {
                "source_type": "web",
                "source_identity": "w02-complex-static-html-revision-001",
                "display_name": "可追蹤的資料流程 / Traceable Data Workflows",
                "source_snapshot_sha256": source_digest,
                "languages": list(LANGUAGES),
            },
            "capabilities": {
                "hierarchy": {"status": "available", "reason": None},
                "language_identification": {"status": "available", "reason": None},
                "geometry": {"status": "unavailable", "reason": "not_captured"},
                "table_structure": {"status": "available", "reason": None},
                "code_metadata": {"status": "available", "reason": None},
                "source_modality": {"status": "available", "reason": None},
                "typed_locators": {"status": "available", "reason": None},
            },
            "sections": sections,
            "elements": elements,
            "producer_provenance": {
                "producer_name": "learnloop-project-authored-reference",
                "producer_version": "1.0.0",
                "configuration_sha256": configuration_digest,
                "segmentation_semantics": "html-static-structure-v1",
                "processing_method": "project_authored_static_html",
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
