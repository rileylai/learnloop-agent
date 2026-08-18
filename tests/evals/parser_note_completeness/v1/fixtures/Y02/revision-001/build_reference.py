"""Build the canonical-serialization reference document for Y02."""

from __future__ import annotations

import hashlib
import re
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
FIXTURE = ROOT / "fixtures" / "Y02" / "revision-001"
GOVERNANCE = ROOT / "governance" / "Y02" / "revision-001"
REFERENCE = ROOT / "reference_documents" / "Y02" / "revision-001"
LANGUAGES = ("zh-Hant", "en")
TIMESTAMP = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.(\d{3})$")


def _read_digest(path: Path) -> str:
    fields = path.read_text(encoding="ascii").strip().split()
    if len(fields) != 2:
        raise ValueError(f"invalid digest record: {path}")
    return fields[0]


def _to_ms(timestamp: str) -> int:
    match = TIMESTAMP.fullmatch(timestamp)
    if match is None:
        raise ValueError(f"invalid timestamp: {timestamp}")
    hours, minutes, seconds, millis = (int(part) for part in match.groups())
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


def _cues() -> list[tuple[int, int, int, str]]:
    lines = (FIXTURE / "captions.vtt").read_text(encoding="utf-8").splitlines()
    if lines[0] != "WEBVTT":
        raise ValueError("captions must begin with WEBVTT")
    cues: list[tuple[int, int, int, str]] = []
    cursor = 1
    while cursor < len(lines):
        if not lines[cursor].strip():
            cursor += 1
            continue
        start, end = (part.strip() for part in lines[cursor].split("-->"))
        cues.append((len(cues), _to_ms(start), _to_ms(end), lines[cursor + 1]))
        cursor += 2
    return cues


def _identity() -> dict[str, Any]:
    return {
        "status": "unavailable",
        "value": None,
        "reason": "synthetic_platform_identity_unavailable",
    }


def _cue_locator(cue_index: int, start_ms: int, end_ms: int) -> dict[str, Any]:
    return {
        "locator_type": "youtube",
        "status": "available",
        "reason": None,
        "video_identity": _identity(),
        "caption_track_identity": _identity(),
        "cue_index": cue_index,
        "start_ms": start_ms,
        "end_ms": end_ms,
    }


def _unavailable_chapter_locator() -> dict[str, Any]:
    return {
        "locator_type": "youtube",
        "status": "unavailable",
        "reason": "chapter_title_locator_unavailable",
        "video_identity": None,
        "caption_track_identity": None,
        "cue_index": None,
        "start_ms": None,
        "end_ms": None,
    }


def _element(
    *,
    elements: list[dict[str, Any]],
    element_id: str,
    kind: str,
    section_id: str,
    content: str,
    locator: dict[str, Any],
) -> None:
    elements.append(
        {
            "element_id": element_id,
            "kind": kind,
            "order": len(elements),
            "section_id": section_id,
            "parent_element_id": None,
            "content": content,
            "languages": list(LANGUAGES),
            "locators": [locator],
            "list_metadata": None,
            "table_cell_metadata": None,
            "code_metadata": None,
        }
    )


def build_document() -> NormalizedDocument:
    snapshot_path = FIXTURE / "source_snapshot.json"
    snapshot_digest = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    configuration_digest = hashlib.sha256(
        (GOVERNANCE / "producer_configuration.json").read_bytes()
    ).hexdigest()
    chapters = __import__("json").loads((FIXTURE / "chapters.json").read_bytes())["chapters"]
    cues = _cues()
    elements: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []

    for chapter in chapters:
        section_id = chapter["chapter_id"]
        start_order = len(elements)
        _element(
            elements=elements,
            element_id=f"{section_id}-heading",
            kind="heading",
            section_id=section_id,
            content=chapter["title"],
            locator=_unavailable_chapter_locator(),
        )
        for cue_index in range(chapter["start_cue_index"], chapter["end_cue_index"] + 1):
            index, start_ms, end_ms, content = cues[cue_index]
            _element(
                elements=elements,
                element_id=f"{section_id}-cue-{index}",
                kind="transcript_segment",
                section_id=section_id,
                content=content,
                locator=_cue_locator(index, start_ms, end_ms),
            )
        sections.append(
            {
                "section_id": section_id,
                "parent_section_id": None,
                "heading_element_id": f"{section_id}-heading",
                "start_order": start_order,
                "end_order": len(elements) - 1,
            }
        )

    return NormalizedDocument.model_validate(
        {
            "schema_version": "normalized-document/1.0.0",
            "artifact_role": "reference_document",
            "document_id": "Y02",
            "source": {
                "source_type": "youtube",
                "source_identity": "y02-synthetic-youtube-caption-revision-001",
                "display_name": "離線字幕快照 / Offline Caption Snapshot",
                "source_snapshot_sha256": snapshot_digest,
                "languages": list(LANGUAGES),
            },
            "capabilities": {
                "hierarchy": {"status": "available", "reason": None},
                "language_identification": {"status": "available", "reason": None},
                "geometry": {"status": "unavailable", "reason": "not_captured"},
                "table_structure": {"status": "not_applicable", "reason": None},
                "code_metadata": {"status": "not_applicable", "reason": None},
                "source_modality": {"status": "available", "reason": None},
                "typed_locators": {"status": "partial", "reason": "chapter_title_locator_unavailable"},
            },
            "sections": sections,
            "elements": elements,
            "producer_provenance": {
                "producer_name": "learnloop-project-authored-reference",
                "producer_version": "1.0.0",
                "configuration_sha256": configuration_digest,
                "segmentation_semantics": "webvtt-bilingual-cues-and-manual-chapters-v1",
                "processing_method": "project_authored_offline_caption_snapshot",
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
