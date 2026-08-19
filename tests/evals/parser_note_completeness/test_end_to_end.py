from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tests.evals.parser_note_completeness.end_to_end import EndToEndResultArtifact
from tests.evals.parser_note_completeness.runner import execute_plan, main


ROOT = Path(__file__).parent / "v1"
PROFILE_ROOT = ROOT / "manifests" / "smoke" / "revision-001"


def _materialize(tmp_path: Path, capsys: object) -> Path:
    plan_dir = tmp_path / "plan"
    assert main(
        [
            "materialize-plan",
            "--profile",
            str(PROFILE_ROOT / "profile.json"),
            "--profile-digest",
            str(PROFILE_ROOT / "profile.sha256"),
            "--benchmark-root",
            str(ROOT),
            "--output-dir",
            str(plan_dir),
        ]
    ) == 0
    capsys.readouterr()  # type: ignore[attr-defined]
    return plan_dir


def _execute_args(plan_dir: Path, store: Path, invocation_id: str) -> list[str]:
    return [
        "execute-plan",
        "--plan",
        str(plan_dir / "run_plan.json"),
        "--plan-digest",
        str(plan_dir / "run_plan.sha256"),
        "--benchmark-root",
        str(ROOT),
        "--lane",
        "end-to-end",
        "--profile",
        str(PROFILE_ROOT / "profile.json"),
        "--profile-digest",
        str(PROFILE_ROOT / "profile.sha256"),
        "--store",
        str(store),
        "--invocation-id",
        invocation_id,
    ]


def _digest(path: Path) -> str:
    fields = path.with_suffix(".sha256").read_text(encoding="ascii").split()
    assert fields[1] == path.name
    assert fields[0] == hashlib.sha256(path.read_bytes()).hexdigest()
    return fields[0]


def test_successful_end_to_end_binds_all_durable_artifacts(
    tmp_path: Path,
    capsys,
) -> None:
    plan_dir = _materialize(tmp_path, capsys)
    store = tmp_path / "store"

    assert main(_execute_args(plan_dir, store, "e2e-success-001")) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["status"] == "collection_complete"

    for execution_dir in sorted(store.glob("attempts/*/attempt-*/execution")):
        result_path = execution_dir / "result.json"
        attempt_path = execution_dir / "attempt.json"
        result = EndToEndResultArtifact.model_validate(json.loads(result_path.read_bytes()))
        attempt = json.loads(attempt_path.read_bytes())
        assert _digest(result_path) == status.get("result_digest", _digest(result_path))
        assert attempt["result_sha256"] == _digest(result_path)
        assert _digest(attempt_path) == hashlib.sha256(attempt_path.read_bytes()).hexdigest()
        assert result.renderer_output_sha256 == _digest(execution_dir / "renderer-output.html")
        assert result.renderer_capture_sha256 == _digest(execution_dir / "renderer-capture.json")
        assert result.rendered_note_projection_sha256 == _digest(
            execution_dir / "rendered-note-projection.json"
        )
        closure = json.loads(
            (execution_dir / "generation" / "coverage_closure.json").read_bytes()
        )
        assert closure["coverage_closure_state"] == "closed"

        terminal = json.loads((execution_dir.parent / "terminal.json").read_bytes())
        assert terminal["result_sha256"] == _digest(result_path)
        assert terminal["terminal_status"] == "contract_valid"


def test_renderer_artifacts_replay_identically_across_e2e_runs(
    tmp_path: Path,
    capsys,
) -> None:
    plan_dir = _materialize(tmp_path, capsys)
    first_store = tmp_path / "first"
    second_store = tmp_path / "second"
    assert main(_execute_args(plan_dir, first_store, "e2e-replay-001")) == 0
    capsys.readouterr()
    assert main(_execute_args(plan_dir, second_store, "e2e-replay-002")) == 0
    capsys.readouterr()

    names = (
        "renderer-output.html",
        "renderer-output.sha256",
        "renderer-capture.json",
        "renderer-capture.sha256",
        "rendered-note-projection.json",
        "rendered-note-projection.sha256",
    )
    for first in sorted(first_store.glob("attempts/*/attempt-*/execution")):
        relative = first.relative_to(first_store)
        second = second_store / relative
        for name in names:
            assert (first / name).read_bytes() == (second / name).read_bytes()


def test_resume_keeps_interrupted_attempt_history_immutable(
    tmp_path: Path,
    capsys,
) -> None:
    plan_dir = _materialize(tmp_path, capsys)
    store = tmp_path / "store"
    plan_path = plan_dir / "run_plan.json"
    plan_digest_path = plan_dir / "run_plan.sha256"

    first = execute_plan(
        plan_path,
        plan_digest_path,
        store,
        invocation_id="e2e-interrupt-001",
        benchmark_root=ROOT,
        lane="end-to-end",
        profile_path=PROFILE_ROOT / "profile.json",
        profile_digest_path=PROFILE_ROOT / "profile.sha256",
        interrupt_after_start_slot="smoke-P01",
    )
    assert first.exit_code == 1
    first_start = store / "attempts" / "smoke-P01" / "attempt-0001" / "start.json"
    first_start_bytes = first_start.read_bytes()
    assert not (first_start.parent / "execution").exists()

    second = execute_plan(
        plan_path,
        plan_digest_path,
        store,
        invocation_id="e2e-resume-002",
        benchmark_root=ROOT,
        lane="end-to-end",
        profile_path=PROFILE_ROOT / "profile.json",
        profile_digest_path=PROFILE_ROOT / "profile.sha256",
        resume=True,
    )
    assert second.exit_code == 0
    assert first_start.read_bytes() == first_start_bytes
    resumed_execution = store / "attempts" / "smoke-P01" / "attempt-0002" / "execution"
    assert (resumed_execution / "result.json").exists()
    assert (resumed_execution.parent / "terminal.json").exists()
    assert len(tuple((store / "collections").glob("revision-*.json"))) == 2

