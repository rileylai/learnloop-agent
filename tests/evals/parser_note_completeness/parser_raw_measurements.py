"""Bounded raw Parser measurements for the frozen 13-case benchmark.

This module deliberately contains no quality thresholds, weighting, partial
credit, aggregate score, or fuzzy alignment.  It reports deterministic facts
only.  The case registry is closed over the current 13 fixtures; adding a case
or metric family requires a new reviewed contract revision.
"""

from __future__ import annotations

import hashlib
import json
from typing import Annotated, Any, Literal, Mapping, Optional, Sequence, Tuple

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, model_validator

from .normalized_document import (
    ArtifactRole,
    ChatLocator,
    Element,
    ElementKind,
    NormalizedDocument,
    NormalizedGeometry,
    ScreenshotLocator,
    YouTubeLocator,
    canonical_normalized_document_bytes,
)


RAW_MEASUREMENT_SCHEMA_VERSION = "parser-raw-measurements/1.0.0"
RAW_MEASUREMENT_REGISTRY_VERSION = "parser-raw-measurement-registry/1.0.0"
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]

MetricFamily = Literal[
    "text_extraction",
    "ocr_cer",
    "reading_order",
    "structure",
    "table",
    "formula",
    "code",
    "duplicate_noise",
    "locator_identity",
    "geometry",
    "caption_timing",
    "chat_identity",
]

FROZEN_CASE_METRICS: Mapping[str, Tuple[MetricFamily, ...]] = {
    "P01": ("text_extraction", "reading_order", "structure", "code", "duplicate_noise", "locator_identity"),
    "P02": ("text_extraction", "reading_order", "structure", "table", "duplicate_noise", "locator_identity"),
    "P03": ("text_extraction", "ocr_cer", "reading_order", "structure", "duplicate_noise", "locator_identity", "geometry"),
    "P04": ("text_extraction", "ocr_cer", "reading_order", "structure", "table", "formula", "duplicate_noise", "locator_identity", "geometry"),
    "W01": ("text_extraction", "reading_order", "structure", "code", "duplicate_noise", "locator_identity"),
    "W02": ("text_extraction", "reading_order", "structure", "table", "code", "duplicate_noise", "locator_identity"),
    "W03": ("text_extraction", "reading_order", "structure", "table", "duplicate_noise", "locator_identity"),
    "Y01": ("text_extraction", "reading_order", "structure", "duplicate_noise", "locator_identity", "caption_timing"),
    "Y02": ("text_extraction", "reading_order", "structure", "duplicate_noise", "locator_identity", "caption_timing"),
    "C01": ("text_extraction", "reading_order", "structure", "duplicate_noise", "locator_identity", "chat_identity"),
    "C02": ("text_extraction", "reading_order", "structure", "code", "duplicate_noise", "locator_identity", "chat_identity"),
    "S01": ("text_extraction", "ocr_cer", "reading_order", "structure", "duplicate_noise", "locator_identity", "geometry"),
    "S02": ("text_extraction", "ocr_cer", "reading_order", "structure", "duplicate_noise", "locator_identity", "geometry"),
}

