from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

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
from .benchmark_note import benchmark_note_sha256
from .full_profile import load_full_profile
from .generation_lane import build_pre_render_note
from .normalized_document import NormalizedDocument, normalized_document_sha256
from .work_unit_receipt import (
    DurableWorkUnitAttemptReceipt,
    WorkUnitAttemptReceiptStore,
    build_work_unit_attempt_receipt,
    persist_work_unit_attempt_receipt,
    read_durable_work_unit_attempt_receipt,
    work_unit_attempt_receipt_sha256,
)


_REFERENCE_PATH = (
    Path(__file__).parent
    / "v1"
    / "reference_documents"
    / "P01"
    / "revision-001"
    / "normalized_document.json"
)
_PROFILE_ROOT = Path(__file__).parent / "v1"
_FULL_PROFILE = load_full_profile(
    _PROFILE_ROOT / "manifests" / "full" / "revision-001" / "profile.json",
    _PROFILE_ROOT / "manifests" / "full" / "revision-001" / "profile.sha256",
    _PROFILE_ROOT,
)
_P01_CASE = next(case for case in _FULL_PROFILE.cases if case.case_id == "P01")
_RECEIPT_FIXTURE_ROOT = Path(tempfile.mkdtemp(prefix="q28-receipt-fixtures-"))


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


def _closure(
    plan: CoveragePlan,
    reference: NormalizedDocument,
    *,
    condition: str = "complete",
    state: CoverageClosureState = CoverageClosureState.CLOSED,
    attempts_by_unit: dict[str, tuple[tuple[int, str], ...]] | None = None,
    observed_merge_order: tuple[str, ...] | None = None,
) -> tuple[CoverageClosure, dict[str, WorkUnitOutput], WorkUnitAttemptReceiptStore, Any]:
    outputs: dict[str, WorkUnitOutput] = {}
    owner_records: list[DurableWorkUnitAttemptReceipt] = []
    outcomes = []
    attempts_by_unit = attempts_by_unit or {
        unit.work_unit_id: ((1, condition),)
        for unit in plan.work_units
    }
    for unit_index, unit in enumerate(plan.work_units, start=1):
        bindings = []
        previous_terminal_digest = None
        logical_run_id = f"logical-run-{unit_index}"
        for ordinal, attempt_condition in attempts_by_unit[unit.work_unit_id]:
            output = _output(plan, unit.work_unit_id, ordinal, attempt_condition)
            output_digest = work_unit_output_sha256(output)
            outputs[output_digest] = output
            start = build_work_unit_attempt_receipt(
                receipt_role="attempt_started",
                lifecycle_status="started",
                coverage_plan_sha256=coverage_plan_sha256(plan),
                work_unit_id=unit.work_unit_id,
                attempt_ordinal=ordinal,
                work_unit_output_sha256=None,
                membership="diagnostic",
                logical_run_id=logical_run_id,
                execution_id=f"execution-{unit_index}-{ordinal}",
                runner_plan_sha256="f" * 64,
                runner_slot_id=f"slot-{unit_index}",
                runner_attempt_ordinal=ordinal,
                runner_invocation_id="test-invocation",
                previous_receipt_sha256=previous_terminal_digest,
            )
            start_digest = work_unit_attempt_receipt_sha256(start)
            terminal_status = (
                "complete"
                if attempt_condition == "complete"
                else "invalid"
                if attempt_condition == "invalid"
                else "failed"
            )
            terminal = build_work_unit_attempt_receipt(
                receipt_role="attempt_terminal",
                lifecycle_status=terminal_status,
                coverage_plan_sha256=coverage_plan_sha256(plan),
                work_unit_id=unit.work_unit_id,
                attempt_ordinal=ordinal,
                work_unit_output_sha256=output_digest,
                membership="diagnostic",
                logical_run_id=logical_run_id,
                execution_id=f"execution-{unit_index}-{ordinal}",
                runner_plan_sha256="f" * 64,
                runner_slot_id=f"slot-{unit_index}",
                runner_attempt_ordinal=ordinal,
                runner_invocation_id="test-invocation",
                previous_receipt_sha256=start_digest,
            )
            terminal_digest = work_unit_attempt_receipt_sha256(terminal)
            start_path = _RECEIPT_FIXTURE_ROOT / f"{start_digest}.json"
            terminal_path = _RECEIPT_FIXTURE_ROOT / f"{terminal_digest}.json"
            start_record = (
                read_durable_work_unit_attempt_receipt(
                    start_path, start_path.with_suffix(".sha256")
                )
                if start_path.exists()
                else persist_work_unit_attempt_receipt(start, start_path)
            )
            terminal_record = (
                read_durable_work_unit_attempt_receipt(
                    terminal_path, terminal_path.with_suffix(".sha256")
                )
                if terminal_path.exists()
                else persist_work_unit_attempt_receipt(terminal, terminal_path)
            )
            owner_records.extend(
                (
                    start_record,
                    terminal_record,
                )
            )
            previous_terminal_digest = terminal_digest
            bindings.append(
                {
                    "attempt_ordinal": ordinal,
                    "output_sha256": output_digest,
                    "receipt_ref": ExternalOwnerRecordRef(
                        schema_version=terminal.schema_version,
                        sha256=terminal_digest,
                        record_type=terminal.artifact_role,
                        record_id=terminal.record_id,
                    ),
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
            sha256=benchmark_note_sha256(build_pre_render_note(_P01_CASE, _PROFILE_ROOT)),
        ),
        source_reference_mappings=(),
        observations=(),
    )
    return closure, outputs, WorkUnitAttemptReceiptStore(owner_records), build_pre_render_note(
        _P01_CASE, _PROFILE_ROOT
    )


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
    closure, outputs, owner_records, final_note = _closure(plan, reference, condition=condition)
    validated = validate_coverage_closure(
        closure,
        plan,
        output_artifacts=outputs,
        owner_records=owner_records,
        reference_document=reference,
        final_pre_render_note_artifact=final_note,
    )
    assert validated.coverage_closure_state == CoverageClosureState.CLOSED
    assert all(outcome.terminal_attempt_ordinal == 1 for outcome in validated.unit_outcomes)


