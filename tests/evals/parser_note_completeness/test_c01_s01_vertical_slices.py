from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from tests.evals.parser_note_completeness.normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


ROOT = Path(__file__).parent / "v1"
CASES = {
    "C01": {
        "fixture": ROOT / "fixtures" / "C01" / "revision-001",
        "reference": ROOT / "reference_documents" / "C01" / "revision-001",
        "governance": ROOT / "governance" / "C01" / "revision-001",
        "source_name": "source.json",
        "source_type": "chat",
        "locator_type": "chat",
        "expected_source_digest": "d0f4543a2e71526ec208dbd5b3f645bedc074145ec3e91de5c017276f9fd6288",
        "expected_reference_digest": "0be80f1cdd163fc0aaeefce69b127aa27d5661c496ab65a0083ab0f91263f390",
        "expected_configuration_digest": "10f98b7e9368036e5694485ec9a50b9b7316bdf2f3c825619acb34c19aab70b0",
    },
    "S01": {
        "fixture": ROOT / "fixtures" / "S01" / "revision-001",
        "reference": ROOT / "reference_documents" / "S01" / "revision-001",
        "governance": ROOT / "governance" / "S01" / "revision-001",
        "source_name": "source.png",
        "source_type": "screenshots",
        "locator_type": "screenshots",
        "expected_source_digest": "d0c61b0f04a224d0c32f55fedfab7d5bb63c6a30d0d40430ca7c255c2125f0bd",
        "expected_reference_digest": "b68a8ca56d829880a175b25d23c9ddca4d501a08600702fd6192f39752c73057",
        "expected_configuration_digest": "ec107df07a284e582011f0a5b147739a888f7f6f057aedf3489543c7e84f1f6d",
    },
}


def _digest_record(path: Path) -> list[str]:
    return path.read_text(encoding="ascii").strip().split()


def _payload(case_id: str) -> dict[str, Any]:
    return json.loads((CASES[case_id]["reference"] / "normalized_document.json").read_bytes())


def test_c01_and_s01_source_and_reference_digests_are_exact() -> None:
    for case_id, case in CASES.items():
        source_path = case["fixture"] / case["source_name"]
        reference_path = case["reference"] / "normalized_document.json"
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == case["expected_source_digest"]
        assert _digest_record(case["fixture"] / "source.sha256") == [
            case["expected_source_digest"],
            case["source_name"],
        ]
        assert hashlib.sha256(reference_path.read_bytes()).hexdigest() == case["expected_reference_digest"]
        assert _digest_record(case["reference"] / "normalized_document.sha256") == [
            case["expected_reference_digest"],
            "normalized_document.json",
        ]
        assert _payload(case_id)["source"]["source_snapshot_sha256"] == case["expected_source_digest"]


def test_c01_and_s01_reference_documents_are_canonical_and_valid() -> None:
    for case_id, case in CASES.items():
        reference_path = case["reference"] / "normalized_document.json"
        payload = _payload(case_id)
        document = NormalizedDocument.model_validate(payload)
        assert document.artifact_role.value == "reference_document"
        assert document.document_id == case_id
        assert document.source.source_type.value == case["source_type"]
        assert reference_path.read_bytes() == canonical_normalized_document_bytes(document)
        assert "artifact_sha256" not in payload
        assert "digest" not in payload


def test_producer_configuration_digests_are_bound_to_exact_bytes() -> None:
    for case in CASES.values():
        configuration_path = case["governance"] / "producer_configuration.json"
        assert hashlib.sha256(configuration_path.read_bytes()).hexdigest() == case[
            "expected_configuration_digest"
        ]
        payload = _payload("C01" if case["source_type"] == "chat" else "S01")
        assert payload["producer_provenance"]["configuration_sha256"] == case[
            "expected_configuration_digest"
        ]


