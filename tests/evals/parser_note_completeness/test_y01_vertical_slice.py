from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from tests.evals.parser_note_completeness.normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


ROOT = Path(__file__).parent / "v1"
FIXTURE = ROOT / "fixtures" / "Y01" / "revision-001"
GOVERNANCE = ROOT / "governance" / "Y01" / "revision-001"
REFERENCE = ROOT / "reference_documents" / "Y01" / "revision-001"
CAPTIONS_DIGEST = "fcba02596d324e983b2a38fd99855065ce5bffb2bcfbb33ded1c433c8b821c3f"
CHAPTERS_DIGEST = "eb42210bf3e91a3ce99a6f59594f6e116a01c6c105964a2000bcdf3593855f86"
SNAPSHOT_DIGEST = "66765dcc81f041b8d20c1484db4651f063d9ed53cac82d3bc900123ea97d873a"
CONFIGURATION_DIGEST = "0cdff3c9ef9d6da48aff3515601b6d88f042fade85d6046929ccaa50ef2c2ca1"
REFERENCE_DIGEST = "c1937ce21c5baba204428eabbeae4d5b52945ca7a06220b9012ade17ba7e6251"
TIMESTAMP = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.(\d{3})$")


def _payload() -> dict[str, object]:
    return json.loads((REFERENCE / "normalized_document.json").read_bytes())


def _to_ms(timestamp: str) -> int:
    match = TIMESTAMP.fullmatch(timestamp)
    assert match is not None
    hours, minutes, seconds, millis = (int(part) for part in match.groups())
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


def _parse_vtt() -> list[tuple[int, int, int, str]]:
    lines = (FIXTURE / "captions.vtt").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "WEBVTT"
    cues = []
    index = 0
    cursor = 1
    while cursor < len(lines):
        if not lines[cursor].strip():
            cursor += 1
            continue
        start, end = (part.strip() for part in lines[cursor].split("-->"))
        text = lines[cursor + 1]
        cues.append((index, _to_ms(start), _to_ms(end), text))
        index += 1
        cursor += 2
    return cues


def _digest_record(path: Path) -> list[str]:
    return path.read_text(encoding="ascii").strip().split()


def test_y01_vtt_cues_are_ordered_and_have_valid_millisecond_ranges() -> None:
    cues = _parse_vtt()
    assert len(cues) == 9
    assert [cue[0] for cue in cues] == list(range(9))
    previous_end = -1
    for _, start_ms, end_ms, text in cues:
        assert start_ms >= 0
        assert end_ms > start_ms
        assert start_ms >= previous_end
        assert text.strip()
        previous_end = end_ms


def test_y01_chapters_bind_exact_cue_boundaries() -> None:
    chapters = json.loads((FIXTURE / "chapters.json").read_bytes())["chapters"]
    cues = _parse_vtt()
    assert len(chapters) == 3
    for chapter in chapters:
        selected = [
            cue
            for cue in cues
            if chapter["start_cue_index"] <= cue[0] <= chapter["end_cue_index"]
        ]
        assert selected
        assert selected[0][1] == chapter["start_ms"]
        assert selected[-1][2] == chapter["end_ms"]
        assert chapter["start_cue_index"] <= chapter["end_cue_index"]


def test_y01_component_and_snapshot_digests_bind_exact_bytes() -> None:
    expected = {
        "captions.vtt": CAPTIONS_DIGEST,
        "chapters.json": CHAPTERS_DIGEST,
    }
    for filename, digest in expected.items():
        path = FIXTURE / filename
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        assert _digest_record(FIXTURE / filename.replace(".vtt", ".sha256").replace(".json", ".sha256")) == [digest, filename]

    snapshot_path = FIXTURE / "source_snapshot.json"
    snapshot = json.loads(snapshot_path.read_bytes())
    assert hashlib.sha256(snapshot_path.read_bytes()).hexdigest() == SNAPSHOT_DIGEST
    assert _digest_record(FIXTURE / "source_snapshot.sha256") == [SNAPSHOT_DIGEST, "source_snapshot.json"]
    canonical_snapshot = json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8") + b"\n"
    assert snapshot_path.read_bytes() == canonical_snapshot
    assert "digest" not in snapshot and "source_snapshot_sha256" not in snapshot
    assert snapshot["source_type"] == "youtube"
    for component in snapshot["components"]:
        component_path = component["path"]
        assert not Path(component_path).is_absolute()
        assert "\\" not in component_path
        assert component["sha256"] == expected[component_path]


