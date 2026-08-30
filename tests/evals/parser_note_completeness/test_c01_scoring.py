from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from .c01_scoring import (
    C01ScoringContractError,
    C01ScoringOperationalError,
    score_c01_execution,
)
from .end_to_end import execute_end_to_end_case
from .q14_scoring import canonical_fixture_metric_result_bytes
from .smoke_profile import load_smoke_profile


ROOT = Path(__file__).parent / "v1"
PROFILE = ROOT / "manifests" / "smoke" / "revision-001"


def _run_c01(tmp_path: Path, name: str) -> Path:
    profile = load_smoke_profile(
        PROFILE / "profile.json",
        PROFILE / "profile.sha256",
        ROOT,
    )
    case = next(item for item in profile.cases if item.case_id == "C01")
    store = tmp_path / name
    execution_dir = store / "attempts" / "smoke-C01" / "attempt-0001" / "execution"
    execution_dir.mkdir(parents=True)
    outcome = execute_end_to_end_case(
        case,
        ROOT,
        execution_dir,
        attempt_id=f"{name}-e2e",
        attempt_ordinal=1,
        runner_plan_sha256="0" * 64,
        runner_slot_id="smoke-C01",
        runner_attempt_ordinal=1,
        runner_invocation_id=f"{name}-invocation",
        logical_run_id=f"{name}-run",
    )
    assert outcome.status == "contract_valid", outcome.error
    return execution_dir


def test_c01_scores_real_persisted_generation_and_end_to_end_artifacts(tmp_path: Path) -> None:
    execution_dir = _run_c01(tmp_path, "first")

    outcome = score_c01_execution(execution_dir, ROOT)

    assert tuple(result.fixture_id for result in outcome.results) == ("C01",) * 4
    assert tuple(result.metric_contract_ref.metric_contract_id for result in outcome.results) == (
        "c01-generation-coverage",
        "c01-generation-support",
        "c01-end_to_end-coverage",
        "c01-end_to_end-support",
    )
    generation_coverage = outcome.results[0].metric_value
    assert generation_coverage.result_kind == "coverage_state_vector"
    assert all(
        item.fully_covered.count == item.denominator_count
        and item.partially_covered.count == 0
        and item.not_covered.count == 0
        for item in generation_coverage.strata
    )
    generation_support = outcome.results[1].metric_value
    assert generation_support.result_kind == "support_state_counts"
    assert generation_support.decided_denominator_count == 3
    assert generation_support.decided_state_counts.supported.count == 3
    assert generation_support.unresolved_audit.count == 0

    for lane in ("generation", "end_to_end"):
        lane_dir = outcome.scoring_dir / "inputs" / lane
        assert (lane_dir / "generated-claim-map.json").exists()
        assert (lane_dir / "claim-to-gold.json").exists()
        assert (lane_dir / "coverage-applicability.json").exists()
        assert (lane_dir / "support-applicability.json").exists()
    assert len(tuple((outcome.scoring_dir / "results").glob("*.json"))) == 4

    gold = json.loads(
        (ROOT / "governance/C01/revision-001/gold.json").read_bytes()
    )
    assert gold["authority_status"] == "draft_candidate"
    assert gold["formal_authority"] is False


def test_c01_replaying_identical_immutable_inputs_reproduces_q14_result_digests(
    tmp_path: Path,
) -> None:
    first = score_c01_execution(_run_c01(tmp_path, "first"), ROOT)
    second = score_c01_execution(_run_c01(tmp_path, "second"), ROOT)

    assert first.result_digests == second.result_digests
    for left, right in zip(first.results, second.results):
        assert canonical_fixture_metric_result_bytes(left) == canonical_fixture_metric_result_bytes(right)
    for relative in (
        "contracts/aggregation.json",
        "contracts/registry.json",
        "contracts/scorer.json",
        "inputs/generation/generated-claim-map.json",
        "inputs/generation/claim-to-gold.json",
        "inputs/end_to_end/generated-claim-map.json",
        "inputs/end_to_end/claim-to-gold.json",
    ):
        assert (first.scoring_dir / relative).read_bytes() == (second.scoring_dir / relative).read_bytes()


def test_c01_scoring_fails_closed_on_persisted_mapping_digest_mismatch(tmp_path: Path) -> None:
    execution_dir = _run_c01(tmp_path, "tampered")
    outcome = score_c01_execution(execution_dir, ROOT)
    digest_path = outcome.scoring_dir / "inputs/generation/claim-to-gold.sha256"
    digest_path.write_text("0" * 64 + "  claim-to-gold.json\n", encoding="ascii")

    with pytest.raises((C01ScoringContractError, C01ScoringOperationalError)):
        score_c01_execution(execution_dir, ROOT)


def test_c01_scoring_fails_closed_on_claim_map_binding_mismatch(tmp_path: Path) -> None:
    execution_dir = _run_c01(tmp_path, "map-binding")
    outcome = score_c01_execution(execution_dir, ROOT)
    mapping_path = outcome.scoring_dir / "inputs/generation/claim-to-gold.json"
    payload = json.loads(mapping_path.read_bytes())
    payload["generated_claim_map_sha256"] = "0" * 64
    mapping_bytes = (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    mapping_path.write_bytes(mapping_bytes)
    mapping_path.with_suffix(".sha256").write_text(
        f"{hashlib.sha256(mapping_bytes).hexdigest()}  {mapping_path.name}\n",
        encoding="ascii",
    )

    with pytest.raises(C01ScoringContractError):
        score_c01_execution(execution_dir, ROOT)


@pytest.mark.parametrize("field", ["raw_source_sha256", "parser_output_sha256"])
def test_c01_scoring_fails_closed_on_end_to_end_lineage_mismatch(
    tmp_path: Path,
    field: str,
) -> None:
    execution_dir = _run_c01(tmp_path, f"lineage-{field}")
    result_path = execution_dir / "result.json"
    payload = json.loads(result_path.read_bytes())
    payload[field] = "0" * 64
    result_bytes = (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    result_path.write_bytes(result_bytes)
    result_path.with_suffix(".sha256").write_text(
        f"{hashlib.sha256(result_bytes).hexdigest()}  {result_path.name}\n",
        encoding="ascii",
    )

    with pytest.raises(C01ScoringContractError):
        score_c01_execution(execution_dir, ROOT)


def test_c01_fixture_result_external_digest_is_content_addressed(tmp_path: Path) -> None:
    outcome = score_c01_execution(_run_c01(tmp_path, "addressed"), ROOT)
    result_path = outcome.scoring_dir / "results/c01-generation-coverage.json"
    digest_path = result_path.with_suffix(".sha256")

    assert digest_path.read_text(encoding="ascii").strip().split() == [
        hashlib.sha256(result_path.read_bytes()).hexdigest(),
        result_path.name,
    ]
