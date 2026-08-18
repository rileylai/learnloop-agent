from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from .benchmark_note import (
    BENCHMARK_NOTE_SCHEMA_VERSION,
    RENDERED_NOTE_PROJECTION_SCHEMA_VERSION,
    BenchmarkNoteDocument,
    CaptureMethod,
    CitationMode,
    CodeLanguageSource,
    CodeLanguageStatus,
    LineageMappingShape,
    LineageMappingState,
    LineageParentRole,
    NoteCitation,
    NoteCodeMetadata,
    NoteLineage,
    NoteLineageMapping,
    NoteListKind,
    NoteListMetadata,
    NoteLocatorReference,
    NoteNode,
    NoteNodeKind,
    NoteProducerProvenance,
    NoteProducerRole,
    NoteTextSpan,
    RenderedNoteProjection,
    benchmark_note_citation_id,
    benchmark_note_mapping_id,
    benchmark_note_node_id,
    benchmark_note_sha256,
    canonical_benchmark_note_bytes,
    validate_benchmark_note_artifact,
)
from .normalized_document import NormalizedDocument, normalized_document_sha256


_REFERENCE_PATH = (
    Path(__file__).parent
    / "v1"
    / "reference_documents"
    / "P01"
    / "revision-001"
    / "normalized_document.json"
)


def _reference() -> NormalizedDocument:
    return NormalizedDocument.model_validate(
        json.loads(_REFERENCE_PATH.read_text(encoding="utf-8"))
    )


def _structural_node_id(
    document_id: str,
    path: list[dict[str, object]],
    kind: NoteNodeKind,
    occurrence: int,
) -> str:
    return benchmark_note_node_id(
        document_id,
        {"anchor_type": "structural_path", "path": path},
        kind,
        occurrence,
    )


def _source_node(
    reference: NormalizedDocument,
    *,
    element_id: str = "p01-page-1-element-1",
    mode: CitationMode = CitationMode.WHOLE_ELEMENT,
    locator_type: str = "pdf",
    locator_index: int = 0,
) -> NoteNode:
    element = next(item for item in reference.elements if item.element_id == element_id)
    locator_ref = NoteLocatorReference(
        locator_type=locator_type,
        element_id=element_id,
        locator_index=locator_index,
    )
    provisional = NoteCitation(
        citation_id="citation-" + "0" * 64,
        reference_document_id=reference.document_id,
        element_id=element_id,
        mode=mode,
        text_span=(
            NoteTextSpan(start=0, end=7)
            if mode == CitationMode.TEXT_RANGE
            else None
        ),
        locator_refs=(locator_ref,),
    )
    anchor = {
        "anchor_type": "reference_locator",
        "element_id": element_id,
        "locator_index": locator_index,
        "locator_type": locator_type,
    }
    node_id = benchmark_note_node_id(
        reference.document_id,
        anchor,
        NoteNodeKind.PARAGRAPH,
        0,
    )
    citation = NoteCitation(
        citation_id=benchmark_note_citation_id(node_id, 0),
        reference_document_id=provisional.reference_document_id,
        element_id=provisional.element_id,
        mode=provisional.mode,
        text_span=provisional.text_span,
        locator_refs=provisional.locator_refs,
    )
    return NoteNode(
        node_id=node_id,
        kind=NoteNodeKind.PARAGRAPH,
        order=0,
        content=element.content,
        languages=("en",),
        citations=(citation,),
    )


def _pre_render(
    reference: NormalizedDocument,
    *,
    nodes: tuple[NoteNode, ...] | None = None,
    producer: NoteProducerProvenance | None = None,
    lineage: NoteLineage | None = None,
) -> BenchmarkNoteDocument:
    return BenchmarkNoteDocument(
        schema_version=BENCHMARK_NOTE_SCHEMA_VERSION,
        artifact_role="pre_render_note",
        document_id=reference.document_id,
        reference_document_sha256=normalized_document_sha256(reference),
        nodes=nodes or (_source_node(reference),),
        producer_provenance=producer
        or NoteProducerProvenance(
            producer_role=NoteProducerRole.GENERATOR,
            producer_name="test-generator",
            producer_version="1.0.0",
            configuration_sha256="a" * 64,
            processing_method="deterministic_generation",
            processing_stage="pre_render_generation",
        ),
        lineage=lineage
        or NoteLineage(
            parent_artifact_role=LineageParentRole.REFERENCE_DOCUMENT,
            parent_artifact_sha256=normalized_document_sha256(reference),
            mapping_state=LineageMappingState.NOT_APPLICABLE,
        ),
    )


