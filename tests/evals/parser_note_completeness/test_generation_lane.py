from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Tuple

import pytest

from tests.evals.parser_note_completeness.diagnostic import load_diagnostic_profile
from tests.evals.parser_note_completeness.full_profile import FULL_CASE_IDS
from tests.evals.parser_note_completeness.generation_lane import (
    GenerationAttemptArtifact,
    GenerationInputArtifact,
    GenerationLaneOutcome,
    GenerationResultArtifact,
    build_generation_input,
    canonical_generation_lane_artifact_bytes,
)
from tests.evals.parser_note_completeness.runner import main
from tests.evals.parser_note_completeness.smoke_profile import SMOKE_CASE_IDS


ROOT = Path(__file__).parent / "v1"
PROFILE_ROOTS = {
    "smoke": ROOT / "manifests" / "smoke" / "revision-001",
    "full": ROOT / "manifests" / "full" / "revision-001",
}


def _profile_paths(kind: str) -> Tuple[Path, Path]:
    root = PROFILE_ROOTS[kind]
    return root / "profile.json", root / "profile.sha256"


def _materialize(kind: str, output_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    profile_path, digest_path = _profile_paths(kind)
    assert (
        main(
            [
                "materialize-plan",
                "--profile",
                str(profile_path),
                "--profile-digest",
                str(digest_path),
                "--benchmark-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )
    capsys.readouterr()


def _execute_args(
    kind: str,
    output_dir: Path,
    store: Path,
    *,
    invocation_id: str,
    resume: bool = False,
) -> list[str]:
    profile_path, digest_path = _profile_paths(kind)
    args = [
        "execute-plan",
        "--plan",
        str(output_dir / "run_plan.json"),
        "--plan-digest",
        str(output_dir / "run_plan.sha256"),
        "--benchmark-root",
        str(ROOT),
        "--lane",
        "generation",
        "--profile",
        str(profile_path),
        "--profile-digest",
        str(digest_path),
        "--store",
        str(store),
        "--invocation-id",
        invocation_id,
    ]
    if resume:
        args.append("--resume")
    return args


def test_generation_input_is_deterministic_and_binds_frozen_reference() -> None:
    profile, _ = load_diagnostic_profile(*_profile_paths("full"), ROOT)

    assert tuple(case.case_id for case in profile.cases) == FULL_CASE_IDS
    for case in profile.cases:
        first = build_generation_input(case, ROOT)
        second = build_generation_input(case, ROOT)
        first_bytes = canonical_generation_lane_artifact_bytes(first)

        assert first_bytes == canonical_generation_lane_artifact_bytes(second)
        assert first.input_role == "reference_document"
        assert first.case_id == first.document_id == case.case_id
        assert first.reference_sha256 == case.reference_sha256
        assert first.producer_configuration_sha256 == case.producer_configuration_sha256
        assert first_bytes == canonical_generation_lane_artifact_bytes(
            GenerationInputArtifact.model_validate(json.loads(first_bytes))
        )
        assert "quality_decision" not in first.model_dump()
        assert "result_role" not in first.model_dump()


def test_repeated_generation_execution_keeps_artifact_digests_stable(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "plan"
    _materialize("smoke", output_dir, capsys)
    first_store = tmp_path / "first-store"
    second_store = tmp_path / "second-store"

    assert main(_execute_args("smoke", output_dir, first_store, invocation_id="generation-repeat-001")) == 0
    capsys.readouterr()
    assert main(_execute_args("smoke", output_dir, second_store, invocation_id="generation-repeat-002")) == 0
    capsys.readouterr()

    first_artifacts = {
        path.relative_to(first_store): path.read_bytes()
        for path in first_store.glob("attempts/*/attempt-*/execution/*")
    }
    second_artifacts = {
        path.relative_to(second_store): path.read_bytes()
        for path in second_store.glob("attempts/*/attempt-*/execution/*")
    }
    assert first_artifacts == second_artifacts


@pytest.mark.parametrize("kind", ["smoke", "full"])
def test_generation_execution_materializes_input_lineage_without_note_candidate(
    kind: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tests.evals.parser_note_completeness.runner as runner_module

    output_dir = tmp_path / "plan"
    store = tmp_path / "store"
    _materialize(kind, output_dir, capsys)

    def parser_must_not_run(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("Generation lane must not consume parser candidates")

    monkeypatch.setattr(runner_module, "execute_parser_case", parser_must_not_run)
    assert main(_execute_args(kind, output_dir, store, invocation_id=f"generation-{kind}-001")) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["status"] == "collection_complete"

    profile, _ = load_diagnostic_profile(*_profile_paths(kind), ROOT)
    cases: dict[str, Any] = {case.case_id: case for case in profile.cases}
    expected_ids = SMOKE_CASE_IDS if kind == "smoke" else FULL_CASE_IDS
    collection_path = next((store / "collections").glob("revision-*.json"))
    collection = json.loads(collection_path.read_bytes())
    assert [slot["case_id"] for slot in collection["slots"]] == list(expected_ids)
    assert all(slot["state"] == "closed" for slot in collection["slots"])

    execution_paths = sorted(store.glob("attempts/*/attempt-*/execution"))
    assert len(execution_paths) == len(expected_ids)
    for execution_path in execution_paths:
        assert {path.name for path in execution_path.iterdir()} == {
            "generation_input.json",
            "generation_input.sha256",
            "result.json",
            "result.sha256",
            "attempt.json",
            "attempt.sha256",
        }
        input_path = execution_path / "generation_input.json"
        result_path = execution_path / "result.json"
        attempt_path = execution_path / "attempt.json"
        input_bytes = input_path.read_bytes()
        result_bytes = result_path.read_bytes()
        attempt_bytes = attempt_path.read_bytes()
        input_model = GenerationInputArtifact.model_validate(json.loads(input_bytes))
        result_model = GenerationResultArtifact.model_validate(json.loads(result_bytes))
        attempt_model = GenerationAttemptArtifact.model_validate(json.loads(attempt_bytes))
        case = cases[input_model.case_id]

        assert input_bytes == canonical_generation_lane_artifact_bytes(input_model)
        assert result_bytes == canonical_generation_lane_artifact_bytes(result_model)
        assert attempt_bytes == canonical_generation_lane_artifact_bytes(attempt_model)
        assert input_path.with_suffix(".sha256").read_text(encoding="ascii").split() == [
            hashlib.sha256(input_bytes).hexdigest(),
            "generation_input.json",
        ]
        assert result_path.with_suffix(".sha256").read_text(encoding="ascii").split() == [
            hashlib.sha256(result_bytes).hexdigest(),
            "result.json",
        ]
        assert attempt_path.with_suffix(".sha256").read_text(encoding="ascii").split() == [
            hashlib.sha256(attempt_bytes).hexdigest(),
            "attempt.json",
        ]
        assert input_model.reference_sha256 == case.reference_sha256
        assert result_model.generation_input_sha256 == hashlib.sha256(input_bytes).hexdigest()
        assert result_model.reference_sha256 == input_model.reference_sha256
        assert attempt_model.result_sha256 == hashlib.sha256(result_bytes).hexdigest()
        assert attempt_model.generation_input_sha256 == result_model.generation_input_sha256
        assert result_model.status == attempt_model.status == "input_materialized"
        assert "quality_decision" not in result_model.model_dump()
        assert "result_role" not in result_model.model_dump()
        assert not any(path.name.startswith("candidate") for path in execution_path.iterdir())
        assert not any(path.name.startswith("note") for path in execution_path.iterdir())
        terminal_bytes = (execution_path.parent / "terminal.json").read_bytes()
        assert terminal_bytes.find(hashlib.sha256(result_bytes).hexdigest().encode("ascii")) >= 0
        assert str(ROOT).encode() not in result_bytes + attempt_bytes + terminal_bytes


def test_generation_lane_rejects_profile_plan_binding_mismatch(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "plan"
    _materialize("smoke", output_dir, capsys)
    args = _execute_args("full", output_dir, tmp_path / "store", invocation_id="generation-mismatch-001")

    assert main(args) == 2
    assert json.loads(capsys.readouterr().out) == {
        "error": "generation profile and run plan binding mismatch",
        "exit_code": 2,
        "status": "invalid_input",
    }


def test_generation_lane_resume_does_not_repeat_closed_slots(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tests.evals.parser_note_completeness.runner as runner_module

    output_dir = tmp_path / "plan"
    store = tmp_path / "store"
    _materialize("smoke", output_dir, capsys)
    original_execute = runner_module.execute_generation_case
    failed = {"value": False}

    def fail_once(*args: Any, **kwargs: Any) -> GenerationLaneOutcome:
        case = args[0]
        if case.case_id == "P01" and not failed["value"]:
            failed["value"] = True
            return GenerationLaneOutcome(1, "operational_failure", error="generation input failed")
        return original_execute(*args, **kwargs)

    monkeypatch.setattr(runner_module, "execute_generation_case", fail_once)
    assert main(_execute_args("smoke", output_dir, store, invocation_id="generation-resume-001")) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "collection_incomplete"
    failed_terminal = json.loads(
        (store / "attempts" / "smoke-P01" / "attempt-0001" / "terminal.json").read_bytes()
    )
    assert failed_terminal["terminal_status"] == "operational_failure"

    monkeypatch.setattr(runner_module, "execute_generation_case", original_execute)
    assert (
        main(
            _execute_args(
                "smoke",
                output_dir,
                store,
                invocation_id="generation-resume-002",
                resume=True,
            )
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["status"] == "collection_complete"
    assert len(tuple((store / "attempts" / "smoke-P01").glob("attempt-*/terminal.json"))) == 2
    assert len(tuple((store / "attempts" / "smoke-W01").glob("attempt-*/terminal.json"))) == 1


def test_generation_lane_rejects_provider_execution_without_network_or_provider_use(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "plan"
    _materialize("smoke", output_dir, capsys)
    args = _execute_args("smoke", output_dir, tmp_path / "store", invocation_id="generation-provider-001")
    args.extend(["--provider", "forbidden-provider"])

    assert main(args) == 2
    assert json.loads(capsys.readouterr().out) == {
        "error": "live execution or credentials are not permitted",
        "exit_code": 2,
        "status": "invalid_input",
    }
