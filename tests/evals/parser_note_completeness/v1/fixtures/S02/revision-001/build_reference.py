"""Build the canonical-serialization reference document for S02."""

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
FIXTURE = ROOT / "fixtures" / "S02" / "revision-001"
GOVERNANCE = ROOT / "governance" / "S02" / "revision-001"
REFERENCE = ROOT / "reference_documents" / "S02" / "revision-001"
LANGUAGES = ("zh-Hant", "en")

REGIONS: tuple[tuple[int, int, int, int], ...] = (
    (62500, 66667, 625000, 122223),
    (112500, 350000, 562500, 161111),
    (593750, 311111, 281250, 155556),
    (62500, 66667, 625000, 122223),
    (131250, 366667, 562500, 161111),
    (612500, 322222, 281250, 155556),
)

CONTENTS = (
    "畫面一 / Screen One",
    "共同內容 / Shared Content",
    "重疊標籤 / Overlay Badge",
    "畫面二 / Screen Two",
    "共同內容 / Shared Content",
    "後續狀態 / Follow-up State",
)


def _locator(image_index: int, image_digest: str, region: tuple[int, int, int, int]) -> dict[str, Any]:
    x, y, width, height = region
    return {
        "locator_type": "screenshots",
        "status": "available",
        "reason": None,
        "image_index": image_index,
        "image_sha256": image_digest,
        "region": {
            "coordinate_space": "normalized_top_left_0_1000000",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        },
        "text_span": None,
    }


def build_document() -> NormalizedDocument:
    manifest_path = FIXTURE / "source_manifest.json"
    manifest_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    configuration_digest = hashlib.sha256(
        (GOVERNANCE / "producer_configuration.json").read_bytes()
    ).hexdigest()
    manifest = json.loads(manifest_path.read_bytes())
    image_digests = {
        image["image_index"]: image["sha256"] for image in manifest["images"]
    }
    elements: list[dict[str, Any]] = []
    for order, (content, region) in enumerate(zip(CONTENTS, REGIONS)):
        image_index = 1 if order < 3 else 2
        section_id = f"s02-image-{image_index}"
        elements.append(
            {
                "element_id": f"s02-element-{order}",
                "kind": "ui_text",
                "order": order,
                "section_id": section_id,
                "parent_element_id": None,
                "content": content,
                "languages": list(LANGUAGES),
                "locators": [_locator(image_index, image_digests[image_index], region)],
                "list_metadata": None,
                "table_cell_metadata": None,
                "code_metadata": None,
            }
        )

    return NormalizedDocument.model_validate(
        {
            "schema_version": "normalized-document/1.0.0",
            "artifact_role": "reference_document",
            "document_id": "S02",
            "source": {
                "source_type": "screenshots",
                "source_identity": "s02-synthetic-screenshot-set-revision-001",
                "display_name": "S02 Bilingual Screenshot Set",
                "source_snapshot_sha256": manifest_digest,
                "languages": list(LANGUAGES),
            },
            "capabilities": {
                "hierarchy": {"status": "partial", "reason": "image_order_only"},
                "language_identification": {"status": "available", "reason": None},
                "geometry": {"status": "available", "reason": None},
                "table_structure": {"status": "not_applicable", "reason": None},
                "code_metadata": {"status": "not_applicable", "reason": None},
                "source_modality": {"status": "available", "reason": None},
                "typed_locators": {"status": "available", "reason": None},
            },
            "sections": [
                {
                    "section_id": "s02-image-1",
                    "parent_section_id": None,
                    "heading_element_id": None,
                    "start_order": 0,
                    "end_order": 2,
                },
                {
                    "section_id": "s02-image-2",
                    "parent_section_id": None,
                    "heading_element_id": None,
                    "start_order": 3,
                    "end_order": 5,
                },
            ],
            "elements": elements,
            "producer_provenance": {
                "producer_name": "learnloop-project-authored-reference",
                "producer_version": "1.0.0",
                "configuration_sha256": configuration_digest,
                "segmentation_semantics": "png-multi-image-text-regions-v1",
                "processing_method": "project_authored_deterministic_screenshot_set",
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
