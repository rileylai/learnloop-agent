from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tests.evals.parser_note_completeness.run_plan import (
    ATTESTATION_SCHEMA_VERSION,
    RUNNER_VERSION,
    CollectionSlot,
    CollectionRevision,
    RunPlan,
    RunSlot,
    TerminalReceipt,
    canonical_collection_bytes,
    canonical_run_plan_bytes,
    invocation_sha256,
    run_plan_sha256,
)
from tests.evals.parser_note_completeness.runner import (
    collect_collection,
    execute_plan,
    main,
)


PACKAGE_ROOT = Path(__file__).parent
REFERENCE_PATH = (
    PACKAGE_ROOT
    / "v1"
    / "reference_documents"
    / "W01"
    / "revision-001"
    / "normalized_document.json"
)
DIGEST_PATH = REFERENCE_PATH.with_name("normalized_document.sha256")
FORBIDDEN_FIELDS = {
    "authority",
    "authority_status",
    "result_role",
    "quality_decision",
    "gate_decision",
    "comparison_decision",
    "adoption_decision",
}


def _plan(
    tmp_path: Path,
    *,
    missing: bool = False,
    invalid: bool = False,
) -> tuple[Path, Path, RunPlan]:
    plan_root = tmp_path / "plan-root"
    plan_root.mkdir()
    reference_path = plan_root / "reference.json"
    slot_digest_path = plan_root / "reference.sha256"
    planned_bytes = b'{"artifact_role":"reference_document"}\n' if invalid else REFERENCE_PATH.read_bytes()
    digest = hashlib.sha256(planned_bytes).hexdigest()
    if not missing:
        reference_path.write_bytes(planned_bytes)
    slot_digest_path.write_text(f"{digest}  {reference_path.name}\n", encoding="ascii")
    plan = RunPlan(
        schema_version="run-plan/1.0.0",
        runner_version=RUNNER_VERSION,
        artifact_type="parser_note_completeness_run_plan",
        plan_id="w01-development-plan",
        plan_revision="revision-001",
        execution_mode="development",
        slots=(
            RunSlot(
                slot_id="slot-w01",
                case_id="W01",
                operation="validate_reference",
                reference_path="reference.json",
                digest_path="reference.sha256",
                reference_sha256=digest,
                membership="diagnostic",
            ),
        ),
    )
    plan_path = plan_root / "plan.json"
    digest_path = plan_root / "plan.sha256"
    plan_bytes = canonical_run_plan_bytes(plan)
    plan_path.write_bytes(plan_bytes)
    plan_digest = hashlib.sha256(plan_bytes).hexdigest()
    digest_path.write_text(f"{plan_digest}  plan.json\n", encoding="ascii")
    return plan_path, digest_path, plan


def _execute_args(
    plan_path: Path,
    digest_path: Path,
    store: Path,
    *extra: str,
    invocation_id: str = "invocation-001",
) -> list[str]:
    return [
        "execute-plan",
        "--plan",
        str(plan_path),
        "--plan-digest",
        str(digest_path),
        "--store",
        str(store),
        "--invocation-id",
        invocation_id,
        *extra,
    ]


def _load_status(capsys: pytest.CaptureFixture[str]) -> dict[str, Any]:
    return json.loads(capsys.readouterr().out)


def test_run_plan_is_strict_frozen_canonical_and_external_digest(tmp_path: Path) -> None:
    plan_path, digest_path, plan = _plan(tmp_path)
    data = plan_path.read_bytes()
    assert data == canonical_run_plan_bytes(json.loads(data))
    assert digest_path.read_text(encoding="ascii").split()[0] == run_plan_sha256(plan)
    with pytest.raises(ValidationError):
        RunPlan.model_validate({**plan.model_dump(), "unexpected": True})
    with pytest.raises(ValidationError):
        RunPlan.model_validate({**plan.model_dump(), "slots": [{**plan.slots[0].model_dump(), "reference_sha256": "1"}]})
    assert plan.slots[0].reference_path == "reference.json"
    assert not Path(plan.slots[0].reference_path).is_absolute()
    with pytest.raises(ValidationError):
        RunSlot.model_validate({**plan.slots[0].model_dump(), "reference_path": "/tmp/reference.json"})
    with pytest.raises(ValidationError):
        RunSlot.model_validate({**plan.slots[0].model_dump(), "digest_path": "..\\digest.sha256"})


