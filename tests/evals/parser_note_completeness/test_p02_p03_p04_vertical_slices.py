from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

from pypdf import PdfReader

from tests.evals.parser_note_completeness.normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


ROOT = Path(__file__).parent / "v1"
CASES: dict[str, dict[str, Any]] = {
    "P02": {
        "fixture": ROOT / "fixtures" / "P02" / "revision-001",
        "governance": ROOT / "governance" / "P02" / "revision-001",
        "reference": ROOT / "reference_documents" / "P02" / "revision-001",
        "source_name": "source.pdf",
        "source_type": "pdf",
        "expected_source_digest": "5ee241278ce972aa4157b18d51a8282be59bf4abbfab6bfe1923b12364d70816",
        "expected_configuration_digest": "4ea30df06a1abedba506938fb0b8f5eb17b3d64ffa06272b17cc83d0b02445da",
        "expected_reference_digest": "70bbca910c764daf4423e793962d8509aa4ab6900ba3015746c8758156277e6e",
    },
    "P03": {
        "fixture": ROOT / "fixtures" / "P03" / "revision-001",
        "governance": ROOT / "governance" / "P03" / "revision-001",
        "reference": ROOT / "reference_documents" / "P03" / "revision-001",
        "source_name": "source.pdf",
        "source_type": "pdf",
        "expected_source_digest": "44a7e46292cbad64bab18269027c1bf5945e62c4957469d6749e60d47559a455",
        "expected_configuration_digest": "79046888fda8303e18679fbf1c8df8ab1f811bc62a62782e505ba9d9a1f937c1",
        "expected_reference_digest": "ca9e37fd3ed2b7a674199b836ae29c38800c81e52843427c614a7aab15590b12",
    },
    "P04": {
        "fixture": ROOT / "fixtures" / "P04" / "revision-001",
        "governance": ROOT / "governance" / "P04" / "revision-001",
        "reference": ROOT / "reference_documents" / "P04" / "revision-001",
        "source_name": "source.pdf",
        "source_type": "pdf",
        "expected_source_digest": "d353e1da824c08c2a2872d365cead717b265abdbebc4f5f94a71596569171c3c",
        "expected_configuration_digest": "f9cd521f05964afb0036b3ff82738e327cedba933526b4693b6d121c7c7dadba",
        "expected_reference_digest": "f4351414267d92f6657eea1f3d04f55c616e0253bc656c18abbf640afe0ee18d",
    },
}


