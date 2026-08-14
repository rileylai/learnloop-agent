from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tests.evals.parser_note_completeness.runner import (
    RUNNER_VERSION,
    RunnerAttemptArtifact,
    RunnerResultArtifact,
    canonical_runner_artifact_bytes,
    main,
    validate_reference,
)
from tests.evals.parser_note_completeness.scorer import QualityFailure


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
CANDIDATE_PATH = (
    PACKAGE_ROOT / "v1" / "governance" / "W01" / "revision-001" / "candidate.json"
)


def _args(output_dir: Path, reference: Path = REFERENCE_PATH, digest: Path = DIGEST_PATH) -> list[str]:
    return [
        "validate-reference",
        "--reference",
        str(reference),
        "--digest",
        str(digest),
        "--output-dir",
        str(output_dir),
        "--attempt-id",
        "w01-attempt-001",
    ]


def _load_result(output_dir: Path) -> dict[str, Any]:
    return json.loads((output_dir / "result.json").read_bytes())


def test_w01_validation_cli_succeeds_with_exit_zero_and_status_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "attempt"

    exit_code = main(_args(output_dir))
    status = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert status["exit_code"] == 0
    assert status["status"] == "contract_valid"
    assert status["result_digest"]
    assert status["attempt_digest"]
    assert RUNNER_VERSION.startswith("parser-note-completeness-runner/")


def test_runner_artifact_models_are_strict_frozen_and_forbid_extra_fields() -> None:
    result = RunnerResultArtifact(
        schema_version="runner-result/1.0.0",
        runner_version=RUNNER_VERSION,
        artifact_type="parser_note_completeness_runner_result",
        operation="validate_reference",
        reference_sha256="a" * 64,
        reference_bytes=10,
        attempt_id="attempt-001",
        status="contract_valid",
        scorer_observation="not_run",
    )
    attempt = RunnerAttemptArtifact(
        schema_version="runner-attempt/1.0.0",
        runner_version=RUNNER_VERSION,
        artifact_type="parser_note_completeness_runner_attempt",
        operation="validate_reference",
        reference_sha256="a" * 64,
        result_sha256="b" * 64,
        attempt_id="attempt-001",
        status="contract_valid",
        scorer_observation="not_run",
    )

    assert result.model_config["frozen"] is True
    assert attempt.model_config["extra"] == "forbid"
    with pytest.raises(ValidationError):
        RunnerResultArtifact.model_validate(
            {**result.model_dump(), "unexpected": "forbidden"}
        )
    with pytest.raises(ValidationError):
        RunnerAttemptArtifact.model_validate(
            {**attempt.model_dump(), "reference_bytes": "10"}
        )
    with pytest.raises(ValidationError):
        result.status = "invalid"  # type: ignore[misc]


