"""Q14 deterministic metric contracts, result artifacts, and v1 scorers.

This module realizes only the frozen Generation/End-to-end Q14 contracts.  It
does not create Parser metrics, quality decisions, gates, comparison records,
or collection/repeat semantics owned by other benchmark questions.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from math import gcd
from typing import (
    Annotated,
    Any,
    Callable,
    Iterable,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    ValidationError,
    field_validator,
    model_validator,
)


Q14_METRIC_CONTRACT_SCHEMA_VERSION = "benchmark-q14-metric-contract/1.0.0"
Q14_METRIC_REGISTRY_SCHEMA_VERSION = "benchmark-q14-metric-registry/1.0.0"
Q14_SCORER_CONTRACT_SCHEMA_VERSION = "benchmark-q14-scorer-contract/1.0.0"
Q14_AGGREGATION_CONTRACT_SCHEMA_VERSION = "benchmark-q14-aggregation-contract/1.0.0"
Q14_FIXTURE_METRIC_RESULT_SCHEMA_VERSION = (
    "benchmark-q14-fixture-metric-result/1.0.0"
)
Q14_COHORT_METRIC_RESULT_SCHEMA_VERSION = (
    "benchmark-q14-cohort-metric-result/1.0.0"
)

FIXTURE_RESULT_ID_SEED_FIELDS = (
    "schema_version",
    "benchmark_revision",
    "fixture_id",
    "fixture_revision",
    "lane",
    "metric_contract_ref",
    "metric_registry_ref",
    "scorer_contract_ref",
    "formula_ref",
    "input_artifacts",
    "applicability_ref",
    "exclusion_ref",
    "metric_value",
)
COHORT_RESULT_ID_SEED_FIELDS = (
    "schema_version",
    "benchmark_revision",
    "cohort_id",
    "cohort_revision",
    "lane",
    "metric_contract_ref",
    "metric_registry_ref",
    "aggregation_contract_ref",
    "fixture_results",
)

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_DERIVED_RESULT_PATTERN = r"^fixture-result-[0-9a-f]{64}$"
_DERIVED_COHORT_PATTERN = r"^cohort-result-[0-9a-f]{64}$"
EnumT = TypeVar("EnumT", bound=Enum)


class Q14ContractError(ValueError):
    """Raised when a Q14 contract, result, or binding is invalid."""


class Q14Lane(str, Enum):
    GENERATION = "generation"
    END_TO_END = "end_to_end"


class MetricKind(str, Enum):
    COVERAGE = "coverage"
    SUPPORT = "support"


class ScoringUnit(str, Enum):
    EXPECTED_CLAIM = "expected_claim"
    GENERATED_CLAIM = "generated_claim"


class FormulaKind(str, Enum):
    COVERAGE_STATE_VECTOR_V1 = "coverage_state_vector_v1"
    SUPPORT_STATE_COUNTS_V1 = "support_state_counts_v1"


class DenominatorSemantics(str, Enum):
    AUTHORITY_CLOSED_APPLICABLE_UNITS = "authority_closed_applicable_units"
    Q8_DECIDED_SUPPORT_UNITS = "q8_decided_support_units"


class ApplicabilityConsumption(str, Enum):
    Q12_AUTHORITATIVE_DISPOSITION = "q12_authoritative_disposition"
    Q8_DECIDED_STATE_DISPOSITION = "q8_decided_state_disposition"


class Direction(str, Enum):
    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"
    NON_DIRECTIONAL = "non_directional"


class CanonicalUnit(str, Enum):
    COUNT = "count"
    RATE = "rate"


class NumericRepresentation(str, Enum):
    INTEGER = "integer"
    EXACT_RATIONAL = "exact_rational"
    CANONICAL_DECIMAL = "canonical_decimal"


class InputArtifactRole(str, Enum):
    RAW_SOURCE = "raw_source"
    NORMALIZED_DOCUMENT = "normalized_document"
    REFERENCE_DOCUMENT = "reference_document"
    CANDIDATE_OUTPUT = "candidate_output"
    PRE_RENDER_NOTE = "pre_render_note"
    RENDERED_NOTE_PROJECTION = "rendered_note_projection"
    GOLD = "gold"
    ITEM_DISPOSITION = "item_disposition"
    MAPPING = "mapping"
    PROJECTION = "projection"
    ALIGNMENT = "alignment"


class ImportanceStratum(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class CoverageState(str, Enum):
    FULLY_COVERED = "fully_covered"
    PARTIALLY_COVERED = "partially_covered"
    NOT_COVERED = "not_covered"


class SupportState(str, Enum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    UNSUPPORTED = "unsupported"
    CONTRADICTED_BY_SOURCE = "contradicted_by_source"
    OVERSTATED = "overstated"
    UNRESOLVED = "unresolved"


class AggregationKind(str, Enum):
    FIXTURE_VECTOR_ONLY = "fixture_vector_only"


Q14LaneValue = Annotated[Q14Lane, BeforeValidator(lambda v: _parse_enum(Q14Lane, v))]
MetricKindValue = Annotated[
    MetricKind, BeforeValidator(lambda v: _parse_enum(MetricKind, v))
]
ScoringUnitValue = Annotated[
    ScoringUnit, BeforeValidator(lambda v: _parse_enum(ScoringUnit, v))
]
FormulaKindValue = Annotated[
    FormulaKind, BeforeValidator(lambda v: _parse_enum(FormulaKind, v))
]
DenominatorSemanticsValue = Annotated[
    DenominatorSemantics,
    BeforeValidator(lambda v: _parse_enum(DenominatorSemantics, v)),
]
ApplicabilityConsumptionValue = Annotated[
    ApplicabilityConsumption,
    BeforeValidator(lambda v: _parse_enum(ApplicabilityConsumption, v)),
]
DirectionValue = Annotated[
    Direction, BeforeValidator(lambda v: _parse_enum(Direction, v))
]
CanonicalUnitValue = Annotated[
    CanonicalUnit, BeforeValidator(lambda v: _parse_enum(CanonicalUnit, v))
]
NumericRepresentationValue = Annotated[
    NumericRepresentation,
    BeforeValidator(lambda v: _parse_enum(NumericRepresentation, v)),
]
InputArtifactRoleValue = Annotated[
    InputArtifactRole,
    BeforeValidator(lambda v: _parse_enum(InputArtifactRole, v)),
]
ImportanceStratumValue = Annotated[
    ImportanceStratum,
    BeforeValidator(lambda v: _parse_enum(ImportanceStratum, v)),
]
CoverageStateValue = Annotated[
    CoverageState, BeforeValidator(lambda v: _parse_enum(CoverageState, v))
]
SupportStateValue = Annotated[
    SupportState, BeforeValidator(lambda v: _parse_enum(SupportState, v))
]
AggregationKindValue = Annotated[
    AggregationKind,
    BeforeValidator(lambda v: _parse_enum(AggregationKind, v)),
]


def _parse_enum(enum_type: type[EnumT], value: object) -> EnumT:
    if isinstance(value, enum_type):
        return value
    if isinstance(value, str):
        try:
            return enum_type(value)
        except ValueError as exc:
            raise ValueError(f"unknown {enum_type.__name__} value") from exc
    raise TypeError(f"{enum_type.__name__} requires its exact string value")


def _tuple_from_json(value: object) -> object:
    return tuple(value) if isinstance(value, list) else value


Sha256 = Annotated[StrictStr, Field(pattern=_SHA256_PATTERN)]
Identifier = Annotated[StrictStr, Field(min_length=1)]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]
PositiveInt = Annotated[StrictInt, Field(ge=1)]
DerivedResultId = Annotated[StrictStr, Field(pattern=_DERIVED_RESULT_PATTERN)]
DerivedCohortId = Annotated[StrictStr, Field(pattern=_DERIVED_COHORT_PATTERN)]


class _StrictFrozenQ14Model(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class FormulaReference(_StrictFrozenQ14Model):
    formula_id: Identifier
    formula_revision: Identifier


class MetricContractReference(_StrictFrozenQ14Model):
    metric_contract_id: Identifier
    metric_contract_version: Identifier
    sha256: Sha256


class MetricRegistryReference(_StrictFrozenQ14Model):
    registry_id: Identifier
    registry_revision: Identifier
    sha256: Sha256


class ScorerContractReference(_StrictFrozenQ14Model):
    scorer_contract_id: Identifier
    scorer_contract_version: Identifier
    sha256: Sha256


class AggregationContractReference(_StrictFrozenQ14Model):
    aggregation_contract_id: Identifier
    aggregation_contract_version: Identifier
    sha256: Sha256


class OwnerRecordReference(_StrictFrozenQ14Model):
    schema_version: Identifier
    record_type: Identifier
    record_id: Identifier
    sha256: Sha256


class InputArtifactReference(_StrictFrozenQ14Model):
    artifact_role: InputArtifactRoleValue
    sha256: Sha256


class Rational(_StrictFrozenQ14Model):
    numerator: NonNegativeInt
    denominator: PositiveInt

    @model_validator(mode="after")
    def _lowest_terms(self) -> "Rational":
        if self.numerator == 0:
            if self.denominator != 1:
                raise ValueError("zero rational must use denominator 1")
            return self
        if gcd(self.numerator, self.denominator) != 1:
            raise ValueError("rational must be in lowest terms")
        return self


class MetricComponent(_StrictFrozenQ14Model):
    component_id: Identifier
    direction: DirectionValue
    canonical_unit: CanonicalUnitValue
    numeric_representation: NumericRepresentationValue


class MetricFormula(_StrictFrozenQ14Model):
    formula_id: Identifier
    formula_revision: Identifier
    formula_kind: FormulaKindValue


class MetricContract(_StrictFrozenQ14Model):
    schema_version: Literal["benchmark-q14-metric-contract/1.0.0"]
    artifact_role: Literal["metric_contract"]
    metric_contract_id: Identifier
    metric_contract_version: Identifier
    metric_kind: MetricKindValue
    lane: Q14LaneValue
    scoring_unit: ScoringUnitValue
    denominator_semantics: DenominatorSemanticsValue
    applicability_consumption: ApplicabilityConsumptionValue
    formula: MetricFormula
    components: Tuple[MetricComponent, ...] = Field(min_length=1)
    required_input_roles: Tuple[InputArtifactRoleValue, ...] = Field(min_length=1)
    aggregation_contract_ref: AggregationContractReference

    @field_validator("components", "required_input_roles", mode="before")
    @classmethod
    def _tuples(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_formula_contract(self) -> "MetricContract":
        _require_unique(
            [component.component_id for component in self.components],
            "metric component IDs",
        )
        if not self.components:
            raise ValueError("metric contract requires components")
        role_values = tuple(role.value for role in self.required_input_roles)
        if len(role_values) != len(set(role_values)):
            raise ValueError("required input roles must be unique")
        if tuple(sorted(role_values, key=_input_role_index)) != role_values:
            raise ValueError("required input roles are not in canonical order")

        if self.metric_kind == MetricKind.COVERAGE:
            expected: Tuple[str, ...] = (
                "fully_covered",
                "partially_covered",
                "not_covered",
            )
            if self.scoring_unit != ScoringUnit.EXPECTED_CLAIM:
                raise ValueError("coverage requires expected_claim scoring")
            if self.denominator_semantics != DenominatorSemantics.AUTHORITY_CLOSED_APPLICABLE_UNITS:
                raise ValueError("coverage denominator semantics mismatch")
            if self.applicability_consumption != ApplicabilityConsumption.Q12_AUTHORITATIVE_DISPOSITION:
                raise ValueError("coverage applicability semantics mismatch")
            if self.formula.formula_kind != FormulaKind.COVERAGE_STATE_VECTOR_V1:
                raise ValueError("coverage formula kind mismatch")
        else:
            expected = (
                "supported",
                "partially_supported",
                "unsupported",
                "contradicted_by_source",
                "overstated",
            )
            if self.scoring_unit != ScoringUnit.GENERATED_CLAIM:
                raise ValueError("support requires generated_claim scoring")
            if self.denominator_semantics != DenominatorSemantics.Q8_DECIDED_SUPPORT_UNITS:
                raise ValueError("support denominator semantics mismatch")
            if self.applicability_consumption != ApplicabilityConsumption.Q8_DECIDED_STATE_DISPOSITION:
                raise ValueError("support applicability semantics mismatch")
            if self.formula.formula_kind != FormulaKind.SUPPORT_STATE_COUNTS_V1:
                raise ValueError("support formula kind mismatch")
        actual = tuple(component.component_id for component in self.components)
        if actual != expected:
            raise ValueError("components do not match the closed formula contract")
        return self


class MetricRegistry(_StrictFrozenQ14Model):
    schema_version: Literal["benchmark-q14-metric-registry/1.0.0"]
    artifact_role: Literal["metric_registry"]
    registry_id: Identifier
    registry_revision: Identifier
    benchmark_revision: Identifier
    metric_contracts: Tuple[MetricContractReference, ...] = Field(min_length=1)

    @field_validator("metric_contracts", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_entries(self) -> "MetricRegistry":
        keys = [
            (entry.metric_contract_id, entry.metric_contract_version)
            for entry in self.metric_contracts
        ]
        _require_unique(keys, "metric registry contract entries")
        if tuple(sorted(keys)) != tuple(keys):
            raise ValueError("metric registry entries are not in canonical order")
        return self


class DeterministicRequirements(_StrictFrozenQ14Model):
    execution_mode: Literal["offline_deterministic"]
    network_egress: Literal["forbidden"]
    randomness: Literal["forbidden"]
    binary_float_authority: Literal["forbidden"]
    input_order: Literal["metric_contract_defined"]
    serialization: Literal["benchmark_canonical_json"]


class ScorerContract(_StrictFrozenQ14Model):
    schema_version: Literal["benchmark-q14-scorer-contract/1.0.0"]
    artifact_role: Literal["scorer_contract"]
    scorer_contract_id: Identifier
    scorer_contract_version: Identifier
    implementation_id: Identifier
    implementation_version: Identifier
    implementation_sha256: Sha256
    configuration_sha256: Sha256
    supported_metric_contracts: Tuple[MetricContractReference, ...] = Field(min_length=1)
    compatible_lanes: Tuple[Q14LaneValue, ...]
    deterministic_requirements: DeterministicRequirements
    fixture_result_schema_version: Literal["benchmark-q14-fixture-metric-result/1.0.0"]

    @field_validator("supported_metric_contracts", "compatible_lanes", mode="before")
    @classmethod
    def _tuples(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_compatibility(self) -> "ScorerContract":
        keys = [
            (entry.metric_contract_id, entry.metric_contract_version)
            for entry in self.supported_metric_contracts
        ]
        _require_unique(keys, "supported metric contracts")
        if tuple(sorted(keys)) != tuple(keys):
            raise ValueError("supported metric contracts are not in canonical order")
        lane_values = tuple(lane.value for lane in self.compatible_lanes)
        if not lane_values:
            raise ValueError("scorer contract needs a compatible lane")
        _require_unique(lane_values, "compatible lanes")
        if tuple(sorted(lane_values, key=_lane_index)) != lane_values:
            raise ValueError("compatible lanes are not in canonical order")
        return self


class AggregationContract(_StrictFrozenQ14Model):
    schema_version: Literal["benchmark-q14-aggregation-contract/1.0.0"]
    artifact_role: Literal["aggregation_contract"]
    aggregation_contract_id: Identifier
    aggregation_contract_version: Identifier
    input_metric_result_schema_version: Literal["benchmark-q14-fixture-metric-result/1.0.0"]
    aggregation_kind: AggregationKindValue
    formal_output: Literal["ordered_fixture_vector"]

    @model_validator(mode="after")
    def _validate_kind(self) -> "AggregationContract":
        if self.aggregation_kind != AggregationKind.FIXTURE_VECTOR_ONLY:
            raise ValueError("only fixture_vector_only is realized in Q14 v1")
        return self


class CountedExpectedClaims(_StrictFrozenQ14Model):
    count: NonNegativeInt
    expected_claim_ids: Tuple[Identifier, ...]

    @field_validator("expected_claim_ids", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_count(self) -> "CountedExpectedClaims":
        _require_unique(self.expected_claim_ids, "expected claim IDs")
        if self.count != len(self.expected_claim_ids):
            raise ValueError("expected claim count does not match IDs")
        return self


class CountedGeneratedClaims(_StrictFrozenQ14Model):
    count: NonNegativeInt
    generated_claim_ids: Tuple[Identifier, ...]

    @field_validator("generated_claim_ids", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_count(self) -> "CountedGeneratedClaims":
        _require_unique(self.generated_claim_ids, "generated claim IDs")
        if self.count != len(self.generated_claim_ids):
            raise ValueError("generated claim count does not match IDs")
        return self


class CoverageStratumVector(_StrictFrozenQ14Model):
    stratum: ImportanceStratumValue
    authoritative_expected_claim_ids: Tuple[Identifier, ...]
    applicable_expected_claim_ids: Tuple[Identifier, ...]
    excluded_expected_claim_ids: Tuple[Identifier, ...]
    denominator_count: NonNegativeInt
    fully_covered: CountedExpectedClaims
    partially_covered: CountedExpectedClaims
    not_covered: CountedExpectedClaims
    fully_covered_rate: Optional[Rational]
    partially_covered_rate: Optional[Rational]
    not_covered_rate: Optional[Rational]

    @field_validator(
        "authoritative_expected_claim_ids",
        "applicable_expected_claim_ids",
        "excluded_expected_claim_ids",
        mode="before",
    )
    @classmethod
    def _tuples(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_partition(self) -> "CoverageStratumVector":
        _require_unique(self.authoritative_expected_claim_ids, "authoritative expected IDs")
        _require_unique(self.applicable_expected_claim_ids, "applicable expected IDs")
        _require_unique(self.excluded_expected_claim_ids, "excluded expected IDs")
        authoritative = set(self.authoritative_expected_claim_ids)
        applicable = set(self.applicable_expected_claim_ids)
        excluded = set(self.excluded_expected_claim_ids)
        if applicable & excluded:
            raise ValueError("applicable and excluded expected claims overlap")
        if authoritative != applicable | excluded:
            raise ValueError("coverage authority is not applicable plus excluded")
        _require_subsequence(self.authoritative_expected_claim_ids, self.applicable_expected_claim_ids, "applicable expected IDs")
        _require_subsequence(self.authoritative_expected_claim_ids, self.excluded_expected_claim_ids, "excluded expected IDs")
        if self.denominator_count != len(applicable):
            raise ValueError("coverage denominator does not match applicable IDs")
        state_groups = (
            self.fully_covered.expected_claim_ids,
            self.partially_covered.expected_claim_ids,
            self.not_covered.expected_claim_ids,
        )
        state_ids = _flatten_unique(state_groups, "coverage state IDs")
        if set(state_ids) != applicable:
            raise ValueError("coverage states do not partition applicable expected IDs")
        for state_group in state_groups:
            _require_subsequence(
                self.applicable_expected_claim_ids,
                state_group,
                "coverage state IDs",
            )
        if sum(group.count for group in (self.fully_covered, self.partially_covered, self.not_covered)) != self.denominator_count:
            raise ValueError("coverage state counts do not sum to denominator")
        _validate_rate(self.fully_covered_rate, self.fully_covered.count, self.denominator_count, "fully covered")
        _validate_rate(self.partially_covered_rate, self.partially_covered.count, self.denominator_count, "partially covered")
        _validate_rate(self.not_covered_rate, self.not_covered.count, self.denominator_count, "not covered")
        return self


class CoverageMetricValue(_StrictFrozenQ14Model):
    result_kind: Literal["coverage_state_vector"]
    strata: Tuple[CoverageStratumVector, ...]

    @field_validator("strata", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_strata(self) -> "CoverageMetricValue":
        expected = tuple(item.value for item in ImportanceStratum)
        actual = tuple(item.stratum.value for item in self.strata)
        if actual != expected:
            raise ValueError("coverage strata must be critical, major, minor")
        all_authoritative = _flatten_unique(
            (item.authoritative_expected_claim_ids for item in self.strata),
            "coverage authoritative IDs",
        )
        all_applicable = _flatten_unique(
            (item.applicable_expected_claim_ids for item in self.strata),
            "coverage applicable IDs",
        )
        all_excluded = _flatten_unique(
            (item.excluded_expected_claim_ids for item in self.strata),
            "coverage excluded IDs",
        )
        if set(all_authoritative) != set(all_applicable) | set(all_excluded):
            raise ValueError("coverage strata do not describe one complete authority")
        return self


class SupportDecidedStateCounts(_StrictFrozenQ14Model):
    supported: CountedGeneratedClaims
    partially_supported: CountedGeneratedClaims
    unsupported: CountedGeneratedClaims
    contradicted_by_source: CountedGeneratedClaims
    overstated: CountedGeneratedClaims


class CandidateInternalContradiction(_StrictFrozenQ14Model):
    count: NonNegativeInt
    relation_ids: Tuple[Identifier, ...]

    @field_validator("relation_ids", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_count(self) -> "CandidateInternalContradiction":
        _require_unique(self.relation_ids, "contradiction relation IDs")
        if self.count != len(self.relation_ids):
            raise ValueError("contradiction count does not match relation IDs")
        return self


class DiagnosticRate(_StrictFrozenQ14Model):
    state: SupportStateValue
    rate: Rational

    @model_validator(mode="after")
    def _decided_only(self) -> "DiagnosticRate":
        if self.state == SupportState.UNRESOLVED:
            raise ValueError("unresolved is not a diagnostic decided-state rate")
        return self


class SupportMetricValue(_StrictFrozenQ14Model):
    result_kind: Literal["support_state_counts"]
    authoritative_generated_claim_ids: Tuple[Identifier, ...]
    applicable_generated_claim_ids: Tuple[Identifier, ...]
    decided_denominator_count: NonNegativeInt
    decided_state_counts: SupportDecidedStateCounts
    unresolved_audit: CountedGeneratedClaims
    candidate_internal_contradiction: CandidateInternalContradiction
    diagnostic_rates: Tuple[DiagnosticRate, ...]

    @field_validator(
        "authoritative_generated_claim_ids",
        "applicable_generated_claim_ids",
        "diagnostic_rates",
        mode="before",
    )
    @classmethod
    def _tuples(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_partition(self) -> "SupportMetricValue":
        _require_unique(self.authoritative_generated_claim_ids, "authoritative generated IDs")
        _require_unique(self.applicable_generated_claim_ids, "applicable generated IDs")
        if self.authoritative_generated_claim_ids != self.applicable_generated_claim_ids:
            raise ValueError("support authoritative and applicable IDs must be identical")
        groups = (
            self.decided_state_counts.supported.generated_claim_ids,
            self.decided_state_counts.partially_supported.generated_claim_ids,
            self.decided_state_counts.unsupported.generated_claim_ids,
            self.decided_state_counts.contradicted_by_source.generated_claim_ids,
            self.decided_state_counts.overstated.generated_claim_ids,
            self.unresolved_audit.generated_claim_ids,
        )
        all_ids = _flatten_unique(groups, "support partition IDs")
        if set(all_ids) != set(self.authoritative_generated_claim_ids):
            raise ValueError("support states do not partition authoritative generated IDs")
        for state_group in groups:
            _require_subsequence(
                self.authoritative_generated_claim_ids,
                state_group,
                "support partition IDs",
            )
        decided_counts = (
            self.decided_state_counts.supported.count,
            self.decided_state_counts.partially_supported.count,
            self.decided_state_counts.unsupported.count,
            self.decided_state_counts.contradicted_by_source.count,
            self.decided_state_counts.overstated.count,
        )
        if sum(decided_counts) != self.decided_denominator_count:
            raise ValueError("support decided denominator mismatch")
        if self.decided_denominator_count == 0 and self.diagnostic_rates:
            raise ValueError("zero decided denominator cannot have diagnostic rates")
        states = tuple(
            rate.state.value for rate in self.diagnostic_rates
        )
        _require_unique(states, "diagnostic rate states")
        if tuple(sorted(states, key=_support_state_index)) != states:
            raise ValueError("diagnostic rates are not in Q8 decided-state order")
        count_by_state = dict(zip(_SUPPORT_DECIDED_STATE_ORDER, decided_counts))
        for rate in self.diagnostic_rates:
            _validate_rate(
                rate.rate,
                count_by_state[rate.state.value],
                self.decided_denominator_count,
                f"diagnostic {rate.state.value}",
            )
        return self


MetricValue = Annotated[
    Union[CoverageMetricValue, SupportMetricValue],
    Field(discriminator="result_kind"),
]


class FixtureMetricResult(_StrictFrozenQ14Model):
    schema_version: Literal["benchmark-q14-fixture-metric-result/1.0.0"]
    artifact_role: Literal["fixture_metric_result"]
    result_id: DerivedResultId
    benchmark_revision: Identifier
    fixture_id: Identifier
    fixture_revision: Identifier
    lane: Q14LaneValue
    metric_contract_ref: MetricContractReference
    metric_registry_ref: MetricRegistryReference
    scorer_contract_ref: ScorerContractReference
    formula_ref: FormulaReference
    input_artifacts: Tuple[InputArtifactReference, ...]
    applicability_ref: OwnerRecordReference
    exclusion_ref: Optional[OwnerRecordReference]
    metric_value: MetricValue

    @field_validator("input_artifacts", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_identity_and_roles(self) -> "FixtureMetricResult":
        roles = tuple(item.artifact_role.value for item in self.input_artifacts)
        _require_unique(roles, "input artifact roles")
        if tuple(sorted(roles, key=_input_role_index)) != roles:
            raise ValueError("input artifacts are not in canonical role order")
        if self.metric_value.result_kind == "coverage_state_vector":
            if self.exclusion_ref is None:
                # A null exclusion is legal only when the owner disposition has
                # no exclusion record; Q14 does not infer that state here.
                pass
        else:
            if self.exclusion_ref is not None:
                raise ValueError("support fixture results require exclusion_ref=null")
        expected = derive_fixture_metric_result_id(
            self.model_dump(mode="json", exclude={"result_id"})
        )
        if self.result_id != expected:
            raise ValueError("fixture result_id is not the frozen derived identity")
        return self


class FixtureResultReference(_StrictFrozenQ14Model):
    fixture_id: Identifier
    fixture_revision: Identifier
    result_sha256: Sha256


class CohortMetricResult(_StrictFrozenQ14Model):
    schema_version: Literal["benchmark-q14-cohort-metric-result/1.0.0"]
    artifact_role: Literal["cohort_metric_result"]
    cohort_result_id: DerivedCohortId
    benchmark_revision: Identifier
    cohort_id: Identifier
    cohort_revision: Identifier
    lane: Q14LaneValue
    metric_contract_ref: MetricContractReference
    metric_registry_ref: MetricRegistryReference
    aggregation_contract_ref: AggregationContractReference
    fixture_results: Tuple[FixtureResultReference, ...] = Field(min_length=1)
    result_kind: Literal["fixture_vector_only"]
    aggregate: Literal[None]

    @field_validator("fixture_results", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_identity(self) -> "CohortMetricResult":
        keys = [(item.fixture_id, item.fixture_revision) for item in self.fixture_results]
        _require_unique(keys, "cohort fixture results")
        expected = derive_cohort_metric_result_id(
            self.model_dump(mode="json", exclude={"cohort_result_id"})
        )
        if self.cohort_result_id != expected:
            raise ValueError("cohort_result_id is not the frozen derived identity")
        return self


def _require_unique(values: Iterable[Any], label: str) -> None:
    values_tuple = tuple(values)
    if len(values_tuple) != len(set(values_tuple)):
        raise ValueError(f"{label} must be unique")


def _flatten_unique(groups: Iterable[Iterable[str]], label: str) -> Tuple[str, ...]:
    values = tuple(value for group in groups for value in group)
    _require_unique(values, label)
    return values


def _require_subsequence(authoritative: Sequence[str], candidate: Sequence[str], label: str) -> None:
    positions = {value: index for index, value in enumerate(authoritative)}
    try:
        candidate_positions = tuple(positions[value] for value in candidate)
    except KeyError as exc:
        raise ValueError(f"{label} contains an ID outside authority") from exc
    if candidate_positions != tuple(sorted(candidate_positions)):
        raise ValueError(f"{label} does not preserve authority order")


def _validate_rate(rate: Optional[Rational], numerator: int, denominator: int, label: str) -> None:
    if denominator == 0:
        if rate is not None:
            raise ValueError(f"{label} rate must be null for zero denominator")
        return
    if rate is None:
        raise ValueError(f"{label} rate is required")
    expected = _make_rational(numerator, denominator)
    if rate != expected:
        raise ValueError(f"{label} rate does not match its exact count")


_INPUT_ROLE_ORDER = tuple(item.value for item in InputArtifactRole)
_LANE_ORDER = tuple(item.value for item in Q14Lane)
_SUPPORT_DECIDED_STATE_ORDER = (
    SupportState.SUPPORTED.value,
    SupportState.PARTIALLY_SUPPORTED.value,
    SupportState.UNSUPPORTED.value,
    SupportState.CONTRADICTED_BY_SOURCE.value,
    SupportState.OVERSTATED.value,
)


def _input_role_index(value: str) -> int:
    return _INPUT_ROLE_ORDER.index(value)


def _lane_index(value: str) -> int:
    return _LANE_ORDER.index(value)


def _support_state_index(value: str) -> int:
    return _SUPPORT_DECIDED_STATE_ORDER.index(value)


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Mapping):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _model_payload(value: BaseModel) -> Mapping[str, Any]:
    return value.model_dump(mode="json")


Q14Artifact = Union[
    MetricContract,
    MetricRegistry,
    ScorerContract,
    AggregationContract,
    FixtureMetricResult,
    CohortMetricResult,
]


def _coerce_q14_artifact(payload: Any) -> Q14Artifact:
    if isinstance(payload, BaseModel):
        # Python-mode dumping avoids serializer warnings for deliberately
        # mutated model_copy instances; exact schema validation happens next.
        payload = payload.model_dump(mode="python", warnings=False)
    if not isinstance(payload, Mapping):
        raise TypeError("Q14 canonicalization requires a Q14 model or mapping")
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, str):
        raise Q14ContractError("Q14 payload is missing schema_version")
    schema_models = {
        Q14_METRIC_CONTRACT_SCHEMA_VERSION: MetricContract,
        Q14_METRIC_REGISTRY_SCHEMA_VERSION: MetricRegistry,
        Q14_SCORER_CONTRACT_SCHEMA_VERSION: ScorerContract,
        Q14_AGGREGATION_CONTRACT_SCHEMA_VERSION: AggregationContract,
        Q14_FIXTURE_METRIC_RESULT_SCHEMA_VERSION: FixtureMetricResult,
        Q14_COHORT_METRIC_RESULT_SCHEMA_VERSION: CohortMetricResult,
    }
    model_type = schema_models.get(schema_version)
    if model_type is None:
        raise Q14ContractError("unknown Q14 schema version")
    try:
        return model_type.model_validate(payload)
    except ValidationError as exc:
        raise Q14ContractError(
            f"invalid {schema_version} artifact cannot be canonicalized"
        ) from exc


def _coerce_q14_type(payload: Any, expected_type: Any) -> Any:
    artifact = _coerce_q14_artifact(payload)
    if not isinstance(artifact, expected_type):
        raise Q14ContractError(
            f"expected {expected_type.__name__}, got {type(artifact).__name__}"
        )
    return artifact


def canonical_q14_bytes(payload: Any) -> bytes:
    """Return Q14 canonical UTF-8 JSON bytes without a trailing newline."""

    return _canonical_json_bytes(_model_payload(_coerce_q14_artifact(payload)))


def q14_artifact_sha256(payload: Any) -> str:
    return hashlib.sha256(canonical_q14_bytes(payload)).hexdigest()


def canonical_metric_contract_bytes(payload: MetricContract) -> bytes:
    return canonical_q14_bytes(payload)


def canonical_metric_registry_bytes(payload: MetricRegistry) -> bytes:
    return canonical_q14_bytes(payload)


def canonical_scorer_contract_bytes(payload: ScorerContract) -> bytes:
    return canonical_q14_bytes(payload)


def canonical_aggregation_contract_bytes(payload: AggregationContract) -> bytes:
    return canonical_q14_bytes(payload)


def canonical_fixture_metric_result_bytes(payload: FixtureMetricResult) -> bytes:
    return canonical_q14_bytes(payload)


def canonical_cohort_metric_result_bytes(payload: CohortMetricResult) -> bytes:
    return canonical_q14_bytes(payload)


def metric_contract_sha256(payload: MetricContract) -> str:
    return q14_artifact_sha256(payload)


def metric_registry_sha256(payload: MetricRegistry) -> str:
    return q14_artifact_sha256(payload)


def scorer_contract_sha256(payload: ScorerContract) -> str:
    return q14_artifact_sha256(payload)


def aggregation_contract_sha256(payload: AggregationContract) -> str:
    return q14_artifact_sha256(payload)


def fixture_metric_result_sha256(payload: FixtureMetricResult) -> str:
    return q14_artifact_sha256(payload)


def cohort_metric_result_sha256(payload: CohortMetricResult) -> str:
    return q14_artifact_sha256(payload)


def validate_metric_contract_bindings(
    metric_contract: MetricContract,
    *,
    aggregation_contract: AggregationContract,
) -> MetricContract:
    metric_contract = _coerce_q14_type(metric_contract, MetricContract)
    aggregation_contract = _coerce_q14_type(aggregation_contract, AggregationContract)
    ref = metric_contract.aggregation_contract_ref
    if (
        ref.aggregation_contract_id != aggregation_contract.aggregation_contract_id
        or ref.aggregation_contract_version != aggregation_contract.aggregation_contract_version
        or ref.sha256 != aggregation_contract_sha256(aggregation_contract)
    ):
        raise Q14ContractError("metric contract aggregation reference mismatch")
    return metric_contract


def validate_metric_registry_bindings(
    registry: MetricRegistry,
    *,
    resolved_metric_contracts: Mapping[Tuple[str, str], MetricContract],
) -> MetricRegistry:
    registry = _coerce_q14_type(registry, MetricRegistry)
    for ref in registry.metric_contracts:
        contract = resolved_metric_contracts.get(
            (ref.metric_contract_id, ref.metric_contract_version)
        )
        if contract is None or metric_contract_sha256(contract) != ref.sha256:
            raise Q14ContractError(
                f"metric registry entry does not resolve: {ref.metric_contract_id}"
            )
    return registry


def validate_scorer_contract_bindings(
    scorer_contract: ScorerContract,
    *,
    resolved_metric_contracts: Mapping[Tuple[str, str], MetricContract],
) -> ScorerContract:
    scorer_contract = _coerce_q14_type(scorer_contract, ScorerContract)
    for ref in scorer_contract.supported_metric_contracts:
        contract = resolved_metric_contracts.get(
            (ref.metric_contract_id, ref.metric_contract_version)
        )
        if contract is None or metric_contract_sha256(contract) != ref.sha256:
            raise Q14ContractError(
                f"scorer contract entry does not resolve: {ref.metric_contract_id}"
            )
    return scorer_contract


def _exact_id_seed(payload: Any, fields: Sequence[str], label: str) -> Mapping[str, Any]:
    seed_payload = _jsonable(payload)
    if not isinstance(seed_payload, Mapping):
        raise Q14ContractError(f"{label} identity seed requires a mapping")
    missing = tuple(field for field in fields if field not in seed_payload)
    if missing:
        raise Q14ContractError(
            f"{label} identity seed is missing fields: {', '.join(missing)}"
        )
    return {field: seed_payload[field] for field in fields}


def derive_fixture_metric_result_id(payload: Any) -> str:
    seed = _exact_id_seed(
        payload,
        FIXTURE_RESULT_ID_SEED_FIELDS,
        "fixture metric result",
    )
    return "fixture-result-" + hashlib.sha256(_canonical_json_bytes(seed)).hexdigest()


def derive_cohort_metric_result_id(payload: Any) -> str:
    seed = _exact_id_seed(
        payload,
        COHORT_RESULT_ID_SEED_FIELDS,
        "cohort metric result",
    )
    return "cohort-result-" + hashlib.sha256(_canonical_json_bytes(seed)).hexdigest()


def _revalidate_fixture_metric_result(
    result: FixtureMetricResult,
) -> FixtureMetricResult:
    """Re-run frozen validation for objects altered through model_copy/update."""

    return _coerce_q14_type(result, FixtureMetricResult)


def _revalidate_cohort_metric_result(
    result: CohortMetricResult,
) -> CohortMetricResult:
    """Re-run frozen validation for objects altered through model_copy/update."""

    return _coerce_q14_type(result, CohortMetricResult)


def build_fixture_metric_result(
    *,
    benchmark_revision: str,
    fixture_id: str,
    fixture_revision: str,
    metric_contract: MetricContract,
    metric_registry: MetricRegistry,
    scorer_contract: ScorerContract,
    input_artifacts: Sequence[InputArtifactReference],
    applicability_ref: OwnerRecordReference,
    exclusion_ref: Optional[OwnerRecordReference],
    metric_value: Union[CoverageMetricValue, SupportMetricValue],
) -> FixtureMetricResult:
    """Materialize a fixture result without adding an unowned policy field."""

    metric_contract = _coerce_q14_type(metric_contract, MetricContract)
    metric_registry = _coerce_q14_type(metric_registry, MetricRegistry)
    scorer_contract = _coerce_q14_type(scorer_contract, ScorerContract)
    if benchmark_revision != metric_registry.benchmark_revision:
        raise Q14ContractError("fixture benchmark revision differs from metric registry")
    if metric_value.result_kind == "coverage_state_vector" and metric_contract.metric_kind != MetricKind.COVERAGE:
        raise Q14ContractError("coverage value requires a coverage metric contract")
    if metric_value.result_kind == "support_state_counts" and metric_contract.metric_kind != MetricKind.SUPPORT:
        raise Q14ContractError("support value requires a support metric contract")
    fields = {
        "schema_version": Q14_FIXTURE_METRIC_RESULT_SCHEMA_VERSION,
        "artifact_role": "fixture_metric_result",
        "benchmark_revision": benchmark_revision,
        "fixture_id": fixture_id,
        "fixture_revision": fixture_revision,
        "lane": metric_contract.lane,
        "metric_contract_ref": MetricContractReference(
            metric_contract_id=metric_contract.metric_contract_id,
            metric_contract_version=metric_contract.metric_contract_version,
            sha256=metric_contract_sha256(metric_contract),
        ),
        "metric_registry_ref": MetricRegistryReference(
            registry_id=metric_registry.registry_id,
            registry_revision=metric_registry.registry_revision,
            sha256=metric_registry_sha256(metric_registry),
        ),
        "scorer_contract_ref": ScorerContractReference(
            scorer_contract_id=scorer_contract.scorer_contract_id,
            scorer_contract_version=scorer_contract.scorer_contract_version,
            sha256=scorer_contract_sha256(scorer_contract),
        ),
        "formula_ref": FormulaReference(
            formula_id=metric_contract.formula.formula_id,
            formula_revision=metric_contract.formula.formula_revision,
        ),
        "input_artifacts": tuple(input_artifacts),
        "applicability_ref": applicability_ref,
        "exclusion_ref": exclusion_ref,
        "metric_value": metric_value,
    }
    seed = _jsonable(fields)
    seed["result_id"] = derive_fixture_metric_result_id(seed)
    return FixtureMetricResult.model_validate(seed)


def build_cohort_metric_result(
    *,
    benchmark_revision: str,
    cohort_id: str,
    cohort_revision: str,
    lane: Q14Lane,
    metric_contract: MetricContract,
    metric_registry: MetricRegistry,
    aggregation_contract: AggregationContract,
    fixture_results: Sequence[FixtureResultReference],
    resolved_fixture_results: Mapping[str, FixtureMetricResult],
) -> CohortMetricResult:
    """Materialize the ordered, non-aggregating v1 cohort vector."""

    metric_contract = _coerce_q14_type(metric_contract, MetricContract)
    metric_registry = _coerce_q14_type(metric_registry, MetricRegistry)
    aggregation_contract = _coerce_q14_type(aggregation_contract, AggregationContract)
    if benchmark_revision != metric_registry.benchmark_revision:
        raise Q14ContractError("cohort benchmark revision differs from metric registry")
    fields = {
        "schema_version": Q14_COHORT_METRIC_RESULT_SCHEMA_VERSION,
        "artifact_role": "cohort_metric_result",
        "benchmark_revision": benchmark_revision,
        "cohort_id": cohort_id,
        "cohort_revision": cohort_revision,
        "lane": lane,
        "metric_contract_ref": MetricContractReference(
            metric_contract_id=metric_contract.metric_contract_id,
            metric_contract_version=metric_contract.metric_contract_version,
            sha256=metric_contract_sha256(metric_contract),
        ),
        "metric_registry_ref": MetricRegistryReference(
            registry_id=metric_registry.registry_id,
            registry_revision=metric_registry.registry_revision,
            sha256=metric_registry_sha256(metric_registry),
        ),
        "aggregation_contract_ref": AggregationContractReference(
            aggregation_contract_id=aggregation_contract.aggregation_contract_id,
            aggregation_contract_version=aggregation_contract.aggregation_contract_version,
            sha256=aggregation_contract_sha256(aggregation_contract),
        ),
        "fixture_results": tuple(fixture_results),
        "result_kind": "fixture_vector_only",
        "aggregate": None,
    }
    seed = _jsonable(fields)
    seed["cohort_result_id"] = derive_cohort_metric_result_id(seed)
    result = CohortMetricResult.model_validate(seed)
    return validate_cohort_metric_result(
        result,
        metric_contract=metric_contract,
        metric_registry=metric_registry,
        aggregation_contract=aggregation_contract,
        required_fixture_order=tuple(
            (item.fixture_id, item.fixture_revision) for item in fixture_results
        ),
        resolved_fixture_results=resolved_fixture_results,
    )


def _resolved_digest(
    ref: OwnerRecordReference,
    resolved_external_digests: Optional[Mapping[str, str]],
) -> None:
    if resolved_external_digests is None:
        return
    actual = resolved_external_digests.get(ref.record_id)
    if actual is None or actual != ref.sha256:
        raise Q14ContractError(f"unresolved or mismatched owner record: {ref.record_id}")


def validate_fixture_metric_result(
    result: FixtureMetricResult,
    *,
    metric_contract: MetricContract,
    metric_registry: MetricRegistry,
    scorer_contract: ScorerContract,
    aggregation_contract: AggregationContract,
    resolved_input_digests: Optional[Mapping[str, str]] = None,
    resolved_external_digests: Optional[Mapping[str, str]] = None,
) -> FixtureMetricResult:
    """Validate a fixture result against all resolved Q14 dependencies.

    The optional digest maps are explicit resolver boundaries.  When supplied,
    every referenced input role and owner record must resolve to its declared
    digest; Q14 never derives those records from a RunPlan or a slot.
    """

    result = _revalidate_fixture_metric_result(result)
    metric_contract = _coerce_q14_type(metric_contract, MetricContract)
    metric_registry = _coerce_q14_type(metric_registry, MetricRegistry)
    scorer_contract = _coerce_q14_type(scorer_contract, ScorerContract)
    aggregation_contract = _coerce_q14_type(aggregation_contract, AggregationContract)
    if result.benchmark_revision != metric_registry.benchmark_revision:
        raise Q14ContractError("fixture benchmark revision differs from metric registry")
    if result.lane != metric_contract.lane:
        raise Q14ContractError("fixture lane does not match metric contract")
    if result.metric_contract_ref.metric_contract_id != metric_contract.metric_contract_id or result.metric_contract_ref.metric_contract_version != metric_contract.metric_contract_version:
        raise Q14ContractError("metric contract identity mismatch")
    if result.metric_contract_ref.sha256 != metric_contract_sha256(metric_contract):
        raise Q14ContractError("metric contract digest mismatch")
    if result.metric_registry_ref.registry_id != metric_registry.registry_id or result.metric_registry_ref.registry_revision != metric_registry.registry_revision:
        raise Q14ContractError("metric registry identity mismatch")
    if result.metric_registry_ref.sha256 != metric_registry_sha256(metric_registry):
        raise Q14ContractError("metric registry digest mismatch")
    registry_ref = next(
        (
            ref
            for ref in metric_registry.metric_contracts
            if ref.metric_contract_id == metric_contract.metric_contract_id
            and ref.metric_contract_version == metric_contract.metric_contract_version
        ),
        None,
    )
    if registry_ref is None or registry_ref.sha256 != result.metric_contract_ref.sha256:
        raise Q14ContractError("metric registry does not select the exact metric contract")
    if result.scorer_contract_ref.scorer_contract_id != scorer_contract.scorer_contract_id or result.scorer_contract_ref.scorer_contract_version != scorer_contract.scorer_contract_version:
        raise Q14ContractError("scorer contract identity mismatch")
    if result.scorer_contract_ref.sha256 != scorer_contract_sha256(scorer_contract):
        raise Q14ContractError("scorer contract digest mismatch")
    if result.lane not in scorer_contract.compatible_lanes:
        raise Q14ContractError("scorer contract is incompatible with fixture lane")
    scorer_ref = next(
        (
            ref
            for ref in scorer_contract.supported_metric_contracts
            if ref.metric_contract_id == metric_contract.metric_contract_id
            and ref.metric_contract_version == metric_contract.metric_contract_version
        ),
        None,
    )
    if scorer_ref is None or scorer_ref.sha256 != result.metric_contract_ref.sha256:
        raise Q14ContractError("scorer contract does not support the exact metric digest")
    aggregation_ref = metric_contract.aggregation_contract_ref
    if aggregation_ref.aggregation_contract_id != aggregation_contract.aggregation_contract_id or aggregation_ref.aggregation_contract_version != aggregation_contract.aggregation_contract_version:
        raise Q14ContractError("aggregation contract identity mismatch")
    if aggregation_ref.sha256 != aggregation_contract_sha256(aggregation_contract):
        raise Q14ContractError("aggregation contract digest mismatch")
    if result.metric_value.result_kind == "coverage_state_vector":
        if metric_contract.metric_kind != MetricKind.COVERAGE or metric_contract.scoring_unit != ScoringUnit.EXPECTED_CLAIM:
            raise Q14ContractError("coverage payload is bound to a non-coverage contract")
    else:
        if metric_contract.metric_kind != MetricKind.SUPPORT or metric_contract.scoring_unit != ScoringUnit.GENERATED_CLAIM:
            raise Q14ContractError("support payload is bound to a non-support contract")
        if result.exclusion_ref is not None:
            raise Q14ContractError("support result cannot bind an exclusion record")
    if result.formula_ref.formula_id != metric_contract.formula.formula_id or result.formula_ref.formula_revision != metric_contract.formula.formula_revision:
        raise Q14ContractError("formula reference mismatch")
    roles = tuple(item.artifact_role for item in result.input_artifacts)
    if roles != metric_contract.required_input_roles:
        raise Q14ContractError("fixture input roles do not exactly match metric contract")
    if resolved_input_digests is None:
        raise Q14ContractError("input artifact digests must resolve before validation")
    for item in result.input_artifacts:
        actual = resolved_input_digests.get(item.artifact_role.value)
        if actual is None or actual != item.sha256:
            raise Q14ContractError(f"input digest mismatch for {item.artifact_role.value}")
    if resolved_external_digests is None:
        raise Q14ContractError("owner record digests must resolve before validation")
    _resolved_digest(result.applicability_ref, resolved_external_digests)
    if result.exclusion_ref is not None:
        _resolved_digest(result.exclusion_ref, resolved_external_digests)
    return result


def validate_cohort_metric_result(
    result: CohortMetricResult,
    *,
    metric_contract: MetricContract,
    metric_registry: MetricRegistry,
    aggregation_contract: AggregationContract,
    required_fixture_order: Optional[Sequence[Tuple[str, str]]] = None,
    resolved_fixture_results: Optional[Mapping[str, FixtureMetricResult]] = None,
) -> CohortMetricResult:
    result = _revalidate_cohort_metric_result(result)
    metric_contract = _coerce_q14_type(metric_contract, MetricContract)
    metric_registry = _coerce_q14_type(metric_registry, MetricRegistry)
    aggregation_contract = _coerce_q14_type(aggregation_contract, AggregationContract)
    if result.benchmark_revision != metric_registry.benchmark_revision:
        raise Q14ContractError("cohort benchmark revision differs from metric registry")
    if result.lane != metric_contract.lane:
        raise Q14ContractError("cohort lane does not match metric contract")
    if result.metric_contract_ref.metric_contract_id != metric_contract.metric_contract_id or result.metric_contract_ref.metric_contract_version != metric_contract.metric_contract_version or result.metric_contract_ref.sha256 != metric_contract_sha256(metric_contract):
        raise Q14ContractError("cohort metric contract reference mismatch")
    if result.metric_registry_ref.registry_id != metric_registry.registry_id or result.metric_registry_ref.registry_revision != metric_registry.registry_revision or result.metric_registry_ref.sha256 != metric_registry_sha256(metric_registry):
        raise Q14ContractError("cohort metric registry reference mismatch")
    if result.aggregation_contract_ref.aggregation_contract_id != aggregation_contract.aggregation_contract_id or result.aggregation_contract_ref.aggregation_contract_version != aggregation_contract.aggregation_contract_version or result.aggregation_contract_ref.sha256 != aggregation_contract_sha256(aggregation_contract):
        raise Q14ContractError("cohort aggregation reference mismatch")
    registry_ref = next(
        (
            ref
            for ref in metric_registry.metric_contracts
            if ref.metric_contract_id == metric_contract.metric_contract_id
            and ref.metric_contract_version == metric_contract.metric_contract_version
        ),
        None,
    )
    if registry_ref is None or registry_ref.sha256 != result.metric_contract_ref.sha256:
        raise Q14ContractError("cohort registry does not select the exact metric digest")
    if metric_contract.aggregation_contract_ref != result.aggregation_contract_ref:
        raise Q14ContractError("cohort aggregation reference differs from metric contract")
    if result.result_kind != AggregationKind.FIXTURE_VECTOR_ONLY.value or result.aggregate is not None:
        raise Q14ContractError("cohort must remain fixture_vector_only with null aggregate")
    actual_order = tuple((item.fixture_id, item.fixture_revision) for item in result.fixture_results)
    if required_fixture_order is not None and actual_order != tuple(required_fixture_order):
        raise Q14ContractError("cohort fixture vector does not match preregistered order")
    if resolved_fixture_results is None:
        raise Q14ContractError("cohort fixture results must resolve before validation")
    for item in result.fixture_results:
        fixture = resolved_fixture_results.get(item.fixture_id)
        if fixture is None:
            raise Q14ContractError(f"unresolved fixture result: {item.fixture_id}")
        fixture = _revalidate_fixture_metric_result(fixture)
        if fixture.fixture_id != item.fixture_id:
            raise Q14ContractError("resolved fixture identity mismatch")
        if fixture.fixture_revision != item.fixture_revision:
            raise Q14ContractError("fixture revision mismatch")
        if fixture.lane != result.lane or fixture.benchmark_revision != result.benchmark_revision:
            raise Q14ContractError("fixture lane or benchmark revision mismatch")
        if fixture.benchmark_revision != metric_registry.benchmark_revision:
            raise Q14ContractError("resolved fixture benchmark revision differs from metric registry")
        if fixture.metric_contract_ref != result.metric_contract_ref or fixture.metric_registry_ref != result.metric_registry_ref:
            raise Q14ContractError("fixture contract reference mismatch")
        if fixture_metric_result_sha256(fixture) != item.result_sha256:
            raise Q14ContractError("fixture result digest mismatch")
    return result


def score_coverage_fixture(
    *,
    authoritative_expected_claim_ids: Sequence[str],
    importance_by_expected_claim_id: Mapping[str, str],
    coverage_state_by_expected_claim_id: Mapping[str, str],
    applicable_expected_claim_ids: Sequence[str],
    excluded_expected_claim_ids: Sequence[str],
) -> CoverageMetricValue:
    """Build the exact Q14 coverage vector from owner-decided inputs."""

    authoritative = tuple(authoritative_expected_claim_ids)
    applicable = tuple(applicable_expected_claim_ids)
    excluded = tuple(excluded_expected_claim_ids)
    _require_unique(authoritative, "authoritative expected IDs")
    _require_unique(applicable, "applicable expected IDs")
    _require_unique(excluded, "excluded expected IDs")
    if set(authoritative) != set(applicable) | set(excluded) or set(applicable) & set(excluded):
        raise Q14ContractError("coverage authority is not applicable plus excluded")
    _require_subsequence(authoritative, applicable, "applicable expected IDs")
    _require_subsequence(authoritative, excluded, "excluded expected IDs")
    if set(importance_by_expected_claim_id) != set(authoritative):
        raise Q14ContractError("importance must be defined for every expected claim")
    if set(coverage_state_by_expected_claim_id) != set(applicable):
        raise Q14ContractError("coverage states must cover exactly applicable expected claims")
    strata: list[CoverageStratumVector] = []
    for stratum in ImportanceStratum:
        stratum_authoritative = tuple(
            claim_id
            for claim_id in authoritative
            if _parse_enum(ImportanceStratum, importance_by_expected_claim_id[claim_id]) == stratum
        )
        stratum_applicable = tuple(claim_id for claim_id in applicable if claim_id in stratum_authoritative)
        stratum_excluded = tuple(claim_id for claim_id in excluded if claim_id in stratum_authoritative)
        groups: dict[CoverageState, list[str]] = {
            state: [] for state in CoverageState
        }
        for claim_id in stratum_applicable:
            state = _parse_enum(CoverageState, coverage_state_by_expected_claim_id[claim_id])
            groups[state].append(claim_id)
        denominator = len(stratum_applicable)
        strata.append(
            CoverageStratumVector(
                stratum=stratum,
                authoritative_expected_claim_ids=stratum_authoritative,
                applicable_expected_claim_ids=stratum_applicable,
                excluded_expected_claim_ids=stratum_excluded,
                denominator_count=denominator,
                fully_covered=CountedExpectedClaims(count=len(groups[CoverageState.FULLY_COVERED]), expected_claim_ids=tuple(groups[CoverageState.FULLY_COVERED])),
                partially_covered=CountedExpectedClaims(count=len(groups[CoverageState.PARTIALLY_COVERED]), expected_claim_ids=tuple(groups[CoverageState.PARTIALLY_COVERED])),
                not_covered=CountedExpectedClaims(count=len(groups[CoverageState.NOT_COVERED]), expected_claim_ids=tuple(groups[CoverageState.NOT_COVERED])),
                fully_covered_rate=_rate_or_none(len(groups[CoverageState.FULLY_COVERED]), denominator),
                partially_covered_rate=_rate_or_none(len(groups[CoverageState.PARTIALLY_COVERED]), denominator),
                not_covered_rate=_rate_or_none(len(groups[CoverageState.NOT_COVERED]), denominator),
            )
        )
    return CoverageMetricValue(result_kind="coverage_state_vector", strata=tuple(strata))


def score_support_fixture(
    *,
    authoritative_generated_claim_ids: Sequence[str],
    support_state_by_generated_claim_id: Mapping[str, str],
    candidate_internal_contradiction_relation_ids: Sequence[str] = (),
    include_diagnostic_rates: bool = False,
) -> SupportMetricValue:
    """Build the exact Q14 generated-claim support vector from Q8 states."""

    authoritative = tuple(authoritative_generated_claim_ids)
    _require_unique(authoritative, "authoritative generated IDs")
    if set(support_state_by_generated_claim_id) != set(authoritative):
        raise Q14ContractError("support states must cover exactly authoritative generated claims")
    groups: dict[SupportState, list[str]] = {state: [] for state in SupportState}
    for claim_id in authoritative:
        state = _parse_enum(
            SupportState,
            support_state_by_generated_claim_id[claim_id],
        )
        groups[state].append(claim_id)
    decided_counts = tuple(len(groups[_parse_enum(SupportState, state)]) for state in _SUPPORT_DECIDED_STATE_ORDER)
    denominator = sum(decided_counts)
    state_counts = SupportDecidedStateCounts(
        supported=CountedGeneratedClaims(count=decided_counts[0], generated_claim_ids=tuple(groups[SupportState.SUPPORTED])),
        partially_supported=CountedGeneratedClaims(count=decided_counts[1], generated_claim_ids=tuple(groups[SupportState.PARTIALLY_SUPPORTED])),
        unsupported=CountedGeneratedClaims(count=decided_counts[2], generated_claim_ids=tuple(groups[SupportState.UNSUPPORTED])),
        contradicted_by_source=CountedGeneratedClaims(count=decided_counts[3], generated_claim_ids=tuple(groups[SupportState.CONTRADICTED_BY_SOURCE])),
        overstated=CountedGeneratedClaims(count=decided_counts[4], generated_claim_ids=tuple(groups[SupportState.OVERSTATED])),
    )
    rates: Tuple[DiagnosticRate, ...] = ()
    if include_diagnostic_rates and denominator:
        rates = tuple(
            DiagnosticRate(
                state=_parse_enum(SupportState, state),
                rate=_make_rational(count, denominator),
            )
            for state, count in zip(_SUPPORT_DECIDED_STATE_ORDER, decided_counts)
        )
    return SupportMetricValue(
        result_kind="support_state_counts",
        authoritative_generated_claim_ids=authoritative,
        applicable_generated_claim_ids=authoritative,
        decided_denominator_count=denominator,
        decided_state_counts=state_counts,
        unresolved_audit=CountedGeneratedClaims(
            count=len(groups[SupportState.UNRESOLVED]),
            generated_claim_ids=tuple(groups[SupportState.UNRESOLVED]),
        ),
        candidate_internal_contradiction=CandidateInternalContradiction(
            count=len(tuple(candidate_internal_contradiction_relation_ids)),
            relation_ids=tuple(candidate_internal_contradiction_relation_ids),
        ),
        diagnostic_rates=rates,
    )


def _rate_or_none(numerator: int, denominator: int) -> Optional[Rational]:
    if denominator == 0:
        return None
    return _make_rational(numerator, denominator)


def _make_rational(numerator: int, denominator: int) -> Rational:
    if denominator <= 0:
        raise Q14ContractError("rational denominator must be positive")
    if numerator == 0:
        return Rational(numerator=0, denominator=1)
    divisor = gcd(numerator, denominator)
    return Rational(numerator=numerator // divisor, denominator=denominator // divisor)


def validate_metric_contract(payload: Any) -> MetricContract:
    return payload if isinstance(payload, MetricContract) else MetricContract.model_validate(payload)


def validate_metric_registry(payload: Any) -> MetricRegistry:
    return payload if isinstance(payload, MetricRegistry) else MetricRegistry.model_validate(payload)


def validate_scorer_contract(payload: Any) -> ScorerContract:
    return payload if isinstance(payload, ScorerContract) else ScorerContract.model_validate(payload)


def validate_aggregation_contract(payload: Any) -> AggregationContract:
    return payload if isinstance(payload, AggregationContract) else AggregationContract.model_validate(payload)


# The shorter Ref names match the existing benchmark modules' public API.
MetricContractRef = MetricContractReference
MetricRegistryRef = MetricRegistryReference
ScorerContractRef = ScorerContractReference
AggregationContractRef = AggregationContractReference


__all__ = [
    "FIXTURE_RESULT_ID_SEED_FIELDS",
    "COHORT_RESULT_ID_SEED_FIELDS",
    "Q14_METRIC_CONTRACT_SCHEMA_VERSION",
    "Q14_METRIC_REGISTRY_SCHEMA_VERSION",
    "Q14_SCORER_CONTRACT_SCHEMA_VERSION",
    "Q14_AGGREGATION_CONTRACT_SCHEMA_VERSION",
    "Q14_FIXTURE_METRIC_RESULT_SCHEMA_VERSION",
    "Q14_COHORT_METRIC_RESULT_SCHEMA_VERSION",
    "Q14ContractError",
    "Q14Lane",
    "MetricKind",
    "ScoringUnit",
    "FormulaKind",
    "DenominatorSemantics",
    "ApplicabilityConsumption",
    "Direction",
    "CanonicalUnit",
    "NumericRepresentation",
    "InputArtifactRole",
    "ImportanceStratum",
    "CoverageState",
    "SupportState",
    "FormulaReference",
    "MetricContractRef",
    "MetricRegistryRef",
    "ScorerContractRef",
    "AggregationContractRef",
    "MetricContractReference",
    "MetricRegistryReference",
    "ScorerContractReference",
    "AggregationContractReference",
    "OwnerRecordReference",
    "InputArtifactReference",
    "Rational",
    "MetricComponent",
    "MetricFormula",
    "MetricContract",
    "MetricRegistry",
    "DeterministicRequirements",
    "ScorerContract",
    "AggregationContract",
    "CountedExpectedClaims",
    "CountedGeneratedClaims",
    "CoverageStratumVector",
    "CoverageMetricValue",
    "SupportDecidedStateCounts",
    "CandidateInternalContradiction",
    "DiagnosticRate",
    "SupportMetricValue",
    "FixtureMetricResult",
    "FixtureResultReference",
    "CohortMetricResult",
    "canonical_q14_bytes",
    "q14_artifact_sha256",
    "canonical_metric_contract_bytes",
    "canonical_metric_registry_bytes",
    "canonical_scorer_contract_bytes",
    "canonical_aggregation_contract_bytes",
    "canonical_fixture_metric_result_bytes",
    "canonical_cohort_metric_result_bytes",
    "metric_contract_sha256",
    "metric_registry_sha256",
    "scorer_contract_sha256",
    "aggregation_contract_sha256",
    "validate_metric_contract_bindings",
    "validate_metric_registry_bindings",
    "validate_scorer_contract_bindings",
    "fixture_metric_result_sha256",
    "cohort_metric_result_sha256",
    "derive_fixture_metric_result_id",
    "derive_cohort_metric_result_id",
    "build_fixture_metric_result",
    "build_cohort_metric_result",
    "validate_fixture_metric_result",
    "validate_metric_contract",
    "validate_metric_registry",
    "validate_scorer_contract",
    "validate_aggregation_contract",
    "validate_cohort_metric_result",
    "score_coverage_fixture",
    "score_support_fixture",
]
