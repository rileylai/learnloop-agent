from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from tests.evals.parser_note_completeness.normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


REVISION_ROOT = (
    Path(__file__).parent
    / "v1"
)
FIXTURE_ROOT = REVISION_ROOT / "fixtures" / "W01" / "revision-001"
REFERENCE_ROOT = REVISION_ROOT / "reference_documents" / "W01" / "revision-001"
GOVERNANCE_ROOT = REVISION_ROOT / "governance" / "W01" / "revision-001"
CONFIGURATION_PATH = GOVERNANCE_ROOT / "producer_configuration.json"


def _read_digest(path: Path) -> str:
    fields = path.read_text(encoding="utf-8").strip().split()
    assert len(fields) == 2
    return fields[0]


def _reference_payload() -> Dict[str, Any]:
    return json.loads(
        (REFERENCE_ROOT / "normalized_document.json").read_bytes()
    )


def test_w01_source_digest_is_exact_and_bound_to_reference() -> None:
    source_bytes = (FIXTURE_ROOT / "source.html").read_bytes()
    source_digest = hashlib.sha256(source_bytes).hexdigest()
    payload = _reference_payload()

    assert source_digest == "1ab20dc2725df5d5066e2d6113487b4f9ae16973db9709f3bd66e53e4e52f43b"
    assert source_digest == _read_digest(FIXTURE_ROOT / "source.sha256")
    assert payload["source"]["source_snapshot_sha256"] == source_digest


def test_w01_configuration_digest_is_bound_to_exact_configuration_bytes() -> None:
    configuration_bytes = CONFIGURATION_PATH.read_bytes()
    configuration_digest = hashlib.sha256(configuration_bytes).hexdigest()
    payload = _reference_payload()
    configuration = json.loads(configuration_bytes)

    assert configuration_digest == "8c215a2da6054e8025014a0411ffa6af44ef25b64e1e97efab9f9c56b136e41d"
    assert payload["producer_provenance"]["configuration_sha256"] == configuration_digest
    assert configuration["processing_method"] == "project_authored_static_html"
    assert configuration["processing_stage"] == "reference_authoring"
    assert configuration["segmentation_semantics"] == "html-block-elements-v1"
    assert configuration["locator_policy"]["identity"] == "snapshot_sha256_and_dom_path"
    assert configuration["code_language_hint_policy"]["source_supplied"] is False


def test_w01_reference_is_valid_normalized_document_and_canonical_json() -> None:
    reference_path = REFERENCE_ROOT / "normalized_document.json"
    reference_bytes = reference_path.read_bytes()
    payload = _reference_payload()
    document = NormalizedDocument.model_validate(payload)

    assert document.artifact_role.value == "reference_document"
    assert document.document_id == "W01"
    assert reference_bytes == canonical_normalized_document_bytes(document)
    assert hashlib.sha256(reference_bytes).hexdigest() == _read_digest(
        REFERENCE_ROOT / "normalized_document.sha256"
    )
    assert "artifact_sha256" not in payload


def test_w01_capabilities_match_captured_evidence() -> None:
    payload = _reference_payload()
    capabilities = payload["capabilities"]

    assert capabilities["geometry"] == {
        "reason": "not_captured",
        "status": "unavailable",
    }
    assert capabilities["table_structure"] == {"reason": None, "status": "not_applicable"}
    for name in (
        "code_metadata",
        "hierarchy",
        "language_identification",
        "source_modality",
        "typed_locators",
    ):
        assert capabilities[name] == {"reason": None, "status": "available"}


def test_w01_web_locators_match_source_type() -> None:
    document = NormalizedDocument.model_validate(_reference_payload())

    assert document.source.source_type.value == "web"
    assert {locator.locator_type for element in document.elements for locator in element.locators} == {
        "web"
    }


def test_w01_html_is_self_contained_and_static() -> None:
    html = (FIXTURE_ROOT / "source.html").read_text(encoding="utf-8").lower()

    assert all(marker in html for marker in ("<h1>", "<p>", "<ul>", "<li>", "<pre><code>"))
    assert all(
        marker not in html
        for marker in (
            "http://",
            "https://",
            "src=",
            "href=",
            "<script",
            "<iframe",
            "<img",
            "<form",
        )
    )


def test_w01_candidate_is_diagnostic_only_and_has_pending_evidence() -> None:
    candidate = json.loads(
        (GOVERNANCE_ROOT / "candidate.json").read_text(encoding="utf-8")
    )

    assert candidate["candidate_status"] == "draft_candidate"
    assert "result_role" not in candidate
    assert candidate["formal_manifest_present"] is False
    assert candidate["authority"] == {
        "canonical_dataset": False,
        "approved": False,
        "formal": False,
        "baseline_gate_authority": False,
    }
    assert any(item.startswith("Q22:") for item in candidate["pending_evidence"])
    assert any(item.startswith("Q25:") for item in candidate["pending_evidence"])
    assert candidate["artifacts"]["producer_configuration"] == "producer_configuration.json"
    assert not (REVISION_ROOT / "manifests" / "W01-revision-001.json").exists()
