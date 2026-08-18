"""Q26 BenchmarkNoteDocument and rendered-note projection contracts.

This module owns only the renderer-neutral note artifact boundary. Alignment,
coverage, scoring, routing, and authority semantics intentionally remain
outside this schema.
"""

from __future__ import annotations

import hashlib
import json
import re
from enum import Enum
from typing import Annotated, Any, Callable, Literal, Mapping, Optional, Tuple, TypeVar, Union

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    field_validator,
    model_validator,
)

from .normalized_document import (
    ArtifactRole,
    NormalizedDocument,
    NormalizedDocumentInput,
    normalized_document_sha256,
    validate_normalized_document,
)

BENCHMARK_NOTE_SCHEMA_VERSION = "benchmark-note-document/1.0.0"
RENDERED_NOTE_PROJECTION_SCHEMA_VERSION = "benchmark-rendered-note-projection/1.0.0"

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_NODE_ID_PATTERN = r"^node-[0-9a-f]{64}$"
_CITATION_ID_PATTERN = r"^citation-[0-9a-f]{64}$"
_MAPPING_ID_PATTERN = r"^mapping-[0-9a-f]{64}$"
_LANGUAGE_PATTERN = re.compile(
    r"^(?:und|[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*)$"
)
_MACHINE_REASON_PATTERN = r"^[a-z0-9]+(?:_[a-z0-9]+)*$"

EnumT = TypeVar("EnumT", bound=Enum)


def _enum_parser(enum_type: type[EnumT]) -> Callable[[object], EnumT]:
    def parse(value: object) -> EnumT:
        if isinstance(value, enum_type):
            return value
        if isinstance(value, str):
            try:
                return enum_type(value)
            except ValueError as exc:
                raise ValueError(f"unknown {enum_type.__name__} value") from exc
        raise TypeError(f"{enum_type.__name__} requires its exact string value")

    return parse


def _tuple_from_json(value: object) -> object:
    if isinstance(value, list):
        return tuple(value)
    return value

Sha256 = Annotated[StrictStr, Field(pattern=_SHA256_PATTERN)]
NodeId = Annotated[StrictStr, Field(pattern=_NODE_ID_PATTERN)]
CitationId = Annotated[StrictStr, Field(pattern=_CITATION_ID_PATTERN)]
MappingId = Annotated[StrictStr, Field(pattern=_MAPPING_ID_PATTERN)]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]
PositiveInt = Annotated[StrictInt, Field(ge=1)]
MachineReason = Annotated[StrictStr, Field(pattern=_MACHINE_REASON_PATTERN)]


