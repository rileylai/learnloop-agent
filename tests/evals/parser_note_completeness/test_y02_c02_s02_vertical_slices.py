from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from tests.evals.parser_note_completeness.normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


ROOT = Path(__file__).parent / "v1"
CASES: dict[str, dict[str, Any]] = {
    "Y02": {
        "fixture": ROOT / "fixtures" / "Y02" / "revision-001",
        "governance": ROOT / "governance" / "Y02" / "revision-001",
        "reference": ROOT / "reference_documents" / "Y02" / "revision-001",
        "captions_digest": "00e026765c4e166395bcc976cc86d51c723069d035b5c8d360cf72abcb360381",
        "chapters_digest": "a2da21a2ca3abbaf0352dfa061f0f9268318036df47c128d9f41dd5c5160fa96",
        "source_snapshot_digest": "a3b1b53f0450ac63bf6ad327d1adfad066ff9a4c706b2614db8a03b96b1f97ec",
        "configuration_digest": "df200ad56e82b12ebf4a1d1a92542d2fdaed1586161bc3caad327585f2d97d71",
        "reference_digest": "e018e28558b6b69604ab6249be99e57bb25729eb878dadad40c7e59e84d8c2d6",
    },
    "C02": {
        "fixture": ROOT / "fixtures" / "C02" / "revision-001",
        "governance": ROOT / "governance" / "C02" / "revision-001",
        "reference": ROOT / "reference_documents" / "C02" / "revision-001",
        "source_digest": "7ac22d5006e724078d5db448768f8e85b704d4ef17ebaebd74f7d148eeb4a77e",
        "configuration_digest": "bec50cc047fa8cc1040fad641a1fd8e7fbef106d714ec1af1608832e562a5b36",
        "reference_digest": "ce6d935830bd56d3b55a56f1b547dac78c798ab8249d224f7b0f19ac179e3e0e",
    },
    "S02": {
        "fixture": ROOT / "fixtures" / "S02" / "revision-002",
        "governance": ROOT / "governance" / "S02" / "revision-002",
        "reference": ROOT / "reference_documents" / "S02" / "revision-002",
        "image_001_digest": "47617d8a01d6d7d3e47fc8b521c96b677bd5f18d170eeeaf8f4eacc18fc7c5ad",
        "image_002_digest": "90ad2a83c837d12586c76d72bddd11293fd2ed6e3c705addb04cb2d794770c4e",
        "source_manifest_digest": "34ac32424526527808db6c54f615ff9b5e2f2594a89590102902c1cb8ecaeb30",
        "configuration_digest": "94edf506a69ec56cee5d6048475b6dbe33fa4c3f7ffd7f9784e0ffb08ee1fe7b",
        "reference_digest": "e5f58120026419c284a9a8bbbf90d31b122c19aa68daaece0f6138fcb33ed98f",
    },
}


def _load_module(case_id: str, name: str) -> ModuleType:
    path = CASES[case_id]["fixture"] / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{case_id.lower()}_{name}", path)
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


