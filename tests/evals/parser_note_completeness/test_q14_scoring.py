from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

import pytest
from pydantic import ValidationError

from .q14_scoring import (
    COHORT_RESULT_ID_SEED_FIELDS,
    FIXTURE_RESULT_ID_SEED_FIELDS,
    Q14_AGGREGATION_CONTRACT_SCHEMA_VERSION,
    Q14_COHORT_METRIC_RESULT_SCHEMA_VERSION,
    Q14_FIXTURE_METRIC_RESULT_SCHEMA_VERSION,
    Q14_METRIC_CONTRACT_SCHEMA_VERSION,
    Q14_METRIC_REGISTRY_SCHEMA_VERSION,
    Q14_SCORER_CONTRACT_SCHEMA_VERSION,
    AggregationContract,
    AggregationContractReference,
    ApplicabilityConsumption,
    CanonicalUnit,
    CohortMetricResult,
    CoverageState,
    DenominatorSemantics,
    DeterministicRequirements,
    Direction,
    FixtureMetricResult,
    FixtureResultReference,
    FormulaKind,
    FormulaReference,
    InputArtifactReference,
    InputArtifactRole,
    MetricComponent,
    MetricContract,
    MetricContractReference,
    MetricFormula,
    MetricKind,
    MetricRegistry,
    MetricRegistryReference,
    NumericRepresentation,
    OwnerRecordReference,
    Q14ContractError,
    Q14Lane,
    Rational,
    ScorerContract,
    ScorerContractReference,
    ScoringUnit,
    SupportMetricValue,
    SupportState,
    canonical_q14_bytes,
    canonical_aggregation_contract_bytes,
    canonical_cohort_metric_result_bytes,
    canonical_fixture_metric_result_bytes,
    canonical_metric_contract_bytes,
    canonical_metric_registry_bytes,
    canonical_scorer_contract_bytes,
    cohort_metric_result_sha256,
    derive_cohort_metric_result_id,
    derive_fixture_metric_result_id,
    fixture_metric_result_sha256,
    metric_contract_sha256,
    metric_registry_sha256,
    q14_artifact_sha256,
    score_coverage_fixture,
    score_support_fixture,
    scorer_contract_sha256,
    aggregation_contract_sha256,
    build_cohort_metric_result,
    build_fixture_metric_result,
    validate_cohort_metric_result,
    validate_fixture_metric_result,
    validate_aggregation_contract,
    validate_metric_contract,
    validate_metric_contract_bindings,
    validate_metric_registry,
    validate_metric_registry_bindings,
    validate_scorer_contract,
    validate_scorer_contract_bindings,
)


def _aggregation() -> AggregationContract:
    return AggregationContract(
        schema_version=Q14_AGGREGATION_CONTRACT_SCHEMA_VERSION,
        artifact_role="aggregation_contract",
        aggregation_contract_id="fixture-vector",
        aggregation_contract_version="1.0.0",
        input_metric_result_schema_version=Q14_FIXTURE_METRIC_RESULT_SCHEMA_VERSION,
        aggregation_kind="fixture_vector_only",
        formal_output="ordered_fixture_vector",
    )


