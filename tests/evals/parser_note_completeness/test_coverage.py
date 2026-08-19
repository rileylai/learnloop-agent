from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from .coverage import (
    COVERAGE_CLOSURE_SCHEMA_VERSION,
    COVERAGE_PLAN_SCHEMA_VERSION,
    WORK_UNIT_OUTPUT_SCHEMA_VERSION,
    CoverageClosure,
    CoverageClosureState,
    CoverageCondition,
    CoverageContractError,
    CoveragePlan,
    DependencyEdge,
    EdgeKind,
    ExternalOwnerRecordRef,
    Q26PreRenderNoteRef,
    ReferenceDocumentRef,
    RouteDecisionRef,
    RoutingPolicyRef,
    SourceSectionRef,
    SourceUnitRef,
    UnitOutcome,
    WorkUnitOutput,
    WorkUnitSpec,
    coverage_plan_sha256,
    canonical_coverage_plan_bytes,
    derive_work_unit_id,
    validate_coverage_closure,
    validate_coverage_plan,
    work_unit_output_sha256,
)
from .normalized_document import NormalizedDocument, normalized_document_sha256


_REFERENCE_PATH = (
    Path(__file__).parent
    / "v1"
    / "reference_documents"
    / "P01"
    / "revision-001"
    / "normalized_document.json"
)


def _reference() -> NormalizedDocument:
    return NormalizedDocument.model_validate(
        json.loads(_REFERENCE_PATH.read_text(encoding="utf-8"))
    )


def _plan() -> tuple[CoveragePlan, NormalizedDocument]:
    reference = _reference()
    reference_sha256 = normalized_document_sha256(reference)
    sections = tuple(
        SourceSectionRef(
            section_id=section.section_id,
            parent_section_id=section.parent_section_id,
            heading_element_id=section.heading_element_id,
            start_order=section.start_order,
            end_order=section.end_order,
        )
        for section in reference.sections
    )
    source_units = tuple(
        SourceUnitRef(
            reference_document_id=reference.document_id,
            section_id=element.section_id,
            element_id=element.element_id,
            order=element.order,
        )
        for element in reference.elements
    )
    groups = (
        tuple(element.element_id for element in reference.elements[:15]),
        tuple(element.element_id for element in reference.elements[15:30]),
        tuple(element.element_id for element in reference.elements[30:]),
    )
    route_sha256 = "c" * 64
    execution_sha256 = "d" * 64
    context = ((), (groups[0][-1],), (groups[1][-1],))
    work_units = tuple(
        WorkUnitSpec(
            work_unit_id=derive_work_unit_id(
                reference_document_sha256=reference_sha256,
                primary_source_unit_ids=primary,
                context_only_source_unit_ids=contexts,
                route_decision_sha256=route_sha256,
                execution_contract_sha256=execution_sha256,
            ),
            primary_source_unit_ids=primary,
            context_only_source_unit_ids=contexts,
        )
        for primary, contexts in zip(groups, context)
    )
    work_unit_ids = tuple(unit.work_unit_id for unit in work_units)
    edges = (
        DependencyEdge(
            predecessor_work_unit_id=work_unit_ids[0],
            successor_work_unit_id=work_unit_ids[1],
            edge_kind=EdgeKind.HIERARCHY,
        ),
        DependencyEdge(
            predecessor_work_unit_id=work_unit_ids[1],
            successor_work_unit_id=work_unit_ids[2],
            edge_kind=EdgeKind.EXECUTION_DEPENDENCY,
        ),
        DependencyEdge(
            predecessor_work_unit_id=work_unit_ids[0],
            successor_work_unit_id=work_unit_ids[2],
            edge_kind=EdgeKind.MERGE_DEPENDENCY,
        ),
    )
    plan = CoveragePlan(
        schema_version=COVERAGE_PLAN_SCHEMA_VERSION,
        artifact_role="coverage_plan",
        plan_id="p01-coverage",
        plan_revision="revision-001",
        reference_document=ReferenceDocumentRef(
            schema_version="normalized-document/1.0.0",
            artifact_role="reference_document",
            document_id=reference.document_id,
            sha256=reference_sha256,
        ),
        routing_policy=RoutingPolicyRef(
            schema_version="benchmark-generation-routing-policy/1.0.0",
            policy_id="q29-policy",
            policy_revision="revision-001",
            sha256="a" * 64,
            configuration_sha256="b" * 64,
        ),
        route_decision=RouteDecisionRef(
            schema_version="benchmark-generation-route-decision/1.0.0",
            artifact_role="route_decision",
            sha256=route_sha256,
        ),
        execution_contract={"contract_id": "execution-001", "sha256": execution_sha256},
        source_sections=sections,
        source_units=source_units,
        work_units=work_units,
        dependency_edges=edges,
        planned_execution_order=work_unit_ids,
        planned_merge_order=work_unit_ids,
    )
    return plan, reference


