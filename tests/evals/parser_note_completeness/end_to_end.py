"""D12 deterministic offline End-to-end lane."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, Callable, Literal, Mapping, Optional, TypeVar, Union, cast

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

from .benchmark_note import (
    BenchmarkNoteDocument,
    RenderedNoteProjection,
    benchmark_note_sha256,
    canonical_benchmark_note_bytes,
    validate_benchmark_note_artifact,
)
from .generation_lane import (
    GenerationAttemptArtifact,
    GenerationLaneOutcome,
    GenerationResultArtifact,
    canonical_generation_lane_artifact_bytes,
    execute_generation_case,
)
from .normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
    normalized_document_sha256,
)
from .parser_lane import (
    ParserLaneAttemptArtifact,
    ParserLaneOutcome,
    ParserLaneResultArtifact,
    canonical_parser_lane_artifact_bytes,
    execute_parser_case,
)
from .renderer import (
    RendererCaptureArtifact,
    RendererContractError,
    RendererOperationalError,
    build_renderer_capture,
    canonical_renderer_capture_bytes,
    parse_rendered_note_projection,
    render_pre_render_note_to_html,
    renderer_capture_sha256,
    validate_renderer_capture,
)

END_TO_END_RESULT_SCHEMA_VERSION = "benchmark-end-to-end-result/1.0.0"
END_TO_END_ATTEMPT_SCHEMA_VERSION = "benchmark-end-to-end-attempt/1.0.0"
END_TO_END_RESULT_ARTIFACT_TYPE = "parser_note_completeness_end_to_end_result"
END_TO_END_ATTEMPT_ARTIFACT_TYPE = "parser_note_completeness_end_to_end_attempt"
END_TO_END_OPERATION = "execute_end_to_end"
RUNNER_VERSION = "parser-note-completeness-runner/1.0.0"

_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]
Identifier = Annotated[StrictStr, Field(pattern=_ID_PATTERN)]
PositiveOrdinal = Annotated[StrictInt, Field(ge=1)]


class EndToEndContractError(ValueError):
    """End-to-end schema or lineage contract rejection."""


class EndToEndOperationalError(Exception):
    """End-to-end execution or durable-store failure."""


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class EndToEndExecutionIdentity(_StrictFrozenModel):
    runner_plan_sha256: Digest
    runner_slot_id: Identifier
    runner_attempt_ordinal: PositiveOrdinal
    runner_invocation_id: Identifier
    logical_run_id: Identifier
    membership: Literal["diagnostic"]


class EndToEndResultArtifact(_StrictFrozenModel):
    schema_version: Literal["benchmark-end-to-end-result/1.0.0"]
    runner_version: Literal["parser-note-completeness-runner/1.0.0"]
    artifact_type: Literal["parser_note_completeness_end_to_end_result"]
    operation: Literal["execute_end_to_end"]
    case_id: StrictStr = Field(min_length=1)
    raw_source_sha256: Digest
    parser_result_sha256: Digest
    parser_attempt_sha256: Digest
    parser_output_sha256: Digest
    generation_result_sha256: Digest
    generation_attempt_sha256: Digest
    generation_output_sha256: Digest
    pre_render_note_sha256: Digest
    renderer_output_sha256: Digest
    renderer_capture_sha256: Digest
    rendered_note_projection_sha256: Digest
    execution_contract_sha256: Digest
    execution_identity: EndToEndExecutionIdentity
    attempt_id: Identifier
    status: Literal["contract_valid"]


class EndToEndAttemptArtifact(_StrictFrozenModel):
    schema_version: Literal["benchmark-end-to-end-attempt/1.0.0"]
    runner_version: Literal["parser-note-completeness-runner/1.0.0"]
    artifact_type: Literal["parser_note_completeness_end_to_end_attempt"]
    operation: Literal["execute_end_to_end"]
    case_id: StrictStr = Field(min_length=1)
    raw_source_sha256: Digest
    parser_result_sha256: Digest
    parser_attempt_sha256: Digest
    parser_output_sha256: Digest
    generation_result_sha256: Digest
    generation_attempt_sha256: Digest
    generation_output_sha256: Digest
    pre_render_note_sha256: Digest
    renderer_output_sha256: Digest
    renderer_capture_sha256: Digest
    rendered_note_projection_sha256: Digest
    execution_contract_sha256: Digest
    execution_identity: EndToEndExecutionIdentity
    attempt_id: Identifier
    result_sha256: Digest
    status: Literal["contract_valid"]


EndToEndArtifact = Union[EndToEndResultArtifact, EndToEndAttemptArtifact]


@dataclass(frozen=True)
class EndToEndOutcome:
    exit_code: int
    status: str
    result_digest: Optional[str] = None
    attempt_digest: Optional[str] = None
    parser_result_digest: Optional[str] = None
    generation_result_digest: Optional[str] = None
    renderer_output_digest: Optional[str] = None
    renderer_capture_digest: Optional[str] = None
    rendered_projection_digest: Optional[str] = None
    error: Optional[str] = None


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


ModelT = TypeVar("ModelT", bound=BaseModel)


def _artifact_model(payload: Union[EndToEndArtifact, Mapping[str, Any]]) -> EndToEndArtifact:
    if isinstance(payload, (EndToEndResultArtifact, EndToEndAttemptArtifact)):
        return payload
    if not isinstance(payload, Mapping):
        raise TypeError("End-to-end artifact must be a mapping or validated model")
    artifact_type = payload.get("artifact_type")
    if artifact_type == END_TO_END_RESULT_ARTIFACT_TYPE:
        return EndToEndResultArtifact.model_validate(payload)
    if artifact_type == END_TO_END_ATTEMPT_ARTIFACT_TYPE:
        return EndToEndAttemptArtifact.model_validate(payload)
    raise ValueError("unknown End-to-end artifact type")


def canonical_end_to_end_artifact_bytes(
    payload: Union[EndToEndArtifact, Mapping[str, Any]],
) -> bytes:
    return _canonical_json_bytes(_artifact_model(payload).model_dump(mode="json"))


def end_to_end_artifact_sha256(
    payload: Union[EndToEndArtifact, Mapping[str, Any]],
) -> str:
    return _sha256(canonical_end_to_end_artifact_bytes(payload))


def _write_immutable_artifact(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = _sha256(data)
    digest_path = path.with_suffix(".sha256")
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise EndToEndOperationalError("immutable artifact already exists") from exc
    except OSError as exc:
        raise EndToEndOperationalError("artifact output is not writable") from exc
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
    except OSError as exc:
        raise EndToEndOperationalError("artifact output write failed") from exc
    try:
        descriptor = os.open(
            digest_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
        )
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(f"{digest}  {path.name}\n".encode("ascii"))
    except FileExistsError as exc:
        raise EndToEndOperationalError("immutable digest record already exists") from exc
    except OSError as exc:
        raise EndToEndOperationalError("artifact digest record write failed") from exc
    try:
        if path.read_bytes() != data:
            raise EndToEndOperationalError("artifact durable readback mismatch")
        if digest_path.read_text(encoding="ascii").strip() != f"{digest}  {path.name}":
            raise EndToEndOperationalError("artifact digest record mismatch")
    except OSError as exc:
        raise EndToEndOperationalError("artifact durable readback failed") from exc
    return digest


def _read_immutable_artifact(path: Path) -> tuple[bytes, str]:
    digest_path = path.with_suffix(".sha256")
    try:
        data = path.read_bytes()
        fields = digest_path.read_text(encoding="ascii").strip().split()
    except (OSError, UnicodeError) as exc:
        raise EndToEndContractError("durable artifact is unavailable") from exc
    if len(fields) != 2 or fields[1] != path.name:
        raise EndToEndContractError("durable artifact digest record is invalid")
    if re.fullmatch(_DIGEST_PATTERN, fields[0]) is None:
        raise EndToEndContractError("durable artifact digest is invalid")
    digest = _sha256(data)
    if digest != fields[0]:
        raise EndToEndContractError("durable artifact digest mismatch")
    return data, digest


def _read_model_artifact(
    path: Path,
    model_type: type[ModelT],
    canonicalizer: Callable[[ModelT], bytes],
) -> tuple[ModelT, str]:
    data, digest = _read_immutable_artifact(path)
    try:
        model = cast(ModelT, model_type.model_validate(json.loads(data)))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise EndToEndContractError("durable parent artifact is invalid") from exc
    if canonicalizer(model) != data:
        raise EndToEndContractError("durable parent artifact is not canonical")
    if _sha256(data) != digest:
        raise EndToEndContractError("durable parent artifact identity mismatch")
    return model, digest


def _read_parser_lineage(execution_dir: Path) -> tuple[
    ParserLaneResultArtifact,
    ParserLaneAttemptArtifact,
    NormalizedDocument,
    str,
    str,
]:
    result, result_digest = _read_model_artifact(
        execution_dir / "result.json",
        ParserLaneResultArtifact,
        canonical_parser_lane_artifact_bytes,
    )
    attempt, _ = _read_model_artifact(
        execution_dir / "attempt.json",
        ParserLaneAttemptArtifact,
        canonical_parser_lane_artifact_bytes,
    )
    candidate_bytes, candidate_digest = _read_immutable_artifact(
        execution_dir / "candidate.json"
    )
    try:
        candidate = NormalizedDocument.model_validate(json.loads(candidate_bytes))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise EndToEndContractError("Parser output is invalid") from exc
    if canonical_normalized_document_bytes(candidate) != candidate_bytes:
        raise EndToEndContractError("Parser output is not canonical")
    if result.candidate_sha256 != candidate_digest:
        raise EndToEndContractError("Parser result/output digest mismatch")
    if attempt.candidate_sha256 != candidate_digest or attempt.result_sha256 != result_digest:
        raise EndToEndContractError("Parser attempt lineage mismatch")
    if result.case_id != attempt.case_id or result.source_sha256 != attempt.source_sha256:
        raise EndToEndContractError("Parser result/attempt identity mismatch")
    if normalized_document_sha256(candidate) != candidate_digest:
        raise EndToEndContractError("Parser output digest mismatch")
    return result, attempt, candidate, result_digest, candidate_digest


def _read_generation_lineage(
    execution_dir: Path,
) -> tuple[
    GenerationResultArtifact,
    GenerationAttemptArtifact,
    BenchmarkNoteDocument,
    str,
    str,
]:
    result, result_digest = _read_model_artifact(
        execution_dir / "result.json",
        GenerationResultArtifact,
        canonical_generation_lane_artifact_bytes,
    )
    attempt, _ = _read_model_artifact(
        execution_dir / "attempt.json",
        GenerationAttemptArtifact,
        canonical_generation_lane_artifact_bytes,
    )
    candidate_bytes, candidate_digest = _read_immutable_artifact(
        execution_dir / "candidate.json"
    )
    try:
        candidate = BenchmarkNoteDocument.model_validate(json.loads(candidate_bytes))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise EndToEndContractError("Generation pre-render note is invalid") from exc
    if canonical_benchmark_note_bytes(candidate) != candidate_bytes:
        raise EndToEndContractError("Generation pre-render note is not canonical")
    if result.candidate_sha256 != candidate_digest:
        raise EndToEndContractError("Generation result/output digest mismatch")
    if attempt.candidate_sha256 != candidate_digest or attempt.result_sha256 != result_digest:
        raise EndToEndContractError("Generation attempt lineage mismatch")
    if result.case_id != attempt.case_id:
        raise EndToEndContractError("Generation result/attempt identity mismatch")
    return result, attempt, candidate, result_digest, candidate_digest


def _load_reference(case: Any, benchmark_root: Path) -> tuple[NormalizedDocument, str]:
    path = benchmark_root / case.reference_path
    try:
        data = path.read_bytes()
        digest_record = (benchmark_root / case.reference_digest_path).read_text(
            encoding="ascii"
        ).strip().split()
    except (OSError, UnicodeError) as exc:
        raise EndToEndOperationalError("reference artifact is unavailable") from exc
    if len(digest_record) != 2 or digest_record[1] != path.name:
        raise EndToEndContractError("reference digest record is invalid")
    digest = _sha256(data)
    if digest != digest_record[0] or digest != case.reference_sha256:
        raise EndToEndContractError("reference digest mismatch")
    try:
        document = NormalizedDocument.model_validate(json.loads(data))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise EndToEndContractError("reference artifact is invalid") from exc
    if canonical_normalized_document_bytes(document) != data:
        raise EndToEndContractError("reference artifact is not canonical")
    return document, digest


_SHARED_RESULT_FIELDS = (
    "runner_version",
    "operation",
    "case_id",
    "raw_source_sha256",
    "parser_result_sha256",
    "parser_attempt_sha256",
    "parser_output_sha256",
    "generation_result_sha256",
    "generation_attempt_sha256",
    "generation_output_sha256",
    "pre_render_note_sha256",
    "renderer_output_sha256",
    "renderer_capture_sha256",
    "rendered_note_projection_sha256",
    "execution_contract_sha256",
    "execution_identity",
    "attempt_id",
    "status",
)


def validate_end_to_end_result(
    result: EndToEndResultArtifact,
    *,
    raw_source_sha256: str,
    parser_result: ParserLaneResultArtifact,
    parser_attempt: ParserLaneAttemptArtifact,
    parser_output: NormalizedDocument,
    parser_result_sha256: str,
    parser_attempt_sha256: str,
    generation_result: GenerationResultArtifact,
    generation_attempt: GenerationAttemptArtifact,
    generation_output: BenchmarkNoteDocument,
    generation_result_sha256: str,
    generation_attempt_sha256: str,
    reference_document: NormalizedDocument,
    renderer_output: bytes,
    renderer_capture: RendererCaptureArtifact,
    rendered_projection: RenderedNoteProjection,
    execution_identity: EndToEndExecutionIdentity,
) -> EndToEndResultArtifact:
    parser_output_sha256 = normalized_document_sha256(parser_output)
    generation_output_sha256 = benchmark_note_sha256(generation_output)
    pre_render_note_sha256 = generation_output_sha256
    renderer_output_sha256 = _sha256(renderer_output)
    capture_digest = renderer_capture_sha256(renderer_capture)
    projection_digest = benchmark_note_sha256(rendered_projection)
    if result.raw_source_sha256 != raw_source_sha256:
        raise EndToEndContractError("E2E raw source binding mismatch")
    if result.parser_result_sha256 != parser_result_sha256:
        raise EndToEndContractError("E2E Parser result binding mismatch")
    if result.parser_attempt_sha256 != parser_attempt_sha256:
        raise EndToEndContractError("E2E Parser attempt binding mismatch")
    if result.parser_output_sha256 != parser_output_sha256:
        raise EndToEndContractError("E2E Parser output binding mismatch")
    if result.generation_result_sha256 != generation_result_sha256:
        raise EndToEndContractError("E2E Generation result binding mismatch")
    if result.generation_attempt_sha256 != generation_attempt_sha256:
        raise EndToEndContractError("E2E Generation attempt binding mismatch")
    if result.generation_output_sha256 != generation_output_sha256:
        raise EndToEndContractError("E2E Generation output binding mismatch")
    if result.pre_render_note_sha256 != pre_render_note_sha256:
        raise EndToEndContractError("E2E pre-render binding mismatch")
    if result.renderer_output_sha256 != renderer_output_sha256:
        raise EndToEndContractError("E2E renderer output binding mismatch")
    if result.renderer_capture_sha256 != capture_digest:
        raise EndToEndContractError("E2E renderer capture binding mismatch")
    if result.rendered_note_projection_sha256 != projection_digest:
        raise EndToEndContractError("E2E projection binding mismatch")
    if result.execution_identity != execution_identity:
        raise EndToEndContractError("E2E execution identity mismatch")
    if result.case_id != parser_result.case_id or result.case_id != generation_result.case_id:
        raise EndToEndContractError("E2E case identity mismatch")
    if parser_result.source_sha256 != raw_source_sha256:
        raise EndToEndContractError("Parser raw source binding mismatch")
    if parser_result.candidate_sha256 != parser_output_sha256:
        raise EndToEndContractError("Parser output artifact mismatch")
    if parser_attempt.result_sha256 != parser_result_sha256:
        raise EndToEndContractError("Parser attempt result mismatch")
    if generation_result.candidate_sha256 != pre_render_note_sha256:
        raise EndToEndContractError("Generation pre-render artifact mismatch")
    if generation_attempt.result_sha256 != generation_result_sha256:
        raise EndToEndContractError("Generation attempt result mismatch")
    if generation_result.execution_contract_sha256 != result.execution_contract_sha256:
        raise EndToEndContractError("E2E execution contract mismatch")
    if result.generation_output_sha256 != result.pre_render_note_sha256:
        raise EndToEndContractError("Generation output/pre-render binding mismatch")
    validate_benchmark_note_artifact(
        generation_output,
        reference_document,
    )
    validate_renderer_capture(
        renderer_capture,
        note=generation_output,
        pre_render_note_sha256=pre_render_note_sha256,
        renderer_output=renderer_output,
    )
    validate_benchmark_note_artifact(
        rendered_projection,
        reference_document,
        parent_artifact=generation_output,
    )
    if rendered_projection.lineage.parent_artifact_sha256 != pre_render_note_sha256:
        raise EndToEndContractError("E2E projection parent mismatch")
    if rendered_projection.producer_provenance != renderer_capture.producer_provenance:
        raise EndToEndContractError("E2E renderer provenance mismatch")
    return result


def validate_end_to_end_attempt(
    attempt: EndToEndAttemptArtifact,
    *,
    result: EndToEndResultArtifact,
    result_sha256: str,
    **lineage: Any,
) -> EndToEndAttemptArtifact:
    if attempt.result_sha256 != result_sha256:
        raise EndToEndContractError("E2E attempt/result digest mismatch")
    result_payload = result.model_dump(mode="json")
    attempt_payload = attempt.model_dump(mode="json")
    if any(result_payload[field] != attempt_payload[field] for field in _SHARED_RESULT_FIELDS):
        raise EndToEndContractError("E2E attempt lineage fields mismatch")
    validate_end_to_end_result(result, **lineage)
    return attempt


def execute_end_to_end_case(
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
) -> EndToEndOutcome:
    """Run Parser, Generation, deterministic renderer, and Q24 artifacts."""

    try:
        reference_document, _reference_digest = _load_reference(case, benchmark_root)
        parser_outcome: ParserLaneOutcome = execute_parser_case(
            case,
            benchmark_root,
            output_dir / "parser",
            attempt_id=f"{attempt_id}-parser",
        )
        if parser_outcome.exit_code != 0:
            return EndToEndOutcome(
                parser_outcome.exit_code,
                parser_outcome.status,
                error=parser_outcome.error,
            )
        parser_result, parser_attempt, parser_output, parser_result_digest, parser_output_digest = (
            _read_parser_lineage(output_dir / "parser")
        )

        slot_root = output_dir.parent.parent
        generation_outcome: GenerationLaneOutcome = execute_generation_case(
            case,
            benchmark_root,
            output_dir / "generation",
            attempt_id=f"{attempt_id}-generation",
            attempt_ordinal=attempt_ordinal,
            runner_plan_sha256=runner_plan_sha256,
            runner_slot_id=runner_slot_id,
            runner_attempt_ordinal=runner_attempt_ordinal,
            runner_invocation_id=runner_invocation_id,
            logical_run_id=logical_run_id,
            attempt_root=slot_root,
        )
        if generation_outcome.exit_code != 0:
            return EndToEndOutcome(
                generation_outcome.exit_code,
                generation_outcome.status,
                parser_result_digest=parser_result_digest,
                error=generation_outcome.error,
            )
        (
            generation_result,
            generation_attempt,
            generation_output,
            generation_result_digest,
            generation_output_digest,
        ) = _read_generation_lineage(output_dir / "generation")
        if generation_output_digest != generation_result.candidate_sha256:
            raise EndToEndContractError("Generation candidate digest mismatch")
        validate_benchmark_note_artifact(generation_output, reference_document)

        parser_attempt_digest = parser_outcome.attempt_digest
        generation_attempt_digest = generation_outcome.attempt_digest
        execution_contract_digest = generation_result.execution_contract_sha256
        if parser_attempt_digest is None:
            raise EndToEndContractError("Parser attempt digest is missing")
        if generation_attempt_digest is None:
            raise EndToEndContractError("Generation attempt digest is missing")
        if execution_contract_digest is None:
            raise EndToEndContractError("Generation execution contract digest is missing")

        pre_render_digest = benchmark_note_sha256(generation_output)
        renderer_output = render_pre_render_note_to_html(generation_output)
        renderer_output_digest = _write_immutable_artifact(
            output_dir / "renderer-output.html",
            renderer_output,
        )
        capture = build_renderer_capture(
            generation_output,
            pre_render_note_sha256=pre_render_digest,
            renderer_output=renderer_output,
        )
        capture_bytes = canonical_renderer_capture_bytes(capture)
        capture_digest = _write_immutable_artifact(
            output_dir / "renderer-capture.json",
            capture_bytes,
        )
        durable_capture_bytes, durable_capture_digest = _read_immutable_artifact(
            output_dir / "renderer-capture.json"
        )
        if durable_capture_digest != capture_digest:
            raise EndToEndContractError("durable renderer capture identity mismatch")
        try:
            durable_capture = RendererCaptureArtifact.model_validate(
                json.loads(durable_capture_bytes)
            )
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise EndToEndContractError("durable renderer capture is invalid") from exc
        if canonical_renderer_capture_bytes(durable_capture) != durable_capture_bytes:
            raise EndToEndContractError("durable renderer capture is not canonical")
        durable_renderer_output, durable_renderer_digest = _read_immutable_artifact(
            output_dir / "renderer-output.html"
        )
        if durable_renderer_digest != renderer_output_digest:
            raise EndToEndContractError("durable renderer output identity mismatch")
        validate_renderer_capture(
            durable_capture,
            note=generation_output,
            pre_render_note_sha256=pre_render_digest,
            renderer_output=durable_renderer_output,
        )
        projection = parse_rendered_note_projection(
            durable_renderer_output,
            pre_render_note=generation_output,
            reference_document=reference_document,
            pre_render_note_sha256=pre_render_digest,
        )
        projection_bytes = canonical_benchmark_note_bytes(projection)
        projection_digest = _write_immutable_artifact(
            output_dir / "rendered-note-projection.json",
            projection_bytes,
        )
        execution_identity = EndToEndExecutionIdentity(
            runner_plan_sha256=runner_plan_sha256,
            runner_slot_id=runner_slot_id,
            runner_attempt_ordinal=runner_attempt_ordinal,
            runner_invocation_id=runner_invocation_id,
            logical_run_id=logical_run_id,
            membership="diagnostic",
        )
        result = EndToEndResultArtifact(
            schema_version="benchmark-end-to-end-result/1.0.0",
            runner_version="parser-note-completeness-runner/1.0.0",
            artifact_type="parser_note_completeness_end_to_end_result",
            operation="execute_end_to_end",
            case_id=case.case_id,
            raw_source_sha256=case.source_sha256,
            parser_result_sha256=parser_result_digest,
            parser_attempt_sha256=parser_attempt_digest,
            parser_output_sha256=parser_output_digest,
            generation_result_sha256=generation_result_digest,
            generation_attempt_sha256=generation_attempt_digest,
            generation_output_sha256=generation_output_digest,
            pre_render_note_sha256=pre_render_digest,
            renderer_output_sha256=renderer_output_digest,
            renderer_capture_sha256=durable_capture_digest,
            rendered_note_projection_sha256=projection_digest,
            execution_contract_sha256=execution_contract_digest,
            execution_identity=execution_identity,
            attempt_id=attempt_id,
            status="contract_valid",
        )
        validate_end_to_end_result(
            result,
            raw_source_sha256=case.source_sha256,
            parser_result=parser_result,
            parser_attempt=parser_attempt,
            parser_output=parser_output,
            parser_result_sha256=parser_result_digest,
            parser_attempt_sha256=parser_attempt_digest,
            generation_result=generation_result,
            generation_attempt=generation_attempt,
            generation_output=generation_output,
            generation_result_sha256=generation_result_digest,
            generation_attempt_sha256=generation_attempt_digest,
            reference_document=reference_document,
            renderer_output=durable_renderer_output,
            renderer_capture=durable_capture,
            rendered_projection=projection,
            execution_identity=execution_identity,
        )
        result_bytes = canonical_end_to_end_artifact_bytes(result)
        result_digest = _write_immutable_artifact(output_dir / "result.json", result_bytes)
        attempt = EndToEndAttemptArtifact(
            schema_version="benchmark-end-to-end-attempt/1.0.0",
            runner_version="parser-note-completeness-runner/1.0.0",
            artifact_type="parser_note_completeness_end_to_end_attempt",
            operation="execute_end_to_end",
            case_id=result.case_id,
            raw_source_sha256=result.raw_source_sha256,
            parser_result_sha256=result.parser_result_sha256,
            parser_attempt_sha256=result.parser_attempt_sha256,
            parser_output_sha256=result.parser_output_sha256,
            generation_result_sha256=result.generation_result_sha256,
            generation_attempt_sha256=result.generation_attempt_sha256,
            generation_output_sha256=result.generation_output_sha256,
            pre_render_note_sha256=result.pre_render_note_sha256,
            renderer_output_sha256=result.renderer_output_sha256,
            renderer_capture_sha256=result.renderer_capture_sha256,
            rendered_note_projection_sha256=result.rendered_note_projection_sha256,
            execution_contract_sha256=result.execution_contract_sha256,
            execution_identity=result.execution_identity,
            attempt_id=result.attempt_id,
            result_sha256=result_digest,
            status="contract_valid",
        )
        validate_end_to_end_attempt(
            attempt,
            result=result,
            result_sha256=result_digest,
            raw_source_sha256=case.source_sha256,
            parser_result=parser_result,
            parser_attempt=parser_attempt,
            parser_output=parser_output,
            parser_result_sha256=parser_result_digest,
            parser_attempt_sha256=parser_attempt_digest,
            generation_result=generation_result,
            generation_attempt=generation_attempt,
            generation_output=generation_output,
            generation_result_sha256=generation_result_digest,
            generation_attempt_sha256=generation_attempt_digest,
            reference_document=reference_document,
            renderer_output=durable_renderer_output,
            renderer_capture=durable_capture,
            rendered_projection=projection,
            execution_identity=execution_identity,
        )
        attempt_digest = _write_immutable_artifact(
            output_dir / "attempt.json",
            canonical_end_to_end_artifact_bytes(attempt),
        )
        return EndToEndOutcome(
            0,
            "contract_valid",
            result_digest=result_digest,
            attempt_digest=attempt_digest,
            parser_result_digest=parser_result_digest,
            generation_result_digest=generation_result_digest,
            renderer_output_digest=renderer_output_digest,
            renderer_capture_digest=capture_digest,
            rendered_projection_digest=projection_digest,
        )
    except (EndToEndContractError, RendererContractError, ValueError) as exc:
        return EndToEndOutcome(2, "invalid_input", error=str(exc))
    except (EndToEndOperationalError, RendererOperationalError, OSError) as exc:
        return EndToEndOutcome(1, "operational_failure", error=str(exc))


__all__ = [
    "END_TO_END_ATTEMPT_ARTIFACT_TYPE",
    "END_TO_END_ATTEMPT_SCHEMA_VERSION",
    "END_TO_END_OPERATION",
    "END_TO_END_RESULT_ARTIFACT_TYPE",
    "END_TO_END_RESULT_SCHEMA_VERSION",
    "EndToEndArtifact",
    "EndToEndAttemptArtifact",
    "EndToEndContractError",
    "EndToEndExecutionIdentity",
    "EndToEndOperationalError",
    "EndToEndOutcome",
    "EndToEndResultArtifact",
    "canonical_end_to_end_artifact_bytes",
    "end_to_end_artifact_sha256",
    "execute_end_to_end_case",
    "validate_end_to_end_attempt",
    "validate_end_to_end_result",
]
