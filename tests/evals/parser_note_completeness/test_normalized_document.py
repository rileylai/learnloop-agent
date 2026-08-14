from __future__ import annotations

import copy
import json
from typing import Any, Dict, List

import pytest
from pydantic import ValidationError

from tests.evals.parser_note_completeness.normalized_document import (
    CAPABILITY_NAMES,
    ELEMENT_KINDS,
    NormalizedDocument,
    canonical_normalized_document_bytes,
    normalized_document_sha256,
)

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64

EXPECTED_ELEMENT_KINDS = (
    "heading",
    "paragraph",
    "list_item",
    "quote",
    "code_block",
    "table",
    "table_row",
    "table_cell",
    "figure",
    "caption",
    "formula",
    "transcript_segment",
    "message",
    "ui_text",
    "page_break",
    "unknown",
)
EXPECTED_SOURCE_TYPES = ("pdf", "web", "youtube", "chat", "screenshots")


def _available_locator(source_type: str) -> Dict[str, Any]:
    locators = {
        "pdf": {
            "locator_type": "pdf",
            "status": "available",
            "page": 1,
        },
        "web": {
            "locator_type": "web",
            "status": "available",
            "snapshot_sha256": SHA_C,
            "dom_path": "html/body/main/p[1]",
        },
        "youtube": {
            "locator_type": "youtube",
            "status": "available",
            "video_identity": {"status": "available", "value": "video-1"},
            "caption_track_identity": {
                "status": "available",
                "value": "track-en",
            },
            "cue_index": 0,
            "start_ms": 100,
            "end_ms": 500,
        },
        "chat": {
            "locator_type": "chat",
            "status": "available",
            "message_id": "message-1",
            "source_sequence": 0,
        },
        "screenshots": {
            "locator_type": "screenshots",
            "status": "available",
            "image_index": 1,
            "image_sha256": SHA_C,
        },
    }
    return copy.deepcopy(locators[source_type])


def _unavailable_locator(source_type: str) -> Dict[str, Any]:
    return {
        "locator_type": source_type,
        "status": "unavailable",
        "reason": "parser_did_not_emit_locator",
    }


def _capabilities() -> Dict[str, Any]:
    return {name: {"status": "available"} for name in CAPABILITY_NAMES}


def _element(
    order: int,
    *,
    kind: str = "paragraph",
    section_id: str = "section-0",
    parent_element_id: str | None = None,
    source_type: str = "pdf",
) -> Dict[str, Any]:
    content = None if kind in {"table", "table_row", "figure", "page_break"} else kind
    element: Dict[str, Any] = {
        "element_id": f"element-{order}",
        "kind": kind,
        "order": order,
        "section_id": section_id,
        "parent_element_id": parent_element_id,
        "content": content,
        "languages": ["en"],
        "locators": [_available_locator(source_type)],
        "list_metadata": None,
        "table_cell_metadata": None,
        "code_metadata": None,
    }
    if kind == "list_item":
        element["list_metadata"] = {
            "list_kind": "ordered",
            "nesting_level": 0,
            "ordinal": 1,
        }
    if kind == "table_cell":
        element["table_cell_metadata"] = {
            "row_index": 0,
            "column_index": 0,
            "row_span": 1,
            "column_span": 1,
            "header_role": "column",
        }
    if kind == "code_block":
        element["code_metadata"] = {
            "language_hint": "python",
            "source_supplied": True,
        }
    return element


def _minimal_payload(
    *,
    source_type: str = "pdf",
    artifact_role: str = "parser_output",
) -> Dict[str, Any]:
    return {
        "schema_version": "normalized-document/1.0.0",
        "artifact_role": artifact_role,
        "document_id": "P01",
        "source": {
            "source_type": source_type,
            "source_identity": "source-1",
            "display_name": "Source One",
            "source_snapshot_sha256": SHA_A,
            "languages": ["en", "zh-Hant"],
        },
        "capabilities": _capabilities(),
        "sections": [
            {
                "section_id": "section-0",
                "parent_section_id": None,
                "heading_element_id": None,
                "start_order": 0,
                "end_order": 0,
            }
        ],
        "elements": [_element(0, source_type=source_type)],
        "producer_provenance": {
            "producer_name": "fixture-parser",
            "producer_version": "1.0.0",
            "configuration_sha256": SHA_B,
            "segmentation_semantics": "fixture-segmentation/1",
            "processing_method": "native_parser",
            "processing_stage": "parse",
            "parser_model": None,
            "ocr_model": None,
            "asr_model": None,
        },
    }


