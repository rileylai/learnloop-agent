"""Q29 deterministic pre-generation routing contracts.

This module realizes the frozen routing artifact boundary only.  It does not
provide a mode-selection policy: callers must inject an approved deterministic
selector before a selected route can be materialized.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import (
    Annotated,
    Any,
    Callable,
    Generic,
    Literal,
    Mapping,
    Optional,
    Protocol,
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
    field_validator,
    model_validator,
)

from .normalized_document import (
    ElementKind,
    NormalizedDocument,
    NormalizedDocumentInput,
    SourceType,
    normalized_document_sha256,
    validate_normalized_document,
)

ROUTING_POLICY_SCHEMA_VERSION = "benchmark-generation-routing-policy/1.0.0"
ROUTING_INPUT_FACTS_SCHEMA_VERSION = "benchmark-generation-routing-input-facts/1.0.0"
ROUTE_DECISION_SCHEMA_VERSION = "benchmark-generation-route-decision/1.0.0"
FORCED_DIAGNOSTIC_SCHEMA_VERSION = "benchmark-generation-forced-diagnostic/1.0.0"
ROUTE_CONFORMANCE_SCHEMA_VERSION = "benchmark-generation-route-conformance/1.0.0"

ROUTING_MODE_ORDER = ("single-pass", "section-aware", "hierarchical")
MODALITY_ORDER = (
    "native_text",
    "scanned_image",
    "caption_text",
    "chat_text",
    "screenshot_image",
)
NORMALIZED_ELEMENT_KIND_ORDER = tuple(kind.value for kind in ElementKind)

_SHA256_PATTERN = r"^[0-9a-f]{64}$"

Sha256 = Annotated[StrictStr, Field(pattern=_SHA256_PATTERN)]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]
PositiveInt = Annotated[StrictInt, Field(ge=1)]


class RoutingContractError(ValueError):
    """Raised when a routing artifact or binding is invalid."""


class RoutingPolicyGapError(RoutingContractError):
    """Raised when no approved deterministic mode selector is supplied."""


class RouteMode(str, Enum):
    SINGLE_PASS = "single-pass"
    SECTION_AWARE = "section-aware"
    HIERARCHICAL = "hierarchical"


class RunMembership(str, Enum):
    FORMAL_REQUIRED = "formal_required"
    DIAGNOSTIC = "diagnostic"


class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class AvailabilityReason(str, Enum):
    NOT_OBSERVED = "not_observed"
    NOT_SUPPLIED = "not_supplied"
    NOT_SUPPORTED = "not_supported"
    NOT_APPROVED = "not_approved"
    REDACTED = "redacted"


class DecisionStatus(str, Enum):
    SELECTED = "selected"
    REJECTED = "rejected"


class DecisionReason(str, Enum):
    REQUIRED_FACT_UNAVAILABLE = "required_fact_unavailable"


class ConformanceStatus(str, Enum):
    CONFORMANT = "conformant"
    MISMATCH = "mismatch"
    REJECTED = "rejected"
    FORCED_DIAGNOSTIC = "forced_diagnostic"


class ConformanceReason(str, Enum):
    EXECUTED_MODE_MISMATCH = "executed_mode_mismatch"
    EXECUTION_CONTRACT_MISMATCH = "execution_contract_mismatch"
    ROUTE_DECISION_REJECTED = "route_decision_rejected"
    FORCED_MODE_EXECUTION = "forced_mode_execution"


class Modality(str, Enum):
    NATIVE_TEXT = "native_text"
    SCANNED_IMAGE = "scanned_image"
    CAPTION_TEXT = "caption_text"
    CHAT_TEXT = "chat_text"
    SCREENSHOT_IMAGE = "screenshot_image"


EnumT = TypeVar("EnumT", bound=Enum)
ValueT = TypeVar("ValueT")


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


RouteModeValue = Annotated[RouteMode, BeforeValidator(_enum_parser(RouteMode))]
RunMembershipValue = Annotated[
    RunMembership, BeforeValidator(_enum_parser(RunMembership))
]
AvailabilityStatusValue = Annotated[
    AvailabilityStatus, BeforeValidator(_enum_parser(AvailabilityStatus))
]
AvailabilityReasonValue = Annotated[
    AvailabilityReason, BeforeValidator(_enum_parser(AvailabilityReason))
]
DecisionStatusValue = Annotated[
    DecisionStatus, BeforeValidator(_enum_parser(DecisionStatus))
]
DecisionReasonValue = Annotated[
    DecisionReason, BeforeValidator(_enum_parser(DecisionReason))
]
ConformanceStatusValue = Annotated[
    ConformanceStatus, BeforeValidator(_enum_parser(ConformanceStatus))
]
ConformanceReasonValue = Annotated[
    ConformanceReason, BeforeValidator(_enum_parser(ConformanceReason))
]
ModalityValue = Annotated[Modality, BeforeValidator(_enum_parser(Modality))]
SourceTypeValue = Annotated[SourceType, BeforeValidator(_enum_parser(SourceType))]
ElementKindValue = Annotated[ElementKind, BeforeValidator(_enum_parser(ElementKind))]


def _tuple_from_json(value: object) -> object:
    if isinstance(value, list):
        return tuple(value)
    return value


class _StrictFrozenRoutingModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
        protected_namespaces=(),
    )


def _require_nonblank(value: str, field_name: str) -> str:
    if not value.strip():
        raise ValueError(f"{field_name} must be nonblank")
    return value


class ContractReference(_StrictFrozenRoutingModel):
    contract_id: StrictStr = Field(min_length=1)
    sha256: Sha256

    @field_validator("contract_id")
    @classmethod
    def _validate_id(cls, value: str) -> str:
        return _require_nonblank(value, "contract_id")


class PolicyBoundaryReference(_StrictFrozenRoutingModel):
    boundary_id: StrictStr = Field(min_length=1)
    evidence_sha256: Sha256
    configuration_sha256: Sha256

    @field_validator("boundary_id")
    @classmethod
    def _validate_id(cls, value: str) -> str:
        return _require_nonblank(value, "boundary_id")


class PolicyReference(_StrictFrozenRoutingModel):
    schema_version: Literal["benchmark-generation-routing-policy/1.0.0"]
    policy_id: StrictStr = Field(min_length=1)
    policy_revision: StrictStr = Field(min_length=1)
    sha256: Sha256
    configuration_sha256: Sha256

    @field_validator("policy_id", "policy_revision")
    @classmethod
    def _validate_identity(cls, value: str, info: Any) -> str:
        return _require_nonblank(value, info.field_name)


class ReferenceDocumentReference(_StrictFrozenRoutingModel):
    schema_version: Literal["normalized-document/1.0.0"]
    artifact_role: Literal["reference_document"]
    document_id: StrictStr = Field(min_length=1)
    sha256: Sha256


class ReferenceDigestReference(_StrictFrozenRoutingModel):
    document_id: StrictStr = Field(min_length=1)
    sha256: Sha256


class ProviderIdentity(_StrictFrozenRoutingModel):
    provider_id: StrictStr = Field(min_length=1)
    revision: StrictStr = Field(min_length=1)

    @field_validator("provider_id", "revision")
    @classmethod
    def _validate_identity(cls, value: str, info: Any) -> str:
        return _require_nonblank(value, info.field_name)


class ModelIdentity(_StrictFrozenRoutingModel):
    model_id: StrictStr = Field(min_length=1)
    revision: StrictStr = Field(min_length=1)

    @field_validator("model_id", "revision")
    @classmethod
    def _validate_identity(cls, value: str, info: Any) -> str:
        return _require_nonblank(value, info.field_name)


class TokenMeasurement(_StrictFrozenRoutingModel):
    unit: Literal["input_tokens"]
    count: NonNegativeInt
    measurement_contract_id: StrictStr = Field(min_length=1)
    measurement_contract_sha256: Sha256

    @field_validator("measurement_contract_id")
    @classmethod
    def _validate_contract_id(cls, value: str) -> str:
        return _require_nonblank(value, "measurement_contract_id")


class ContextCapacity(_StrictFrozenRoutingModel):
    unit: Literal["input_tokens"]
    maximum: PositiveInt


class Availability(_StrictFrozenRoutingModel, Generic[ValueT]):
    status: AvailabilityStatusValue
    value: Optional[ValueT] = None
    reason: Optional[AvailabilityReasonValue] = None

    @model_validator(mode="after")
    def _validate_value_and_reason(self) -> "Availability[ValueT]":
        if self.status == AvailabilityStatus.AVAILABLE:
            if self.value is None:
                raise ValueError("available fact requires a typed value")
            if self.reason is not None:
                raise ValueError("available fact must have reason=null")
        else:
            if self.value is not None:
                raise ValueError("unavailable fact must have value=null")
            if self.reason is None:
                raise ValueError("unavailable fact requires a machine-readable reason")
        return self


class RoutingReferenceFacts(_StrictFrozenRoutingModel):
    schema_version: Literal["normalized-document/1.0.0"]
    artifact_role: Literal["reference_document"]
    document_id: StrictStr = Field(min_length=1)
    sha256: Sha256


class RoutingSourceFacts(_StrictFrozenRoutingModel):
    source_type: SourceTypeValue
    source_snapshot_sha256: Sha256
    byte_count: NonNegativeInt
    token_count: Availability[TokenMeasurement]


class RoutingSectionFact(_StrictFrozenRoutingModel):
    section_id: StrictStr = Field(min_length=1)
    parent_section_id: Optional[StrictStr] = Field(default=None, min_length=1)
    heading_element_id: Optional[StrictStr] = Field(default=None, min_length=1)
    start_order: NonNegativeInt
    end_order: NonNegativeInt

    @model_validator(mode="after")
    def _validate_range(self) -> "RoutingSectionFact":
        if self.end_order < self.start_order:
            raise ValueError("section end_order must be at least start_order")
        if self.parent_section_id == self.section_id:
            raise ValueError("section must not be its own parent")
        return self


class RoutingElementFact(_StrictFrozenRoutingModel):
    element_id: StrictStr = Field(min_length=1)
    kind: ElementKindValue
    order: NonNegativeInt
    section_id: StrictStr = Field(min_length=1)
    parent_element_id: Optional[StrictStr] = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _validate_parent(self) -> "RoutingElementFact":
        if self.parent_element_id == self.element_id:
            raise ValueError("element must not be its own parent")
        return self


class RoutingStructureFacts(_StrictFrozenRoutingModel):
    sections: Tuple[RoutingSectionFact, ...] = Field(min_length=1)
    elements: Tuple[RoutingElementFact, ...] = Field(min_length=1)

    @field_validator("sections", "elements", mode="before")
    @classmethod
    def _accept_json_arrays(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_structure(self) -> "RoutingStructureFacts":
        section_ids = tuple(section.section_id for section in self.sections)
        if len(section_ids) != len(set(section_ids)):
            raise ValueError("routing section IDs must be unique")
        element_ids = tuple(element.element_id for element in self.elements)
        if len(element_ids) != len(set(element_ids)):
            raise ValueError("routing element IDs must be unique")
        orders = [element.order for element in self.elements]
        if orders != list(range(len(self.elements))):
            raise ValueError("routing element order must be gap-free and zero-based")
        section_by_id = {section.section_id: section for section in self.sections}
        element_by_id = {element.element_id: element for element in self.elements}
        for section in self.sections:
            if (
                section.parent_section_id is not None
                and section.parent_section_id not in section_by_id
            ):
                raise ValueError("routing parent section must reference a section")
            if section.end_order >= len(self.elements):
                raise ValueError("routing section range must reference an element")
        for element in self.elements:
            if element.section_id not in section_by_id:
                raise ValueError("routing element section must reference a section")
            if element.parent_element_id is not None and element.parent_element_id not in element_by_id:
                raise ValueError("routing parent element must reference an element")
            section = section_by_id[element.section_id]
            if not section.start_order <= element.order <= section.end_order:
                raise ValueError("routing element must be inside its section range")
        return self


class RoutingModalityFacts(_StrictFrozenRoutingModel):
    values: Tuple[ModalityValue, ...] = Field(min_length=1)

    @field_validator("values", mode="before")
    @classmethod
    def _accept_json_array(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_order(self) -> "RoutingModalityFacts":
        values = tuple(value.value for value in self.values)
        if len(values) != len(set(values)):
            raise ValueError("routing modality values must be unique")
        if values != tuple(
            value for value in MODALITY_ORDER if value in values
        ):
            raise ValueError("routing modality values must use canonical enum order")
        return self


class RoutingProviderModelFacts(_StrictFrozenRoutingModel):
    provider: Availability[ProviderIdentity]
    model: Availability[ModelIdentity]


class RoutingCapacityFacts(_StrictFrozenRoutingModel):
    context_capacity: Availability[ContextCapacity]


class RoutingExecutionFacts(_StrictFrozenRoutingModel):
    contract_id: StrictStr = Field(min_length=1)
    contract_sha256: Sha256

    @field_validator("contract_id")
    @classmethod
    def _validate_contract_id(cls, value: str) -> str:
        return _require_nonblank(value, "contract_id")


class RoutingInputFacts(_StrictFrozenRoutingModel):
    schema_version: Literal["benchmark-generation-routing-input-facts/1.0.0"]
    reference: RoutingReferenceFacts
    source: RoutingSourceFacts
    structure: RoutingStructureFacts
    modality: RoutingModalityFacts
    provider_model: RoutingProviderModelFacts
    capacity: RoutingCapacityFacts
    execution: RoutingExecutionFacts


class RoutingPolicy(_StrictFrozenRoutingModel):
    schema_version: Literal["benchmark-generation-routing-policy/1.0.0"]
    policy_id: StrictStr = Field(min_length=1)
    policy_revision: StrictStr = Field(min_length=1)
    implementation_id: StrictStr = Field(min_length=1)
    implementation_version: StrictStr = Field(min_length=1)
    configuration_sha256: Sha256
    input_facts_schema_version: Literal[
        "benchmark-generation-routing-input-facts/1.0.0"
    ]
    mode_order: Tuple[RouteModeValue, ...] = Field(min_length=3, max_length=3)
    boundary_references: Tuple[PolicyBoundaryReference, ...]
    execution_contract: ContractReference

    @field_validator(
        "policy_id",
        "policy_revision",
        "implementation_id",
        "implementation_version",
    )
    @classmethod
    def _validate_identity(cls, value: str, info: Any) -> str:
        return _require_nonblank(value, info.field_name)

    @field_validator("mode_order", "boundary_references", mode="before")
    @classmethod
    def _accept_json_arrays(cls, value: object) -> object:
        return _tuple_from_json(value)

    @model_validator(mode="after")
    def _validate_closed_mode_order(self) -> "RoutingPolicy":
        modes = tuple(mode.value for mode in self.mode_order)
        if modes != ROUTING_MODE_ORDER:
            raise ValueError("routing policy mode_order must be the frozen three-mode order")
        boundary_ids = tuple(item.boundary_id for item in self.boundary_references)
        if boundary_ids != tuple(sorted(boundary_ids)):
            raise ValueError("boundary_references must be sorted by boundary_id")
        if len(boundary_ids) != len(set(boundary_ids)):
            raise ValueError("boundary_references must have unique boundary IDs")
        return self


class RouteDecision(_StrictFrozenRoutingModel):
    schema_version: Literal["benchmark-generation-route-decision/1.0.0"]
    artifact_role: Literal["route_decision"]
    run_membership: RunMembershipValue
    policy: PolicyReference
    reference_document: ReferenceDocumentReference
    input_facts: RoutingInputFacts
    input_facts_sha256: Sha256
    execution_contract: ContractReference
    decision_status: DecisionStatusValue
    selected_mode: Optional[RouteModeValue] = None
    decision_reason: Optional[DecisionReasonValue] = None

    @model_validator(mode="after")
    def _validate_decision_pairing(self) -> "RouteDecision":
        if self.policy.schema_version != ROUTING_POLICY_SCHEMA_VERSION:
            raise ValueError("route decision policy schema mismatch")
        if self.input_facts.schema_version != ROUTING_INPUT_FACTS_SCHEMA_VERSION:
            raise ValueError("route decision input-facts schema mismatch")
        if self.reference_document.document_id != self.input_facts.reference.document_id:
            raise ValueError("route decision reference document ID mismatch")
        if self.reference_document.sha256 != self.input_facts.reference.sha256:
            raise ValueError("route decision reference document digest mismatch")
        if self.execution_contract != ContractReference(
            contract_id=self.input_facts.execution.contract_id,
            sha256=self.input_facts.execution.contract_sha256,
        ):
            raise ValueError("route decision execution contract mismatch")
        if self.decision_status == DecisionStatus.SELECTED:
            if self.selected_mode is None:
                raise ValueError("selected route decision requires selected_mode")
            if self.decision_reason is not None:
                raise ValueError("selected route decision must have decision_reason=null")
        else:
            if self.selected_mode is not None:
                raise ValueError("rejected route decision must have selected_mode=null")
            if self.decision_reason != DecisionReason.REQUIRED_FACT_UNAVAILABLE:
                raise ValueError(
                    "rejected route decision requires required_fact_unavailable"
                )
        return self


class ForcedDiagnostic(_StrictFrozenRoutingModel):
    schema_version: Literal["benchmark-generation-forced-diagnostic/1.0.0"]
    artifact_role: Literal["forced_diagnostic"]
    run_membership: Literal["diagnostic"]
    diagnostic_slot_id: StrictStr = Field(min_length=1)
    route_decision_sha256: Sha256
    reference_document: ReferenceDigestReference
    policy_selected_mode: Optional[RouteModeValue] = None
    effective_mode: RouteModeValue
    execution_contract: ContractReference

    @field_validator("diagnostic_slot_id")
    @classmethod
    def _validate_slot_id(cls, value: str) -> str:
        return _require_nonblank(value, "diagnostic_slot_id")


class RouteConformance(_StrictFrozenRoutingModel):
    schema_version: Literal["benchmark-generation-route-conformance/1.0.0"]
    artifact_role: Literal["route_conformance"]
    run_membership: RunMembershipValue
    route_decision_sha256: Sha256
    execution_contract: ContractReference
    policy_selected_mode: Optional[RouteModeValue] = None
    executed_mode: Optional[RouteModeValue] = None
    status: ConformanceStatusValue
    reason: Optional[ConformanceReasonValue] = None
    forced_diagnostic_sha256: Optional[Sha256] = None

    @model_validator(mode="after")
    def _validate_status_pairing(self) -> "RouteConformance":
        if self.status == ConformanceStatus.CONFORMANT:
            if self.reason is not None or self.forced_diagnostic_sha256 is not None:
                raise ValueError("conformant conformance must not have a reason or forced digest")
            if self.executed_mode is None or self.policy_selected_mode is None:
                raise ValueError("conformant conformance requires both route modes")
        elif self.status == ConformanceStatus.MISMATCH:
            if self.reason not in {
                ConformanceReason.EXECUTED_MODE_MISMATCH,
                ConformanceReason.EXECUTION_CONTRACT_MISMATCH,
            }:
                raise ValueError("mismatch requires a mismatch reason")
            if self.forced_diagnostic_sha256 is not None:
                raise ValueError("mismatch must not reference a forced diagnostic")
        elif self.status == ConformanceStatus.REJECTED:
            if self.reason != ConformanceReason.ROUTE_DECISION_REJECTED:
                raise ValueError("rejected conformance requires route_decision_rejected")
            if self.executed_mode is not None or self.forced_diagnostic_sha256 is not None:
                raise ValueError("rejected conformance must have no execution")
        else:
            if self.run_membership != RunMembership.DIAGNOSTIC:
                raise ValueError("forced conformance must be diagnostic")
            if self.reason != ConformanceReason.FORCED_MODE_EXECUTION:
                raise ValueError("forced conformance requires forced_mode_execution")
            if self.forced_diagnostic_sha256 is None or self.executed_mode is None:
                raise ValueError("forced conformance requires forced artifact and mode")
        return self


RoutingArtifact = Union[
    RoutingPolicy,
    RoutingInputFacts,
    RouteDecision,
    ForcedDiagnostic,
    RouteConformance,
]
RoutingArtifactInput = Union[RoutingArtifact, Mapping[str, Any]]


def _model_payload(value: Union[BaseModel, Mapping[str, Any]]) -> Mapping[str, Any]:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    return value


def validate_routing_artifact(artifact: RoutingArtifactInput) -> RoutingArtifact:
    payload = _model_payload(artifact)
    schema_version = payload.get("schema_version")
    if schema_version == ROUTING_POLICY_SCHEMA_VERSION:
        return RoutingPolicy.model_validate(payload)
    if schema_version == ROUTING_INPUT_FACTS_SCHEMA_VERSION:
        return RoutingInputFacts.model_validate(payload)
    if schema_version == ROUTE_DECISION_SCHEMA_VERSION:
        return RouteDecision.model_validate(payload)
    if schema_version == FORCED_DIAGNOSTIC_SCHEMA_VERSION:
        return ForcedDiagnostic.model_validate(payload)
    if schema_version == ROUTE_CONFORMANCE_SCHEMA_VERSION:
        return RouteConformance.model_validate(payload)
    raise RoutingContractError("unknown routing schema version")


def validate_routing_input_facts(artifact: RoutingArtifactInput) -> RoutingInputFacts:
    validated = validate_routing_artifact(artifact)
    if not isinstance(validated, RoutingInputFacts):
        raise RoutingContractError("artifact is not routing input-facts")
    return validated


def canonical_routing_bytes(artifact: RoutingArtifactInput) -> bytes:
    validated = validate_routing_artifact(artifact)
    payload = json.dumps(
        validated.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return payload.encode("utf-8")


def canonical_routing_input_facts_bytes(
    artifact: Union[RoutingInputFacts, Mapping[str, Any]],
) -> bytes:
    return canonical_routing_bytes(artifact)


def routing_artifact_sha256(artifact: RoutingArtifactInput) -> str:
    return hashlib.sha256(canonical_routing_bytes(artifact)).hexdigest()


def routing_input_facts_sha256(
    artifact: Union[RoutingInputFacts, Mapping[str, Any]],
) -> str:
    return hashlib.sha256(canonical_routing_input_facts_bytes(artifact)).hexdigest()


def routing_policy_sha256(policy: Union[RoutingPolicy, Mapping[str, Any]]) -> str:
    return routing_artifact_sha256(policy)


def route_decision_sha256(decision: Union[RouteDecision, Mapping[str, Any]]) -> str:
    return routing_artifact_sha256(decision)


def forced_diagnostic_sha256(
    artifact: Union[ForcedDiagnostic, Mapping[str, Any]],
) -> str:
    return routing_artifact_sha256(artifact)


def route_conformance_sha256(
    artifact: Union[RouteConformance, Mapping[str, Any]],
) -> str:
    return routing_artifact_sha256(artifact)


def _unavailable(value_type: Any, reason: AvailabilityReason) -> Any:
    return Availability[value_type](
        status=AvailabilityStatus.UNAVAILABLE,
        value=None,
        reason=reason,
    )


def _modality_from_reference(reference: NormalizedDocument) -> Tuple[Modality, ...]:
    source_type = reference.source.source_type
    if source_type == SourceType.WEB:
        return (Modality.NATIVE_TEXT,)
    if source_type == SourceType.YOUTUBE:
        return (Modality.CAPTION_TEXT,)
    if source_type == SourceType.CHAT:
        return (Modality.CHAT_TEXT,)
    if source_type == SourceType.SCREENSHOTS:
        return (Modality.SCREENSHOT_IMAGE,)

    method = reference.producer_provenance.processing_method
    pdf_modalities = {
        "project_authored_native_pdf": (Modality.NATIVE_TEXT,),
        "project_authored_deterministic_raster_scan": (Modality.SCANNED_IMAGE,),
        "project_authored_mixed_native_and_raster_pdf": (
            Modality.NATIVE_TEXT,
            Modality.SCANNED_IMAGE,
        ),
    }
    try:
        return pdf_modalities[method]
    except KeyError as exc:
        raise RoutingContractError(
            "modality fact is unavailable for this reference producer method"
        ) from exc


def _structure_from_reference(reference: NormalizedDocument) -> RoutingStructureFacts:
    return RoutingStructureFacts(
        sections=tuple(
            RoutingSectionFact(
                section_id=section.section_id,
                parent_section_id=section.parent_section_id,
                heading_element_id=section.heading_element_id,
                start_order=section.start_order,
                end_order=section.end_order,
            )
            for section in reference.sections
        ),
        elements=tuple(
            RoutingElementFact(
                element_id=element.element_id,
                kind=element.kind,
                order=element.order,
                section_id=element.section_id,
                parent_element_id=element.parent_element_id,
            )
            for element in reference.elements
        ),
    )


def materialize_routing_input_facts(
    reference_document: NormalizedDocumentInput,
    source_bytes: bytes,
    execution_contract: ContractReference,
    *,
    provider: Optional[Availability[ProviderIdentity]] = None,
    model: Optional[Availability[ModelIdentity]] = None,
    context_capacity: Optional[Availability[ContextCapacity]] = None,
    token_count: Optional[Availability[TokenMeasurement]] = None,
) -> RoutingInputFacts:
    """Materialize facts without copying source text or selecting a route."""

    reference = validate_normalized_document(reference_document)
    if not isinstance(source_bytes, bytes):
        raise RoutingContractError("source_bytes must be exact bytes")
    source_digest = hashlib.sha256(source_bytes).hexdigest()
    if source_digest != reference.source.source_snapshot_sha256:
        raise RoutingContractError("source bytes do not match reference source snapshot digest")

    input_facts = RoutingInputFacts(
        schema_version=ROUTING_INPUT_FACTS_SCHEMA_VERSION,
        reference=RoutingReferenceFacts(
            schema_version="normalized-document/1.0.0",
            artifact_role="reference_document",
            document_id=reference.document_id,
            sha256=normalized_document_sha256(reference),
        ),
        source=RoutingSourceFacts(
            source_type=reference.source.source_type,
            source_snapshot_sha256=reference.source.source_snapshot_sha256,
            byte_count=len(source_bytes),
            token_count=token_count
            or _unavailable(TokenMeasurement, AvailabilityReason.NOT_APPROVED),
        ),
        structure=_structure_from_reference(reference),
        modality=RoutingModalityFacts(values=_modality_from_reference(reference)),
        provider_model=RoutingProviderModelFacts(
            provider=provider
            or _unavailable(ProviderIdentity, AvailabilityReason.NOT_OBSERVED),
            model=model
            or _unavailable(ModelIdentity, AvailabilityReason.NOT_OBSERVED),
        ),
        capacity=RoutingCapacityFacts(
            context_capacity=context_capacity
            or _unavailable(ContextCapacity, AvailabilityReason.NOT_APPROVED),
        ),
        execution=RoutingExecutionFacts(
            contract_id=execution_contract.contract_id,
            contract_sha256=execution_contract.sha256,
        ),
    )
    validate_routing_input_facts(input_facts)
    return input_facts


def _reference_facts_equal(
    facts: RoutingInputFacts,
    reference: NormalizedDocument,
) -> None:
    expected_digest = normalized_document_sha256(reference)
    if facts.reference.document_id != reference.document_id:
        raise RoutingContractError("routing facts reference document ID mismatch")
    if facts.reference.sha256 != expected_digest:
        raise RoutingContractError("routing facts reference document digest mismatch")
    if facts.source.source_snapshot_sha256 != reference.source.source_snapshot_sha256:
        raise RoutingContractError("routing facts source snapshot digest mismatch")


def validate_routing_input_facts_bindings(
    facts: Union[RoutingInputFacts, Mapping[str, Any]],
    reference_document: NormalizedDocumentInput,
    *,
    source_bytes: Optional[bytes] = None,
) -> RoutingInputFacts:
    validated_facts = validate_routing_input_facts(facts)
    reference = validate_normalized_document(reference_document)
    _reference_facts_equal(validated_facts, reference)
    expected_structure = _structure_from_reference(reference)
    if validated_facts.structure != expected_structure:
        raise RoutingContractError("routing facts structure does not match reference document")
    if source_bytes is not None:
        if not isinstance(source_bytes, bytes):
            raise RoutingContractError("source_bytes must be exact bytes")
        actual_source_digest = hashlib.sha256(source_bytes).hexdigest()
        if actual_source_digest != validated_facts.source.source_snapshot_sha256:
            raise RoutingContractError("routing facts source digest mismatch")
        if len(source_bytes) != validated_facts.source.byte_count:
            raise RoutingContractError("routing facts source byte count mismatch")
    return validated_facts


class DeterministicModeSelector(Protocol):
    def __call__(
        self,
        policy: RoutingPolicy,
        facts: RoutingInputFacts,
    ) -> RouteMode:
        """Return one frozen mode using only pre-generation facts."""


def _fact_is_available(facts: RoutingInputFacts, path: str) -> bool:
    current: Any = facts
    for part in path.split("."):
        if not hasattr(current, part):
            raise RoutingContractError(f"unknown required fact path: {path}")
        current = getattr(current, part)
    if isinstance(current, Availability):
        return current.status == AvailabilityStatus.AVAILABLE
    return current is not None


def materialize_route_decision(
    policy: Union[RoutingPolicy, Mapping[str, Any]],
    input_facts: Union[RoutingInputFacts, Mapping[str, Any]],
    *,
    policy_sha256: str,
    run_membership: Union[RunMembership, str],
    required_fact_paths: Sequence[str] = (),
    selector: Optional[DeterministicModeSelector] = None,
) -> RouteDecision:
    """Execute the decision interface without providing a routing algorithm."""

    policy_model = RoutingPolicy.model_validate(_model_payload(policy))
    facts_model = validate_routing_input_facts(input_facts)
    membership = RunMembership(_enum_parser(RunMembership)(run_membership))
    if policy_model.execution_contract.contract_id != facts_model.execution.contract_id:
        raise RoutingContractError("policy and input-facts execution contract ID mismatch")
    if policy_model.execution_contract.sha256 != facts_model.execution.contract_sha256:
        raise RoutingContractError("policy and input-facts execution contract digest mismatch")
    if not isinstance(policy_sha256, str) or len(policy_sha256) != 64:
        raise RoutingContractError("policy_sha256 must be a lowercase SHA-256 digest")
    if policy_sha256 != routing_policy_sha256(policy_model):
        raise RoutingContractError("policy_sha256 does not match canonical policy bytes")

    unavailable = tuple(
        path for path in required_fact_paths if not _fact_is_available(facts_model, path)
    )
    policy_reference = PolicyReference(
        schema_version=ROUTING_POLICY_SCHEMA_VERSION,
        policy_id=policy_model.policy_id,
        policy_revision=policy_model.policy_revision,
        sha256=policy_sha256,
        configuration_sha256=policy_model.configuration_sha256,
    )
    reference_reference = ReferenceDocumentReference(
        schema_version="normalized-document/1.0.0",
        artifact_role="reference_document",
        document_id=facts_model.reference.document_id,
        sha256=facts_model.reference.sha256,
    )
    execution_reference = ContractReference(
        contract_id=facts_model.execution.contract_id,
        sha256=facts_model.execution.contract_sha256,
    )
    common = {
        "schema_version": ROUTE_DECISION_SCHEMA_VERSION,
        "artifact_role": "route_decision",
        "run_membership": membership,
        "policy": policy_reference,
        "reference_document": reference_reference,
        "input_facts": facts_model,
        "input_facts_sha256": routing_input_facts_sha256(facts_model),
        "execution_contract": execution_reference,
    }
    if unavailable:
        return RouteDecision(
            **common,
            decision_status=DecisionStatus.REJECTED,
            selected_mode=None,
            decision_reason=DecisionReason.REQUIRED_FACT_UNAVAILABLE,
        )
    if selector is None:
        raise RoutingPolicyGapError(
            "no approved deterministic mode selector implementation is available"
        )
    selected = selector(policy_model, facts_model)
    try:
        selected_mode = RouteMode(selected)
    except (TypeError, ValueError) as exc:
        raise RoutingContractError("mode selector returned an unknown routing mode") from exc
    if selected_mode.value not in policy_model.mode_order:
        raise RoutingContractError("mode selector returned a mode outside policy mode_order")
    return RouteDecision(
        **common,
        decision_status=DecisionStatus.SELECTED,
        selected_mode=selected_mode,
        decision_reason=None,
    )


def validate_route_decision_bindings(
    decision: Union[RouteDecision, Mapping[str, Any]],
    policy: Union[RoutingPolicy, Mapping[str, Any]],
    reference_document: NormalizedDocumentInput,
    *,
    source_bytes: Optional[bytes] = None,
) -> RouteDecision:
    decision_model = decision if isinstance(decision, RouteDecision) else RouteDecision.model_validate(decision)
    policy_model = policy if isinstance(policy, RoutingPolicy) else RoutingPolicy.model_validate(policy)
    facts = validate_routing_input_facts_bindings(
        decision_model.input_facts,
        reference_document,
        source_bytes=source_bytes,
    )
    actual_policy_digest = routing_policy_sha256(policy_model)
    if decision_model.policy.sha256 != actual_policy_digest:
        raise RoutingContractError("route decision policy digest mismatch")
    if decision_model.policy.policy_id != policy_model.policy_id:
        raise RoutingContractError("route decision policy ID mismatch")
    if decision_model.policy.policy_revision != policy_model.policy_revision:
        raise RoutingContractError("route decision policy revision mismatch")
    if decision_model.policy.configuration_sha256 != policy_model.configuration_sha256:
        raise RoutingContractError("route decision configuration digest mismatch")
    if decision_model.input_facts_sha256 != routing_input_facts_sha256(facts):
        raise RoutingContractError("route decision input-facts digest mismatch")
    if decision_model.execution_contract != policy_model.execution_contract:
        raise RoutingContractError("route decision execution contract mismatch")
    return decision_model


def build_forced_diagnostic(
    route_decision: Union[RouteDecision, Mapping[str, Any]],
    *,
    diagnostic_slot_id: str,
    effective_mode: Union[RouteMode, str],
    execution_contract: ContractReference,
) -> ForcedDiagnostic:
    decision = route_decision if isinstance(route_decision, RouteDecision) else RouteDecision.model_validate(route_decision)
    mode = RouteMode(_enum_parser(RouteMode)(effective_mode))
    return ForcedDiagnostic(
        schema_version=FORCED_DIAGNOSTIC_SCHEMA_VERSION,
        artifact_role="forced_diagnostic",
        run_membership="diagnostic",
        diagnostic_slot_id=diagnostic_slot_id,
        route_decision_sha256=route_decision_sha256(decision),
        reference_document=ReferenceDigestReference(
            document_id=decision.reference_document.document_id,
            sha256=decision.reference_document.sha256,
        ),
        policy_selected_mode=decision.selected_mode,
        effective_mode=mode,
        execution_contract=execution_contract,
    )


def validate_forced_diagnostic_bindings(
    forced: Union[ForcedDiagnostic, Mapping[str, Any]],
    route_decision: Union[RouteDecision, Mapping[str, Any]],
) -> ForcedDiagnostic:
    forced_model = forced if isinstance(forced, ForcedDiagnostic) else ForcedDiagnostic.model_validate(forced)
    decision = route_decision if isinstance(route_decision, RouteDecision) else RouteDecision.model_validate(route_decision)
    if forced_model.route_decision_sha256 != route_decision_sha256(decision):
        raise RoutingContractError("forced diagnostic route-decision digest mismatch")
    if forced_model.reference_document.document_id != decision.reference_document.document_id:
        raise RoutingContractError("forced diagnostic reference document ID mismatch")
    if forced_model.reference_document.sha256 != decision.reference_document.sha256:
        raise RoutingContractError("forced diagnostic reference document digest mismatch")
    if forced_model.policy_selected_mode != decision.selected_mode:
        raise RoutingContractError("forced diagnostic policy-selected mode mismatch")
    return forced_model


def build_route_conformance(
    route_decision: Union[RouteDecision, Mapping[str, Any]],
    *,
    execution_contract: ContractReference,
    executed_mode: Optional[Union[RouteMode, str]],
    forced_diagnostic: Optional[Union[ForcedDiagnostic, Mapping[str, Any]]] = None,
) -> RouteConformance:
    decision = route_decision if isinstance(route_decision, RouteDecision) else RouteDecision.model_validate(route_decision)
    forced = None
    if forced_diagnostic is not None:
        forced = validate_forced_diagnostic_bindings(forced_diagnostic, decision)
    executed = None if executed_mode is None else RouteMode(_enum_parser(RouteMode)(executed_mode))
    if forced is not None:
        return RouteConformance(
            schema_version=ROUTE_CONFORMANCE_SCHEMA_VERSION,
            artifact_role="route_conformance",
            run_membership=RunMembership.DIAGNOSTIC,
            route_decision_sha256=route_decision_sha256(decision),
            execution_contract=execution_contract,
            policy_selected_mode=decision.selected_mode,
            executed_mode=executed,
            status=ConformanceStatus.FORCED_DIAGNOSTIC,
            reason=ConformanceReason.FORCED_MODE_EXECUTION,
            forced_diagnostic_sha256=forced_diagnostic_sha256(forced),
        )
    if decision.decision_status == DecisionStatus.REJECTED:
        return RouteConformance(
            schema_version=ROUTE_CONFORMANCE_SCHEMA_VERSION,
            artifact_role="route_conformance",
            run_membership=decision.run_membership,
            route_decision_sha256=route_decision_sha256(decision),
            execution_contract=execution_contract,
            policy_selected_mode=None,
            executed_mode=None,
            status=ConformanceStatus.REJECTED,
            reason=ConformanceReason.ROUTE_DECISION_REJECTED,
            forced_diagnostic_sha256=None,
        )
    if execution_contract != decision.execution_contract:
        status = ConformanceStatus.MISMATCH
        reason = ConformanceReason.EXECUTION_CONTRACT_MISMATCH
    elif executed != decision.selected_mode:
        status = ConformanceStatus.MISMATCH
        reason = ConformanceReason.EXECUTED_MODE_MISMATCH
    else:
        status = ConformanceStatus.CONFORMANT
        reason = None
    return RouteConformance(
        schema_version=ROUTE_CONFORMANCE_SCHEMA_VERSION,
        artifact_role="route_conformance",
        run_membership=decision.run_membership,
        route_decision_sha256=route_decision_sha256(decision),
        execution_contract=execution_contract,
        policy_selected_mode=decision.selected_mode,
        executed_mode=executed,
        status=status,
        reason=reason,
        forced_diagnostic_sha256=None,
    )


def validate_route_conformance_bindings(
    conformance: Union[RouteConformance, Mapping[str, Any]],
    route_decision: Union[RouteDecision, Mapping[str, Any]],
    *,
    forced_diagnostic: Optional[Union[ForcedDiagnostic, Mapping[str, Any]]] = None,
) -> RouteConformance:
    conformance_model = conformance if isinstance(conformance, RouteConformance) else RouteConformance.model_validate(conformance)
    decision = route_decision if isinstance(route_decision, RouteDecision) else RouteDecision.model_validate(route_decision)
    if conformance_model.route_decision_sha256 != route_decision_sha256(decision):
        raise RoutingContractError("route conformance route-decision digest mismatch")
    if conformance_model.policy_selected_mode != decision.selected_mode:
        raise RoutingContractError("route conformance policy-selected mode mismatch")
    if conformance_model.status == ConformanceStatus.FORCED_DIAGNOSTIC:
        if forced_diagnostic is None:
            raise RoutingContractError("forced conformance requires forced diagnostic artifact")
        forced = validate_forced_diagnostic_bindings(forced_diagnostic, decision)
        expected_digest = forced_diagnostic_sha256(forced)
        if conformance_model.forced_diagnostic_sha256 != expected_digest:
            raise RoutingContractError("route conformance forced diagnostic digest mismatch")
        if conformance_model.executed_mode != forced.effective_mode:
            raise RoutingContractError("route conformance forced mode mismatch")
        if conformance_model.execution_contract != forced.execution_contract:
            raise RoutingContractError("route conformance forced contract mismatch")
    elif conformance_model.forced_diagnostic_sha256 is not None:
        raise RoutingContractError("ordinary conformance must not bind forced diagnostic")
    elif conformance_model.run_membership != decision.run_membership:
        raise RoutingContractError("route conformance run membership mismatch")
    if conformance_model.status == ConformanceStatus.CONFORMANT:
        if conformance_model.execution_contract != decision.execution_contract:
            raise RoutingContractError("conformant execution contract mismatch")
        if conformance_model.executed_mode != decision.selected_mode:
            raise RoutingContractError("conformant executed mode mismatch")
    if conformance_model.status == ConformanceStatus.MISMATCH:
        if decision.decision_status != DecisionStatus.SELECTED:
            raise RoutingContractError("mismatch conformance requires selected decision")
        if conformance_model.reason == ConformanceReason.EXECUTED_MODE_MISMATCH:
            if conformance_model.execution_contract != decision.execution_contract:
                raise RoutingContractError("mode mismatch has a contract mismatch")
            if conformance_model.executed_mode is None:
                raise RoutingContractError("mode mismatch requires executed mode")
            if conformance_model.executed_mode == decision.selected_mode:
                raise RoutingContractError("mode mismatch reason does not match modes")
        elif conformance_model.execution_contract == decision.execution_contract:
            raise RoutingContractError("contract mismatch reason does not match contracts")
    if conformance_model.status == ConformanceStatus.REJECTED:
        if decision.decision_status != DecisionStatus.REJECTED:
            raise RoutingContractError("rejected conformance requires rejected decision")
        if conformance_model.execution_contract != decision.execution_contract:
            raise RoutingContractError("rejected conformance contract mismatch")
    return conformance_model


__all__ = [
    "Availability",
    "AvailabilityReason",
    "AvailabilityStatus",
    "ContextCapacity",
    "ContractReference",
    "ConformanceReason",
    "ConformanceStatus",
    "DecisionReason",
    "DecisionStatus",
    "DeterministicModeSelector",
    "FORCED_DIAGNOSTIC_SCHEMA_VERSION",
    "ForcedDiagnostic",
    "ModelIdentity",
    "MODALITY_ORDER",
    "Modality",
    "PolicyBoundaryReference",
    "PolicyReference",
    "ROUTE_CONFORMANCE_SCHEMA_VERSION",
    "ROUTE_DECISION_SCHEMA_VERSION",
    "ROUTING_INPUT_FACTS_SCHEMA_VERSION",
    "ROUTING_MODE_ORDER",
    "ROUTING_POLICY_SCHEMA_VERSION",
    "RouteConformance",
    "RouteDecision",
    "RouteMode",
    "RoutingCapacityFacts",
    "RoutingContractError",
    "RoutingElementFact",
    "RoutingExecutionFacts",
    "RoutingInputFacts",
    "RoutingModalityFacts",
    "RoutingPolicy",
    "RoutingPolicyGapError",
    "RoutingProviderModelFacts",
    "RoutingReferenceFacts",
    "RoutingSectionFact",
    "RoutingSourceFacts",
    "RoutingStructureFacts",
    "RunMembership",
    "TokenMeasurement",
    "ProviderIdentity",
    "ReferenceDigestReference",
    "ReferenceDocumentReference",
    "build_forced_diagnostic",
    "build_route_conformance",
    "canonical_routing_bytes",
    "canonical_routing_input_facts_bytes",
    "forced_diagnostic_sha256",
    "materialize_route_decision",
    "materialize_routing_input_facts",
    "route_conformance_sha256",
    "route_decision_sha256",
    "routing_artifact_sha256",
    "routing_input_facts_sha256",
    "routing_policy_sha256",
    "validate_forced_diagnostic_bindings",
    "validate_route_conformance_bindings",
    "validate_route_decision_bindings",
    "validate_routing_artifact",
    "validate_routing_input_facts",
    "validate_routing_input_facts_bindings",
]