def _rendered_projection(
    reference: NormalizedDocument,
    parent: BenchmarkNoteDocument,
    *,
    capture_method: CaptureMethod = CaptureMethod.VERIFIED_READBACK,
    mappings: tuple[NoteLineageMapping, ...] | None = None,
    mapping_state: LineageMappingState = LineageMappingState.PROVIDED,
) -> RenderedNoteProjection:
    target_id = _structural_node_id(
        reference.document_id,
        [{"kind": "paragraph", "occurrence": 0}],
        NoteNodeKind.PARAGRAPH,
        0,
    )
    target = NoteNode(
        node_id=target_id,
        kind=NoteNodeKind.PARAGRAPH,
        order=0,
        content="Rendered readback",
        languages=("en",),
    )
    mapping_items = mappings
    if mapping_items is None and mapping_state == LineageMappingState.PROVIDED:
        mapping_items = (
            NoteLineageMapping(
                mapping_id=benchmark_note_mapping_id(
                    (parent.nodes[0].node_id,),
                    (target.node_id,),
                    0,
                ),
                source_node_ids=(parent.nodes[0].node_id,),
                target_node_ids=(target.node_id,),
                mapping_shape=LineageMappingShape.ONE_TO_ONE,
            ),
        )
    return RenderedNoteProjection(
        schema_version=RENDERED_NOTE_PROJECTION_SCHEMA_VERSION,
        artifact_role="rendered_note_projection",
        document_id=reference.document_id,
        reference_document_sha256=normalized_document_sha256(reference),
        nodes=(target,),
        producer_provenance=NoteProducerProvenance(
            producer_role=NoteProducerRole.RENDERER,
            producer_name="test-renderer",
            producer_version="1.0.0",
            configuration_sha256="b" * 64,
            processing_method="deterministic_readback",
            processing_stage="rendered_projection_capture",
            capture_method=capture_method,
        ),
        lineage=NoteLineage(
            parent_artifact_role=LineageParentRole.PRE_RENDER_NOTE,
            parent_artifact_sha256=benchmark_note_sha256(parent),
            mapping_state=mapping_state,
            mappings=mapping_items or (),
        ),
    )


def test_exact_schema_role_pairing_and_strict_top_level_fields() -> None:
    reference = _reference()
    pre = _pre_render(reference)
    assert pre.schema_version == BENCHMARK_NOTE_SCHEMA_VERSION
    assert pre.artifact_role == "pre_render_note"

    payload = pre.model_dump(mode="json")
    payload["result_role"] = "candidate"
    with pytest.raises(ValidationError):
        BenchmarkNoteDocument.model_validate(payload)

    payload = pre.model_dump(mode="json")
    payload["artifact_role"] = "rendered_note_projection"
    with pytest.raises(ValidationError):
        BenchmarkNoteDocument.model_validate(payload)

    payload = pre.model_dump(mode="json")
    payload["schema_version"] = RENDERED_NOTE_PROJECTION_SCHEMA_VERSION
    with pytest.raises(ValidationError):
        BenchmarkNoteDocument.model_validate(payload)


def test_closed_node_kinds_and_metadata_contract() -> None:
    with pytest.raises(ValidationError):
        NoteNode(
            node_id="node-" + "1" * 64,
            kind="unknown",
            order=0,
            content="unsupported",
            languages=("en",),
        )
    with pytest.raises(ValidationError):
        NoteNode(
            node_id="node-" + "1" * 64,
            kind=NoteNodeKind.LIST_ITEM,
            order=0,
            content="item",
            languages=("en",),
        )
    with pytest.raises(ValidationError):
        NoteCodeMetadata(
            code_language_status=CodeLanguageStatus.UNAVAILABLE,
            language_hint="python",
            language_source=CodeLanguageSource.SOURCE_DECLARED,
            reason="not_found",
        )
    with pytest.raises(ValidationError):
        NoteNode(
            node_id="node-" + "1" * 64,
            kind=NoteNodeKind.PARAGRAPH,
            order=0,
            content="x",
            languages=("mixed",),
        )

    list_node = NoteNode(
        node_id="node-" + "1" * 64,
        kind=NoteNodeKind.LIST_ITEM,
        order=0,
        content="item",
        languages=("en",),
        list_metadata=NoteListMetadata(
            list_kind=NoteListKind.UNORDERED,
            nesting_level=0,
        ),
    )
    assert list_node.list_metadata is not None


def test_order_hierarchy_and_nested_list_validation() -> None:
    reference = _reference()
    heading_path = [{"kind": "heading", "occurrence": 0}]
    heading = NoteNode(
        node_id=_structural_node_id(
            reference.document_id, heading_path, NoteNodeKind.HEADING, 0
        ),
        kind=NoteNodeKind.HEADING,
        order=0,
        content="Heading",
        languages=("en",),
    )
    paragraph_path = [*heading_path, {"kind": "paragraph", "occurrence": 0}]
    paragraph = NoteNode(
        node_id=_structural_node_id(
            reference.document_id, paragraph_path, NoteNodeKind.PARAGRAPH, 0
        ),
        kind=NoteNodeKind.PARAGRAPH,
        order=1,
        parent_node_id=heading.node_id,
        content="Paragraph",
        languages=("en",),
    )
    pre = _pre_render(reference, nodes=(heading, paragraph))
    assert [node.order for node in pre.nodes] == [0, 1]

    invalid = pre.model_dump(mode="json")
    invalid["nodes"][1]["order"] = 2
    with pytest.raises(ValidationError):
        BenchmarkNoteDocument.model_validate(invalid)

    invalid = pre.model_dump(mode="json")
    invalid["nodes"][1]["parent_node_id"] = None
    with pytest.raises(ValidationError):
        BenchmarkNoteDocument.model_validate(invalid)