def _metric(
    *, kind: MetricKind, lane: Q14Lane = Q14Lane.GENERATION
) -> tuple[MetricContract, MetricRegistry, ScorerContract, AggregationContract]:
    aggregation = _aggregation()
    if kind == MetricKind.COVERAGE:
        scoring_unit = ScoringUnit.EXPECTED_CLAIM
        denominator = DenominatorSemantics.AUTHORITY_CLOSED_APPLICABLE_UNITS
        applicability = ApplicabilityConsumption.Q12_AUTHORITATIVE_DISPOSITION
        formula_kind = FormulaKind.COVERAGE_STATE_VECTOR_V1
        components = (
            MetricComponent(
                component_id="fully_covered",
                direction=Direction.NON_DIRECTIONAL,
                canonical_unit=CanonicalUnit.COUNT,
                numeric_representation=NumericRepresentation.INTEGER,
            ),
            MetricComponent(
                component_id="partially_covered",
                direction=Direction.NON_DIRECTIONAL,
                canonical_unit=CanonicalUnit.COUNT,
                numeric_representation=NumericRepresentation.INTEGER,
            ),
            MetricComponent(
                component_id="not_covered",
                direction=Direction.NON_DIRECTIONAL,
                canonical_unit=CanonicalUnit.COUNT,
                numeric_representation=NumericRepresentation.INTEGER,
            ),
        )
        required_roles = (InputArtifactRole.GOLD,)
        metric_id = "coverage-v1"
    else:
        scoring_unit = ScoringUnit.GENERATED_CLAIM
        denominator = DenominatorSemantics.Q8_DECIDED_SUPPORT_UNITS
        applicability = ApplicabilityConsumption.Q8_DECIDED_STATE_DISPOSITION
        formula_kind = FormulaKind.SUPPORT_STATE_COUNTS_V1
        components = tuple(
            MetricComponent(
                component_id=state,
                direction=Direction.NON_DIRECTIONAL,
                canonical_unit=CanonicalUnit.COUNT,
                numeric_representation=NumericRepresentation.INTEGER,
            )
            for state in (
                "supported",
                "partially_supported",
                "unsupported",
                "contradicted_by_source",
                "overstated",
            )
        )
        required_roles = (InputArtifactRole.CANDIDATE_OUTPUT,)
        metric_id = "support-v1"
    contract = MetricContract(
        schema_version=Q14_METRIC_CONTRACT_SCHEMA_VERSION,
        artifact_role="metric_contract",
        metric_contract_id=metric_id,
        metric_contract_version="1.0.0",
        metric_kind=kind,
        lane=lane,
        scoring_unit=scoring_unit,
        denominator_semantics=denominator,
        applicability_consumption=applicability,
        formula=MetricFormula(
            formula_id=metric_id,
            formula_revision="1.0.0",
            formula_kind=formula_kind,
        ),
        components=components,
        required_input_roles=required_roles,
        aggregation_contract_ref=AggregationContractReference(
            aggregation_contract_id=aggregation.aggregation_contract_id,
            aggregation_contract_version=aggregation.aggregation_contract_version,
            sha256=aggregation_contract_sha256(aggregation),
        ),
    )
    registry = MetricRegistry(
        schema_version=Q14_METRIC_REGISTRY_SCHEMA_VERSION,
        artifact_role="metric_registry",
        registry_id="q14-registry",
        registry_revision="revision-001",
        benchmark_revision="benchmark-001",
        metric_contracts=(
            MetricContractReference(
                metric_contract_id=contract.metric_contract_id,
                metric_contract_version=contract.metric_contract_version,
                sha256=metric_contract_sha256(contract),
            ),
        ),
    )
    scorer = ScorerContract(
        schema_version=Q14_SCORER_CONTRACT_SCHEMA_VERSION,
        artifact_role="scorer_contract",
        scorer_contract_id="q14-deterministic-scorer",
        scorer_contract_version="1.0.0",
        implementation_id="q14-python-foundation",
        implementation_version="1.0.0",
        implementation_sha256="1" * 64,
        configuration_sha256="2" * 64,
        supported_metric_contracts=registry.metric_contracts,
        compatible_lanes=(lane,),
        deterministic_requirements=DeterministicRequirements(
            execution_mode="offline_deterministic",
            network_egress="forbidden",
            randomness="forbidden",
            binary_float_authority="forbidden",
            input_order="metric_contract_defined",
            serialization="benchmark_canonical_json",
        ),
        fixture_result_schema_version=Q14_FIXTURE_METRIC_RESULT_SCHEMA_VERSION,
    )
    return contract, registry, scorer, aggregation


def _fixture(
    contract: MetricContract,
    registry: MetricRegistry,
    scorer: ScorerContract,
    value: Any,
    *,
    fixture_id: str = "fixture-001",
    input_digest: str = "3" * 64,
    exclusion_ref: Optional[OwnerRecordReference] = None,
) -> FixtureMetricResult:
    input_artifacts = tuple(
        InputArtifactReference(artifact_role=role, sha256=input_digest)
        for role in contract.required_input_roles
    )
    fields = {
        "schema_version": Q14_FIXTURE_METRIC_RESULT_SCHEMA_VERSION,
        "artifact_role": "fixture_metric_result",
        "benchmark_revision": "benchmark-001",
        "fixture_id": fixture_id,
        "fixture_revision": "revision-001",
        "lane": contract.lane,
        "metric_contract_ref": MetricContractReference(
            metric_contract_id=contract.metric_contract_id,
            metric_contract_version=contract.metric_contract_version,
            sha256=metric_contract_sha256(contract),
        ),
        "metric_registry_ref": MetricRegistryReference(
            registry_id=registry.registry_id,
            registry_revision=registry.registry_revision,
            sha256=metric_registry_sha256(registry),
        ),
        "scorer_contract_ref": ScorerContractReference(
            scorer_contract_id=scorer.scorer_contract_id,
            scorer_contract_version=scorer.scorer_contract_version,
            sha256=scorer_contract_sha256(scorer),
        ),
        "formula_ref": FormulaReference(
            formula_id=contract.formula.formula_id,
            formula_revision=contract.formula.formula_revision,
        ),
        "input_artifacts": input_artifacts,
        "applicability_ref": OwnerRecordReference(
            schema_version="q12-disposition/1.0.0",
            record_type="applicability",
            record_id="disposition-001",
            sha256="4" * 64,
        ),
        "exclusion_ref": exclusion_ref,
        "metric_value": value,
    }
    seed = {
        key: value.model_dump(mode="json") if hasattr(value, "model_dump") else value
        for key, value in fields.items()
    }
    seed["metric_value"] = value.model_dump(mode="json")
    result_id = derive_fixture_metric_result_id(seed)
    return FixtureMetricResult(result_id=result_id, **fields)


def _rebuild_fixture(result: FixtureMetricResult, **updates: Any) -> FixtureMetricResult:
    payload = result.model_dump(mode="json")
    payload.update(updates)
    payload["result_id"] = derive_fixture_metric_result_id(payload)
    return FixtureMetricResult.model_validate(payload)


def _rebuild_cohort(cohort: CohortMetricResult, **updates: Any) -> CohortMetricResult:
    payload = cohort.model_dump(mode="json")
    payload.update(updates)
    payload["cohort_result_id"] = derive_cohort_metric_result_id(payload)
    return CohortMetricResult.model_validate(payload)


