"""Q28 exhaustive long-source coverage contracts.

This module owns only the frozen Q28 coverage-plan, work-unit-output, and
coverage-closure schema boundary.  It does not implement generation,
retrieval, merge algorithms, retry policy, scoring, or runner execution.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
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
    model_validator,
)

from .benchmark_note import (
    BenchmarkNoteArtifactInput,
    BenchmarkNoteDocument,
    benchmark_note_sha256,
    validate_benchmark_note_artifact,
)
from .normalized_document import (
    ArtifactRole,
    NormalizedDocument,
    NormalizedDocumentInput,
    normalized_document_sha256,
    validate_normalized_document,
)
from .routing import (
    ContractReference,
    RouteDecision,
    RoutingPolicy,
    route_decision_sha256,
    routing_policy_sha256,
)

COVERAGE_PLAN_SCHEMA_VERSION = "benchmark-generation-coverage-plan/1.0.0"
WORK_UNIT_OUTPUT_SCHEMA_VERSION = "benchmark-generation-work-unit-output/1.0.0"
COVERAGE_CLOSURE_SCHEMA_VERSION = "benchmark-generation-coverage-closure/1.0.0"
WORK_UNIT_IDENTITY_SCHEMA_VERSION = "benchmark-generation-work-unit/1.0.0"

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
_WORK_UNIT_ID_PATTERN = r"^work-unit-[0-9a-f]{64}$"


class CoverageContractError(ValueError):
    """Raised when a Q28 schema or cross-artifact binding is invalid."""


class CoverageCondition(str, Enum):
    COMPLETE = "complete"
    MISSING = "missing"
    FAILED = "failed"
    TRUNCATED = "truncated"
    INVALID = "invalid"


class OutputCondition(str, Enum):
    COMPLETE = "complete"
    MISSING = "missing"
    FAILED = "failed"
    TRUNCATED = "truncated"
    INVALID = "invalid"


class CoverageClosureState(str, Enum):
    CLOSED = "closed"
    NOT_CLOSED = "not_closed"


class EdgeKind(str, Enum):
    HIERARCHY = "hierarchy"
    EXECUTION_DEPENDENCY = "execution_dependency"
    MERGE_DEPENDENCY = "merge_dependency"


class ObservationKind(str, Enum):
    OMISSION = "omission"
    DUPLICATION = "duplication"
    TRUNCATION = "truncation"
    ORDERING_LOSS = "ordering_loss"
    INTERNAL_CONTRADICTION = "internal_contradiction"


EnumT = TypeVar("EnumT", bound=Enum)


def _enum_parser(enum_type: type[EnumT]) -> Callable[[object], EnumT]:
    def parse(value: object) -> EnumT:
        if isinstance(value, enum_type):
            return value
        if isinstance(value, str):
            try:
                return enum_type(value)
            except ValueError as exc:
                raise ValueError(f"unknown {enum_type.__name__} value") from exc
        raise TypeError(f"{enum_type.__name__} requires its exact string value")

    return parse


def _tuple_from_json(value: object) -> object:
    if isinstance(value, list):
        return tuple(value)
    return value


Sha256 = Annotated[StrictStr, Field(pattern=_SHA256_PATTERN)]
Identifier = Annotated[StrictStr, Field(pattern=_IDENTIFIER_PATTERN)]
Identity = Annotated[StrictStr, Field(min_length=1)]
WorkUnitId = Annotated[StrictStr, Field(pattern=_WORK_UNIT_ID_PATTERN)]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]
PositiveInt = Annotated[StrictInt, Field(ge=1)]
CoverageConditionValue = Annotated[
    CoverageCondition, BeforeValidator(_enum_parser(CoverageCondition))
]
OutputConditionValue = Annotated[
    OutputCondition, BeforeValidator(_enum_parser(OutputCondition))
]
CoverageClosureStateValue = Annotated[
    CoverageClosureState, BeforeValidator(_enum_parser(CoverageClosureState))
]
EdgeKindValue = Annotated[EdgeKind, BeforeValidator(_enum_parser(EdgeKind))]
ObservationKindValue = Annotated[
    ObservationKind, BeforeValidator(_enum_parser(ObservationKind))
]


class _StrictFrozenCoverageModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class ReferenceDocumentRef(_StrictFrozenCoverageModel):
    schema_version: Literal["normalized-document/1.0.0"]
    artifact_role: Literal["reference_document"]
    document_id: Identity
    sha256: Sha256


class RoutingPolicyRef(_StrictFrozenCoverageModel):
    schema_version: Literal["benchmark-generation-routing-policy/1.0.0"]
    policy_id: Identity
    policy_revision: Identifier
    sha256: Sha256
    configuration_sha256: Sha256


class RouteDecisionRef(_StrictFrozenCoverageModel):
    schema_version: Literal["benchmark-generation-route-decision/1.0.0"]
    artifact_role: Literal["route_decision"]
    sha256: Sha256


class ExecutionContractRef(_StrictFrozenCoverageModel):
    contract_id: Identity
    sha256: Sha256


class ExternalOwnerRecordRef(_StrictFrozenCoverageModel):
    schema_version: Identity
    sha256: Sha256
    record_type: Identity
    record_id: Identity


class Q26PreRenderNoteRef(_StrictFrozenCoverageModel):
    schema_version: Literal["benchmark-note-document/1.0.0"]
    artifact_role: Literal["pre_render_note"]
    document_id: Identity
    reference_document_sha256: Sha256
    sha256: Sha256


class Q26NodeRef(_StrictFrozenCoverageModel):
    artifact_sha256: Sha256
    node_id: Identity


class Q26CitationRef(_StrictFrozenCoverageModel):
    artifact_sha256: Sha256
    node_id: Identity
    citation_id: Identity


class SourceSectionRef(_StrictFrozenCoverageModel):
    section_id: Identity
    parent_section_id: Optional[Identity] = None
    heading_element_id: Optional[Identity] = None
    start_order: NonNegativeInt
    end_order: NonNegativeInt

    @model_validator(mode="after")
    def _validate_range(self) -> "SourceSectionRef":
        if self.end_order < self.start_order:
            raise ValueError("section end_order must be at least start_order")
        return self


class SourceUnitRef(_StrictFrozenCoverageModel):
    reference_document_id: Identity
    section_id: Identity
    element_id: Identity
    order: NonNegativeInt


class WorkUnitIdentitySeed(_StrictFrozenCoverageModel):
    identity_schema_version: str = WORK_UNIT_IDENTITY_SCHEMA_VERSION
    reference_document_sha256: Sha256
    primary_source_unit_ids: Annotated[
        Tuple[Identity, ...], BeforeValidator(_tuple_from_json)
    ]
    context_only_source_unit_ids: Annotated[
        Tuple[Identity, ...], BeforeValidator(_tuple_from_json)
    ]
    route_decision_sha256: Sha256
    execution_contract_sha256: Sha256

    @model_validator(mode="after")
    def _validate_seed(self) -> "WorkUnitIdentitySeed":
        if self.identity_schema_version != WORK_UNIT_IDENTITY_SCHEMA_VERSION:
            raise ValueError("identity_schema_version is invalid")
        if len(self.primary_source_unit_ids) != len(
            set(self.primary_source_unit_ids)
        ):
            raise ValueError("primary source unit IDs must be unique")
        if len(self.context_only_source_unit_ids) != len(
            set(self.context_only_source_unit_ids)
        ):
            raise ValueError("context-only source unit IDs must be unique")
        if set(self.primary_source_unit_ids).intersection(
            self.context_only_source_unit_ids
        ):
            raise ValueError("primary and context-only source IDs must be disjoint")
        return self


class WorkUnitSpec(_StrictFrozenCoverageModel):
    work_unit_id: WorkUnitId
    primary_source_unit_ids: Annotated[
        Tuple[Identity, ...], BeforeValidator(_tuple_from_json)
    ] = Field(min_length=1)
    context_only_source_unit_ids: Annotated[
        Tuple[Identity, ...], BeforeValidator(_tuple_from_json)
    ]

    @model_validator(mode="after")
    def _validate_assignments(self) -> "WorkUnitSpec":
        if len(self.primary_source_unit_ids) != len(
            set(self.primary_source_unit_ids)
        ):
            raise ValueError("primary source unit IDs must be unique")
        if len(self.context_only_source_unit_ids) != len(
            set(self.context_only_source_unit_ids)
        ):
            raise ValueError("context-only source unit IDs must be unique")
        if set(self.primary_source_unit_ids).intersection(
            self.context_only_source_unit_ids
        ):
            raise ValueError("primary and context-only source IDs must be disjoint")
        return self


class DependencyEdge(_StrictFrozenCoverageModel):
    predecessor_work_unit_id: WorkUnitId
    successor_work_unit_id: WorkUnitId
    edge_kind: EdgeKindValue

    @model_validator(mode="after")
    def _validate_direction(self) -> "DependencyEdge":
        if self.predecessor_work_unit_id == self.successor_work_unit_id:
            raise ValueError("dependency edge must not be self-referential")
        return self


class AttemptBinding(_StrictFrozenCoverageModel):
    attempt_ordinal: PositiveInt
    output_sha256: Sha256
    receipt_ref: ExternalOwnerRecordRef


class UnitOutcome(_StrictFrozenCoverageModel):
    work_unit_id: WorkUnitId
    attempts: Annotated[
        Tuple[AttemptBinding, ...], BeforeValidator(_tuple_from_json)
    ]
    terminal_attempt_ordinal: Optional[PositiveInt]
    coverage_condition: CoverageConditionValue

    @model_validator(mode="after")
    def _validate_attempt_order(self) -> "UnitOutcome":
        ordinals = tuple(attempt.attempt_ordinal for attempt in self.attempts)
        if len(ordinals) != len(set(ordinals)):
            raise ValueError("attempt ordinals must be unique")
        if ordinals != tuple(sorted(ordinals)):
            raise ValueError("attempts must be ordered by ascending ordinal")
        if self.terminal_attempt_ordinal is not None and (
            self.terminal_attempt_ordinal not in ordinals
        ):
            raise ValueError("terminal_attempt_ordinal must reference an attempt")
        return self


class WorkUnitOutput(_StrictFrozenCoverageModel):
    schema_version: Literal["benchmark-generation-work-unit-output/1.0.0"]
    artifact_role: Literal["work_unit_output"]
    coverage_plan_sha256: Sha256
    work_unit_id: WorkUnitId
    attempt_ordinal: PositiveInt
    output_condition: OutputConditionValue
    pre_render_note: Optional[Q26PreRenderNoteRef]



class SourceReferenceMapping(_StrictFrozenCoverageModel):
    source_unit_ref: SourceUnitRef
    work_unit_id: WorkUnitId
    output_node_ref: Optional[Q26NodeRef]
    citation_ref: Optional[Q26CitationRef]
    external_owner_record_refs: Optional[
        Annotated[Tuple[ExternalOwnerRecordRef, ...], BeforeValidator(_tuple_from_json)]
    ]

    @model_validator(mode="after")
    def _validate_citation_parent(self) -> "SourceReferenceMapping":
        if self.citation_ref is not None and self.output_node_ref is not None:
            if self.citation_ref.artifact_sha256 != self.output_node_ref.artifact_sha256:
                raise ValueError("citation artifact must match output node artifact")
            if self.citation_ref.node_id != self.output_node_ref.node_id:
                raise ValueError("citation node must match output node")
        return self


class Observation(_StrictFrozenCoverageModel):
    observation_id: Identifier
    observation_kind: ObservationKindValue
    source_unit_refs: Annotated[
        Tuple[SourceUnitRef, ...], BeforeValidator(_tuple_from_json)
    ]
    work_unit_ids: Annotated[
        Tuple[WorkUnitId, ...], BeforeValidator(_tuple_from_json)
    ]
    output_node_refs: Annotated[
        Tuple[Q26NodeRef, ...], BeforeValidator(_tuple_from_json)
    ]
    basis_refs: Annotated[
        Tuple[ExternalOwnerRecordRef, ...], BeforeValidator(_tuple_from_json)
    ]


class CoveragePlan(_StrictFrozenCoverageModel):
    schema_version: Literal["benchmark-generation-coverage-plan/1.0.0"]
    artifact_role: Literal["coverage_plan"]
    plan_id: Identifier
    plan_revision: Identifier
    reference_document: ReferenceDocumentRef
    routing_policy: RoutingPolicyRef
    route_decision: RouteDecisionRef
    execution_contract: ExecutionContractRef
    source_sections: Annotated[
        Tuple[SourceSectionRef, ...], BeforeValidator(_tuple_from_json)
    ] = Field(min_length=1)
    source_units: Annotated[
        Tuple[SourceUnitRef, ...], BeforeValidator(_tuple_from_json)
    ] = Field(min_length=1)
    work_units: Annotated[
        Tuple[WorkUnitSpec, ...], BeforeValidator(_tuple_from_json)
    ] = Field(min_length=1)
    dependency_edges: Annotated[
        Tuple[DependencyEdge, ...], BeforeValidator(_tuple_from_json)
    ]
    planned_execution_order: Annotated[
        Tuple[WorkUnitId, ...], BeforeValidator(_tuple_from_json)
    ] = Field(min_length=1)
    planned_merge_order: Annotated[
        Tuple[WorkUnitId, ...], BeforeValidator(_tuple_from_json)
    ] = Field(min_length=1)



class CoverageClosure(_StrictFrozenCoverageModel):
    schema_version: Literal["benchmark-generation-coverage-closure/1.0.0"]
    artifact_role: Literal["coverage_closure"]
    coverage_closure_state: CoverageClosureStateValue
    coverage_plan_sha256: Sha256
    unit_outcomes: Annotated[
        Tuple[UnitOutcome, ...], BeforeValidator(_tuple_from_json)
    ]
    observed_merge_order: Annotated[
        Tuple[WorkUnitId, ...], BeforeValidator(_tuple_from_json)
    ]
    final_pre_render_note: Q26PreRenderNoteRef
    source_reference_mappings: Annotated[
        Tuple[SourceReferenceMapping, ...], BeforeValidator(_tuple_from_json)
    ]
    observations: Annotated[
        Tuple[Observation, ...], BeforeValidator(_tuple_from_json)
    ]

    @model_validator(mode="after")
    def _validate_order(self) -> "CoverageClosure":
        if len(self.observed_merge_order) != len(set(self.observed_merge_order)):
            raise ValueError("observed_merge_order must not contain duplicates")
        observation_ids = tuple(observation.observation_id for observation in self.observations)
        if observation_ids != tuple(sorted(observation_ids)):
            raise ValueError("observations must be ordered by observation_id")
        return self


CoverageArtifact = Union[CoveragePlan, WorkUnitOutput, CoverageClosure]
CoveragePlanArtifact = CoveragePlan
WorkUnitOutputArtifact = WorkUnitOutput
CoverageClosureArtifact = CoverageClosure
CoverageArtifactInput = Union[CoverageArtifact, Mapping[str, Any]]
WorkUnitOutputInput = Union[WorkUnitOutput, Mapping[str, Any]]
CoveragePlanInput = Union[CoveragePlan, Mapping[str, Any]]
CoverageClosureInput = Union[CoverageClosure, Mapping[str, Any]]


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _canonical_model_bytes(model: BaseModel) -> bytes:
    return _canonical_json_bytes(model.model_dump(mode="json"))


def _model_payload(artifact: Union[BaseModel, Mapping[str, Any]]) -> Mapping[str, Any]:
    if isinstance(artifact, BaseModel):
        return artifact.model_dump(mode="json")
    if isinstance(artifact, Mapping):
        return artifact
    raise TypeError("artifact must be a Pydantic model or mapping")


def canonical_identity_seed_bytes(
    seed: Union[WorkUnitIdentitySeed, Mapping[str, Any]],
) -> bytes:
    model = seed if isinstance(seed, WorkUnitIdentitySeed) else WorkUnitIdentitySeed.model_validate(seed)
    return _canonical_model_bytes(model)


def work_unit_id_from_seed(
    seed: Union[WorkUnitIdentitySeed, Mapping[str, Any]],
) -> str:
    return "work-unit-" + hashlib.sha256(canonical_identity_seed_bytes(seed)).hexdigest()


def derive_work_unit_id(
    *,
    reference_document_sha256: str,
    primary_source_unit_ids: Sequence[str],
    context_only_source_unit_ids: Sequence[str],
    route_decision_sha256: str,
    execution_contract_sha256: str,
) -> str:
    return work_unit_id_from_seed(
        WorkUnitIdentitySeed(
            identity_schema_version=WORK_UNIT_IDENTITY_SCHEMA_VERSION,
            reference_document_sha256=reference_document_sha256,
            primary_source_unit_ids=tuple(primary_source_unit_ids),
            context_only_source_unit_ids=tuple(context_only_source_unit_ids),
            route_decision_sha256=route_decision_sha256,
            execution_contract_sha256=execution_contract_sha256,
        )
    )


def validate_coverage_artifact(payload: CoverageArtifactInput) -> CoverageArtifact:
    data = _model_payload(payload)
    schema_version = data.get("schema_version")
    if schema_version == COVERAGE_PLAN_SCHEMA_VERSION:
        return CoveragePlan.model_validate(data)
    if schema_version == WORK_UNIT_OUTPUT_SCHEMA_VERSION:
        return WorkUnitOutput.model_validate(data)
    if schema_version == COVERAGE_CLOSURE_SCHEMA_VERSION:
        return CoverageClosure.model_validate(data)
    raise CoverageContractError("unknown Q28 coverage schema_version")


def canonical_coverage_bytes(payload: CoverageArtifactInput) -> bytes:
    return _canonical_model_bytes(validate_coverage_artifact(payload))


def coverage_artifact_sha256(payload: CoverageArtifactInput) -> str:
    return hashlib.sha256(canonical_coverage_bytes(payload)).hexdigest()


def canonical_coverage_plan_bytes(payload: CoveragePlanInput) -> bytes:
    model = payload if isinstance(payload, CoveragePlan) else CoveragePlan.model_validate(payload)
    return _canonical_model_bytes(model)


def coverage_plan_sha256(payload: CoveragePlanInput) -> str:
    return hashlib.sha256(canonical_coverage_plan_bytes(payload)).hexdigest()


def canonical_work_unit_output_bytes(payload: WorkUnitOutputInput) -> bytes:
    model = payload if isinstance(payload, WorkUnitOutput) else WorkUnitOutput.model_validate(payload)
    return _canonical_model_bytes(model)


def work_unit_output_sha256(payload: WorkUnitOutputInput) -> str:
    return hashlib.sha256(canonical_work_unit_output_bytes(payload)).hexdigest()


def canonical_coverage_closure_bytes(payload: CoverageClosureInput) -> bytes:
    model = payload if isinstance(payload, CoverageClosure) else CoverageClosure.model_validate(payload)
    return _canonical_model_bytes(model)


def coverage_closure_sha256(payload: CoverageClosureInput) -> str:
    return hashlib.sha256(canonical_coverage_closure_bytes(payload)).hexdigest()


def _validate_permutation(
    order: Sequence[str], work_unit_ids: Sequence[str], field_name: str
) -> None:
    expected = tuple(work_unit_ids)
    actual = tuple(order)
    if len(actual) != len(expected) or set(actual) != set(expected):
        raise CoverageContractError(
            f"{field_name} must contain every work unit ID exactly once"
        )


def _validate_topological_order(
    order: Sequence[str], edges: Iterable[DependencyEdge], field_name: str
) -> None:
    positions = {work_unit_id: index for index, work_unit_id in enumerate(order)}
    for edge in edges:
        if positions[edge.predecessor_work_unit_id] >= positions[edge.successor_work_unit_id]:
            raise CoverageContractError(
                f"{field_name} violates dependency edge order"
            )


def _validate_acyclic(
    work_unit_ids: Sequence[str], edges: Iterable[DependencyEdge]
) -> None:
    successors: dict[str, set[str]] = {
        work_unit_id: set() for work_unit_id in work_unit_ids
    }
    indegree = {work_unit_id: 0 for work_unit_id in work_unit_ids}
    for edge in edges:
        if edge.successor_work_unit_id not in successors[edge.predecessor_work_unit_id]:
            successors[edge.predecessor_work_unit_id].add(edge.successor_work_unit_id)
            indegree[edge.successor_work_unit_id] += 1
    ready = [work_unit_id for work_unit_id in work_unit_ids if indegree[work_unit_id] == 0]
    visited = 0
    while ready:
        current = ready.pop()
        visited += 1
        for successor in successors[current]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
    if visited != len(work_unit_ids):
        raise CoverageContractError("dependency graph must be acyclic")


def _validate_routing_bindings(
    plan: CoveragePlan,
    *,
    routing_policy: Optional[Union[RoutingPolicy, Mapping[str, Any]]],
    route_decision: Optional[Union[RouteDecision, Mapping[str, Any]]],
    execution_contract: Optional[Union[ContractReference, Mapping[str, Any]]],
) -> None:
    policy_model: Optional[RoutingPolicy] = None
    if routing_policy is not None:
        policy_model = (
            routing_policy
            if isinstance(routing_policy, RoutingPolicy)
            else RoutingPolicy.model_validate(routing_policy)
        )
        if routing_policy_sha256(policy_model) != plan.routing_policy.sha256:
            raise CoverageContractError("routing policy digest binding mismatch")
        if policy_model.policy_id != plan.routing_policy.policy_id:
            raise CoverageContractError("routing policy ID binding mismatch")
        if policy_model.policy_revision != plan.routing_policy.policy_revision:
            raise CoverageContractError("routing policy revision binding mismatch")
        if policy_model.configuration_sha256 != plan.routing_policy.configuration_sha256:
            raise CoverageContractError("routing policy configuration binding mismatch")

    decision_model: Optional[RouteDecision] = None
    if route_decision is not None:
        decision_model = (
            route_decision
            if isinstance(route_decision, RouteDecision)
            else RouteDecision.model_validate(route_decision)
        )
        if route_decision_sha256(decision_model) != plan.route_decision.sha256:
            raise CoverageContractError("route decision digest binding mismatch")
        if decision_model.policy.policy_id != plan.routing_policy.policy_id:
            raise CoverageContractError("route decision policy ID mismatch")
        if decision_model.policy.policy_revision != plan.routing_policy.policy_revision:
            raise CoverageContractError("route decision policy revision mismatch")
        if decision_model.policy.configuration_sha256 != plan.routing_policy.configuration_sha256:
            raise CoverageContractError("route decision configuration binding mismatch")
        if decision_model.reference_document.document_id != plan.reference_document.document_id:
            raise CoverageContractError("route decision document ID mismatch")
        if decision_model.reference_document.sha256 != plan.reference_document.sha256:
            raise CoverageContractError("route decision document digest mismatch")
        if decision_model.execution_contract.contract_id != plan.execution_contract.contract_id:
            raise CoverageContractError("route decision execution contract ID mismatch")
        if decision_model.execution_contract.sha256 != plan.execution_contract.sha256:
            raise CoverageContractError("route decision execution contract digest mismatch")
        if decision_model.policy.sha256 != plan.routing_policy.sha256:
            raise CoverageContractError("route decision policy digest mismatch")

    if execution_contract is not None:
        contract = (
            execution_contract
            if isinstance(execution_contract, ContractReference)
            else ContractReference.model_validate(execution_contract)
        )
        if contract.contract_id != plan.execution_contract.contract_id:
            raise CoverageContractError("execution contract ID binding mismatch")
        if contract.sha256 != plan.execution_contract.sha256:
            raise CoverageContractError("execution contract digest mismatch")

    if policy_model is not None and decision_model is not None:
        if decision_model.policy.sha256 != routing_policy_sha256(policy_model):
            raise CoverageContractError("route decision does not bind supplied policy")


def validate_coverage_plan(
    payload: CoveragePlanInput,
    reference_document: NormalizedDocumentInput,
    *,
    routing_policy: Optional[Union[RoutingPolicy, Mapping[str, Any]]] = None,
    route_decision: Optional[Union[RouteDecision, Mapping[str, Any]]] = None,
    execution_contract: Optional[Union[ContractReference, Mapping[str, Any]]] = None,
) -> CoveragePlan:
    """Validate a plan against the exact reference-document source universe."""

    plan = payload if isinstance(payload, CoveragePlan) else CoveragePlan.model_validate(payload)
    document = validate_normalized_document(reference_document)
    if document.artifact_role != ArtifactRole.REFERENCE_DOCUMENT:
        raise CoverageContractError("coverage plan must bind a reference_document")
    if plan.reference_document.document_id != document.document_id:
        raise CoverageContractError("reference document ID binding mismatch")
    if plan.reference_document.sha256 != normalized_document_sha256(document):
        raise CoverageContractError("reference document digest binding mismatch")

    expected_sections = tuple(
        SourceSectionRef(
            section_id=section.section_id,
            parent_section_id=section.parent_section_id,
            heading_element_id=section.heading_element_id,
            start_order=section.start_order,
            end_order=section.end_order,
        )
        for section in document.sections
    )
    if plan.source_sections != expected_sections:
        raise CoverageContractError("source_sections do not match reference order")

    expected_units = tuple(
        SourceUnitRef(
            reference_document_id=document.document_id,
            section_id=element.section_id,
            element_id=element.element_id,
            order=element.order,
        )
        for element in document.elements
    )
    if plan.source_units != expected_units:
        raise CoverageContractError("source_units do not match reference universe/order")

    source_ids = tuple(unit.element_id for unit in plan.source_units)
    source_id_set = set(source_ids)
    source_order = {unit.element_id: unit.order for unit in plan.source_units}
    work_unit_ids = tuple(work_unit.work_unit_id for work_unit in plan.work_units)
    if len(work_unit_ids) != len(set(work_unit_ids)):
        raise CoverageContractError("work_unit IDs must be unique")

    primary_occurrences: list[str] = []
    for work_unit in plan.work_units:
        primary = tuple(work_unit.primary_source_unit_ids)
        context = tuple(work_unit.context_only_source_unit_ids)
        missing = (set(primary) | set(context)) - source_id_set
        if missing:
            raise CoverageContractError("work unit references a foreign source unit")
        if primary != tuple(sorted(primary, key=source_order.__getitem__)):
            raise CoverageContractError("primary source IDs must use source order")
        if context != tuple(sorted(context, key=source_order.__getitem__)):
            raise CoverageContractError("context-only source IDs must use source order")
        primary_occurrences.extend(primary)
        expected_id = derive_work_unit_id(
            reference_document_sha256=plan.reference_document.sha256,
            primary_source_unit_ids=primary,
            context_only_source_unit_ids=context,
            route_decision_sha256=plan.route_decision.sha256,
            execution_contract_sha256=plan.execution_contract.sha256,
        )
        if work_unit.work_unit_id != expected_id:
            raise CoverageContractError("work_unit_id does not match frozen identity seed")

    if tuple(sorted(primary_occurrences, key=source_order.__getitem__)) != source_ids:
        raise CoverageContractError("primary assignments must cover source units exactly once")
    if len(primary_occurrences) != len(set(primary_occurrences)):
        raise CoverageContractError("each source unit must have exactly one primary assignment")

    expected_work_order = tuple(
        sorted(
            plan.work_units,
            key=lambda work_unit: (
                source_order[work_unit.primary_source_unit_ids[0]],
                work_unit.work_unit_id,
            ),
        )
    )
    if plan.work_units != expected_work_order:
        raise CoverageContractError("work_units must use canonical source order")

    edge_keys = tuple(
        (
            edge.predecessor_work_unit_id,
            edge.successor_work_unit_id,
            edge.edge_kind.value,
        )
        for edge in plan.dependency_edges
    )
    if len(edge_keys) != len(set(edge_keys)):
        raise CoverageContractError("dependency edges must be unique by typed edge")
    for edge in plan.dependency_edges:
        if edge.predecessor_work_unit_id not in work_unit_ids or edge.successor_work_unit_id not in work_unit_ids:
            raise CoverageContractError("dependency edge references a foreign work unit")
    edge_kind_order = {
        EdgeKind.HIERARCHY: 0,
        EdgeKind.EXECUTION_DEPENDENCY: 1,
        EdgeKind.MERGE_DEPENDENCY: 2,
    }
    expected_edges = tuple(
        sorted(
            plan.dependency_edges,
            key=lambda edge: (
                edge_kind_order[edge.edge_kind],
                edge.predecessor_work_unit_id,
                edge.successor_work_unit_id,
            ),
        )
    )
    if plan.dependency_edges != expected_edges:
        raise CoverageContractError("dependency_edges must use canonical typed order")
    _validate_acyclic(work_unit_ids, plan.dependency_edges)

    _validate_permutation(
        plan.planned_execution_order, work_unit_ids, "planned_execution_order"
    )
    _validate_topological_order(
        plan.planned_execution_order,
        plan.dependency_edges,
        "planned_execution_order",
    )
    _validate_permutation(plan.planned_merge_order, work_unit_ids, "planned_merge_order")
    _validate_topological_order(
        plan.planned_merge_order,
        tuple(edge for edge in plan.dependency_edges if edge.edge_kind == EdgeKind.MERGE_DEPENDENCY),
        "planned_merge_order",
    )
    _validate_routing_bindings(
        plan,
        routing_policy=routing_policy,
        route_decision=route_decision,
        execution_contract=execution_contract,
    )
    return plan


def _validate_q26_note_binding(
    reference: Q26PreRenderNoteRef,
    artifact: Optional[BenchmarkNoteArtifactInput],
    reference_document: Optional[NormalizedDocumentInput],
) -> Optional[BenchmarkNoteDocument]:
    if artifact is None:
        return None
    if reference_document is None:
        note = BenchmarkNoteDocument.model_validate(_model_payload(artifact))
    else:
        validated = validate_benchmark_note_artifact(artifact, reference_document)
        if not isinstance(validated, BenchmarkNoteDocument):
            raise CoverageContractError("Q28 requires a Q26 pre_render_note artifact")
        note = validated
    if benchmark_note_sha256(note) != reference.sha256:
        raise CoverageContractError("Q26 pre_render_note digest binding mismatch")
    if note.document_id != reference.document_id:
        raise CoverageContractError("Q26 pre_render_note document ID mismatch")
    if note.reference_document_sha256 != reference.reference_document_sha256:
        raise CoverageContractError("Q26 pre_render_note reference digest mismatch")
    return note


def validate_work_unit_output(
    payload: WorkUnitOutputInput,
    coverage_plan: Optional[CoveragePlanInput] = None,
    *,
    reference_document: Optional[NormalizedDocumentInput] = None,
    pre_render_note_artifact: Optional[BenchmarkNoteArtifactInput] = None,
) -> WorkUnitOutput:
    """Validate one immutable output envelope and optional Q26 binding."""

    output = payload if isinstance(payload, WorkUnitOutput) else WorkUnitOutput.model_validate(payload)
    plan: Optional[CoveragePlan] = None
    if coverage_plan is not None:
        plan = coverage_plan if isinstance(coverage_plan, CoveragePlan) else CoveragePlan.model_validate(coverage_plan)
        if output.coverage_plan_sha256 != coverage_plan_sha256(plan):
            raise CoverageContractError("work-unit output plan digest mismatch")
        if output.work_unit_id not in {unit.work_unit_id for unit in plan.work_units}:
            raise CoverageContractError("work-unit output references a foreign work unit")
    if output.pre_render_note is None:
        if pre_render_note_artifact is not None:
            raise CoverageContractError("pre_render_note artifact supplied for null binding")
    else:
        if plan is not None:
            if output.pre_render_note.document_id != plan.reference_document.document_id:
                raise CoverageContractError("output note document ID mismatch")
            if output.pre_render_note.reference_document_sha256 != plan.reference_document.sha256:
                raise CoverageContractError("output note reference digest mismatch")
        _validate_q26_note_binding(
            output.pre_render_note,
            pre_render_note_artifact,
            reference_document,
        )
    return output


def _lookup_digest_record(
    records: Optional[Union[Mapping[str, Any], Sequence[Any]]],
    digest: str,
) -> Any:
    if records is None:
        return None
    if isinstance(records, Mapping):
        return records.get(digest)
    for record in records:
        data: Mapping[str, Any]
        if isinstance(record, BaseModel):
            data = record.model_dump(mode="json")
        elif isinstance(record, Mapping):
            data = record
        else:
            continue
        if data.get("sha256") == digest or data.get("artifact_sha256") == digest:
            return record
    return None


def _validate_owner_record(
    reference: ExternalOwnerRecordRef,
    record: Any,
    *,
    plan_sha256: Optional[str] = None,
    work_unit_id: Optional[str] = None,
    attempt_ordinal: Optional[int] = None,
) -> None:
    if record is None:
        raise CoverageContractError("owner receipt reference cannot be resolved")
    data = record.model_dump(mode="json") if isinstance(record, BaseModel) else record
    if not isinstance(data, Mapping):
        raise CoverageContractError("owner receipt record must be a mapping/model")
    if data.get("schema_version") is not None and data["schema_version"] != reference.schema_version:
        raise CoverageContractError("owner receipt schema_version mismatch")
    if data.get("record_type") is not None and data["record_type"] != reference.record_type:
        raise CoverageContractError("owner receipt record_type mismatch")
    if data.get("record_id") is not None and data["record_id"] != reference.record_id:
        raise CoverageContractError("owner receipt record_id mismatch")
    if data.get("sha256") is not None and data["sha256"] != reference.sha256:
        raise CoverageContractError("owner receipt digest mismatch")
    for field_name in ("coverage_plan_sha256", "plan_sha256"):
        if (
            plan_sha256 is not None
            and data.get(field_name) is not None
            and data[field_name] != plan_sha256
        ):
            raise CoverageContractError("owner receipt plan binding mismatch")
    if (
        work_unit_id is not None
        and data.get("work_unit_id") is not None
        and data["work_unit_id"] != work_unit_id
    ):
        raise CoverageContractError("owner receipt work-unit binding mismatch")
    if (
        attempt_ordinal is not None
        and data.get("attempt_ordinal") is not None
        and data["attempt_ordinal"] != attempt_ordinal
    ):
        raise CoverageContractError("owner receipt attempt binding mismatch")


def _validate_source_ref(
    source_ref: SourceUnitRef,
    source_units: Mapping[str, SourceUnitRef],
) -> None:
    expected = source_units.get(source_ref.element_id)
    if expected is None or source_ref != expected:
        raise CoverageContractError("source reference does not resolve to the plan")


def _validate_q26_node_ref(
    reference: Q26NodeRef,
    artifacts: Optional[Union[Mapping[str, Any], Sequence[Any]]],
) -> None:
    if artifacts is None:
        return
    artifact = _lookup_digest_record(artifacts, reference.artifact_sha256)
    if artifact is None:
        raise CoverageContractError("Q26 node artifact reference cannot be resolved")
    note = BenchmarkNoteDocument.model_validate(_model_payload(artifact))
    if benchmark_note_sha256(note) != reference.artifact_sha256:
        raise CoverageContractError("Q26 node artifact digest mismatch")
    if reference.node_id not in {node.node_id for node in note.nodes}:
        raise CoverageContractError("Q26 node reference cannot be resolved")


def _validate_q26_citation_ref(
    reference: Q26CitationRef,
    artifacts: Optional[Union[Mapping[str, Any], Sequence[Any]]],
) -> None:
    if artifacts is None:
        return
    artifact = _lookup_digest_record(artifacts, reference.artifact_sha256)
    if artifact is None:
        raise CoverageContractError("Q26 citation artifact reference cannot be resolved")
    note = BenchmarkNoteDocument.model_validate(_model_payload(artifact))
    if benchmark_note_sha256(note) != reference.artifact_sha256:
        raise CoverageContractError("Q26 citation artifact digest mismatch")
    nodes = {node.node_id: node for node in note.nodes}
    node = nodes.get(reference.node_id)
    if node is None or reference.citation_id not in {citation.citation_id for citation in node.citations}:
        raise CoverageContractError("Q26 citation reference cannot be resolved")


def _validate_external_ref_order(refs: Optional[Sequence[ExternalOwnerRecordRef]]) -> None:
    if refs is None:
        return
    keys = tuple((ref.schema_version, ref.record_type, ref.record_id, ref.sha256) for ref in refs)
    if keys != tuple(sorted(keys)):
        raise CoverageContractError("external owner references must use canonical order")


def _validate_closure_order_and_refs(
    closure: CoverageClosure,
    plan: CoveragePlan,
    *,
    q26_artifacts: Optional[Union[Mapping[str, Any], Sequence[Any]]],
    owner_records: Optional[Union[Mapping[str, Any], Sequence[Any]]],
) -> None:
    work_unit_ids = tuple(unit.work_unit_id for unit in plan.work_units)
    outcome_ids = tuple(outcome.work_unit_id for outcome in closure.unit_outcomes)
    if len(outcome_ids) != len(set(outcome_ids)) or set(outcome_ids) != set(work_unit_ids):
        raise CoverageContractError("unit_outcomes must exactly match plan work-unit IDs")
    if outcome_ids != work_unit_ids:
        raise CoverageContractError("unit_outcomes must use plan work-unit order")
    source_units = {source.element_id: source for source in plan.source_units}
    work_unit_id_set = set(work_unit_ids)

    merge_edges = tuple(
        edge for edge in plan.dependency_edges if edge.edge_kind == EdgeKind.MERGE_DEPENDENCY
    )
    if any(
        work_unit_id not in work_unit_id_set
        for work_unit_id in closure.observed_merge_order
    ):
        raise CoverageContractError("observed_merge_order references a foreign work unit")
    positions = {work_unit_id: index for index, work_unit_id in enumerate(closure.observed_merge_order)}
    for edge in merge_edges:
        if edge.successor_work_unit_id in positions:
            if edge.predecessor_work_unit_id not in positions:
                raise CoverageContractError("observed merge order omits a merge predecessor")
            if positions[edge.predecessor_work_unit_id] >= positions[edge.successor_work_unit_id]:
                raise CoverageContractError("observed merge order violates merge dependency")

    mapping_keys = []
    for mapping in closure.source_reference_mappings:
        _validate_source_ref(mapping.source_unit_ref, source_units)
        if mapping.work_unit_id not in work_unit_id_set:
            raise CoverageContractError("mapping references a foreign work unit")
        if mapping.output_node_ref:
            _validate_q26_node_ref(mapping.output_node_ref, q26_artifacts)
        if mapping.citation_ref:
            _validate_q26_citation_ref(mapping.citation_ref, q26_artifacts)
        _validate_external_ref_order(mapping.external_owner_record_refs)
        if mapping.external_owner_record_refs:
            for reference in mapping.external_owner_record_refs:
                _validate_owner_record(
                    reference,
                    _lookup_digest_record(owner_records, reference.sha256),
                )
        mapping_keys.append(
            (
                mapping.source_unit_ref.order,
                mapping.work_unit_id,
                0 if mapping.output_node_ref is None else 1,
                "" if mapping.output_node_ref is None else mapping.output_node_ref.artifact_sha256,
                "" if mapping.output_node_ref is None else mapping.output_node_ref.node_id,
                0 if mapping.citation_ref is None else 1,
                "" if mapping.citation_ref is None else mapping.citation_ref.citation_id,
            )
        )
    if tuple(mapping_keys) != tuple(sorted(mapping_keys)):
        raise CoverageContractError(
            "source_reference_mappings must use canonical source/node order"
        )

    observation_ids = tuple(observation.observation_id for observation in closure.observations)
    if len(observation_ids) != len(set(observation_ids)):
        raise CoverageContractError("observation IDs must be unique")
    for observation in closure.observations:
        for source_ref in observation.source_unit_refs:
            _validate_source_ref(source_ref, source_units)
        if any(work_unit_id not in work_unit_id_set for work_unit_id in observation.work_unit_ids):
            raise CoverageContractError("observation references a foreign work unit")
        for node_ref in observation.output_node_refs:
            _validate_q26_node_ref(node_ref, q26_artifacts)
        _validate_external_ref_order(observation.basis_refs)
        for reference in observation.basis_refs:
            _validate_owner_record(
                reference,
                _lookup_digest_record(owner_records, reference.sha256),
            )


def validate_coverage_closure(
    payload: CoverageClosureInput,
    coverage_plan: Optional[CoveragePlanInput] = None,
    *,
    output_artifacts: Optional[Union[Mapping[str, Any], Sequence[Any]]] = None,
    owner_records: Optional[Union[Mapping[str, Any], Sequence[Any]]] = None,
    receipts: Optional[Union[Mapping[str, Any], Sequence[Any]]] = None,
    reference_document: Optional[NormalizedDocumentInput] = None,
    final_pre_render_note_artifact: Optional[BenchmarkNoteArtifactInput] = None,
    q26_artifacts: Optional[Union[Mapping[str, Any], Sequence[Any]]] = None,
) -> CoverageClosure:
    """Validate closure identity, history bindings, merge order, and refs."""

    closure = payload if isinstance(payload, CoverageClosure) else CoverageClosure.model_validate(payload)
    plan: Optional[CoveragePlan] = None
    if coverage_plan is not None:
        plan = coverage_plan if isinstance(coverage_plan, CoveragePlan) else CoveragePlan.model_validate(coverage_plan)
        if closure.coverage_plan_sha256 != coverage_plan_sha256(plan):
            raise CoverageContractError("coverage closure plan digest mismatch")
        if closure.final_pre_render_note.document_id != plan.reference_document.document_id:
            raise CoverageContractError("closure final note document ID mismatch")
        if closure.final_pre_render_note.reference_document_sha256 != plan.reference_document.sha256:
            raise CoverageContractError("closure final note reference digest mismatch")
        _validate_closure_order_and_refs(
            closure,
            plan,
            q26_artifacts=q26_artifacts,
            owner_records=owner_records or receipts,
        )

    if final_pre_render_note_artifact is not None:
        _validate_q26_note_binding(
            closure.final_pre_render_note,
            final_pre_render_note_artifact,
            reference_document,
        )

    outputs = output_artifacts
    if plan is not None:
        for outcome in closure.unit_outcomes:
            for attempt in outcome.attempts:
                record = _lookup_digest_record(outputs, attempt.output_sha256)
                if outputs is not None and record is None:
                    raise CoverageContractError("output binding cannot be resolved")
                if record is not None:
                    output = record if isinstance(record, WorkUnitOutput) else WorkUnitOutput.model_validate(_model_payload(record))
                    if work_unit_output_sha256(output) != attempt.output_sha256:
                        raise CoverageContractError("output digest binding mismatch")
                    validate_work_unit_output(output, plan)
                    if output.pre_render_note is not None:
                        if output.pre_render_note.document_id != plan.reference_document.document_id:
                            raise CoverageContractError("output note document ID mismatch")
                        if output.pre_render_note.reference_document_sha256 != plan.reference_document.sha256:
                            raise CoverageContractError("output note reference digest mismatch")
                    if output.work_unit_id != outcome.work_unit_id or output.attempt_ordinal != attempt.attempt_ordinal:
                        raise CoverageContractError("output unit/attempt binding mismatch")
                receipt_record = _lookup_digest_record(owner_records or receipts, attempt.receipt_ref.sha256)
                if owner_records is not None or receipts is not None:
                    _validate_owner_record(
                        attempt.receipt_ref,
                        receipt_record,
                        plan_sha256=closure.coverage_plan_sha256,
                        work_unit_id=outcome.work_unit_id,
                        attempt_ordinal=attempt.attempt_ordinal,
                    )
        if closure.coverage_closure_state == CoverageClosureState.CLOSED:
            for outcome in closure.unit_outcomes:
                if outcome.terminal_attempt_ordinal is None:
                    raise CoverageContractError("closed closure requires terminal attempts")

    if closure.coverage_closure_state == CoverageClosureState.CLOSED:
        if any(outcome.terminal_attempt_ordinal is None for outcome in closure.unit_outcomes):
            raise CoverageContractError("closed closure requires non-null terminals")
    return closure


validate_coverage_plan_artifact = validate_coverage_plan
validate_work_unit_output_artifact = validate_work_unit_output
validate_coverage_closure_artifact = validate_coverage_closure
canonical_q28_bytes = canonical_coverage_bytes
q28_artifact_sha256 = coverage_artifact_sha256


__all__ = [
    "AttemptBinding",
    "COVERAGE_CLOSURE_SCHEMA_VERSION",
    "COVERAGE_PLAN_SCHEMA_VERSION",
    "CoverageArtifact",
    "CoverageClosure",
    "CoverageClosureState",
    "CoverageCondition",
    "CoverageContractError",
    "CoveragePlan",
    "CoveragePlanArtifact",
    "CoverageClosureArtifact",
    "DependencyEdge",
    "EdgeKind",
    "ExecutionContractRef",
    "ExternalOwnerRecordRef",
    "Observation",
    "ObservationKind",
    "OutputCondition",
    "Q26CitationRef",
    "Q26NodeRef",
    "Q26PreRenderNoteRef",
    "ReferenceDocumentRef",
    "RouteDecisionRef",
    "RoutingPolicyRef",
    "SourceReferenceMapping",
    "SourceSectionRef",
    "SourceUnitRef",
    "UnitOutcome",
    "WORK_UNIT_IDENTITY_SCHEMA_VERSION",
    "WORK_UNIT_OUTPUT_SCHEMA_VERSION",
    "WorkUnitIdentitySeed",
    "WorkUnitOutput",
    "WorkUnitOutputArtifact",
    "WorkUnitSpec",
    "canonical_coverage_bytes",
    "canonical_coverage_closure_bytes",
    "canonical_coverage_plan_bytes",
    "canonical_identity_seed_bytes",
    "canonical_q28_bytes",
    "canonical_work_unit_output_bytes",
    "coverage_artifact_sha256",
    "coverage_closure_sha256",
    "coverage_plan_sha256",
    "derive_work_unit_id",
    "q28_artifact_sha256",
    "validate_coverage_artifact",
    "validate_coverage_closure",
    "validate_coverage_closure_artifact",
    "validate_coverage_plan",
    "validate_coverage_plan_artifact",
    "validate_work_unit_output",
    "validate_work_unit_output_artifact",
    "work_unit_id_from_seed",
    "work_unit_output_sha256",
]
