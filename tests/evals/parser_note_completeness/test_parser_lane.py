from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Tuple

import pytest

from tests.evals.parser_note_completeness.diagnostic import load_diagnostic_profile
from tests.evals.parser_note_completeness.full_profile import FULL_CASE_IDS
from tests.evals.parser_note_completeness.normalized_document import (
    ArtifactRole,
    CapabilityStatus,
    NormalizedDocument,
    SourceType,
    canonical_normalized_document_bytes,
)
from tests.evals.parser_note_completeness.parser_lane import (
    ParserLaneOutcome,
    ParserLaneResultArtifact,
    build_parser_candidate,
    canonical_parser_lane_artifact_bytes,
)
from tests.evals.parser_note_completeness.runner import main
from tests.evals.parser_note_completeness.smoke_profile import SMOKE_CASE_IDS


ROOT = Path(__file__).parent / "v1"
PROFILE_ROOTS = {
    "smoke": ROOT / "manifests" / "smoke" / "revision-001",
    "full": ROOT / "manifests" / "full" / "revision-001",
}
EXPECTED_SOURCE_TYPES = {
    "P01": SourceType.PDF,
    "P02": SourceType.PDF,
    "P03": SourceType.PDF,
    "P04": SourceType.PDF,
    "W01": SourceType.WEB,
    "W02": SourceType.WEB,
    "W03": SourceType.WEB,
    "Y01": SourceType.YOUTUBE,
    "Y02": SourceType.YOUTUBE,
    "C01": SourceType.CHAT,
    "C02": SourceType.CHAT,
    "S01": SourceType.SCREENSHOTS,
    "S02": SourceType.SCREENSHOTS,
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
        "parser",
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


def test_parser_candidates_cover_fixed_case_order_source_and_provenance_bindings() -> None:
    profile_path, digest_path = _profile_paths("full")
    profile, _ = load_diagnostic_profile(profile_path, digest_path, ROOT)

    assert tuple(case.case_id for case in profile.cases) == FULL_CASE_IDS
    for case in profile.cases:
        document, source_digest, configuration_digest, unavailable = build_parser_candidate(
            case,
            ROOT,
        )
        candidate_bytes = canonical_normalized_document_bytes(document)
        repeated_document, _, _, _ = build_parser_candidate(case, ROOT)
        assert candidate_bytes == canonical_normalized_document_bytes(repeated_document)
        assert hashlib.sha256(candidate_bytes).hexdigest() == hashlib.sha256(
            canonical_normalized_document_bytes(repeated_document)
        ).hexdigest()

        assert document.artifact_role == ArtifactRole.PARSER_OUTPUT
        assert document.document_id == case.case_id
        assert document.source.source_type == EXPECTED_SOURCE_TYPES[case.case_id]
        assert document.source.source_snapshot_sha256 == source_digest == case.source_sha256
        assert (
            document.producer_provenance.configuration_sha256
            == configuration_digest
            == case.producer_configuration_sha256
        )
        assert candidate_bytes == canonical_normalized_document_bytes(
            NormalizedDocument.model_validate(json.loads(candidate_bytes))
        )
        assert tuple(unavailable) == tuple(
            name
            for name in (
                "hierarchy",
                "language_identification",
                "geometry",
                "table_structure",
                "code_metadata",
                "source_modality",
                "typed_locators",
            )
            if getattr(document.capabilities, name).status
            in {CapabilityStatus.PARTIAL, CapabilityStatus.UNAVAILABLE}
        )


def test_parser_lane_full_execution_writes_content_addressed_candidates_and_receipts(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "plan"
    store = tmp_path / "store"
    _materialize("full", output_dir, capsys)

    assert main(_execute_args("full", output_dir, store, invocation_id="parser-full-001")) == 0
    status = json.loads(capsys.readouterr().out)
    plan = json.loads((output_dir / "run_plan.json").read_bytes())
    collection_path = next((store / "collections").glob("revision-*.json"))
    collection = json.loads(collection_path.read_bytes())

    assert status["status"] == "collection_complete"
    assert [slot["case_id"] for slot in collection["slots"]] == list(FULL_CASE_IDS)
    assert all(slot["state"] == "closed" for slot in collection["slots"])

    profile, _ = load_diagnostic_profile(*_profile_paths("full"), ROOT)
    cases = {case.case_id: case for case in profile.cases}
    candidate_paths = sorted(store.glob("attempts/*/attempt-*/execution/candidate.json"))
    assert len(candidate_paths) == len(FULL_CASE_IDS)
    for candidate_path in candidate_paths:
        candidate_bytes = candidate_path.read_bytes()
        candidate = NormalizedDocument.model_validate(json.loads(candidate_bytes))
        candidate_digest = hashlib.sha256(candidate_bytes).hexdigest()
        candidate_digest_record = candidate_path.with_suffix(".sha256").read_text(encoding="ascii").split()
        result_path = candidate_path.with_name("result.json")
        result = ParserLaneResultArtifact.model_validate(json.loads(result_path.read_bytes()))
        result_bytes = result_path.read_bytes()
        terminal_path = candidate_path.parents[1] / "terminal.json"
        terminal = json.loads(terminal_path.read_bytes())
        case = cases[candidate.document_id]

        assert candidate_bytes == canonical_normalized_document_bytes(candidate)
        assert candidate_digest_record == [candidate_digest, "candidate.json"]
        assert result_bytes == canonical_parser_lane_artifact_bytes(result)
        assert result.candidate_sha256 == candidate_digest
        assert result.source_sha256 == case.source_sha256
        assert result.producer_configuration_sha256 == case.producer_configuration_sha256
        assert terminal["result_sha256"] == hashlib.sha256(result_bytes).hexdigest()
        assert str(ROOT).encode() not in result_bytes + terminal_path.read_bytes()
        assert "quality_decision" not in result.model_dump()
        assert "result_role" not in result.model_dump()

    assert [slot["case_id"] for slot in plan["slots"]] == list(FULL_CASE_IDS)


@pytest.mark.parametrize(
    ("case_id", "capability", "status", "reason"),
    [
        ("P03", "geometry", CapabilityStatus.UNAVAILABLE, "pdf_geometry_not_projected"),
        ("Y02", "hierarchy", CapabilityStatus.PARTIAL, "chapter_structure_not_projected"),
        ("S02", "language_identification", CapabilityStatus.UNAVAILABLE, "ocr_not_run"),
        ("S02", "geometry", CapabilityStatus.UNAVAILABLE, "ocr_geometry_not_projected"),
    ],
)
def test_unsupported_capabilities_are_explicit_and_platform_identity_is_not_fabricated(
    case_id: str,
    capability: str,
    status: CapabilityStatus,
    reason: str,
) -> None:
    profile, _ = load_diagnostic_profile(*_profile_paths("full"), ROOT)
    case = next(case for case in profile.cases if case.case_id == case_id)
    document, _, _, _ = build_parser_candidate(case, ROOT)
    declaration = getattr(document.capabilities, capability)

    assert declaration.status == status
    assert declaration.reason == reason
    if case_id == "P03":
        assert all(element.kind.value == "page_break" for element in document.elements)

    if case_id.startswith("Y"):
        youtube_locators = [
            locator
            for element in document.elements
            for locator in element.locators
            if locator.locator_type == "youtube"
        ]
        assert youtube_locators
        assert all(locator.video_identity.status.value == "unavailable" for locator in youtube_locators)
        assert all(locator.caption_track_identity.status.value == "unavailable" for locator in youtube_locators)


def test_parser_lane_rejects_profile_plan_binding_mismatch(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "plan"
    _materialize("smoke", output_dir, capsys)
    args = _execute_args("full", output_dir, tmp_path / "store", invocation_id="mismatch-001")

    assert main(args) == 2
    status = json.loads(capsys.readouterr().out)
    assert status == {
        "error": "parser profile and run plan binding mismatch",
        "exit_code": 2,
        "status": "invalid_input",
    }
    assert not (tmp_path / "store" / "attempts").exists()


def test_parser_lane_rejects_provider_execution_without_network_or_provider_use(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "plan"
    _materialize("smoke", output_dir, capsys)
    args = _execute_args("smoke", output_dir, tmp_path / "store", invocation_id="provider-001")
    args.extend(["--provider", "forbidden-provider"])

    assert main(args) == 2
    status = json.loads(capsys.readouterr().out)
    assert status == {
        "error": "live execution or credentials are not permitted",
        "exit_code": 2,
        "status": "invalid_input",
    }


def test_parser_lane_resume_does_not_repeat_closed_slots(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tests.evals.parser_note_completeness.runner as runner_module

    output_dir = tmp_path / "plan"
    store = tmp_path / "store"
    _materialize("smoke", output_dir, capsys)
    original_execute = runner_module.execute_parser_case
    failed = {"value": False}

    def fail_once(*args: Any, **kwargs: Any) -> ParserLaneOutcome:
        case = args[0]
        if case.case_id == "P01" and not failed["value"]:
            failed["value"] = True
            return ParserLaneOutcome(1, "operational_failure", error="parser execution failed")
        return original_execute(*args, **kwargs)

    monkeypatch.setattr(runner_module, "execute_parser_case", fail_once)
    assert main(_execute_args("smoke", output_dir, store, invocation_id="parser-resume-001")) == 1
    first_status = json.loads(capsys.readouterr().out)
    assert first_status["status"] == "collection_incomplete"
    failed_terminal = json.loads(
        (store / "attempts" / "smoke-P01" / "attempt-0001" / "terminal.json").read_bytes()
    )
    incomplete_collection = json.loads(
        next((store / "collections").glob("revision-*.json")).read_bytes()
    )
    assert failed_terminal["terminal_status"] == "operational_failure"
    assert next(slot for slot in incomplete_collection["slots"] if slot["case_id"] == "P01")["state"] == "operational"

    monkeypatch.setattr(runner_module, "execute_parser_case", original_execute)
    assert main(
        _execute_args(
            "smoke",
            output_dir,
            store,
            invocation_id="parser-resume-002",
            resume=True,
        )
    ) == 0
    second_status = json.loads(capsys.readouterr().out)
    assert second_status["status"] == "collection_complete"
    assert len(tuple((store / "attempts" / "smoke-W01").glob("attempt-*/terminal.json"))) == 1
    assert len(tuple((store / "attempts" / "smoke-P01").glob("attempt-*/terminal.json"))) == 2
