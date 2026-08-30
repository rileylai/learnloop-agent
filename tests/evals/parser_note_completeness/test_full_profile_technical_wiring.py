from __future__ import annotations

import json
from pathlib import Path

import pytest

from .full_profile import FULL_CASE_IDS
from .runner import main


ROOT = Path(__file__).parent / "v1"
PROFILE = ROOT / "manifests" / "full" / "revision-002"


def test_full_profile_end_to_end_readiness_closes_all_diagnostic_slots(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan_dir = tmp_path / "plan"
    assert main(
        [
            "materialize-plan",
            "--profile",
            str(PROFILE / "profile.json"),
            "--profile-digest",
            str(PROFILE / "profile.sha256"),
            "--benchmark-root",
            str(ROOT),
            "--output-dir",
            str(plan_dir),
        ]
    ) == 0
    capsys.readouterr()
    store = tmp_path / "store"

    assert main(
        [
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
            str(PROFILE / "profile.json"),
            "--profile-digest",
            str(PROFILE / "profile.sha256"),
            "--store",
            str(store),
            "--invocation-id",
            "full-e2e-readiness-001",
        ]
    ) == 0
    status = json.loads(capsys.readouterr().out)
    collection = json.loads(
        next((store / "collections").glob("revision-*.json")).read_bytes()
    )

    assert status["status"] == "collection_complete"
    assert tuple(slot["case_id"] for slot in collection["slots"]) == FULL_CASE_IDS
    assert all(slot["state"] == "closed" for slot in collection["slots"])
    assert collection["membership"] == "diagnostic"
    assert collection["offline_attestation"] == "missing"
    assert "result_role" not in collection
    assert "quality_decision" not in collection