def _load_build_source(case_id: str) -> ModuleType:
    path = CASES[case_id]["fixture"] / "build_source.py"
    spec = importlib.util.spec_from_file_location(f"{case_id.lower()}_build_source", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload(case_id: str) -> dict[str, Any]:
    return json.loads((CASES[case_id]["reference"] / "normalized_document.json").read_bytes())


def _digest_record(path: Path) -> list[str]:
    return path.read_text(encoding="ascii").strip().split()


def _document(case_id: str) -> NormalizedDocument:
    return NormalizedDocument.model_validate(_payload(case_id))


def test_p02_p03_p04_source_configuration_and_reference_digests_are_exact() -> None:
    for case_id, case in CASES.items():
        source_path = case["fixture"] / case["source_name"]
        configuration_path = case["governance"] / "producer_configuration.json"
        reference_path = case["reference"] / "normalized_document.json"
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == case["expected_source_digest"]
        assert _digest_record(case["fixture"] / "source.sha256") == [case["expected_source_digest"], case["source_name"]]
        assert hashlib.sha256(configuration_path.read_bytes()).hexdigest() == case["expected_configuration_digest"]
        assert hashlib.sha256(reference_path.read_bytes()).hexdigest() == case["expected_reference_digest"]
        assert _digest_record(case["reference"] / "normalized_document.sha256") == [case["expected_reference_digest"], "normalized_document.json"]


def test_p02_p03_p04_references_are_canonical_schema_valid_and_bound() -> None:
    for case_id, case in CASES.items():
        payload = _payload(case_id)
        document = NormalizedDocument.model_validate(payload)
        assert document.document_id == case_id
        assert document.artifact_role.value == "reference_document"
        assert document.source.source_type.value == case["source_type"]
        assert document.source.source_snapshot_sha256 == case["expected_source_digest"]
        assert document.producer_provenance.configuration_sha256 == case["expected_configuration_digest"]
        assert (case["reference"] / "normalized_document.json").read_bytes() == canonical_normalized_document_bytes(document)
        assert "artifact_sha256" not in payload
        assert "digest" not in payload


def test_p02_is_bilingual_native_text_with_two_tables_and_two_figures() -> None:
    case = CASES["P02"]
    reader = PdfReader(str(case["fixture"] / "source.pdf"))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "雙語資料系統報告" in extracted
    assert "Bilingual Data Systems Report" in extracted
    assert all("/XObject" not in page.get("/Resources", {}) for page in reader.pages)

    document = _document("P02")
    assert len(document.sections) == 4
    assert sum(element.kind.value == "table" for element in document.elements) == 2
    assert sum(element.kind.value == "figure" for element in document.elements) == 2
    assert sum(element.kind.value == "table_cell" for element in document.elements) == 24
    assert document.source.languages == ("zh-Hant", "en")
    assert document.capabilities.table_structure.status.value == "available"
    assert document.capabilities.geometry.status.value == "unavailable"


def test_p02_build_recipe_reproduces_exact_native_pdf_bytes() -> None:
    module = _load_build_source("P02")
    assert module.build_pdf() == (CASES["P02"]["fixture"] / "source.pdf").read_bytes()


def test_p03_is_at_least_five_pages_and_raster_only_with_geometry() -> None:
    case = CASES["P03"]
    reader = PdfReader(str(case["fixture"] / "source.pdf"))
    assert len(reader.pages) >= 5
    for page in reader.pages:
        assert page.extract_text() in (None, "")
        xobjects = page["/Resources"]["/XObject"].get_object()
        assert xobjects
        assert all(resource.get("/Subtype") == "/Image" for resource in xobjects.values())

    document = _document("P03")
    assert document.source.languages == ("zh-Hant",)
    assert document.capabilities.geometry.status.value == "available"
    assert all(element.locators[0].geometry is not None for element in document.elements)
    assert all(element.locators[0].page == index for index, section in enumerate(document.sections, start=1) for element in document.elements[section.start_order : section.end_order + 1])
    assert any("第一頁" in element.content for element in document.elements if element.content)


def test_p03_build_recipe_reproduces_exact_scanned_pdf_bytes() -> None:
    module = _load_build_source("P03")
    assert module.build_pdf() == (CASES["P03"]["fixture"] / "source.pdf").read_bytes()


def test_p04_has_native_and_scanned_pages_with_formula_and_table() -> None:
    case = CASES["P04"]
    reader = PdfReader(str(case["fixture"] / "source.pdf"))
    assert len(reader.pages) == 4
    assert (reader.pages[0].extract_text() or "").strip()
    assert (reader.pages[2].extract_text() or "").strip()
    assert reader.pages[1].extract_text() in (None, "")
    assert reader.pages[3].extract_text() in (None, "")
    assert "/XObject" not in reader.pages[0].get("/Resources", {})
    assert "/XObject" not in reader.pages[2].get("/Resources", {})
    assert "/XObject" in reader.pages[1].get("/Resources", {})
    assert "/XObject" in reader.pages[3].get("/Resources", {})

    document = _document("P04")
    assert document.source.languages == ("zh-Hant", "en")
    assert sum(element.kind.value == "formula" for element in document.elements) == 1
    assert sum(element.kind.value == "table" for element in document.elements) == 1
    assert document.capabilities.geometry.status.value == "partial"
    assert document.capabilities.source_modality.status.value == "available"
    assert {element.locators[0].page for element in document.elements if element.locators[0].geometry is not None} == {2, 4}


def test_p04_build_recipe_reproduces_exact_mixed_pdf_bytes() -> None:
    module = _load_build_source("P04")
    assert module.build_pdf() == (CASES["P04"]["fixture"] / "source.pdf").read_bytes()


def test_p02_p03_p04_candidates_remain_draft_and_non_authoritative() -> None:
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


def test_p02_p03_p04_sources_and_configurations_are_project_owned_self_contained() -> None:
    for case in CASES.values():
        configuration = (case["governance"] / "producer_configuration.json").read_text(encoding="utf-8").lower()
        assert all(marker not in configuration for marker in ("http://", "https://", "password", "secret"))
