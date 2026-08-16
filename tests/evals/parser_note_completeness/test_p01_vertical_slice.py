from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from pypdf import PdfReader

from tests.evals.parser_note_completeness.normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


ROOT = Path(__file__).parent / "v1"
FIXTURE = ROOT / "fixtures" / "P01" / "revision-001"
GOVERNANCE = ROOT / "governance" / "P01" / "revision-001"
REFERENCE = ROOT / "reference_documents" / "P01" / "revision-001"
SOURCE_DIGEST = "2ec844a220a426e14eca5a60a9d19767751bee022b67cb3998a110cdf382b973"
CONFIGURATION_DIGEST = "4064fb9d2531a1acc8e5ea5c7e307b01098d895c98037d08ed5424749c9f1fdd"
REFERENCE_DIGEST = "a6a86086598084f9557bda254857439511237aa07117eecbefb8db5d08c22db3"


def _document_payload() -> dict[str, object]:
    return json.loads((REFERENCE / "normalized_document.json").read_bytes())


def _load_build_source():
    path = FIXTURE / "build_source.py"
    spec = importlib.util.spec_from_file_location("p01_build_source", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p01_pdf_is_native_text_with_eight_pages_and_required_content() -> None:
    source = FIXTURE / "source.pdf"
    assert source.read_bytes().startswith(b"%PDF-")
    reader = PdfReader(str(source))
    assert len(reader.pages) >= 8
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    for required in (
        "Reliable Queue Workers",
        "Queue Contracts",
        "Idempotent Jobs",
        "Retries and Backoff",
        "def handle(job, store):",
        "python -m pytest tests/test_worker.py -q",
    ):
        assert required in extracted
    assert all("/XObject" not in page.get("/Resources", {}) for page in reader.pages)


def test_p01_pdf_list_items_have_visible_markers_but_paragraphs_do_not() -> None:
    reader = PdfReader(str(FIXTURE / "source.pdf"))
    page_text = [page.extract_text() or "" for page in reader.pages]
    document = NormalizedDocument.model_validate(_document_payload())
    for element in document.elements:
        page = element.locators[0].page
        assert page is not None
        if element.kind.value == "list_item":
            assert f"- {element.content}" in page_text[page - 1]
        elif element.kind.value == "paragraph":
            assert element.content in page_text[page - 1]
            assert f"- {element.content}" not in page_text[page - 1]


def test_p01_build_recipe_reproduces_exact_pdf_bytes() -> None:
    module = _load_build_source()
    assert module.build_pdf() == (FIXTURE / "source.pdf").read_bytes()
    assert set(module.__dict__) >= {"PAGES", "build_pdf"}


def test_p01_source_configuration_and_reference_digests_are_exact() -> None:
    source = FIXTURE / "source.pdf"
    configuration = GOVERNANCE / "producer_configuration.json"
    reference = REFERENCE / "normalized_document.json"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_DIGEST
    assert (FIXTURE / "source.sha256").read_text(encoding="ascii").strip().split() == [
        SOURCE_DIGEST,
        "source.pdf",
    ]
    assert hashlib.sha256(configuration.read_bytes()).hexdigest() == CONFIGURATION_DIGEST
    assert hashlib.sha256(reference.read_bytes()).hexdigest() == REFERENCE_DIGEST
    assert (REFERENCE / "normalized_document.sha256").read_text(encoding="ascii").strip().split() == [
        REFERENCE_DIGEST,
        "normalized_document.json",
    ]


def test_p01_reference_is_canonical_valid_and_source_bound() -> None:
    payload = _document_payload()
    document = NormalizedDocument.model_validate(payload)
    assert document.document_id == "P01"
    assert document.artifact_role.value == "reference_document"
    assert document.source.source_type.value == "pdf"
    assert document.source.source_snapshot_sha256 == SOURCE_DIGEST
    assert document.producer_provenance.configuration_sha256 == CONFIGURATION_DIGEST
    assert (REFERENCE / "normalized_document.json").read_bytes() == canonical_normalized_document_bytes(document)
    assert "artifact_sha256" not in payload
    assert "digest" not in payload


def test_p01_pdf_locators_preserve_page_order_without_fabricated_geometry() -> None:
    document = NormalizedDocument.model_validate(_document_payload())
    assert len(document.sections) == 8
    assert [section.start_order for section in document.sections] == sorted(
        section.start_order for section in document.sections
    )
    for section in document.sections:
        heading = document.elements[section.start_order]
        assert heading.kind.value == "heading"
        assert section.heading_element_id == heading.element_id
        for element in document.elements[section.start_order : section.end_order + 1]:
            locator = element.locators[0]
            assert locator.locator_type == "pdf"
            assert locator.status.value == "available"
            assert locator.page == int(section.section_id.rsplit("-", 1)[1])
            assert locator.geometry is None
    assert document.capabilities.geometry.status.value == "unavailable"
    assert document.capabilities.geometry.reason == "not_captured"


def test_p01_code_metadata_and_list_structure_match_pdf_content() -> None:
    document = NormalizedDocument.model_validate(_document_payload())
    code_blocks = [element for element in document.elements if element.kind.value == "code_block"]
    assert {element.code_metadata.language_hint for element in code_blocks} == {"python", "shell"}
    assert all(element.code_metadata.source_supplied is True for element in code_blocks)
    list_items = [element for element in document.elements if element.kind.value == "list_item"]
    assert list_items
    assert all(element.list_metadata.list_kind.value == "unordered" for element in list_items)
    assert all(element.list_metadata.nesting_level == 0 for element in list_items)
    assert document.capabilities.code_metadata.status.value == "available"


def test_p01_candidate_is_draft_and_non_authoritative() -> None:
    candidate = json.loads((GOVERNANCE / "candidate.json").read_bytes())
    assert candidate["candidate_status"] == "draft_candidate"
    assert candidate["formal_manifest_present"] is False
    assert candidate["authority"] == {
        "approved": False,
        "baseline_gate_authority": False,
        "canonical_dataset": False,
        "formal": False,
    }
    assert "result_role" not in candidate
    assert any(item.startswith("Q22:") for item in candidate["pending_evidence"])
    assert any(item.startswith("Q25:") for item in candidate["pending_evidence"])
    assert all(not Path(value).is_absolute() for value in candidate["artifacts"].values())
    assert not (ROOT / "manifests" / "P01-revision-001.json").exists()


def test_p01_source_is_project_owned_and_has_no_remote_dependency() -> None:
    source_text = "\n".join(page.extract_text() or "" for page in PdfReader(str(FIXTURE / "source.pdf")).pages).lower()
    configuration = (GOVERNANCE / "producer_configuration.json").read_text(encoding="utf-8").lower()
    assert all(marker not in source_text for marker in ("http://", "https://", "password", "secret"))
    assert all(marker not in configuration for marker in ("http://", "https://", "password", "secret"))
    assert "stdlib" in configuration