def _cohort_from_fixture(
    contract: MetricContract,
    registry: MetricRegistry,
    aggregation: AggregationContract,
    fixture: FixtureMetricResult,
) -> CohortMetricResult:
    return build_cohort_metric_result(
        benchmark_revision=registry.benchmark_revision,
        cohort_id="cohort-001",
        cohort_revision="revision-001",
        lane=contract.lane,
        metric_contract=contract,
        metric_registry=registry,
        aggregation_contract=aggregation,
        fixture_results=(
            FixtureResultReference(
                fixture_id=fixture.fixture_id,
                fixture_revision=fixture.fixture_revision,
                result_sha256=fixture_metric_result_sha256(fixture),
            ),
        ),
        resolved_fixture_results={fixture.fixture_id: fixture},
    )


def test_generation_coverage_result_has_exact_strata_and_rational_rates() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.COVERAGE)
    value = score_coverage_fixture(
        authoritative_expected_claim_ids=("e1", "e2", "e3"),
        importance_by_expected_claim_id={"e1": "critical", "e2": "major", "e3": "minor"},
        coverage_state_by_expected_claim_id={
            "e1": "fully_covered",
            "e2": "partially_covered",
            "e3": "not_covered",
        },
        applicable_expected_claim_ids=("e1", "e2", "e3"),
        excluded_expected_claim_ids=(),
    )
    assert tuple(item.stratum.value for item in value.strata) == (
        "critical",
        "major",
        "minor",
    )
    assert value.strata[0].fully_covered_rate == Rational(numerator=1, denominator=1)
    result = _fixture(contract, registry, scorer, value)
    validate_fixture_metric_result(
        result,
        metric_contract=contract,
        metric_registry=registry,
        scorer_contract=scorer,
        aggregation_contract=aggregation,
        resolved_input_digests={"gold": "3" * 64},
        resolved_external_digests={"disposition-001": "4" * 64},
    )


def test_end_to_end_coverage_result_uses_the_same_frozen_vector_contract() -> None:
    contract, registry, scorer, aggregation = _metric(
        kind=MetricKind.COVERAGE,
        lane=Q14Lane.END_TO_END,
    )
    value = score_coverage_fixture(
        authoritative_expected_claim_ids=("e2e-1",),
        importance_by_expected_claim_id={"e2e-1": "critical"},
        coverage_state_by_expected_claim_id={"e2e-1": "fully_covered"},
        applicable_expected_claim_ids=("e2e-1",),
        excluded_expected_claim_ids=(),
    )
    result = _fixture(contract, registry, scorer, value, fixture_id="e2e-001")
    assert result.lane == Q14Lane.END_TO_END
    validate_fixture_metric_result(
        result,
        metric_contract=contract,
        metric_registry=registry,
        scorer_contract=scorer,
        aggregation_contract=aggregation,
        resolved_input_digests={"gold": "3" * 64},
        resolved_external_digests={"disposition-001": "4" * 64},
    )


def test_coverage_zero_denominator_has_null_rates_and_no_cross_unit_field() -> None:
    value = score_coverage_fixture(
        authoritative_expected_claim_ids=("e1",),
        importance_by_expected_claim_id={"e1": "critical"},
        coverage_state_by_expected_claim_id={},
        applicable_expected_claim_ids=(),
        excluded_expected_claim_ids=("e1",),
    )
    assert value.strata[0].denominator_count == 0
    assert value.strata[0].fully_covered_rate is None
    with pytest.raises(ValidationError):
        value.__class__.model_validate(
            {**value.model_dump(mode="json"), "generated_claim_ids": ("g1",)}
        )


def test_support_is_generated_claim_only_and_keeps_unresolved_out_of_denominator() -> None:
    value = score_support_fixture(
        authoritative_generated_claim_ids=("g1", "g2", "g3", "g4", "g5", "g6"),
        support_state_by_generated_claim_id={
            "g1": "supported",
            "g2": "partially_supported",
            "g3": "unsupported",
            "g4": "contradicted_by_source",
            "g5": "overstated",
            "g6": "unresolved",
        },
        candidate_internal_contradiction_relation_ids=("r1",),
        include_diagnostic_rates=True,
    )
    assert value.authoritative_generated_claim_ids == value.applicable_generated_claim_ids
    assert value.decided_denominator_count == 5
    assert value.unresolved_audit.generated_claim_ids == ("g6",)
    assert len(value.diagnostic_rates) == 5
    assert not hasattr(value, "importance_strata")
    mixed_order = score_support_fixture(
        authoritative_generated_claim_ids=("g2", "g1"),
        support_state_by_generated_claim_id={
            "g2": "unsupported",
            "g1": "supported",
        },
    )
    assert mixed_order.decided_state_counts.supported.generated_claim_ids == ("g1",)
    assert mixed_order.decided_state_counts.unsupported.generated_claim_ids == ("g2",)
    with pytest.raises(ValidationError):
        SupportMetricValue.model_validate(
            {
                **value.model_dump(mode="json"),
                "excluded_generated_claim_ids": [],
            }
        )


