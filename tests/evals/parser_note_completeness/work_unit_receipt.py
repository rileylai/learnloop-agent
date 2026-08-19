"""Q15/Q17 per-work-unit attempt receipt realization.

The receipt is a Q17-owned immutable artifact carrying Q15 attempt and
history identity.  Q28 consumes it only through a durable, content-addressed
reference and never uses the slot-level runner receipts as a substitute.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Annotated, Literal, Mapping, Optional, Sequence, Union

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, model_validator

WORK_UNIT_ATTEMPT_RECEIPT_SCHEMA_VERSION = (
    "benchmark-generation-work-unit-attempt-receipt/1.0.0"
)
WORK_UNIT_ATTEMPT_RECEIPT_RECORD_TYPE = "work_unit_attempt_receipt"
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
_WORK_UNIT_ID_PATTERN = r"^work-unit-[0-9a-f]{64}$"
_HISTORY_ID_PATTERN = r"^work-unit-history-[0-9a-f]{64}$"
_RECORD_ID_PATTERN = r"^work-unit-receipt-[0-9a-f]{64}$"

Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]
Identifier = Annotated[StrictStr, Field(pattern=_IDENTIFIER_PATTERN)]
WorkUnitId = Annotated[StrictStr, Field(pattern=_WORK_UNIT_ID_PATTERN)]
HistoryId = Annotated[StrictStr, Field(pattern=_HISTORY_ID_PATTERN)]
RecordId = Annotated[StrictStr, Field(pattern=_RECORD_ID_PATTERN)]
PositiveOrdinal = Annotated[StrictInt, Field(ge=1)]


class WorkUnitReceiptContractError(ValueError):
    """Raised when a per-work-unit owner receipt is invalid or not durable."""


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class RunnerBinding(_StrictFrozenModel):
    runner_plan_sha256: Digest
    runner_slot_id: Identifier
    runner_attempt_ordinal: PositiveOrdinal
    runner_invocation_id: Identifier


class WorkUnitAttemptReceipt(_StrictFrozenModel):
    schema_version: Literal["benchmark-generation-work-unit-attempt-receipt/1.0.0"]
    artifact_role: Literal["work_unit_attempt_receipt"]
    record_id: RecordId
    receipt_role: Literal["attempt_started", "attempt_terminal"]
    coverage_plan_sha256: Digest
    work_unit_id: WorkUnitId
    attempt_ordinal: PositiveOrdinal
    work_unit_output_sha256: Optional[Digest]
    lifecycle_status: Literal[
        "started",
        "complete",
        "failed",
        "invalid",
        "interrupted",
        "unclosed",
    ]
    membership: Literal["formal_required", "diagnostic"]
    logical_run_id: Identifier
    execution_id: Identifier
    runner_binding: RunnerBinding
    history_id: HistoryId
    previous_receipt_sha256: Optional[Digest]

    @model_validator(mode="after")
    def _validate_lifecycle(self) -> "WorkUnitAttemptReceipt":
        if self.receipt_role == "attempt_started":
            if self.lifecycle_status not in {"started", "unclosed"}:
                raise ValueError("started receipt has an invalid lifecycle status")
            if self.work_unit_output_sha256 is not None:
                raise ValueError("started receipt cannot bind a work-unit output")
        else:
            if self.lifecycle_status not in {
                "complete",
                "failed",
                "invalid",
                "interrupted",
            }:
                raise ValueError("terminal receipt has an invalid lifecycle status")
            if self.work_unit_output_sha256 is None:
                raise ValueError("terminal receipt requires a work-unit output digest")
        if self.attempt_ordinal == 1 and self.receipt_role == "attempt_started":
            if self.previous_receipt_sha256 is not None:
                raise ValueError("first started receipt must have no parent")
        elif self.previous_receipt_sha256 is None:
            raise ValueError("non-first receipt must bind its previous receipt")
        return self


ReceiptInput = Union[WorkUnitAttemptReceipt, Mapping[str, Any]]


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _model(payload: ReceiptInput) -> WorkUnitAttemptReceipt:
    return payload if isinstance(payload, WorkUnitAttemptReceipt) else WorkUnitAttemptReceipt.model_validate(payload)


def canonical_work_unit_attempt_receipt_bytes(payload: ReceiptInput) -> bytes:
    return _canonical_json_bytes(_model(payload).model_dump(mode="json"))


def work_unit_attempt_receipt_sha256(payload: ReceiptInput) -> str:
    return hashlib.sha256(canonical_work_unit_attempt_receipt_bytes(payload)).hexdigest()


def _history_seed_bytes(
    *, coverage_plan_sha256: str, work_unit_id: str, logical_run_id: str
) -> bytes:
    return _canonical_json_bytes(
        {
            "coverage_plan_sha256": coverage_plan_sha256,
            "work_unit_id": work_unit_id,
            "logical_run_id": logical_run_id,
        }
    )


def derive_history_id(
    *, coverage_plan_sha256: str, work_unit_id: str, logical_run_id: str
) -> str:
    return "work-unit-history-" + hashlib.sha256(
        _history_seed_bytes(
            coverage_plan_sha256=coverage_plan_sha256,
            work_unit_id=work_unit_id,
            logical_run_id=logical_run_id,
        )
    ).hexdigest()


def _record_seed_bytes(
    *,
    coverage_plan_sha256: str,
    work_unit_id: str,
    logical_run_id: str,
    attempt_ordinal: int,
    receipt_role: str,
    execution_id: str,
) -> bytes:
    return _canonical_json_bytes(
        {
            "attempt_ordinal": attempt_ordinal,
            "coverage_plan_sha256": coverage_plan_sha256,
            "execution_id": execution_id,
            "logical_run_id": logical_run_id,
            "receipt_role": receipt_role,
            "work_unit_id": work_unit_id,
        }
    )


def derive_record_id(
    *,
    coverage_plan_sha256: str,
    work_unit_id: str,
    logical_run_id: str,
    attempt_ordinal: int,
    receipt_role: str,
    execution_id: str,
) -> str:
    return "work-unit-receipt-" + hashlib.sha256(
        _record_seed_bytes(
            coverage_plan_sha256=coverage_plan_sha256,
            work_unit_id=work_unit_id,
            logical_run_id=logical_run_id,
            attempt_ordinal=attempt_ordinal,
            receipt_role=receipt_role,
            execution_id=execution_id,
        )
    ).hexdigest()


def _validate_derived_identity(receipt: WorkUnitAttemptReceipt) -> None:
    expected_history_id = derive_history_id(
        coverage_plan_sha256=receipt.coverage_plan_sha256,
        work_unit_id=receipt.work_unit_id,
        logical_run_id=receipt.logical_run_id,
    )
    if receipt.history_id != expected_history_id:
        raise WorkUnitReceiptContractError("receipt history identity mismatch")
    expected_record_id = derive_record_id(
        coverage_plan_sha256=receipt.coverage_plan_sha256,
        work_unit_id=receipt.work_unit_id,
        logical_run_id=receipt.logical_run_id,
        attempt_ordinal=receipt.attempt_ordinal,
        receipt_role=receipt.receipt_role,
        execution_id=receipt.execution_id,
    )
    if receipt.record_id != expected_record_id:
        raise WorkUnitReceiptContractError("receipt record identity mismatch")


def build_work_unit_attempt_receipt(
    *,
    receipt_role: Literal["attempt_started", "attempt_terminal"],
    lifecycle_status: Literal[
        "started",
        "complete",
        "failed",
        "invalid",
        "interrupted",
        "unclosed",
    ],
    coverage_plan_sha256: str,
    work_unit_id: str,
    attempt_ordinal: int,
    work_unit_output_sha256: Optional[str],
    membership: Literal["formal_required", "diagnostic"],
    logical_run_id: str,
    execution_id: str,
    runner_plan_sha256: str,
    runner_slot_id: str,
    runner_attempt_ordinal: int,
    runner_invocation_id: str,
    previous_receipt_sha256: Optional[str],
) -> WorkUnitAttemptReceipt:
    history_id = derive_history_id(
        coverage_plan_sha256=coverage_plan_sha256,
        work_unit_id=work_unit_id,
        logical_run_id=logical_run_id,
    )
    record_id = derive_record_id(
        coverage_plan_sha256=coverage_plan_sha256,
        work_unit_id=work_unit_id,
        logical_run_id=logical_run_id,
        attempt_ordinal=attempt_ordinal,
        receipt_role=receipt_role,
        execution_id=execution_id,
    )
    return WorkUnitAttemptReceipt(
        schema_version="benchmark-generation-work-unit-attempt-receipt/1.0.0",
        artifact_role="work_unit_attempt_receipt",
        record_id=record_id,
        receipt_role=receipt_role,
        coverage_plan_sha256=coverage_plan_sha256,
        work_unit_id=work_unit_id,
        attempt_ordinal=attempt_ordinal,
        work_unit_output_sha256=work_unit_output_sha256,
        lifecycle_status=lifecycle_status,
        membership=membership,
        logical_run_id=logical_run_id,
        execution_id=execution_id,
        runner_binding=RunnerBinding(
            runner_plan_sha256=runner_plan_sha256,
            runner_slot_id=runner_slot_id,
            runner_attempt_ordinal=runner_attempt_ordinal,
            runner_invocation_id=runner_invocation_id,
        ),
        history_id=history_id,
        previous_receipt_sha256=previous_receipt_sha256,
    )


@dataclass(frozen=True)
class DurableWorkUnitAttemptReceipt:
    receipt: WorkUnitAttemptReceipt
    sha256: str
    path: Path
    digest_path: Path

    def __post_init__(self) -> None:
        if self.sha256 != work_unit_attempt_receipt_sha256(self.receipt):
            raise WorkUnitReceiptContractError("durable receipt identity mismatch")
        if not self.path.is_file() or not self.digest_path.is_file():
            raise WorkUnitReceiptContractError("receipt artifact is not durable")
        try:
            data = self.path.read_bytes()
            external_digest = _read_digest_record(self.digest_path, self.path.name)
        except (OSError, WorkUnitReceiptContractError) as exc:
            raise WorkUnitReceiptContractError("receipt artifact is not durable") from exc
        if external_digest != self.sha256 or hashlib.sha256(data).hexdigest() != self.sha256:
            raise WorkUnitReceiptContractError("receipt artifact is not durable")


def _read_digest_record(path: Path, expected_filename: str) -> str:
    try:
        fields = path.read_text(encoding="ascii").strip().split()
    except (OSError, UnicodeError) as exc:
        raise WorkUnitReceiptContractError("receipt digest record unavailable") from exc
    if len(fields) != 2 or fields[1] != expected_filename:
        raise WorkUnitReceiptContractError("receipt digest record is invalid")
    if re.fullmatch(_DIGEST_PATTERN, fields[0]) is None:
        raise WorkUnitReceiptContractError("receipt digest record is invalid")
    return fields[0]


def read_durable_work_unit_attempt_receipt(
    path: Path, digest_path: Path
) -> DurableWorkUnitAttemptReceipt:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise WorkUnitReceiptContractError("receipt artifact unavailable") from exc
    expected = _read_digest_record(digest_path, path.name)
    actual = hashlib.sha256(data).hexdigest()
    if expected != actual:
        raise WorkUnitReceiptContractError("receipt digest mismatch")
    try:
        payload = json.loads(data)
        receipt = WorkUnitAttemptReceipt.model_validate(payload)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise WorkUnitReceiptContractError("receipt artifact is invalid") from exc
    if canonical_work_unit_attempt_receipt_bytes(receipt) != data:
        raise WorkUnitReceiptContractError("receipt artifact is not canonical")
    _validate_derived_identity(receipt)
    if work_unit_attempt_receipt_sha256(receipt) != expected:
        raise WorkUnitReceiptContractError("receipt artifact identity mismatch")
    return DurableWorkUnitAttemptReceipt(receipt, expected, path, digest_path)


def _write_exclusive(path: Path, data: bytes) -> None:
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise WorkUnitReceiptContractError("immutable receipt already exists") from exc
    except OSError as exc:
        raise WorkUnitReceiptContractError("receipt artifact is not writable") from exc
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
    except OSError as exc:
        raise WorkUnitReceiptContractError("receipt artifact write failed") from exc


def persist_work_unit_attempt_receipt(
    receipt: WorkUnitAttemptReceipt, path: Path
) -> DurableWorkUnitAttemptReceipt:
    data = canonical_work_unit_attempt_receipt_bytes(receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(data).hexdigest()
    digest_path = path.with_suffix(".sha256")
    _write_exclusive(path, data)
    _write_exclusive(digest_path, f"{digest}  {path.name}\n".encode("ascii"))
    return read_durable_work_unit_attempt_receipt(path, digest_path)


class WorkUnitAttemptReceiptStore:
    """Durable receipt lookup and append-only chain validation for one run."""

    def __init__(self, records: Sequence[DurableWorkUnitAttemptReceipt]) -> None:
        by_digest = {record.sha256: record for record in records}
        if len(by_digest) != len(records):
            raise WorkUnitReceiptContractError("receipt store contains duplicate digests")
        by_record_id: dict[str, str] = {}
        for record in records:
            previous_digest = by_record_id.setdefault(record.receipt.record_id, record.sha256)
            if previous_digest != record.sha256:
                raise WorkUnitReceiptContractError(
                    "receipt store contains conflicting record IDs"
                )
        self._records = by_digest

    @classmethod
    def from_execution_root(cls, root: Path) -> "WorkUnitAttemptReceiptStore":
        records: list[DurableWorkUnitAttemptReceipt] = []
        if not root.exists():
            return cls(())
        try:
            execution_dirs: list[Path] = []
            for attempt_dir in sorted(
                (path for path in root.glob("attempt-*") if path.is_dir()),
                key=lambda path: path.name,
            ):
                execution_dir = attempt_dir / "execution"
                if execution_dir.is_dir():
                    execution_dirs.append(execution_dir)
                    # D12 keeps Parser artifacts separate from the existing
                    # Generation artifact names.  The owner receipt remains
                    # the same immutable record; this is only its bounded
                    # diagnostic subdirectory discovery rule.
                    generation_dir = execution_dir / "generation"
                    if generation_dir.is_dir():
                        execution_dirs.append(generation_dir)
        except OSError as exc:
            raise WorkUnitReceiptContractError("receipt history unavailable") from exc
        for execution_dir in execution_dirs:
            for stem in ("work_unit_attempt_start", "work_unit_attempt_receipt"):
                path = execution_dir / f"{stem}.json"
                digest_path = execution_dir / f"{stem}.sha256"
                if path.exists() or digest_path.exists():
                    if not path.exists() or not digest_path.exists():
                        raise WorkUnitReceiptContractError("receipt history is incomplete")
                    records.append(read_durable_work_unit_attempt_receipt(path, digest_path))
        return cls(records)

    def resolve(self, digest: str) -> Optional[DurableWorkUnitAttemptReceipt]:
        return self._records.get(digest)

    def require_durable(self, digest: str) -> DurableWorkUnitAttemptReceipt:
        record = self.resolve(digest)
        if record is None:
            raise WorkUnitReceiptContractError("durable receipt reference cannot be resolved")
        return record

    def latest_terminal_digest(
        self, *, history_id: str, attempt_ordinal: Optional[int] = None
    ) -> Optional[str]:
        candidates = [
            record
            for record in self._records.values()
            if record.receipt.history_id == history_id
            and record.receipt.receipt_role == "attempt_terminal"
            and (attempt_ordinal is None or record.receipt.attempt_ordinal == attempt_ordinal)
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda record: record.receipt.attempt_ordinal).sha256

    def next_attempt_ordinal(self, *, history_id: str) -> int:
        """Return the next Q15 ordinal for one immutable receipt history."""

        ordinals = [
            record.receipt.attempt_ordinal
            for record in self._records.values()
            if record.receipt.history_id == history_id
        ]
        return max(ordinals, default=0) + 1

    def validate_chain(self, receipt: WorkUnitAttemptReceipt) -> None:
        visited: set[str] = set()
        current = receipt
        while True:
            digest = work_unit_attempt_receipt_sha256(current)
            if digest in visited:
                raise WorkUnitReceiptContractError("receipt history contains a cycle")
            visited.add(digest)
            if current.previous_receipt_sha256 is None:
                if current.attempt_ordinal != 1 or current.receipt_role != "attempt_started":
                    raise WorkUnitReceiptContractError("receipt history root is invalid")
                return
            parent_record = self.require_durable(current.previous_receipt_sha256)
            parent = parent_record.receipt
            if parent.history_id != current.history_id:
                raise WorkUnitReceiptContractError("receipt history ID mismatch")
            if parent.logical_run_id != current.logical_run_id:
                raise WorkUnitReceiptContractError("receipt logical-run identity mismatch")
            if parent.coverage_plan_sha256 != current.coverage_plan_sha256:
                raise WorkUnitReceiptContractError("receipt history plan mismatch")
            if parent.work_unit_id != current.work_unit_id:
                raise WorkUnitReceiptContractError("receipt history work-unit mismatch")
            if parent.attempt_ordinal > current.attempt_ordinal:
                raise WorkUnitReceiptContractError("receipt history ordinal order is invalid")
            if current.receipt_role == "attempt_terminal":
                if (
                    parent.receipt_role != "attempt_started"
                    or parent.attempt_ordinal != current.attempt_ordinal
                ):
                    raise WorkUnitReceiptContractError("terminal receipt parent is invalid")
            elif (
                parent.receipt_role != "attempt_terminal"
                or parent.attempt_ordinal != current.attempt_ordinal - 1
            ):
                raise WorkUnitReceiptContractError("retry start parent is invalid")
            current = parent


def validate_work_unit_attempt_receipt(
    payload: ReceiptInput,
    *,
    coverage_plan_sha256: Optional[str] = None,
    work_unit_id: Optional[str] = None,
    attempt_ordinal: Optional[int] = None,
    output_sha256: Optional[str] = None,
) -> WorkUnitAttemptReceipt:
    receipt = _model(payload)
    _validate_derived_identity(receipt)
    if coverage_plan_sha256 is not None and receipt.coverage_plan_sha256 != coverage_plan_sha256:
        raise WorkUnitReceiptContractError("receipt coverage-plan binding mismatch")
    if work_unit_id is not None and receipt.work_unit_id != work_unit_id:
        raise WorkUnitReceiptContractError("receipt work-unit binding mismatch")
    if attempt_ordinal is not None and receipt.attempt_ordinal != attempt_ordinal:
        raise WorkUnitReceiptContractError("receipt attempt binding mismatch")
    if output_sha256 is not None and receipt.work_unit_output_sha256 != output_sha256:
        raise WorkUnitReceiptContractError("receipt output binding mismatch")
    return receipt


__all__ = [
    "DurableWorkUnitAttemptReceipt",
    "RunnerBinding",
    "WORK_UNIT_ATTEMPT_RECEIPT_RECORD_TYPE",
    "WORK_UNIT_ATTEMPT_RECEIPT_SCHEMA_VERSION",
    "WorkUnitAttemptReceipt",
    "WorkUnitAttemptReceiptStore",
    "WorkUnitReceiptContractError",
    "build_work_unit_attempt_receipt",
    "canonical_work_unit_attempt_receipt_bytes",
    "derive_history_id",
    "derive_record_id",
    "persist_work_unit_attempt_receipt",
    "read_durable_work_unit_attempt_receipt",
    "validate_work_unit_attempt_receipt",
    "work_unit_attempt_receipt_sha256",
]