def test_w01_plan_closes_once_and_resume_does_not_rerun_closed_slot(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan_path, digest_path, _ = _plan(tmp_path)
    store = tmp_path / "store"
    assert main(_execute_args(plan_path, digest_path, store, invocation_id="invocation-001")) == 0
    first_status = _load_status(capsys)
    assert first_status["status"] == "collection_complete"
    first_start = (store / "attempts" / "slot-w01" / "attempt-0001" / "start.json").read_bytes()

    assert main(_execute_args(plan_path, digest_path, store, invocation_id="invocation-002")) == 0
    second_status = _load_status(capsys)
    assert second_status["status"] == "collection_complete"
    assert not (store / "attempts" / "slot-w01" / "attempt-0002").exists()
    assert (store / "attempts" / "slot-w01" / "attempt-0001" / "start.json").read_bytes() == first_start
    assert second_status["collection_digest"] != first_status["collection_digest"]


def test_same_invocation_id_is_rejected_without_new_attempt_or_collection(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan_path, digest_path, _ = _plan(tmp_path)
    store = tmp_path / "store"
    assert main(_execute_args(plan_path, digest_path, store, invocation_id="invocation-001")) == 0
    _load_status(capsys)
    assert main(_execute_args(plan_path, digest_path, store, invocation_id="invocation-001")) == 2
    status = _load_status(capsys)
    assert status["error"] == "invocation already exists"
    assert len(tuple((store / "collections").glob("revision-*.json"))) == 1
    assert not (store / "attempts" / "slot-w01" / "attempt-0002").exists()


def test_operational_slot_resume_appends_attempt_and_closes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan_path, digest_path, _ = _plan(tmp_path, missing=True)
    store = tmp_path / "store"
    assert main(_execute_args(plan_path, digest_path, store, invocation_id="invocation-001")) == 1
    assert _load_status(capsys)["status"] == "collection_incomplete"
    assert (store / "attempts" / "slot-w01" / "attempt-0001" / "terminal.json").exists()

    (plan_path.parent / "reference.json").write_bytes(REFERENCE_PATH.read_bytes())
    # The plan and its external digest stay immutable while the input becomes available.

    assert main(
        _execute_args(
            plan_path,
            digest_path,
            store,
            "--resume",
            invocation_id="invocation-002",
        )
    ) == 0
    assert _load_status(capsys)["status"] == "collection_complete"
    assert (store / "attempts" / "slot-w01" / "attempt-0002" / "terminal.json").exists()


def test_start_only_attempt_is_unclosed_and_collection_is_canonical(tmp_path: Path) -> None:
    plan_path, digest_path, plan = _plan(tmp_path)
    store = tmp_path / "store"
    outcome = execute_plan(
        plan_path,
        digest_path,
        store,
        invocation_id="invocation-001",
        interrupt_after_start_slot="slot-w01",
    )
    assert outcome.exit_code == 1
    start = store / "attempts" / "slot-w01" / "attempt-0001" / "start.json"
    assert start.exists()
    assert not (start.parent / "terminal.json").exists()
    revision_paths = sorted((store / "collections").glob("revision-*.json"))
    assert len(revision_paths) == 1
    revision_bytes = revision_paths[0].read_bytes()
    revision = CollectionRevision.model_validate(json.loads(revision_bytes))
    assert revision.slots[0].state == "unclosed"
    assert revision_bytes == canonical_collection_bytes(revision)
    assert set(revision.model_dump()).isdisjoint(FORBIDDEN_FIELDS)

    resumed = execute_plan(
        plan_path,
        digest_path,
        store,
        invocation_id="invocation-002",
        resume=True,
    )
    assert resumed.exit_code == 0
    assert (store / "attempts" / "slot-w01" / "attempt-0002" / "terminal.json").exists()
    assert not (store / "attempts" / "slot-w01" / "attempt-0001" / "terminal.json").exists()


def test_missing_slot_collection_is_explicit_and_has_no_decision_ownership(tmp_path: Path) -> None:
    plan_path, digest_path, plan = _plan(tmp_path)
    loaded = RunPlan.model_validate(json.loads(plan_path.read_bytes()))
    revision, digest = collect_collection(
        loaded,
        run_plan_sha256(loaded),
        "invocation-001",
        "a" * 64,
        tmp_path / "store",
        offline_attestation="missing",
    )
    assert revision.slots[0].state == "missing"
    assert digest == hashlib.sha256(canonical_collection_bytes(revision)).hexdigest()
    assert FORBIDDEN_FIELDS.isdisjoint(revision.model_dump())


def test_terminal_and_collection_slot_state_invariants_are_strict() -> None:
    base_terminal = {
        "schema_version": "runner-terminal-receipt/1.0.0",
        "runner_version": RUNNER_VERSION,
        "artifact_type": "runner_terminal_receipt",
        "operation": "validate_reference",
        "plan_sha256": "a" * 64,
        "invocation_id": "invocation-001",
        "reference_sha256": "b" * 64,
        "invocation_sha256": "c" * 64,
        "slot_id": "slot-w01",
        "case_id": "W01",
        "attempt_ordinal": 1,
        "membership": "diagnostic",
        "offline_attestation": "missing",
    }
    with pytest.raises(ValidationError):
        TerminalReceipt.model_validate({**base_terminal, "exit_code": 0, "terminal_status": "contract_valid"})
    valid = TerminalReceipt.model_validate(
        {**base_terminal, "exit_code": 0, "terminal_status": "contract_valid", "result_sha256": "d" * 64}
    )
    assert valid.exit_code == 0
    with pytest.raises(ValidationError):
        TerminalReceipt.model_validate(
            {**base_terminal, "exit_code": 1, "terminal_status": "operational_failure", "result_sha256": "d" * 64}
        )
    with pytest.raises(ValidationError):
        CollectionSlot(slot_id="slot-w01", case_id="W01", attempt_ordinals=(1,), state="missing")
    with pytest.raises(ValidationError):
        CollectionSlot(slot_id="slot-w01", case_id="W01", attempt_ordinals=(1, 3), state="operational")
    assert CollectionSlot(slot_id="slot-w01", case_id="W01", attempt_ordinals=(), state="missing")


def test_preflight_rejects_live_flags_without_leaking_values(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan_path, digest_path, _ = _plan(tmp_path)
    secret = "do-not-print-this-secret"
    monkeypatch.setenv("OPENAI_API_KEY", secret)
    exit_code = main(_execute_args(plan_path, digest_path, tmp_path / "store", "--live"))
    assert exit_code == 2
    output = capsys.readouterr().out
    assert secret not in output
    assert json.loads(output)["error"] == "live execution or credentials are not permitted"


def test_secret_bearing_cli_flags_are_unknown_json_argument_errors(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan_path, digest_path, _ = _plan(tmp_path)
    secret = "never-print-this"
    exit_code = main(
        _execute_args(plan_path, digest_path, tmp_path / "store", "--api-key", secret)
    )
    output = capsys.readouterr()
    assert exit_code == 2
    assert output.err == ""
    assert secret not in output.out
    assert json.loads(output.out) == {
        "error": "invalid command arguments",
        "exit_code": 2,
        "status": "invalid_input",
    }


def test_missing_attestation_is_non_authoritative_and_formal_is_rejected(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan_path, digest_path, _ = _plan(tmp_path)
    assert main(_execute_args(plan_path, digest_path, tmp_path / "store", "--formal")) == 2
    status = _load_status(capsys)
    assert status["status"] == "invalid_input"


def test_invalid_slot_is_collected_without_quality_or_authority_decisions(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan_path, digest_path, _ = _plan(tmp_path, invalid=True)
    assert main(
        _execute_args(plan_path, digest_path, tmp_path / "store", invocation_id="invocation-001")
    ) == 2
    status = _load_status(capsys)
    collection = json.loads(
        (tmp_path / "store" / "collections" / "revision-0001.json").read_bytes()
    )
    assert status["status"] == "invalid_input"
    assert collection["slots"][0]["state"] == "invalid"
    assert FORBIDDEN_FIELDS.isdisjoint(collection)


def test_fake_network_attestation_is_rejected_without_formal_authority(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan_path, plan_digest_path, _ = _plan(tmp_path)
    plan_digest = plan_digest_path.read_text(encoding="ascii").split()[0]
    invocation_digest = invocation_sha256(
        {
            "command": "execute-plan",
            "plan_sha256": plan_digest,
            "invocation_id": "invocation-001",
            "resume": False,
            "formal": False,
            "attestation_supplied": True,
        }
    )
    fake_payload = {
        "schema_version": ATTESTATION_SCHEMA_VERSION,
        "runner_version": RUNNER_VERSION,
        "artifact_type": "network_denial_attestation",
        "plan_sha256": plan_digest,
        "invocation_id": "invocation-001",
        "invocation_sha256": invocation_digest,
        "outer_boundary_mechanism": "python_mock",
        "network_denial": "enforced",
        "failed_socket_probe": "failed",
        "socket_probe_target": "127.0.0.1:9",
    }
    attestation_path = tmp_path / "attestation.json"
    attestation_bytes = json.dumps(fake_payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    attestation_path.write_bytes(attestation_bytes)
    attestation_digest_path = tmp_path / "attestation.sha256"
    attestation_digest_path.write_text(
        f"{hashlib.sha256(attestation_bytes).hexdigest()}  attestation.json\n",
        encoding="ascii",
    )
    assert main(
        _execute_args(
            plan_path,
            plan_digest_path,
            tmp_path / "store",
            "--attestation",
            str(attestation_path),
            "--attestation-digest",
            str(attestation_digest_path),
        )
    ) == 2
    output = _load_status(capsys)
    assert output["status"] == "invalid_input"
    assert not (tmp_path / "store" / "attempts").exists()
