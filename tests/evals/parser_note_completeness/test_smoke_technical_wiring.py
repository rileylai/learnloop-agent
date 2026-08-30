from __future__ import annotations

import json
from pathlib import Path

from .c01_scoring import score_c01_execution
from .end_to_end import execute_end_to_end_case
from .gold_review_packet import GoldReviewPacket, canonical_gold_review_packet_bytes
from .smoke_profile import SMOKE_CASE_IDS, load_smoke_profile


ROOT = Path(__file__).parent / "v1"
PROFILE = ROOT / "manifests" / "smoke" / "revision-001"


def _execute_smoke(tmp_path: Path, run_name: str) -> dict[str, Path]:
    profile = load_smoke_profile(
        PROFILE / "profile.json",
        PROFILE / "profile.sha256",
        ROOT,
    )
    execution_dirs: dict[str, Path] = {}
    for case in profile.cases:
        execution_dir = (
            tmp_path
            / run_name
            / "attempts"
            / f"smoke-{case.case_id}"
            / "attempt-0001"
            / "execution"
        )
        execution_dir.mkdir(parents=True)
        outcome = execute_end_to_end_case(
            case,
            ROOT,
            execution_dir,
            attempt_id=f"{run_name}-{case.case_id}-e2e",
            attempt_ordinal=1,
            runner_plan_sha256="0" * 64,
            runner_slot_id=f"smoke-{case.case_id}",
            runner_attempt_ordinal=1,
            runner_invocation_id=f"{run_name}-invocation",
            logical_run_id=f"{run_name}-logical-run",
        )
        assert outcome.status == "contract_valid", outcome.error
        execution_dirs[case.case_id] = execution_dir
    return execution_dirs


def _artifact_digest(execution_dir: Path, relative_path: str) -> str:
    fields = (execution_dir / relative_path).with_suffix(".sha256").read_text(
        encoding="ascii"
    ).split()
    return fields[0]


def test_exact_five_case_smoke_replays_all_lanes_and_stays_diagnostic(
    tmp_path: Path,
) -> None:
    first = _execute_smoke(tmp_path, "first")
    second = _execute_smoke(tmp_path, "second")

    assert tuple(first) == SMOKE_CASE_IDS
    for case_id in SMOKE_CASE_IDS:
        for relative_path in (
            "parser/candidate.json",
            "generation/candidate.json",
            "rendered-note-projection.json",
        ):
            assert _artifact_digest(first[case_id], relative_path) == _artifact_digest(
                second[case_id], relative_path
            ), (case_id, relative_path)
        result = json.loads((first[case_id] / "result.json").read_bytes())
        assert result["execution_identity"]["membership"] == "diagnostic"
        assert "formal_authority" not in result
        assert "quality_decision" not in result

        packet_path = next(
            (ROOT / "governance" / case_id).glob(
                "revision-*/gold-review-packet.json"
            )
        )
        packet = GoldReviewPacket.model_validate(json.loads(packet_path.read_bytes()))
        assert packet_path.read_bytes() == canonical_gold_review_packet_bytes(packet)
        assert packet.formal_authority is False
        assert packet.authority_gates.scorer_binding == "blocked_pending_reviewed_gold"

    c01_first = score_c01_execution(first["C01"], ROOT)
    c01_second = score_c01_execution(second["C01"], ROOT)
    assert c01_first.result_digests == c01_second.result_digests
    assert len(c01_first.results) == 4