def test_support_rejects_expected_claim_shaped_payload_and_exclusion() -> None:
    with pytest.raises(ValidationError):
        SupportMetricValue.model_validate(
            {
                "result_kind": "support_state_counts",
                "authoritative_generated_claim_ids": ["g1"],
                "applicable_generated_claim_ids": ["g1"],
                "decided_denominator_count": 1,
                "decided_state_counts": {
                    "supported": {"count": 1, "generated_claim_ids": ["g1"]},
                    "partially_supported": {"count": 0, "generated_claim_ids": []},
                    "unsupported": {"count": 0, "generated_claim_ids": []},
                    "contradicted_by_source": {"count": 0, "generated_claim_ids": []},
                    "overstated": {"count": 0, "generated_claim_ids": []},
                },
                "unresolved_audit": {"count": 0, "generated_claim_ids": []},
                "candidate_internal_contradiction": {"count": 0, "relation_ids": []},
                "diagnostic_rates": [],
                "expected_claim_ids": ["e1"],
            }
        )


def test_support_rejects_q14_field_name_as_owner_state() -> None:
    with pytest.raises(ValueError):
        score_support_fixture(
            authoritative_generated_claim_ids=("g1",),
            support_state_by_generated_claim_id={"g1": "unresolved_audit"},
        )


def test_support_rejects_exclusion_mismatch_and_partition_errors() -> None:
    contract, registry, scorer, _ = _metric(kind=MetricKind.SUPPORT)
    value = score_support_fixture(
        authoritative_generated_claim_ids=("g1", "g2"),
        support_state_by_generated_claim_id={
            "g1": "supported",
            "g2": "unresolved",
        },
    )
    exclusion = OwnerRecordReference(
        schema_version="q12-exclusion/1.0.0",
        record_type="exclusion",
        record_id="exclusion-001",
        sha256="5" * 64,
    )
    with pytest.raises(ValidationError):
        _fixture(contract, registry, scorer, value, exclusion_ref=exclusion)

    payload = value.model_dump(mode="json")
    payload["applicable_generated_claim_ids"] = []
    with pytest.raises(ValidationError):
        SupportMetricValue.model_validate(payload)

    payload = value.model_dump(mode="json")
    payload["decided_state_counts"]["supported"]["generated_claim_ids"] = ["g1", "g1"]
    payload["decided_state_counts"]["supported"]["count"] = 2
    with pytest.raises(ValidationError):
        SupportMetricValue.model_validate(payload)

    payload = value.model_dump(mode="json")
    payload["unresolved_audit"] = {"count": 0, "generated_claim_ids": []}
    with pytest.raises(ValidationError):
        SupportMetricValue.model_validate(payload)


def test_support_rejects_invalid_diagnostic_rate_value_and_order() -> None:
    value = score_support_fixture(
        authoritative_generated_claim_ids=("g1", "g2"),
        support_state_by_generated_claim_id={
            "g1": "supported",
            "g2": "unsupported",
        },
        include_diagnostic_rates=True,
    )
    payload = value.model_dump(mode="json")
    payload["diagnostic_rates"][0]["state"] = "unresolved"
    with pytest.raises(ValidationError):
        SupportMetricValue.model_validate(payload)

    payload = value.model_dump(mode="json")
    payload["diagnostic_rates"] = list(reversed(payload["diagnostic_rates"]))
    with pytest.raises(ValidationError):
        SupportMetricValue.model_validate(payload)


def test_parser_lane_is_not_realized_in_q14_v1() -> None:
    with pytest.raises(ValidationError):
        MetricContract.model_validate(
            {
                "schema_version": Q14_METRIC_CONTRACT_SCHEMA_VERSION,
                "artifact_role": "metric_contract",
                "metric_contract_id": "parser-v1",
                "metric_contract_version": "1.0.0",
                "metric_kind": "coverage",
                "lane": "parser",
                "scoring_unit": "expected_claim",
                "denominator_semantics": "authority_closed_applicable_units",
                "applicability_consumption": "q12_authoritative_disposition",
                "formula": {
                    "formula_id": "parser-v1",
                    "formula_revision": "1.0.0",
                    "formula_kind": "coverage_state_vector_v1",
                },
                "components": [],
                "required_input_roles": [],
                "aggregation_contract_ref": {
                    "aggregation_contract_id": "a",
                    "aggregation_contract_version": "1.0.0",
                    "sha256": "0" * 64,
                },
            }
        )


def test_fixture_binding_rejects_wrong_contract_digest_and_float_rates() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.COVERAGE)
    value = score_coverage_fixture(
        authoritative_expected_claim_ids=("e1",),
        importance_by_expected_claim_id={"e1": "critical"},
        coverage_state_by_expected_claim_id={"e1": "fully_covered"},
        applicable_expected_claim_ids=("e1",),
        excluded_expected_claim_ids=(),
    )
    result = _fixture(contract, registry, scorer, value)
    broken = result.model_copy(
        update={
            "metric_contract_ref": result.metric_contract_ref.model_copy(
                update={"sha256": "f" * 64}
            )
        }
    )
    with pytest.raises(Q14ContractError):
        validate_fixture_metric_result(
            broken,
            metric_contract=contract,
            metric_registry=registry,
            scorer_contract=scorer,
            aggregation_contract=aggregation,
        )
    with pytest.raises(ValidationError):
        Rational(numerator=1.0, denominator=2)


