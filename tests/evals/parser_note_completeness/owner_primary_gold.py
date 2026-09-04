"""Deterministic owner-primary Gold artifacts for the approved 12-case batch.

The case specifications below are a direct machine-readable realization of the
owner-approved proposal digest.  They grant no independent or formal authority.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, Literal, Mapping, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, StrictStr, model_validator

from .normalized_document import NormalizedDocument


V1_ROOT = Path(__file__).parent / "v1"
PROPOSAL_SHA256 = "d4e40123dd4eb7be453b92e4767118c5e9b3b185288b410f6b618a0539ad7530"
PROFILE_SHA256 = "45a00105debf8b452bdc18f045fe48a2e75fd2ebaeb94f20a71c1ca877187039"
BENCHMARK_MANIFEST_SHA256 = "bf6a50e131d6f2b922717f25efafb1452d2de8a94b5180a3af424cfa5693811f"
DECISION_REFERENCE = "dev_state/parser-note-completeness/human-review-intake.json#remaining-primary-gold-decision-2026-09-01-001"
ASSIGNED_AT = "2026-09-01T13:44:36+08:00"
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]

Category = Literal[
    "background_context",
    "definition",
    "core_concept",
    "mechanism",
    "procedure",
    "quantitative_result",
    "condition",
    "limitation",
    "exception",
    "risk",
    "example",
    "counterpoint",
    "conclusion",
    "recommendation",
    "uncertainty",
    "contradiction",
    "open_question",
    "attribution_context",
]
Importance = Literal["critical", "major", "minor"]

ALL_CATEGORIES = (
    "background_context",
    "definition",
    "core_concept",
    "mechanism",
    "procedure",
    "quantitative_result",
    "condition",
    "limitation",
    "exception",
    "risk",
    "example",
    "counterpoint",
    "conclusion",
    "recommendation",
    "uncertainty",
    "contradiction",
    "open_question",
    "attribution_context",
)

SELECTED_FIXTURE_REVISIONS = {
    "P01": "revision-001",
    "P02": "revision-002",
    "P03": "revision-003",
    "P04": "revision-003",
    "W01": "revision-001",
    "W02": "revision-002",
    "W03": "revision-002",
    "Y01": "revision-001",
    "Y02": "revision-001",
    "C02": "revision-001",
    "S01": "revision-001",
    "S02": "revision-002",
}

OWNER_PRIMARY_REVISIONS = {
    "P01": "revision-002",
    "P02": "revision-003",
    "P03": "revision-004",
    "P04": "revision-004",
    "W01": "revision-002",
    "W02": "revision-003",
    "W03": "revision-003",
    "Y01": "revision-002",
    "Y02": "revision-002",
    "C02": "revision-003",
    "S01": "revision-002",
    "S02": "revision-003",
}


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class IndependentReview(_StrictFrozenModel):
    status: Literal["pending"] = "pending"
    reviewer: None = None
    reviewed_at: None = None


class SourceReference(_StrictFrozenModel):
    source_reference_id: StrictStr = Field(min_length=1)
    mode: Literal["whole_element"] = "whole_element"
    element_id: StrictStr = Field(min_length=1)


class EvidenceItem(_StrictFrozenModel):
    evidence_id: StrictStr = Field(min_length=1)
    source_reference_ids: Tuple[StrictStr, ...] = Field(min_length=1)
    primary_category: Category
    additional_categories: Tuple[Category, ...] = ()


class ExpectedClaim(_StrictFrozenModel):
    expected_claim_id: StrictStr = Field(min_length=1)
    evidence_id: StrictStr = Field(min_length=1)
    support_role: Literal["required"] = "required"
    importance: Importance
    importance_rationale: StrictStr = Field(min_length=1)
    review_status: Literal["independent_review_pending"] = "independent_review_pending"


class StructureAssertion(_StrictFrozenModel):
    assertion_id: StrictStr = Field(min_length=1)
    predicate: Literal[
        "canonical_document_order",
        "exact_element_contracts",
        "exact_section_contracts",
        "typed_relation_contracts",
    ]
    subject_ids: Tuple[StrictStr, ...] = Field(min_length=1)
    reference_document_sha256: Digest


class LocatorAssertion(_StrictFrozenModel):
    assertion_id: StrictStr = Field(min_length=1)
    predicate: Literal["exact_typed_locator_identity"] = "exact_typed_locator_identity"
    element_ids: Tuple[StrictStr, ...] = Field(min_length=1)
    reference_document_sha256: Digest


class SourceExclusion(_StrictFrozenModel):
    exclusion_id: StrictStr = Field(min_length=1)
    element_id: StrictStr = Field(min_length=1)
    scope: Literal["generation_and_end_to_end_expected_claim_denominator"]
    disposition: Literal["source_noise"]
    parser_measurement_disposition: Literal["retained"] = "retained"


class DuplicateOccurrence(_StrictFrozenModel):
    duplicate_id: StrictStr = Field(min_length=1)
    element_id: StrictStr = Field(min_length=1)
    canonical_expected_claim_id: StrictStr = Field(min_length=1)
    disposition: Literal["duplicate_occurrence"]
    claim_count_effect: Literal["no_new_claim"] = "no_new_claim"
    parser_measurement_disposition: Literal["retained"] = "retained"


class SupplementalOwnerAssertionBinding(_StrictFrozenModel):
    artifact_name: StrictStr = Field(min_length=1)
    sha256: Digest
    authority_status: Literal["owner_approved_independent_review_pending"]


class OwnerPrimaryGoldArtifact(_StrictFrozenModel):
    schema_version: Literal["parser-note-completeness-owner-primary-gold/1.0.0"] = "parser-note-completeness-owner-primary-gold/1.0.0"
    artifact_role: Literal["owner_primary_gold"] = "owner_primary_gold"
    authority_status: Literal["owner_approved_independent_review_pending"] = "owner_approved_independent_review_pending"
    formal_authority: Literal[False] = False
    formal_baseline_ready: Literal[False] = False
    benchmark_version: Literal["parser-note-completeness/1.0.2"] = "parser-note-completeness/1.0.2"
    benchmark_manifest_sha256: Digest = BENCHMARK_MANIFEST_SHA256
    full_profile_sha256: Digest = PROFILE_SHA256
    primary_proposal_sha256: Digest = PROPOSAL_SHA256
    case_id: StrictStr = Field(min_length=1)
    governance_revision: StrictStr = Field(pattern=r"^revision-[0-9]{3}$")
    fixture_revision: StrictStr = Field(pattern=r"^revision-[0-9]{3}$")
    source_sha256: Digest
    reference_document_sha256: Digest
    decision_reference: StrictStr = Field(min_length=1)
    assigned_by: Literal["Riley Lai"] = "Riley Lai"
    assigned_at: Literal["2026-09-01T13:44:36+08:00"] = ASSIGNED_AT
    independent_review: IndependentReview = IndependentReview()
    source_references: Tuple[SourceReference, ...]
    evidence_items: Tuple[EvidenceItem, ...]
    expected_claims: Tuple[ExpectedClaim, ...]
    category_applicability: Mapping[Category, Literal["present_and_required", "not_present"]]
    structure_assertions: Tuple[StructureAssertion, ...]
    locator_assertions: Tuple[LocatorAssertion, ...]
    source_exclusions: Tuple[SourceExclusion, ...] = ()
    duplicate_occurrences: Tuple[DuplicateOccurrence, ...] = ()
    supplemental_owner_assertion_bindings: Tuple[SupplementalOwnerAssertionBinding, ...] = ()
    unresolved_items: Tuple[StrictStr, ...] = ()

    @model_validator(mode="after")
    def _validate_internal_references(self) -> "OwnerPrimaryGoldArtifact":
        reference_ids = {item.source_reference_id for item in self.source_references}
        evidence_ids = {item.evidence_id for item in self.evidence_items}
        claim_ids = {item.expected_claim_id for item in self.expected_claims}
        if len(reference_ids) != len(self.source_references):
            raise ValueError("source reference IDs must be unique")
        if len(evidence_ids) != len(self.evidence_items):
            raise ValueError("evidence IDs must be unique")
        if len(claim_ids) != len(self.expected_claims):
            raise ValueError("expected claim IDs must be unique")
        if any(not set(item.source_reference_ids) <= reference_ids for item in self.evidence_items):
            raise ValueError("evidence cites an unknown source reference")
        if any(item.evidence_id not in evidence_ids for item in self.expected_claims):
            raise ValueError("expected claim cites unknown evidence")
        if tuple(self.category_applicability) != ALL_CATEGORIES:
            raise ValueError("category applicability must use frozen category order")
        return self


class OwnerPrimaryGoldIndexEntry(_StrictFrozenModel):
    case_id: StrictStr = Field(min_length=1)
    artifact_path: StrictStr = Field(min_length=1)
    sha256: Digest
    expected_claim_count: int = Field(ge=1)
    authority_status: Literal["owner_approved_independent_review_pending"] = "owner_approved_independent_review_pending"
    independent_review: Literal["pending"] = "pending"
    formal_authority: Literal[False] = False


class OwnerPrimaryGoldIndex(_StrictFrozenModel):
    schema_version: Literal["parser-note-completeness-owner-primary-gold-index/1.0.0"] = "parser-note-completeness-owner-primary-gold-index/1.0.0"
    artifact_role: Literal["owner_primary_gold_review_index"] = "owner_primary_gold_review_index"
    authority_status: Literal["owner_approved_independent_review_pending"] = "owner_approved_independent_review_pending"
    formal_authority: Literal[False] = False
    formal_baseline_ready: Literal[False] = False
    benchmark_version: Literal["parser-note-completeness/1.0.2"] = "parser-note-completeness/1.0.2"
    benchmark_manifest_sha256: Digest = BENCHMARK_MANIFEST_SHA256
    full_profile_sha256: Digest = PROFILE_SHA256
    owner_decision_references: Tuple[StrictStr, StrictStr] = (
        "dev_state/parser-note-completeness/human-review-intake.json#c01-primary-gold-decision-2026-08-31-001",
        DECISION_REFERENCE,
    )
    cases: Tuple[OwnerPrimaryGoldIndexEntry, ...] = Field(min_length=13, max_length=13)
    independent_review: IndependentReview = IndependentReview()

    @model_validator(mode="after")
    def _validate_case_order(self) -> "OwnerPrimaryGoldIndex":
        expected = ("P01", "P02", "P03", "P04", "W01", "W02", "W03", "Y01", "Y02", "C01", "C02", "S01", "S02")
        if tuple(item.case_id for item in self.cases) != expected:
            raise ValueError("owner-primary Gold index requires exact 13-case order")
        return self


@dataclass(frozen=True)
class ClaimSpec:
    element_ids: Tuple[str, ...]
    category: Category
    importance: Importance
    rationale: str
    additional_categories: Tuple[Category, ...] = ()


def _ids(prefix: str, start: int, end: int) -> Tuple[str, ...]:
    return tuple(f"{prefix}{index}" for index in range(start, end + 1))


def _table_cells(table: str, row: int, columns: int = 3) -> Tuple[str, ...]:
    return _ids(f"{table}-row-0-cell-", 0, columns - 1) + _ids(
        f"{table}-row-{row}-cell-", 0, columns - 1
    )


def _claim(
    element_ids: Tuple[str, ...],
    category: Category,
    importance: Importance,
    rationale: str,
    additional_categories: Tuple[Category, ...] = (),
) -> ClaimSpec:
    return ClaimSpec(element_ids, category, importance, rationale, additional_categories)


CASE_CLAIMS: Mapping[str, Tuple[ClaimSpec, ...]] = {
    "P01": (
        _claim(_ids("p01-page-1-element-", 3, 5), "procedure", "critical", "Losing stable identity, replay safety, or terminal reasons removes the principal reliable-work invariants.", ("recommendation",)),
        _claim(_ids("p01-page-2-element-", 1, 2), "definition", "critical", "A queue contract without ownership/acknowledgement or with premature success reverses the contract boundary."),
        _claim(_ids("p01-page-2-element-", 3, 5), "procedure", "critical", "Omitting payload versioning, lease rules, or post-write acknowledgement makes execution materially unsafe.", ("recommendation",)),
        _claim(_ids("p01-page-3-element-", 1, 3), "mechanism", "critical", "Omitting the transactional idempotency-key/effect relation makes safe replay meaning false.", ("condition",)),
        _claim(("p01-page-4-element-1",), "limitation", "major", "Without the bounded-observation limitation, retries may be mistaken for guaranteed success."),
        _claim(_ids("p01-page-4-element-", 2, 5), "procedure", "major", "Failure classification, visible backoff, and exhausted-work review are substantive retry controls.", ("recommendation",)),
        _claim(_ids("p01-page-5-element-", 1, 2), "condition", "critical", "Losing the no-private-payload and heartbeat-scope conditions changes privacy and ownership truth conditions.", ("risk",)),
        _claim(_ids("p01-page-5-element-", 3, 5), "procedure", "major", "Heartbeat age, queue facts, and bounded receipts are needed for useful operational visibility."),
        _claim(("p01-page-6-element-1", "p01-page-6-element-3"), "procedure", "critical", "An incorrect shutdown sequence can claim new work or lose visible open leases.", ("recommendation",)),
        _claim(("p01-page-6-element-2", "p01-page-6-element-4"), "condition", "critical", "Conflating disappearance with closure or inventing success corrupts recovery state.", ("risk",)),
        _claim(_ids("p01-page-7-element-", 1, 5), "procedure", "major", "Omitting replay/interruption/malformed-input tests leaves a substantive verification gap.", ("recommendation",)),
        _claim(_ids("p01-page-8-element-", 1, 5), "recommendation", "major", "The pre-enable checklist is the source's operational decision aid.", ("procedure",)),
    ),
    "P02": (
        _claim(_ids("p02-page-1-paragraph-", 1, 4), "background_context", "minor", "The project-owned, observable, native-text/table/vector scope improves context but is not the main quantitative content."),
        _claim(_table_cells("p02-table-1", 1), "quantitative_result", "major", "Losing stage, unit, owner, or value would make the Parse median 18 ms fact uninterpretable."),
        _claim(_table_cells("p02-table-1", 2), "quantitative_result", "major", "Losing stage, unit, owner, or value would make the Index median 42 ms fact uninterpretable."),
        _claim(_table_cells("p02-table-1", 3), "quantitative_result", "major", "Losing stage, unit, owner, or value would make the Review median 75 ms fact uninterpretable."),
        _claim(_table_cells("p02-table-2", 1), "conclusion", "major", "The PDF native/review-pending status is a distinct source-coverage result."),
        _claim(_table_cells("p02-table-2", 2), "conclusion", "major", "The Web native/review-pending status is a distinct source-coverage result."),
        _claim(_table_cells("p02-table-2", 3), "conclusion", "major", "The Scan image/review-pending status is a distinct source-coverage result."),
        _claim(_ids("p02-page-4-paragraph-", 1, 4) + ("p02-figure-1-caption", "p02-figure-2-caption"), "limitation", "major", "Omitting vector/no-external-assets or development-only scope could misrepresent provenance or authority."),
    ),
    "P03": tuple(
        _claim(
            _ids(f"p03-page-{page}-paragraph-", 1, 2),
            category,
            importance,
            rationale,
        )
        for page, category, importance, rationale in (
            (1, "mechanism", "major", "Fixed angle/noise preserving scan shape explains how the source enters the workflow."),
            (2, "condition", "critical", "Reordering paragraphs or losing region-return segmentation reverses traceability."),
            (3, "condition", "critical", "Failure/retry provenance and the distinction between noise and loss are core truth conditions."),
            (4, "procedure", "major", "Page/region review location and the no-external/private-data scope are substantive audit context."),
            (5, "mechanism", "critical", "Recovery source/order retention and deterministic bytes are the reproducibility conclusion."),
        )
    ),
    "P04": (
        _claim(_ids("p04-page-1-paragraph-", 1, 2) + _ids("p04-page-3-paragraph-", 1, 3), "mechanism", "major", "Omitting native/scanned page-boundary semantics leaves the mixed-modality design materially incomplete."),
        _claim(("p04-page-1-formula",), "core_concept", "critical", "Missing or changing F = m * a loses the source's sole formula."),
        _claim(_table_cells("p04-table-1", 1), "quantitative_result", "major", "Force = 12 N requires its measure/value/unit relation."),
        _claim(_table_cells("p04-table-1", 2), "quantitative_result", "major", "Mass = 3 kg requires its measure/value/unit relation."),
        _claim(_ids("p04-page-2-paragraph-", 1, 2), "mechanism", "major", "The deterministic skewed-scan recipe and retained region position explain page-2 modality."),
        _claim(_ids("p04-page-4-paragraph-", 1, 2), "mechanism", "major", "Bilingual scanned content and geometry-to-source recovery explain page-4 traceability."),
    ),
    "W01": (
        _claim(("w01-element-1",), "background_context", "minor", "Project-authored minimal-web scope is useful context, not the principal instruction."),
        _claim(("w01-element-2",), "recommendation", "critical", "Losing heading preservation removes one of two explicit parser requirements."),
        _claim(("w01-element-3",), "recommendation", "critical", "Losing code-block preservation removes one of two explicit parser requirements."),
        _claim(("w01-element-4",), "procedure", "major", "The exact normalization example is the concrete implementation content."),
    ),
    "W02": (
        _claim(("w02-lede", "w02-overview-paragraph"), "mechanism", "major", "The boundary-to-bilingual-context relation explains traceability."),
        _claim(("w02-overview-unordered-1",), "recommendation", "critical", "Losing heading/paragraph hierarchy reverses a principal preservation rule."),
        _claim(("w02-overview-unordered-2",), "recommendation", "major", "Locatable list items are a substantive structural requirement."),
        _claim(("w02-overview-unordered-3",), "recommendation", "major", "Distinguishing boilerplate from article body prevents source/noise conflation."),
        _claim(("w02-overview-ordered-1", "w02-overview-ordered-2"), "procedure", "critical", "Snapshot-before-reference ordering is the source's core authoring sequence."),
        _claim(_table_cells("w02-event-table", 1), "quantitative_result", "major", "Parse 18 ms and Read structure require the full row/header relation."),
        _claim(_table_cells("w02-event-table", 2), "quantitative_result", "major", "Review 42 ms and Keep context require the full row/header relation."),
        _claim(_table_cells("w02-event-table", 3), "quantitative_result", "major", "Publish 75 ms and Await decision require the full row/header relation."),
        _claim(("w02-code",), "procedure", "major", "Stable-source normalization is the concrete code procedure."),
        _claim(("w02-figure-text", "w02-figure-caption"), "procedure", "critical", "Losing Input to Normalize to Review reverses or erases the workflow."),
        _claim(("w02-aside",), "limitation", "major", "Development-only, non-adoption scope is necessary authority context."),
    ),
    "W03": (
        _claim(("w03-intro",), "definition", "critical", "Browser/network independence defines the offline snapshot."),
        _claim(("w03-overview-paragraph",), "mechanism", "major", "Nested-section context is the principal hierarchy mechanism."),
        _claim(("w03-overview-item-1", "w03-overview-item-2"), "procedure", "critical", "Fixed rendered DOM and bilingual preservation are the core input rules."),
        _claim(("w03-details-paragraph",), "mechanism", "major", "One snapshot identity binding table and figure is material traceability context."),
        _claim(_table_cells("w03-snapshot-table", 1), "conclusion", "major", "Rendered=yes with fixed DOM is a distinct snapshot state."),
        _claim(_table_cells("w03-snapshot-table", 2), "limitation", "critical", "Network=no/offline build is a defining no-network condition."),
        _claim(("w03-figure-text", "w03-figure-caption"), "procedure", "critical", "Snapshot to Structure to Reference is the source's core relationship."),
        _claim(("w03-conclusion-paragraph",), "conclusion", "critical", "Fixed-byte provenance is the reproducibility conclusion."),
    ),
    "Y01": (
        _claim(_ids("y01-chapter-1-cue-", 0, 2), "procedure", "critical", "Contract ownership, lease, acknowledgement, and before-code timing form one principal prerequisite."),
        _claim(_ids("y01-chapter-2-cue-", 3, 5), "mechanism", "critical", "Persisting the idempotency key with the durable effect is necessary for a retry to observe the first result."),
        _claim(_ids("y01-chapter-3-cue-", 6, 8), "procedure", "critical", "Heartbeat visibility, shutdown preservation, and recovery reconciliation form the core recovery sequence."),
    ),
    "Y02": (
        _claim(("y02-chapter-1-cue-0",), "recommendation", "critical", "Contract-before-implementation is the principal process prerequisite."),
        _claim(("y02-chapter-1-cue-1",), "mechanism", "major", "Shared bilingual cue identity is substantive caption structure."),
        _claim(("y02-chapter-2-cue-2",), "condition", "critical", "Traceable timing boundaries are necessary for locator correctness."),
        _claim(("y02-chapter-2-cue-3",), "limitation", "critical", "Chapters must not be misrepresented as platform identity."),
        _claim(("y02-chapter-2-cue-4",), "mechanism", "critical", "Same-byte offline reproduction is the reproducibility mechanism."),
        _claim(("y02-chapter-3-cue-5",), "background_context", "minor", "Project ownership is provenance context rather than the main process."),
        _claim(("y02-chapter-3-cue-6",), "procedure", "critical", "Cue order and millisecond ranges are the required preservation rule."),
        _claim(("y02-chapter-3-cue-7",), "limitation", "major", "Development-only scope prevents authority overstatement."),
    ),
    "C02": (
        _claim(("c02-message-001-element", "c02-message-002-quote-1"), "recommendation", "critical", "Parser-contract-before-implementation is the principal prerequisite; the quote is supporting recurrence, not a new claim."),
        _claim(("c02-message-002-element",), "recommendation", "major", "Keeping the source binding is a substantive evidence-integrity step."),
        _claim(("c02-message-003-element", "c02-message-003-code-1"), "procedure", "critical", "Fixed-byte SHA-256 verification is the concrete integrity procedure."),
        _claim(("c02-message-004-element",), "condition", "critical", "Review that changes the contract would invalidate the stated governance boundary."),
        _claim(("c02-message-005-element",), "recommendation", "major", "Preserving bilingual order is a substantive content-order rule."),
        _claim(("c02-message-006-element",), "conclusion", "major", "Follow-up thread independence is a distinct source-structure conclusion."),
    ),
    "S01": (
        _claim(("s01-element-0",), "background_context", "minor", "Board identity is navigation/context."),
        _claim(("s01-element-1",), "conclusion", "major", "Parser lane ready is the principal displayed status."),
        _claim(("s01-element-2",), "limitation", "major", "No external assets is material provenance scope."),
    ),
    "S02": (
        _claim(("s02-element-0",), "background_context", "minor", "Screen-one identity provides sequence context."),
        _claim(("s02-element-1", "s02-element-4"), "core_concept", "major", "Shared content across both images is the intended overlap fact; recurrence forms one claim."),
        _claim(("s02-element-2",), "condition", "major", "The overlay badge is a distinct visible region/overlap condition."),
        _claim(("s02-element-3",), "background_context", "minor", "Screen-two identity provides sequence context."),
        _claim(("s02-element-5",), "conclusion", "major", "Follow-up state is the final displayed status."),
    ),
}


def _load_profile_bindings() -> dict[str, dict[str, str]]:
    path = V1_ROOT / "manifests" / "full" / "revision-003" / "profile.json"
    payload = json.loads(path.read_bytes())
    return {item["case_id"]: item for item in payload["cases"]}


def _load_reference(case_id: str) -> NormalizedDocument:
    revision = SELECTED_FIXTURE_REVISIONS[case_id]
    path = V1_ROOT / "reference_documents" / case_id / revision / "normalized_document.json"
    return NormalizedDocument.model_validate_json(path.read_bytes())


def build_owner_primary_gold(case_id: str) -> OwnerPrimaryGoldArtifact:
    if case_id not in CASE_CLAIMS:
        raise ValueError("case is outside the owner-approved 12-case batch")
    reference = _load_reference(case_id)
    profile = _load_profile_bindings()[case_id]
    elements_by_id = {element.element_id: element for element in reference.elements}
    claim_specs = CASE_CLAIMS[case_id]
    required_ids = {element_id for claim in claim_specs for element_id in claim.element_ids}
    unknown = required_ids - set(elements_by_id)
    if unknown:
        raise ValueError(f"approved proposal cites unknown elements: {sorted(unknown)}")

    ordered_required_ids = tuple(
        element.element_id for element in reference.elements if element.element_id in required_ids
    )
    prefix = case_id.lower()
    source_references = tuple(
        SourceReference(
            source_reference_id=f"{prefix}-source-ref-{index:03d}",
            element_id=element_id,
        )
        for index, element_id in enumerate(ordered_required_ids, start=1)
    )
    reference_id_by_element = {
        item.element_id: item.source_reference_id for item in source_references
    }

    evidence_items = []
    expected_claims = []
    for index, claim in enumerate(claim_specs, start=1):
        evidence_id = f"{prefix}-evidence-{index:03d}"
        expected_claim_id = f"{prefix}-expected-claim-{index:03d}"
        evidence_items.append(
            EvidenceItem(
                evidence_id=evidence_id,
                source_reference_ids=tuple(reference_id_by_element[element_id] for element_id in claim.element_ids),
                primary_category=claim.category,
                additional_categories=claim.additional_categories,
            )
        )
        expected_claims.append(
            ExpectedClaim(
                expected_claim_id=expected_claim_id,
                evidence_id=evidence_id,
                importance=claim.importance,
                importance_rationale=claim.rationale,
            )
        )

    present_categories = {
        category
        for claim in claim_specs
        for category in (claim.category, *claim.additional_categories)
    }
    all_element_ids = tuple(element.element_id for element in reference.elements)
    typed_relation_ids = tuple(
        element.element_id
        for element in reference.elements
        if element.parent_element_id is not None
        or element.list_metadata is not None
        or element.table_cell_metadata is not None
        or element.code_metadata is not None
        or element.kind.value
        in {"table", "table_row", "figure", "caption", "formula", "transcript_segment", "message", "ui_text"}
    )
    structure_assertions = (
        StructureAssertion(
            assertion_id=f"{prefix}-structure-document-order",
            predicate="canonical_document_order",
            subject_ids=all_element_ids,
            reference_document_sha256=profile["reference_sha256"],
        ),
        StructureAssertion(
            assertion_id=f"{prefix}-structure-element-contracts",
            predicate="exact_element_contracts",
            subject_ids=all_element_ids,
            reference_document_sha256=profile["reference_sha256"],
        ),
        StructureAssertion(
            assertion_id=f"{prefix}-structure-section-contracts",
            predicate="exact_section_contracts",
            subject_ids=tuple(section.section_id for section in reference.sections),
            reference_document_sha256=profile["reference_sha256"],
        ),
    ) + (
        (
            StructureAssertion(
                assertion_id=f"{prefix}-structure-typed-relations",
                predicate="typed_relation_contracts",
                subject_ids=typed_relation_ids,
                reference_document_sha256=profile["reference_sha256"],
            ),
        )
        if typed_relation_ids
        else ()
    )

    exclusions: tuple[SourceExclusion, ...] = ()
    if case_id == "W02":
        exclusions = tuple(
            SourceExclusion(
                exclusion_id=f"w02-exclusion-{index:03d}",
                element_id=element_id,
                scope="generation_and_end_to_end_expected_claim_denominator",
                disposition="source_noise",
            )
            for index, element_id in enumerate(
                ("w02-header-brand", "w02-navigation", "w02-footer"), start=1
            )
        )

    duplicates: tuple[DuplicateOccurrence, ...] = ()
    supplemental: tuple[SupplementalOwnerAssertionBinding, ...] = ()
    if case_id == "C02":
        duplicates = (
            DuplicateOccurrence(
                duplicate_id="c02-duplicate-occurrence-001",
                element_id="c02-message-002-quote-1",
                canonical_expected_claim_id="c02-expected-claim-001",
                disposition="duplicate_occurrence",
            ),
        )
        supplemental = (
            SupplementalOwnerAssertionBinding(
                artifact_name="owner-speaker-identity-assertions.json",
                sha256="bfabff5fa7bf9ce6ae5380065151b08a5c5b8da1e7f845d2cd74ed149e7ab424",
                authority_status="owner_approved_independent_review_pending",
            ),
        )

    return OwnerPrimaryGoldArtifact(
        case_id=case_id,
        governance_revision=OWNER_PRIMARY_REVISIONS[case_id],
        fixture_revision=SELECTED_FIXTURE_REVISIONS[case_id],
        source_sha256=profile["source_sha256"],
        reference_document_sha256=profile["reference_sha256"],
        decision_reference=DECISION_REFERENCE,
        source_references=source_references,
        evidence_items=tuple(evidence_items),
        expected_claims=tuple(expected_claims),
        category_applicability={
            category: "present_and_required" if category in present_categories else "not_present"
            for category in ALL_CATEGORIES
        },
        structure_assertions=structure_assertions,
        locator_assertions=(
            LocatorAssertion(
                assertion_id=f"{prefix}-locator-exact-identity",
                element_ids=all_element_ids,
                reference_document_sha256=profile["reference_sha256"],
            ),
        ),
        source_exclusions=exclusions,
        duplicate_occurrences=duplicates,
        supplemental_owner_assertion_bindings=supplemental,
    )


def canonical_owner_primary_gold_bytes(
    payload: OwnerPrimaryGoldArtifact | Mapping[str, Any],
) -> bytes:
    model = payload if isinstance(payload, OwnerPrimaryGoldArtifact) else OwnerPrimaryGoldArtifact.model_validate(payload)
    return (
        json.dumps(
            model.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def write_owner_primary_gold(case_id: str) -> Path:
    artifact = build_owner_primary_gold(case_id)
    data = canonical_owner_primary_gold_bytes(artifact)
    root = V1_ROOT / "governance" / case_id / OWNER_PRIMARY_REVISIONS[case_id]
    root.mkdir(parents=True, exist_ok=False)
    path = root / "owner-primary-gold.json"
    path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    (root / "owner-primary-gold.sha256").write_text(
        f"{digest}  owner-primary-gold.json\n",
        encoding="ascii",
    )
    return path


def write_all_owner_primary_gold() -> Tuple[Path, ...]:
    return tuple(write_owner_primary_gold(case_id) for case_id in OWNER_PRIMARY_REVISIONS)


def build_owner_primary_gold_index() -> OwnerPrimaryGoldIndex:
    case_order = ("P01", "P02", "P03", "P04", "W01", "W02", "W03", "Y01", "Y02", "C01", "C02", "S01", "S02")
    entries = []
    for case_id in case_order:
        if case_id == "C01":
            path = V1_ROOT / "governance" / "C01" / "revision-002" / "owner-primary-annotation.json"
            artifact_path = "../../C01/revision-002/owner-primary-annotation.json"
        else:
            revision = OWNER_PRIMARY_REVISIONS[case_id]
            path = V1_ROOT / "governance" / case_id / revision / "owner-primary-gold.json"
            artifact_path = f"../../{case_id}/{revision}/owner-primary-gold.json"
        payload = json.loads(path.read_bytes())
        entries.append(
            OwnerPrimaryGoldIndexEntry(
                case_id=case_id,
                artifact_path=artifact_path,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                expected_claim_count=len(payload["expected_claims"]),
            )
        )
    return OwnerPrimaryGoldIndex(cases=tuple(entries))


def canonical_owner_primary_gold_index_bytes(
    payload: OwnerPrimaryGoldIndex | Mapping[str, Any],
) -> bytes:
    model = payload if isinstance(payload, OwnerPrimaryGoldIndex) else OwnerPrimaryGoldIndex.model_validate(payload)
    return (
        json.dumps(
            model.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def write_owner_primary_gold_index() -> Path:
    data = canonical_owner_primary_gold_index_bytes(build_owner_primary_gold_index())
    root = V1_ROOT / "governance" / "owner-primary" / "revision-001"
    root.mkdir(parents=True, exist_ok=False)
    path = root / "manifest.json"
    path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    (root / "manifest.sha256").write_text(
        f"{digest}  manifest.json\n",
        encoding="ascii",
    )
    return path


__all__ = [
    "OWNER_PRIMARY_REVISIONS",
    "OwnerPrimaryGoldArtifact",
    "build_owner_primary_gold",
    "build_owner_primary_gold_index",
    "canonical_owner_primary_gold_bytes",
    "canonical_owner_primary_gold_index_bytes",
    "write_all_owner_primary_gold",
    "write_owner_primary_gold_index",
]
