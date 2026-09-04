from __future__ import annotations

import json
from pathlib import Path

import pytest

from .normalized_document import ArtifactRole, NormalizedDocument
from .parser_raw_measurements import (
    FROZEN_CASE_METRICS,
    RawMeasurementReport,
    canonical_raw_measurement_bytes,
    measure_parser_output,
)


ROOT = Path(__file__).parent / "v1"
REVISIONS = {
    "P01": "revision-001",
    "P02": "revision-002",
    "P03": "revision-003",
    "P04": "revision-003",
    "W01": "revision-001",
    "W02": "revision-002",
    "W03": "revision-002",
    "Y01": "revision-001",
    "Y02": "revision-001",
    "C01": "revision-001",
    "C02": "revision-001",
    "S01": "revision-001",
    "S02": "revision-002",
}


def _reference(case_id: str) -> NormalizedDocument:
    path = (
        ROOT
        / "reference_documents"
        / case_id
        / REVISIONS[case_id]
        / "normalized_document.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    return NormalizedDocument.model_validate(payload)


def _candidate(reference: NormalizedDocument) -> NormalizedDocument:
    return reference.model_copy(update={"artifact_role": ArtifactRole.PARSER_OUTPUT})


def _fact(report: RawMeasurementReport, family: str, unit_id: str):
    return next(
        fact
        for fact in report.facts
        if fact.metric_family == family and fact.unit_id == unit_id
    )


def test_registry_is_exactly_the_frozen_thirteen_case_scope() -> None:
    assert tuple(FROZEN_CASE_METRICS) == tuple(REVISIONS)
    assert all("span_overlap" not in families for families in FROZEN_CASE_METRICS.values())
    assert all("wer" not in families for families in FROZEN_CASE_METRICS.values())
    assert all("asr" not in families for families in FROZEN_CASE_METRICS.values())


@pytest.mark.parametrize("case_id", tuple(REVISIONS))
def test_each_frozen_case_emits_only_its_declared_raw_families(case_id: str) -> None:
    reference = _reference(case_id)
    report = measure_parser_output(case_id, reference, _candidate(reference))

    assert report.metric_families == FROZEN_CASE_METRICS[case_id]
    assert {fact.metric_family for fact in report.facts} <= set(report.metric_families)
    assert report.facts
    assert report.unresolved_unit_ids == ()


def test_identical_p04_emits_raw_facts_without_score_or_threshold_fields() -> None:
    reference = _reference("P04")
    report = measure_parser_output("P04", reference, _candidate(reference))

    assert report.case_id == "P04"
    assert _fact(report, "formula", "p04-page-1-formula").disposition == "preserved"
    assert any(f.metric_family == "ocr_cer" for f in report.facts)
    assert any(f.metric_family == "geometry" for f in report.facts)
    payload = canonical_raw_measurement_bytes(report)
    for forbidden in (b"threshold", b"weight", b"partial_credit", b"global_score", b"macro", b"micro"):
        assert forbidden not in payload


def test_text_and_ocr_report_exact_edits_and_never_a_pass_decision() -> None:
    reference = _reference("S01")
    changed = _candidate(reference).model_copy(
        update={
            "elements": (
                reference.elements[0].model_copy(
                    update={"content": (reference.elements[0].content or "")[:-1]}
                ),
                *reference.elements[1:],
            )
        }
    )

    report = measure_parser_output("S01", reference, changed)
    text = _fact(report, "text_extraction", "s01-element-0")
    ocr = _fact(report, "ocr_cer", "s01-element-0")
    assert text.disposition == "different"
    assert text.edit_count == 1
    assert text.reference_count == len(reference.elements[0].content or "")
    assert ocr.disposition == "different"
    assert ocr.edit_count == 1
    assert ocr.reference_count == len(reference.elements[0].content or "")


def test_ambiguous_exact_locator_alignment_stays_unresolved() -> None:
    reference = _reference("S01")
    first = reference.elements[0]
    candidate = _candidate(reference).model_copy(
        update={
            "elements": (
                first.model_copy(update={"element_id": "candidate-a"}),
                reference.elements[1].model_copy(
                    update={"kind": first.kind, "locators": first.locators}
                ),
                reference.elements[2].model_copy(
                    update={"kind": first.kind, "locators": first.locators}
                ),
            )
        }
    )

    report = measure_parser_output("S01", reference, candidate)
    fact = _fact(report, "text_extraction", first.element_id)
    assert fact.alignment == "unresolved"
    assert fact.disposition == "unresolved"
    assert fact.edit_count is None
    assert fact.reference_count is None


def test_geometry_emits_integer_intersection_union_and_rational_iou() -> None:
    reference = _reference("S02")
    report = measure_parser_output("S02", reference, _candidate(reference))
    fact = _fact(report, "geometry", "s02-element-0")

    assert fact.disposition == "correct"
    assert fact.intersection_area == fact.union_area
    assert fact.iou_numerator == fact.iou_denominator
    assert fact.iou_denominator and fact.iou_denominator > 0


def test_youtube_timing_emits_signed_integer_deltas() -> None:
    reference = _reference("Y01")
    report = measure_parser_output("Y01", reference, _candidate(reference))
    timing = next(fact for fact in report.facts if fact.metric_family == "caption_timing")

    assert timing.start_delta_ms == 0
    assert timing.end_delta_ms == 0
    assert timing.duration_delta_ms == 0


def test_c02_speaker_identity_is_explicitly_missing_from_normalized_document() -> None:
    reference = _reference("C02")
    report = measure_parser_output("C02", reference, _candidate(reference))
    speaker_facts = [
        fact for fact in report.facts if fact.metric_family == "chat_identity" and ".speaker_id" in fact.unit_id
    ]

    assert len(speaker_facts) == 6
    assert {fact.disposition for fact in speaker_facts} == {"missing"}
    assert {fact.candidate_value for fact in speaker_facts} == {None}