def test_fixture_binding_rejects_registry_scorer_aggregation_and_revision_mismatch() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.COVERAGE)
    value = score_coverage_fixture(
        authoritative_expected_claim_ids=("e1",),
        importance_by_expected_claim_id={"e1": "critical"},
        coverage_state_by_expected_claim_id={"e1": "fully_covered"},
        applicable_expected_claim_ids=("e1",),
        excluded_expected_claim_ids=(),
    )
    result = _fixture(contract, registry, scorer, value)
    bad_registry_entry = registry.metric_contracts[0].model_copy(
        update={"sha256": "f" * 64}
    )
    bad_registry = registry.model_copy(update={"metric_contracts": (bad_registry_entry,)})
    with pytest.raises(Q14ContractError):
        validate_fixture_metric_result(
            result,
            metric_contract=contract,
            metric_registry=bad_registry,
            scorer_contract=scorer,
            aggregation_contract=aggregation,
            resolved_input_digests={"gold": "3" * 64},
            resolved_external_digests={"disposition-001": "4" * 64},
        )

    bad_scorer = scorer.model_copy(update={"configuration_sha256": "9" * 64})
    with pytest.raises(Q14ContractError):
        validate_fixture_metric_result(
            result,
            metric_contract=contract,
            metric_registry=registry,
            scorer_contract=bad_scorer,
            aggregation_contract=aggregation,
            resolved_input_digests={"gold": "3" * 64},
            resolved_external_digests={"disposition-001": "4" * 64},
        )

    bad_aggregation = aggregation.model_copy(
        update={"aggregation_contract_version": "2.0.0"}
    )
    with pytest.raises(Q14ContractError):
        validate_fixture_metric_result(
            result,
            metric_contract=contract,
            metric_registry=registry,
            scorer_contract=scorer,
            aggregation_contract=bad_aggregation,
            resolved_input_digests={"gold": "3" * 64},
            resolved_external_digests={"disposition-001": "4" * 64},
        )

    stale_revision = _rebuild_fixture(result, benchmark_revision="benchmark-002")
    with pytest.raises(Q14ContractError):
        validate_fixture_metric_result(
            stale_revision,
            metric_contract=contract,
            metric_registry=registry,
            scorer_contract=scorer,
            aggregation_contract=aggregation,
            resolved_input_digests={"gold": "3" * 64},
            resolved_external_digests={"disposition-001": "4" * 64},
        )

    with pytest.raises(Q14ContractError):
        build_fixture_metric_result(
            benchmark_revision="benchmark-002",
            fixture_id="fixture-001",
            fixture_revision="revision-001",
            metric_contract=contract,
            metric_registry=registry,
            scorer_contract=scorer,
            input_artifacts=(
                InputArtifactReference(artifact_role="gold", sha256="3" * 64),
            ),
            applicability_ref=OwnerRecordReference(
                schema_version="q12-disposition/1.0.0",
                record_type="applicability",
                record_id="disposition-001",
                sha256="4" * 64,
            ),
            exclusion_ref=None,
            metric_value=value,
        )


def test_fixture_binding_rejects_required_input_and_resolved_digest_mismatch() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.COVERAGE)
    value = score_coverage_fixture(
        authoritative_expected_claim_ids=("e1",),
        importance_by_expected_claim_id={"e1": "critical"},
        coverage_state_by_expected_claim_id={"e1": "fully_covered"},
        applicable_expected_claim_ids=("e1",),
        excluded_expected_claim_ids=(),
    )
    result = _fixture(contract, registry, scorer, value)
    wrong_role = _rebuild_fixture(
        result,
        input_artifacts=[{"artifact_role": "raw_source", "sha256": "3" * 64}],
    )
    with pytest.raises(Q14ContractError):
        validate_fixture_metric_result(
            wrong_role,
            metric_contract=contract,
            metric_registry=registry,
            scorer_contract=scorer,
            aggregation_contract=aggregation,
            resolved_input_digests={"gold": "3" * 64},
            resolved_external_digests={"disposition-001": "4" * 64},
        )

    with pytest.raises(Q14ContractError):
        validate_fixture_metric_result(
            result,
            metric_contract=contract,
            metric_registry=registry,
            scorer_contract=scorer,
            aggregation_contract=aggregation,
            resolved_input_digests={"gold": "6" * 64},
            resolved_external_digests={"disposition-001": "4" * 64},
        )
    with pytest.raises(Q14ContractError):
        validate_fixture_metric_result(
            result,
            metric_contract=contract,
            metric_registry=registry,
            scorer_contract=scorer,
            aggregation_contract=aggregation,
            resolved_input_digests={"gold": "3" * 64},
            resolved_external_digests={"disposition-001": "6" * 64},
        )


