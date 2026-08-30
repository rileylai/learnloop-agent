"""Evidence-honest draft gold review packets for the 13-case full profile.

The packet is a deterministic review aid, not gold. It inventories each
reference element by identity, kind, and content digest so a human reviewer can
decide claim boundaries, importance, and applicability without this generator
asserting those governance decisions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Annotated, Literal, Mapping, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator, model_validator

from .full_profile import FullCase, FullProfile
from .normalized_document import NormalizedDocument, canonical_normalized_document_bytes


GOLD_REVIEW_PACKET_SCHEMA_VERSION: Literal[
    "benchmark-gold-review-packet/1.0.0"
] = "benchmark-gold-review-packet/1.0.0"
BENCHMARK_REVISION: Literal[
    "parser-note-completeness/1.0.1"
] = "parser-note-completeness/1.0.1"

Digest = Annotated[StrictStr, Field(pattern=r"^[0-9a-f]{64}$")]
Identifier = Annotated[StrictStr, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")]


class GoldReviewPacketError(ValueError):
    """A review packet or one of its immutable inputs is invalid."""


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, allow_inf_nan=False)


class DraftClaimInventoryItem(_StrictFrozenModel):
    candidate_claim_id: Identifier
    source_element_id: Identifier
    source_element_kind: Identifier
    source_content_sha256: Digest
    claim_boundary_status: Literal["review_required"]
    importance_status: Literal["review_required"]
    applicability_status: Literal["review_required"]
    review_status: Literal["unreviewed"]


class AuthorityGateInventory(_StrictFrozenModel):
    fixture_provenance: Literal["evidence_required"]
    redistribution_rights: Literal["evidence_required"]
    privacy_review: Literal["evidence_required"]
    independent_gold_review: Literal["human_review_required"]
    separation_of_duties: Literal["human_review_required"]
    scorer_binding: Literal["blocked_pending_reviewed_gold"]
    formal_manifest: Literal["blocked_pending_authority"]


class GoldReviewPacket(_StrictFrozenModel):
    schema_version: Literal["benchmark-gold-review-packet/1.0.0"]
    artifact_role: Literal["gold_review_packet"]
    benchmark_revision: Literal["parser-note-completeness/1.0.1"]
    case_id: Identifier
    fixture_revision: Identifier
    source_sha256: Digest
    reference_document_sha256: Digest
    producer_configuration_sha256: Digest
    candidate_status: Literal["draft_candidate"]
    formal_authority: Literal[False]
    annotation_method: Literal["deterministic_reference_element_inventory"]
    authority_gates: AuthorityGateInventory
    claim_inventory: Tuple[DraftClaimInventoryItem, ...]

    @field_validator("claim_inventory", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def _validate_inventory(self) -> "GoldReviewPacket":
        claim_ids = tuple(item.candidate_claim_id for item in self.claim_inventory)
        element_ids = tuple(item.source_element_id for item in self.claim_inventory)
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("review-packet candidate claim IDs must be unique")
        if len(element_ids) != len(set(element_ids)):
            raise ValueError("review-packet source element IDs must be unique")
        return self


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_bytes(payload: Mapping[str, object]) -> bytes:
    return (
        json.dumps(
            dict(payload),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_gold_review_packet_bytes(
    payload: Union[GoldReviewPacket, Mapping[str, object]],
) -> bytes:
    model = (
        payload
        if isinstance(payload, GoldReviewPacket)
        else GoldReviewPacket.model_validate(payload)
    )
    return _canonical_json_bytes(model.model_dump(mode="json"))


def gold_review_packet_sha256(
    payload: Union[GoldReviewPacket, Mapping[str, object]],
) -> str:
    return _sha256(canonical_gold_review_packet_bytes(payload))


def _load_reference(case: FullCase, benchmark_root: Path) -> NormalizedDocument:
    reference_path = benchmark_root / case.reference_path
    digest_path = benchmark_root / case.reference_digest_path
    try:
        reference_bytes = reference_path.read_bytes()
        digest_fields = digest_path.read_text(encoding="ascii").strip().split()
        reference = NormalizedDocument.model_validate(json.loads(reference_bytes))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise GoldReviewPacketError("review-packet reference is unavailable or invalid") from exc
    if digest_fields != [case.reference_sha256, reference_path.name]:
        raise GoldReviewPacketError("review-packet reference digest record mismatch")
    if _sha256(reference_bytes) != case.reference_sha256:
        raise GoldReviewPacketError("review-packet reference digest mismatch")
    if canonical_normalized_document_bytes(reference) != reference_bytes:
        raise GoldReviewPacketError("review-packet reference is not canonical")
    return reference


def build_gold_review_packet(case: FullCase, benchmark_root: Path) -> GoldReviewPacket:
    """Build an unreviewed element inventory for one selected full-profile case."""

    reference = _load_reference(case, benchmark_root)
    inventory = tuple(
        DraftClaimInventoryItem(
            candidate_claim_id=f"{case.case_id.lower()}-claim-candidate-{index:03d}",
            source_element_id=element.element_id,
            source_element_kind=element.kind.value,
            source_content_sha256=_sha256(
                _canonical_json_bytes({"content": element.content})
            ),
            claim_boundary_status="review_required",
            importance_status="review_required",
            applicability_status="review_required",
            review_status="unreviewed",
        )
        for index, element in enumerate(reference.elements, start=1)
    )
    return GoldReviewPacket(
        schema_version=GOLD_REVIEW_PACKET_SCHEMA_VERSION,
        artifact_role="gold_review_packet",
        benchmark_revision=BENCHMARK_REVISION,
        case_id=case.case_id,
        fixture_revision=case.fixture_revision,
        source_sha256=case.source_sha256,
        reference_document_sha256=case.reference_sha256,
        producer_configuration_sha256=case.producer_configuration_sha256,
        candidate_status="draft_candidate",
        formal_authority=False,
        annotation_method="deterministic_reference_element_inventory",
        authority_gates=AuthorityGateInventory(
            fixture_provenance="evidence_required",
            redistribution_rights="evidence_required",
            privacy_review="evidence_required",
            independent_gold_review="human_review_required",
            separation_of_duties="human_review_required",
            scorer_binding="blocked_pending_reviewed_gold",
            formal_manifest="blocked_pending_authority",
        ),
        claim_inventory=inventory,
    )


def build_full_profile_review_packets(
    profile: FullProfile,
    benchmark_root: Path,
) -> Tuple[GoldReviewPacket, ...]:
    return tuple(build_gold_review_packet(case, benchmark_root) for case in profile.cases)


def _write_external_artifact(path: Path, data: bytes) -> str:
    digest = _sha256(data)
    digest_path = path.with_suffix(".sha256")
    expected_record = f"{digest}  {path.name}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or digest_path.exists():
        try:
            if path.read_bytes() == data and digest_path.read_text(encoding="ascii") == expected_record:
                return digest
        except (OSError, UnicodeError) as exc:
            raise GoldReviewPacketError("existing review packet cannot be read") from exc
        raise GoldReviewPacketError("immutable review packet already differs")
    try:
        path.write_bytes(data)
        digest_path.write_text(expected_record, encoding="ascii")
        if path.read_bytes() != data or digest_path.read_text(encoding="ascii") != expected_record:
            raise GoldReviewPacketError("review packet durable readback mismatch")
    except OSError as exc:
        raise GoldReviewPacketError("review packet write failed") from exc
    return digest


def write_full_profile_review_packets(
    profile: FullProfile,
    benchmark_root: Path,
) -> Mapping[str, str]:
    """Persist one immutable review packet beside each selected governance candidate."""

    digests: dict[str, str] = {}
    for packet in build_full_profile_review_packets(profile, benchmark_root):
        path = (
            benchmark_root
            / "governance"
            / packet.case_id
            / packet.fixture_revision
            / "gold-review-packet.json"
        )
        digests[packet.case_id] = _write_external_artifact(
            path,
            canonical_gold_review_packet_bytes(packet),
        )
    return digests


__all__ = [
    "BENCHMARK_REVISION",
    "GOLD_REVIEW_PACKET_SCHEMA_VERSION",
    "GoldReviewPacket",
    "GoldReviewPacketError",
    "build_full_profile_review_packets",
    "build_gold_review_packet",
    "canonical_gold_review_packet_bytes",
    "gold_review_packet_sha256",
    "write_full_profile_review_packets",
]