def _output(
    plan: CoveragePlan,
    work_unit_id: str,
    attempt_ordinal: int,
    condition: str,
) -> WorkUnitOutput:
    return WorkUnitOutput(
        schema_version=WORK_UNIT_OUTPUT_SCHEMA_VERSION,
        artifact_role="work_unit_output",
        coverage_plan_sha256=coverage_plan_sha256(plan),
        work_unit_id=work_unit_id,
        attempt_ordinal=attempt_ordinal,
        output_condition=condition,
        pre_render_note=None,
    )


def _receipt_ref(work_unit_id: str, attempt_ordinal: int) -> ExternalOwnerRecordRef:
    digest = hashlib.sha256(f"{work_unit_id}:{attempt_ordinal}".encode()).hexdigest()
    return ExternalOwnerRecordRef(
        schema_version="q15-receipt/1.0.0",
        sha256=digest,
        record_type="receipt",
        record_id=f"receipt-{work_unit_id[-8:]}-{attempt_ordinal}",
    )


def _closure(
    plan: CoveragePlan,
    reference: NormalizedDocument,
    *,
    condition: str = "complete",
    state: CoverageClosureState = CoverageClosureState.CLOSED,
    attempts_by_unit: dict[str, tuple[tuple[int, str], ...]] | None = None,
    observed_merge_order: tuple[str, ...] | None = None,
) -> tuple[CoverageClosure, dict[str, WorkUnitOutput], dict[str, dict[str, object]]]:
    outputs: dict[str, WorkUnitOutput] = {}
    owner_records: dict[str, dict[str, object]] = {}
    outcomes = []
    attempts_by_unit = attempts_by_unit or {
        unit.work_unit_id: ((1, condition),)
        for unit in plan.work_units
    }
    for unit in plan.work_units:
        bindings = []
        for ordinal, attempt_condition in attempts_by_unit[unit.work_unit_id]:
            output = _output(plan, unit.work_unit_id, ordinal, attempt_condition)
            output_digest = work_unit_output_sha256(output)
            outputs[output_digest] = output
            receipt_ref = _receipt_ref(unit.work_unit_id, ordinal)
            owner_records[receipt_ref.sha256] = {
                "schema_version": receipt_ref.schema_version,
                "record_type": receipt_ref.record_type,
                "record_id": receipt_ref.record_id,
                "plan_sha256": coverage_plan_sha256(plan),
                "work_unit_id": unit.work_unit_id,
                "attempt_ordinal": ordinal,
            }
            bindings.append(
                {
                    "attempt_ordinal": ordinal,
                    "output_sha256": output_digest,
                    "receipt_ref": receipt_ref,
                }
            )
        terminal = bindings[-1]["attempt_ordinal"] if state == CoverageClosureState.CLOSED else None
        outcomes.append(
            UnitOutcome(
                work_unit_id=unit.work_unit_id,
                attempts=tuple(bindings),
                terminal_attempt_ordinal=terminal,
                coverage_condition=condition,
            )
        )
    closure = CoverageClosure(
        schema_version=COVERAGE_CLOSURE_SCHEMA_VERSION,
        artifact_role="coverage_closure",
        coverage_closure_state=state,
        coverage_plan_sha256=coverage_plan_sha256(plan),
        unit_outcomes=tuple(outcomes),
        observed_merge_order=(
            plan.planned_merge_order
            if observed_merge_order is None
            else observed_merge_order
        ),
        final_pre_render_note=Q26PreRenderNoteRef(
            schema_version="benchmark-note-document/1.0.0",
            artifact_role="pre_render_note",
            document_id=reference.document_id,
            reference_document_sha256=normalized_document_sha256(reference),
            sha256="e" * 64,
        ),
        source_reference_mappings=(),
        observations=(),
    )
    return closure, outputs, owner_records


def test_work_unit_identity_is_repeatedly_byte_identical() -> None:
    arguments = {
        "reference_document_sha256": "a" * 64,
        "primary_source_unit_ids": ("element-1", "element-2"),
        "context_only_source_unit_ids": ("element-0",),
        "route_decision_sha256": "b" * 64,
        "execution_contract_sha256": "c" * 64,
    }
    first = derive_work_unit_id(**arguments)
    second = derive_work_unit_id(**arguments)
    assert first == second
    assert first.startswith("work-unit-")
    assert len(first) == len("work-unit-") + 64