_C02_SPEAKER_IDS = {
    "c02-message-001-element": "speaker-alice",
    "c02-message-002-element": "speaker-bob",
    "c02-message-003-element": "speaker-chen",
    "c02-message-004-element": "speaker-alice",
    "c02-message-005-element": "speaker-chen",
    "c02-message-006-element": "speaker-bob",
}


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class RawMeasurementFact(_StrictFrozenModel):
    metric_family: MetricFamily
    unit_id: StrictStr = Field(min_length=1)
    alignment: Literal["exact_element_id", "exact_typed_locator", "not_required", "unresolved"]
    disposition: Literal[
        "preserved",
        "different",
        "missing",
        "noise",
        "duplicate",
        "satisfied",
        "reversed",
        "correct",
        "conflicting",
        "fabricated",
        "unavailable",
        "empty_reference",
        "invalid_geometry",
        "unresolved",
    ]
    reference_value: Optional[StrictStr] = None
    candidate_value: Optional[StrictStr] = None
    edit_count: Optional[StrictInt] = Field(default=None, ge=0)
    reference_count: Optional[StrictInt] = Field(default=None, ge=0)
    intersection_area: Optional[StrictInt] = Field(default=None, ge=0)
    union_area: Optional[StrictInt] = Field(default=None, ge=0)
    iou_numerator: Optional[StrictInt] = Field(default=None, ge=0)
    iou_denominator: Optional[StrictInt] = Field(default=None, ge=1)
    start_delta_ms: Optional[StrictInt] = None
    end_delta_ms: Optional[StrictInt] = None
    duration_delta_ms: Optional[StrictInt] = None

    @model_validator(mode="after")
    def _keep_unresolved_value_free(self) -> "RawMeasurementFact":
        raw_values = (
            self.edit_count,
            self.reference_count,
            self.intersection_area,
            self.union_area,
            self.iou_numerator,
            self.iou_denominator,
            self.start_delta_ms,
            self.end_delta_ms,
            self.duration_delta_ms,
        )
        if self.disposition == "unresolved" and any(value is not None for value in raw_values):
            raise ValueError("unresolved alignment cannot carry a raw numeric value")
        return self


class RawMeasurementReport(_StrictFrozenModel):
    schema_version: Literal["parser-raw-measurements/1.0.0"] = RAW_MEASUREMENT_SCHEMA_VERSION
    registry_version: Literal["parser-raw-measurement-registry/1.0.0"] = RAW_MEASUREMENT_REGISTRY_VERSION
    artifact_type: Literal["parser_raw_measurement_report"] = "parser_raw_measurement_report"
    case_id: StrictStr = Field(min_length=1)
    reference_sha256: Digest
    candidate_sha256: Digest
    metric_families: Tuple[MetricFamily, ...]
    facts: Tuple[RawMeasurementFact, ...]
    unresolved_unit_ids: Tuple[StrictStr, ...]