def test_chat_and_screenshot_families_keep_distinct_locator_identity_semantics() -> None:
    chat = NormalizedDocument.model_validate(_payload("C01"))
    screenshot = NormalizedDocument.model_validate(_payload("S01"))

    assert all(element.kind.value == "message" for element in chat.elements)
    assert all(locator.locator_type == "chat" for element in chat.elements for locator in element.locators)
    assert all(locator.message_id and locator.source_sequence is not None for element in chat.elements for locator in element.locators)
    assert all(element.kind.value == "ui_text" for element in screenshot.elements)
    assert all(locator.locator_type == "screenshots" for element in screenshot.elements for locator in element.locators)
    assert all(locator.image_index == 1 and locator.image_sha256 for element in screenshot.elements for locator in element.locators)
    assert not any(element.kind.value == "transcript_segment" for element in screenshot.elements)


def test_chat_reply_relations_are_present_in_source_and_reference() -> None:
    source = json.loads((CASES["C01"]["fixture"] / "source.json").read_bytes())
    reference = NormalizedDocument.model_validate(_payload("C01"))
    source_by_id = {message["message_id"]: message for message in source["messages"]}
    assert source_by_id["c01-message-001"]["reply_to_message_id"] is None
    for element in reference.elements:
        locator = element.locators[0]
        assert source_by_id[locator.message_id]["reply_to_message_id"] == locator.reply_to_message_id


def test_screenshot_geometry_is_normalized_integer_and_bounded() -> None:
    document = NormalizedDocument.model_validate(_payload("S01"))
    authoring_bounds = ((70, 84, 570, 112), (70, 166, 474, 194), (70, 248, 498, 276))
    for element, expected in zip(document.elements, authoring_bounds):
        geometry = element.locators[0].region
        assert geometry.coordinate_space == "normalized_top_left_0_1000000"
        assert all(isinstance(getattr(geometry, name), int) for name in ("x", "y", "width", "height"))
        assert 0 <= geometry.x <= 1_000_000
        assert 0 <= geometry.y <= 1_000_000
        assert 0 <= geometry.x + geometry.width <= 1_000_000
        assert 0 <= geometry.y + geometry.height <= 1_000_000
        left = geometry.x * 640 // 1_000_000
        top = geometry.y * 360 // 1_000_000
        right = (geometry.x + geometry.width) * 640 // 1_000_000
        bottom = (geometry.y + geometry.height) * 360 // 1_000_000
        assert left <= expected[0] and top <= expected[1]
        assert right >= expected[2] and bottom >= expected[3]


def test_screenshot_is_fixed_size_raster_and_hierarchy_is_not_claimed() -> None:
    source = (CASES["S01"]["fixture"] / "source.png").read_bytes()
    assert source[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", source[16:24]) == (640, 360)
    payload = _payload("S01")
    assert not (CASES["S01"]["fixture"] / "source.svg").exists()
    assert payload["capabilities"]["hierarchy"] == {
        "reason": "not_captured",
        "status": "unavailable",
    }


def test_sources_are_project_owned_self_contained_and_static() -> None:
    chat = (CASES["C01"]["fixture"] / "source.json").read_text(encoding="utf-8").lower()
    screenshot = (CASES["S01"]["fixture"] / "source.png").read_bytes()
    assert all(marker not in chat for marker in ("http://", "https://", "secret", "password", "@"))
    assert all(marker not in screenshot.lower() for marker in (b"http://", b"https://", b"secret", b"password"))
    assert "conversation_id" in chat and "messages" in chat


def test_candidates_are_draft_non_authoritative_and_have_pending_governance() -> None:
    for case in CASES.values():
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
        assert any(item.startswith("Q22:") for item in candidate["pending_evidence"])
        assert any(item.startswith("Q25:") for item in candidate["pending_evidence"])
        assert any("rights" in item and "privacy" in item and "provenance" in item for item in candidate["pending_evidence"])
        assert any("independent approval" in item for item in candidate["pending_evidence"])
        assert all(not Path(value).is_absolute() for value in candidate["artifacts"].values())
        assert not (ROOT / "manifests" / f"{candidate['case_id']}-revision-001.json").exists()
