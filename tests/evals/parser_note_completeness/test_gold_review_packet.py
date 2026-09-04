from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from .full_profile import FULL_CASE_IDS, load_full_profile
from .gold_review_packet import (
    GoldReviewPacket,
    GoldReviewPacketError,
    build_full_profile_review_packets,
    canonical_gold_review_packet_bytes,
    gold_review_packet_sha256,
    write_full_profile_review_packets,
    build_gold_review_packet,
)


ROOT = Path(__file__).parent / "v1"
PROFILE = ROOT / "manifests" / "full" / "revision-002"


def _packets() -> tuple[GoldReviewPacket, ...]:
    profile = load_full_profile(
        PROFILE / "profile.json",
        PROFILE / "profile.sha256",
        ROOT,
    )
    return build_full_profile_review_packets(profile, ROOT)


def test_full_profile_review_packets_are_deterministic_and_evidence_honest() -> None:
    first = _packets()
    second = _packets()

    assert tuple(packet.case_id for packet in first) == FULL_CASE_IDS
    assert tuple(canonical_gold_review_packet_bytes(packet) for packet in first) == tuple(
        canonical_gold_review_packet_bytes(packet) for packet in second
    )
    assert tuple(gold_review_packet_sha256(packet) for packet in first) == tuple(
        gold_review_packet_sha256(packet) for packet in second
    )
    for packet in first:
        assert packet.candidate_status == "draft_candidate"
        assert packet.formal_authority is False
        assert packet.authority_gates.independent_gold_review == "human_review_required"
        assert packet.authority_gates.scorer_binding == "blocked_pending_reviewed_gold"
        assert packet.claim_inventory
        assert all(item.importance_status == "review_required" for item in packet.claim_inventory)
        assert all(item.applicability_status == "review_required" for item in packet.claim_inventory)
        assert all(
            "content" not in item.model_dump(mode="json")
            for item in packet.claim_inventory
        )
        governance_root = ROOT / "governance" / packet.case_id / packet.fixture_revision
        candidate = json.loads((governance_root / "candidate.json").read_bytes())
        assert candidate["artifacts"]["gold_review_packet"] == "gold-review-packet.json"
        packet_path = governance_root / "gold-review-packet.json"
        assert packet_path.read_bytes() == canonical_gold_review_packet_bytes(packet)
        assert (governance_root / "gold-review-packet.sha256").read_text(
            encoding="ascii"
        ).split() == [
            hashlib.sha256(packet_path.read_bytes()).hexdigest(),
            packet_path.name,
        ]


def test_review_packet_canonical_round_trip_and_strict_schema() -> None:
    packet = _packets()[0]
    canonical = canonical_gold_review_packet_bytes(packet)

    assert canonical_gold_review_packet_bytes(json.loads(canonical)) == canonical
    with pytest.raises(ValueError):
        GoldReviewPacket.model_validate({**json.loads(canonical), "formal_authority": True})
    with pytest.raises(ValueError):
        GoldReviewPacket.model_validate({**json.loads(canonical), "unexpected": True})


def test_review_packet_fails_closed_on_reference_digest_mismatch(tmp_path: Path) -> None:
    profile = load_full_profile(
        PROFILE / "profile.json",
        PROFILE / "profile.sha256",
        ROOT,
    )
    case = profile.cases[0]
    copied_root = tmp_path / "v1"
    reference_path = copied_root / case.reference_path
    digest_path = copied_root / case.reference_digest_path
    reference_path.parent.mkdir(parents=True)
    reference_path.write_bytes((ROOT / case.reference_path).read_bytes())
    digest_path.write_text("0" * 64 + f"  {reference_path.name}\n", encoding="ascii")

    from .gold_review_packet import build_gold_review_packet

    with pytest.raises(GoldReviewPacketError, match="digest record mismatch"):
        build_gold_review_packet(case, copied_root)


def test_review_packet_writer_is_immutable_and_idempotent(tmp_path: Path) -> None:
    profile = load_full_profile(
        PROFILE / "profile.json",
        PROFILE / "profile.sha256",
        ROOT,
    )
    copied_root = tmp_path / "v1"
    for case in profile.cases:
        for relative_path in (case.reference_path, case.reference_digest_path):
            source = ROOT / relative_path
            target = copied_root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())

    first = write_full_profile_review_packets(profile, copied_root)
    second = write_full_profile_review_packets(profile, copied_root)

    assert first == second
    assert tuple(first) == FULL_CASE_IDS
    tampered_path = copied_root / "governance/P01/revision-001/gold-review-packet.json"
    tampered_path.write_bytes(b"{}\n")
    with pytest.raises(GoldReviewPacketError, match="already differs"):
        write_full_profile_review_packets(profile, copied_root)


def test_successor_review_packets_bind_benchmark_102_and_remain_non_authoritative() -> None:
    profile_root = ROOT / "manifests" / "full" / "revision-003"
    profile = load_full_profile(profile_root / "profile.json", profile_root / "profile.sha256", ROOT)
    successor_ids = {"P02", "P03", "P04", "W02", "W03"}
    for case in profile.cases:
        if case.case_id not in successor_ids:
            continue
        packet = build_gold_review_packet(
            case,
            ROOT,
            benchmark_revision="parser-note-completeness/1.0.2",
        )
        packet_path = ROOT / "governance" / case.case_id / case.fixture_revision / "gold-review-packet.json"
        assert packet.benchmark_revision == "parser-note-completeness/1.0.2"
        assert packet.formal_authority is False
        assert packet_path.read_bytes() == canonical_gold_review_packet_bytes(packet)