def test_identity_helpers_are_deterministic_and_content_independent() -> None:
    anchor = {"anchor_type": "structural_path", "path": []}
    node_id = benchmark_note_node_id("P01", anchor, NoteNodeKind.PARAGRAPH, 0)
    assert node_id == benchmark_note_node_id("P01", anchor, "paragraph", 0)
    assert node_id != benchmark_note_node_id("P01", anchor, "paragraph", 1)
    citation_id = benchmark_note_citation_id(node_id, 0)
    assert citation_id == benchmark_note_citation_id(node_id, 0)
    mapping_id = benchmark_note_mapping_id((node_id,), (node_id,), 0)
    assert mapping_id == benchmark_note_mapping_id((node_id,), (node_id,), 0)


def test_citation_text_range_and_typed_locator_bind_to_reference() -> None:
    reference = _reference()
    note = _pre_render(
        reference,
        nodes=(
            _source_node(
                reference,
                mode=CitationMode.TEXT_RANGE,
            ),
        ),
    )
    assert validate_benchmark_note_artifact(note, reference) == note

    invalid = note.model_dump(mode="json")
    invalid["nodes"][0]["citations"][0]["text_span"]["end"] = 10_000
    with pytest.raises(ValueError, match="text_span"):
        validate_benchmark_note_artifact(invalid, reference)

    invalid_node = _source_node(reference, locator_type="web")
    invalid_note = _pre_render(reference, nodes=(invalid_node,))
    with pytest.raises(ValueError, match="locator reference type"):
        validate_benchmark_note_artifact(invalid_note, reference)

    invalid_node = _source_node(reference, locator_index=1)
    invalid_note = _pre_render(reference, nodes=(invalid_node,))
    with pytest.raises(ValueError, match="locator reference index"):
        validate_benchmark_note_artifact(invalid_note, reference)


def test_provenance_and_rendered_lineage_boundary() -> None:
    reference = _reference()
    with pytest.raises(ValidationError):
        NoteProducerProvenance(
            producer_role=NoteProducerRole.GENERATOR,
            producer_name="generator",
            producer_version="1.0.0",
            configuration_sha256="a" * 64,
            processing_method="deterministic_generation",
            processing_stage="pre_render_generation",
            capture_method=CaptureMethod.VERIFIED_READBACK,
        )

    parent = _pre_render(reference)
    rendered = _rendered_projection(reference, parent)
    assert validate_benchmark_note_artifact(
        rendered,
        reference,
        parent_artifact=parent,
    ) == rendered

    unavailable = _rendered_projection(
        reference,
        parent,
        mapping_state=LineageMappingState.UNAVAILABLE,
        mappings=(),
    )
    assert validate_benchmark_note_artifact(
        unavailable,
        reference,
        parent_artifact=parent,
    ) == unavailable

    invalid = rendered.model_dump(mode="json")
    invalid["producer_provenance"]["capture_method"] = "outgoing_request"
    with pytest.raises(ValidationError):
        RenderedNoteProjection.model_validate(invalid)

    invalid = rendered.model_dump(mode="json")
    invalid["lineage"]["parent_artifact_sha256"] = "c" * 64
    with pytest.raises(ValueError, match="parent digest"):
        validate_benchmark_note_artifact(invalid, reference, parent_artifact=parent)


def test_canonical_bytes_have_no_newline_and_digest_matches_external_hash() -> None:
    reference = _reference()
    note = _pre_render(reference)
    first = canonical_benchmark_note_bytes(note)
    second = canonical_benchmark_note_bytes(note.model_dump(mode="json"))
    assert first == second
    assert not first.endswith(b"\n")
    assert benchmark_note_sha256(note) == hashlib.sha256(first).hexdigest()


def test_unknown_schema_and_invalid_mapping_shape_fail_closed() -> None:
    reference = _reference()
    note = _pre_render(reference)
    invalid = note.model_dump(mode="json")
    invalid["schema_version"] = "benchmark-note-document/9.9.9"
    with pytest.raises(ValueError, match="unknown"):
        canonical_benchmark_note_bytes(invalid)

    parent_id = note.nodes[0].node_id
    with pytest.raises(ValidationError):
        NoteLineageMapping(
            mapping_id=benchmark_note_mapping_id((parent_id,), (), 0),
            source_node_ids=(parent_id,),
            target_node_ids=(),
            mapping_shape=LineageMappingShape.ONE_TO_ONE,
        )
