from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

from tests.evals.parser_note_completeness.normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


ROOT = Path(__file__).parent / "v1"
CASES: dict[str, dict[str, Any]] = {
    "W02": {
        "fixture": ROOT / "fixtures" / "W02" / "revision-001",
        "governance": ROOT / "governance" / "W02" / "revision-001",
        "reference": ROOT / "reference_documents" / "W02" / "revision-001",
        "expected_source_digest": "368f3bf9192bb7c9099e83f95e8d0b72cffbc0dab3ee04ac81e4415fcca32e51",
        "expected_configuration_digest": "422a1f8f222481c6578783c3c0d82efade14a1721a3896a83e79596275d21943",
        "expected_reference_digest": "a56bde702d26ed1b0e2d0b0693bdf5bc60176097bd394ab72050df693c392ad1",
    },
    "W03": {
        "fixture": ROOT / "fixtures" / "W03" / "revision-001",
        "governance": ROOT / "governance" / "W03" / "revision-001",
        "reference": ROOT / "reference_documents" / "W03" / "revision-001",
        "expected_source_digest": "a6b8495a77d7d5fd95fb4ba9ca98aa56e9043c09447f42b15090bd1dc134f2df",
        "expected_configuration_digest": "3b6de7bd4f633e2504ff08c8691d0b41468d4c99ac899217f542967bb7c7418e",
        "expected_reference_digest": "7f487bccc28484982f71f4f24ea1a501724c9adb2797cd35bcd0e16ef394832f",
    },
}