def test_y01_reference_is_canonical_and_bound_to_source_configuration() -> None:
    reference_path = REFERENCE / "normalized_document.json"
    configuration_path = GOVERNANCE / "producer_configuration.json"
    document = NormalizedDocument.model_validate(_payload())
    assert hashlib.sha256(configuration_path.read_bytes()).hexdigest() == CONFIGURATION_DIGEST
    assert hashlib.sha256(reference_path.read_bytes()).hexdigest() == REFERENCE_DIGEST
    assert _digest_record(REFERENCE / "normalized_document.sha256") == [REFERENCE_DIGEST, "normalized_document.json"]
    assert reference_path.read_bytes() == canonical_normalized_document_bytes(document)
    assert document.source.source_type.value == "youtube"
    assert document.source.source_snapshot_sha256 == SNAPSHOT_DIGEST
    assert document.producer_provenance.configuration_sha256 == CONFIGURATION_DIGEST
    assert "artifact_sha256" not in _payload()
    assert "digest" not in _payload()


def test_y01_cue_locators_use_typed_unavailable_platform_identities() -> None:
    document = NormalizedDocument.model_validate(_payload())
    segments = [element for element in document.elements if element.kind.value == "transcript_segment"]
    headings = [element for element in document.elements if element.kind.value == "heading"]
    assert len(segments) == 9
    assert len(headings) == 3
    for index, element in enumerate(segments):
        locator = element.locators[0]
        assert locator.locator_type == "youtube"
        assert locator.status.value == "available"
        assert locator.cue_index == index
        assert locator.start_ms is not None and locator.end_ms is not None
        assert locator.end_ms > locator.start_ms
        assert locator.video_identity.status.value == "unavailable"
        assert locator.caption_track_identity.status.value == "unavailable"
        assert locator.video_identity.value is None
        assert locator.caption_track_identity.value is None
        assert locator.video_identity.reason == "synthetic_platform_identity_unavailable"
        assert locator.caption_track_identity.reason == "synthetic_platform_identity_unavailable"
    for heading in headings:
        locator = heading.locators[0]
        assert locator.status.value == "unavailable"
        assert locator.reason == "chapter_title_locator_unavailable"
        assert locator.cue_index is None
        assert locator.start_ms is None
        assert locator.end_ms is None
        assert locator.video_identity is None
        assert locator.caption_track_identity is None
    assert document.capabilities.typed_locators.status.value == "partial"
    assert document.capabilities.typed_locators.reason == "chapter_title_locator_unavailable"


def test_y01_sections_preserve_chapter_titles_and_cue_order() -> None:
    document = NormalizedDocument.model_validate(_payload())
    assert len(document.sections) == 3
    assert [section.start_order for section in document.sections] == [0, 4, 8]
    assert [section.end_order for section in document.sections] == [3, 7, 11]
    for section in document.sections:
        heading = document.elements[section.start_order]
        assert heading.element_id == section.heading_element_id
        assert heading.kind.value == "heading"
        assert heading.section_id == section.section_id
        assert all(
            element.section_id == section.section_id
            for element in document.elements[section.start_order : section.end_order + 1]
        )


def test_y01_has_no_platform_media_or_asr_claims_and_is_non_authoritative() -> None:
    fixture_text = " ".join(
        path.read_text(encoding="utf-8").lower()
        for path in (FIXTURE / "captions.vtt", FIXTURE / "chapters.json", FIXTURE / "source_snapshot.json", GOVERNANCE / "producer_configuration.json")
    )
    assert all(marker not in fixture_text for marker in ("http://", "https://", "youtube.com", "youtu.be", "audio", "asr score"))
    document = NormalizedDocument.model_validate(_payload())
    assert document.producer_provenance.asr_model is None
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
    assert not (ROOT / "manifests" / "Y01-revision-001.json").exists()
