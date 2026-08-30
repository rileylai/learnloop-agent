"""Small C01 real-artifact Generation/End-to-end Q14 scoring slice.

This module is deliberately benchmark-local.  It reads the immutable artifacts
produced by the existing Parser, Generation, and End-to-end lanes, materializes
the candidate-specific mapping inputs, and delegates the actual metric
calculation to the frozen Q14 scorer functions.

The C01 gold and mapping inputs are explicitly draft diagnostic artifacts.
This slice therefore proves artifact wiring and deterministic replay; it does
not create formal benchmark or adoption authority.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, Literal, Mapping, Optional, Tuple, TypeVar, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    field_validator,
    model_validator,
)

from .benchmark_note import (
    BenchmarkNoteDocument,
    RenderedNoteProjection,
    canonical_benchmark_note_bytes,
    validate_benchmark_note_artifact,
)
from .end_to_end import (
    EndToEndResultArtifact,
    canonical_end_to_end_artifact_bytes,
)
from .normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
    normalized_document_sha256,
)
from .q14_scoring import (
    AggregationContract,
    AggregationContractReference,
    ApplicabilityConsumption,
    AggregationKind,
    CanonicalUnit,
    DenominatorSemantics,
    DeterministicRequirements,
    Direction,
    FixtureMetricResult,
    FormulaKind,
    InputArtifactReference,
    InputArtifactRole,
    MetricComponent,
    MetricContract,
    MetricContractReference,
    MetricFormula,
    MetricKind,
    MetricRegistry,
    NumericRepresentation,
    OwnerRecordReference,
    Q14Lane,
    ScorerContract,
    ScoringUnit,
    build_fixture_metric_result,
    canonical_aggregation_contract_bytes,
    canonical_fixture_metric_result_bytes,
    canonical_metric_contract_bytes,
    canonical_metric_registry_bytes,
    canonical_scorer_contract_bytes,
    metric_contract_sha256,
    metric_registry_sha256,
    score_coverage_fixture,
    score_support_fixture,
    scorer_contract_sha256,
    aggregation_contract_sha256,
    validate_fixture_metric_result,
    validate_metric_contract_bindings,
    validate_metric_registry_bindings,
    validate_scorer_contract_bindings,
)
from .smoke_profile import SmokeCase, load_smoke_profile, read_external_sha256_record


C01_BENCHMARK_REVISION = "parser-note-completeness/1.0.1"
C01_FIXTURE_REVISION: Literal["revision-001"] = "revision-001"
C01_CASE_ID: Literal["C01"] = "C01"
C01_GOLD_RELATIVE_PATH = "governance/C01/revision-001/gold.json"
C01_SMOKE_PROFILE_RELATIVE_PATH = "manifests/smoke/revision-001/profile.json"
C01_SMOKE_PROFILE_DIGEST_RELATIVE_PATH = "manifests/smoke/revision-001/profile.sha256"

_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]
Identifier = Annotated[StrictStr, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]


class C01ScoringContractError(ValueError):
    """A C01 scoring artifact or cross-artifact binding is invalid."""


class C01ScoringOperationalError(Exception):
    """A C01 scoring artifact could not be read or durably written."""


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class C01GoldClaim(_StrictFrozenModel):
    expected_claim_id: Identifier
    importance: Literal["critical", "major", "minor"]
    source_element_id: Identifier


class C01GoldArtifact(_StrictFrozenModel):
    schema_version: Literal["benchmark-c01-draft-gold/1.0.0"]
    artifact_role: Literal["gold"]
    case_id: Literal["C01"]
    fixture_revision: Literal["revision-001"]
    reference_document_sha256: Digest
    authority_status: Literal["draft_candidate"]
    formal_authority: Literal[False]
    expected_claims: Tuple[C01GoldClaim, ...]

    @field_validator("expected_claims", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def _validate_claims(self) -> "C01GoldArtifact":
        ids = tuple(claim.expected_claim_id for claim in self.expected_claims)
        source_ids = tuple(claim.source_element_id for claim in self.expected_claims)
        if len(ids) != len(set(ids)) or len(source_ids) != len(set(source_ids)):
            raise ValueError("C01 draft gold claim and source IDs must be unique")
        return self


class C01ContentSpan(_StrictFrozenModel):
    path: Literal["nodes[].content"]
    start: NonNegativeInt
    end: NonNegativeInt

    @model_validator(mode="after")
    def _validate_range(self) -> "C01ContentSpan":
        if self.end <= self.start:
            raise ValueError("generated claim content span must be non-empty")
        return self


class C01GeneratedClaim(_StrictFrozenModel):
    generated_claim_id: Identifier
    candidate_node_id: Identifier
    candidate_node_order: NonNegativeInt
    content_span: C01ContentSpan
    presentation_only: Literal[False]


class C01GeneratedClaimMap(_StrictFrozenModel):
    schema_version: Literal["benchmark-generated-claim-map/1.0.0"]
    artifact_role: Literal["generated_claim_map"]
    case_id: Literal["C01"]
    fixture_revision: Literal["revision-001"]
    lane: Literal["generation", "end_to_end"]
    candidate_output_role: Literal["pre_render_note", "rendered_note_projection"]
    candidate_output_sha256: Digest
    claims: Tuple[C01GeneratedClaim, ...]

    @field_validator("claims", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def _validate_claims(self) -> "C01GeneratedClaimMap":
        ids = tuple(claim.generated_claim_id for claim in self.claims)
        nodes = tuple(claim.candidate_node_id for claim in self.claims)
        if len(ids) != len(set(ids)) or len(nodes) != len(set(nodes)):
            raise ValueError("generated claim and node IDs must be unique")
        if tuple(claim.candidate_node_order for claim in self.claims) != tuple(
            sorted(claim.candidate_node_order for claim in self.claims)
        ):
            raise ValueError("generated claims must preserve candidate order")
        return self


class C01ClaimLink(_StrictFrozenModel):
    generated_claim_id: Identifier
    expected_claim_id: Identifier
    matched_source_element_ids: Tuple[Identifier, ...]

    @field_validator("matched_source_element_ids", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class C01ExpectedCoverage(_StrictFrozenModel):
    expected_claim_id: Identifier
    coverage_state: Literal["fully_covered", "partially_covered", "not_covered"]
    contributing_generated_claim_ids: Tuple[Identifier, ...]

    @field_validator("contributing_generated_claim_ids", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class C01GeneratedSupport(_StrictFrozenModel):
    generated_claim_id: Identifier
    support_state: Literal[
        "supported",
        "partially_supported",
        "unsupported",
        "contradicted_by_source",
        "overstated",
        "unresolved",
    ]
    matched_source_element_ids: Tuple[Identifier, ...]

    @field_validator("matched_source_element_ids", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class C01ClaimToGoldArtifact(_StrictFrozenModel):
    schema_version: Literal["benchmark-claim-to-gold-match/1.0.0"]
    artifact_role: Literal["claim_to_gold_mapping"]
    case_id: Literal["C01"]
    fixture_revision: Literal["revision-001"]
    lane: Literal["generation", "end_to_end"]
    candidate_output_sha256: Digest
    generated_claim_map_sha256: Digest
    gold_sha256: Digest
    reference_document_sha256: Digest
    authority_status: Literal["draft_candidate"]
    formal_authority: Literal[False]
    claim_links: Tuple[C01ClaimLink, ...]
    expected_claim_coverage_results: Tuple[C01ExpectedCoverage, ...]
    generated_claim_support_results: Tuple[C01GeneratedSupport, ...]
    candidate_internal_contradiction_relation_ids: Tuple[Identifier, ...]

    @field_validator(
        "claim_links",
        "expected_claim_coverage_results",
        "generated_claim_support_results",
        "candidate_internal_contradiction_relation_ids",
        mode="before",
    )
    @classmethod
    def _tuples(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class C01CoverageApplicability(_StrictFrozenModel):
    schema_version: Literal["benchmark-c01-applicability-record/1.0.0"]
    artifact_role: Literal["item_disposition"]
    record_id: Identifier
    case_id: Literal["C01"]
    fixture_revision: Literal["revision-001"]
    lane: Literal["generation", "end_to_end"]
    metric_kind: Literal["coverage"]
    authority_status: Literal["draft_candidate"]
    formal_authority: Literal[False]
    authoritative_expected_claim_ids: Tuple[Identifier, ...]
    applicable_expected_claim_ids: Tuple[Identifier, ...]
    excluded_expected_claim_ids: Tuple[Identifier, ...]
    denominator_count: NonNegativeInt

    @field_validator(
        "authoritative_expected_claim_ids",
        "applicable_expected_claim_ids",
        "excluded_expected_claim_ids",
        mode="before",
    )
    @classmethod
    def _tuples(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def _validate_partition(self) -> "C01CoverageApplicability":
        authoritative = set(self.authoritative_expected_claim_ids)
        applicable = set(self.applicable_expected_claim_ids)
        excluded = set(self.excluded_expected_claim_ids)
        if len(authoritative) != len(self.authoritative_expected_claim_ids):
            raise ValueError("C01 expected claim authority must be unique")
        if applicable & excluded or authoritative != applicable | excluded:
            raise ValueError("C01 coverage applicability is not a partition")
        if self.denominator_count != len(applicable):
            raise ValueError("C01 coverage denominator does not match applicable IDs")
        return self


class C01SupportApplicability(_StrictFrozenModel):
    schema_version: Literal["benchmark-c01-applicability-record/1.0.0"]
    artifact_role: Literal["item_disposition"]
    record_id: Identifier
    case_id: Literal["C01"]
    fixture_revision: Literal["revision-001"]
    lane: Literal["generation", "end_to_end"]
    metric_kind: Literal["support"]
    authority_status: Literal["draft_candidate"]
    formal_authority: Literal[False]
    authoritative_generated_claim_ids: Tuple[Identifier, ...]
    applicable_generated_claim_ids: Tuple[Identifier, ...]
    unresolved_generated_claim_ids: Tuple[Identifier, ...]
    decided_denominator_count: NonNegativeInt

    @field_validator(
        "authoritative_generated_claim_ids",
        "applicable_generated_claim_ids",
        "unresolved_generated_claim_ids",
        mode="before",
    )
    @classmethod
    def _tuples(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def _validate_partition(self) -> "C01SupportApplicability":
        authoritative = set(self.authoritative_generated_claim_ids)
        applicable = set(self.applicable_generated_claim_ids)
        unresolved = set(self.unresolved_generated_claim_ids)
        if len(authoritative) != len(self.authoritative_generated_claim_ids):
            raise ValueError("C01 generated claim authority must be unique")
        if authoritative != applicable or not unresolved <= applicable:
            raise ValueError("C01 support applicability is not a closed disposition")
        expected_denominator = len(applicable - unresolved)
        if self.decided_denominator_count != expected_denominator:
            raise ValueError("C01 support denominator does not match decided IDs")
        return self


@dataclass(frozen=True)
class C01ScoringOutcome:
    scoring_dir: Path
    results: Tuple[FixtureMetricResult, ...]
    result_digests: Mapping[str, str]


ModelT = TypeVar("ModelT", bound=BaseModel)


def _canonical_json_bytes(model: BaseModel) -> bytes:
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


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_immutable(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = _sha256(data)
    digest_path = path.with_suffix(".sha256")
    if path.exists() or digest_path.exists():
        try:
            if path.read_bytes() == data and digest_path.read_text(encoding="ascii").strip() == f"{digest}  {path.name}":
                return digest
        except (OSError, UnicodeError) as exc:
            raise C01ScoringOperationalError("existing scoring artifact cannot be read") from exc
        raise C01ScoringOperationalError("immutable scoring artifact already differs")
    try:
        path.write_bytes(data)
        digest_path.write_text(f"{digest}  {path.name}\n", encoding="ascii")
        if path.read_bytes() != data or digest_path.read_text(encoding="ascii").strip() != f"{digest}  {path.name}":
            raise C01ScoringOperationalError("scoring artifact durable readback mismatch")
    except OSError as exc:
        raise C01ScoringOperationalError("scoring artifact write failed") from exc
    return digest


def _read_immutable(path: Path) -> tuple[bytes, str]:
    try:
        data = path.read_bytes()
        record = path.with_suffix(".sha256").read_text(encoding="ascii").strip().split()
    except (OSError, UnicodeError) as exc:
        raise C01ScoringContractError("required C01 scoring artifact is unavailable") from exc
    if len(record) != 2 or record[1] != path.name or record[0] != _sha256(data):
        raise C01ScoringContractError("C01 scoring artifact digest mismatch")
    return data, record[0]


def _load_model(
    path: Path,
    model_type: type[ModelT],
    canonicalizer: Any,
) -> tuple[ModelT, str]:
    data, digest = _read_immutable(path)
    try:
        model = model_type.model_validate(json.loads(data))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise C01ScoringContractError("C01 scoring artifact schema is invalid") from exc
    if canonicalizer(model) != data:
        raise C01ScoringContractError("C01 scoring artifact is not canonical")
    return model, digest


def _load_c01_case(benchmark_root: Path) -> SmokeCase:
    profile = load_smoke_profile(
        benchmark_root / C01_SMOKE_PROFILE_RELATIVE_PATH,
        benchmark_root / C01_SMOKE_PROFILE_DIGEST_RELATIVE_PATH,
        benchmark_root,
    )
    return next(case for case in profile.cases if case.case_id == C01_CASE_ID)


def _read_case_source(case: SmokeCase, benchmark_root: Path) -> tuple[bytes, str]:
    source_path = benchmark_root / case.source_artifact_path
    digest_path = benchmark_root / case.source_digest_path
    try:
        source = source_path.read_bytes()
        record = read_external_sha256_record(digest_path, source_path.name)
    except (OSError, ValueError) as exc:
        raise C01ScoringContractError("C01 source fixture is unavailable") from exc
    actual = _sha256(source)
    if actual != case.source_sha256 or record != case.source_sha256:
        raise C01ScoringContractError("C01 source fixture digest mismatch")
    return source, actual


def _read_reference(case: SmokeCase, benchmark_root: Path) -> tuple[NormalizedDocument, str]:
    path = benchmark_root / case.reference_path
    try:
        data = path.read_bytes()
        record = read_external_sha256_record(
            benchmark_root / case.reference_digest_path,
            path.name,
        )
        document = NormalizedDocument.model_validate(json.loads(data))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise C01ScoringContractError("C01 reference document is invalid") from exc
    digest = _sha256(data)
    if digest != case.reference_sha256 or record != digest:
        raise C01ScoringContractError("C01 reference document digest mismatch")
    if canonical_normalized_document_bytes(document) != data:
        raise C01ScoringContractError("C01 reference document is not canonical")
    return document, digest


def _read_parser_output(execution_dir: Path) -> tuple[NormalizedDocument, str]:
    path = execution_dir / "parser" / "candidate.json"
    data, digest = _read_immutable(path)
    try:
        document = NormalizedDocument.model_validate(json.loads(data))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise C01ScoringContractError("C01 Parser output is invalid") from exc
    if canonical_normalized_document_bytes(document) != data:
        raise C01ScoringContractError("C01 Parser output is not canonical")
    if normalized_document_sha256(document) != digest:
        raise C01ScoringContractError("C01 Parser output digest mismatch")
    return document, digest


def _read_end_to_end_lineage(
    execution_dir: Path,
    reference_document: NormalizedDocument,
    *,
    raw_source_digest: str,
    parser_output_digest: str,
) -> tuple[
    EndToEndResultArtifact,
    str,
    BenchmarkNoteDocument,
    str,
    RenderedNoteProjection,
    str,
]:
    result, result_digest = _load_model(
        execution_dir / "result.json",
        EndToEndResultArtifact,
        canonical_end_to_end_artifact_bytes,
    )
    note, note_digest = _load_model(
        execution_dir / "generation" / "candidate.json",
        BenchmarkNoteDocument,
        canonical_benchmark_note_bytes,
    )
    projection, projection_digest = _load_model(
        execution_dir / "rendered-note-projection.json",
        RenderedNoteProjection,
        canonical_benchmark_note_bytes,
    )
    if result.case_id != C01_CASE_ID:
        raise C01ScoringContractError("C01 scoring received a different End-to-end case")
    if result.raw_source_sha256 != raw_source_digest:
        raise C01ScoringContractError("C01 raw source is not bound by End-to-end result")
    if result.parser_output_sha256 != parser_output_digest:
        raise C01ScoringContractError("C01 Parser output is not bound by End-to-end result")
    if result.generation_output_sha256 != note_digest or result.pre_render_note_sha256 != note_digest:
        raise C01ScoringContractError("C01 pre-render note is not bound by End-to-end result")
    if result.rendered_note_projection_sha256 != projection_digest:
        raise C01ScoringContractError("C01 rendered projection is not bound by End-to-end result")
    validate_benchmark_note_artifact(note, reference_document)
    validate_benchmark_note_artifact(
        projection,
        reference_document,
        parent_artifact=note,
    )
    return result, result_digest, note, note_digest, projection, projection_digest


def _load_gold(
    benchmark_root: Path,
    reference_digest: str,
) -> tuple[C01GoldArtifact, str]:
    gold, digest = _load_model(
        benchmark_root / C01_GOLD_RELATIVE_PATH,
        C01GoldArtifact,
        _canonical_json_bytes,
    )
    if gold.reference_document_sha256 != reference_digest:
        raise C01ScoringContractError("C01 draft gold/reference binding mismatch")
    return gold, digest


def _build_generated_claim_map(
    note: Any,
    note_bytes: bytes,
    note_digest: str,
    *,
    lane: Literal["generation", "end_to_end"],
) -> C01GeneratedClaimMap:
    try:
        text = note_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise C01ScoringContractError("C01 candidate output is not UTF-8") from exc
    claims = []
    cursor = 0
    for node in note.nodes:
        if node.content is None or not node.content:
            raise C01ScoringContractError("C01 generated claim has no semantic content")
        start = text.find(node.content, cursor)
        if start < 0:
            raise C01ScoringContractError("C01 generated claim content span is unavailable")
        end = start + len(node.content)
        cursor = end
        claims.append(
            C01GeneratedClaim(
                generated_claim_id=f"c01-{lane}-generated-claim-{node.order + 1:03d}",
                candidate_node_id=node.node_id,
                candidate_node_order=node.order,
                content_span=C01ContentSpan(path="nodes[].content", start=start, end=end),
                presentation_only=False,
            )
        )
    return C01GeneratedClaimMap(
        schema_version="benchmark-generated-claim-map/1.0.0",
        artifact_role="generated_claim_map",
        case_id=C01_CASE_ID,
        fixture_revision=C01_FIXTURE_REVISION,
        lane=lane,
        candidate_output_role=(
            "pre_render_note" if lane == "generation" else "rendered_note_projection"
        ),
        candidate_output_sha256=note_digest,
        claims=tuple(claims),
    )


def _validate_generated_claim_map(
    claim_map: C01GeneratedClaimMap,
    note: Any,
    note_bytes: bytes,
    note_digest: str,
) -> None:
    if claim_map.candidate_output_sha256 != note_digest:
        raise C01ScoringContractError("C01 generated-claim map/output digest mismatch")
    try:
        text = note_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise C01ScoringContractError("C01 candidate output is not UTF-8") from exc
    nodes_by_id = {node.node_id: node for node in note.nodes}
    if len(nodes_by_id) != len(note.nodes) or len(claim_map.claims) != len(note.nodes):
        raise C01ScoringContractError("C01 generated-claim map is not exhaustive")
    for claim in claim_map.claims:
        node = nodes_by_id.get(claim.candidate_node_id)
        if node is None or node.order != claim.candidate_node_order or node.content is None:
            raise C01ScoringContractError("C01 generated-claim node binding mismatch")
        if text[claim.content_span.start : claim.content_span.end] != node.content:
            raise C01ScoringContractError("C01 generated-claim content span mismatch")


def _build_claim_to_gold(
    *,
    lane: Literal["generation", "end_to_end"],
    note: Any,
    note_digest: str,
    claim_map: C01GeneratedClaimMap,
    claim_map_digest: str,
    gold: C01GoldArtifact,
    gold_digest: str,
    reference: NormalizedDocument,
    reference_digest: str,
) -> C01ClaimToGoldArtifact:
    gold_by_source = {claim.source_element_id: claim for claim in gold.expected_claims}
    reference_by_id = {element.element_id: element for element in reference.elements}
    nodes_by_id = {node.node_id: node for node in note.nodes}
    links: list[C01ClaimLink] = []
    coverage: list[C01ExpectedCoverage] = []
    support: list[C01GeneratedSupport] = []
    generated_by_expected: dict[str, list[str]] = {claim.expected_claim_id: [] for claim in gold.expected_claims}

    for generated in claim_map.claims:
        node = nodes_by_id.get(generated.candidate_node_id)
        if node is None:
            raise C01ScoringContractError("C01 generated-claim map references an unknown node")
        cited_elements = tuple(
            citation.element_id
            for citation in node.citations
            if citation.reference_document_id == reference.document_id
        )
        if len(cited_elements) != 1 or cited_elements[0] not in gold_by_source:
            raise C01ScoringContractError(
                "C01 draft gold does not close every generated claim to one source claim"
            )
        source_element_id = cited_elements[0]
        expected = gold_by_source[source_element_id]
        source_element = reference_by_id.get(source_element_id)
        if source_element is None or node.content is None:
            raise C01ScoringContractError("C01 claim-to-gold source binding is invalid")
        generated_by_expected[expected.expected_claim_id].append(generated.generated_claim_id)
        exact = node.content == source_element.content
        links.append(
            C01ClaimLink(
                generated_claim_id=generated.generated_claim_id,
                expected_claim_id=expected.expected_claim_id,
                matched_source_element_ids=(source_element_id,),
            )
        )
        support.append(
            C01GeneratedSupport(
                generated_claim_id=generated.generated_claim_id,
                support_state="supported" if exact else "overstated",
                matched_source_element_ids=(source_element_id,),
            )
        )

    for expected in gold.expected_claims:
        generated_ids = tuple(generated_by_expected[expected.expected_claim_id])
        if not generated_ids:
            state = "not_covered"
        elif len(generated_ids) == 1:
            generated_node = nodes_by_id[
                next(
                    claim.candidate_node_id
                    for claim in claim_map.claims
                    if claim.generated_claim_id == generated_ids[0]
                )
            ]
            state = (
                "fully_covered"
                if generated_node.content == reference_by_id[expected.source_element_id].content
                else "partially_covered"
            )
        else:
            state = "partially_covered"
        coverage.append(
            C01ExpectedCoverage(
                expected_claim_id=expected.expected_claim_id,
                coverage_state=cast(
                    Literal["fully_covered", "partially_covered", "not_covered"],
                    state,
                ),
                contributing_generated_claim_ids=generated_ids,
            )
        )

    return C01ClaimToGoldArtifact(
        schema_version="benchmark-claim-to-gold-match/1.0.0",
        artifact_role="claim_to_gold_mapping",
        case_id=C01_CASE_ID,
        fixture_revision=C01_FIXTURE_REVISION,
        lane=lane,
        candidate_output_sha256=note_digest,
        generated_claim_map_sha256=claim_map_digest,
        gold_sha256=gold_digest,
        reference_document_sha256=reference_digest,
        authority_status="draft_candidate",
        formal_authority=False,
        claim_links=tuple(links),
        expected_claim_coverage_results=tuple(coverage),
        generated_claim_support_results=tuple(support),
        candidate_internal_contradiction_relation_ids=(),
    )


def _validate_claim_to_gold(
    mapping: C01ClaimToGoldArtifact,
    *,
    note: Any,
    note_digest: str,
    claim_map: C01GeneratedClaimMap,
    claim_map_digest: str,
    gold: C01GoldArtifact,
    gold_digest: str,
    reference: NormalizedDocument,
    reference_digest: str,
) -> None:
    if (
        mapping.candidate_output_sha256 != note_digest
        or mapping.generated_claim_map_sha256 != claim_map_digest
        or mapping.gold_sha256 != gold_digest
        or mapping.reference_document_sha256 != reference_digest
    ):
        raise C01ScoringContractError("C01 claim-to-gold dependency digest mismatch")
    expected_ids = tuple(claim.expected_claim_id for claim in gold.expected_claims)
    generated_ids = tuple(claim.generated_claim_id for claim in claim_map.claims)
    if tuple(item.expected_claim_id for item in mapping.expected_claim_coverage_results) != expected_ids:
        raise C01ScoringContractError("C01 coverage mapping is not gold-exhaustive")
    if tuple(item.generated_claim_id for item in mapping.generated_claim_support_results) != generated_ids:
        raise C01ScoringContractError("C01 support mapping is not map-exhaustive")
    if tuple(item.generated_claim_id for item in mapping.claim_links) != generated_ids:
        raise C01ScoringContractError("C01 claim links are not map-ordered")
    source_ids = {element.element_id for element in reference.elements}
    expected_by_id = {
        claim.expected_claim_id: claim for claim in gold.expected_claims
    }
    coverage_by_id = {
        item.expected_claim_id: item
        for item in mapping.expected_claim_coverage_results
    }
    if any(
        link.expected_claim_id not in expected_by_id
        or link.generated_claim_id not in generated_ids
        or link.generated_claim_id
        not in coverage_by_id[link.expected_claim_id].contributing_generated_claim_ids
        or link.matched_source_element_ids
        != (expected_by_id[link.expected_claim_id].source_element_id,)
        for link in mapping.claim_links
    ):
        raise C01ScoringContractError("C01 claim link is not bound to gold coverage")
    if any(
        source_id not in source_ids
        for link in mapping.claim_links
        for source_id in link.matched_source_element_ids
    ):
        raise C01ScoringContractError("C01 claim-to-gold mapping cites an unknown source element")


def _build_applicability(
    *,
    lane: Literal["generation", "end_to_end"],
    gold: C01GoldArtifact,
    claim_map: C01GeneratedClaimMap,
) -> tuple[C01CoverageApplicability, C01SupportApplicability]:
    expected_ids = tuple(claim.expected_claim_id for claim in gold.expected_claims)
    generated_ids = tuple(claim.generated_claim_id for claim in claim_map.claims)
    return (
        C01CoverageApplicability(
            schema_version="benchmark-c01-applicability-record/1.0.0",
            artifact_role="item_disposition",
            record_id=f"c01-{lane}-coverage-applicability",
            case_id=C01_CASE_ID,
            fixture_revision=C01_FIXTURE_REVISION,
            lane=lane,
            metric_kind="coverage",
            authority_status="draft_candidate",
            formal_authority=False,
            authoritative_expected_claim_ids=expected_ids,
            applicable_expected_claim_ids=expected_ids,
            excluded_expected_claim_ids=(),
            denominator_count=len(expected_ids),
        ),
        C01SupportApplicability(
            schema_version="benchmark-c01-applicability-record/1.0.0",
            artifact_role="item_disposition",
            record_id=f"c01-{lane}-support-applicability",
            case_id=C01_CASE_ID,
            fixture_revision=C01_FIXTURE_REVISION,
            lane=lane,
            metric_kind="support",
            authority_status="draft_candidate",
            formal_authority=False,
            authoritative_generated_claim_ids=generated_ids,
            applicable_generated_claim_ids=generated_ids,
            unresolved_generated_claim_ids=(),
            decided_denominator_count=len(generated_ids),
        ),
    )


def _persist_input_artifacts(
    *,
    scoring_dir: Path,
    lane: Literal["generation", "end_to_end"],
    claim_map: C01GeneratedClaimMap,
    mapping: C01ClaimToGoldArtifact,
    applicability: tuple[C01CoverageApplicability, C01SupportApplicability],
) -> None:
    lane_dir = scoring_dir / "inputs" / lane
    _write_immutable(
        lane_dir / "generated-claim-map.json",
        _canonical_json_bytes(claim_map),
    )
    _write_immutable(
        lane_dir / "claim-to-gold.json",
        _canonical_json_bytes(mapping),
    )
    for item in applicability:
        _write_immutable(
            lane_dir / f"{item.metric_kind}-applicability.json",
            _canonical_json_bytes(item),
        )


def _metric_contract(
    *,
    lane: Q14Lane,
    metric_kind: MetricKind,
    aggregation: AggregationContract,
) -> MetricContract:
    note_role = (
        InputArtifactRole.PRE_RENDER_NOTE
        if lane == Q14Lane.GENERATION
        else InputArtifactRole.RENDERED_NOTE_PROJECTION
    )
    required_roles = (
        InputArtifactRole.RAW_SOURCE,
        InputArtifactRole.NORMALIZED_DOCUMENT,
        InputArtifactRole.REFERENCE_DOCUMENT,
        note_role,
        InputArtifactRole.GOLD,
        InputArtifactRole.ITEM_DISPOSITION,
        InputArtifactRole.MAPPING,
    )
    lane_label = lane.value
    kind_label = metric_kind.value
    metric_id = f"c01-{lane_label}-{kind_label}"
    components: Tuple[MetricComponent, ...]
    if metric_kind == MetricKind.COVERAGE:
        components = (
            MetricComponent(
                component_id="fully_covered",
                direction=Direction.NON_DIRECTIONAL,
                canonical_unit=CanonicalUnit.COUNT,
                numeric_representation=NumericRepresentation.INTEGER,
            ),
            MetricComponent(
                component_id="partially_covered",
                direction=Direction.NON_DIRECTIONAL,
                canonical_unit=CanonicalUnit.COUNT,
                numeric_representation=NumericRepresentation.INTEGER,
            ),
            MetricComponent(
                component_id="not_covered",
                direction=Direction.NON_DIRECTIONAL,
                canonical_unit=CanonicalUnit.COUNT,
                numeric_representation=NumericRepresentation.INTEGER,
            ),
        )
        scoring_unit = ScoringUnit.EXPECTED_CLAIM
        formula_kind = FormulaKind.COVERAGE_STATE_VECTOR_V1
        denominator = DenominatorSemantics.AUTHORITY_CLOSED_APPLICABLE_UNITS
        applicability = ApplicabilityConsumption.Q12_AUTHORITATIVE_DISPOSITION
    else:
        components = tuple(
            MetricComponent(
                component_id=state,
                direction=Direction.NON_DIRECTIONAL,
                canonical_unit=CanonicalUnit.COUNT,
                numeric_representation=NumericRepresentation.INTEGER,
            )
            for state in (
                "supported",
                "partially_supported",
                "unsupported",
                "contradicted_by_source",
                "overstated",
            )
        )
        scoring_unit = ScoringUnit.GENERATED_CLAIM
        formula_kind = FormulaKind.SUPPORT_STATE_COUNTS_V1
        denominator = DenominatorSemantics.Q8_DECIDED_SUPPORT_UNITS
        applicability = ApplicabilityConsumption.Q8_DECIDED_STATE_DISPOSITION
    return MetricContract(
        schema_version="benchmark-q14-metric-contract/1.0.0",
        artifact_role="metric_contract",
        metric_contract_id=metric_id,
        metric_contract_version="1.0.0",
        metric_kind=metric_kind,
        lane=lane,
        scoring_unit=scoring_unit,
        denominator_semantics=denominator,
        applicability_consumption=applicability,
        formula=MetricFormula(
            formula_id=metric_id,
            formula_revision="1.0.0",
            formula_kind=formula_kind,
        ),
        components=components,
        required_input_roles=required_roles,
        aggregation_contract_ref=AggregationContractReference(
            aggregation_contract_id=aggregation.aggregation_contract_id,
            aggregation_contract_version=aggregation.aggregation_contract_version,
            sha256=aggregation_contract_sha256(aggregation),
        ),
    )


def _build_q14_contracts() -> tuple[
    AggregationContract,
    MetricRegistry,
    ScorerContract,
    Mapping[str, MetricContract],
]:
    aggregation = AggregationContract(
        schema_version="benchmark-q14-aggregation-contract/1.0.0",
        artifact_role="aggregation_contract",
        aggregation_contract_id="parser-note-completeness-fixture-vector",
        aggregation_contract_version="1.0.0",
        input_metric_result_schema_version="benchmark-q14-fixture-metric-result/1.0.0",
        aggregation_kind=AggregationKind.FIXTURE_VECTOR_ONLY,
        formal_output="ordered_fixture_vector",
    )
    contracts = {
        f"c01-{lane.value}-{kind.value}": _metric_contract(
            lane=lane,
            metric_kind=kind,
            aggregation=aggregation,
        )
        for lane in (Q14Lane.GENERATION, Q14Lane.END_TO_END)
        for kind in (MetricKind.COVERAGE, MetricKind.SUPPORT)
    }
    contract_refs = tuple(
        MetricContractReference(
            metric_contract_id=contract.metric_contract_id,
            metric_contract_version=contract.metric_contract_version,
            sha256=metric_contract_sha256(contract),
        )
        for contract in sorted(contracts.values(), key=lambda item: item.metric_contract_id)
    )
    registry = MetricRegistry(
        schema_version="benchmark-q14-metric-registry/1.0.0",
        artifact_role="metric_registry",
        registry_id="parser-note-completeness-q14-registry",
        registry_revision="revision-001",
        benchmark_revision=C01_BENCHMARK_REVISION,
        metric_contracts=contract_refs,
    )
    import tests.evals.parser_note_completeness.q14_scoring as q14_module

    scorer = ScorerContract(
        schema_version="benchmark-q14-scorer-contract/1.0.0",
        artifact_role="scorer_contract",
        scorer_contract_id="parser-note-completeness-q14-python-scorer",
        scorer_contract_version="1.0.0",
        implementation_id="q14-python-foundation",
        implementation_version="1.0.0",
        implementation_sha256=_sha256(Path(q14_module.__file__).read_bytes()),
        configuration_sha256=_sha256(b"c01-real-artifact-q14-scorer/1.0.0"),
        supported_metric_contracts=contract_refs,
        compatible_lanes=(Q14Lane.GENERATION, Q14Lane.END_TO_END),
        deterministic_requirements=DeterministicRequirements(
            execution_mode="offline_deterministic",
            network_egress="forbidden",
            randomness="forbidden",
            binary_float_authority="forbidden",
            input_order="metric_contract_defined",
            serialization="benchmark_canonical_json",
        ),
        fixture_result_schema_version="benchmark-q14-fixture-metric-result/1.0.0",
    )
    return aggregation, registry, scorer, contracts


def _persist_q14_contracts(
    scoring_dir: Path,
    aggregation: AggregationContract,
    registry: MetricRegistry,
    scorer: ScorerContract,
    contracts: Mapping[str, MetricContract],
) -> None:
    contract_dir = scoring_dir / "contracts"
    _write_immutable(contract_dir / "aggregation.json", canonical_aggregation_contract_bytes(aggregation))
    _write_immutable(contract_dir / "registry.json", canonical_metric_registry_bytes(registry))
    _write_immutable(contract_dir / "scorer.json", canonical_scorer_contract_bytes(scorer))
    for metric_id, contract in sorted(contracts.items()):
        _write_immutable(
            contract_dir / f"{metric_id}.json",
            canonical_metric_contract_bytes(contract),
        )


def _load_q14_contracts(
    scoring_dir: Path,
) -> tuple[AggregationContract, MetricRegistry, ScorerContract, Mapping[str, MetricContract]]:
    contract_dir = scoring_dir / "contracts"
    aggregation, _ = _load_model(
        contract_dir / "aggregation.json",
        AggregationContract,
        canonical_aggregation_contract_bytes,
    )
    registry, _ = _load_model(
        contract_dir / "registry.json",
        MetricRegistry,
        canonical_metric_registry_bytes,
    )
    scorer, _ = _load_model(
        contract_dir / "scorer.json",
        ScorerContract,
        canonical_scorer_contract_bytes,
    )
    contracts: dict[str, MetricContract] = {}
    for ref in registry.metric_contracts:
        contract, _ = _load_model(
            contract_dir / f"{ref.metric_contract_id}.json",
            MetricContract,
            canonical_metric_contract_bytes,
        )
        contracts[contract.metric_contract_id] = contract
    validate_metric_registry_bindings(
        registry,
        resolved_metric_contracts={
            (item.metric_contract_id, item.metric_contract_version): item
            for item in contracts.values()
        },
    )
    validate_scorer_contract_bindings(
        scorer,
        resolved_metric_contracts={
            (item.metric_contract_id, item.metric_contract_version): item
            for item in contracts.values()
        },
    )
    for contract in contracts.values():
        validate_metric_contract_bindings(contract, aggregation_contract=aggregation)
    return aggregation, registry, scorer, contracts


def materialize_c01_scoring_inputs(
    execution_dir: Path,
    benchmark_root: Path,
    *,
    scoring_dir: Optional[Path] = None,
) -> Path:
    """Persist C01 claim/mapping/applicability inputs from real lane artifacts."""

    scoring_dir = scoring_dir or execution_dir / "q14-scoring"
    case = _load_c01_case(benchmark_root)
    _source, source_digest = _read_case_source(case, benchmark_root)
    reference, reference_digest = _read_reference(case, benchmark_root)
    _parser_output, parser_digest = _read_parser_output(execution_dir)
    _result, _result_digest, pre_render, pre_digest, projection, projection_digest = _read_end_to_end_lineage(
        execution_dir,
        reference,
        raw_source_digest=source_digest,
        parser_output_digest=parser_digest,
    )
    gold, gold_digest = _load_gold(benchmark_root, reference_digest)

    lanes: tuple[tuple[Literal["generation", "end_to_end"], Any, str], ...] = (
        ("generation", pre_render, pre_digest),
        ("end_to_end", projection, projection_digest),
    )
    for lane, note, note_digest in lanes:
        note_bytes = canonical_benchmark_note_bytes(note)
        claim_map = _build_generated_claim_map(
            note,
            note_bytes,
            note_digest,
            lane=lane,
        )
        claim_map_digest = _sha256(_canonical_json_bytes(claim_map))
        _validate_generated_claim_map(claim_map, note, note_bytes, note_digest)
        mapping = _build_claim_to_gold(
            lane=lane,
            note=note,
            note_digest=note_digest,
            claim_map=claim_map,
            claim_map_digest=claim_map_digest,
            gold=gold,
            gold_digest=gold_digest,
            reference=reference,
            reference_digest=reference_digest,
        )
        applicability = _build_applicability(
            lane=lane,
            gold=gold,
            claim_map=claim_map,
        )
        _persist_input_artifacts(
            scoring_dir=scoring_dir,
            lane=lane,
            claim_map=claim_map,
            mapping=mapping,
            applicability=applicability,
        )

    aggregation, registry, scorer, contracts = _build_q14_contracts()
    _persist_q14_contracts(scoring_dir, aggregation, registry, scorer, contracts)
    return scoring_dir


def _load_scoring_inputs(
    scoring_dir: Path,
    *,
    lane: Literal["generation", "end_to_end"],
    note: Any,
    note_bytes: bytes,
    note_digest: str,
    gold: C01GoldArtifact,
    gold_digest: str,
    reference: NormalizedDocument,
    reference_digest: str,
) -> tuple[C01GeneratedClaimMap, str, C01ClaimToGoldArtifact, str, C01CoverageApplicability, C01SupportApplicability]:
    lane_dir = scoring_dir / "inputs" / lane
    claim_map, claim_map_digest = _load_model(
        lane_dir / "generated-claim-map.json",
        C01GeneratedClaimMap,
        _canonical_json_bytes,
    )
    mapping, mapping_digest = _load_model(
        lane_dir / "claim-to-gold.json",
        C01ClaimToGoldArtifact,
        _canonical_json_bytes,
    )
    coverage_app, coverage_app_digest = _load_model(
        lane_dir / "coverage-applicability.json",
        C01CoverageApplicability,
        _canonical_json_bytes,
    )
    support_app, support_app_digest = _load_model(
        lane_dir / "support-applicability.json",
        C01SupportApplicability,
        _canonical_json_bytes,
    )
    _validate_generated_claim_map(claim_map, note, note_bytes, note_digest)
    _validate_claim_to_gold(
        mapping,
        note=note,
        note_digest=note_digest,
        claim_map=claim_map,
        claim_map_digest=claim_map_digest,
        gold=gold,
        gold_digest=gold_digest,
        reference=reference,
        reference_digest=reference_digest,
    )
    expected_ids = tuple(claim.expected_claim_id for claim in gold.expected_claims)
    generated_ids = tuple(claim.generated_claim_id for claim in claim_map.claims)
    if coverage_app.authoritative_expected_claim_ids != expected_ids:
        raise C01ScoringContractError("C01 coverage applicability/gold binding mismatch")
    if support_app.authoritative_generated_claim_ids != generated_ids:
        raise C01ScoringContractError("C01 support applicability/map binding mismatch")
    del coverage_app_digest, support_app_digest
    return claim_map, claim_map_digest, mapping, mapping_digest, coverage_app, support_app


def _input_digests(
    *,
    case: SmokeCase,
    parser_digest: str,
    reference_digest: str,
    note_digest: str,
    gold_digest: str,
    mapping_digest: str,
    lane: Q14Lane,
) -> Mapping[str, str]:
    note_role = (
        InputArtifactRole.PRE_RENDER_NOTE
        if lane == Q14Lane.GENERATION
        else InputArtifactRole.RENDERED_NOTE_PROJECTION
    )
    return {
        InputArtifactRole.RAW_SOURCE.value: case.source_sha256,
        InputArtifactRole.NORMALIZED_DOCUMENT.value: parser_digest,
        InputArtifactRole.REFERENCE_DOCUMENT.value: reference_digest,
        note_role.value: note_digest,
        InputArtifactRole.GOLD.value: gold_digest,
        InputArtifactRole.MAPPING.value: mapping_digest,
    }


def _score_lane(
    *,
    scoring_dir: Path,
    case: SmokeCase,
    lane: Literal["generation", "end_to_end"],
    note: Any,
    note_bytes: bytes,
    note_digest: str,
    gold: C01GoldArtifact,
    gold_digest: str,
    reference: NormalizedDocument,
    reference_digest: str,
    parser_digest: str,
    aggregation: AggregationContract,
    registry: MetricRegistry,
    scorer: ScorerContract,
    contracts: Mapping[str, MetricContract],
) -> tuple[FixtureMetricResult, FixtureMetricResult, str, str]:
    claim_map, _claim_map_digest, mapping, mapping_digest, coverage_app, support_app = _load_scoring_inputs(
        scoring_dir,
        lane=lane,
        note=note,
        note_bytes=note_bytes,
        note_digest=note_digest,
        gold=gold,
        gold_digest=gold_digest,
        reference=reference,
        reference_digest=reference_digest,
    )
    lane_enum = Q14Lane(lane)
    input_base = _input_digests(
        case=case,
        parser_digest=parser_digest,
        reference_digest=reference_digest,
        note_digest=note_digest,
        gold_digest=gold_digest,
        mapping_digest=mapping_digest,
        lane=lane_enum,
    )
    expected_importance = {
        claim.expected_claim_id: claim.importance for claim in gold.expected_claims
    }
    coverage_states = {
        item.expected_claim_id: item.coverage_state
        for item in mapping.expected_claim_coverage_results
    }
    support_states = {
        item.generated_claim_id: item.support_state
        for item in mapping.generated_claim_support_results
    }
    coverage_value = score_coverage_fixture(
        authoritative_expected_claim_ids=coverage_app.authoritative_expected_claim_ids,
        importance_by_expected_claim_id=expected_importance,
        coverage_state_by_expected_claim_id=coverage_states,
        applicable_expected_claim_ids=coverage_app.applicable_expected_claim_ids,
        excluded_expected_claim_ids=coverage_app.excluded_expected_claim_ids,
    )
    support_value = score_support_fixture(
        authoritative_generated_claim_ids=support_app.authoritative_generated_claim_ids,
        support_state_by_generated_claim_id=support_states,
        candidate_internal_contradiction_relation_ids=mapping.candidate_internal_contradiction_relation_ids,
    )
    coverage_contract = contracts[f"c01-{lane}-coverage"]
    support_contract = contracts[f"c01-{lane}-support"]
    coverage_app_digest = _sha256(
        _canonical_json_bytes(coverage_app)
    )
    support_app_digest = _sha256(
        _canonical_json_bytes(support_app)
    )
    coverage_inputs = tuple(
        InputArtifactReference(
            artifact_role=role,
            sha256=(
                coverage_app_digest
                if role == InputArtifactRole.ITEM_DISPOSITION
                else input_base[role.value]
            ),
        )
        for role in coverage_contract.required_input_roles
    )
    support_inputs = tuple(
        InputArtifactReference(
            artifact_role=role,
            sha256=(
                support_app_digest
                if role == InputArtifactRole.ITEM_DISPOSITION
                else input_base[role.value]
            ),
        )
        for role in support_contract.required_input_roles
    )
    coverage_result = build_fixture_metric_result(
        benchmark_revision=C01_BENCHMARK_REVISION,
        fixture_id=C01_CASE_ID,
        fixture_revision=C01_FIXTURE_REVISION,
        metric_contract=coverage_contract,
        metric_registry=registry,
        scorer_contract=scorer,
        input_artifacts=coverage_inputs,
        applicability_ref=OwnerRecordReference(
            schema_version=coverage_app.schema_version,
            record_type=coverage_app.artifact_role,
            record_id=coverage_app.record_id,
            sha256=coverage_app_digest,
        ),
        exclusion_ref=None,
        metric_value=coverage_value,
    )
    support_result = build_fixture_metric_result(
        benchmark_revision=C01_BENCHMARK_REVISION,
        fixture_id=C01_CASE_ID,
        fixture_revision=C01_FIXTURE_REVISION,
        metric_contract=support_contract,
        metric_registry=registry,
        scorer_contract=scorer,
        input_artifacts=support_inputs,
        applicability_ref=OwnerRecordReference(
            schema_version=support_app.schema_version,
            record_type=support_app.artifact_role,
            record_id=support_app.record_id,
            sha256=support_app_digest,
        ),
        exclusion_ref=None,
        metric_value=support_value,
    )
    resolved_input_coverage = dict(input_base)
    resolved_input_coverage[InputArtifactRole.ITEM_DISPOSITION.value] = coverage_app_digest
    resolved_input_support = dict(input_base)
    resolved_input_support[InputArtifactRole.ITEM_DISPOSITION.value] = support_app_digest
    external = {
        coverage_app.record_id: coverage_app_digest,
        support_app.record_id: support_app_digest,
    }
    validate_fixture_metric_result(
        coverage_result,
        metric_contract=coverage_contract,
        metric_registry=registry,
        scorer_contract=scorer,
        aggregation_contract=aggregation,
        resolved_input_digests=resolved_input_coverage,
        resolved_external_digests=external,
    )
    validate_fixture_metric_result(
        support_result,
        metric_contract=support_contract,
        metric_registry=registry,
        scorer_contract=scorer,
        aggregation_contract=aggregation,
        resolved_input_digests=resolved_input_support,
        resolved_external_digests=external,
    )
    result_dir = scoring_dir / "results"
    coverage_digest = _write_immutable(
        result_dir / f"{coverage_contract.metric_contract_id}.json",
        canonical_fixture_metric_result_bytes(coverage_result),
    )
    support_digest = _write_immutable(
        result_dir / f"{support_contract.metric_contract_id}.json",
        canonical_fixture_metric_result_bytes(support_result),
    )
    return coverage_result, support_result, coverage_digest, support_digest


def score_c01_execution(
    execution_dir: Path,
    benchmark_root: Path,
    *,
    scoring_dir: Optional[Path] = None,
) -> C01ScoringOutcome:
    """Score persisted C01 Generation and End-to-end artifacts through Q14."""

    scoring_dir = scoring_dir or execution_dir / "q14-scoring"
    if not scoring_dir.exists():
        materialize_c01_scoring_inputs(
            execution_dir,
            benchmark_root,
            scoring_dir=scoring_dir,
        )
    case = _load_c01_case(benchmark_root)
    _source, source_digest = _read_case_source(case, benchmark_root)
    reference, reference_digest = _read_reference(case, benchmark_root)
    _parser_output, parser_digest = _read_parser_output(execution_dir)
    _result, _result_digest, pre_render, pre_digest, projection, projection_digest = _read_end_to_end_lineage(
        execution_dir,
        reference,
        raw_source_digest=source_digest,
        parser_output_digest=parser_digest,
    )
    gold, gold_digest = _load_gold(benchmark_root, reference_digest)
    aggregation, registry, scorer, contracts = _load_q14_contracts(scoring_dir)
    generation = _score_lane(
        scoring_dir=scoring_dir,
        case=case,
        lane="generation",
        note=pre_render,
        note_bytes=canonical_benchmark_note_bytes(pre_render),
        note_digest=pre_digest,
        gold=gold,
        gold_digest=gold_digest,
        reference=reference,
        reference_digest=reference_digest,
        parser_digest=parser_digest,
        aggregation=aggregation,
        registry=registry,
        scorer=scorer,
        contracts=contracts,
    )
    end_to_end = _score_lane(
        scoring_dir=scoring_dir,
        case=case,
        lane="end_to_end",
        note=projection,
        note_bytes=canonical_benchmark_note_bytes(projection),
        note_digest=projection_digest,
        gold=gold,
        gold_digest=gold_digest,
        reference=reference,
        reference_digest=reference_digest,
        parser_digest=parser_digest,
        aggregation=aggregation,
        registry=registry,
        scorer=scorer,
        contracts=contracts,
    )
    results = (generation[0], generation[1], end_to_end[0], end_to_end[1])
    digests = {
        result.metric_contract_ref.metric_contract_id: digest
        for result, digest in (
            (generation[0], generation[2]),
            (generation[1], generation[3]),
            (end_to_end[0], end_to_end[2]),
            (end_to_end[1], end_to_end[3]),
        )
    }
    return C01ScoringOutcome(scoring_dir=scoring_dir, results=results, result_digests=digests)


__all__ = [
    "C01_BENCHMARK_REVISION",
    "C01ClaimToGoldArtifact",
    "C01CoverageApplicability",
    "C01GoldArtifact",
    "C01GeneratedClaimMap",
    "C01ScoringContractError",
    "C01ScoringOperationalError",
    "C01ScoringOutcome",
    "C01SupportApplicability",
    "materialize_c01_scoring_inputs",
    "score_c01_execution",
]