def _set_elements(payload: Dict[str, Any], elements: List[Dict[str, Any]]) -> None:
    payload["elements"] = elements
    payload["sections"][0]["start_order"] = 0
    payload["sections"][0]["end_order"] = len(elements) - 1


def test_minimal_document_round_trip_uses_immutable_json_arrays() -> None:
    payload = _minimal_payload()

    document = NormalizedDocument.model_validate(payload)
    dumped = document.model_dump(mode="json")

    assert NormalizedDocument.model_validate(dumped) == document
    assert json.loads(canonical_normalized_document_bytes(document)) == dumped
    assert isinstance(document.source.languages, tuple)
    assert isinstance(document.sections, tuple)
    assert isinstance(document.elements, tuple)
    assert isinstance(document.elements[0].locators, tuple)


@pytest.mark.parametrize("artifact_role", ["parser_output", "reference_document"])
def test_artifact_roles_validate(artifact_role: str) -> None:
    document = NormalizedDocument.model_validate(
        _minimal_payload(artifact_role=artifact_role)
    )

    assert document.artifact_role.value == artifact_role


def test_unknown_artifact_role_is_rejected() -> None:
    payload = _minimal_payload()
    payload["artifact_role"] = "gold"

    with pytest.raises(ValidationError):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("source_type", EXPECTED_SOURCE_TYPES)
def test_exact_source_type_enum_and_locator_family(source_type: str) -> None:
    document = NormalizedDocument.model_validate(
        _minimal_payload(source_type=source_type)
    )

    assert document.source.source_type.value == source_type


@pytest.mark.parametrize("source_type", ["screenshot", "url", "captions"])
def test_unknown_or_legacy_source_type_is_rejected(source_type: str) -> None:
    payload = _minimal_payload()
    payload["source"]["source_type"] = source_type

    with pytest.raises(ValidationError):
        NormalizedDocument.model_validate(payload)


def test_closed_element_kind_enum_is_exact() -> None:
    assert ELEMENT_KINDS == EXPECTED_ELEMENT_KINDS
    assert "row" not in ELEMENT_KINDS
    assert "cell" not in ELEMENT_KINDS


def test_all_closed_element_kinds_validate_and_appear_in_json_schema() -> None:
    payload = _minimal_payload()
    elements = [
        _element(index, kind=kind)
        for index, kind in enumerate(EXPECTED_ELEMENT_KINDS)
    ]
    table_index = EXPECTED_ELEMENT_KINDS.index("table")
    row_index = EXPECTED_ELEMENT_KINDS.index("table_row")
    cell_index = EXPECTED_ELEMENT_KINDS.index("table_cell")
    elements[row_index]["parent_element_id"] = f"element-{table_index}"
    elements[cell_index]["parent_element_id"] = f"element-{row_index}"
    _set_elements(payload, elements)
    payload["sections"][0]["heading_element_id"] = "element-0"

    document = NormalizedDocument.model_validate(payload)
    schema = NormalizedDocument.model_json_schema()

    assert tuple(element.kind.value for element in document.elements) == ELEMENT_KINDS
    assert tuple(schema["$defs"]["ElementKind"]["enum"]) == ELEMENT_KINDS


def test_language_order_is_preserved_and_und_is_allowed() -> None:
    payload = _minimal_payload()
    payload["source"]["languages"] = ["zh-Hant", "en", "und"]
    payload["elements"][0]["languages"] = ["und"]

    document = NormalizedDocument.model_validate(payload)

    assert document.source.languages == ("zh-Hant", "en", "und")
    assert document.elements[0].languages == ("und",)


def test_element_languages_can_be_a_case_insensitive_source_subset() -> None:
    payload = _minimal_payload()
    payload["source"]["languages"] = ["en", "zh-Hant"]
    payload["elements"][0]["languages"] = ["EN"]

    document = NormalizedDocument.model_validate(payload)

    assert document.elements[0].languages == ("EN",)