def _parse_vtt(path: Path) -> list[tuple[int, int, int, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "WEBVTT"
    cues: list[tuple[int, int, int, str]] = []
    cursor = 1
    while cursor < len(lines):
        if not lines[cursor].strip():
            cursor += 1
            continue
        start, end = (part.strip() for part in lines[cursor].split("-->"))
        def to_ms(value: str) -> int:
            hours, minutes, rest = value.split(":")
            seconds, millis = rest.split(".")
            return ((int(hours) * 60 + int(minutes)) * 60 + int(seconds)) * 1000 + int(millis)
        cues.append((len(cues), to_ms(start), to_ms(end), lines[cursor + 1]))
        cursor += 2
    return cues


def test_y02_c02_s02_source_configuration_and_reference_digests_are_exact() -> None:
    y02 = CASES["Y02"]
    assert hashlib.sha256((y02["fixture"] / "captions.vtt").read_bytes()).hexdigest() == y02["captions_digest"]
    assert _digest_record(y02["fixture"] / "captions.sha256") == [y02["captions_digest"], "captions.vtt"]
    assert hashlib.sha256((y02["fixture"] / "chapters.json").read_bytes()).hexdigest() == y02["chapters_digest"]
    assert _digest_record(y02["fixture"] / "chapters.sha256") == [y02["chapters_digest"], "chapters.json"]
    assert hashlib.sha256((y02["fixture"] / "source_snapshot.json").read_bytes()).hexdigest() == y02["source_snapshot_digest"]
    assert _digest_record(y02["fixture"] / "source_snapshot.sha256") == [y02["source_snapshot_digest"], "source_snapshot.json"]

    for case_id in ("C02",):
        case = CASES[case_id]
        assert hashlib.sha256((case["fixture"] / "source.json").read_bytes()).hexdigest() == case["source_digest"]
        assert _digest_record(case["fixture"] / "source.sha256") == [case["source_digest"], "source.json"]

    s02 = CASES["S02"]
    for index in (1, 2):
        digest = s02[f"image_{index:03d}_digest"]
        filename = f"source-{index:03d}.png"
        assert hashlib.sha256((s02["fixture"] / filename).read_bytes()).hexdigest() == digest
        assert _digest_record(s02["fixture"] / f"source-{index:03d}.sha256") == [digest, filename]
    assert hashlib.sha256((s02["fixture"] / "source_manifest.json").read_bytes()).hexdigest() == s02["source_manifest_digest"]
    assert _digest_record(s02["fixture"] / "source.sha256") == [s02["source_manifest_digest"], "source_manifest.json"]

    for case_id in CASES:
        case = CASES[case_id]
        configuration = case["governance"] / "producer_configuration.json"
        reference = case["reference"] / "normalized_document.json"
        assert hashlib.sha256(configuration.read_bytes()).hexdigest() == case["configuration_digest"]
        assert hashlib.sha256(reference.read_bytes()).hexdigest() == case["reference_digest"]
        assert _digest_record(case["reference"] / "normalized_document.sha256") == [case["reference_digest"], "normalized_document.json"]


def test_y02_has_ordered_bilingual_cues_with_timestamp_locators() -> None:
    case = CASES["Y02"]
    cues = _parse_vtt(case["fixture"] / "captions.vtt")
    assert len(cues) == 8
    assert [cue[0] for cue in cues] == list(range(8))
    previous_end = -1
    for _, start_ms, end_ms, text in cues:
        assert start_ms >= previous_end
        assert end_ms > start_ms
        assert any("\u4e00" <= character <= "\u9fff" for character in text)
        assert any(character.isascii() and character.isalpha() for character in text)
        previous_end = end_ms

    snapshot = json.loads((case["fixture"] / "source_snapshot.json").read_bytes())
    assert snapshot["offline"] is True
    assert snapshot["source_type"] == "youtube"
    assert [component["path"] for component in snapshot["components"]] == ["captions.vtt", "chapters.json"]
    assert all(not Path(component["path"]).is_absolute() and "\\" not in component["path"] for component in snapshot["components"])
    assert all(marker not in (case["fixture"] / filename).read_text(encoding="utf-8").lower() for filename in ("captions.vtt", "chapters.json", "source_snapshot.json") for marker in ("http://", "https://", "youtube.com", "youtu.be"))

    document = _document("Y02")
    segments = [element for element in document.elements if element.kind.value == "transcript_segment"]
    headings = [element for element in document.elements if element.kind.value == "heading"]
    assert len(segments) == 8
    assert len(headings) == 3
    assert document.source.languages == ("zh-Hant", "en")
    assert document.source.source_snapshot_sha256 == CASES["Y02"]["source_snapshot_digest"]
    for element, cue in zip(segments, cues):
        locator = element.locators[0]
        assert locator.status.value == "available"
        assert locator.cue_index == cue[0]
        assert locator.start_ms == cue[1]
        assert locator.end_ms == cue[2]
        assert locator.video_identity.status.value == "unavailable"
        assert locator.caption_track_identity.status.value == "unavailable"
    assert all(locator.status.value == "unavailable" for heading in headings for locator in heading.locators)
    assert document.capabilities.typed_locators.status.value == "partial"


def test_c02_preserves_multi_speaker_order_threads_replies_and_embedded_code_quote() -> None:
    case = CASES["C02"]
    source = json.loads((case["fixture"] / "source.json").read_bytes())
    messages = source["messages"]
    assert len(messages) == 6
    assert [message["sequence"] for message in messages] == list(range(6))
    assert {message["speaker_id"] for message in messages} == {"speaker-alice", "speaker-bob", "speaker-chen"}
    assert {message["thread_id"] for message in messages} == {"c02-thread-main", "c02-thread-followup"}
    assert messages[1]["reply_to_message_id"] == messages[0]["message_id"]
    assert messages[4]["reply_to_message_id"] is None
    assert all(marker not in (case["fixture"] / "source.json").read_text(encoding="utf-8").lower() for marker in ("http://", "https://", "@", "password", "secret"))

    document = _document("C02")
    message_elements = [element for element in document.elements if element.kind.value == "message"]
    assert len(message_elements) == 6
    assert [element.locators[0].source_sequence for element in message_elements] == list(range(6))
    assert sum(element.kind.value == "quote" for element in document.elements) == 1
    assert sum(element.kind.value == "code_block" for element in document.elements) == 1
    code = next(element for element in document.elements if element.kind.value == "code_block")
    quote = next(element for element in document.elements if element.kind.value == "quote")
    assert code.parent_element_id == "c02-message-003-element"
    assert quote.parent_element_id == "c02-message-002-element"
    assert code.code_metadata is not None and code.code_metadata.language_hint == "python"
    assert all("/" in element.content for element in message_elements)
    for message, element in zip(messages, message_elements):
        locator = element.locators[0]
        assert locator.message_id == message["message_id"]
        assert locator.thread_id == message["thread_id"]
        assert locator.reply_to_message_id == message["reply_to_message_id"]
    assert document.source.source_snapshot_sha256 == case["source_digest"]


def test_s02_has_ordered_bilingual_images_bounded_geometry_and_overlap_evidence() -> None:
    case = CASES["S02"]
    manifest_path = case["fixture"] / "source_manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    assert manifest["offline"] is True
    assert [image["image_index"] for image in manifest["images"]] == [1, 2]
    assert manifest["shared_content"] == ["共同內容 / Shared Content"]
    for image in manifest["images"]:
        image_path = case["fixture"] / image["path"]
        image_bytes = image_path.read_bytes()
        assert image_bytes[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">II", image_bytes[16:24]) == (640, 360)
        assert hashlib.sha256(image_bytes).hexdigest() == image["sha256"]

    document = _document("S02")
    assert document.source.languages == ("zh-Hant", "en")
    assert document.source.source_snapshot_sha256 == case["source_manifest_digest"]
    assert [element.locators[0].image_index for element in document.elements] == [1, 1, 1, 2, 2, 2]
    assert [element.order for element in document.elements] == list(range(6))
    assert document.capabilities.geometry.status.value == "available"
    shared = [element for element in document.elements if element.content == "共同內容 / Shared Content"]
    assert [element.locators[0].image_index for element in shared] == [1, 2]

    by_image: dict[int, list[Any]] = {1: [], 2: []}
    for element in document.elements:
        locator = element.locators[0]
        assert locator.image_sha256 == case[f"image_{locator.image_index:03d}_digest"]
        geometry = locator.region
        assert geometry is not None
        assert geometry.x + geometry.width <= 1_000_000
        assert geometry.y + geometry.height <= 1_000_000
        by_image[locator.image_index].append(geometry)

    def overlaps(first: Any, second: Any) -> bool:
        return (
            max(first.x, second.x) < min(first.x + first.width, second.x + second.width)
            and max(first.y, second.y) < min(first.y + first.height, second.y + second.height)
        )

    assert all(any(overlaps(first, second) for index, first in enumerate(regions) for second in regions[index + 1:]) for regions in by_image.values())


def test_y02_c02_s02_builders_are_deterministic_and_offline_only(tmp_path: Path) -> None:
    y02_source = _load_module("Y02", "build_source")
    y02_reference = _load_module("Y02", "build_reference")
    y02_copy = tmp_path / "y02"
    y02_source.build_artifacts(y02_copy)
    for filename in ("captions.vtt", "captions.sha256", "chapters.json", "chapters.sha256", "source_snapshot.json", "source_snapshot.sha256"):
        assert (y02_copy / filename).read_bytes() == (CASES["Y02"]["fixture"] / filename).read_bytes()
    assert canonical_normalized_document_bytes(y02_reference.build_document()) == (CASES["Y02"]["reference"] / "normalized_document.json").read_bytes()

    c02_source = _load_module("C02", "build_source")
    c02_reference = _load_module("C02", "build_reference")
    assert c02_source.build_source_bytes() == (CASES["C02"]["fixture"] / "source.json").read_bytes()
    assert canonical_normalized_document_bytes(c02_reference.build_document()) == (CASES["C02"]["reference"] / "normalized_document.json").read_bytes()

    s02_source = _load_module("S02", "build_source")
    s02_reference = _load_module("S02", "build_reference")
    s02_copy = tmp_path / "s02"
    s02_source.build_artifacts(s02_copy)
    for filename in (
        "source-001.png",
        "source-001.sha256",
        "source-002.png",
        "source-002.sha256",
        "source_manifest.json",
        "source.sha256",
    ):
        assert (s02_copy / filename).read_bytes() == (CASES["S02"]["fixture"] / filename).read_bytes()
    assert canonical_normalized_document_bytes(s02_reference.build_document()) == (CASES["S02"]["reference"] / "normalized_document.json").read_bytes()


def test_s02_controlled_font_is_fail_closed_and_cwd_independent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = CASES["S02"]
    source_module = _load_module("S02", "build_source")
    source_text = (case["fixture"] / "build_source.py").read_text(encoding="utf-8")
    assert "Hiragino" not in source_text
    assert "/System/Library/Fonts" not in source_text
    assert hashlib.sha256(source_module.FONT_PATH.read_bytes()).hexdigest() == source_module.FONT_SHA256

    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    monkeypatch.chdir(tmp_path)
    source_module.build_artifacts(first_dir)
    source_module.build_artifacts(second_dir)
    for filename in (
        "source-001.png",
        "source-001.sha256",
        "source-002.png",
        "source-002.sha256",
        "source_manifest.json",
        "source.sha256",
    ):
        assert (first_dir / filename).read_bytes() == (second_dir / filename).read_bytes()

    monkeypatch.setattr(source_module, "FONT_PATH", tmp_path / "missing.otf")
    with pytest.raises(RuntimeError, match="font is unavailable"):
        source_module.build_artifacts(tmp_path / "missing")

    monkeypatch.setattr(source_module, "FONT_PATH", case["fixture"] / "source_manifest.json")
    with pytest.raises(RuntimeError, match="font digest mismatch"):
        source_module.build_artifacts(tmp_path / "wrong")

    forbidden_imports = {"requests", "urllib", "urllib3", "httpx", "playwright", "selenium", "yt_dlp", "pytube"}
    for case_id in CASES:
        for filename in ("build_source.py", "build_reference.py"):
            path = CASES[case_id]["fixture"] / filename
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imported = {
                alias.name.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            assert imported.isdisjoint(forbidden_imports)
            source_text = path.read_text(encoding="utf-8").lower()
            assert "http://" not in source_text and "https://" not in source_text


def test_y02_c02_s02_candidates_remain_draft_and_non_authoritative() -> None:
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
