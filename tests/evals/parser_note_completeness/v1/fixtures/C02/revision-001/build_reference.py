"""Build the canonical-serialization reference document for C02."""

from __future__ import annotations

import hashlib
import json
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
FIXTURE = ROOT / "fixtures" / "C02" / "revision-001"
GOVERNANCE = ROOT / "governance" / "C02" / "revision-001"
REFERENCE = ROOT / "reference_documents" / "C02" / "revision-001"
LANGUAGES = ("zh-Hant", "en")


def _locator(message: dict[str, Any]) -> dict[str, Any]:
    return {
        "locator_type": "chat",
        "status": "available",
        "reason": None,
        "message_id": message["message_id"],
        "source_sequence": message["sequence"],
        "thread_id": message["thread_id"],
        "reply_to_message_id": message["reply_to_message_id"],
        "source_timestamp": None,
        "text_span": None,
    }


def _element(
    *,
    elements: list[dict[str, Any]],
    element_id: str,
    kind: str,
    section_id: str,
    content: str,
    locator: dict[str, Any],
    parent_element_id: str | None = None,
    languages: tuple[str, ...] = LANGUAGES,
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
            "locators": [locator],
            "list_metadata": None,
            "table_cell_metadata": None,
            "code_metadata": code_metadata,
        }
    )


def build_document() -> NormalizedDocument:
    source_path = FIXTURE / "source.json"
    source_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    configuration_digest = hashlib.sha256(
        (GOVERNANCE / "producer_configuration.json").read_bytes()
    ).hexdigest()
    source = json.loads(source_path.read_bytes())
    elements: list[dict[str, Any]] = []
    section_ranges: dict[str, list[int]] = {}

    for message in source["messages"]:
        section_id = message["thread_id"]
        section_ranges.setdefault(section_id, [len(elements), len(elements)])
        message_element_id = f"{message['message_id']}-element"
        message_content = f"[{message['speaker_name']}] {message['text']}"
        locator = _locator(message)
        _element(
            elements=elements,
            element_id=message_element_id,
            kind="message",
            section_id=section_id,
            content=message_content,
            locator=locator,
        )
        for part_index, part in enumerate(message["parts"]):
            if part["kind"] == "text":
                continue
            if part["kind"] == "quote":
                _element(
                    elements=elements,
                    element_id=f"{message['message_id']}-quote-{part_index}",
                    kind="quote",
                    section_id=section_id,
                    content=part["text"],
                    locator=locator,
                    parent_element_id=message_element_id,
                )
            elif part["kind"] == "code":
                _element(
                    elements=elements,
                    element_id=f"{message['message_id']}-code-{part_index}",
                    kind="code_block",
                    section_id=section_id,
                    content=part["text"],
                    locator=locator,
                    parent_element_id=message_element_id,
                    languages=("en",),
                    code_metadata={
                        "language_hint": part["language"],
                        "source_supplied": True,
                    },
                )
            else:
                raise ValueError(f"unsupported chat part: {part['kind']}")
        section_ranges[section_id][1] = len(elements) - 1

    sections = [
        {
            "section_id": section_id,
            "parent_section_id": None,
            "heading_element_id": None,
            "start_order": bounds[0],
            "end_order": bounds[1],
        }
        for section_id, bounds in section_ranges.items()
    ]
    return NormalizedDocument.model_validate(
        {
            "schema_version": "normalized-document/1.0.0",
            "artifact_role": "reference_document",
            "document_id": "C02",
            "source": {
                "source_type": "chat",
                "source_identity": source["conversation_id"],
                "display_name": "C02 Structured Multi-speaker Chat",
                "source_snapshot_sha256": source_digest,
                "languages": list(LANGUAGES),
            },
            "capabilities": {
                "hierarchy": {"status": "available", "reason": None},
                "language_identification": {"status": "available", "reason": None},
                "geometry": {"status": "unavailable", "reason": "not_captured"},
                "table_structure": {"status": "not_applicable", "reason": None},
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
                "segmentation_semantics": "message-records-with-embedded-quote-code-v1",
                "processing_method": "project_authored_structured_chat",
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