@pytest.mark.parametrize("argv", [[], ["unknown-command"]])
def test_argument_errors_are_single_json_exit_two(
    argv: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(argv)
    output = capsys.readouterr()

    assert exit_code == 2
    assert output.err == ""
    assert json.loads(output.out) == {
        "error": "invalid command arguments",
        "exit_code": 2,
        "status": "invalid_input",
    }


def test_digest_mismatch_is_invalid_input_exit_two(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    digest_path = tmp_path / "wrong.sha256"
    digest_path.write_text("f" * 64 + "  normalized_document.json\n", encoding="ascii")

    exit_code = main(_args(tmp_path / "attempt", digest=digest_path))
    status = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert status == {
        "error": "reference digest mismatch",
        "exit_code": 2,
        "status": "invalid_input",
    }


def test_invalid_schema_is_invalid_input_exit_two(tmp_path: Path) -> None:
    reference_path = tmp_path / "invalid.json"
    reference_bytes = b'{"artifact_role":"gold"}\n'
    reference_path.write_bytes(reference_bytes)
    digest_path = tmp_path / "invalid.sha256"
    digest_path.write_text(
        f"{hashlib.sha256(reference_bytes).hexdigest()}  invalid.json\n",
        encoding="ascii",
    )

    outcome = validate_reference(reference_path, digest_path, tmp_path / "attempt")

    assert outcome.exit_code == 2
    assert outcome.status == "invalid_input"
    assert outcome.error == "reference schema is invalid"


@pytest.mark.parametrize("missing_kind", ["reference", "digest"])
def test_missing_input_is_operational_exit_one(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    missing_kind: str,
) -> None:
    reference = REFERENCE_PATH if missing_kind == "reference" else tmp_path / "missing.json"
    digest = DIGEST_PATH if missing_kind == "digest" else tmp_path / "missing.sha256"

    exit_code = main(_args(tmp_path / "attempt", reference=reference, digest=digest))
    status = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert status["status"] == "operational_failure"


def test_output_directory_io_failure_is_operational_exit_one(tmp_path: Path) -> None:
    output_path = tmp_path / "output-file"
    output_path.write_text("not a directory", encoding="utf-8")

    outcome = validate_reference(REFERENCE_PATH, DIGEST_PATH, output_path)

    assert outcome.exit_code == 1
    assert outcome.status == "operational_failure"


def test_immutable_output_cannot_be_overwritten(tmp_path: Path) -> None:
    output_dir = tmp_path / "attempt"
    first = validate_reference(REFERENCE_PATH, DIGEST_PATH, output_dir)
    result_path = output_dir / "result.json"
    original_bytes = result_path.read_bytes()

    second = validate_reference(REFERENCE_PATH, DIGEST_PATH, output_dir)

    assert first.exit_code == 0
    assert second.exit_code == 1
    assert result_path.read_bytes() == original_bytes


def test_result_and_attempt_are_canonical_and_have_external_digests(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "attempt"
    outcome = validate_reference(REFERENCE_PATH, DIGEST_PATH, output_dir)

    for name in ("result", "attempt"):
        artifact_path = output_dir / f"{name}.json"
        digest_path = output_dir / f"{name}.sha256"
        artifact_bytes = artifact_path.read_bytes()
        payload = json.loads(artifact_bytes)
        fields = digest_path.read_text(encoding="ascii").strip().split()

        assert artifact_bytes == canonical_runner_artifact_bytes(payload)
        assert fields == [hashlib.sha256(artifact_bytes).hexdigest(), f"{name}.json"]
        assert "artifact_sha256" not in payload
        if name == "result":
            assert "result_sha256" not in payload
        else:
            assert "attempt_sha256" not in payload

    assert outcome.result_digest == _read_digest(output_dir / "result.sha256")
    assert outcome.attempt_digest == _read_digest(output_dir / "attempt.sha256")


def _read_digest(path: Path) -> str:
    return path.read_text(encoding="ascii").strip().split()[0]


def test_fixture_has_no_result_role_and_runner_has_no_authority(
    tmp_path: Path,
) -> None:
    candidate = json.loads(CANDIDATE_PATH.read_bytes())
    output_dir = tmp_path / "attempt"
    validate_reference(REFERENCE_PATH, DIGEST_PATH, output_dir)
    result = _load_result(output_dir)
    attempt = json.loads((output_dir / "attempt.json").read_bytes())

    assert "result_role" not in candidate
    forbidden_fields = {
        "authority",
        "authority_status",
        "result_role",
        "quality_decision",
        "gate_decision",
        "comparison_decision",
        "adoption_decision",
    }
    for artifact in (result, attempt):
        assert forbidden_fields.isdisjoint(artifact)
        assert artifact["operation"] == "validate_reference"


class _SuccessfulScorer:
    def evaluate(self, document: Any) -> None:
        return None


def test_successful_scorer_marks_completed_and_exits_zero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "attempt"

    exit_code = main(_args(output_dir), scorer=_SuccessfulScorer())
    status = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert status["status"] == "contract_valid"
    assert _load_result(output_dir)["scorer_observation"] == "completed"


class _QualityFailingScorer:
    def evaluate(self, document: Any) -> None:
        raise QualityFailure("stub quality failure")


class _UnexpectedScorer:
    def evaluate(self, document: Any) -> None:
        raise RuntimeError("secret scorer details")


def test_quality_failure_is_not_runner_operational_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "attempt"

    exit_code = main(_args(output_dir), scorer=_QualityFailingScorer())
    status = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert status["status"] == "contract_valid"
    assert _load_result(output_dir)["scorer_observation"] == "quality_failure"


def test_unexpected_scorer_exception_is_json_exit_one_without_result(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "attempt"

    exit_code = main(_args(output_dir), scorer=_UnexpectedScorer())
    status = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert status == {
        "error": "scorer execution failed",
        "exit_code": 1,
        "status": "operational_failure",
    }
    assert not (output_dir / "result.json").exists()