def test_cohort_is_ordered_fixture_vector_and_requires_resolved_children() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.SUPPORT)
    value = score_support_fixture(
        authoritative_generated_claim_ids=("g1",),
        support_state_by_generated_claim_id={"g1": "supported"},
    )
    fixture = _fixture(contract, registry, scorer, value, fixture_id="fixture-001")
    cohort_fields = {
        "schema_version": Q14_COHORT_METRIC_RESULT_SCHEMA_VERSION,
        "artifact_role": "cohort_metric_result",
        "benchmark_revision": "benchmark-001",
        "cohort_id": "cohort-001",
        "cohort_revision": "revision-001",
        "lane": contract.lane,
        "metric_contract_ref": MetricContractReference(
            metric_contract_id=contract.metric_contract_id,
            metric_contract_version=contract.metric_contract_version,
            sha256=metric_contract_sha256(contract),
        ),
        "metric_registry_ref": MetricRegistryReference(
            registry_id=registry.registry_id,
            registry_revision=registry.registry_revision,
            sha256=metric_registry_sha256(registry),
        ),
        "aggregation_contract_ref": AggregationContractReference(
            aggregation_contract_id=aggregation.aggregation_contract_id,
            aggregation_contract_version=aggregation.aggregation_contract_version,
            sha256=aggregation_contract_sha256(aggregation),
        ),
        "fixture_results": (
            FixtureResultReference(
                fixture_id=fixture.fixture_id,
                fixture_revision=fixture.fixture_revision,
                result_sha256=fixture_metric_result_sha256(fixture),
            ),
        ),
        "result_kind": "fixture_vector_only",
        "aggregate": None,
    }
    cohort_id = derive_cohort_metric_result_id(
        {
            key: value.model_dump(mode="json") if hasattr(value, "model_dump") else value
            for key, value in cohort_fields.items()
        }
    )
    cohort = CohortMetricResult(cohort_result_id=cohort_id, **cohort_fields)
    validate_cohort_metric_result(
        cohort,
        metric_contract=contract,
        metric_registry=registry,
        aggregation_contract=aggregation,
        required_fixture_order=(("fixture-001", "revision-001"),),
        resolved_fixture_results={"fixture-001": fixture},
    )
    with pytest.raises(Q14ContractError):
        validate_cohort_metric_result(
            cohort,
            metric_contract=contract,
            metric_registry=registry,
            aggregation_contract=aggregation,
            resolved_fixture_results={},
        )
    assert canonical_q14_bytes(cohort).endswith(b"}")
    assert b"\n" not in canonical_q14_bytes(cohort)
    assert cohort_metric_result_sha256(cohort) == cohort_metric_result_sha256(cohort)


def test_cohort_rejects_order_duplicates_missing_children_aggregate_and_revision() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.SUPPORT)
    value = score_support_fixture(
        authoritative_generated_claim_ids=("g1",),
        support_state_by_generated_claim_id={"g1": "supported"},
    )
    fixture_one = _fixture(contract, registry, scorer, value, fixture_id="fixture-001")
    fixture_two = _fixture(contract, registry, scorer, value, fixture_id="fixture-002")
    refs = tuple(
        FixtureResultReference(
            fixture_id=fixture.fixture_id,
            fixture_revision=fixture.fixture_revision,
            result_sha256=fixture_metric_result_sha256(fixture),
        )
        for fixture in (fixture_one, fixture_two)
    )
    cohort = build_cohort_metric_result(
        benchmark_revision=registry.benchmark_revision,
        cohort_id="cohort-001",
        cohort_revision="revision-001",
        lane=contract.lane,
        metric_contract=contract,
        metric_registry=registry,
        aggregation_contract=aggregation,
        fixture_results=refs,
        resolved_fixture_results={
            fixture_one.fixture_id: fixture_one,
            fixture_two.fixture_id: fixture_two,
        },
    )
    resolved = {
        fixture_one.fixture_id: fixture_one,
        fixture_two.fixture_id: fixture_two,
    }
    with pytest.raises(Q14ContractError):
        validate_cohort_metric_result(
            cohort,
            metric_contract=contract,
            metric_registry=registry,
            aggregation_contract=aggregation,
            required_fixture_order=(
                ("fixture-002", "revision-001"),
                ("fixture-001", "revision-001"),
            ),
            resolved_fixture_results=resolved,
        )
    with pytest.raises(Q14ContractError):
        validate_cohort_metric_result(
            cohort.model_copy(update={"fixture_results": (refs[0], refs[0])}),
            metric_contract=contract,
            metric_registry=registry,
            aggregation_contract=aggregation,
            resolved_fixture_results=resolved,
        )
    with pytest.raises(Q14ContractError):
        validate_cohort_metric_result(
            cohort.model_copy(update={"fixture_results": ()}),
            metric_contract=contract,
            metric_registry=registry,
            aggregation_contract=aggregation,
            resolved_fixture_results=resolved,
        )
    with pytest.raises(Q14ContractError):
        validate_cohort_metric_result(
            cohort.model_copy(update={"aggregate": {"value": 1}}),
            metric_contract=contract,
            metric_registry=registry,
            aggregation_contract=aggregation,
            resolved_fixture_results=resolved,
        )
    stale_cohort = _rebuild_cohort(cohort, benchmark_revision="benchmark-002")
    with pytest.raises(Q14ContractError):
        validate_cohort_metric_result(
            stale_cohort,
            metric_contract=contract,
            metric_registry=registry,
            aggregation_contract=aggregation,
            resolved_fixture_results=resolved,
        )

    stale_child = _rebuild_fixture(fixture_two, benchmark_revision="benchmark-002")
    with pytest.raises(Q14ContractError):
        validate_cohort_metric_result(
            cohort,
            metric_contract=contract,
            metric_registry=registry,
            aggregation_contract=aggregation,
            resolved_fixture_results={
                fixture_one.fixture_id: fixture_one,
                fixture_two.fixture_id: stale_child,
            },
        )