def test_missing_without_attempt_is_not_closed() -> None:
    plan, reference = _plan()
    closure, _, _, final_note = _closure(
        plan,
        reference,
        condition="missing",
        state=CoverageClosureState.NOT_CLOSED,
        attempts_by_unit={unit.work_unit_id: () for unit in plan.work_units},
    )
    assert validate_coverage_closure(
        closure,
        plan,
        reference_document=reference,
        final_pre_render_note_artifact=final_note,
    ).coverage_closure_state == CoverageClosureState.NOT_CLOSED


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
    closure, outputs, owner_records, final_note = _closure(
        plan,
        reference,
        attempts_by_unit=attempts,
    )
    validated = validate_coverage_closure(
        closure,
        plan,
        output_artifacts=outputs,
        owner_records=owner_records,
        reference_document=reference,
        final_pre_render_note_artifact=final_note,
    )
    assert all(len(outcome.attempts) == 2 for outcome in validated.unit_outcomes)
    assert all(outcome.terminal_attempt_ordinal == 2 for outcome in validated.unit_outcomes)


def test_closed_closure_rejects_owner_receipt_without_q28_attempt_bindings() -> None:
    plan, reference = _plan()
    closure, outputs, owner_records, final_note = _closure(plan, reference)
    incomplete_records = {
        digest: {
            key: value
            for key, value in record.receipt.model_dump(mode="json").items()
            if key not in {"coverage_plan_sha256", "work_unit_id", "attempt_ordinal"}
        }
        for digest, record in owner_records._records.items()
        if record.receipt.receipt_role == "attempt_terminal"
    }

    with pytest.raises(CoverageContractError, match="frozen receipt contract"):
        validate_coverage_closure(
            closure,
            plan,
            output_artifacts=outputs,
            owner_records=incomplete_records,
            reference_document=reference,
            final_pre_render_note_artifact=final_note,
        )


