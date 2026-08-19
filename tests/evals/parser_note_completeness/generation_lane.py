"""Offline Generation-lane input and pre-render note execution.

The lane consumes only the frozen reference ``NormalizedDocument``.  Its
diagnostic producer is a deterministic, local projection into the frozen Q26
``BenchmarkNoteDocument`` boundary; it does not call a provider or decide
coverage, routing, quality, or authority semantics.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Mapping, Optional, Tuple, Union, cast

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, ValidationError

from .coverage import (
    Q26PreRenderNoteRef,
    CoveragePlan,
    CoverageClosure,
    CoverageClosureState,
    CoverageCondition,
    OutputCondition,
    UnitOutcome,
    AttemptBinding,
    WorkUnitOutput,
    canonical_coverage_plan_bytes,
    canonical_coverage_closure_bytes,
    canonical_work_unit_output_bytes,
    ExternalOwnerRecordRef,
    coverage_plan_sha256,
    materialize_single_pass_coverage_plan,
    validate_coverage_closure,
    validate_coverage_plan,
    validate_work_unit_output,
    work_unit_output_sha256,
)
from .normalized_document import (
    ElementKind,
    NormalizedDocument,
    canonical_normalized_document_bytes,
)
from .benchmark_note import (
    BenchmarkNoteDocument,
    CitationMode,
    CodeLanguageSource,
    CodeLanguageStatus,
    LineageMappingState,
    LineageParentRole,
    NoteCitation,
    NoteCodeMetadata,
    NoteHeaderRole,
    NoteLineage,
    NoteListKind,
    NoteListMetadata,
    NoteLocatorReference,
    NoteNode,
    NoteNodeKind,
    NoteProducerProvenance,
    NoteProducerRole,
    NoteTableCellMetadata,
    benchmark_note_citation_id,
    benchmark_note_node_id,
    canonical_benchmark_note_bytes,
    validate_benchmark_note_artifact,
)
from .routing import (
    ContractReference,
    RouteMode,
    RunMembership,
    RoutingPolicy,
    canonical_routing_bytes,
    materialize_route_decision,
    materialize_routing_input_facts,
    route_decision_sha256,
    routing_input_facts_sha256,
    routing_policy_sha256,
    validate_route_decision_bindings,
)
from .work_unit_receipt import (
    DurableWorkUnitAttemptReceipt,
    WorkUnitAttemptReceiptStore,
    WorkUnitReceiptContractError,
    build_work_unit_attempt_receipt,
    derive_history_id,
    persist_work_unit_attempt_receipt,
    read_durable_work_unit_attempt_receipt,
)

GENERATION_INPUT_SCHEMA_VERSION = "generation-input/1.0.0"
GENERATION_RESULT_SCHEMA_VERSION = "generation-lane-result/1.0.0"
GENERATION_ATTEMPT_SCHEMA_VERSION = "generation-lane-attempt/1.0.0"
GENERATION_RUNNER_VERSION = "parser-note-completeness-runner/1.0.0"
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_ATTEMPT_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
_Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]
_AttemptId = Annotated[StrictStr, Field(pattern=_ATTEMPT_ID_PATTERN)]
_ReceiptMembership = Literal["formal_required", "diagnostic"]


def _receipt_membership(value: RunMembership | str) -> _ReceiptMembership:
    return cast(_ReceiptMembership, value.value if isinstance(value, RunMembership) else value)


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class GenerationInputArtifact(_StrictFrozenModel):
    """A reference-bound input envelope, not a generated note document."""

    schema_version: Literal["generation-input/1.0.0"]
    runner_version: Literal["parser-note-completeness-runner/1.0.0"]
    artifact_type: Literal["parser_note_completeness_generation_input"]
    operation: Literal["prepare_generation_input"]
    case_id: StrictStr = Field(min_length=1)
    input_role: Literal["reference_document"]
    reference_sha256: _Digest
    reference_bytes: Annotated[StrictInt, Field(ge=0)]
    document_id: StrictStr = Field(min_length=1)
    source_type: Literal["pdf", "web", "youtube", "chat", "screenshots"]
    normalized_document_schema_version: Literal["normalized-document/1.0.0"]
    producer_configuration_sha256: _Digest


class GenerationResultArtifact(_StrictFrozenModel):
    """Execution result for a reference-bound pre-render note candidate."""

    schema_version: Literal["generation-lane-result/1.0.0"]
    runner_version: Literal["parser-note-completeness-runner/1.0.0"]
    artifact_type: Literal["parser_note_completeness_generation_result"]
    operation: Literal["generate_pre_render_note"]
    case_id: StrictStr = Field(min_length=1)
    reference_sha256: _Digest
    producer_configuration_sha256: _Digest
    generation_input_sha256: _Digest
    generation_input_bytes: Annotated[StrictInt, Field(ge=0)]
    candidate_sha256: _Digest
    candidate_bytes: Annotated[StrictInt, Field(ge=0)]
    routing_policy_sha256: Optional[_Digest] = None
    route_decision_sha256: Optional[_Digest] = None
    execution_contract_sha256: Optional[_Digest] = None
    coverage_plan_sha256: Optional[_Digest] = None
    work_unit_output_sha256: Optional[_Digest] = None
    attempt_id: _AttemptId
    status: Literal["contract_valid"]


class GenerationAttemptArtifact(_StrictFrozenModel):
    """Immutable attempt lineage for one pre-render note candidate."""

    schema_version: Literal["generation-lane-attempt/1.0.0"]
    runner_version: Literal["parser-note-completeness-runner/1.0.0"]
    artifact_type: Literal["parser_note_completeness_generation_attempt"]
    operation: Literal["generate_pre_render_note"]
    case_id: StrictStr = Field(min_length=1)
    reference_sha256: _Digest
    producer_configuration_sha256: _Digest
    generation_input_sha256: _Digest
    candidate_sha256: _Digest
    result_sha256: _Digest
    routing_policy_sha256: Optional[_Digest] = None
    route_decision_sha256: Optional[_Digest] = None
    execution_contract_sha256: Optional[_Digest] = None
    coverage_plan_sha256: Optional[_Digest] = None
    work_unit_output_sha256: Optional[_Digest] = None
    attempt_id: _AttemptId
    status: Literal["contract_valid"]


GenerationLaneArtifact = Union[
    GenerationInputArtifact,
    GenerationResultArtifact,
    GenerationAttemptArtifact,
]


class GenerationLaneOutcome:
    """Small runner-facing result with operational status kept separate."""

    __slots__ = (
        "exit_code",
        "status",
        "candidate_digest",
        "generation_input_digest",
        "result_digest",
        "attempt_digest",
        "routing_policy_digest",
        "route_decision_digest",
        "execution_contract_digest",
        "coverage_plan_digest",
        "work_unit_output_digest",
        "work_unit_attempt_receipt_digest",
        "coverage_closure_digest",
        "error",
    )

    def __init__(
        self,
        exit_code: int,
        status: str,
        *,
        candidate_digest: Optional[str] = None,
        generation_input_digest: Optional[str] = None,
        result_digest: Optional[str] = None,
        attempt_digest: Optional[str] = None,
        routing_policy_digest: Optional[str] = None,
        route_decision_digest: Optional[str] = None,
        execution_contract_digest: Optional[str] = None,
        coverage_plan_digest: Optional[str] = None,
        work_unit_output_digest: Optional[str] = None,
        work_unit_attempt_receipt_digest: Optional[str] = None,
        coverage_closure_digest: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        self.exit_code = exit_code
        self.status = status
        self.candidate_digest = candidate_digest
        self.generation_input_digest = generation_input_digest
        self.result_digest = result_digest
        self.attempt_digest = attempt_digest
        self.routing_policy_digest = routing_policy_digest
        self.route_decision_digest = route_decision_digest
        self.execution_contract_digest = execution_contract_digest
        self.coverage_plan_digest = coverage_plan_digest
        self.work_unit_output_digest = work_unit_output_digest
        self.work_unit_attempt_receipt_digest = work_unit_attempt_receipt_digest
        self.coverage_closure_digest = coverage_closure_digest
        self.error = error


class _InvalidInput(Exception):
    """Reference or Generation input contract failure."""


class _OperationalFailure(Exception):
    """Local artifact I/O failure."""


def _artifact_model(payload: Union[GenerationLaneArtifact, Mapping[str, Any]]) -> GenerationLaneArtifact:
    if isinstance(
        payload,
        (GenerationInputArtifact, GenerationResultArtifact, GenerationAttemptArtifact),
    ):
        return payload
    if not isinstance(payload, Mapping):
        raise TypeError("generation lane artifact must be a mapping or validated model")
    artifact_type = payload.get("artifact_type")
    if artifact_type == "parser_note_completeness_generation_input":
        return GenerationInputArtifact.model_validate(payload)
    if artifact_type == "parser_note_completeness_generation_result":
        return GenerationResultArtifact.model_validate(payload)
    if artifact_type == "parser_note_completeness_generation_attempt":
        return GenerationAttemptArtifact.model_validate(payload)
    raise ValueError("unknown generation lane artifact type")


def canonical_generation_lane_artifact_bytes(
    payload: Union[GenerationLaneArtifact, Mapping[str, Any]],
) -> bytes:
    """Validate and serialize a Generation-lane artifact canonically."""

    model = _artifact_model(payload)
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


def generation_lane_artifact_sha256(
    payload: Union[GenerationLaneArtifact, Mapping[str, Any]],
) -> str:
    return hashlib.sha256(canonical_generation_lane_artifact_bytes(payload)).hexdigest()


def _read_bounded_file(root: Path, relative_path: str, label: str) -> tuple[Path, bytes]:
    try:
        root_resolved = root.resolve(strict=True)
        target = (root / relative_path).resolve(strict=True)
        target.relative_to(root_resolved)
        if not target.is_file():
            raise OSError("not a regular file")
        return target, target.read_bytes()
    except (OSError, ValueError) as exc:
        raise _OperationalFailure(f"{label} is unavailable or outside the benchmark root") from exc


def _read_checksum_record(data: bytes, expected_filename: str) -> str:
    try:
        fields = data.decode("ascii").strip().split()
    except UnicodeDecodeError as exc:
        raise _InvalidInput("invalid external digest record") from exc
    if len(fields) != 2 or fields[1] != expected_filename:
        raise _InvalidInput("invalid external digest record")
    if re.fullmatch(_DIGEST_PATTERN, fields[0]) is None:
        raise _InvalidInput("invalid external digest record")
    return fields[0]


def _read_reference(
    case: Any,
    benchmark_root: Path,
) -> tuple[NormalizedDocument, str, int]:
    reference_path, reference_bytes = _read_bounded_file(
        benchmark_root,
        case.reference_path,
        "canonical reference",
    )
    _, digest_bytes = _read_bounded_file(
        benchmark_root,
        case.reference_digest_path,
        "reference checksum record",
    )
    expected_digest = _read_checksum_record(
        digest_bytes,
        PurePosixPath(case.reference_path).name,
    )
    actual_digest = hashlib.sha256(reference_bytes).hexdigest()
    if expected_digest != case.reference_sha256 or actual_digest != case.reference_sha256:
        raise _InvalidInput("reference digest binding mismatch")
    try:
        payload = json.loads(reference_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
        raise _InvalidInput("canonical reference JSON is invalid") from exc
    try:
        document = NormalizedDocument.model_validate(payload)
    except ValidationError as exc:
        raise _InvalidInput("canonical reference schema is invalid") from exc
    if document.artifact_role.value != "reference_document":
        raise _InvalidInput("Generation input requires a reference_document")
    if document.document_id != case.case_id:
        raise _InvalidInput("reference document ID does not match case")
    if canonical_normalized_document_bytes(document) != reference_bytes:
        raise _InvalidInput("canonical reference is not canonical")
    if document.source.source_snapshot_sha256 != case.source_sha256:
        raise _InvalidInput("reference source binding mismatch")
    if document.producer_provenance.configuration_sha256 != case.producer_configuration_sha256:
        raise _InvalidInput("reference configuration binding mismatch")
    return document, actual_digest, len(reference_bytes)


_DIAGNOSTIC_ROUTING_POLICY_ID = "diagnostic-routing-policy"
_DIAGNOSTIC_ROUTING_POLICY_REVISION = "revision-001"
_DIAGNOSTIC_ROUTING_CONFIGURATION_SHA256 = hashlib.sha256(
    b"diagnostic-fixed-single-pass-selector/1.0.0"
).hexdigest()
_DIAGNOSTIC_EXECUTION_CONTRACT_ID = "generation-diagnostic-v1"


def _diagnostic_execution_contract(case: Any) -> ContractReference:
    contract_seed = (
        "generation-diagnostic-execution-contract/1.0.0\n"
        + case.producer_configuration_sha256
    ).encode("ascii")
    return ContractReference(
        contract_id=_DIAGNOSTIC_EXECUTION_CONTRACT_ID,
        sha256=hashlib.sha256(contract_seed).hexdigest(),
    )


def _read_source_for_routing(case: Any, benchmark_root: Path) -> bytes:
    _, source_bytes = _read_bounded_file(
        benchmark_root,
        case.source_artifact_path,
        "source snapshot",
    )
    _, digest_bytes = _read_bounded_file(
        benchmark_root,
        case.source_digest_path,
        "source checksum record",
    )
    expected_digest = _read_checksum_record(
        digest_bytes,
        PurePosixPath(case.source_artifact_path).name,
    )
    actual_digest = hashlib.sha256(source_bytes).hexdigest()
    if expected_digest != case.source_sha256 or actual_digest != case.source_sha256:
        raise _InvalidInput("routing source digest binding mismatch")
    return source_bytes


def _select_diagnostic_single_pass(policy: RoutingPolicy, facts: Any) -> RouteMode:
    """Use the preregistered diagnostic route only; this is not production routing."""

    del policy, facts
    return RouteMode.SINGLE_PASS


def _materialize_generation_coverage(
    case: Any,
    benchmark_root: Path,
    document: NormalizedDocument,
) -> tuple[Any, Any, Any, ContractReference, Any]:
    source_bytes = _read_source_for_routing(case, benchmark_root)
    execution_contract = _diagnostic_execution_contract(case)
    routing_policy = RoutingPolicy(
        schema_version="benchmark-generation-routing-policy/1.0.0",
        policy_id=_DIAGNOSTIC_ROUTING_POLICY_ID,
        policy_revision=_DIAGNOSTIC_ROUTING_POLICY_REVISION,
        implementation_id="diagnostic-fixed-single-pass-selector",
        implementation_version="1.0.0",
        configuration_sha256=_DIAGNOSTIC_ROUTING_CONFIGURATION_SHA256,
        input_facts_schema_version="benchmark-generation-routing-input-facts/1.0.0",
        mode_order=(
            RouteMode.SINGLE_PASS,
            RouteMode.SECTION_AWARE,
            RouteMode.HIERARCHICAL,
        ),
        boundary_references=(),
        execution_contract=execution_contract,
    )
    input_facts = materialize_routing_input_facts(
        document,
        source_bytes,
        execution_contract,
    )
    route_decision = materialize_route_decision(
        routing_policy,
        input_facts,
        policy_sha256=routing_policy_sha256(routing_policy),
        run_membership=RunMembership.DIAGNOSTIC,
        selector=_select_diagnostic_single_pass,
    )
    validate_route_decision_bindings(
        route_decision,
        routing_policy,
        document,
        source_bytes=source_bytes,
    )
    coverage_plan = materialize_single_pass_coverage_plan(
        document,
        routing_policy,
        route_decision,
        execution_contract,
        plan_id=f"{case.case_id}-coverage",
        plan_revision=case.fixture_revision,
    )
    return (
        routing_policy,
        input_facts,
        route_decision,
        execution_contract,
        coverage_plan,
    )


def build_generation_input(case: Any, benchmark_root: Path) -> GenerationInputArtifact:
    """Materialize only the frozen reference-bound Generation input envelope."""

    document, reference_digest, reference_bytes = _read_reference(case, Path(benchmark_root))
    return GenerationInputArtifact(
        schema_version="generation-input/1.0.0",
        runner_version="parser-note-completeness-runner/1.0.0",
        artifact_type="parser_note_completeness_generation_input",
        operation="prepare_generation_input",
        case_id=case.case_id,
        input_role="reference_document",
        reference_sha256=reference_digest,
        reference_bytes=reference_bytes,
        document_id=document.document_id,
        source_type=document.source.source_type.value,
        normalized_document_schema_version=document.schema_version,
        producer_configuration_sha256=document.producer_provenance.configuration_sha256,
    )


_Q26_SUPPORTED_ELEMENT_KINDS = frozenset(
    {
        ElementKind.HEADING,
        ElementKind.PARAGRAPH,
        ElementKind.LIST_ITEM,
        ElementKind.QUOTE,
        ElementKind.CODE_BLOCK,
        ElementKind.TABLE,
        ElementKind.TABLE_ROW,
        ElementKind.TABLE_CELL,
        ElementKind.FIGURE,
        ElementKind.CAPTION,
        ElementKind.FORMULA,
        ElementKind.TRANSCRIPT_SEGMENT,
        ElementKind.MESSAGE,
    }
)


def _candidate_elements(document: NormalizedDocument) -> tuple[Any, ...]:
    """Select only reference elements representable without semantic invention."""

    elements_by_id = {element.element_id: element for element in document.elements}
    selected = []
    for element in document.elements:
        if element.kind not in _Q26_SUPPORTED_ELEMENT_KINDS:
            continue
        if element.kind == ElementKind.CAPTION:
            parent = elements_by_id.get(element.parent_element_id or "")
            if parent is None or parent.kind != ElementKind.FIGURE:
                continue
        if element.kind == ElementKind.LIST_ITEM:
            metadata = element.list_metadata
            if metadata is None:
                continue
            if metadata.nesting_level > 0 and element.parent_element_id is None:
                continue
        if element.kind == ElementKind.TABLE_CELL and element.table_cell_metadata is None:
            continue
        selected.append(element)
    return tuple(selected)


def _build_pre_render_note(
    document: NormalizedDocument,
    *,
    reference_digest: str,
    configuration_digest: str,
) -> BenchmarkNoteDocument:
    selected = _candidate_elements(document)
    node_ids_by_element: dict[str, str] = {}
    occurrences: dict[tuple[str, str], int] = {}

    for element in selected:
        first_locator = element.locators[0]
        anchor = {
            "anchor_type": "reference_locator",
            "element_id": element.element_id,
            "locator_index": 0,
            "locator_type": first_locator.locator_type,
        }
        key = (json.dumps(anchor, sort_keys=True), element.kind.value)
        occurrence = occurrences.get(key, 0)
        occurrences[key] = occurrence + 1
        node_ids_by_element[element.element_id] = benchmark_note_node_id(
            document.document_id,
            anchor,
            element.kind.value,
            occurrence,
        )

    nodes: list[NoteNode] = []
    for element in selected:
        note_kind = NoteNodeKind(element.kind.value)
        locator_refs = tuple(
            NoteLocatorReference(
                locator_type=locator.locator_type,
                element_id=element.element_id,
                locator_index=index,
            )
            for index, locator in enumerate(element.locators)
        )
        node_id = node_ids_by_element[element.element_id]
        citation = NoteCitation(
            citation_id=benchmark_note_citation_id(node_id, 0),
            reference_document_id=document.document_id,
            element_id=element.element_id,
            mode=CitationMode.WHOLE_ELEMENT,
            locator_refs=locator_refs,
        )

        list_metadata = None
        if element.list_metadata is not None:
            list_metadata = NoteListMetadata(
                list_kind=element.list_metadata.list_kind.value,
                nesting_level=element.list_metadata.nesting_level,
                ordinal=element.list_metadata.ordinal,
            )

        table_cell_metadata = None
        if element.table_cell_metadata is not None:
            header_role = element.table_cell_metadata.header_role
            table_cell_metadata = NoteTableCellMetadata(
                row_index=element.table_cell_metadata.row_index,
                column_index=element.table_cell_metadata.column_index,
                row_span=element.table_cell_metadata.row_span,
                column_span=element.table_cell_metadata.column_span,
                header_role=(
                    NoteHeaderRole(header_role.value) if header_role is not None else None
                ),
            )

        code_metadata = None
        if note_kind == NoteNodeKind.CODE_BLOCK:
            source_code_metadata = element.code_metadata
            if source_code_metadata is None:
                code_metadata = NoteCodeMetadata(
                    code_language_status=CodeLanguageStatus.UNAVAILABLE,
                    reason="language_unavailable",
                )
            else:
                code_metadata = NoteCodeMetadata(
                    code_language_status=CodeLanguageStatus.AVAILABLE,
                    language_hint=source_code_metadata.language_hint,
                    language_source=(
                        CodeLanguageSource.SOURCE_DECLARED
                        if source_code_metadata.source_supplied
                        else CodeLanguageSource.PRODUCER_DETECTED
                    ),
                )

        nodes.append(
            NoteNode(
                node_id=node_id,
                kind=note_kind,
                order=len(nodes),
                parent_node_id=(
                    node_ids_by_element.get(element.parent_element_id)
                    if element.parent_element_id is not None
                    else None
                ),
                content=element.content,
                languages=element.languages,
                list_metadata=list_metadata,
                table_cell_metadata=table_cell_metadata,
                code_metadata=code_metadata,
                citations=(citation,),
            )
        )

    candidate = BenchmarkNoteDocument(
        schema_version="benchmark-note-document/1.0.0",
        artifact_role="pre_render_note",
        document_id=document.document_id,
        reference_document_sha256=reference_digest,
        nodes=tuple(nodes),
        producer_provenance=NoteProducerProvenance(
            producer_role=NoteProducerRole.GENERATOR,
            producer_name="learnloop-diagnostic-generator",
            producer_version="1.0.0",
            configuration_sha256=configuration_digest,
            processing_method="deterministic_reference_projection",
            processing_stage="pre_render_generation",
        ),
        lineage=NoteLineage(
            parent_artifact_role=LineageParentRole.REFERENCE_DOCUMENT,
            parent_artifact_sha256=reference_digest,
            mapping_state=LineageMappingState.NOT_APPLICABLE,
            mappings=(),
        ),
    )
    validate_benchmark_note_artifact(candidate, document)
    return candidate


def build_pre_render_note(case: Any, benchmark_root: Path) -> BenchmarkNoteDocument:
    """Build a deterministic Q26 pre-render note from the frozen reference only."""

    document, reference_digest, _ = _read_reference(case, Path(benchmark_root))
    return _build_pre_render_note(
        document,
        reference_digest=reference_digest,
        configuration_digest=case.producer_configuration_sha256,
    )


def _write_immutable(path: Path, data: bytes) -> None:
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise _OperationalFailure("immutable output already exists") from exc
    except OSError as exc:
        raise _OperationalFailure("Generation output is not writable") from exc
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
    except OSError as exc:
        raise _OperationalFailure("Generation output write failed") from exc


def _write_artifact(path: Path, data: bytes) -> str:
    digest = hashlib.sha256(data).hexdigest()
    _write_immutable(path, data)
    digest_path = path.with_suffix(".sha256")
    _write_immutable(digest_path, f"{digest}  {path.name}\n".encode("ascii"))
    try:
        if path.read_bytes() != data:
            raise _OperationalFailure("Generation artifact durable readback mismatch")
        if digest_path.read_text(encoding="ascii").strip() != f"{digest}  {path.name}":
            raise _OperationalFailure("Generation artifact digest record mismatch")
    except OSError as exc:
        raise _OperationalFailure("Generation artifact durable readback failed") from exc
    return digest


def _read_durable_work_unit_output(path: Path) -> tuple[WorkUnitOutput, str]:
    try:
        data = path.read_bytes()
        fields = path.with_suffix(".sha256").read_text(encoding="ascii").strip().split()
    except (OSError, UnicodeError) as exc:
        raise _InvalidInput("work-unit output durability record is unavailable") from exc
    if len(fields) != 2 or fields[1] != path.name:
        raise _InvalidInput("work-unit output digest record is invalid")
    digest = hashlib.sha256(data).hexdigest()
    if fields[0] != digest:
        raise _InvalidInput("work-unit output digest record mismatch")
    try:
        output = WorkUnitOutput.model_validate(json.loads(data))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise _InvalidInput("work-unit output artifact is invalid") from exc
    if canonical_work_unit_output_bytes(output) != data or work_unit_output_sha256(output) != digest:
        raise _InvalidInput("work-unit output artifact is not canonical")
    return output, digest


def _generation_attempt_artifacts(
    output_dir: Path,
    coverage_plan: CoveragePlan,
    *,
    reference_document: NormalizedDocument,
    attempt_root: Optional[Path] = None,
) -> tuple[
    tuple[AttemptBinding, ...],
    dict[str, WorkUnitOutput],
    WorkUnitAttemptReceiptStore,
]:
    attempt_root = attempt_root or output_dir.parent.parent
    receipt_store = WorkUnitAttemptReceiptStore.from_execution_root(attempt_root)
    current_unit_id = coverage_plan.work_units[0].work_unit_id
    bindings: list[AttemptBinding] = []
    outputs: dict[str, WorkUnitOutput] = {}
    try:
        attempt_dirs = sorted(
            (path for path in attempt_root.glob("attempt-*") if path.is_dir()),
            key=lambda path: int(path.name.removeprefix("attempt-")),
        )
    except (OSError, ValueError) as exc:
        raise _InvalidInput("work-unit attempt history is unavailable") from exc
    for attempt_dir in attempt_dirs:
        execution_dir = attempt_dir / "execution"
        owner_execution_dir = execution_dir
        if not (owner_execution_dir / "work_unit_output.json").exists():
            nested_generation_dir = execution_dir / "generation"
            if nested_generation_dir.is_dir():
                owner_execution_dir = nested_generation_dir
        output_path = owner_execution_dir / "work_unit_output.json"
        output_digest_path = owner_execution_dir / "work_unit_output.sha256"
        receipt_path = owner_execution_dir / "work_unit_attempt_receipt.json"
        receipt_digest_path = owner_execution_dir / "work_unit_attempt_receipt.sha256"
        present = any(
            path.exists()
            for path in (
                output_path,
                output_digest_path,
                receipt_path,
                receipt_digest_path,
            )
        )
        if not present:
            continue
        if not all(
            path.exists()
            for path in (output_path, output_digest_path, receipt_path, receipt_digest_path)
        ):
            raise _InvalidInput("work-unit attempt output/receipt history is incomplete")
        output, output_digest = _read_durable_work_unit_output(output_path)
        try:
            receipt_record = read_durable_work_unit_attempt_receipt(
                receipt_path, receipt_digest_path
            )
        except WorkUnitReceiptContractError as exc:
            raise _InvalidInput(str(exc)) from exc
        receipt = receipt_record.receipt
        validate_work_unit_output(
            output,
            coverage_plan,
            reference_document=reference_document,
        )
        if output.work_unit_id != current_unit_id:
            raise _InvalidInput("generation coverage supports one planned work unit only")
        if (
            receipt.receipt_role != "attempt_terminal"
            or receipt.work_unit_output_sha256 != output_digest
            or receipt.work_unit_id != output.work_unit_id
            or receipt.attempt_ordinal != output.attempt_ordinal
        ):
            raise _InvalidInput("work-unit receipt/output binding mismatch")
        outputs[output_digest] = output
        bindings.append(
            AttemptBinding(
                attempt_ordinal=output.attempt_ordinal,
                output_sha256=output_digest,
                receipt_ref=ExternalOwnerRecordRef(
                    schema_version=receipt.schema_version,
                    sha256=receipt_record.sha256,
                    record_type=receipt.artifact_role,
                    record_id=receipt.record_id,
                ),
            )
        )
    bindings.sort(key=lambda binding: binding.attempt_ordinal)
    if not bindings:
        raise _InvalidInput("Q28 closure dependency gap: no durable work-unit attempt receipt")
    return tuple(bindings), outputs, receipt_store


def _write_generation_coverage_closure(
    *,
    output_dir: Path,
    coverage_plan: CoveragePlan,
    coverage_plan_digest: str,
    reference_document: NormalizedDocument,
    final_note: BenchmarkNoteDocument,
    final_note_digest: str,
    attempt_root: Optional[Path] = None,
) -> str:
    bindings, outputs, receipt_store = _generation_attempt_artifacts(
        output_dir,
        coverage_plan,
        reference_document=reference_document,
        attempt_root=attempt_root,
    )
    terminal = bindings[-1]
    current_output = outputs[terminal.output_sha256]
    if current_output.pre_render_note is None:
        raise _InvalidInput("closed Q28 closure requires a final pre_render_note")
    closure = CoverageClosure(
        schema_version="benchmark-generation-coverage-closure/1.0.0",
        artifact_role="coverage_closure",
        coverage_closure_state=CoverageClosureState.CLOSED,
        coverage_plan_sha256=coverage_plan_digest,
        unit_outcomes=(
            UnitOutcome(
                work_unit_id=coverage_plan.work_units[0].work_unit_id,
                attempts=bindings,
                terminal_attempt_ordinal=terminal.attempt_ordinal,
                coverage_condition=CoverageCondition(current_output.output_condition.value),
            ),
        ),
        observed_merge_order=coverage_plan.planned_merge_order,
        final_pre_render_note=current_output.pre_render_note,
        source_reference_mappings=(),
        observations=(),
    )
    validate_coverage_closure(
        closure,
        coverage_plan,
        output_artifacts=outputs,
        owner_records=receipt_store,
        reference_document=reference_document,
        final_pre_render_note_artifact=final_note,
        q26_artifacts={final_note_digest: final_note},
    )
    closure_bytes = canonical_coverage_closure_bytes(closure)
    closure_digest = _write_artifact(output_dir / "coverage_closure.json", closure_bytes)
    if closure_digest != hashlib.sha256(closure_bytes).hexdigest():
        raise _InvalidInput("coverage closure digest binding mismatch")
    return closure_digest


def _materialize_failed_work_unit_receipt(
    *,
    output_dir: Path,
    coverage_plan: CoveragePlan,
    coverage_plan_digest: str,
    reference_document: NormalizedDocument,
    attempt_ordinal: int,
    membership: RunMembership,
    logical_run_id: str,
    attempt_id: str,
    runner_plan_sha256: str,
    runner_slot_id: str,
    runner_attempt_ordinal: int,
    runner_invocation_id: str,
    start_receipt_record: DurableWorkUnitAttemptReceipt,
    existing_output: Optional[WorkUnitOutput],
    existing_output_digest: Optional[str],
) -> None:
    """Durably retain an owner failure after a started work-unit attempt."""

    output = existing_output
    output_digest = existing_output_digest
    if output is None or output_digest is None:
        output = WorkUnitOutput(
            schema_version="benchmark-generation-work-unit-output/1.0.0",
            artifact_role="work_unit_output",
            coverage_plan_sha256=coverage_plan_digest,
            work_unit_id=coverage_plan.work_units[0].work_unit_id,
            attempt_ordinal=attempt_ordinal,
            output_condition=OutputCondition.FAILED,
            pre_render_note=None,
        )
        validate_work_unit_output(output, coverage_plan, reference_document=reference_document)
        output_bytes = canonical_work_unit_output_bytes(output)
        output_digest = _write_artifact(output_dir / "work_unit_output.json", output_bytes)
    terminal = build_work_unit_attempt_receipt(
        receipt_role="attempt_terminal",
        lifecycle_status="failed",
        coverage_plan_sha256=coverage_plan_digest,
        work_unit_id=output.work_unit_id,
        attempt_ordinal=output.attempt_ordinal,
        work_unit_output_sha256=output_digest,
        membership=_receipt_membership(membership),
        logical_run_id=logical_run_id,
        execution_id=attempt_id,
        runner_plan_sha256=runner_plan_sha256,
        runner_slot_id=runner_slot_id,
        runner_attempt_ordinal=runner_attempt_ordinal,
        runner_invocation_id=runner_invocation_id,
        previous_receipt_sha256=start_receipt_record.sha256,
    )
    receipt_path = output_dir / "work_unit_attempt_receipt.json"
    if receipt_path.exists() or receipt_path.with_suffix(".sha256").exists():
        return
    persist_work_unit_attempt_receipt(terminal, receipt_path)


def execute_generation_case(
    case: Any,
    benchmark_root: Path,
    output_dir: Path,
    *,
    attempt_id: str,
    attempt_ordinal: int,
    runner_plan_sha256: str,
    runner_slot_id: str,
    runner_attempt_ordinal: int,
    runner_invocation_id: str,
    logical_run_id: str,
    attempt_root: Optional[Path] = None,
) -> GenerationLaneOutcome:
    """Generate one deterministic pre-render note and owner lineage offline.

    The caller supplies the outer attempt context, while the effective Q15
    per-work-unit ordinal is resolved from durable owner history.  The outer
    runner ordinal is carried separately in ``runner_binding`` and is never
    used as an inferred owner ordinal.
    """

    if re.fullmatch(_ATTEMPT_ID_PATTERN, attempt_id) is None:
        return GenerationLaneOutcome(2, "invalid_input", error="invalid attempt id")
    if attempt_ordinal < 1 or runner_attempt_ordinal < 1:
        return GenerationLaneOutcome(2, "invalid_input", error="invalid attempt ordinal")
    if re.fullmatch(_ATTEMPT_ID_PATTERN, runner_slot_id) is None:
        return GenerationLaneOutcome(2, "invalid_input", error="invalid runner slot id")
    if re.fullmatch(_ATTEMPT_ID_PATTERN, runner_invocation_id) is None:
        return GenerationLaneOutcome(2, "invalid_input", error="invalid runner invocation id")
    if re.fullmatch(_ATTEMPT_ID_PATTERN, logical_run_id) is None:
        return GenerationLaneOutcome(2, "invalid_input", error="invalid logical run id")
    if re.fullmatch(_DIGEST_PATTERN, runner_plan_sha256) is None:
        return GenerationLaneOutcome(2, "invalid_input", error="invalid runner plan digest")
    start_receipt_record: Optional[DurableWorkUnitAttemptReceipt] = None
    coverage_plan: Optional[CoveragePlan] = None
    coverage_plan_digest: Optional[str] = None
    document: Optional[NormalizedDocument] = None
    reference_digest: Optional[str] = None
    candidate_model: Optional[BenchmarkNoteDocument] = None
    candidate_digest: Optional[str] = None
    work_unit_output: Optional[WorkUnitOutput] = None
    work_unit_output_digest: Optional[str] = None
    terminal_receipt_record: Optional[DurableWorkUnitAttemptReceipt] = None
    route_decision = None
    receipt_attempt_root = attempt_root or output_dir.parent.parent

    def retain_failed_owner_history() -> None:
        if (
            start_receipt_record is None
            or coverage_plan is None
            or coverage_plan_digest is None
            or document is None
            or route_decision is None
        ):
            return
        if (output_dir / "work_unit_attempt_receipt.json").exists():
            return
        try:
            _materialize_failed_work_unit_receipt(
                output_dir=output_dir,
                coverage_plan=coverage_plan,
                coverage_plan_digest=coverage_plan_digest,
                reference_document=document,
                attempt_ordinal=attempt_ordinal,
                membership=_receipt_membership(route_decision.run_membership),
                logical_run_id=logical_run_id,
                attempt_id=attempt_id,
                runner_plan_sha256=runner_plan_sha256,
                runner_slot_id=runner_slot_id,
                runner_attempt_ordinal=runner_attempt_ordinal,
                runner_invocation_id=runner_invocation_id,
                start_receipt_record=start_receipt_record,
                existing_output=work_unit_output,
                existing_output_digest=work_unit_output_digest,
            )
        except (OSError, ValueError, WorkUnitReceiptContractError, _OperationalFailure):
            # Preserve the original execution failure.  The absence of a
            # durable owner failure receipt keeps any later closure fail-closed.
            return
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        input_model = build_generation_input(case, benchmark_root)
        input_bytes = canonical_generation_lane_artifact_bytes(input_model)
        input_digest = _write_artifact(output_dir / "generation_input.json", input_bytes)
        document, reference_digest, _ = _read_reference(case, Path(benchmark_root))
        if reference_digest != input_model.reference_sha256:
            raise _InvalidInput("Generation input and note reference binding mismatch")
        (
            routing_policy,
            input_facts,
            route_decision,
            execution_contract,
            coverage_plan,
        ) = _materialize_generation_coverage(case, Path(benchmark_root), document)
        assert coverage_plan is not None
        policy_digest = _write_artifact(
            output_dir / "routing_policy.json",
            canonical_routing_bytes(routing_policy),
        )
        facts_digest = _write_artifact(
            output_dir / "routing_input_facts.json",
            canonical_routing_bytes(input_facts),
        )
        route_digest = _write_artifact(
            output_dir / "route_decision.json",
            canonical_routing_bytes(route_decision),
        )
        if facts_digest != routing_input_facts_sha256(input_facts):
            raise _InvalidInput("routing facts digest binding mismatch")
        if route_digest != route_decision_sha256(route_decision):
            raise _InvalidInput("route decision digest binding mismatch")
        if policy_digest != routing_policy_sha256(routing_policy):
            raise _InvalidInput("routing policy digest binding mismatch")
        plan_digest = _write_artifact(
            output_dir / "coverage_plan.json",
            canonical_coverage_plan_bytes(coverage_plan),
        )
        coverage_plan_digest = plan_digest
        if plan_digest != coverage_plan_sha256(coverage_plan):
            raise _InvalidInput("coverage plan digest binding mismatch")
        validate_coverage_plan(
            coverage_plan,
            document,
            routing_policy=routing_policy,
            route_decision=route_decision,
            execution_contract=execution_contract,
        )
        history_id = derive_history_id(
            coverage_plan_sha256=plan_digest,
            work_unit_id=coverage_plan.work_units[0].work_unit_id,
            logical_run_id=logical_run_id,
        )
        prior_store = WorkUnitAttemptReceiptStore.from_execution_root(receipt_attempt_root)
        # The Q15 work-unit ordinal is derived from durable owner history.  It
        # is intentionally independent from the outer runner ordinal: a
        # runner attempt interrupted before Generation starts creates no Q15
        # attempt and therefore does not consume this ordinal.
        attempt_ordinal = prior_store.next_attempt_ordinal(history_id=history_id)
        try:
            previous_receipt_sha256 = prior_store.latest_terminal_digest(
                history_id=history_id
            )
            start_receipt = build_work_unit_attempt_receipt(
                receipt_role="attempt_started",
                lifecycle_status="started",
                coverage_plan_sha256=plan_digest,
                work_unit_id=coverage_plan.work_units[0].work_unit_id,
                attempt_ordinal=attempt_ordinal,
                work_unit_output_sha256=None,
                membership=_receipt_membership(route_decision.run_membership),
                logical_run_id=logical_run_id,
                execution_id=attempt_id,
                runner_plan_sha256=runner_plan_sha256,
                runner_slot_id=runner_slot_id,
                runner_attempt_ordinal=runner_attempt_ordinal,
                runner_invocation_id=runner_invocation_id,
                previous_receipt_sha256=previous_receipt_sha256,
            )
            start_receipt_record = persist_work_unit_attempt_receipt(
                start_receipt,
                output_dir / "work_unit_attempt_start.json",
            )
        except WorkUnitReceiptContractError as exc:
            raise _InvalidInput(str(exc)) from exc
        candidate_model = _build_pre_render_note(
            document,
            reference_digest=reference_digest,
            configuration_digest=input_model.producer_configuration_sha256,
        )
        candidate_bytes = canonical_benchmark_note_bytes(candidate_model)
        candidate_digest = _write_artifact(
            output_dir / "candidate.json",
            candidate_bytes,
        )
        work_unit = coverage_plan.work_units[0]
        work_unit_output = WorkUnitOutput(
            schema_version="benchmark-generation-work-unit-output/1.0.0",
            artifact_role="work_unit_output",
            coverage_plan_sha256=plan_digest,
            work_unit_id=work_unit.work_unit_id,
            attempt_ordinal=attempt_ordinal,
            output_condition=OutputCondition.COMPLETE,
            pre_render_note=Q26PreRenderNoteRef(
                schema_version=candidate_model.schema_version,
                artifact_role=candidate_model.artifact_role,
                document_id=candidate_model.document_id,
                reference_document_sha256=candidate_model.reference_document_sha256,
                sha256=candidate_digest,
            ),
        )
        validate_work_unit_output(
            work_unit_output,
            coverage_plan,
            reference_document=document,
            pre_render_note_artifact=candidate_model,
        )
        work_unit_output_bytes = canonical_work_unit_output_bytes(work_unit_output)
        work_unit_output_digest = _write_artifact(
            output_dir / "work_unit_output.json",
            work_unit_output_bytes,
        )
        if work_unit_output_digest != work_unit_output_sha256(work_unit_output):
            raise _InvalidInput("work-unit output digest binding mismatch")
        try:
            terminal_receipt = build_work_unit_attempt_receipt(
                receipt_role="attempt_terminal",
                lifecycle_status="complete",
                coverage_plan_sha256=plan_digest,
                work_unit_id=work_unit_output.work_unit_id,
                attempt_ordinal=work_unit_output.attempt_ordinal,
                work_unit_output_sha256=work_unit_output_digest,
                membership=_receipt_membership(route_decision.run_membership),
                logical_run_id=logical_run_id,
                execution_id=attempt_id,
                runner_plan_sha256=runner_plan_sha256,
                runner_slot_id=runner_slot_id,
                runner_attempt_ordinal=runner_attempt_ordinal,
                runner_invocation_id=runner_invocation_id,
                previous_receipt_sha256=(
                    start_receipt_record.sha256 if start_receipt_record is not None else None
                ),
            )
            terminal_receipt_record = persist_work_unit_attempt_receipt(
                terminal_receipt,
                output_dir / "work_unit_attempt_receipt.json",
            )
        except WorkUnitReceiptContractError as exc:
            raise _InvalidInput(str(exc)) from exc
        assert (
            candidate_model is not None
            and candidate_digest is not None
            and work_unit_output_digest is not None
            and coverage_plan is not None
        )
        coverage_closure_digest = _write_generation_coverage_closure(
            output_dir=output_dir,
            coverage_plan=coverage_plan,
            coverage_plan_digest=plan_digest,
            reference_document=document,
            final_note=candidate_model,
            final_note_digest=candidate_digest,
            attempt_root=receipt_attempt_root,
        )
        assert (
            candidate_digest is not None
            and work_unit_output_digest is not None
            and terminal_receipt_record is not None
            and coverage_plan_digest is not None
        )
        result_model = GenerationResultArtifact(
            schema_version="generation-lane-result/1.0.0",
            runner_version="parser-note-completeness-runner/1.0.0",
            artifact_type="parser_note_completeness_generation_result",
            operation="generate_pre_render_note",
            case_id=case.case_id,
            reference_sha256=input_model.reference_sha256,
            producer_configuration_sha256=input_model.producer_configuration_sha256,
            generation_input_sha256=input_digest,
            generation_input_bytes=len(input_bytes),
            candidate_sha256=candidate_digest,
            candidate_bytes=len(candidate_bytes),
            routing_policy_sha256=policy_digest,
            route_decision_sha256=route_digest,
            execution_contract_sha256=execution_contract.sha256,
            coverage_plan_sha256=plan_digest,
            work_unit_output_sha256=work_unit_output_digest,
            attempt_id=attempt_id,
            status="contract_valid",
        )
        result_bytes = canonical_generation_lane_artifact_bytes(result_model)
        result_digest = _write_artifact(output_dir / "result.json", result_bytes)
        attempt_model = GenerationAttemptArtifact(
            schema_version="generation-lane-attempt/1.0.0",
            runner_version="parser-note-completeness-runner/1.0.0",
            artifact_type="parser_note_completeness_generation_attempt",
            operation="generate_pre_render_note",
            case_id=case.case_id,
            reference_sha256=input_model.reference_sha256,
            producer_configuration_sha256=input_model.producer_configuration_sha256,
            generation_input_sha256=input_digest,
            candidate_sha256=candidate_digest,
            result_sha256=result_digest,
            routing_policy_sha256=policy_digest,
            route_decision_sha256=route_digest,
            execution_contract_sha256=execution_contract.sha256,
            coverage_plan_sha256=plan_digest,
            work_unit_output_sha256=work_unit_output_digest,
            attempt_id=attempt_id,
            status="contract_valid",
        )
        attempt_digest = _write_artifact(
            output_dir / "attempt.json",
            canonical_generation_lane_artifact_bytes(attempt_model),
        )
        return GenerationLaneOutcome(
            0,
            "contract_valid",
            candidate_digest=candidate_digest,
            generation_input_digest=input_digest,
            result_digest=result_digest,
            attempt_digest=attempt_digest,
            routing_policy_digest=policy_digest,
            route_decision_digest=route_digest,
            execution_contract_digest=execution_contract.sha256,
            coverage_plan_digest=plan_digest,
            work_unit_output_digest=work_unit_output_digest,
            work_unit_attempt_receipt_digest=terminal_receipt_record.sha256,
            coverage_closure_digest=coverage_closure_digest,
        )
    except _InvalidInput as exc:
        retain_failed_owner_history()
        return GenerationLaneOutcome(2, "invalid_input", error=str(exc))
    except _OperationalFailure as exc:
        retain_failed_owner_history()
        return GenerationLaneOutcome(1, "operational_failure", error=str(exc))
    except (ValidationError, ValueError) as exc:
        retain_failed_owner_history()
        return GenerationLaneOutcome(2, "invalid_input", error=str(exc))


__all__ = [
    "GENERATION_ATTEMPT_SCHEMA_VERSION",
    "GENERATION_INPUT_SCHEMA_VERSION",
    "GENERATION_RESULT_SCHEMA_VERSION",
    "GenerationAttemptArtifact",
    "GenerationInputArtifact",
    "GenerationLaneArtifact",
    "GenerationLaneOutcome",
    "GenerationResultArtifact",
    "build_generation_input",
    "build_pre_render_note",
    "canonical_generation_lane_artifact_bytes",
    "execute_generation_case",
    "generation_lane_artifact_sha256",
]