@pytest.mark.parametrize("element_language", ["fr", "zh-Hant"])
def test_element_languages_cannot_add_undeclared_source_language(
    element_language: str,
) -> None:
    payload = _minimal_payload()
    payload["source"]["languages"] = ["und"]
    payload["elements"][0]["languages"] = [element_language]

    with pytest.raises(ValidationError, match="element languages"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("languages", [["en", "en"], ["en", "EN"]])
def test_duplicate_language_tags_are_rejected(languages: List[str]) -> None:
    payload = _minimal_payload()
    payload["source"]["languages"] = languages

    with pytest.raises(ValidationError, match="language tags must be deduplicated"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("languages", [["mixed"], ["en", "MIXED"], [" "]])
def test_mixed_or_blank_language_tags_are_rejected(languages: List[str]) -> None:
    payload = _minimal_payload()
    payload["source"]["languages"] = languages

    with pytest.raises(ValidationError):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize(
    ("status", "reason"),
    [
        ("available", None),
        ("partial", "some_pages_missing"),
        ("unavailable", "parser_did_not_emit"),
        ("not_applicable", None),
    ],
)
def test_capability_availability_statuses_validate(
    status: str,
    reason: str | None,
) -> None:
    payload = _minimal_payload()
    declaration: Dict[str, Any] = {"status": status}
    if reason is not None:
        declaration["reason"] = reason
    payload["capabilities"]["geometry"] = declaration

    document = NormalizedDocument.model_validate(payload)

    assert document.capabilities.geometry.status.value == status


@pytest.mark.parametrize("status", ["partial", "unavailable"])
def test_partial_and_unavailable_capabilities_require_reason(status: str) -> None:
    payload = _minimal_payload()
    payload["capabilities"]["geometry"] = {"status": status}

    with pytest.raises(ValidationError, match="reason is required"):
        NormalizedDocument.model_validate(payload)


def test_missing_required_capability_declaration_is_rejected() -> None:
    payload = _minimal_payload()
    payload["capabilities"].pop("source_modality")

    with pytest.raises(ValidationError):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("invalid_order", ["0", True, 0.0])
def test_order_rejects_scalar_coercion(invalid_order: Any) -> None:
    payload = _minimal_payload()
    payload["elements"][0]["order"] = invalid_order

    with pytest.raises(ValidationError):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("invalid_page", ["1", True, 1.0])
def test_pdf_page_rejects_scalar_coercion(invalid_page: Any) -> None:
    payload = _minimal_payload()
    payload["elements"][0]["locators"][0]["page"] = invalid_page

    with pytest.raises(ValidationError):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [("cue_index", "0"), ("cue_index", True), ("start_ms", "100"), ("end_ms", True)],
)
def test_youtube_integer_fields_reject_scalar_coercion(
    field_name: str,
    invalid_value: Any,
) -> None:
    payload = _minimal_payload(source_type="youtube")
    payload["elements"][0]["locators"][0][field_name] = invalid_value

    with pytest.raises(ValidationError):
        NormalizedDocument.model_validate(payload)


def test_youtube_real_platform_identities_with_cue_timestamps_validate() -> None:
    document = NormalizedDocument.model_validate(_minimal_payload(source_type="youtube"))

    locator = document.elements[0].locators[0]
    assert locator.video_identity.value == "video-1"
    assert locator.caption_track_identity.value == "track-en"
    assert locator.cue_index == 0


def test_youtube_synthetic_unavailable_identities_keep_cue_timestamps() -> None:
    payload = _minimal_payload(source_type="youtube")
    locator = payload["elements"][0]["locators"][0]
    locator["video_identity"] = {
        "status": "unavailable",
        "reason": "synthetic_fixture_no_video_identity",
    }
    locator["caption_track_identity"] = {
        "status": "unavailable",
        "reason": "synthetic_fixture_no_caption_track_identity",
    }

    document = NormalizedDocument.model_validate(payload)

    assert document.elements[0].locators[0].start_ms == 100
    assert document.elements[0].locators[0].end_ms == 500


@pytest.mark.parametrize(
    "identity",
    [
        {"status": "unavailable", "value": "invented", "reason": "not_real"},
        {"status": "available", "reason": "missing_value"},
    ],
)
def test_youtube_identity_record_requires_status_consistent_value(
    identity: Dict[str, Any],
) -> None:
    payload = _minimal_payload(source_type="youtube")
    payload["elements"][0]["locators"][0]["video_identity"] = identity

    with pytest.raises(ValidationError, match="identity"):
        NormalizedDocument.model_validate(payload)


def test_unavailable_youtube_locator_rejects_cue_and_timestamps() -> None:
    payload = _minimal_payload(source_type="youtube")
    payload["elements"][0]["locators"] = [
        {
            "locator_type": "youtube",
            "status": "unavailable",
            "reason": "parser_did_not_emit_locator",
            "cue_index": 0,
            "start_ms": 100,
            "end_ms": 500,
        }
    ]

    with pytest.raises(ValidationError, match="unavailable locator"):
        NormalizedDocument.model_validate(payload)


def test_youtube_start_must_not_follow_end() -> None:
    payload = _minimal_payload(source_type="youtube")
    locator = payload["elements"][0]["locators"][0]
    locator["start_ms"] = 501

    with pytest.raises(ValidationError, match="end_ms"):
        NormalizedDocument.model_validate(payload)


def test_boolean_field_rejects_string_coercion() -> None:
    payload = _minimal_payload()
    payload["elements"] = [_element(0, kind="code_block")]
    payload["elements"][0]["code_metadata"]["source_supplied"] = "false"

    with pytest.raises(ValidationError):
        NormalizedDocument.model_validate(payload)


def test_elements_array_must_match_global_order() -> None:
    payload = _minimal_payload()
    elements = [_element(0), _element(1)]
    _set_elements(payload, list(reversed(elements)))

    with pytest.raises(ValidationError, match="elements must be ordered"):
        NormalizedDocument.model_validate(payload)


def test_duplicate_element_id_is_rejected() -> None:
    payload = _minimal_payload()
    elements = [_element(0), _element(1)]
    elements[1]["element_id"] = elements[0]["element_id"]
    _set_elements(payload, elements)

    with pytest.raises(ValidationError, match="element IDs must be unique"):
        NormalizedDocument.model_validate(payload)


def test_duplicate_section_id_is_rejected() -> None:
    payload = _minimal_payload()
    payload["sections"].append(copy.deepcopy(payload["sections"][0]))

    with pytest.raises(ValidationError, match="section IDs must be unique"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("orders", [(0, 0), (0, 2), (1, 2)])
def test_invalid_global_order_is_rejected(orders: tuple[int, int]) -> None:
    payload = _minimal_payload()
    elements = [_element(0), _element(1)]
    for element, order in zip(elements, orders):
        element["order"] = order
    _set_elements(payload, elements)

    with pytest.raises(ValidationError, match="elements must be ordered"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize(
    "parents",
    [
        {"section-a": "section-b", "section-b": "section-a"},
        {
            "section-a": "section-b",
            "section-b": "section-c",
            "section-c": "section-a",
        },
    ],
)
def test_section_hierarchy_cycles_are_rejected(parents: Dict[str, str]) -> None:
    payload = _minimal_payload()
    payload["sections"] = [
        {
            "section_id": section_id,
            "parent_section_id": parent_id,
            "heading_element_id": None,
            "start_order": 0,
            "end_order": 0,
        }
        for section_id, parent_id in parents.items()
    ]
    payload["elements"][0]["section_id"] = next(iter(parents))

    with pytest.raises(ValidationError, match="section hierarchy must be acyclic"):
        NormalizedDocument.model_validate(payload)


def test_child_section_range_must_be_within_parent_range() -> None:
    payload = _minimal_payload()
    _set_elements(payload, [_element(0), _element(1, section_id="child")])
    payload["sections"] = [
        {
            "section_id": "parent",
            "parent_section_id": None,
            "heading_element_id": None,
            "start_order": 0,
            "end_order": 0,
        },
        {
            "section_id": "child",
            "parent_section_id": "parent",
            "heading_element_id": None,
            "start_order": 0,
            "end_order": 1,
        },
    ]
    payload["elements"][0]["section_id"] = "parent"

    with pytest.raises(ValidationError, match="child section range"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("failure", ["missing", "wrong_kind", "outside_range"])
def test_invalid_heading_element_reference_is_rejected(failure: str) -> None:
    payload = _minimal_payload()
    elements = [_element(0, kind="heading"), _element(1)]
    _set_elements(payload, elements)
    if failure == "missing":
        payload["sections"][0]["heading_element_id"] = "not-found"
    elif failure == "wrong_kind":
        payload["sections"][0]["heading_element_id"] = "element-1"
    else:
        payload["sections"] = [
            {
                "section_id": "root",
                "parent_section_id": None,
                "heading_element_id": None,
                "start_order": 0,
                "end_order": 1,
            },
            {
                "section_id": "child",
                "parent_section_id": "root",
                "heading_element_id": "element-0",
                "start_order": 1,
                "end_order": 1,
            },
        ]
        elements[0]["section_id"] = "root"
        elements[1]["section_id"] = "child"

    with pytest.raises(ValidationError, match="heading element"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("end_order", [0, 1])
def test_heading_must_belong_to_section_when_ranges_overlap(end_order: int) -> None:
    payload = _minimal_payload()
    elements = [_element(0, kind="heading", section_id="section-b")]
    if end_order == 1:
        elements.append(_element(1, section_id="section-a"))
    payload["elements"] = elements
    payload["sections"] = [
        {
            "section_id": "section-a",
            "parent_section_id": None,
            "heading_element_id": "element-0",
            "start_order": 0,
            "end_order": end_order,
        },
        {
            "section_id": "section-b",
            "parent_section_id": None,
            "heading_element_id": None,
            "start_order": 0,
            "end_order": end_order,
        },
    ]

    with pytest.raises(ValidationError, match="heading element must belong"):
        NormalizedDocument.model_validate(payload)


def test_parent_element_cycle_is_rejected() -> None:
    payload = _minimal_payload()
    elements = [
        _element(0, parent_element_id="element-1"),
        _element(1, parent_element_id="element-0"),
    ]
    _set_elements(payload, elements)

    with pytest.raises(ValidationError, match="element hierarchy must be acyclic"):
        NormalizedDocument.model_validate(payload)


def test_table_list_and_code_metadata_validate() -> None:
    payload = _minimal_payload()
    elements = [
        _element(0, kind="table"),
        _element(1, kind="table_row", parent_element_id="element-0"),
        _element(2, kind="table_cell", parent_element_id="element-1"),
        _element(3, kind="list_item"),
        _element(4, kind="code_block"),
        _element(5, kind="page_break"),
    ]
    _set_elements(payload, elements)

    document = NormalizedDocument.model_validate(payload)

    assert document.elements[2].table_cell_metadata.row_span == 1
    assert document.elements[3].list_metadata.nesting_level == 0
    assert document.elements[4].code_metadata.language_hint == "python"
    assert document.elements[5].content is None


def test_table_cell_without_position_metadata_is_valid() -> None:
    payload = _minimal_payload()
    elements = [
        _element(0, kind="table"),
        _element(1, kind="table_row", parent_element_id="element-0"),
        _element(2, kind="table_cell", parent_element_id="element-1"),
    ]
    elements[2]["table_cell_metadata"] = None
    _set_elements(payload, elements)

    document = NormalizedDocument.model_validate(payload)

    assert document.elements[2].table_cell_metadata is None


def test_table_cell_metadata_is_rejected_on_non_table_cell() -> None:
    payload = _minimal_payload()
    payload["elements"][0]["table_cell_metadata"] = {
        "row_index": 0,
        "column_index": 0,
    }

    with pytest.raises(ValidationError, match="allowed only for table_cell"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize(
    ("kind", "parent_kind", "error"),
    [
        ("table_row", "paragraph", "table_row parent must be table"),
        ("table_cell", "table", "table_cell parent must be table_row"),
    ],
)
def test_table_row_and_cell_require_correct_parent_kinds(
    kind: str,
    parent_kind: str,
    error: str,
) -> None:
    payload = _minimal_payload()
    elements = [
        _element(0, kind=parent_kind),
        _element(1, kind=kind, parent_element_id="element-0"),
    ]
    _set_elements(payload, elements)

    with pytest.raises(ValidationError, match=error):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("kind", ["table", "table_row"])
def test_table_and_row_reject_duplicated_descendant_text_field(kind: str) -> None:
    payload = _minimal_payload()
    element = _element(0, kind=kind)
    element["content"] = "duplicated cells"
    payload["elements"] = [element]

    with pytest.raises(ValidationError, match="must not carry content"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("content", [None, "", "   "])
def test_text_bearing_kinds_require_nonblank_content(content: str | None) -> None:
    payload = _minimal_payload()
    payload["elements"][0]["content"] = content

    with pytest.raises(ValidationError, match="text-bearing element"):
        NormalizedDocument.model_validate(payload)


def test_page_break_rejects_nonblank_content() -> None:
    payload = _minimal_payload()
    payload["elements"] = [_element(0, kind="page_break")]
    payload["elements"][0]["content"] = "unexpected page text"

    with pytest.raises(ValidationError, match="page_break"):
        NormalizedDocument.model_validate(payload)


def test_pdf_page_without_optional_geometry_validates() -> None:
    document = NormalizedDocument.model_validate(_minimal_payload())

    locator = document.elements[0].locators[0]
    assert locator.page == 1
    assert locator.geometry is None


@pytest.mark.parametrize("source_type", EXPECTED_SOURCE_TYPES)
def test_five_available_locator_identities_validate(source_type: str) -> None:
    document = NormalizedDocument.model_validate(
        _minimal_payload(source_type=source_type)
    )

    assert document.elements[0].locators[0].status.value == "available"


@pytest.mark.parametrize("source_type", EXPECTED_SOURCE_TYPES)
def test_five_typed_unavailable_locators_validate(source_type: str) -> None:
    payload = _minimal_payload(source_type=source_type)
    payload["elements"][0]["locators"] = [_unavailable_locator(source_type)]

    document = NormalizedDocument.model_validate(payload)

    assert document.elements[0].locators[0].status.value == "unavailable"


def test_unavailable_locator_requires_reason() -> None:
    payload = _minimal_payload()
    locator = _unavailable_locator("pdf")
    locator.pop("reason")
    payload["elements"][0]["locators"] = [locator]

    with pytest.raises(ValidationError, match="reason"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize(
    ("source_type", "identity_field", "identity_value"),
    [
        ("pdf", "page", 1),
        ("web", "dom_path", "html/body"),
        ("youtube", "cue_index", 0),
        ("chat", "message_id", "message-1"),
        ("screenshots", "image_index", 1),
    ],
)
def test_unavailable_locator_rejects_fabricated_identity(
    source_type: str,
    identity_field: str,
    identity_value: Any,
) -> None:
    payload = _minimal_payload(source_type=source_type)
    locator = _unavailable_locator(source_type)
    locator[identity_field] = identity_value
    payload["elements"][0]["locators"] = [locator]

    with pytest.raises(ValidationError, match="unavailable locator"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize(
    ("source_type", "required_field"),
    [
        ("pdf", "page"),
        ("web", "dom_path"),
        ("youtube", "caption_track_identity"),
        ("chat", "message_id"),
        ("screenshots", "image_sha256"),
    ],
)
def test_available_locator_requires_identity(
    source_type: str,
    required_field: str,
) -> None:
    payload = _minimal_payload(source_type=source_type)
    payload["elements"][0]["locators"][0].pop(required_field)

    with pytest.raises(ValidationError, match="available locator"):
        NormalizedDocument.model_validate(payload)


def _normalized_geometry() -> Dict[str, Any]:
    return {
        "coordinate_space": "normalized_top_left_0_1000000",
        "x": 900_000,
        "y": 800_000,
        "width": 100_000,
        "height": 200_000,
    }


def test_normalized_geometry_boundaries_validate() -> None:
    payload = _minimal_payload()
    payload["elements"][0]["locators"][0]["geometry"] = _normalized_geometry()

    document = NormalizedDocument.model_validate(payload)

    assert document.elements[0].locators[0].geometry.x == 900_000


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("x", -1),
        ("x", 1_000_001),
        ("x", 1.0),
        ("x", "1"),
        ("x", True),
        ("x", float("nan")),
        ("x", float("inf")),
        ("x", float("-inf")),
        ("width", 100_001),
    ],
)
def test_invalid_normalized_geometry_is_rejected(
    field_name: str,
    invalid_value: Any,
) -> None:
    payload = _minimal_payload()
    geometry = _normalized_geometry()
    geometry[field_name] = invalid_value
    payload["elements"][0]["locators"][0]["geometry"] = geometry

    with pytest.raises(ValidationError):
        NormalizedDocument.model_validate(payload)


def test_extra_field_is_rejected() -> None:
    payload = _minimal_payload()
    payload["source"]["unexpected"] = "not allowed"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize(
    "field_name",
    [
        "chunks",
        "embeddings",
        "retrieval_score",
        "top_k",
        "evidence_importance",
        "gold",
        "expected_claims",
        "execution_time_ms",
        "latency_ms",
        "cost",
        "hardware",
        "artifact_sha256",
    ],
)
def test_out_of_scope_artifact_fields_are_rejected(field_name: str) -> None:
    payload = _minimal_payload()
    payload[field_name] = "forbidden"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        NormalizedDocument.model_validate(payload)


@pytest.mark.parametrize("field_name", ["latency_ms", "cost", "hardware", "timestamp"])
def test_volatile_producer_provenance_is_rejected(field_name: str) -> None:
    payload = _minimal_payload()
    payload["producer_provenance"][field_name] = "forbidden"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        NormalizedDocument.model_validate(payload)


def test_canonical_json_sorts_keys_recursively_and_is_compact() -> None:
    payload = _minimal_payload()
    document = NormalizedDocument.model_validate(payload)
    canonical_payload = document.model_dump(mode="json")

    canonical = canonical_normalized_document_bytes(payload)

    assert canonical == (
        json.dumps(
            canonical_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    assert b'": "' not in canonical
    assert b'", "' not in canonical


def test_canonical_json_is_utf8_with_one_lf_terminator() -> None:
    payload = _minimal_payload()
    payload["elements"][0]["content"] = "臺灣 benchmark text"

    canonical = canonical_normalized_document_bytes(payload)

    assert "臺灣".encode("utf-8") in canonical
    assert b"\\u81fa" not in canonical
    assert canonical.endswith(b"\n")
    assert not canonical.endswith(b"\n\n")


def test_canonical_json_preserves_array_order() -> None:
    payload = _minimal_payload()
    first = _available_locator("pdf")
    second = _available_locator("pdf")
    first["page"] = 2
    second["page"] = 1
    payload["elements"][0]["locators"] = [first, second]

    decoded = json.loads(canonical_normalized_document_bytes(payload))

    assert [locator["page"] for locator in decoded["elements"][0]["locators"]] == [
        2,
        1,
    ]


def test_input_key_order_does_not_change_canonical_bytes_or_digest() -> None:
    payload = _minimal_payload()
    reordered = dict(reversed(tuple(payload.items())))

    assert canonical_normalized_document_bytes(payload) == (
        canonical_normalized_document_bytes(reordered)
    )
    assert normalized_document_sha256(payload) == normalized_document_sha256(reordered)


def test_artifact_payload_has_no_self_digest() -> None:
    document = NormalizedDocument.model_validate(_minimal_payload())
    schema = NormalizedDocument.model_json_schema()

    assert "artifact_sha256" not in document.model_dump(mode="json")
    assert "artifact_sha256" not in schema["properties"]
    assert schema["additionalProperties"] is False


def test_versioned_json_schema_is_derived_from_pydantic_model() -> None:
    schema = NormalizedDocument.model_json_schema()

    assert schema["$id"].endswith("/normalized-document/1.0.0")
    assert schema["properties"]["schema_version"]["const"] == (
        "normalized-document/1.0.0"
    )
    assert set(schema["properties"]) == {
        "schema_version",
        "artifact_role",
        "document_id",
        "source",
        "capabilities",
        "sections",
        "elements",
        "producer_provenance",
    }


def test_validation_failure_produces_no_canonical_bytes_or_digest() -> None:
    payload = _minimal_payload()
    payload["elements"][0]["locators"] = []

    for operation in (
        canonical_normalized_document_bytes,
        normalized_document_sha256,
    ):
        with pytest.raises(ValidationError):
            operation(payload)


def test_locator_variant_must_match_document_source_type() -> None:
    payload = _minimal_payload()
    payload["elements"][0]["locators"] = [_available_locator("web")]

    with pytest.raises(ValidationError, match="locator type must match"):
        NormalizedDocument.model_validate(payload)