def test_derived_ids_are_validated_again_after_copy_and_canonical_replay() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.SUPPORT)
    value = score_support_fixture(
        authoritative_generated_claim_ids=("g1",),
        support_state_by_generated_claim_id={"g1": "supported"},
    )
    fixture = _fixture(contract, registry, scorer, value)
    with pytest.raises(Q14ContractError):
        validate_fixture_metric_result(
            fixture.model_copy(update={"benchmark_revision": "benchmark-002"}),
            metric_contract=contract,
            metric_registry=registry,
            scorer_contract=scorer,
            aggregation_contract=aggregation,
            resolved_input_digests={"candidate_output": "3" * 64},
            resolved_external_digests={"disposition-001": "4" * 64},
        )
    with pytest.raises(ValidationError):
        FixtureMetricResult.model_validate(
            {
                **fixture.model_dump(mode="json"),
                "result_id": "fixture-result-" + "0" * 64,
            }
        )

    cohort = _cohort_from_fixture(contract, registry, aggregation, fixture)
    with pytest.raises(ValidationError):
        CohortMetricResult.model_validate(
            {
                **cohort.model_dump(mode="json"),
                "cohort_result_id": "cohort-result-" + "0" * 64,
            }
        )
    replay = CohortMetricResult.model_validate(cohort.model_dump(mode="json"))
    assert canonical_q14_bytes(cohort) == canonical_q14_bytes(replay)
    assert cohort_metric_result_sha256(cohort) == cohort_metric_result_sha256(replay)


def test_parser_lane_is_rejected_on_every_realized_q14_surface() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.SUPPORT)
    value = score_support_fixture(
        authoritative_generated_claim_ids=("g1",),
        support_state_by_generated_claim_id={"g1": "supported"},
    )
    fixture = _fixture(contract, registry, scorer, value)
    cohort = _cohort_from_fixture(contract, registry, aggregation, fixture)
    surfaces = (
        (MetricContract, {**contract.model_dump(mode="json"), "lane": "parser"}),
        (
            MetricRegistry,
            {**registry.model_dump(mode="json"), "lane": "parser"},
        ),
        (
            ScorerContract,
            {**scorer.model_dump(mode="json"), "compatible_lanes": ["parser"]},
        ),
        (
            AggregationContract,
            {**aggregation.model_dump(mode="json"), "lane": "parser"},
        ),
        (
            FixtureMetricResult,
            {**fixture.model_dump(mode="json"), "lane": "parser"},
        ),
        (
            CohortMetricResult,
            {**cohort.model_dump(mode="json"), "lane": "parser"},
        ),
    )
    for model_type, payload in surfaces:
        with pytest.raises(ValidationError):
            model_type.model_validate(payload)


