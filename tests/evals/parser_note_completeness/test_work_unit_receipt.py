from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from .work_unit_receipt import (
    WORK_UNIT_ATTEMPT_RECEIPT_RECORD_TYPE,
    WORK_UNIT_ATTEMPT_RECEIPT_SCHEMA_VERSION,
    WorkUnitAttemptReceipt,
    WorkUnitAttemptReceiptStore,
    WorkUnitReceiptContractError,
    build_work_unit_attempt_receipt,
    canonical_work_unit_attempt_receipt_bytes,
    persist_work_unit_attempt_receipt,
    read_durable_work_unit_attempt_receipt,
    validate_work_unit_attempt_receipt,
    work_unit_attempt_receipt_sha256,
)


PLAN_DIGEST = "a" * 64
UNIT_ID = "work-unit-" + "b" * 64
OUTPUT_DIGEST = "c" * 64
RUNNER_PLAN_DIGEST = "d" * 64


def _receipt(
    *,
    role: str,
    status: str,
    ordinal: int = 1,
    output_digest: str | None = None,
    previous_digest: str | None = None,
    runner_ordinal: int = 1,
    execution_id: str = "execution-1",
) -> WorkUnitAttemptReceipt:
    return build_work_unit_attempt_receipt(
        receipt_role=role,  # type: ignore[arg-type]
        lifecycle_status=status,  # type: ignore[arg-type]
        coverage_plan_sha256=PLAN_DIGEST,
        work_unit_id=UNIT_ID,
        attempt_ordinal=ordinal,
        work_unit_output_sha256=output_digest,
        membership="diagnostic",
        logical_run_id="logical-run-1",
        execution_id=execution_id,
        runner_plan_sha256=RUNNER_PLAN_DIGEST,
        runner_slot_id="slot-1",
        runner_attempt_ordinal=runner_ordinal,
        runner_invocation_id="invocation-1",
        previous_receipt_sha256=previous_digest,
    )


def _persist_pair(root: Path) -> tuple[WorkUnitAttemptReceipt, WorkUnitAttemptReceipt, WorkUnitAttemptReceiptStore]:
    start = _receipt(role="attempt_started", status="started")
    start_path = root / "attempt-0001" / "execution" / "work_unit_attempt_start.json"
    start_record = persist_work_unit_attempt_receipt(start, start_path)
    terminal = _receipt(
        role="attempt_terminal",
        status="complete",
        output_digest=OUTPUT_DIGEST,
        previous_digest=start_record.sha256,
    )
    terminal_path = root / "attempt-0001" / "execution" / "work_unit_attempt_receipt.json"
    terminal_record = persist_work_unit_attempt_receipt(terminal, terminal_path)
    return start, terminal, WorkUnitAttemptReceiptStore.from_execution_root(root)


def test_receipt_schema_roles_and_canonical_digest_are_exact() -> None:
    start = _receipt(role="attempt_started", status="started")
    terminal = _receipt(
        role="attempt_terminal",
        status="complete",
        output_digest=OUTPUT_DIGEST,
        previous_digest=work_unit_attempt_receipt_sha256(start),
    )
    assert set(start.model_dump(mode="json")) == {
        "schema_version",
        "artifact_role",
        "record_id",
        "receipt_role",
        "coverage_plan_sha256",
        "work_unit_id",
        "attempt_ordinal",
        "work_unit_output_sha256",
        "lifecycle_status",
        "membership",
        "logical_run_id",
        "execution_id",
        "runner_binding",
        "history_id",
        "previous_receipt_sha256",
    }
    assert start.schema_version == WORK_UNIT_ATTEMPT_RECEIPT_SCHEMA_VERSION
    assert start.artifact_role == WORK_UNIT_ATTEMPT_RECEIPT_RECORD_TYPE
    assert canonical_work_unit_attempt_receipt_bytes(start) == canonical_work_unit_attempt_receipt_bytes(
        json.loads(canonical_work_unit_attempt_receipt_bytes(start))
    )
    assert not canonical_work_unit_attempt_receipt_bytes(start).endswith(b"\n")
    assert terminal.work_unit_output_sha256 == OUTPUT_DIGEST

    with pytest.raises(ValidationError):
        _receipt(role="attempt_terminal", status="complete")
    with pytest.raises(ValidationError):
        _receipt(role="attempt_started", status="started", output_digest=OUTPUT_DIGEST)


def test_receipt_is_immutable_and_durable_before_store_resolution(tmp_path: Path) -> None:
    start, terminal, store = _persist_pair(tmp_path / "slot-1")
    terminal_digest = work_unit_attempt_receipt_sha256(terminal)
    resolved = store.require_durable(terminal_digest)
    assert resolved.receipt == terminal
    assert resolved.sha256 == terminal_digest
    assert resolved.path.read_bytes() == canonical_work_unit_attempt_receipt_bytes(terminal)
    assert store.latest_terminal_digest(history_id=terminal.history_id) == terminal_digest
    store.validate_chain(terminal)

    with pytest.raises(WorkUnitReceiptContractError):
        persist_work_unit_attempt_receipt(start, resolved.path)


def test_broken_history_chain_and_pending_digest_fail_closed(tmp_path: Path) -> None:
    _, terminal, full_store = _persist_pair(tmp_path / "complete-slot")
    terminal_record = full_store.require_durable(work_unit_attempt_receipt_sha256(terminal))
    broken_store = WorkUnitAttemptReceiptStore((terminal_record,))
    with pytest.raises(WorkUnitReceiptContractError, match="cannot be resolved"):
        broken_store.validate_chain(terminal)

    with pytest.raises(WorkUnitReceiptContractError, match="cannot be resolved"):
        WorkUnitAttemptReceiptStore(()).require_durable("e" * 64)


def test_runner_attempt_ordinal_is_lineage_only() -> None:
    receipt = _receipt(
        role="attempt_terminal",
        status="complete",
        output_digest=OUTPUT_DIGEST,
        previous_digest="e" * 64,
        runner_ordinal=2,
        ordinal=1,
    )
    assert receipt.attempt_ordinal == 1
    assert receipt.runner_binding.runner_attempt_ordinal == 2
    assert validate_work_unit_attempt_receipt(
        receipt,
        coverage_plan_sha256=PLAN_DIGEST,
        work_unit_id=UNIT_ID,
        attempt_ordinal=1,
        output_sha256=OUTPUT_DIGEST,
    ) == receipt
    with pytest.raises(WorkUnitReceiptContractError, match="attempt binding"):
        validate_work_unit_attempt_receipt(receipt, attempt_ordinal=2)


def test_durable_reader_rejects_pending_or_tampered_digest(tmp_path: Path) -> None:
    start = _receipt(role="attempt_started", status="started")
    path = tmp_path / "work_unit_attempt_start.json"
    record = persist_work_unit_attempt_receipt(start, path)
    record.digest_path.write_text(f"{'f' * 64}  {path.name}\n", encoding="ascii")
    with pytest.raises(WorkUnitReceiptContractError, match="digest mismatch"):
        read_durable_work_unit_attempt_receipt(record.path, record.digest_path)
