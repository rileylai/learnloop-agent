"""Offline Generation-lane input binding for diagnostic runs.

The Generation note, coverage, and routing schemas are not frozen yet.  This
module therefore stops at the legal execution boundary: it validates the
frozen reference ``NormalizedDocument`` and materializes a deterministic input
binding artifact without inventing a note candidate schema.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Mapping, Optional, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, ValidationError

from .normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
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
    """Execution result for the materialized Generation input boundary."""

    schema_version: Literal["generation-lane-result/1.0.0"]
    runner_version: Literal["parser-note-completeness-runner/1.0.0"]
    artifact_type: Literal["parser_note_completeness_generation_result"]
    operation: Literal["prepare_generation_input"]
    case_id: StrictStr = Field(min_length=1)
    reference_sha256: _Digest
    generation_input_sha256: _Digest
    generation_input_bytes: Annotated[StrictInt, Field(ge=0)]
    attempt_id: _AttemptId
    status: Literal["input_materialized"]


class GenerationAttemptArtifact(_StrictFrozenModel):
    """Immutable attempt lineage for one Generation input preparation."""

    schema_version: Literal["generation-lane-attempt/1.0.0"]
    runner_version: Literal["parser-note-completeness-runner/1.0.0"]
    artifact_type: Literal["parser_note_completeness_generation_attempt"]
    operation: Literal["prepare_generation_input"]
    case_id: StrictStr = Field(min_length=1)
    reference_sha256: _Digest
    generation_input_sha256: _Digest
    result_sha256: _Digest
    attempt_id: _AttemptId
    status: Literal["input_materialized"]


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
        "generation_input_digest",
        "result_digest",
        "attempt_digest",
        "error",
    )

    def __init__(
        self,
        exit_code: int,
        status: str,
        *,
        generation_input_digest: Optional[str] = None,
        result_digest: Optional[str] = None,
        attempt_digest: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        self.exit_code = exit_code
        self.status = status
        self.generation_input_digest = generation_input_digest
        self.result_digest = result_digest
        self.attempt_digest = attempt_digest
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
) -> GenerationLaneOutcome:
    """Prepare one deterministic input and its lineage artifacts offline."""

    if re.fullmatch(_ATTEMPT_ID_PATTERN, attempt_id) is None:
        return GenerationLaneOutcome(2, "invalid_input", error="invalid attempt id")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        input_model = build_generation_input(case, benchmark_root)
        input_bytes = canonical_generation_lane_artifact_bytes(input_model)
        input_digest = _write_artifact(output_dir / "generation_input.json", input_bytes)
        result_model = GenerationResultArtifact(
            schema_version="generation-lane-result/1.0.0",
            runner_version="parser-note-completeness-runner/1.0.0",
            artifact_type="parser_note_completeness_generation_result",
            operation="prepare_generation_input",
            case_id=case.case_id,
            reference_sha256=input_model.reference_sha256,
            generation_input_sha256=input_digest,
            generation_input_bytes=len(input_bytes),
            attempt_id=attempt_id,
            status="input_materialized",
        )
        result_bytes = canonical_generation_lane_artifact_bytes(result_model)
        result_digest = _write_artifact(output_dir / "result.json", result_bytes)
        attempt_model = GenerationAttemptArtifact(
            schema_version="generation-lane-attempt/1.0.0",
            runner_version="parser-note-completeness-runner/1.0.0",
            artifact_type="parser_note_completeness_generation_attempt",
            operation="prepare_generation_input",
            case_id=case.case_id,
            reference_sha256=input_model.reference_sha256,
            generation_input_sha256=input_digest,
            result_sha256=result_digest,
            attempt_id=attempt_id,
            status="input_materialized",
        )
        attempt_digest = _write_artifact(
            output_dir / "attempt.json",
            canonical_generation_lane_artifact_bytes(attempt_model),
        )
        return GenerationLaneOutcome(
            0,
            "input_materialized",
            generation_input_digest=input_digest,
            result_digest=result_digest,
            attempt_digest=attempt_digest,
        )
    except _InvalidInput as exc:
        return GenerationLaneOutcome(2, "invalid_input", error=str(exc))
    except _OperationalFailure as exc:
        return GenerationLaneOutcome(1, "operational_failure", error=str(exc))


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
    "canonical_generation_lane_artifact_bytes",
    "execute_generation_case",
    "generation_lane_artifact_sha256",
]
