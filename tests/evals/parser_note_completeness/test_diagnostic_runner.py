from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Tuple

import pytest

from tests.evals.parser_note_completeness.diagnostic import (
    DiagnosticProfile,
    load_diagnostic_profile,
    materialize_diagnostic_run_plan,
    materialize_profile_run_plan,
)
from tests.evals.parser_note_completeness.full_profile import FULL_CASE_IDS
from tests.evals.parser_note_completeness.run_plan import (
    canonical_run_plan_bytes,
    run_plan_sha256,
)
from tests.evals.parser_note_completeness.runner import main
from tests.evals.parser_note_completeness.smoke_profile import SMOKE_CASE_IDS


ROOT = Path(__file__).parent / "v1"
PROFILE_ROOTS = {
    "smoke": ROOT / "manifests" / "smoke" / "revision-001",
    "full": ROOT / "manifests" / "full" / "revision-001",
}


def _profile_inputs(kind: str) -> Tuple[Path, Path]:
    profile_root = PROFILE_ROOTS[kind]
    return profile_root / "profile.json", profile_root / "profile.sha256"


def _load_and_materialize(kind: str) -> Tuple[DiagnosticProfile, str, Any, str]:
    profile_path, digest_path = _profile_inputs(kind)
    profile, profile_digest = load_diagnostic_profile(profile_path, digest_path, ROOT)
    plan, plan_digest = materialize_diagnostic_run_plan(profile, profile_digest)
    return profile, profile_digest, plan, plan_digest


@pytest.mark.parametrize(
    ("kind", "expected_case_ids"),
    [("smoke", SMOKE_CASE_IDS), ("full", FULL_CASE_IDS)],
)
def test_profile_materialization_preserves_order_bindings_and_canonical_bytes(
    kind: str,
    expected_case_ids: Tuple[str, ...],
) -> None:
    profile, profile_digest, plan, plan_digest = _load_and_materialize(kind)

    assert tuple(case.case_id for case in profile.cases) == expected_case_ids
    assert tuple(slot.case_id for slot in plan.slots) == expected_case_ids
    assert tuple(slot.slot_id for slot in plan.slots) == tuple(
        f"{kind}-{case_id}" for case_id in expected_case_ids
    )
    for case, slot in zip(profile.cases, plan.slots):
        assert slot.reference_path == case.reference_path
        assert slot.digest_path == case.reference_digest_path
        assert slot.reference_sha256 == case.reference_sha256
        assert slot.membership == "diagnostic"
    assert plan.execution_mode == "development"
    assert plan.plan_id.endswith(profile_digest)
    assert plan_digest == run_plan_sha256(plan)
    assert canonical_run_plan_bytes(plan) == canonical_run_plan_bytes(
        json.loads(canonical_run_plan_bytes(plan))
    )


@pytest.mark.parametrize("kind", ["smoke", "full"])
def test_repeated_profile_materialization_is_byte_deterministic(kind: str) -> None:
    first_plan, first_digest = materialize_profile_run_plan(
        *_profile_inputs(kind),
        ROOT,
    )
    second_plan, second_digest = materialize_profile_run_plan(
        *_profile_inputs(kind),
        ROOT,
    )

    assert canonical_run_plan_bytes(first_plan) == canonical_run_plan_bytes(second_plan)
    assert first_digest == second_digest


