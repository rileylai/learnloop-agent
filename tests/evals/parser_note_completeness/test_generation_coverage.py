from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from .coverage import (
    CoverageContractError,
    CoveragePlanningGapError,
    canonical_coverage_plan_bytes,
    coverage_plan_sha256,
    materialize_coverage_plan,
)
from .full_profile import load_full_profile
from .normalized_document import NormalizedDocument
from .routing import (
    ContractReference,
    RouteMode,
    ROUTING_INPUT_FACTS_SCHEMA_VERSION,
    ROUTING_MODE_ORDER,
    ROUTING_POLICY_SCHEMA_VERSION,
    RoutingPolicy,
    RunMembership,
    materialize_route_decision,
    materialize_routing_input_facts,
    routing_policy_sha256,
)


ROOT = Path(__file__).parent / "v1"
PROFILE = load_full_profile(
    ROOT / "manifests" / "full" / "revision-001" / "profile.json",
    ROOT / "manifests" / "full" / "revision-001" / "profile.sha256",
    ROOT,
)


def _reference_and_source(case_id: str = "P01") -> tuple[NormalizedDocument, bytes]:
    case = next(case for case in PROFILE.cases if case.case_id == case_id)
    reference = NormalizedDocument.model_validate(
        json.loads((ROOT / case.reference_path).read_bytes())
    )
    return reference, (ROOT / case.source_artifact_path).read_bytes()


def _route(
    mode: RouteMode = RouteMode.SINGLE_PASS,
    *,
    case_id: str = "P01",
) -> tuple[NormalizedDocument, RoutingPolicy, Any, ContractReference]:
    reference, source_bytes = _reference_and_source(case_id)
    contract = ContractReference(
        contract_id="q28-test-execution",
        sha256="d" * 64,
    )
    policy = RoutingPolicy(
        schema_version=ROUTING_POLICY_SCHEMA_VERSION,
        policy_id="q28-test-routing-policy",
        policy_revision="revision-001",
        implementation_id="q28-test-selector",
        implementation_version="1.0.0",
        configuration_sha256="a" * 64,
        input_facts_schema_version=ROUTING_INPUT_FACTS_SCHEMA_VERSION,
        mode_order=ROUTING_MODE_ORDER,
        boundary_references=(),
        execution_contract=contract,
    )
    facts = materialize_routing_input_facts(reference, source_bytes, contract)

    def selector(policy_model: RoutingPolicy, facts_model: Any) -> RouteMode:
        del policy_model, facts_model
        return mode

    decision = materialize_route_decision(
        policy,
        facts,
        policy_sha256=routing_policy_sha256(policy),
        run_membership=RunMembership.DIAGNOSTIC,
        selector=selector,
    )
    return reference, policy, decision, contract


def test_single_pass_materializes_exhaustive_one_unit_plan() -> None:
    reference, policy, decision, contract = _route()
    plan = materialize_coverage_plan(reference, policy, decision, contract)

    assert len(plan.work_units) == 1
    assert plan.work_units[0].primary_source_unit_ids == tuple(
        element.element_id for element in reference.elements
    )
    assert plan.work_units[0].context_only_source_unit_ids == ()
    assert plan.dependency_edges == ()
    assert plan.planned_execution_order == (plan.work_units[0].work_unit_id,)
    assert plan.planned_merge_order == (plan.work_units[0].work_unit_id,)


def test_single_pass_plan_bytes_and_digest_repeat_identically() -> None:
    reference, policy, decision, contract = _route()
    first = materialize_coverage_plan(reference, policy, decision, contract)
    second = materialize_coverage_plan(reference, policy, decision, contract)

    assert canonical_coverage_plan_bytes(first) == canonical_coverage_plan_bytes(second)
    assert coverage_plan_sha256(first) == coverage_plan_sha256(second)


@pytest.mark.parametrize("mode", [RouteMode.SECTION_AWARE, RouteMode.HIERARCHICAL])
def test_modes_without_frozen_q28_planner_fail_closed(mode: RouteMode) -> None:
    reference, policy, decision, contract = _route(mode)

    with pytest.raises(CoveragePlanningGapError, match=mode.value):
        materialize_coverage_plan(reference, policy, decision, contract)


def test_route_reference_config_and_execution_mismatch_reject() -> None:
    reference, policy, decision, contract = _route()
    other_reference, _, _, _ = _route(case_id="W01")
    with pytest.raises(CoverageContractError):
        materialize_coverage_plan(other_reference, policy, decision, contract)

    policy_data = policy.model_dump(mode="json")
    policy_data["configuration_sha256"] = "b" * 64
    mismatched_policy = RoutingPolicy.model_validate(policy_data)
    with pytest.raises(CoverageContractError):
        materialize_coverage_plan(reference, mismatched_policy, decision, contract)

    mismatched_contract = ContractReference(
        contract_id=contract.contract_id,
        sha256="e" * 64,
    )
    with pytest.raises(CoverageContractError):
        materialize_coverage_plan(reference, policy, decision, mismatched_contract)


def test_work_unit_id_changes_only_with_frozen_identity_inputs() -> None:
    reference, policy, decision, contract = _route()
    first = materialize_coverage_plan(reference, policy, decision, contract)
    second = materialize_coverage_plan(
        reference,
        policy,
        decision,
        contract,
        plan_id="different-plan-id",
    )
    assert first.work_units[0].work_unit_id == second.work_units[0].work_unit_id
