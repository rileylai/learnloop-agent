from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from .full_profile import load_full_profile
from .routing import (
    Availability,
    AvailabilityReason,
    AvailabilityStatus,
    ContextCapacity,
    ContractReference,
    ConformanceReason,
    ConformanceStatus,
    DecisionReason,
    DecisionStatus,
    FORCED_DIAGNOSTIC_SCHEMA_VERSION,
    ModelIdentity,
    RouteConformance,
    RouteDecision,
    RouteMode,
    RoutingContractError,
    RoutingPolicy,
    RoutingPolicyGapError,
    ROUTE_DECISION_SCHEMA_VERSION,
    ROUTING_INPUT_FACTS_SCHEMA_VERSION,
    ROUTING_MODE_ORDER,
    ROUTING_POLICY_SCHEMA_VERSION,
    RunMembership,
    TokenMeasurement,
    build_forced_diagnostic,
    build_route_conformance,
    canonical_routing_bytes,
    materialize_route_decision,
    materialize_routing_input_facts,
    route_decision_sha256,
    routing_input_facts_sha256,
    routing_policy_sha256,
    validate_forced_diagnostic_bindings,
    validate_route_conformance_bindings,
    validate_route_decision_bindings,
    validate_routing_input_facts_bindings,
)
from .normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


ROOT = Path(__file__).parent / "v1"
FULL_PROFILE = load_full_profile(
    ROOT / "manifests" / "full" / "revision-001" / "profile.json",
    ROOT / "manifests" / "full" / "revision-001" / "profile.sha256",
    ROOT,
)


def _reference_and_source(case_id: str) -> tuple[NormalizedDocument, bytes]:
    case = next(item for item in FULL_PROFILE.cases if item.case_id == case_id)
    reference = NormalizedDocument.model_validate(
        json.loads((ROOT / case.reference_path).read_bytes())
    )
    return reference, (ROOT / case.source_artifact_path).read_bytes()


def _contract(identifier: str = "generation-diagnostic-v1", fill: str = "b") -> ContractReference:
    return ContractReference(contract_id=identifier, sha256=fill * 64)


def _policy(configuration_fill: str = "a") -> RoutingPolicy:
    return RoutingPolicy(
        schema_version=ROUTING_POLICY_SCHEMA_VERSION,
        policy_id="diagnostic-routing-policy",
        policy_revision="revision-001",
        implementation_id="unimplemented-selector-interface",
        implementation_version="1.0.0",
        configuration_sha256=configuration_fill * 64,
        input_facts_schema_version=ROUTING_INPUT_FACTS_SCHEMA_VERSION,
        mode_order=ROUTING_MODE_ORDER,
        boundary_references=(),
        execution_contract=_contract(),
    )


def _facts(case_id: str = "P01"):
    reference, source_bytes = _reference_and_source(case_id)
    return reference, source_bytes, materialize_routing_input_facts(
        reference,
        source_bytes,
        _contract(),
    )


def _constant_selector(policy: RoutingPolicy, facts: Any) -> RouteMode:
    del policy, facts
    return RouteMode.SINGLE_PASS


def test_exact_schema_versions_and_strict_extra_fields() -> None:
    policy = _policy()
    payload = policy.model_dump(mode="json")
    payload["unexpected"] = True
    with pytest.raises(ValidationError):
        RoutingPolicy.model_validate(payload)

    reference, _, facts = _facts()
    decision = materialize_route_decision(
        policy,
        facts,
        policy_sha256=routing_policy_sha256(policy),
        run_membership=RunMembership.FORMAL_REQUIRED,
        selector=_constant_selector,
    )
    decision_payload = decision.model_dump(mode="json")
    decision_payload["schema_version"] = FORCED_DIAGNOSTIC_SCHEMA_VERSION
    with pytest.raises(ValidationError):
        RouteDecision.model_validate(decision_payload)
    assert reference.document_id == decision.reference_document.document_id
    assert decision.schema_version == ROUTE_DECISION_SCHEMA_VERSION


def test_input_facts_materialize_deterministically_without_source_text() -> None:
    for case_id in [item.case_id for item in FULL_PROFILE.cases]:
        reference, source_bytes, first = _facts(case_id)
        second = materialize_routing_input_facts(reference, source_bytes, _contract())
        assert canonical_routing_bytes(first) == canonical_routing_bytes(second)
        assert canonical_routing_bytes(first) == canonical_routing_bytes(first).rstrip(b"\n")
        assert hashlib.sha256(canonical_routing_bytes(first)).hexdigest() == routing_input_facts_sha256(first)
        assert first.reference.sha256 == hashlib.sha256(
            canonical_normalized_document_bytes(reference)
        ).hexdigest()
        assert reference.elements[0].content.encode("utf-8") not in canonical_routing_bytes(first)
        assert first.structure.elements[-1].order == len(reference.elements) - 1