def test_materialize_cli_writes_canonical_plan_and_external_digest(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_path, profile_digest_path = _profile_inputs("smoke")
    output_dir = tmp_path / "plan"

    exit_code = main(
        [
            "materialize-plan",
            "--profile",
            str(profile_path),
            "--profile-digest",
            str(profile_digest_path),
            "--benchmark-root",
            str(ROOT),
            "--output-dir",
            str(output_dir),
        ]
    )
    status = json.loads(capsys.readouterr().out)
    plan_bytes = (output_dir / "run_plan.json").read_bytes()
    plan_digest = (output_dir / "run_plan.sha256").read_text(encoding="ascii").split()

    assert exit_code == 0
    assert status["status"] == "plan_materialized"
    assert status["plan_digest"] == plan_digest[0]
    assert plan_bytes == canonical_run_plan_bytes(json.loads(plan_bytes))
    assert plan_digest == [hashlib.sha256(plan_bytes).hexdigest(), "run_plan.json"]


@pytest.mark.parametrize("kind", ["smoke", "full"])
def test_diagnostic_execution_produces_ordered_terminal_receipts_and_collection(
    kind: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_path, profile_digest_path = _profile_inputs(kind)
    output_dir = tmp_path / "plan"
    assert (
        main(
            [
                "materialize-plan",
                "--profile",
                str(profile_path),
                "--profile-digest",
                str(profile_digest_path),
                "--benchmark-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )
    capsys.readouterr()
    store = tmp_path / "store"

    exit_code = main(
        [
            "execute-plan",
            "--plan",
            str(output_dir / "run_plan.json"),
            "--plan-digest",
            str(output_dir / "run_plan.sha256"),
            "--benchmark-root",
            str(ROOT),
            "--store",
            str(store),
            "--invocation-id",
            f"{kind}-invocation-001",
        ]
    )
    status = json.loads(capsys.readouterr().out)
    plan = json.loads((output_dir / "run_plan.json").read_bytes())
    collection = json.loads(
        next((store / "collections").glob("revision-*.json")).read_bytes()
    )

    assert exit_code == 0
    assert status["status"] == "collection_complete"
    assert [slot["case_id"] for slot in collection["slots"]] == [
        slot["case_id"] for slot in plan["slots"]
    ]
    assert all(slot["state"] == "closed" for slot in collection["slots"])
    terminal_paths = sorted(store.glob("attempts/*/attempt-*/terminal.json"))
    assert len(terminal_paths) == len(plan["slots"])
    for terminal_path in terminal_paths:
        terminal = json.loads(terminal_path.read_bytes())
        assert terminal["terminal_status"] == "contract_valid"
        assert terminal["membership"] == "diagnostic"
        assert "quality_decision" not in terminal
        assert "result_role" not in terminal
    all_terminal_bytes = b"".join(path.read_bytes() for path in terminal_paths)
    all_collection_bytes = b"".join(
        path.read_bytes() for path in (store / "collections").glob("*.json")
    )
    assert str(ROOT).encode() not in all_terminal_bytes + all_collection_bytes


def test_profile_digest_mismatch_is_contract_rejection() -> None:
    profile_path, _ = _profile_inputs("smoke")
    profile, _ = load_diagnostic_profile(
        profile_path,
        PROFILE_ROOTS["smoke"] / "profile.sha256",
        ROOT,
    )

    with pytest.raises(ValueError, match="profile digest mismatch"):
        materialize_diagnostic_run_plan(profile, "0" * 64)


@pytest.mark.parametrize("field", ["reference_path", "digest_path"])
def test_execution_rejects_symlink_escape_from_benchmark_root(
    field: str,
    tmp_path: Path,
) -> None:
    profile, _, plan, plan_digest = _load_and_materialize("smoke")
    del profile
    plan_dir = tmp_path / "plan"
    plan_dir.mkdir()
    plan_path = plan_dir / "run_plan.json"
    plan_digest_path = plan_dir / "run_plan.sha256"
    plan_path.write_bytes(canonical_run_plan_bytes(plan))
    plan_digest_path.write_text(f"{plan_digest}  run_plan.json\n", encoding="ascii")

    benchmark_root = tmp_path / "benchmark-root"
    target_case = plan.slots[0]
    escaped = tmp_path / "outside.bin"
    escaped.write_bytes(b"outside")
    escaped_path = benchmark_root / (
        target_case.reference_path if field == "reference_path" else target_case.digest_path
    )
    escaped_path.parent.mkdir(parents=True)
    escaped_path.symlink_to(escaped)

    from tests.evals.parser_note_completeness.runner import execute_plan

    outcome = execute_plan(
        plan_path,
        plan_digest_path,
        tmp_path / "store",
        invocation_id="escape-test-001",
        benchmark_root=benchmark_root,
    )

    assert outcome.exit_code == 2
    assert outcome.status == "invalid_input"
    assert outcome.error in {
        "reference artifact is outside the benchmark root",
        "reference digest is outside the benchmark root",
    }