def canonical_raw_measurement_bytes(
    payload: RawMeasurementReport | Mapping[str, Any],
) -> bytes:
    model = payload if isinstance(payload, RawMeasurementReport) else RawMeasurementReport.model_validate(payload)
    return (
        json.dumps(
            model.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def raw_measurement_sha256(payload: RawMeasurementReport | Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_raw_measurement_bytes(payload)).hexdigest()


def _project_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_char in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


def _locator_key(element: Element) -> str:
    payload = {
        "kind": element.kind.value,
        "locators": [locator.model_dump(mode="json") for locator in element.locators],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _align_elements(
    reference: NormalizedDocument,
    candidate: NormalizedDocument,
) -> tuple[dict[str, tuple[str, Optional[Element]]], set[str]]:
    candidate_by_id = {element.element_id: element for element in candidate.elements}
    candidate_by_locator: dict[str, list[Element]] = {}
    for element in candidate.elements:
        candidate_by_locator.setdefault(_locator_key(element), []).append(element)

    alignments: dict[str, tuple[str, Optional[Element]]] = {}
    used_candidate_ids: set[str] = set()
    for reference_element in reference.elements:
        exact_id = candidate_by_id.get(reference_element.element_id)
        if exact_id is not None:
            alignments[reference_element.element_id] = ("exact_element_id", exact_id)
            used_candidate_ids.add(exact_id.element_id)
            continue
        locator_matches = [
            element
            for element in candidate_by_locator.get(_locator_key(reference_element), [])
            if element.element_id not in used_candidate_ids
        ]
        if len(locator_matches) == 1:
            aligned = locator_matches[0]
            alignments[reference_element.element_id] = ("exact_typed_locator", aligned)
            used_candidate_ids.add(aligned.element_id)
        elif len(locator_matches) > 1:
            alignments[reference_element.element_id] = ("unresolved", None)
        else:
            alignments[reference_element.element_id] = ("not_required", None)
    return alignments, used_candidate_ids


def _unresolved_fact(family: MetricFamily, unit_id: str) -> RawMeasurementFact:
    return RawMeasurementFact(
        metric_family=family,
        unit_id=unit_id,
        alignment="unresolved",
        disposition="unresolved",
    )


def _missing_fact(family: MetricFamily, unit_id: str, reference_value: str | None = None) -> RawMeasurementFact:
    return RawMeasurementFact(
        metric_family=family,
        unit_id=unit_id,
        alignment="not_required",
        disposition="missing",
        reference_value=reference_value,
    )


def _text_fact(
    family: Literal["text_extraction", "ocr_cer", "formula", "code"],
    reference_element: Element,
    alignment: str,
    candidate_element: Optional[Element],
) -> RawMeasurementFact:
    if alignment == "unresolved":
        return _unresolved_fact(family, reference_element.element_id)
    reference_text = _project_text(reference_element.content or "")
    if candidate_element is None:
        return _missing_fact(family, reference_element.element_id, reference_text)
    candidate_text = _project_text(candidate_element.content or "")
    if not reference_text:
        return RawMeasurementFact(
            metric_family=family,
            unit_id=reference_element.element_id,
            alignment=alignment,
            disposition="empty_reference",
            reference_value=reference_text,
            candidate_value=candidate_text,
            edit_count=None,
            reference_count=0,
        )
    edit_count = _levenshtein(reference_text, candidate_text)
    return RawMeasurementFact(
        metric_family=family,
        unit_id=reference_element.element_id,
        alignment=alignment,
        disposition="preserved" if edit_count == 0 else "different",
        reference_value=reference_text,
        candidate_value=candidate_text,
        edit_count=edit_count,
        reference_count=len(reference_text),
    )


def _text_elements(document: NormalizedDocument) -> tuple[Element, ...]:
    return tuple(element for element in document.elements if element.content is not None)


def _geometry(element: Element) -> Optional[NormalizedGeometry]:
    for locator in element.locators:
        if hasattr(locator, "geometry") and locator.geometry is not None:
            return locator.geometry
        if isinstance(locator, ScreenshotLocator) and locator.region is not None:
            return locator.region
    return None


def _geometry_area(geometry: NormalizedGeometry) -> int:
    return geometry.width * geometry.height


def _geometry_intersection(left: NormalizedGeometry, right: NormalizedGeometry) -> int:
    width = max(0, min(left.x + left.width, right.x + right.width) - max(left.x, right.x))
    height = max(0, min(left.y + left.height, right.y + right.height) - max(left.y, right.y))
    return width * height


def _structure_value(element: Element) -> str:
    payload = {
        "kind": element.kind.value,
        "order": element.order,
        "section_id": element.section_id,
        "parent_element_id": element.parent_element_id,
        "list_metadata": element.list_metadata.model_dump(mode="json") if element.list_metadata else None,
        "table_cell_metadata": element.table_cell_metadata.model_dump(mode="json") if element.table_cell_metadata else None,
        "code_metadata": element.code_metadata.model_dump(mode="json") if element.code_metadata else None,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _comparison_fact(
    family: MetricFamily,
    unit_id: str,
    alignment: str,
    reference_value: str,
    candidate_value: Optional[str],
) -> RawMeasurementFact:
    if alignment == "unresolved":
        return _unresolved_fact(family, unit_id)
    if candidate_value is None:
        return _missing_fact(family, unit_id, reference_value)
    return RawMeasurementFact(
        metric_family=family,
        unit_id=unit_id,
        alignment=alignment,
        disposition="correct" if reference_value == candidate_value else "conflicting",
        reference_value=reference_value,
        candidate_value=candidate_value,
    )


def measure_parser_output(
    case_id: str,
    reference: NormalizedDocument,
    candidate: NormalizedDocument,
) -> RawMeasurementReport:
    """Measure one frozen case without making any quality decision."""

    if case_id not in FROZEN_CASE_METRICS:
        raise ValueError("case is outside the frozen 13-case measurement registry")
    if reference.artifact_role != ArtifactRole.REFERENCE_DOCUMENT:
        raise ValueError("reference must have reference_document artifact role")
    if candidate.artifact_role != ArtifactRole.PARSER_OUTPUT:
        raise ValueError("candidate must have parser_output artifact role")
    if reference.source.source_snapshot_sha256 != candidate.source.source_snapshot_sha256:
        raise ValueError("reference and candidate source digest identities differ")

    families = FROZEN_CASE_METRICS[case_id]
    alignments, used_candidate_ids = _align_elements(reference, candidate)
    reference_by_id = {element.element_id: element for element in reference.elements}
    facts: list[RawMeasurementFact] = []

    if "text_extraction" in families:
        for element in _text_elements(reference):
            alignment, aligned = alignments[element.element_id]
            facts.append(_text_fact("text_extraction", element, alignment, aligned))

    if "ocr_cer" in families:
        for element in _text_elements(reference):
            if _geometry(element) is None:
                continue
            alignment, aligned = alignments[element.element_id]
            facts.append(_text_fact("ocr_cer", element, alignment, aligned))

    if "reading_order" in families:
        for left, right in zip(reference.elements, reference.elements[1:]):
            unit_id = f"{left.element_id}->{right.element_id}"
            left_alignment, left_candidate = alignments[left.element_id]
            right_alignment, right_candidate = alignments[right.element_id]
            if "unresolved" in {left_alignment, right_alignment}:
                facts.append(_unresolved_fact("reading_order", unit_id))
            elif left_candidate is None or right_candidate is None:
                facts.append(_missing_fact("reading_order", unit_id))
            else:
                facts.append(
                    RawMeasurementFact(
                        metric_family="reading_order",
                        unit_id=unit_id,
                        alignment="exact_element_id" if left_alignment == right_alignment == "exact_element_id" else "exact_typed_locator",
                        disposition="satisfied" if left_candidate.order < right_candidate.order else "reversed",
                    )
                )

    if "structure" in families:
        for element in reference.elements:
            alignment, aligned = alignments[element.element_id]
            facts.append(
                _comparison_fact(
                    "structure",
                    element.element_id,
                    alignment,
                    _structure_value(element),
                    _structure_value(aligned) if aligned is not None else None,
                )
            )

    if "table" in families:
        for element in reference.elements:
            if element.kind != ElementKind.TABLE_CELL:
                continue
            alignment, aligned = alignments[element.element_id]
            reference_value = json.dumps(
                {
                    "content": _project_text(element.content or ""),
                    "metadata": element.table_cell_metadata.model_dump(mode="json") if element.table_cell_metadata else None,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            candidate_value = None
            if aligned is not None:
                candidate_value = json.dumps(
                    {
                        "content": _project_text(aligned.content or ""),
                        "metadata": aligned.table_cell_metadata.model_dump(mode="json") if aligned.table_cell_metadata else None,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            facts.append(_comparison_fact("table", element.element_id, alignment, reference_value, candidate_value))

    for family, kind in (("formula", ElementKind.FORMULA), ("code", ElementKind.CODE_BLOCK)):
        if family not in families:
            continue
        for element in reference.elements:
            if element.kind == kind:
                alignment, aligned = alignments[element.element_id]
                facts.append(_text_fact(family, element, alignment, aligned))

    if "duplicate_noise" in families:
        reference_locator_text = {
            (_locator_key(element), _project_text(element.content or ""))
            for element in reference.elements
            if element.content is not None
        }
        for element in candidate.elements:
            if element.element_id in used_candidate_ids or not (element.content or "").strip():
                continue
            disposition = (
                "duplicate"
                if (_locator_key(element), _project_text(element.content or "")) in reference_locator_text
                else "noise"
            )
            facts.append(
                RawMeasurementFact(
                    metric_family="duplicate_noise",
                    unit_id=element.element_id,
                    alignment="not_required",
                    disposition=disposition,
                    candidate_value=_project_text(element.content or ""),
                )
            )

    if "locator_identity" in families:
        for element in reference.elements:
            alignment, aligned = alignments[element.element_id]
            reference_value = json.dumps([locator.model_dump(mode="json") for locator in element.locators], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            candidate_value = None if aligned is None else json.dumps([locator.model_dump(mode="json") for locator in aligned.locators], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            facts.append(_comparison_fact("locator_identity", element.element_id, alignment, reference_value, candidate_value))

    if "geometry" in families:
        for element in reference.elements:
            reference_geometry = _geometry(element)
            if reference_geometry is None:
                continue
            alignment, aligned = alignments[element.element_id]
            if alignment == "unresolved":
                facts.append(_unresolved_fact("geometry", element.element_id))
                continue
            candidate_geometry = _geometry(aligned) if aligned is not None else None
            if candidate_geometry is None:
                facts.append(_missing_fact("geometry", element.element_id))
                continue
            intersection = _geometry_intersection(reference_geometry, candidate_geometry)
            union = _geometry_area(reference_geometry) + _geometry_area(candidate_geometry) - intersection
            if union <= 0:
                facts.append(
                    RawMeasurementFact(
                        metric_family="geometry",
                        unit_id=element.element_id,
                        alignment=alignment,
                        disposition="invalid_geometry",
                    )
                )
                continue
            facts.append(
                RawMeasurementFact(
                    metric_family="geometry",
                    unit_id=element.element_id,
                    alignment=alignment,
                    disposition="correct" if reference_geometry == candidate_geometry else "different",
                    intersection_area=intersection,
                    union_area=union,
                    iou_numerator=intersection,
                    iou_denominator=union,
                )
            )

    if "caption_timing" in families:
        for element in reference.elements:
            reference_locator = next(
                (
                    locator
                    for locator in element.locators
                    if isinstance(locator, YouTubeLocator)
                    and locator.start_ms is not None
                    and locator.end_ms is not None
                ),
                None,
            )
            if reference_locator is None:
                continue
            alignment, aligned = alignments[element.element_id]
            if alignment == "unresolved":
                facts.append(_unresolved_fact("caption_timing", element.element_id))
                continue
            candidate_locator = None if aligned is None else next(
                (
                    locator
                    for locator in aligned.locators
                    if isinstance(locator, YouTubeLocator)
                    and locator.start_ms is not None
                    and locator.end_ms is not None
                ),
                None,
            )
            if candidate_locator is None or any(value is None for value in (reference_locator.start_ms, reference_locator.end_ms, candidate_locator.start_ms, candidate_locator.end_ms)):
                facts.append(_missing_fact("caption_timing", element.element_id))
                continue
            start_delta = candidate_locator.start_ms - reference_locator.start_ms
            end_delta = candidate_locator.end_ms - reference_locator.end_ms
            facts.append(
                RawMeasurementFact(
                    metric_family="caption_timing",
                    unit_id=element.element_id,
                    alignment=alignment,
                    disposition="correct" if start_delta == end_delta == 0 else "different",
                    start_delta_ms=start_delta,
                    end_delta_ms=end_delta,
                    duration_delta_ms=(candidate_locator.end_ms - candidate_locator.start_ms) - (reference_locator.end_ms - reference_locator.start_ms),
                )
            )

    if "chat_identity" in families:
        for element in reference.elements:
            if element.kind != ElementKind.MESSAGE:
                continue
            reference_locator = next((locator for locator in element.locators if isinstance(locator, ChatLocator)), None)
            if reference_locator is None:
                continue
            alignment, aligned = alignments[element.element_id]
            candidate_locator = None if aligned is None else next((locator for locator in aligned.locators if isinstance(locator, ChatLocator)), None)
            reference_value = json.dumps(reference_locator.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            candidate_value = None if candidate_locator is None else json.dumps(candidate_locator.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            facts.append(_comparison_fact("chat_identity", element.element_id, alignment, reference_value, candidate_value))
        if case_id == "C02":
            for element_id, speaker_id in _C02_SPEAKER_IDS.items():
                facts.append(
                    RawMeasurementFact(
                        metric_family="chat_identity",
                        unit_id=f"{element_id}.speaker_id",
                        alignment="not_required",
                        disposition="missing",
                        reference_value=speaker_id,
                        candidate_value=None,
                    )
                )

    unresolved = tuple(fact.unit_id for fact in facts if fact.disposition == "unresolved")
    return RawMeasurementReport(
        case_id=case_id,
        reference_sha256=hashlib.sha256(canonical_normalized_document_bytes(reference)).hexdigest(),
        candidate_sha256=hashlib.sha256(canonical_normalized_document_bytes(candidate)).hexdigest(),
        metric_families=families,
        facts=tuple(facts),
        unresolved_unit_ids=unresolved,
    )
