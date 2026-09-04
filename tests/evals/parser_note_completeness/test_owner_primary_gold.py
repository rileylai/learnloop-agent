from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .owner_primary_gold import (
    OWNER_PRIMARY_REVISIONS,
    build_owner_primary_gold,
    build_owner_primary_gold_index,
    canonical_owner_primary_gold_bytes,
    canonical_owner_primary_gold_index_bytes,
)


ROOT = Path(__file__).parent / "v1"
EXPECTED_CLAIM_COUNTS = {
    "P01": 12,
    "P02": 8,
    "P03": 5,
    "P04": 6,
    "W01": 4,
    "W02": 11,
    "W03": 8,
    "Y01": 3,
    "Y02": 8,
    "C02": 6,
    "S01": 3,
    "S02": 5,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_twelve_owner_primary_gold_revisions_are_canonical_digest_bound_and_reproducible() -> None:
    assert set(OWNER_PRIMARY_REVISIONS) == set(EXPECTED_CLAIM_COUNTS)
    assert sum(EXPECTED_CLAIM_COUNTS.values()) == 79

    for case_id, governance_revision in OWNER_PRIMARY_REVISIONS.items():
        root = ROOT / "governance" / case_id / governance_revision
        path = root / "owner-primary-gold.json"
        digest_path = root / "owner-primary-gold.sha256"
        payload = json.loads(path.read_bytes())
        rebuilt = build_owner_primary_gold(case_id)

        assert canonical_owner_primary_gold_bytes(rebuilt) == path.read_bytes()
        assert digest_path.read_text(encoding="ascii").split() == [
            _sha256(path),
            path.name,
        ]
        assert payload["case_id"] == case_id
        assert payload["authority_status"] == "owner_approved_independent_review_pending"
        assert payload["independent_review"] == {
            "status": "pending",
            "reviewer": None,
            "reviewed_at": None,
        }
        assert payload["formal_authority"] is False
        assert payload["formal_baseline_ready"] is False
        assert payload["primary_proposal_sha256"] == "d4e40123dd4eb7be453b92e4767118c5e9b3b185288b410f6b618a0539ad7530"
        assert len(payload["expected_claims"]) == EXPECTED_CLAIM_COUNTS[case_id]
        assert payload["unresolved_items"] == []


def test_every_claim_has_exact_required_source_references_and_owner_rationale() -> None:
    for case_id in OWNER_PRIMARY_REVISIONS:
        artifact = build_owner_primary_gold(case_id)
        source_reference_ids = {
            reference.source_reference_id for reference in artifact.source_references
        }
        evidence_ids = {item.evidence_id for item in artifact.evidence_items}
        assert len(source_reference_ids) == len(artifact.source_references)
        assert len(evidence_ids) == len(artifact.evidence_items)
        for item in artifact.evidence_items:
            assert item.source_reference_ids
            assert set(item.source_reference_ids) <= source_reference_ids
        for claim in artifact.expected_claims:
            assert claim.evidence_id in evidence_ids
            assert claim.support_role == "required"
            assert claim.importance_rationale
            assert claim.review_status == "independent_review_pending"


def test_case_specific_duplicate_exclusion_and_speaker_decisions_are_preserved() -> None:
    w02 = build_owner_primary_gold("W02")
    assert {item.element_id for item in w02.source_exclusions} == {
        "w02-header-brand",
        "w02-navigation",
        "w02-footer",
    }
    assert {item.scope for item in w02.source_exclusions} == {
        "generation_and_end_to_end_expected_claim_denominator"
    }

    c02 = build_owner_primary_gold("C02")
    assert len(c02.duplicate_occurrences) == 1
    assert c02.duplicate_occurrences[0].element_id == "c02-message-002-quote-1"
    assert c02.duplicate_occurrences[0].canonical_expected_claim_id == "c02-expected-claim-001"
    assert c02.supplemental_owner_assertion_bindings[0].artifact_name == "owner-speaker-identity-assertions.json"

    s02 = build_owner_primary_gold("S02")
    second = next(claim for claim in s02.expected_claims if claim.expected_claim_id == "s02-expected-claim-002")
    evidence = next(item for item in s02.evidence_items if item.evidence_id == second.evidence_id)
    assert len(evidence.source_reference_ids) == 2
    assert s02.duplicate_occurrences == ()


def test_thirteen_case_gold_status_keeps_c01_and_all_successors_non_formal() -> None:
    c01_path = ROOT / "governance" / "C01" / "revision-002" / "owner-primary-annotation.json"
    c01 = json.loads(c01_path.read_bytes())
    assert c01["authority_status"] == "owner_approved_independent_review_pending"
    assert c01["formal_authority"] is False
    assert c01["independent_review"]["status"] == "pending"

    statuses = [build_owner_primary_gold(case_id).authority_status for case_id in OWNER_PRIMARY_REVISIONS]
    assert statuses == ["owner_approved_independent_review_pending"] * 12


def test_owner_primary_gold_index_binds_exactly_all_thirteen_non_formal_records() -> None:
    root = ROOT / "governance" / "owner-primary" / "revision-001"
    path = root / "manifest.json"
    index = build_owner_primary_gold_index()

    assert canonical_owner_primary_gold_index_bytes(index) == path.read_bytes()
    assert (root / "manifest.sha256").read_text(encoding="ascii").split() == [
        _sha256(path),
        "manifest.json",
    ]
    assert len(index.cases) == 13
    assert sum(item.expected_claim_count for item in index.cases) == 82
    assert index.independent_review.status == "pending"
    assert index.formal_authority is False
    assert index.formal_baseline_ready is False


def test_human_intake_matches_selected_profile_and_all_owner_primary_records() -> None:
    intake_path = Path(__file__).parents[3] / "dev_state" / "parser-note-completeness" / "human-review-intake.json"
    intake = json.loads(intake_path.read_bytes())
    profile = json.loads((ROOT / "manifests" / "full" / "revision-003" / "profile.json").read_bytes())
    intake_by_case = {item["case_id"]: item for item in intake["cases"]}

    for selected in profile["cases"]:
        recorded = intake_by_case[selected["case_id"]]
        assert recorded["fixture_revision"] == selected["fixture_revision"]
        assert recorded["source_sha256"] == selected["source_sha256"]
        assert recorded["reference_sha256"] == selected["reference_sha256"]
        assert recorded["gold_review"]["decision"] == "owner_approved_primary_annotation_independent_review_pending"
        assert recorded["q25_independence"] == {
            "decision": "pending",
            "independent_reviewer": "pending",
        }

    assert intake["owner_primary_gold_index"]["sha256"] == _sha256(
        ROOT / "governance" / "owner-primary" / "revision-001" / "manifest.json"
    )
    assert intake["formal_authority"] is False