def _load_build_source(case_id: str) -> ModuleType:
    path = CASES[case_id]["fixture"] / "build_source.py"
    spec = importlib.util.spec_from_file_location(f"{case_id.lower()}_build_source", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_build_reference(case_id: str) -> ModuleType:
    path = CASES[case_id]["fixture"] / "build_reference.py"
    spec = importlib.util.spec_from_file_location(f"{case_id.lower()}_build_reference", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload(case_id: str) -> dict[str, Any]:
    return json.loads((CASES[case_id]["reference"] / "normalized_document.json").read_bytes())


def _document(case_id: str) -> NormalizedDocument:
    return NormalizedDocument.model_validate(_payload(case_id))


def _digest_record(path: Path) -> list[str]:
    return path.read_text(encoding="ascii").strip().split()


def test_w02_w03_source_configuration_and_reference_digests_are_exact() -> None:
    for case_id, case in CASES.items():
        source_path = case["fixture"] / "source.html"
        configuration_path = case["governance"] / "producer_configuration.json"
        reference_path = case["reference"] / "normalized_document.json"
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == case["expected_source_digest"]
        assert _digest_record(case["fixture"] / "source.sha256") == [
            case["expected_source_digest"],
            "source.html",
        ]
        assert hashlib.sha256(configuration_path.read_bytes()).hexdigest() == case["expected_configuration_digest"]
        assert hashlib.sha256(reference_path.read_bytes()).hexdigest() == case["expected_reference_digest"]
        assert _digest_record(case["reference"] / "normalized_document.sha256") == [
            case["expected_reference_digest"],
            "normalized_document.json",
        ]


def test_w02_w03_references_are_canonical_schema_valid_and_web_bound() -> None:
    for case_id, case in CASES.items():
        payload = _payload(case_id)
        document = _document(case_id)
        assert document.document_id == case_id
        assert document.artifact_role.value == "reference_document"
        assert document.source.source_type.value == "web"
        assert document.source.source_snapshot_sha256 == case["expected_source_digest"]
        assert document.producer_provenance.configuration_sha256 == case["expected_configuration_digest"]
        assert (case["reference"] / "normalized_document.json").read_bytes() == canonical_normalized_document_bytes(document)
        assert "artifact_sha256" not in payload
        assert "digest" not in payload
        for element in document.elements:
            locator = element.locators[0]
            assert locator.snapshot_sha256 == case["expected_source_digest"]
            assert locator.dom_path.startswith("/html/")


def test_w02_is_complex_bilingual_static_html_with_required_structures() -> None:
    case = CASES["W02"]
    html = (case["fixture"] / "source.html").read_text(encoding="utf-8")
    assert all(
        marker in html
        for marker in (
            "<h1>",
            "<h2>",
            "<ul>",
            "<ol>",
            "<table>",
            "<pre><code",
            "<figure",
            "<figcaption>",
            "<header",
            "<nav",
            "<aside",
            "<footer",
            "Traceable Data Workflows",
            "可追蹤的資料流程",
        )
    )
    assert all(marker not in html.lower() for marker in ("http://", "https://", "<script", "<iframe", "src="))

    document = _document("W02")
    assert document.source.languages == ("zh-Hant", "en")
    assert sum(element.kind.value == "list_item" for element in document.elements) == 5
    assert sum(element.kind.value == "table" for element in document.elements) == 1
    assert sum(element.kind.value == "table_cell" for element in document.elements) == 12
    assert sum(element.kind.value == "code_block" for element in document.elements) == 1
    assert sum(element.kind.value == "figure" for element in document.elements) == 1
    assert sum(element.kind.value == "caption" for element in document.elements) == 2
    assert document.capabilities.table_structure.status.value == "available"
    assert document.capabilities.code_metadata.status.value == "available"


def test_w03_is_deterministic_offline_rendered_dom_with_nested_sections() -> None:
    case = CASES["W03"]
    html = (case["fixture"] / "source.html").read_text(encoding="utf-8").lower()
    assert "data-rendered-dom-snapshot=\"offline-revision-001\"" in html
    assert "data-rendered=\"true\"" in html
    assert all(
        marker not in html
        for marker in (
            "http://",
            "https://",
            "<script",
            "<iframe",
            "playwright",
            "selenium",
            "src=",
        )
    )

    configuration = json.loads(
        (case["governance"] / "producer_configuration.json").read_bytes()
    )
    assert configuration["network_policy"] == "offline_no_network_access"
    assert configuration["runtime_policy"] == "no_browser_runtime"

    document = _document("W03")
    sections = {section.section_id: section for section in document.sections}
    assert document.source.languages == ("zh-Hant", "en")
    assert sections["w03-table"].parent_section_id == "w03-details"
    assert sections["w03-figure"].parent_section_id == "w03-details"
    assert sections["w03-details"].parent_section_id == "w03-root"
    assert sum(element.kind.value == "table" for element in document.elements) == 1
    assert sum(element.kind.value == "table_cell" for element in document.elements) == 9
    assert sum(element.kind.value == "figure" for element in document.elements) == 1
    assert sum(element.kind.value == "caption" for element in document.elements) == 2
    assert document.capabilities.hierarchy.status.value == "available"


def test_w02_w03_builders_are_byte_deterministic_and_have_no_runtime_or_network_imports() -> None:
    forbidden_imports = {"requests", "urllib", "urllib3", "playwright", "selenium", "pyppeteer"}
    for case_id, case in CASES.items():
        source_module = _load_build_source(case_id)
        reference_module = _load_build_reference(case_id)
        assert source_module.build_html() == (case["fixture"] / "source.html").read_bytes()
        assert canonical_normalized_document_bytes(reference_module.build_document()) == (
            case["reference"] / "normalized_document.json"
        ).read_bytes()
        for module_path in (case["fixture"] / "build_source.py", case["fixture"] / "build_reference.py"):
            tree = ast.parse(module_path.read_text(encoding="utf-8"))
            imported_names = {
                alias.name.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            assert imported_names.isdisjoint(forbidden_imports)
            assert "http://" not in module_path.read_text(encoding="utf-8").lower()
            assert "https://" not in module_path.read_text(encoding="utf-8").lower()


def test_w02_w03_candidates_remain_draft_and_non_authoritative() -> None:
    for case_id, case in CASES.items():
        candidate = json.loads((case["governance"] / "candidate.json").read_bytes())
        assert candidate["candidate_status"] == "draft_candidate"
        assert candidate["formal_manifest_present"] is False
        assert candidate["authority"] == {
            "approved": False,
            "baseline_gate_authority": False,
            "canonical_dataset": False,
            "formal": False,
        }
        assert "result_role" not in candidate
        assert all(not Path(value).is_absolute() for value in candidate["artifacts"].values())
        assert any(item.startswith("Q22:") for item in candidate["pending_evidence"])
        assert any(item.startswith("Q25:") for item in candidate["pending_evidence"])
        assert not (ROOT / "manifests" / f"{case_id}-revision-001.json").exists()
