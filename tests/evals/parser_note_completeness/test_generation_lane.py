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
    build_pre_render_note,
    canonical_generation_lane_artifact_bytes,
)
from tests.evals.parser_note_completeness.benchmark_note import (
    BenchmarkNoteDocument,
    canonical_benchmark_note_bytes,
    validate_benchmark_note_artifact,
)
from tests.evals.parser_note_completeness.normalized_document import NormalizedDocument
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

    assert main(_execute_args("smoke", output_dir, first_store, invocation_id="generation-repeat-001")) == 2
    capsys.readouterr()
    assert main(_execute_args("smoke", output_dir, second_store, invocation_id="generation-repeat-002")) == 2
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
    assert all("coverage_closure" not in path.name for path in first_artifacts)


@pytest.mark.parametrize("kind", ["smoke", "full"])
def test_generation_execution_materializes_pre_render_note_candidate(
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
    assert main(_execute_args(kind, output_dir, store, invocation_id=f"generation-{kind}-001")) == 2
    status = json.loads(capsys.readouterr().out)
    assert status["status"] == "invalid_input"
    assert "Q28 closure dependency gap" in status["error"]

    profile, _ = load_diagnostic_profile(*_profile_paths(kind), ROOT)
    cases: dict[str, Any] = {case.case_id: case for case in profile.cases}
    expected_ids = SMOKE_CASE_IDS if kind == "smoke" else FULL_CASE_IDS
    collection_path = next((store / "collections").glob("revision-*.json"))
    collection = json.loads(collection_path.read_bytes())
    assert [slot["case_id"] for slot in collection["slots"]] == list(expected_ids)
    assert all(slot["state"] == "invalid" for slot in collection["slots"])

    execution_paths = sorted(store.glob("attempts/*/attempt-*/execution"))
    assert len(execution_paths) == len(expected_ids)
    for execution_path in execution_paths:
        assert {path.name for path in execution_path.iterdir()} == {
            "generation_input.json",
            "generation_input.sha256",
            "candidate.json",
            "candidate.sha256",
            "routing_policy.json",
            "routing_policy.sha256",
            "routing_input_facts.json",
            "routing_input_facts.sha256",
            "route_decision.json",
            "route_decision.sha256",
            "coverage_plan.json",
            "coverage_plan.sha256",
            "work_unit_output.json",
            "work_unit_output.sha256",
            "result.json",
            "result.sha256",
            "attempt.json",
            "attempt.sha256",
        }
        input_path = execution_path / "generation_input.json"
        candidate_path = execution_path / "candidate.json"
        result_path = execution_path / "result.json"
        attempt_path = execution_path / "attempt.json"
        input_bytes = input_path.read_bytes()
        candidate_bytes = candidate_path.read_bytes()
        result_bytes = result_path.read_bytes()
        attempt_bytes = attempt_path.read_bytes()
        input_model = GenerationInputArtifact.model_validate(json.loads(input_bytes))
        candidate_model = BenchmarkNoteDocument.model_validate(json.loads(candidate_bytes))
        result_model = GenerationResultArtifact.model_validate(json.loads(result_bytes))
        attempt_model = GenerationAttemptArtifact.model_validate(json.loads(attempt_bytes))
        case = cases[input_model.case_id]
        reference = NormalizedDocument.model_validate(
            json.loads((ROOT / case.reference_path).read_bytes())
        )

        assert input_bytes == canonical_generation_lane_artifact_bytes(input_model)
        assert candidate_bytes == canonical_benchmark_note_bytes(candidate_model)
        assert validate_benchmark_note_artifact(candidate_model, reference) == candidate_model
        assert result_bytes == canonical_generation_lane_artifact_bytes(result_model)
        assert attempt_bytes == canonical_generation_lane_artifact_bytes(attempt_model)
        assert input_path.with_suffix(".sha256").read_text(encoding="ascii").split() == [
            hashlib.sha256(input_bytes).hexdigest(),
            "generation_input.json",
        ]
        assert candidate_path.with_suffix(".sha256").read_text(encoding="ascii").split() == [
            hashlib.sha256(candidate_bytes).hexdigest(),
            "candidate.json",
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
        assert candidate_model.document_id == input_model.document_id == case.case_id
        assert candidate_model.reference_document_sha256 == input_model.reference_sha256
        assert candidate_model.producer_provenance.configuration_sha256 == case.producer_configuration_sha256
        assert candidate_model.lineage.parent_artifact_sha256 == input_model.reference_sha256
        assert candidate_model.producer_provenance.processing_stage == "pre_render_generation"
        assert result_model.candidate_sha256 == hashlib.sha256(candidate_bytes).hexdigest()
        assert result_model.candidate_bytes == len(candidate_bytes)
        assert result_model.producer_configuration_sha256 == input_model.producer_configuration_sha256
        assert result_model.generation_input_sha256 == hashlib.sha256(input_bytes).hexdigest()
        assert result_model.reference_sha256 == input_model.reference_sha256
        assert attempt_model.result_sha256 == hashlib.sha256(result_bytes).hexdigest()
        assert attempt_model.candidate_sha256 == result_model.candidate_sha256
        assert attempt_model.generation_input_sha256 == result_model.generation_input_sha256
        assert result_model.status == attempt_model.status == "contract_valid"
        plan_model = json.loads((execution_path / "coverage_plan.json").read_bytes())
        work_unit_output_model = json.loads(
            (execution_path / "work_unit_output.json").read_bytes()
        )
        plan_digest = hashlib.sha256(
            (execution_path / "coverage_plan.json").read_bytes()
        ).hexdigest()
        work_unit_output_digest = hashlib.sha256(
            (execution_path / "work_unit_output.json").read_bytes()
        ).hexdigest()
        assert result_model.coverage_plan_sha256 == plan_digest
        assert result_model.work_unit_output_sha256 == work_unit_output_digest
        assert attempt_model.coverage_plan_sha256 == plan_digest
        assert attempt_model.work_unit_output_sha256 == work_unit_output_digest
        assert work_unit_output_model["attempt_ordinal"] == 1
        assert work_unit_output_model["work_unit_id"] == plan_model["work_units"][0]["work_unit_id"]
        assert not (execution_path / "coverage_closure.json").exists()
        assert not (execution_path / "coverage_closure.sha256").exists()
        assert "quality_decision" not in result_model.model_dump()
        assert "result_role" not in result_model.model_dump()
        terminal_bytes = (execution_path.parent / "terminal.json").read_bytes()
        assert terminal_bytes.find(hashlib.sha256(result_bytes).hexdigest().encode("ascii")) == -1
        assert str(ROOT).encode() not in result_bytes + attempt_bytes + terminal_bytes


def test_pre_render_note_builder_is_reference_only_and_deterministic() -> None:
    profile, _ = load_diagnostic_profile(*_profile_paths("full"), ROOT)

    for case in profile.cases:
        first = build_pre_render_note(case, ROOT)
        second = build_pre_render_note(case, ROOT)
        first_bytes = canonical_benchmark_note_bytes(first)
        assert first_bytes == canonical_benchmark_note_bytes(second)
        assert first.artifact_role == "pre_render_note"
        assert first.producer_provenance.producer_role.value == "generator"
        assert first.producer_provenance.processing_stage == "pre_render_generation"
        assert first.lineage.parent_artifact_role.value == "reference_document"
        assert first.lineage.parent_artifact_sha256 == case.reference_sha256
        assert first.reference_document_sha256 == case.reference_sha256
        assert validate_benchmark_note_artifact(
            first,
            NormalizedDocument.model_validate(
                json.loads((ROOT / case.reference_path).read_bytes())
            ),
        ) == first
        assert "quality_decision" not in first.model_dump()
        assert "result_role" not in first.model_dump()
        assert "gold" not in first.model_dump()

    smoke_profile, _ = load_diagnostic_profile(*_profile_paths("smoke"), ROOT)
    screenshot_notes = [
        build_pre_render_note(case, ROOT)
        for case in smoke_profile.cases
        if case.case_id == "S01"
    ]
    assert len(screenshot_notes) == 1
    assert screenshot_notes[0].nodes == ()


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
    assert main(_execute_args("smoke", output_dir, store, invocation_id="generation-resume-001")) == 2
    first_status = json.loads(capsys.readouterr().out)
    assert first_status["status"] == "invalid_input"
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
        == 2
    )
    second_status = json.loads(capsys.readouterr().out)
    assert second_status["status"] == "invalid_input"
    assert "Q28 closure dependency gap" in second_status["error"]
    assert len(tuple((store / "attempts" / "smoke-P01").glob("attempt-*/terminal.json"))) == 2
    assert len(tuple((store / "attempts" / "smoke-W01").glob("attempt-*/terminal.json"))) == 1
    second_execution = store / "attempts" / "smoke-P01" / "attempt-0002" / "execution"
    assert json.loads((second_execution / "work_unit_output.json").read_bytes())["attempt_ordinal"] == 2
    assert not (second_execution / "coverage_closure.json").exists()
    assert not (store / "attempts" / "smoke-P01" / "attempt-0001" / "execution" / "coverage_closure.json").exists()


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