def test_structure_and_order_bind_exactly_to_reference() -> None:
    reference, source_bytes, facts = _facts("P04")
    assert tuple(item.element_id for item in facts.structure.elements) == tuple(
        item.element_id for item in reference.elements
    )
    assert tuple(item.order for item in facts.structure.elements) == tuple(
        range(len(reference.elements))
    )
    assert tuple(item.section_id for item in facts.structure.elements) == tuple(
        item.section_id for item in reference.elements
    )
    assert validate_routing_input_facts_bindings(facts, reference, source_bytes=source_bytes) == facts

    invalid = facts.model_dump(mode="json")
    invalid["structure"]["elements"][0]["order"] = 1
    with pytest.raises(ValidationError):
        type(facts).model_validate(invalid)


def test_availability_and_token_measurement_are_strict() -> None:
    with pytest.raises(ValidationError):
        Availability[ModelIdentity](status=AvailabilityStatus.AVAILABLE, value=None)
    with pytest.raises(ValidationError):
        Availability[ModelIdentity](
            status=AvailabilityStatus.UNAVAILABLE,
            value=ModelIdentity(model_id="model", revision="r1"),
            reason=AvailabilityReason.NOT_OBSERVED,
        )
    with pytest.raises(ValidationError):
        TokenMeasurement(
            unit="input_tokens",
            count=1,
            measurement_contract_id="",
            measurement_contract_sha256="a" * 64,
        )

    _, _, facts = _facts()
    assert facts.source.token_count.status == AvailabilityStatus.UNAVAILABLE
    assert facts.source.token_count.reason == AvailabilityReason.NOT_APPROVED
    assert facts.capacity.context_capacity.status == AvailabilityStatus.UNAVAILABLE


def test_source_digest_and_reference_binding_fail_closed() -> None:
    reference, source_bytes, facts = _facts()
    with pytest.raises(RoutingContractError, match="source digest"):
        validate_routing_input_facts_bindings(facts, reference, source_bytes=b"tampered")
    with pytest.raises(RoutingContractError, match="source bytes"):
        materialize_routing_input_facts(reference, b"tampered", _contract())

    invalid = facts.model_dump(mode="json")
    invalid["reference"]["sha256"] = "c" * 64
    with pytest.raises(RoutingContractError, match="reference document digest"):
        validate_routing_input_facts_bindings(invalid, reference, source_bytes=source_bytes)


def test_no_selector_means_policy_evidence_gap_not_invented_mode() -> None:
    _, _, facts = _facts()
    policy = _policy()
    with pytest.raises(RoutingPolicyGapError, match="selector"):
        materialize_route_decision(
            policy,
            facts,
            policy_sha256=routing_policy_sha256(policy),
            run_membership="formal_required",
        )


def test_unavailable_required_fact_rejects_formal_route() -> None:
    _, _, facts = _facts()
    policy = _policy()
    decision = materialize_route_decision(
        policy,
        facts,
        policy_sha256=routing_policy_sha256(policy),
        run_membership="formal_required",
        required_fact_paths=("capacity.context_capacity",),
        selector=_constant_selector,
    )
    assert decision.decision_status == DecisionStatus.REJECTED
    assert decision.decision_reason == DecisionReason.REQUIRED_FACT_UNAVAILABLE
    assert decision.selected_mode is None
    assert validate_route_decision_bindings(decision, policy, _reference_and_source("P01")[0]) == decision


def test_route_decision_digest_bindings_reject_policy_config_and_fact_tampering() -> None:
    reference, source_bytes, facts = _facts()
    policy = _policy()
    decision = materialize_route_decision(
        policy,
        facts,
        policy_sha256=routing_policy_sha256(policy),
        run_membership="formal_required",
        selector=_constant_selector,
    )
    validate_route_decision_bindings(decision, policy, reference, source_bytes=source_bytes)

    invalid_policy = decision.model_dump(mode="json")
    invalid_policy["policy"]["configuration_sha256"] = "c" * 64
    with pytest.raises(RoutingContractError, match="configuration"):
        validate_route_decision_bindings(invalid_policy, policy, reference, source_bytes=source_bytes)

    invalid_facts = decision.model_dump(mode="json")
    invalid_facts["input_facts_sha256"] = "d" * 64
    with pytest.raises(RoutingContractError, match="input-facts"):
        validate_route_decision_bindings(invalid_facts, policy, reference, source_bytes=source_bytes)