def test_closed_closure_requires_durable_owner_receipt_context() -> None:
    plan, reference = _plan()
    closure, _, _, final_note = _closure(plan, reference)

    with pytest.raises(CoverageContractError, match="durable per-work-unit"):
        validate_coverage_closure(closure, plan)


def _alternate_receipt_pair(
    root: Path,
    *,
    plan_sha256: str,
    work_unit_id: str,
    attempt_ordinal: int,
    output_sha256: str,
    runner_attempt_ordinal: int,
    label: str,
) -> tuple[DurableWorkUnitAttemptReceipt, DurableWorkUnitAttemptReceipt]:
    previous = None if attempt_ordinal == 1 else "e" * 64
    start = build_work_unit_attempt_receipt(
        receipt_role="attempt_started",
        lifecycle_status="started",
        coverage_plan_sha256=plan_sha256,
        work_unit_id=work_unit_id,
        attempt_ordinal=attempt_ordinal,
        work_unit_output_sha256=None,
        membership="diagnostic",
        logical_run_id=f"alternate-run-{label}",
        execution_id=f"alternate-execution-{label}",
        runner_plan_sha256="f" * 64,
        runner_slot_id="alternate-slot",
        runner_attempt_ordinal=runner_attempt_ordinal,
        runner_invocation_id="alternate-invocation",
        previous_receipt_sha256=previous,
    )
    start_record = persist_work_unit_attempt_receipt(
        start, root / f"{label}-start.json"
    )
    terminal = build_work_unit_attempt_receipt(
        receipt_role="attempt_terminal",
        lifecycle_status="complete",
        coverage_plan_sha256=plan_sha256,
        work_unit_id=work_unit_id,
        attempt_ordinal=attempt_ordinal,
        work_unit_output_sha256=output_sha256,
        membership="diagnostic",
        logical_run_id=f"alternate-run-{label}",
        execution_id=f"alternate-execution-{label}",
        runner_plan_sha256="f" * 64,
        runner_slot_id="alternate-slot",
        runner_attempt_ordinal=runner_attempt_ordinal,
        runner_invocation_id="alternate-invocation",
        previous_receipt_sha256=start_record.sha256,
    )
    terminal_record = persist_work_unit_attempt_receipt(
        terminal, root / f"{label}-terminal.json"
    )
    return start_record, terminal_record


def _closure_with_first_receipt(
    closure: CoverageClosure, receipt: DurableWorkUnitAttemptReceipt
) -> CoverageClosure:
    data = closure.model_dump(mode="json")
    data["unit_outcomes"][0]["attempts"][0]["receipt_ref"] = {
        "schema_version": receipt.receipt.schema_version,
        "sha256": receipt.sha256,
        "record_type": receipt.receipt.artifact_role,
        "record_id": receipt.receipt.record_id,
    }
    return CoverageClosure.model_validate(data)


@pytest.mark.parametrize("mismatch", ["plan", "work_unit", "ordinal", "output"])
def test_closed_closure_rejects_direct_owner_binding_mismatches(
    mismatch: str, tmp_path: Path
) -> None:
    plan, reference = _plan()
    closure, outputs, owner_records, final_note = _closure(plan, reference)
    target_unit = plan.work_units[0].work_unit_id
    target_output = next(
        attempt.output_sha256
        for attempt in closure.unit_outcomes[0].attempts
        if attempt.attempt_ordinal == 1
    )
    alternate_plan = "e" * 64 if mismatch == "plan" else coverage_plan_sha256(plan)
    alternate_unit = "work-unit-" + "e" * 64 if mismatch == "work_unit" else target_unit
    alternate_ordinal = 2 if mismatch == "ordinal" else 1
    alternate_output = "f" * 64 if mismatch == "output" else target_output
    start_record, terminal_record = _alternate_receipt_pair(
        tmp_path,
        plan_sha256=alternate_plan,
        work_unit_id=alternate_unit,
        attempt_ordinal=alternate_ordinal,
        output_sha256=alternate_output,
        runner_attempt_ordinal=9,
        label=mismatch,
    )
    all_records = tuple(owner_records._records.values()) + (start_record, terminal_record)
    bad_closure = _closure_with_first_receipt(closure, terminal_record)
    with pytest.raises(CoverageContractError):
        validate_coverage_closure(
            bad_closure,
            plan,
            output_artifacts=outputs,
            owner_records=WorkUnitAttemptReceiptStore(all_records),
            reference_document=reference,
            final_pre_render_note_artifact=final_note,
        )


