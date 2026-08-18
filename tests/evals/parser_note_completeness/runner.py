"""Versioned local validation runner for parser-note completeness artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, Literal, Mapping, NoReturn, Optional, Sequence, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, ValidationError

from .diagnostic import write_diagnostic_run_plan
from .normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)
from .run_plan import (
    COLLECTION_SCHEMA_VERSION,
    START_RECEIPT_SCHEMA_VERSION,
    TERMINAL_RECEIPT_SCHEMA_VERSION,
    CollectionRevision,
    CollectionSlot,
    NetworkDenialAttestation,
    RunPlan,
    RunSlot,
    StartReceipt,
    TerminalReceipt,
    artifact_sha256,
    canonical_attestation_bytes,
    canonical_collection_bytes,
    canonical_receipt_bytes,
    canonical_run_plan_bytes,
    invocation_sha256,
)
from .scorer import QualityFailure, Scorer

RUNNER_VERSION = "parser-note-completeness-runner/1.0.0"
RESULT_SCHEMA_VERSION = "runner-result/1.0.0"
ATTEMPT_SCHEMA_VERSION = "runner-attempt/1.0.0"
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_ATTEMPT_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
_Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]
_AttemptId = Annotated[StrictStr, Field(pattern=_ATTEMPT_ID_PATTERN)]


class RunnerResultArtifact(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )

    schema_version: Literal["runner-result/1.0.0"]
    runner_version: Literal["parser-note-completeness-runner/1.0.0"]
    artifact_type: Literal["parser_note_completeness_runner_result"]
    operation: Literal["validate_reference"]
    reference_sha256: _Digest
    reference_bytes: Annotated[StrictInt, Field(ge=0)]
    attempt_id: _AttemptId
    status: Literal["contract_valid"]
    scorer_observation: Literal["not_run", "completed", "quality_failure"]


class RunnerAttemptArtifact(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )

    schema_version: Literal["runner-attempt/1.0.0"]
    runner_version: Literal["parser-note-completeness-runner/1.0.0"]
    artifact_type: Literal["parser_note_completeness_runner_attempt"]
    operation: Literal["validate_reference"]
    reference_sha256: _Digest
    result_sha256: _Digest
    attempt_id: _AttemptId
    status: Literal["contract_valid"]
    scorer_observation: Literal["not_run", "completed", "quality_failure"]


RunnerArtifact = Union[RunnerResultArtifact, RunnerAttemptArtifact]


class _OperationalFailure(Exception):
    """Input/output or incomplete-work failure, mapped to exit code 1."""


class _InvalidInput(Exception):
    """Digest, JSON, schema, or canonical-contract failure, mapped to 2."""


class _ArgumentFailure(Exception):
    """Argument parsing failure, mapped to one JSON exit-2 status."""


@dataclass(frozen=True)
class RunnerOutcome:
    exit_code: int
    status: str
    plan_digest: Optional[str] = None
    result_digest: Optional[str] = None
    attempt_digest: Optional[str] = None
    collection_digest: Optional[str] = None
    invocation_id: Optional[str] = None
    error: Optional[str] = None

    def as_status(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "exit_code": self.exit_code,
            "status": self.status,
        }
        if self.plan_digest is not None:
            payload["plan_digest"] = self.plan_digest
        if self.result_digest is not None:
            payload["result_digest"] = self.result_digest
        if self.attempt_digest is not None:
            payload["attempt_digest"] = self.attempt_digest
        if self.collection_digest is not None:
            payload["collection_digest"] = self.collection_digest
        if self.invocation_id is not None:
            payload["invocation_id"] = self.invocation_id
        if self.error is not None:
            payload["error"] = self.error
        return payload


def _artifact_model(payload: Union[RunnerArtifact, Mapping[str, Any]]) -> RunnerArtifact:
    if isinstance(payload, (RunnerResultArtifact, RunnerAttemptArtifact)):
        return payload
    if not isinstance(payload, Mapping):
        raise TypeError("runner artifact must be a mapping or validated model")
    artifact_type = payload.get("artifact_type")
    if artifact_type == "parser_note_completeness_runner_result":
        return RunnerResultArtifact.model_validate(payload)
    if artifact_type == "parser_note_completeness_runner_attempt":
        return RunnerAttemptArtifact.model_validate(payload)
    raise ValueError("unknown runner artifact type")


def canonical_runner_artifact_bytes(
    payload: Union[RunnerArtifact, Mapping[str, Any]],
) -> bytes:
    """Validate a runner model before canonical serialization."""

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


def runner_artifact_sha256(
    payload: Union[RunnerArtifact, Mapping[str, Any]],
) -> str:
    return hashlib.sha256(canonical_runner_artifact_bytes(payload)).hexdigest()


def _read_external_digest(path: Path, expected_filename: str) -> str:
    try:
        fields = path.read_text(encoding="utf-8").strip().split()
    except (OSError, UnicodeError) as exc:
        raise _OperationalFailure("digest input unavailable") from exc
    if len(fields) != 2 or fields[1] != expected_filename:
        raise _InvalidInput("invalid external digest record")
    if re.fullmatch(_DIGEST_PATTERN, fields[0]) is None:
        raise _InvalidInput("invalid external digest value")
    return fields[0]


def _read_and_validate_reference(
    reference_path: Path,
    digest_path: Path,
) -> Tuple[NormalizedDocument, str, int]:
    try:
        reference_bytes = reference_path.read_bytes()
    except OSError as exc:
        raise _OperationalFailure("reference input unavailable") from exc

    expected_digest = _read_external_digest(digest_path, reference_path.name)
    actual_digest = hashlib.sha256(reference_bytes).hexdigest()
    if actual_digest != expected_digest:
        raise _InvalidInput("reference digest mismatch")

    try:
        payload = json.loads(reference_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
        raise _InvalidInput("reference JSON is invalid") from exc
    if not isinstance(payload, dict):
        raise _InvalidInput("reference JSON must be an object")

    try:
        document = NormalizedDocument.model_validate(payload)
    except ValidationError as exc:
        raise _InvalidInput("reference schema is invalid") from exc
    if canonical_normalized_document_bytes(document) != reference_bytes:
        raise _InvalidInput("reference JSON is not canonical")
    return document, actual_digest, len(reference_bytes)


def _write_immutable(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(path, flags, 0o644)
    except FileExistsError as exc:
        raise _OperationalFailure("immutable output already exists") from exc
    except OSError as exc:
        raise _OperationalFailure("result output is not writable") from exc
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
    except OSError as exc:
        raise _OperationalFailure("result output write failed") from exc


def _write_outputs(
    output_dir: Path,
    result_bytes: bytes,
    attempt_bytes: bytes,
) -> Tuple[str, str]:
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise _OperationalFailure("result output directory is not writable") from exc

    result_digest = hashlib.sha256(result_bytes).hexdigest()
    attempt_digest = hashlib.sha256(attempt_bytes).hexdigest()
    artifacts = (
        (output_dir / "result.json", result_bytes),
        (
            output_dir / "result.sha256",
            f"{result_digest}  result.json\n".encode("ascii"),
        ),
        (output_dir / "attempt.json", attempt_bytes),
        (
            output_dir / "attempt.sha256",
            f"{attempt_digest}  attempt.json\n".encode("ascii"),
        ),
    )
    if any(path.exists() for path, _ in artifacts):
        raise _OperationalFailure("immutable output already exists")
    for path, data in artifacts:
        _write_immutable(path, data)
    return result_digest, attempt_digest


def validate_reference(
    reference_path: Path,
    digest_path: Path,
    output_dir: Path,
    *,
    attempt_id: str = "attempt-001",
    scorer: Optional[Scorer] = None,
) -> RunnerOutcome:
    """Validate one immutable reference and optionally observe quality."""

    if re.fullmatch(_ATTEMPT_ID_PATTERN, attempt_id) is None:
        return RunnerOutcome(2, "invalid_input", error="invalid attempt id")

    try:
        document, reference_digest, reference_bytes = _read_and_validate_reference(
            reference_path, digest_path
        )
        scorer_observation = "not_run"
        if scorer is not None:
            try:
                scorer.evaluate(document)
            except QualityFailure:
                scorer_observation = "quality_failure"
            except Exception as exc:
                raise _OperationalFailure("scorer execution failed") from exc
            else:
                scorer_observation = "completed"

        result_model = RunnerResultArtifact(
            schema_version=RESULT_SCHEMA_VERSION,
            runner_version=RUNNER_VERSION,
            artifact_type="parser_note_completeness_runner_result",
            operation="validate_reference",
            reference_sha256=reference_digest,
            reference_bytes=reference_bytes,
            attempt_id=attempt_id,
            status="contract_valid",
            scorer_observation=scorer_observation,
        )
        result_bytes = canonical_runner_artifact_bytes(result_model)
        result_digest = hashlib.sha256(result_bytes).hexdigest()
        attempt_model = RunnerAttemptArtifact(
            schema_version=ATTEMPT_SCHEMA_VERSION,
            runner_version=RUNNER_VERSION,
            artifact_type="parser_note_completeness_runner_attempt",
            operation="validate_reference",
            reference_sha256=reference_digest,
            result_sha256=result_digest,
            attempt_id=attempt_id,
            status="contract_valid",
            scorer_observation=scorer_observation,
        )
        attempt_bytes = canonical_runner_artifact_bytes(attempt_model)
        written_result_digest, attempt_digest = _write_outputs(
            output_dir, result_bytes, attempt_bytes
        )
        return RunnerOutcome(
            0,
            "contract_valid",
            result_digest=written_result_digest,
            attempt_digest=attempt_digest,
        )
    except _InvalidInput as exc:
        return RunnerOutcome(2, "invalid_input", error=str(exc))
    except _OperationalFailure as exc:
        return RunnerOutcome(1, "operational_failure", error=str(exc))


_KNOWN_CREDENTIAL_ENV = (
    "NOTION_TOKEN",
    "OPENAI_API_KEY",
    "TELEGRAM_BOT_TOKEN",
)
class _ExternalInterruption(Exception):
    """Testing hook for a process that disappears after its start receipt."""


def _write_external_artifact(path: Path, digest_path: Path, data: bytes, filename: str) -> str:
    digest = artifact_sha256(data)
    _write_immutable(path, data)
    _write_immutable(digest_path, f"{digest}  {filename}\n".encode("ascii"))
    return digest


def _read_canonical_artifact(
    path: Path,
    digest_path: Path,
    expected_filename: str,
    model_loader: Any,
    bytes_encoder: Any,
    invalid_message: str,
    canonical_message: Optional[str] = None,
) -> tuple[Any, str]:
    try:
        data = path.read_bytes()
    except (OSError, UnicodeError) as exc:
        raise _OperationalFailure("artifact input unavailable") from exc
    expected = _read_external_digest(digest_path, expected_filename)
    actual = artifact_sha256(data)
    if actual != expected:
        raise _InvalidInput("artifact digest mismatch")
    try:
        payload = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
        raise _InvalidInput(invalid_message) from exc
    try:
        model = model_loader(payload)
        if bytes_encoder(model) != data:
            raise _InvalidInput(canonical_message or f"{invalid_message} is not canonical")
    except _InvalidInput:
        raise
    except Exception as exc:
        raise _InvalidInput(invalid_message) from exc
    return model, actual


def _read_run_plan(plan_path: Path, digest_path: Path) -> tuple[RunPlan, str]:
    model, digest = _read_canonical_artifact(
        plan_path,
        digest_path,
        plan_path.name,
        lambda payload: RunPlan.model_validate(payload),
        canonical_run_plan_bytes,
        "run plan is invalid",
        "run plan is not canonical",
    )
    try:
        if canonical_run_plan_bytes(model) != plan_path.read_bytes():
            raise _InvalidInput("run plan is not canonical")
    except OSError as exc:
        raise _OperationalFailure("run plan input unavailable") from exc
    return model, digest


def _invocation_digest(
    plan_digest: str,
    invocation_id: str,
    *,
    resume: bool,
    formal: bool,
    attestation_supplied: bool,
) -> str:
    return invocation_sha256(
        {
            "command": "execute-plan",
            "plan_sha256": plan_digest,
            "invocation_id": invocation_id,
            "resume": resume,
            "formal": formal,
            "attestation_supplied": attestation_supplied,
        }
    )


def _preflight_execute(
    *,
    live: bool,
    provider: Optional[str],
) -> None:
    if live or provider is not None:
        raise _InvalidInput("live execution or credentials are not permitted")
    if any(name in os.environ for name in _KNOWN_CREDENTIAL_ENV):
        raise _InvalidInput("live execution or credentials are not permitted")


def _read_attestation(
    path: Optional[Path],
    digest_path: Optional[Path],
    *,
    plan_digest: str,
    invocation_id: str,
    invocation_digest: str,
) -> Literal["attested", "missing"]:
    if path is None and digest_path is None:
        return "missing"
    if path is None or digest_path is None:
        raise _InvalidInput("network attestation inputs are incomplete")
    model, _ = _read_canonical_artifact(
        path,
        digest_path,
        path.name,
        lambda payload: NetworkDenialAttestation.model_validate(payload),
        canonical_attestation_bytes,
        "network attestation is invalid",
        "network attestation is not canonical",
    )
    if (
        model.plan_sha256 != plan_digest
        or model.invocation_id != invocation_id
        or model.invocation_sha256 != invocation_digest
    ):
        raise _InvalidInput("network attestation binding mismatch")
    return "attested"


def _attempt_dir(store: Path, slot_id: str, ordinal: int) -> Path:
    return store / "attempts" / slot_id / f"attempt-{ordinal:04d}"


def _receipt_model(path: Path, digest_path: Path, *, terminal: bool) -> Any:
    model, _ = _read_canonical_artifact(
        path,
        digest_path,
        path.name,
        lambda payload: (
            TerminalReceipt.model_validate(payload)
            if terminal
            else StartReceipt.model_validate(payload)
        ),
        canonical_receipt_bytes,
        "receipt is invalid",
        "receipt is not canonical",
    )
    return model


def _slot_history(
    store: Path,
    slot: RunSlot,
    plan_digest: str,
) -> list[tuple[int, Optional[StartReceipt], Optional[TerminalReceipt]]]:
    root = store / "attempts" / slot.slot_id
    if not root.exists():
        return []
    histories: list[tuple[int, Optional[StartReceipt], Optional[TerminalReceipt]]] = []
    try:
        entries = tuple(root.iterdir())
    except OSError as exc:
        raise _OperationalFailure("attempt history unavailable") from exc
    if any(
        not entry.is_dir() or re.fullmatch(r"attempt-\d{4,}", entry.name) is None
        for entry in entries
    ):
        raise _InvalidInput("attempt history contains unknown entry")
    directories = sorted(entries, key=lambda path: int(path.name.removeprefix("attempt-")))
    actual_ordinals = tuple(int(path.name.removeprefix("attempt-")) for path in directories)
    if actual_ordinals != tuple(range(1, len(directories) + 1)):
        raise _InvalidInput("attempt history ordinals are not contiguous")
    for directory in directories:
        match = re.fullmatch(r"attempt-(\d{4,})", directory.name)
        if match is None or not directory.is_dir():
            continue
        ordinal = int(match.group(1))
        start_path = directory / "start.json"
        start_digest = directory / "start.sha256"
        terminal_path = directory / "terminal.json"
        terminal_digest = directory / "terminal.sha256"
        try:
            attempt_entries = {entry.name for entry in directory.iterdir()}
        except OSError as exc:
            raise _OperationalFailure("attempt history unavailable") from exc
        if not attempt_entries.issubset(
            {"start.json", "start.sha256", "terminal.json", "terminal.sha256", "execution"}
        ):
            raise _InvalidInput("attempt entry contains unknown artifact")
        execution_path = directory / "execution"
        if execution_path.exists() and not execution_path.is_dir():
            raise _InvalidInput("attempt execution entry is malformed")
        if execution_path.is_dir():
            try:
                execution_entries = {entry.name for entry in execution_path.iterdir()}
            except OSError as exc:
                raise _OperationalFailure("attempt history unavailable") from exc
            if not execution_entries.issubset(
                {"result.json", "result.sha256", "attempt.json", "attempt.sha256"}
            ):
                raise _InvalidInput("attempt execution contains unknown artifact")
        if not start_path.exists() or not start_digest.exists():
            raise _InvalidInput("attempt history is incomplete")
        start = _receipt_model(start_path, start_digest, terminal=False)
        if (
            start.plan_sha256 != plan_digest
            or start.slot_id != slot.slot_id
            or start.case_id != slot.case_id
            or start.reference_sha256 != slot.reference_sha256
            or start.attempt_ordinal != ordinal
        ):
            raise _InvalidInput("attempt history binding mismatch")
        terminal = None
        if terminal_path.exists() or terminal_digest.exists():
            if not terminal_path.exists() or not terminal_digest.exists():
                raise _InvalidInput("attempt history is incomplete")
            terminal = _receipt_model(terminal_path, terminal_digest, terminal=True)
            if (
                terminal.slot_id != start.slot_id
                or terminal.case_id != start.case_id
                or terminal.reference_sha256 != start.reference_sha256
                or terminal.attempt_ordinal != start.attempt_ordinal
                or terminal.plan_sha256 != start.plan_sha256
                or terminal.invocation_id != start.invocation_id
                or terminal.invocation_sha256 != start.invocation_sha256
            ):
                raise _InvalidInput("attempt history binding mismatch")
        histories.append((ordinal, start, terminal))
    for _, _, terminal in histories[:-1]:
        if terminal is not None and terminal.terminal_status in {"contract_valid", "invalid_input"}:
            raise _InvalidInput("attempt history continues after a closed slot")
    return histories


def _collection_state(
    histories: list[tuple[int, Optional[StartReceipt], Optional[TerminalReceipt]]],
) -> tuple[str, tuple[int, ...]]:
    ordinals = tuple(item[0] for item in histories)
    if not histories:
        return "missing", ordinals
    _, _, terminal = histories[-1]
    if terminal is None:
        return "unclosed", ordinals
    if terminal.terminal_status == "contract_valid":
        return "closed", ordinals
    if terminal.terminal_status == "invalid_input":
        return "invalid", ordinals
    return "operational", ordinals


def _next_revision_ordinal(store: Path) -> int:
    root = store / "collections"
    values = []
    if root.exists():
        for path in root.glob("revision-*.json"):
            match = re.fullmatch(r"revision-(\d{4,})\.json", path.name)
            if match is not None:
                values.append(int(match.group(1)))
    return max(values, default=0) + 1


def _invocation_exists(store: Path, invocation_id: str, invocation_digest: str) -> bool:
    candidates: list[Path] = []
    collections_root = store / "collections"
    attempts_root = store / "attempts"
    if collections_root.exists():
        candidates.extend(collections_root.glob("revision-*.json"))
    if attempts_root.exists():
        candidates.extend(attempts_root.glob("*/attempt-*/start.json"))
        candidates.extend(attempts_root.glob("*/attempt-*/terminal.json"))
    for path in candidates:
        try:
            payload = json.loads(path.read_bytes())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if (
            isinstance(payload, dict)
            and payload.get("invocation_id") == invocation_id
        ):
            return True
    return False


def _collection_invocation_exists(store: Path, invocation_id: str, invocation_digest: str) -> bool:
    root = store / "collections"
    if not root.exists():
        return False
    for path in root.glob("revision-*.json"):
        try:
            payload = json.loads(path.read_bytes())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if (
            isinstance(payload, dict)
            and payload.get("invocation_id") == invocation_id
        ):
            return True
    return False


def _validate_attempt_roots(store: Path, plan: RunPlan) -> None:
    root = store / "attempts"
    if not root.exists():
        return
    expected = {slot.slot_id for slot in plan.slots}
    try:
        entries = tuple(root.iterdir())
    except OSError as exc:
        raise _OperationalFailure("attempt history unavailable") from exc
    if any(not entry.is_dir() or entry.name not in expected for entry in entries):
        raise _InvalidInput("attempt history contains unknown slot entry")


def collect_collection(
    plan: RunPlan,
    plan_digest: str,
    invocation_id: str,
    invocation_digest: str,
    store: Path,
    *,
    offline_attestation: Literal["attested", "missing"],
) -> tuple[CollectionRevision, str]:
    if _collection_invocation_exists(store, invocation_id, invocation_digest):
        raise _InvalidInput("invocation already exists")
    _validate_attempt_roots(store, plan)
    collection_slots = []
    for slot in plan.slots:
        state, ordinals = _collection_state(_slot_history(store, slot, plan_digest))
        collection_slots.append(
            CollectionSlot(
                slot_id=slot.slot_id,
                case_id=slot.case_id,
                attempt_ordinals=ordinals,
                state=state,
            )
        )
    revision = CollectionRevision(
        schema_version=COLLECTION_SCHEMA_VERSION,
        runner_version=RUNNER_VERSION,
        artifact_type="development_collection_revision",
        operation="execute_plan",
        plan_sha256=plan_digest,
        invocation_id=invocation_id,
        invocation_sha256=invocation_digest,
        revision_ordinal=_next_revision_ordinal(store),
        membership="diagnostic",
        offline_attestation=offline_attestation,
        slots=tuple(collection_slots),
    )
    data = canonical_collection_bytes(revision)
    path = store / "collections" / f"revision-{revision.revision_ordinal:04d}.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise _OperationalFailure("collection output directory is not writable") from exc
    digest = _write_external_artifact(
        path,
        path.with_suffix(".sha256"),
        data,
        path.name,
    )
    return revision, digest


def _write_start_receipt(
    attempt_dir: Path,
    *,
    plan_digest: str,
    invocation_id: str,
    invocation_digest: str,
    slot: RunSlot,
    ordinal: int,
    offline_attestation: Literal["attested", "missing"],
) -> StartReceipt:
    receipt = StartReceipt(
        schema_version=START_RECEIPT_SCHEMA_VERSION,
        runner_version=RUNNER_VERSION,
        artifact_type="runner_start_receipt",
        operation="validate_reference",
        plan_sha256=plan_digest,
        invocation_id=invocation_id,
        reference_sha256=slot.reference_sha256,
        invocation_sha256=invocation_digest,
        slot_id=slot.slot_id,
        case_id=slot.case_id,
        attempt_ordinal=ordinal,
        membership="diagnostic",
        offline_attestation=offline_attestation,
        status="started",
    )
    data = canonical_receipt_bytes(receipt)
    attempt_dir.mkdir(parents=True, exist_ok=False)
    _write_external_artifact(
        attempt_dir / "start.json",
        attempt_dir / "start.sha256",
        data,
        "start.json",
    )
    return receipt


def _write_terminal_receipt(
    attempt_dir: Path,
    *,
    plan_digest: str,
    invocation_id: str,
    invocation_digest: str,
    slot: RunSlot,
    ordinal: int,
    offline_attestation: Literal["attested", "missing"],
    outcome: RunnerOutcome,
) -> TerminalReceipt:
    if outcome.exit_code == 0:
        terminal_status = "contract_valid"
    elif outcome.exit_code == 2:
        terminal_status = "invalid_input"
    else:
        terminal_status = "operational_failure"
    receipt = TerminalReceipt(
        schema_version=TERMINAL_RECEIPT_SCHEMA_VERSION,
        runner_version=RUNNER_VERSION,
        artifact_type="runner_terminal_receipt",
        operation="validate_reference",
        plan_sha256=plan_digest,
        invocation_id=invocation_id,
        reference_sha256=slot.reference_sha256,
        invocation_sha256=invocation_digest,
        slot_id=slot.slot_id,
        case_id=slot.case_id,
        attempt_ordinal=ordinal,
        membership="diagnostic",
        offline_attestation=offline_attestation,
        exit_code=outcome.exit_code,
        terminal_status=terminal_status,
        result_sha256=outcome.result_digest,
    )
    data = canonical_receipt_bytes(receipt)
    _write_external_artifact(
        attempt_dir / "terminal.json",
        attempt_dir / "terminal.sha256",
        data,
        "terminal.json",
    )
    return receipt


def _resolve_bounded_execution_path(
    benchmark_root: Path,
    relative_path: str,
    label: str,
) -> Path:
    """Resolve a plan artifact without allowing symlink escape from its root."""

    try:
        root = benchmark_root.resolve(strict=True)
        target = (root / relative_path).resolve(strict=False)
        target.relative_to(root)
    except (OSError, ValueError) as exc:
        raise _InvalidInput(f"{label} is outside the benchmark root") from exc
    return target


def execute_plan(
    plan_path: Path,
    plan_digest_path: Path,
    store: Path,
    *,
    invocation_id: str,
    resume: bool = False,
    attestation_path: Optional[Path] = None,
    attestation_digest_path: Optional[Path] = None,
    live: bool = False,
    provider: Optional[str] = None,
    formal: bool = False,
    interrupt_after_start_slot: Optional[str] = None,
    benchmark_root: Optional[Path] = None,
) -> RunnerOutcome:
    """Execute only diagnostic development slots and append immutable history."""

    try:
        if re.fullmatch(_ATTEMPT_ID_PATTERN, invocation_id) is None:
            raise _InvalidInput("invalid invocation id")
        _preflight_execute(
            live=live,
            provider=provider,
        )
        plan, plan_digest = _read_run_plan(plan_path, plan_digest_path)
        if formal or plan.execution_mode != "development":
            raise _InvalidInput("formal execution is unsupported")
        artifact_root = Path(benchmark_root) if benchmark_root is not None else plan_path.parent
        planned_paths = {
            slot.slot_id: (
                _resolve_bounded_execution_path(
                    artifact_root,
                    slot.reference_path,
                    "reference artifact",
                ),
                _resolve_bounded_execution_path(
                    artifact_root,
                    slot.digest_path,
                    "reference digest",
                ),
            )
            for slot in plan.slots
        }
        invocation_digest = _invocation_digest(
            plan_digest,
            invocation_id,
            resume=resume,
            formal=formal,
            attestation_supplied=attestation_path is not None,
        )
        offline_attestation = _read_attestation(
            attestation_path,
            attestation_digest_path,
            plan_digest=plan_digest,
            invocation_id=invocation_id,
            invocation_digest=invocation_digest,
        )
        if _invocation_exists(store, invocation_id, invocation_digest):
            raise _InvalidInput("invocation already exists")
        _validate_attempt_roots(store, plan)

        for slot in plan.slots:
            histories = _slot_history(store, slot, plan_digest)
            state, _ = _collection_state(histories)
            if state in {"closed", "invalid"}:
                continue
            if state in {"operational", "unclosed"} and not resume:
                continue
            ordinal = histories[-1][0] + 1 if histories else 1
            attempt_dir = _attempt_dir(store, slot.slot_id, ordinal)
            _write_start_receipt(
                attempt_dir,
                plan_digest=plan_digest,
                invocation_id=invocation_id,
                invocation_digest=invocation_digest,
                slot=slot,
                ordinal=ordinal,
                offline_attestation=offline_attestation,
            )
            if interrupt_after_start_slot == slot.slot_id:
                raise _ExternalInterruption
            reference_path, digest_path = planned_paths[slot.slot_id]
            attempt_id = f"{slot.slot_id}-attempt-{ordinal:04d}"
            try:
                planned_bytes = reference_path.read_bytes()
            except OSError:
                planned_bytes = None
            if planned_bytes is not None and artifact_sha256(planned_bytes) != slot.reference_sha256:
                outcome = RunnerOutcome(2, "invalid_input", error="planned reference digest mismatch")
            else:
                outcome = validate_reference(
                    reference_path,
                    digest_path,
                    attempt_dir / "execution",
                    attempt_id=attempt_id,
                )
            _write_terminal_receipt(
                attempt_dir,
                plan_digest=plan_digest,
                invocation_id=invocation_id,
                invocation_digest=invocation_digest,
                slot=slot,
                ordinal=ordinal,
                offline_attestation=offline_attestation,
                outcome=outcome,
            )

        revision, collection_digest = collect_collection(
            plan,
            plan_digest,
            invocation_id,
            invocation_digest,
            store,
            offline_attestation=offline_attestation,
        )
        states = {slot.state for slot in revision.slots}
        if "invalid" in states:
            return RunnerOutcome(
                2,
                "invalid_input",
                collection_digest=collection_digest,
                invocation_id=invocation_id,
            )
        if states.intersection({"missing", "operational", "unclosed"}):
            return RunnerOutcome(
                1,
                "collection_incomplete",
                collection_digest=collection_digest,
                invocation_id=invocation_id,
            )
        return RunnerOutcome(
            0,
            "collection_complete",
            collection_digest=collection_digest,
            invocation_id=invocation_id,
        )
    except _ExternalInterruption:
        try:
            plan, plan_digest = _read_run_plan(plan_path, plan_digest_path)
            invocation_digest = _invocation_digest(
                plan_digest,
                invocation_id,
                resume=resume,
                formal=formal,
                attestation_supplied=attestation_path is not None,
            )
            offline_attestation = "attested" if attestation_path is not None else "missing"
            _, collection_digest = collect_collection(
                plan,
                plan_digest,
                invocation_id,
                invocation_digest,
                store,
                offline_attestation=offline_attestation,
            )
            return RunnerOutcome(
                1,
                "operational_failure",
                collection_digest=collection_digest,
                invocation_id=invocation_id,
                error="attempt interrupted before terminal receipt",
            )
        except Exception:
            return RunnerOutcome(1, "operational_failure", error="runner execution failed")
    except _InvalidInput as exc:
        return RunnerOutcome(2, "invalid_input", error=str(exc))
    except _OperationalFailure as exc:
        return RunnerOutcome(1, "operational_failure", error=str(exc))


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise _ArgumentFailure from None


def _build_parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(prog="parser-note-completeness-runner")
    parser.add_argument("--version", action="version", version=RUNNER_VERSION)
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        parser_class=_ArgumentParser,
    )
    validate = subparsers.add_parser("validate-reference")
    validate.add_argument("--reference", required=True, type=Path)
    validate.add_argument("--digest", required=True, type=Path)
    validate.add_argument("--output-dir", required=True, type=Path)
    validate.add_argument("--attempt-id", default="attempt-001")
    materialize = subparsers.add_parser("materialize-plan")
    materialize.add_argument("--profile", required=True, type=Path)
    materialize.add_argument("--profile-digest", required=True, type=Path)
    materialize.add_argument("--benchmark-root", required=True, type=Path)
    materialize.add_argument("--output-dir", required=True, type=Path)
    execute = subparsers.add_parser("execute-plan")
    execute.add_argument("--plan", required=True, type=Path)
    execute.add_argument("--plan-digest", required=True, type=Path)
    execute.add_argument("--store", required=True, type=Path)
    execute.add_argument("--benchmark-root", type=Path)
    execute.add_argument("--resume", action="store_true")
    execute.add_argument("--attestation", type=Path)
    execute.add_argument("--attestation-digest", type=Path)
    execute.add_argument("--live", action="store_true")
    execute.add_argument("--provider")
    execute.add_argument("--invocation-id", required=True)
    execute.add_argument("--formal", action="store_true")
    return parser


def _status_json(outcome: RunnerOutcome) -> str:
    return json.dumps(
        outcome.as_status(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    scorer: Optional[Scorer] = None,
) -> int:
    try:
        args = _build_parser().parse_args(argv)
    except _ArgumentFailure:
        print(_status_json(RunnerOutcome(2, "invalid_input", error="invalid command arguments")))
        return 2

    try:
        if args.command == "validate-reference":
            outcome = validate_reference(
                args.reference,
                args.digest,
                args.output_dir,
                attempt_id=args.attempt_id,
                scorer=scorer,
            )
        elif args.command == "materialize-plan":
            plan_path = args.output_dir / "run_plan.json"
            plan_digest_path = args.output_dir / "run_plan.sha256"
            try:
                _, plan_digest = write_diagnostic_run_plan(
                    args.profile,
                    args.profile_digest,
                    args.benchmark_root,
                    plan_path,
                    plan_digest_path,
                )
            except ValueError as exc:
                outcome = RunnerOutcome(2, "invalid_input", error=str(exc))
            except OSError:
                outcome = RunnerOutcome(1, "operational_failure", error="run plan output failed")
            else:
                outcome = RunnerOutcome(
                    0,
                    "plan_materialized",
                    plan_digest=plan_digest,
                )
        elif args.command == "execute-plan":
            outcome = execute_plan(
                args.plan,
                args.plan_digest,
                args.store,
                invocation_id=args.invocation_id,
                benchmark_root=args.benchmark_root,
                resume=args.resume,
                attestation_path=args.attestation,
                attestation_digest_path=args.attestation_digest,
                live=args.live,
                provider=args.provider,
                formal=args.formal,
            )
        else:
            outcome = RunnerOutcome(2, "invalid_input", error="invalid command arguments")
    except Exception:
        outcome = RunnerOutcome(1, "operational_failure", error="runner execution failed")
    print(_status_json(outcome))
    return outcome.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
