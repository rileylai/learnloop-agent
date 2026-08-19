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
from typing import Annotated, Any, Literal, Mapping, Optional, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, ValidationError

from .coverage import (
    Q26PreRenderNoteRef,
    CoveragePlan,
    WORK_UNIT_OUTPUT_SCHEMA_VERSION,
    WorkUnitOutput,
    canonical_coverage_plan_bytes,
    canonical_work_unit_output_bytes,
    coverage_plan_sha256,
    materialize_single_pass_coverage_plan,
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

GENERATION_INPUT_SCHEMA_VERSION = "generation-input/1.0.0"
GENERATION_RESULT_SCHEMA_VERSION = "generation-lane-result/1.0.0"
GENERATION_ATTEMPT_SCHEMA_VERSION = "generation-lane-attempt/1.0.0"
GENERATION_RUNNER_VERSION = "parser-note-completeness-runner/1.0.0"
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_ATTEMPT_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
_Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]
_AttemptId = Annotated[StrictStr, Field(pattern=_ATTEMPT_ID_PATTERN)]


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
            producer_role="generator",
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
    _write_immutable(path.with_suffix(".sha256"), f"{digest}  {path.name}\n".encode("ascii"))
    return digest


def execute_generation_case(
    case: Any,
    benchmark_root: Path,
    output_dir: Path,
    *,
    attempt_id: str,
    attempt_ordinal: int,
) -> GenerationLaneOutcome:
    """Generate one deterministic pre-render note and lineage artifacts offline."""

    if re.fullmatch(_ATTEMPT_ID_PATTERN, attempt_id) is None:
        return GenerationLaneOutcome(2, "invalid_input", error="invalid attempt id")
    if attempt_ordinal < 1:
        return GenerationLaneOutcome(2, "invalid_input", error="invalid attempt ordinal")
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
        if plan_digest != coverage_plan_sha256(coverage_plan):
            raise _InvalidInput("coverage plan digest binding mismatch")
        validate_coverage_plan(
            coverage_plan,
            document,
            routing_policy=routing_policy,
            route_decision=route_decision,
            execution_contract=execution_contract,
        )
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
            schema_version=WORK_UNIT_OUTPUT_SCHEMA_VERSION,
            artifact_role="work_unit_output",
            coverage_plan_sha256=plan_digest,
            work_unit_id=work_unit.work_unit_id,
            attempt_ordinal=attempt_ordinal,
            output_condition="complete",
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
        )
    except _InvalidInput as exc:
        return GenerationLaneOutcome(2, "invalid_input", error=str(exc))
    except _OperationalFailure as exc:
        return GenerationLaneOutcome(1, "operational_failure", error=str(exc))
    except (ValidationError, ValueError) as exc:
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