def test_plan_validates_complete_partition_context_overlap_and_dag() -> None:
    plan, reference = _plan()
    assert validate_coverage_plan(plan, reference) == plan
    assert plan.work_units[1].context_only_source_unit_ids


def test_plan_rejects_missing_primary_assignment() -> None:
    plan, reference = _plan()
    data = plan.model_dump(mode="json")
    data["work_units"][0]["primary_source_unit_ids"].pop()
    with pytest.raises((ValidationError, CoverageContractError)):
        validate_coverage_plan(data, reference)


def test_plan_rejects_stale_work_unit_identity() -> None:
    plan, reference = _plan()
    data = plan.model_dump(mode="json")
    data["work_units"][0]["work_unit_id"] = "work-unit-" + "0" * 64
    with pytest.raises(CoverageContractError):
        validate_coverage_plan(data, reference)


def test_plan_rejects_cycle_and_invalid_execution_order() -> None:
    plan, reference = _plan()
    cycle_data = plan.model_dump(mode="json")
    first, second, third = (unit.work_unit_id for unit in plan.work_units)
    cycle_data["dependency_edges"] = [
        {
            "predecessor_work_unit_id": first,
            "successor_work_unit_id": second,
            "edge_kind": "hierarchy",
        },
        {
            "predecessor_work_unit_id": second,
            "successor_work_unit_id": first,
            "edge_kind": "execution_dependency",
        },
        {
            "predecessor_work_unit_id": first,
            "successor_work_unit_id": third,
            "edge_kind": "merge_dependency",
        },
    ]
    with pytest.raises(CoverageContractError):
        validate_coverage_plan(cycle_data, reference)

    order_data = plan.model_dump(mode="json")
    order_data["planned_execution_order"] = list(reversed(order_data["planned_execution_order"]))
    with pytest.raises(CoverageContractError):
        validate_coverage_plan(order_data, reference)


def test_q28_models_forbid_unknown_fields_and_canonical_bytes_have_no_newline() -> None:
    plan, reference = _plan()
    data = plan.model_dump(mode="json")
    data["unexpected"] = True
    with pytest.raises(ValidationError):
        CoveragePlan.model_validate(data)
    assert len(coverage_plan_sha256(plan)) == 64
    assert not canonical_coverage_plan_bytes(plan).endswith(b"\n")


@pytest.mark.parametrize("condition", ["complete", "failed", "truncated", "invalid", "missing"])
def test_closed_terminal_conditions_are_structurally_valid(condition: str) -> None:
    plan, reference = _plan()
    closure, outputs, owner_records = _closure(plan, reference, condition=condition)
    validated = validate_coverage_closure(
        closure,
        plan,
        output_artifacts=outputs,
        owner_records=owner_records,
    )
    assert validated.coverage_closure_state == CoverageClosureState.CLOSED
    assert all(outcome.terminal_attempt_ordinal == 1 for outcome in validated.unit_outcomes)


def test_missing_without_attempt_is_not_closed() -> None:
    plan, reference = _plan()
    closure, _, _ = _closure(
        plan,
        reference,
        condition="missing",
        state=CoverageClosureState.NOT_CLOSED,
        attempts_by_unit={unit.work_unit_id: () for unit in plan.work_units},
    )
    assert validate_coverage_closure(closure, plan).coverage_closure_state == CoverageClosureState.NOT_CLOSED


def test_terminal_pointer_must_reference_an_existing_attempt() -> None:
    with pytest.raises(ValidationError):
        UnitOutcome(
            work_unit_id="work-unit-" + "0" * 64,
            attempts=(),
            terminal_attempt_ordinal=1,
            coverage_condition=CoverageCondition.MISSING,
        )


def test_prior_failed_attempt_remains_in_later_terminal_history() -> None:
    plan, reference = _plan()
    attempts = {
        unit.work_unit_id: ((1, "failed"), (2, "complete"))
        for unit in plan.work_units
    }
    closure, outputs, owner_records = _closure(
        plan,
        reference,
        attempts_by_unit=attempts,
    )
    validated = validate_coverage_closure(
        closure,
        plan,
        output_artifacts=outputs,
        owner_records=owner_records,
    )
    assert all(len(outcome.attempts) == 2 for outcome in validated.unit_outcomes)
    assert all(outcome.terminal_attempt_ordinal == 2 for outcome in validated.unit_outcomes)


def test_observed_merge_order_must_respect_merge_dependency() -> None:
    plan, reference = _plan()
    closure, _, _ = _closure(
        plan,
        reference,
        state=CoverageClosureState.NOT_CLOSED,
        observed_merge_order=(plan.planned_merge_order[-1],),
    )
    with pytest.raises(CoverageContractError):
        validate_coverage_closure(closure, plan)