def test_forced_diagnostic_is_independent_and_formal_membership_is_invalid() -> None:
    reference, source_bytes, facts = _facts()
    policy = _policy()
    decision = materialize_route_decision(
        policy,
        facts,
        policy_sha256=routing_policy_sha256(policy),
        run_membership="formal_required",
        selector=_constant_selector,
    )
    forced = build_forced_diagnostic(
        decision,
        diagnostic_slot_id="diagnostic-P01-hierarchical",
        effective_mode=RouteMode.HIERARCHICAL,
        execution_contract=_contract("forced-diagnostic-v1", "e"),
    )
    assert forced.run_membership == "diagnostic"
    assert forced.policy_selected_mode == decision.selected_mode
    assert forced.effective_mode == RouteMode.HIERARCHICAL
    validate_forced_diagnostic_bindings(forced, decision)
    assert validate_route_decision_bindings(
        decision, policy, reference, source_bytes=source_bytes
    ) == decision

    invalid = forced.model_dump(mode="json")
    invalid["run_membership"] = "formal_required"
    with pytest.raises(ValidationError):
        type(forced).model_validate(invalid)


def test_conformance_covers_conformant_mode_contract_rejected_and_forced() -> None:
    reference, source_bytes, facts = _facts()
    policy = _policy()
    decision = materialize_route_decision(
        policy,
        facts,
        policy_sha256=routing_policy_sha256(policy),
        run_membership="formal_required",
        selector=_constant_selector,
    )
    validate_route_decision_bindings(decision, policy, reference, source_bytes=source_bytes)

    conformant = build_route_conformance(
        decision,
        execution_contract=_contract(),
        executed_mode=RouteMode.SINGLE_PASS,
    )
    assert conformant.status == ConformanceStatus.CONFORMANT
    validate_route_conformance_bindings(conformant, decision)

    mode_mismatch = build_route_conformance(
        decision,
        execution_contract=_contract(),
        executed_mode=RouteMode.HIERARCHICAL,
    )
    assert mode_mismatch.status == ConformanceStatus.MISMATCH
    assert mode_mismatch.reason == ConformanceReason.EXECUTED_MODE_MISMATCH
    validate_route_conformance_bindings(mode_mismatch, decision)

    contract_mismatch = build_route_conformance(
        decision,
        execution_contract=_contract("other-contract", "f"),
        executed_mode=RouteMode.SINGLE_PASS,
    )
    assert contract_mismatch.status == ConformanceStatus.MISMATCH
    assert contract_mismatch.reason == ConformanceReason.EXECUTION_CONTRACT_MISMATCH
    validate_route_conformance_bindings(contract_mismatch, decision)

    rejected = materialize_route_decision(
        policy,
        facts,
        policy_sha256=routing_policy_sha256(policy),
        run_membership="formal_required",
        required_fact_paths=("provider_model.provider",),
        selector=_constant_selector,
    )
    rejected_conformance = build_route_conformance(
        rejected,
        execution_contract=_contract(),
        executed_mode=None,
    )
    assert rejected_conformance.status == ConformanceStatus.REJECTED
    assert rejected_conformance.reason == ConformanceReason.ROUTE_DECISION_REJECTED
    validate_route_conformance_bindings(rejected_conformance, rejected)

    forced = build_forced_diagnostic(
        decision,
        diagnostic_slot_id="diagnostic-P01-hierarchical",
        effective_mode=RouteMode.HIERARCHICAL,
        execution_contract=_contract("forced-diagnostic-v1", "e"),
    )
    forced_conformance = build_route_conformance(
        decision,
        execution_contract=forced.execution_contract,
        executed_mode=forced.effective_mode,
        forced_diagnostic=forced,
    )
    assert forced_conformance.status == ConformanceStatus.FORCED_DIAGNOSTIC
    assert forced_conformance.reason == ConformanceReason.FORCED_MODE_EXECUTION
    validate_route_conformance_bindings(
        forced_conformance,
        decision,
        forced_diagnostic=forced,
    )


def test_canonical_digest_helpers_are_external_and_repeatable() -> None:
    policy = _policy()
    first = canonical_routing_bytes(policy)
    second = canonical_routing_bytes(policy.model_dump(mode="json"))
    assert first == second
    assert not first.endswith(b"\n")
    assert routing_policy_sha256(policy) == hashlib.sha256(first).hexdigest()