class _StrictFrozenNoteModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class NoteNodeKind(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    QUOTE = "quote"
    CODE_BLOCK = "code_block"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    FIGURE = "figure"
    CAPTION = "caption"
    FORMULA = "formula"
    TRANSCRIPT_SEGMENT = "transcript_segment"
    MESSAGE = "message"


class NoteListKind(str, Enum):
    ORDERED = "ordered"
    UNORDERED = "unordered"


class CodeLanguageStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class CodeLanguageSource(str, Enum):
    SOURCE_DECLARED = "source_declared"
    PRODUCER_DETECTED = "producer_detected"


class CitationMode(str, Enum):
    WHOLE_ELEMENT = "whole_element"
    TEXT_RANGE = "text_range"


class NoteLocatorType(str, Enum):
    PDF = "pdf"
    WEB = "web"
    YOUTUBE = "youtube"
    CHAT = "chat"
    SCREENSHOTS = "screenshots"


class LineageParentRole(str, Enum):
    REFERENCE_DOCUMENT = "reference_document"
    PRE_RENDER_NOTE = "pre_render_note"


class LineageMappingState(str, Enum):
    NOT_APPLICABLE = "not_applicable"
    PROVIDED = "provided"
    UNAVAILABLE = "unavailable"


class LineageMappingShape(str, Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"
    UNMATCHED_SOURCE = "unmatched_source"
    UNMATCHED_TARGET = "unmatched_target"


class NoteProducerRole(str, Enum):
    GENERATOR = "generator"
    RENDERER = "renderer"


class CaptureMethod(str, Enum):
    AUTHORITATIVE_OUTPUT = "authoritative_output"
    VERIFIED_READBACK = "verified_readback"


class NoteHeaderRole(str, Enum):
    ROW = "row"
    COLUMN = "column"
    BOTH = "both"


NoteNodeKindValue = Annotated[
    NoteNodeKind, BeforeValidator(_enum_parser(NoteNodeKind))
]
NoteListKindValue = Annotated[
    NoteListKind, BeforeValidator(_enum_parser(NoteListKind))
]
CodeLanguageStatusValue = Annotated[
    CodeLanguageStatus, BeforeValidator(_enum_parser(CodeLanguageStatus))
]
CodeLanguageSourceValue = Annotated[
    CodeLanguageSource, BeforeValidator(_enum_parser(CodeLanguageSource))
]
CitationModeValue = Annotated[
    CitationMode, BeforeValidator(_enum_parser(CitationMode))
]
NoteLocatorTypeValue = Annotated[
    NoteLocatorType, BeforeValidator(_enum_parser(NoteLocatorType))
]
LineageParentRoleValue = Annotated[
    LineageParentRole, BeforeValidator(_enum_parser(LineageParentRole))
]
LineageMappingStateValue = Annotated[
    LineageMappingState, BeforeValidator(_enum_parser(LineageMappingState))
]
LineageMappingShapeValue = Annotated[
    LineageMappingShape, BeforeValidator(_enum_parser(LineageMappingShape))
]
NoteProducerRoleValue = Annotated[
    NoteProducerRole, BeforeValidator(_enum_parser(NoteProducerRole))
]
CaptureMethodValue = Annotated[
    CaptureMethod, BeforeValidator(_enum_parser(CaptureMethod))
]
NoteHeaderRoleValue = Annotated[
    NoteHeaderRole, BeforeValidator(_enum_parser(NoteHeaderRole))
]


class NoteTextSpan(_StrictFrozenNoteModel):
    start: NonNegativeInt
    end: PositiveInt

    @model_validator(mode="after")
    def _validate_range(self) -> "NoteTextSpan":
        if self.end <= self.start:
            raise ValueError("text span end must be greater than start")
        return self


class NoteListMetadata(_StrictFrozenNoteModel):
    list_kind: NoteListKindValue
    nesting_level: NonNegativeInt
    ordinal: Optional[NonNegativeInt] = None


class NoteTableCellMetadata(_StrictFrozenNoteModel):
    row_index: NonNegativeInt
    column_index: NonNegativeInt
    row_span: Optional[PositiveInt] = None
    column_span: Optional[PositiveInt] = None
    header_role: Optional[NoteHeaderRoleValue] = None


class NoteCodeMetadata(_StrictFrozenNoteModel):
    code_language_status: CodeLanguageStatusValue
    language_hint: Optional[StrictStr] = Field(default=None, min_length=1)
    language_source: Optional[CodeLanguageSourceValue] = None
    reason: Optional[MachineReason] = None

    @model_validator(mode="after")
    def _validate_language_contract(self) -> "NoteCodeMetadata":
        if self.code_language_status == CodeLanguageStatus.AVAILABLE:
            if self.language_hint is None or self.language_source is None:
                raise ValueError(
                    "available code language requires hint and source"
                )
            if self.reason is not None:
                raise ValueError(
                    "available code language must not include unavailable reason"
                )
        else:
            if self.language_hint is not None or self.language_source is not None:
                raise ValueError(
                    "unavailable code language must not include language identity"
                )
            if self.reason is None:
                raise ValueError("unavailable code language requires reason")
        return self


class NoteLocatorReference(_StrictFrozenNoteModel):
    locator_type: NoteLocatorTypeValue
    element_id: StrictStr = Field(min_length=1)
    locator_index: NonNegativeInt


class NoteCitation(_StrictFrozenNoteModel):
    citation_id: CitationId
    reference_document_id: StrictStr = Field(min_length=1)
    element_id: StrictStr = Field(min_length=1)
    mode: CitationModeValue
    text_span: Optional[NoteTextSpan] = None
    locator_refs: Annotated[
        Tuple[NoteLocatorReference, ...], BeforeValidator(_tuple_from_json)
    ] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_citation_shape(self) -> "NoteCitation":
        if self.mode == CitationMode.WHOLE_ELEMENT:
            if self.text_span is not None:
                raise ValueError("whole_element citation must not have text_span")
        elif self.text_span is None:
            raise ValueError("text_range citation requires text_span")

        if any(ref.element_id != self.element_id for ref in self.locator_refs):
            raise ValueError("locator references must target citation element_id")
        locator_indexes = tuple(ref.locator_index for ref in self.locator_refs)
        if locator_indexes != tuple(sorted(locator_indexes)):
            raise ValueError("locator references must be ordered by locator_index")
        if len(locator_indexes) != len(set(locator_indexes)):
            raise ValueError("locator references must not repeat locator_index")
        return self


_TEXT_BEARING_NODE_KINDS = frozenset(
    {
        NoteNodeKind.HEADING,
        NoteNodeKind.PARAGRAPH,
        NoteNodeKind.LIST_ITEM,
        NoteNodeKind.QUOTE,
        NoteNodeKind.CODE_BLOCK,
        NoteNodeKind.TABLE_CELL,
        NoteNodeKind.CAPTION,
        NoteNodeKind.FORMULA,
        NoteNodeKind.TRANSCRIPT_SEGMENT,
        NoteNodeKind.MESSAGE,
    }
)


class NoteNode(_StrictFrozenNoteModel):
    node_id: NodeId
    kind: NoteNodeKindValue
    order: NonNegativeInt
    parent_node_id: Optional[NodeId] = None
    content: Optional[StrictStr] = None
    languages: Annotated[
        Tuple[StrictStr, ...], BeforeValidator(_tuple_from_json)
    ] = Field(min_length=1)
    list_metadata: Optional[NoteListMetadata] = None
    table_cell_metadata: Optional[NoteTableCellMetadata] = None
    code_metadata: Optional[NoteCodeMetadata] = None
    citations: Annotated[
        Tuple[NoteCitation, ...], BeforeValidator(_tuple_from_json)
    ] = ()

    @field_validator("languages")
    @classmethod
    def _validate_languages(cls, languages: Tuple[str, ...]) -> Tuple[str, ...]:
        normalized = []
        for language in languages:
            if language != language.strip() or not language:
                raise ValueError("languages must contain trimmed nonblank tags")
            if language.casefold() == "mixed":
                raise ValueError("mixed is not a language tag; use und")
            if _LANGUAGE_PATTERN.fullmatch(language) is None:
                raise ValueError("language must be a valid BCP 47 shaped tag")
            normalized.append(language.casefold())
        if len(normalized) != len(set(normalized)):
            raise ValueError("languages must be deduplicated in declared order")
        return languages

    @model_validator(mode="after")
    def _validate_kind_contract(self) -> "NoteNode":
        if self.kind in _TEXT_BEARING_NODE_KINDS:
            if self.content is None or not self.content.strip():
                raise ValueError("text-bearing node requires nonblank content")
        elif self.kind in {NoteNodeKind.TABLE, NoteNodeKind.TABLE_ROW}:
            if self.content is not None:
                raise ValueError("table and table_row must have null content")

        if (self.kind == NoteNodeKind.LIST_ITEM) != (
            self.list_metadata is not None
        ):
            raise ValueError("list_metadata is required only for list_item")
        if (self.kind == NoteNodeKind.TABLE_CELL) != (
            self.table_cell_metadata is not None
        ):
            raise ValueError("table_cell_metadata is required only for table_cell")
        if (self.kind == NoteNodeKind.CODE_BLOCK) != (self.code_metadata is not None):
            raise ValueError("code_metadata is required only for code_block")
        return self


class NoteProducerProvenance(_StrictFrozenNoteModel):
    producer_role: NoteProducerRoleValue
    producer_name: StrictStr = Field(min_length=1)
    producer_version: StrictStr = Field(min_length=1)
    configuration_sha256: Sha256
    processing_method: StrictStr = Field(min_length=1)
    processing_stage: StrictStr = Field(min_length=1)
    capture_method: Optional[CaptureMethodValue] = None

    @model_validator(mode="after")
    def _validate_provenance_boundary(self) -> "NoteProducerProvenance":
        if self.producer_role == NoteProducerRole.GENERATOR:
            if self.capture_method is not None:
                raise ValueError("generator provenance must omit capture_method")
            if self.processing_stage != "pre_render_generation":
                raise ValueError(
                    "generator provenance must use pre_render_generation"
                )
        else:
            if self.capture_method is None:
                raise ValueError("renderer provenance requires capture_method")
            if self.processing_stage != "rendered_projection_capture":
                raise ValueError(
                    "renderer provenance must use rendered_projection_capture"
                )
        return self


class NoteLineageMapping(_StrictFrozenNoteModel):
    mapping_id: MappingId
    source_node_ids: Annotated[
        Tuple[NodeId, ...], BeforeValidator(_tuple_from_json)
    ] = ()
    target_node_ids: Annotated[
        Tuple[NodeId, ...], BeforeValidator(_tuple_from_json)
    ] = ()
    mapping_shape: LineageMappingShapeValue

    @model_validator(mode="after")
    def _validate_mapping_shape(self) -> "NoteLineageMapping":
        if len(self.source_node_ids) != len(set(self.source_node_ids)):
            raise ValueError("source_node_ids must be unique within a mapping")
        if len(self.target_node_ids) != len(set(self.target_node_ids)):
            raise ValueError("target_node_ids must be unique within a mapping")

        source_count = len(self.source_node_ids)
        target_count = len(self.target_node_ids)
        expected = {
            LineageMappingShape.ONE_TO_ONE: (1, 1),
            LineageMappingShape.ONE_TO_MANY: (1, None),
            LineageMappingShape.MANY_TO_ONE: (None, 1),
            LineageMappingShape.MANY_TO_MANY: (None, None),
            LineageMappingShape.UNMATCHED_SOURCE: (None, 0),
            LineageMappingShape.UNMATCHED_TARGET: (0, None),
        }[self.mapping_shape]
        source_ok = (
            source_count >= 2 if expected[0] is None else source_count == expected[0]
        )
        target_ok = (
            target_count >= 2 if expected[1] is None else target_count == expected[1]
        )
        if not source_ok or not target_ok:
            raise ValueError("mapping_shape does not agree with node ID cardinality")
        if source_count == 0 and target_count == 0:
            raise ValueError("mapping must contain a source or target node")
        return self


class NoteLineage(_StrictFrozenNoteModel):
    parent_artifact_role: LineageParentRoleValue
    parent_artifact_sha256: Sha256
    mapping_state: LineageMappingStateValue
    mappings: Annotated[
        Tuple[NoteLineageMapping, ...], BeforeValidator(_tuple_from_json)
    ] = ()

    @model_validator(mode="after")
    def _validate_lineage_state(self) -> "NoteLineage":
        if self.mapping_state == LineageMappingState.NOT_APPLICABLE:
            if self.mappings:
                raise ValueError("not_applicable lineage must have no mappings")
        elif self.mapping_state == LineageMappingState.PROVIDED:
            if not self.mappings:
                raise ValueError("provided lineage requires mappings")
        elif self.mapping_state == LineageMappingState.UNAVAILABLE:
            if self.mappings:
                raise ValueError("unavailable lineage must have no mappings")
        return self


class _BenchmarkNoteArtifact(_StrictFrozenNoteModel):
    document_id: StrictStr = Field(min_length=1)
    reference_document_sha256: Sha256
    nodes: Annotated[
        Tuple[NoteNode, ...], BeforeValidator(_tuple_from_json)
    ]
    producer_provenance: NoteProducerProvenance
    lineage: NoteLineage

    @model_validator(mode="after")
    def _validate_artifact_shape(self) -> "_BenchmarkNoteArtifact":
        orders = tuple(node.order for node in self.nodes)
        if orders != tuple(range(len(self.nodes))):
            raise ValueError("nodes must use gap-free ascending order")

        node_by_id = {node.node_id: node for node in self.nodes}
        if len(node_by_id) != len(self.nodes):
            raise ValueError("node IDs must be unique")
        for node in self.nodes:
            if node.parent_node_id is None:
                continue
            parent = node_by_id.get(node.parent_node_id)
            if parent is None:
                raise ValueError("parent_node_id must reference a node")
            if parent.order >= node.order:
                raise ValueError("parent_node_id must reference an earlier node")

            if node.kind == NoteNodeKind.TABLE_ROW and parent.kind != NoteNodeKind.TABLE:
                raise ValueError("table_row parent must be table")
            if node.kind == NoteNodeKind.TABLE_CELL and parent.kind != NoteNodeKind.TABLE_ROW:
                raise ValueError("table_cell parent must be table_row")
            if node.kind == NoteNodeKind.CAPTION and parent.kind != NoteNodeKind.FIGURE:
                raise ValueError("caption parent must be figure")

        for node in self.nodes:
            if node.kind == NoteNodeKind.TABLE_ROW and node.parent_node_id is None:
                raise ValueError("table_row requires a table parent")
            if node.kind == NoteNodeKind.TABLE_CELL and node.parent_node_id is None:
                raise ValueError("table_cell requires a table_row parent")
            if node.kind == NoteNodeKind.CAPTION and node.parent_node_id is None:
                raise ValueError("caption requires a figure parent")

            if node.kind == NoteNodeKind.LIST_ITEM:
                assert node.list_metadata is not None
                if node.parent_node_id is None:
                    if node.list_metadata.nesting_level != 0:
                        raise ValueError("root list_item must have nesting_level zero")
                else:
                    parent = node_by_id[node.parent_node_id]
                    if parent.kind != NoteNodeKind.LIST_ITEM:
                        raise ValueError("nested list_item parent must be list_item")
                    assert parent.list_metadata is not None
                    if node.list_metadata.nesting_level != parent.list_metadata.nesting_level + 1:
                        raise ValueError("nested list nesting_level must increment by one")

        expected_node_ids = _expected_node_ids(self.document_id, self.nodes)
        for node, expected_id in zip(self.nodes, expected_node_ids):
            if node.node_id != expected_id:
                raise ValueError("node_id does not match frozen identity rule")

        for node in self.nodes:
            for occurrence, citation in enumerate(node.citations):
                expected_id = benchmark_note_citation_id(node.node_id, occurrence)
                if citation.citation_id != expected_id:
                    raise ValueError("citation_id does not match frozen identity rule")

        if self.lineage.parent_artifact_role == LineageParentRole.REFERENCE_DOCUMENT:
            if self.lineage.mapping_state != LineageMappingState.NOT_APPLICABLE:
                raise ValueError("reference lineage must be not_applicable")
            if self.lineage.mappings:
                raise ValueError("reference lineage must have no mappings")
        elif self.lineage.mapping_state == LineageMappingState.NOT_APPLICABLE:
            raise ValueError("pre_render_note lineage cannot be not_applicable")

        mapping_ids = tuple(mapping.mapping_id for mapping in self.lineage.mappings)
        if len(mapping_ids) != len(set(mapping_ids)):
            raise ValueError("mapping IDs must be unique")
        if self.lineage.mappings:
            target_orders = []
            for mapping in self.lineage.mappings:
                if not mapping.target_node_ids:
                    target_orders.append((len(self.nodes), (), mapping.mapping_id))
                else:
                    missing = set(mapping.target_node_ids) - node_by_id.keys()
                    if missing:
                        raise ValueError("mapping target must reference a node")
                    target_orders.append(
                        (
                            min(node_by_id[node_id].order for node_id in mapping.target_node_ids),
                            tuple(node_by_id[node_id].order for node_id in mapping.target_node_ids),
                            mapping.mapping_id,
                        )
                    )
            if target_orders != sorted(target_orders):
                raise ValueError("mappings must be ordered by target reading order")
            for occurrence, mapping in enumerate(self.lineage.mappings):
                expected_id = benchmark_note_mapping_id(
                    mapping.source_node_ids,
                    mapping.target_node_ids,
                    occurrence,
                )
                if mapping.mapping_id != expected_id:
                    raise ValueError("mapping_id does not match frozen identity rule")
        return self


class BenchmarkNoteDocument(_BenchmarkNoteArtifact):
    schema_version: Literal["benchmark-note-document/1.0.0"]
    artifact_role: Literal["pre_render_note"]

    @model_validator(mode="after")
    def _validate_pre_render_contract(self) -> "BenchmarkNoteDocument":
        if self.producer_provenance.producer_role != NoteProducerRole.GENERATOR:
            raise ValueError("pre-render note requires generator provenance")
        if self.lineage.parent_artifact_role != LineageParentRole.REFERENCE_DOCUMENT:
            raise ValueError("pre-render note must bind reference_document lineage")
        return self


class RenderedNoteProjection(_BenchmarkNoteArtifact):
    schema_version: Literal["benchmark-rendered-note-projection/1.0.0"]
    artifact_role: Literal["rendered_note_projection"]

    @model_validator(mode="after")
    def _validate_rendered_contract(self) -> "RenderedNoteProjection":
        if self.producer_provenance.producer_role != NoteProducerRole.RENDERER:
            raise ValueError("rendered projection requires renderer provenance")
        if self.lineage.parent_artifact_role != LineageParentRole.PRE_RENDER_NOTE:
            raise ValueError("rendered projection must bind pre_render_note lineage")
        return self


BenchmarkNoteArtifact = Union[BenchmarkNoteDocument, RenderedNoteProjection]
BenchmarkNoteArtifactInput = Union[BenchmarkNoteArtifact, Mapping[str, Any]]


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _identity_digest(seed: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json_bytes(seed)).hexdigest()


def benchmark_note_node_id(
    document_id: str,
    anchor: Mapping[str, Any],
    kind: Union[NoteNodeKind, str],
    occurrence: int,
) -> str:
    if not isinstance(document_id, str) or not document_id:
        raise ValueError("document_id must be a nonblank string")
    if not isinstance(anchor, Mapping):
        raise TypeError("anchor must be a mapping")
    if not isinstance(occurrence, int) or isinstance(occurrence, bool) or occurrence < 0:
        raise ValueError("occurrence must be a nonnegative integer")
    node_kind = NoteNodeKind(kind).value
    return "node-" + _identity_digest(
        {
            "anchor": anchor,
            "document_id": document_id,
            "kind": node_kind,
            "occurrence": occurrence,
        }
    )


def benchmark_note_citation_id(node_id: str, occurrence: int) -> str:
    if re.fullmatch(_NODE_ID_PATTERN, node_id) is None:
        raise ValueError("node_id must be a valid benchmark note node ID")
    if not isinstance(occurrence, int) or isinstance(occurrence, bool) or occurrence < 0:
        raise ValueError("occurrence must be a nonnegative integer")
    return "citation-" + _identity_digest(
        {"node_id": node_id, "occurrence": occurrence}
    )


def benchmark_note_mapping_id(
    source_node_ids: Tuple[str, ...],
    target_node_ids: Tuple[str, ...],
    occurrence: int,
) -> str:
    if not isinstance(occurrence, int) or isinstance(occurrence, bool) or occurrence < 0:
        raise ValueError("occurrence must be a nonnegative integer")
    if any(
        re.fullmatch(_NODE_ID_PATTERN, node_id) is None
        for node_id in (*source_node_ids, *target_node_ids)
    ):
        raise ValueError("mapping node IDs must be valid benchmark note node IDs")
    return "mapping-" + _identity_digest(
        {
            "occurrence": occurrence,
            "source_node_ids": list(source_node_ids),
            "target_node_ids": list(target_node_ids),
        }
    )


def _first_source_anchor(node: NoteNode) -> Optional[dict[str, Any]]:
    for citation in node.citations:
        if citation.locator_refs:
            locator = citation.locator_refs[0]
            return {
                "anchor_type": "reference_locator",
                "element_id": locator.element_id,
                "locator_index": locator.locator_index,
                "locator_type": locator.locator_type.value,
            }
    return None


def _expected_node_ids(document_id: str, nodes: Tuple[NoteNode, ...]) -> Tuple[str, ...]:
    occurrences: dict[tuple[str, str], int] = {}
    structural_paths: dict[str, list[dict[str, Any]]] = {}
    expected: list[str] = []
    for node in nodes:
        source_anchor = _first_source_anchor(node)
        if source_anchor is not None:
            key = (json.dumps(source_anchor, sort_keys=True), node.kind.value)
            occurrence = occurrences.get(key, 0)
            occurrences[key] = occurrence + 1
            expected.append(
                benchmark_note_node_id(document_id, source_anchor, node.kind, occurrence)
            )
            structural_paths[node.node_id] = [
                {
                    "anchor_type": "reference_locator",
                    "anchor": source_anchor,
                    "kind": node.kind.value,
                    "occurrence": occurrence,
                }
            ]
            continue

        parent_path = (
            structural_paths.get(node.parent_node_id, [])
            if node.parent_node_id is not None
            else []
        )
        parent_key = node.parent_node_id or "<root>"
        key = (parent_key, node.kind.value)
        occurrence = occurrences.get(key, 0)
        occurrences[key] = occurrence + 1
        path = [*parent_path, {"kind": node.kind.value, "occurrence": occurrence}]
        structural_paths[node.node_id] = path
        expected.append(
            benchmark_note_node_id(
                document_id,
                {"anchor_type": "structural_path", "path": path},
                node.kind,
                occurrence,
            )
        )
    return tuple(expected)


def _artifact_model(payload: BenchmarkNoteArtifactInput) -> BenchmarkNoteArtifact:
    if isinstance(payload, (BenchmarkNoteDocument, RenderedNoteProjection)):
        return payload
    if not isinstance(payload, Mapping):
        raise TypeError("benchmark note artifact must be a mapping or validated model")
    schema_version = payload.get("schema_version")
    if schema_version == BENCHMARK_NOTE_SCHEMA_VERSION:
        return BenchmarkNoteDocument.model_validate(payload)
    if schema_version == RENDERED_NOTE_PROJECTION_SCHEMA_VERSION:
        return RenderedNoteProjection.model_validate(payload)
    raise ValueError("unknown benchmark note schema_version")


def canonical_benchmark_note_bytes(payload: BenchmarkNoteArtifactInput) -> bytes:
    """Return canonical UTF-8 bytes with no trailing newline."""

    artifact = _artifact_model(payload)
    return _canonical_json_bytes(artifact.model_dump(mode="json"))


def benchmark_note_sha256(payload: BenchmarkNoteArtifactInput) -> str:
    return hashlib.sha256(canonical_benchmark_note_bytes(payload)).hexdigest()


def _validate_reference_binding(
    artifact: BenchmarkNoteArtifact,
    reference_document: NormalizedDocumentInput,
) -> NormalizedDocument:
    document = validate_normalized_document(reference_document)
    if document.artifact_role != ArtifactRole.REFERENCE_DOCUMENT:
        raise ValueError("note artifact must bind a reference_document artifact")
    if artifact.document_id != document.document_id:
        raise ValueError("note document_id must equal reference document_id")
    if artifact.reference_document_sha256 != normalized_document_sha256(document):
        raise ValueError("reference_document_sha256 does not match canonical reference")
    return document


def _validate_citations(
    artifact: BenchmarkNoteArtifact,
    reference_document: NormalizedDocument,
) -> None:
    elements = {element.element_id: element for element in reference_document.elements}
    for node in artifact.nodes:
        for citation in node.citations:
            if citation.reference_document_id != artifact.document_id:
                raise ValueError("citation reference_document_id must equal document_id")
            element = elements.get(citation.element_id)
            if element is None:
                raise ValueError("citation element_id must resolve in reference document")
            if citation.mode == CitationMode.TEXT_RANGE:
                assert citation.text_span is not None
                if element.content is None or citation.text_span.end > len(element.content):
                    raise ValueError("citation text_span must fit exact reference content")
            for locator_ref in citation.locator_refs:
                if locator_ref.element_id != citation.element_id:
                    raise ValueError("locator reference element_id mismatch")
                if locator_ref.locator_index >= len(element.locators):
                    raise ValueError("locator reference index is outside reference element")
                locator = element.locators[locator_ref.locator_index]
                if locator.locator_type != locator_ref.locator_type.value:
                    raise ValueError("locator reference type mismatches reference locator")


def _validate_lineage_binding(
    artifact: BenchmarkNoteArtifact,
    parent_artifact: Optional[BenchmarkNoteArtifactInput],
) -> None:
    if isinstance(artifact, BenchmarkNoteDocument):
        if parent_artifact is not None:
            raise ValueError("pre-render note must not declare a note parent artifact")
        return

    if parent_artifact is None:
        raise ValueError("rendered projection validation requires its pre-render parent")
    parent = _artifact_model(parent_artifact)
    if not isinstance(parent, BenchmarkNoteDocument):
        raise ValueError("rendered projection parent must be a pre-render note")
    if artifact.lineage.parent_artifact_sha256 != benchmark_note_sha256(parent):
        raise ValueError("rendered lineage parent digest does not match parent bytes")
    if artifact.document_id != parent.document_id:
        raise ValueError("rendered document_id must equal pre-render document_id")
    if artifact.reference_document_sha256 != parent.reference_document_sha256:
        raise ValueError("rendered reference digest must equal pre-render reference digest")

    parent_orders = {node.node_id: node.order for node in parent.nodes}
    target_orders = {node.node_id: node.order for node in artifact.nodes}
    for mapping in artifact.lineage.mappings:
        if any(node_id not in parent_orders for node_id in mapping.source_node_ids):
            raise ValueError("mapping source must reference a parent node")
        if any(node_id not in target_orders for node_id in mapping.target_node_ids):
            raise ValueError("mapping target must reference a rendered node")
        if mapping.source_node_ids and tuple(
            sorted(mapping.source_node_ids, key=parent_orders.__getitem__)
        ) != mapping.source_node_ids:
            raise ValueError("mapping source IDs must use parent reading order")

    mapping_order = tuple(
        (
            min(
                (target_orders[node_id] for node_id in mapping.target_node_ids),
                default=len(target_orders),
            ),
            tuple(target_orders[node_id] for node_id in mapping.target_node_ids),
            mapping.mapping_id,
        )
        for mapping in artifact.lineage.mappings
    )
    if mapping_order != tuple(sorted(mapping_order)):
        raise ValueError("mapping order must use target then source reading order")


def validate_benchmark_note_artifact(
    artifact: BenchmarkNoteArtifactInput,
    reference_document: NormalizedDocumentInput,
    *,
    parent_artifact: Optional[BenchmarkNoteArtifactInput] = None,
) -> BenchmarkNoteArtifact:
    """Validate schema shape and bind the artifact to frozen reference bytes."""

    model = _artifact_model(artifact)
    document = _validate_reference_binding(model, reference_document)
    _validate_citations(model, document)
    _validate_lineage_binding(model, parent_artifact)
    return model


validate_benchmark_note = validate_benchmark_note_artifact
canonical_note_artifact_bytes = canonical_benchmark_note_bytes
note_artifact_sha256 = benchmark_note_sha256


__all__ = [
    "BENCHMARK_NOTE_SCHEMA_VERSION",
    "RENDERED_NOTE_PROJECTION_SCHEMA_VERSION",
    "BenchmarkNoteArtifact",
    "BenchmarkNoteDocument",
    "CaptureMethod",
    "CitationMode",
    "CodeLanguageSource",
    "CodeLanguageStatus",
    "LineageMappingShape",
    "LineageMappingState",
    "LineageParentRole",
    "NoteCitation",
    "NoteCodeMetadata",
    "NoteHeaderRole",
    "NoteListKind",
    "NoteListMetadata",
    "NoteLineage",
    "NoteLineageMapping",
    "NoteLocatorReference",
    "NoteLocatorType",
    "NoteNode",
    "NoteNodeKind",
    "NoteProducerProvenance",
    "NoteProducerRole",
    "NoteTableCellMetadata",
    "NoteTextSpan",
    "RenderedNoteProjection",
    "benchmark_note_citation_id",
    "benchmark_note_mapping_id",
    "benchmark_note_node_id",
    "benchmark_note_sha256",
    "canonical_benchmark_note_bytes",
    "canonical_note_artifact_bytes",
    "note_artifact_sha256",
    "validate_benchmark_note",
    "validate_benchmark_note_artifact",
]