def test_derived_ids_use_only_the_frozen_exact_dependency_seeds() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.SUPPORT)
    value = score_support_fixture(
        authoritative_generated_claim_ids=("g1",),
        support_state_by_generated_claim_id={"g1": "supported"},
    )
    fixture = _fixture(contract, registry, scorer, value)
    fixture_payload = fixture.model_dump(mode="json")
    fixture_seed = {
        field: fixture_payload[field] for field in FIXTURE_RESULT_ID_SEED_FIELDS
    }
    independent_fixture_id = "fixture-result-" + hashlib.sha256(
        json.dumps(
            fixture_seed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    assert derive_fixture_metric_result_id(fixture_payload) == independent_fixture_id
    assert derive_fixture_metric_result_id(
        {
            **fixture_payload,
            "artifact_role": "changed-envelope-role",
            "result_id": "fixture-result-" + "f" * 64,
            "result_kind": "non-seed-envelope-field",
        }
    ) == independent_fixture_id
    changed_fixture_dependency = {
        **fixture_payload,
        "fixture_id": "fixture-002",
    }
    assert derive_fixture_metric_result_id(changed_fixture_dependency) != independent_fixture_id

    cohort = _cohort_from_fixture(contract, registry, aggregation, fixture)
    cohort_payload = cohort.model_dump(mode="json")
    cohort_seed = {
        field: cohort_payload[field] for field in COHORT_RESULT_ID_SEED_FIELDS
    }
    independent_cohort_id = "cohort-result-" + hashlib.sha256(
        json.dumps(
            cohort_seed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    assert derive_cohort_metric_result_id(cohort_payload) == independent_cohort_id
    assert derive_cohort_metric_result_id(
        {
            **cohort_payload,
            "artifact_role": "changed-envelope-role",
            "cohort_result_id": "cohort-result-" + "f" * 64,
            "result_kind": "changed-envelope-field",
            "aggregate": {"must": "remain-non-seed"},
        }
    ) == independent_cohort_id
    changed_cohort_dependency = {
        **cohort_payload,
        "cohort_id": "cohort-002",
    }
    assert derive_cohort_metric_result_id(changed_cohort_dependency) != independent_cohort_id


def test_canonicalization_revalidates_all_mutated_q14_artifacts() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.SUPPORT)
    value = score_support_fixture(
        authoritative_generated_claim_ids=("g1",),
        support_state_by_generated_claim_id={"g1": "supported"},
    )
    fixture = _fixture(contract, registry, scorer, value)
    cohort = _cohort_from_fixture(contract, registry, aggregation, fixture)
    mutated_cases = (
        (
            registry.model_copy(
                update={"metric_contracts": registry.metric_contracts * 2}
            ),
            canonical_metric_registry_bytes,
            metric_registry_sha256,
        ),
        (
            scorer.model_copy(
                update={
                    "compatible_lanes": (
                        Q14Lane.END_TO_END,
                        Q14Lane.GENERATION,
                    )
                }
            ),
            canonical_scorer_contract_bytes,
            scorer_contract_sha256,
        ),
        (
            contract.model_copy(update={"components": tuple(reversed(contract.components))}),
            canonical_metric_contract_bytes,
            metric_contract_sha256,
        ),
        (
            aggregation.model_copy(update={"aggregation_kind": "invalid-kind"}),
            canonical_aggregation_contract_bytes,
            aggregation_contract_sha256,
        ),
        (
            aggregation.model_copy(update={"aggregation_contract_version": ""}),
            canonical_aggregation_contract_bytes,
            aggregation_contract_sha256,
        ),
        (
            fixture.model_copy(update={"fixture_revision": "revision-002"}),
            canonical_fixture_metric_result_bytes,
            fixture_metric_result_sha256,
        ),
        (
            cohort.model_copy(update={"cohort_revision": "revision-002"}),
            canonical_cohort_metric_result_bytes,
            cohort_metric_result_sha256,
        ),
    )
    for artifact, canonicalizer, sha256 in mutated_cases:
        with pytest.raises(Q14ContractError):
            canonical_q14_bytes(artifact)
        with pytest.raises(Q14ContractError):
            canonicalizer(artifact)
        with pytest.raises(Q14ContractError):
            sha256(artifact)
        with pytest.raises(Q14ContractError):
            q14_artifact_sha256(artifact)


def test_binding_helpers_revalidate_mutated_parent_contracts() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.SUPPORT)
    bad_contract = contract.model_copy(
        update={"components": tuple(reversed(contract.components))}
    )
    with pytest.raises(Q14ContractError):
        validate_metric_contract_bindings(
            bad_contract,
            aggregation_contract=aggregation,
        )

    bad_registry = registry.model_copy(
        update={"metric_contracts": registry.metric_contracts * 2}
    )
    with pytest.raises(Q14ContractError):
        validate_metric_registry_bindings(
            bad_registry,
            resolved_metric_contracts={
                (contract.metric_contract_id, contract.metric_contract_version): contract
            },
        )

    bad_scorer = scorer.model_copy(
        update={"compatible_lanes": (Q14Lane.END_TO_END, Q14Lane.GENERATION)}
    )
    with pytest.raises(Q14ContractError):
        validate_scorer_contract_bindings(
            bad_scorer,
            resolved_metric_contracts={
                (contract.metric_contract_id, contract.metric_contract_version): contract
            },
        )


def test_public_validation_helpers_revalidate_existing_model_instances() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.SUPPORT)
    mutated = (
        (validate_metric_contract, contract.model_copy(
            update={"components": tuple(reversed(contract.components))}
        )),
        (validate_metric_registry, registry.model_copy(
            update={"metric_contracts": registry.metric_contracts * 2}
        )),
        (validate_scorer_contract, scorer.model_copy(
            update={
                "compatible_lanes": (
                    Q14Lane.END_TO_END,
                    Q14Lane.GENERATION,
                )
            }
        )),
        (validate_aggregation_contract, aggregation.model_copy(
            update={"aggregation_kind": "invalid-kind"}
        )),
    )
    for validator, payload in mutated:
        with pytest.raises(Q14ContractError):
            validator(payload)


def test_generic_and_named_q14_canonical_helpers_enforce_their_boundaries() -> None:
    contract, registry, scorer, aggregation = _metric(kind=MetricKind.SUPPORT)
    value = score_support_fixture(
        authoritative_generated_claim_ids=("g1",),
        support_state_by_generated_claim_id={"g1": "supported"},
    )
    fixture = _fixture(contract, registry, scorer, value)
    cohort = _cohort_from_fixture(contract, registry, aggregation, fixture)
    artifacts = (contract, registry, scorer, aggregation, fixture, cohort)

    for artifact in artifacts:
        replay = type(artifact).model_validate(artifact.model_dump(mode="json"))
        assert canonical_q14_bytes(artifact) == canonical_q14_bytes(replay)
        assert q14_artifact_sha256(artifact) == q14_artifact_sha256(replay)

    typed_helpers = (
        (contract, canonical_metric_contract_bytes, metric_contract_sha256),
        (registry, canonical_metric_registry_bytes, metric_registry_sha256),
        (scorer, canonical_scorer_contract_bytes, scorer_contract_sha256),
        (aggregation, canonical_aggregation_contract_bytes, aggregation_contract_sha256),
        (fixture, canonical_fixture_metric_result_bytes, fixture_metric_result_sha256),
        (cohort, canonical_cohort_metric_result_bytes, cohort_metric_result_sha256),
    )
    for artifact, canonicalizer, sha256 in typed_helpers:
        assert canonicalizer(artifact) == canonical_q14_bytes(artifact)
        assert sha256(artifact) == q14_artifact_sha256(artifact)

    wrong_type_cases = (
        (canonical_metric_contract_bytes, metric_contract_sha256, registry),
        (canonical_metric_registry_bytes, metric_registry_sha256, contract),
        (canonical_scorer_contract_bytes, scorer_contract_sha256, contract),
        (canonical_aggregation_contract_bytes, aggregation_contract_sha256, scorer),
        (canonical_fixture_metric_result_bytes, fixture_metric_result_sha256, cohort),
        (canonical_cohort_metric_result_bytes, cohort_metric_result_sha256, fixture),
    )
    for canonicalizer, sha256, wrong_artifact in wrong_type_cases:
        with pytest.raises(Q14ContractError):
            canonicalizer(wrong_artifact)
        with pytest.raises(Q14ContractError):
            sha256(wrong_artifact)
