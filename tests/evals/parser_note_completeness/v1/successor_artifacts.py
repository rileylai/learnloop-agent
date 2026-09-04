"""Deterministic helpers for approved successor fixture/reference revisions."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

from tests.evals.parser_note_completeness.normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


V1_ROOT = Path(__file__).resolve().parent


def _load_builder(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"successor_{path.parent.parent.name}_{path.parent.name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load predecessor builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clone_predecessor_source(*, case_id: str, predecessor_revision: str, output: Path) -> bytes:
    module = _load_builder(V1_ROOT / "fixtures" / case_id / predecessor_revision / "build_source.py")
    function_name = "build_pdf" if output.suffix == ".pdf" else "build_html"
    data = getattr(module, function_name)()
    output.write_bytes(data)
    output.with_name("source.sha256").write_text(
        f"{hashlib.sha256(data).hexdigest()}  {output.name}\n",
        encoding="ascii",
    )
    return data


def _base_document(case_id: str, predecessor_revision: str, successor_revision: str) -> dict[str, Any]:
    module = _load_builder(V1_ROOT / "fixtures" / case_id / predecessor_revision / "build_reference.py")
    module.FIXTURE = V1_ROOT / "fixtures" / case_id / successor_revision
    module.GOVERNANCE = V1_ROOT / "governance" / case_id / successor_revision
    module.REFERENCE = V1_ROOT / "reference_documents" / case_id / successor_revision
    return module.build_document().model_dump(mode="json")


def _copy_text_element(template: dict[str, Any], *, element_id: str, content: str, kind: str = "paragraph") -> dict[str, Any]:
    value = dict(template)
    value.update({"element_id": element_id, "kind": kind, "content": content, "parent_element_id": None})
    return value


def _insert_after(elements: list[dict[str, Any]], element_id: str, additions: list[dict[str, Any]]) -> None:
    index = next(i for i, element in enumerate(elements) if element["element_id"] == element_id)
    elements[index + 1:index + 1] = additions


def _finish(payload: dict[str, Any], *, case_id: str, successor_revision: str) -> NormalizedDocument:
    elements = payload["elements"]
    for order, element in enumerate(elements):
        element["order"] = order
    parent_by_id = {section["section_id"]: section["parent_section_id"] for section in payload["sections"]}
    for section in payload["sections"]:
        included_ids = {section["section_id"]}
        changed = True
        while changed:
            changed = False
            for child_id, parent_id in parent_by_id.items():
                if parent_id in included_ids and child_id not in included_ids:
                    included_ids.add(child_id)
                    changed = True
        orders = [element["order"] for element in elements if element["section_id"] in included_ids]
        if orders:
            section["start_order"] = min(orders)
            section["end_order"] = max(orders)
    payload["source"]["source_identity"] = f"{payload['source']['source_identity'].rsplit('-revision-', 1)[0]}-{successor_revision}"
    payload["producer_provenance"]["segmentation_semantics"] += "-successor"
    payload["document_id"] = case_id
    return NormalizedDocument.model_validate(payload)


def build_successor_reference(case_id: str, predecessor_revision: str, successor_revision: str) -> NormalizedDocument:
    payload = _base_document(case_id, predecessor_revision, successor_revision)
    elements: list[dict[str, Any]] = payload["elements"]

    if case_id == "P02":
        p1 = next(element for element in elements if element["element_id"] == "p02-page-1-paragraph-2")
        _insert_after(
            elements,
            p1["element_id"],
            [
                _copy_text_element(p1, element_id="p02-page-1-paragraph-3", content="文字、表格與圖形都保留在同一份 native-text PDF 中。"),
                _copy_text_element(p1, element_id="p02-page-1-paragraph-4", content="Text, tables, and vector figures remain in one native-text PDF."),
            ],
        )
        p4 = next(element for element in elements if element["element_id"] == "p02-page-4-paragraph-2")
        _insert_after(
            elements,
            p4["element_id"],
            [
                _copy_text_element(p4, element_id="p02-page-4-paragraph-3", content="這份 draft 僅用於 development validation。"),
                _copy_text_element(p4, element_id="p02-page-4-paragraph-4", content="This draft is for development validation only."),
            ],
        )
        replacements = {
            "p02-table-1-row-0-cell-0": "Stage / 階段",
            "p02-table-1-row-0-cell-1": "Median ms / 中位毫秒",
            "p02-table-1-row-0-cell-2": "Owner / 負責人",
            "p02-figure-1-caption": "圖1 / Figure 1",
            "p02-figure-2-caption": "圖2 / Figure 2",
        }
        for element in elements:
            if element["element_id"] in replacements:
                element["content"] = replacements[element["element_id"]]

    elif case_id == "P03":
        for page in range(1, 6):
            heading = next(element for element in elements if element["element_id"] == f"p03-page-{page}-heading")
            scan_label = _copy_text_element(
                heading,
                element_id=f"p03-page-{page}-scan-label",
                content=f"掃描頁碼 {page}",
                kind="ui_text",
            )
            scan_label["locators"][0]["geometry"] = {
                "coordinate_space": "normalized_top_left_0_1000000", "x": 110000, "y": 145000, "width": 300000, "height": 55000
            }
            _insert_after(elements, heading["element_id"], [scan_label])
            template = next(element for element in elements if element["element_id"] == f"p03-page-{page}-paragraph-2")
            labels = []
            for suffix, content, x in (("region-a", "區域甲", 115000), ("region-b", "區域乙", 550000)):
                label = _copy_text_element(template, element_id=f"p03-page-{page}-{suffix}", content=content, kind="ui_text")
                label["locators"][0]["geometry"] = {
                    "coordinate_space": "normalized_top_left_0_1000000", "x": x, "y": 800000, "width": 300000, "height": 110000
                }
                labels.append(label)
            _insert_after(elements, template["element_id"], labels)

    elif case_id == "P04":
        p1 = next(element for element in elements if element["element_id"] == "p04-page-1-paragraph-1")
        _insert_after(elements, p1["element_id"], [_copy_text_element(p1, element_id="p04-page-1-paragraph-2", content="表格保留單位與欄位關係，方便逐格定位。")])
        next(element for element in elements if element["element_id"] == "p04-page-1-formula")["content"] = "公式 / Formula: F = m * a"
        for page in (2, 4):
            template = next(element for element in elements if element["element_id"] == f"p04-page-{page}-paragraph-2")
            labels = []
            for suffix, content, x, languages in (
                ("region-a", "區域 A", 115000, ["zh-Hant", "en"]),
                ("review-b", "Review B", 537500, ["en"]),
            ):
                label = _copy_text_element(template, element_id=f"p04-page-{page}-{suffix}", content=content, kind="ui_text")
                label["languages"] = languages
                label["locators"][0]["geometry"] = {
                    "coordinate_space": "normalized_top_left_0_1000000", "x": x, "y": 815000, "width": 360000, "height": 100000
                }
                labels.append(label)
            _insert_after(elements, template["element_id"], labels)

    elif case_id in {"W02", "W03"}:
        prefix = case_id.lower()
        figure_id = f"{prefix}-figure"
        figure = next(element for element in elements if element["element_id"] == figure_id)
        text = "[Input] → [Normalize] → [Review]" if case_id == "W02" else "[Snapshot] → [Structure] → [Reference]"
        figure_text = _copy_text_element(
            figure,
            element_id=f"{figure_id}-text",
            content=text,
            kind="ui_text",
        )
        figure_text["parent_element_id"] = figure_id
        figure_text["languages"] = ["en"]
        figure_text["locators"][0]["dom_path"] += "/div"
        _insert_after(elements, figure_id, [figure_text])
    else:
        raise ValueError(f"unsupported successor case: {case_id}")

    return _finish(payload, case_id=case_id, successor_revision=successor_revision)


def write_successor_reference(case_id: str, predecessor_revision: str, successor_revision: str) -> None:
    document = build_successor_reference(case_id, predecessor_revision, successor_revision)
    data = canonical_normalized_document_bytes(document)
    output = V1_ROOT / "reference_documents" / case_id / successor_revision
    output.mkdir(parents=True, exist_ok=True)
    (output / "normalized_document.json").write_bytes(data)
    (output / "normalized_document.sha256").write_text(
        f"{hashlib.sha256(data).hexdigest()}  normalized_document.json\n",
        encoding="ascii",
    )


__all__ = ["build_successor_reference", "clone_predecessor_source", "write_successor_reference"]