def test_closed_closure_rejects_missing_and_non_durable_receipts() -> None:
    plan, reference = _plan()
    closure, outputs, owner_records, final_note = _closure(plan, reference)
    with pytest.raises(CoverageContractError, match="cannot be resolved"):
        validate_coverage_closure(
            closure,
            plan,
            output_artifacts=outputs,
            owner_records=WorkUnitAttemptReceiptStore(()),
            reference_document=reference,
            final_pre_render_note_artifact=final_note,
        )

    pending_records = {
        digest: record.receipt for digest, record in owner_records._records.items()
    }
    with pytest.raises(CoverageContractError, match="durable per-work-unit"):
        validate_coverage_closure(
            closure,
            plan,
            output_artifacts=outputs,
            owner_records=pending_records,
            reference_document=reference,
            final_pre_render_note_artifact=final_note,
        )


def test_closed_closure_rejects_broken_owner_history_chain() -> None:
    plan, reference = _plan()
    closure, outputs, owner_records, final_note = _closure(plan, reference)
    terminal_only = WorkUnitAttemptReceiptStore(
        tuple(
            record
            for record in owner_records._records.values()
            if record.receipt.receipt_role == "attempt_terminal"
        )
    )
    with pytest.raises(CoverageContractError, match="cannot be resolved"):
        validate_coverage_closure(
            closure,
            plan,
            output_artifacts=outputs,
            owner_records=terminal_only,
            reference_document=reference,
            final_pre_render_note_artifact=final_note,
        )


def test_q28_ignores_runner_ordinal_when_owner_attempt_binding_is_correct(
    tmp_path: Path,
) -> None:
    plan, reference = _plan()
    closure, outputs, owner_records, final_note = _closure(plan, reference)
    target_output = closure.unit_outcomes[0].attempts[0].output_sha256
    start_record, terminal_record = _alternate_receipt_pair(
        tmp_path,
        plan_sha256=coverage_plan_sha256(plan),
        work_unit_id=plan.work_units[0].work_unit_id,
        attempt_ordinal=1,
        output_sha256=target_output,
        runner_attempt_ordinal=99,
        label="runner-ordinal-only",
    )
    bad_closure = _closure_with_first_receipt(closure, terminal_record)
    validated = validate_coverage_closure(
        bad_closure,
        plan,
        output_artifacts=outputs,
        owner_records=WorkUnitAttemptReceiptStore(
            tuple(owner_records._records.values()) + (start_record, terminal_record)
        ),
        reference_document=reference,
        final_pre_render_note_artifact=final_note,
    )
    assert validated.coverage_closure_state == CoverageClosureState.CLOSED


def test_observed_merge_order_must_respect_merge_dependency() -> None:
    plan, reference = _plan()
    closure, _, _, final_note = _closure(
        plan,
        reference,
        state=CoverageClosureState.NOT_CLOSED,
        observed_merge_order=(plan.planned_merge_order[-1],),
    )
    with pytest.raises(CoverageContractError):
        validate_coverage_closure(
            closure,
            plan,
            reference_document=reference,
            final_pre_render_note_artifact=final_note,
        )
