from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Annotated, Any, Literal, Mapping, Optional, Tuple, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
    field_validator,
    model_validator,
)

SCHEMA_VERSION = "normalized-document/1.0.0"
NORMALIZED_COORDINATE_MAX = 1_000_000
_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_MACHINE_REASON_PATTERN = r"^[a-z0-9]+(?:_[a-z0-9]+)*$"

Sha256 = Annotated[StrictStr, Field(pattern=_SHA256_PATTERN)]
MachineReason = Annotated[StrictStr, Field(pattern=_MACHINE_REASON_PATTERN)]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]
PositiveInt = Annotated[StrictInt, Field(ge=1)]
NormalizedCoordinate = Annotated[
    StrictInt,
    Field(ge=0, le=NORMALIZED_COORDINATE_MAX),
]


class _StrictBenchmarkModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        frozen=True,
    )


class ArtifactRole(str, Enum):
    PARSER_OUTPUT = "parser_output"
    REFERENCE_DOCUMENT = "reference_document"


class SourceType(str, Enum):
    PDF = "pdf"
    WEB = "web"
    YOUTUBE = "youtube"
    CHAT = "chat"
    SCREENSHOTS = "screenshots"


class ElementKind(str, Enum):
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
    UI_TEXT = "ui_text"
    PAGE_BREAK = "page_break"
    UNKNOWN = "unknown"


ELEMENT_KINDS = tuple(kind.value for kind in ElementKind)


class CapabilityStatus(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"


class LocatorStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class IdentityStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class ListKind(str, Enum):
    ORDERED = "ordered"
    UNORDERED = "unordered"


class HeaderRole(str, Enum):
    ROW = "row"
    COLUMN = "column"
    BOTH = "both"


CAPABILITY_NAMES = (
    "hierarchy",
    "language_identification",
    "geometry",
    "table_structure",
    "code_metadata",
    "source_modality",
    "typed_locators",
)

_TEXT_BEARING_KINDS = frozenset(
    {
        ElementKind.HEADING,
        ElementKind.PARAGRAPH,
        ElementKind.LIST_ITEM,
        ElementKind.QUOTE,
        ElementKind.CODE_BLOCK,
        ElementKind.TABLE_CELL,
        ElementKind.CAPTION,
        ElementKind.FORMULA,
        ElementKind.TRANSCRIPT_SEGMENT,
        ElementKind.MESSAGE,
        ElementKind.UI_TEXT,
        ElementKind.UNKNOWN,
    }
)


def _validate_language_tags(languages: Tuple[str, ...]) -> Tuple[str, ...]:
    normalized_tags = []
    for tag in languages:
        if not tag or tag != tag.strip():
            raise ValueError("language tags must be nonblank and trimmed")
        normalized = tag.casefold()
        if normalized == "mixed":
            raise ValueError("mixed is not a language tag; use und when unknown")
        normalized_tags.append(normalized)
    if len(normalized_tags) != len(set(normalized_tags)):
        raise ValueError("language tags must be deduplicated in declared order")
    return languages


class SourceMetadata(_StrictBenchmarkModel):
    source_type: SourceType
    source_identity: StrictStr = Field(min_length=1)
    display_name: StrictStr = Field(min_length=1)
    source_snapshot_sha256: Sha256
    languages: Tuple[StrictStr, ...] = Field(min_length=1)

    @field_validator("languages")
    @classmethod
    def _validate_languages(cls, languages: Tuple[str, ...]) -> Tuple[str, ...]:
        return _validate_language_tags(languages)


class CapabilityDeclaration(_StrictBenchmarkModel):
    status: CapabilityStatus
    reason: Optional[MachineReason] = None

    @model_validator(mode="after")
    def _validate_reason(self) -> "CapabilityDeclaration":
        if self.status in {
            CapabilityStatus.PARTIAL,
            CapabilityStatus.UNAVAILABLE,
        } and self.reason is None:
            raise ValueError("reason is required for partial or unavailable capability")
        return self


class TypedIdentity(_StrictBenchmarkModel):
    status: IdentityStatus
    value: Optional[StrictStr] = Field(default=None, min_length=1)
    reason: Optional[MachineReason] = None

    @model_validator(mode="after")
    def _validate_identity(self) -> "TypedIdentity":
        if self.status == IdentityStatus.AVAILABLE:
            if self.value is None:
                raise ValueError("available identity requires value")
            if self.reason is not None:
                raise ValueError("available identity must not include reason")
        else:
            if self.value is not None:
                raise ValueError("unavailable identity must not include value")
            if self.reason is None:
                raise ValueError("unavailable identity requires reason")
        return self


class Capabilities(_StrictBenchmarkModel):
    hierarchy: CapabilityDeclaration
    language_identification: CapabilityDeclaration
    geometry: CapabilityDeclaration
    table_structure: CapabilityDeclaration
    code_metadata: CapabilityDeclaration
    source_modality: CapabilityDeclaration
    typed_locators: CapabilityDeclaration


class NormalizedGeometry(_StrictBenchmarkModel):
    coordinate_space: Literal["normalized_top_left_0_1000000"]
    x: NormalizedCoordinate
    y: NormalizedCoordinate
    width: NormalizedCoordinate
    height: NormalizedCoordinate

    @model_validator(mode="after")
    def _validate_bounds(self) -> "NormalizedGeometry":
        if self.x + self.width > NORMALIZED_COORDINATE_MAX:
            raise ValueError("geometry exceeds normalized horizontal range")
        if self.y + self.height > NORMALIZED_COORDINATE_MAX:
            raise ValueError("geometry exceeds normalized vertical range")
        return self


class TextSpan(_StrictBenchmarkModel):
    start: NonNegativeInt
    end: PositiveInt

    @model_validator(mode="after")
    def _validate_range(self) -> "TextSpan":
        if self.end <= self.start:
            raise ValueError("text span end must be greater than start")
        return self


def _validate_locator_availability(
    locator: BaseModel,
    *,
    required_fields: Tuple[str, ...],
    identity_fields: Tuple[str, ...],
) -> None:
    status = getattr(locator, "status")
    reason = getattr(locator, "reason")
    if status == LocatorStatus.AVAILABLE:
        missing = [name for name in required_fields if getattr(locator, name) is None]
        if missing:
            raise ValueError(
                "available locator requires identity: " + ", ".join(missing)
            )
        if reason is not None:
            raise ValueError("available locator must not include unavailable reason")
        return

    if reason is None:
        raise ValueError("unavailable locator requires machine-readable reason")
    populated = [name for name in identity_fields if getattr(locator, name) is not None]
    if populated:
        raise ValueError(
            "unavailable locator must not include available identity: "
            + ", ".join(populated)
        )


class PdfLocator(_StrictBenchmarkModel):
    locator_type: Literal["pdf"]
    status: LocatorStatus
    reason: Optional[MachineReason] = None
    page: Optional[PositiveInt] = None
    geometry: Optional[NormalizedGeometry] = None
    text_span: Optional[TextSpan] = None

    @model_validator(mode="after")
    def _validate_availability(self) -> "PdfLocator":
        _validate_locator_availability(
            self,
            required_fields=("page",),
            identity_fields=("page", "geometry", "text_span"),
        )
        return self


class WebLocator(_StrictBenchmarkModel):
    locator_type: Literal["web"]
    status: LocatorStatus
    reason: Optional[MachineReason] = None
    snapshot_sha256: Optional[Sha256] = None
    dom_path: Optional[StrictStr] = Field(default=None, min_length=1)
    text_span: Optional[TextSpan] = None

    @model_validator(mode="after")
    def _validate_availability(self) -> "WebLocator":
        _validate_locator_availability(
            self,
            required_fields=("snapshot_sha256", "dom_path"),
            identity_fields=("snapshot_sha256", "dom_path", "text_span"),
        )
        return self


class YouTubeLocator(_StrictBenchmarkModel):
    locator_type: Literal["youtube"]
    status: LocatorStatus
    reason: Optional[MachineReason] = None
    video_identity: Optional[TypedIdentity] = None
    caption_track_identity: Optional[TypedIdentity] = None
    cue_index: Optional[NonNegativeInt] = None
    start_ms: Optional[NonNegativeInt] = None
    end_ms: Optional[NonNegativeInt] = None

    @model_validator(mode="after")
    def _validate_availability(self) -> "YouTubeLocator":
        fields = (
            "video_identity",
            "caption_track_identity",
            "cue_index",
            "start_ms",
            "end_ms",
        )
        _validate_locator_availability(
            self,
            required_fields=fields,
            identity_fields=fields,
        )
        if (
            self.start_ms is not None
            and self.end_ms is not None
            and self.end_ms < self.start_ms
        ):
            raise ValueError("YouTube locator end_ms must be at least start_ms")
        return self


class ChatLocator(_StrictBenchmarkModel):
    locator_type: Literal["chat"]
    status: LocatorStatus
    reason: Optional[MachineReason] = None
    message_id: Optional[StrictStr] = Field(default=None, min_length=1)
    source_sequence: Optional[NonNegativeInt] = None
    thread_id: Optional[StrictStr] = Field(default=None, min_length=1)
    reply_to_message_id: Optional[StrictStr] = Field(default=None, min_length=1)
    source_timestamp: Optional[StrictStr] = Field(default=None, min_length=1)
    text_span: Optional[TextSpan] = None

    @model_validator(mode="after")
    def _validate_availability(self) -> "ChatLocator":
        identity_fields = (
            "message_id",
            "source_sequence",
            "thread_id",
            "reply_to_message_id",
            "source_timestamp",
            "text_span",
        )
        _validate_locator_availability(
            self,
            required_fields=("message_id", "source_sequence"),
            identity_fields=identity_fields,
        )
        return self


class ScreenshotLocator(_StrictBenchmarkModel):
    locator_type: Literal["screenshots"]
    status: LocatorStatus
    reason: Optional[MachineReason] = None
    image_index: Optional[PositiveInt] = None
    image_sha256: Optional[Sha256] = None
    region: Optional[NormalizedGeometry] = None
    text_span: Optional[TextSpan] = None

    @model_validator(mode="after")
    def _validate_availability(self) -> "ScreenshotLocator":
        identity_fields = ("image_index", "image_sha256", "region", "text_span")
        _validate_locator_availability(
            self,
            required_fields=("image_index", "image_sha256"),
            identity_fields=identity_fields,
        )
        return self


Locator = Annotated[
    Union[
        PdfLocator,
        WebLocator,
        YouTubeLocator,
        ChatLocator,
        ScreenshotLocator,
    ],
    Field(discriminator="locator_type"),
]


class Section(_StrictBenchmarkModel):
    section_id: StrictStr = Field(min_length=1)
    parent_section_id: Optional[StrictStr] = Field(default=None, min_length=1)
    heading_element_id: Optional[StrictStr] = Field(default=None, min_length=1)
    start_order: NonNegativeInt
    end_order: NonNegativeInt

    @model_validator(mode="after")
    def _validate_order_range(self) -> "Section":
        if self.end_order < self.start_order:
            raise ValueError("section end_order must be at least start_order")
        return self


class ListMetadata(_StrictBenchmarkModel):
    list_kind: ListKind
    nesting_level: NonNegativeInt
    ordinal: Optional[NonNegativeInt] = None


class TableCellMetadata(_StrictBenchmarkModel):
    row_index: NonNegativeInt
    column_index: NonNegativeInt
    row_span: Optional[PositiveInt] = None
    column_span: Optional[PositiveInt] = None
    header_role: Optional[HeaderRole] = None


class CodeMetadata(_StrictBenchmarkModel):
    language_hint: StrictStr = Field(min_length=1)
    source_supplied: StrictBool


class Element(_StrictBenchmarkModel):
    element_id: StrictStr = Field(min_length=1)
    kind: ElementKind
    order: NonNegativeInt
    section_id: StrictStr = Field(min_length=1)
    parent_element_id: Optional[StrictStr] = Field(default=None, min_length=1)
    content: Optional[StrictStr] = None
    languages: Tuple[StrictStr, ...] = Field(min_length=1)
    locators: Tuple[Locator, ...] = Field(min_length=1)
    list_metadata: Optional[ListMetadata] = None
    table_cell_metadata: Optional[TableCellMetadata] = None
    code_metadata: Optional[CodeMetadata] = None

    @field_validator("languages")
    @classmethod
    def _validate_languages(cls, languages: Tuple[str, ...]) -> Tuple[str, ...]:
        return _validate_language_tags(languages)

    @model_validator(mode="after")
    def _validate_kind_contract(self) -> "Element":
        if self.kind in _TEXT_BEARING_KINDS and (
            self.content is None or not self.content.strip()
        ):
            raise ValueError("text-bearing element requires nonblank content")
        if self.kind in {ElementKind.TABLE, ElementKind.TABLE_ROW} and self.content is not None:
            raise ValueError("table and table_row must not carry content")

        if (self.kind == ElementKind.LIST_ITEM) != (self.list_metadata is not None):
            raise ValueError("list_metadata is allowed and required only for list_item")
        if self.table_cell_metadata is not None and self.kind != ElementKind.TABLE_CELL:
            raise ValueError(
                "table_cell_metadata is allowed only for table_cell"
            )
        if self.kind == ElementKind.PAGE_BREAK and self.content is not None:
            if self.content.strip():
                raise ValueError("page_break must not carry nonblank content")
        if self.code_metadata is not None and self.kind != ElementKind.CODE_BLOCK:
            raise ValueError("code_metadata is allowed only for code_block")
        return self


class ProducerProvenance(_StrictBenchmarkModel):
    producer_name: StrictStr = Field(min_length=1)
    producer_version: StrictStr = Field(min_length=1)
    configuration_sha256: Sha256
    segmentation_semantics: StrictStr = Field(min_length=1)
    processing_method: StrictStr = Field(min_length=1)
    processing_stage: StrictStr = Field(min_length=1)
    parser_model: Optional[StrictStr] = Field(default=None, min_length=1)
    ocr_model: Optional[StrictStr] = Field(default=None, min_length=1)
    asr_model: Optional[StrictStr] = Field(default=None, min_length=1)


def _validate_acyclic(
    parent_by_id: Mapping[str, Optional[str]],
    *,
    hierarchy_name: str,
) -> None:
    for start_id in parent_by_id:
        seen = set()
        current_id: Optional[str] = start_id
        while current_id is not None:
            if current_id in seen:
                raise ValueError(f"{hierarchy_name} hierarchy must be acyclic")
            seen.add(current_id)
            current_id = parent_by_id.get(current_id)


class NormalizedDocument(_StrictBenchmarkModel):
    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        frozen=True,
        json_schema_extra={
            "$id": f"https://learnloop.local/schemas/{SCHEMA_VERSION}",
        },
    )

    schema_version: Literal["normalized-document/1.0.0"]
    artifact_role: ArtifactRole
    document_id: StrictStr = Field(min_length=1)
    source: SourceMetadata
    capabilities: Capabilities
    sections: Tuple[Section, ...] = Field(min_length=1)
    elements: Tuple[Element, ...] = Field(min_length=1)
    producer_provenance: ProducerProvenance

    @model_validator(mode="after")
    def _validate_document_invariants(self) -> "NormalizedDocument":
        section_ids = tuple(section.section_id for section in self.sections)
        if len(section_ids) != len(set(section_ids)):
            raise ValueError("section IDs must be unique")

        element_ids = tuple(element.element_id for element in self.elements)
        if len(element_ids) != len(set(element_ids)):
            raise ValueError("element IDs must be unique")

        orders = [element.order for element in self.elements]
        if orders != list(range(len(self.elements))):
            raise ValueError(
                "elements must be ordered by unique, contiguous order starting at 0"
            )

        sections_by_id = {section.section_id: section for section in self.sections}
        elements_by_id = {element.element_id: element for element in self.elements}

        section_parents = {}
        for section in self.sections:
            parent_id = section.parent_section_id
            if parent_id == section.section_id:
                raise ValueError("section must not be its own parent")
            if parent_id is not None and parent_id not in sections_by_id:
                raise ValueError("parent_section_id must reference a section")
            if section.end_order >= len(self.elements):
                raise ValueError("section range must reference valid element order")
            section_parents[section.section_id] = parent_id
        _validate_acyclic(section_parents, hierarchy_name="section")

        for section in self.sections:
            if section.parent_section_id is not None:
                parent = sections_by_id[section.parent_section_id]
                if not (
                    parent.start_order <= section.start_order
                    and section.end_order <= parent.end_order
                ):
                    raise ValueError("child section range must be within parent range")

            if section.heading_element_id is not None:
                heading = elements_by_id.get(section.heading_element_id)
                if heading is None:
                    raise ValueError("heading element must reference an element")
                if heading.kind != ElementKind.HEADING:
                    raise ValueError("heading element must have heading kind")
                if heading.section_id != section.section_id:
                    raise ValueError("heading element must belong to section")
                if not section.start_order <= heading.order <= section.end_order:
                    raise ValueError("heading element must be inside section range")

        expected_locator_type = self.source.source_type.value
        element_parents = {}
        for element in self.elements:
            section = sections_by_id.get(element.section_id)
            if section is None:
                raise ValueError("element section_id must reference a section")
            if not section.start_order <= element.order <= section.end_order:
                raise ValueError("element order must be inside its section range")
            source_languages = {
                language.casefold() for language in self.source.languages
            }
            if any(
                language.casefold() not in source_languages
                for language in element.languages
            ):
                raise ValueError("element languages must be declared by source")

            parent_id = element.parent_element_id
            if parent_id == element.element_id:
                raise ValueError("element must not be its own parent")
            if parent_id is not None and parent_id not in elements_by_id:
                raise ValueError("parent_element_id must reference an element")
            element_parents[element.element_id] = parent_id

            if element.kind == ElementKind.TABLE_ROW:
                if parent_id is None or elements_by_id[parent_id].kind != ElementKind.TABLE:
                    raise ValueError("table_row parent must be table")
            if element.kind == ElementKind.TABLE_CELL:
                if (
                    parent_id is None
                    or elements_by_id[parent_id].kind != ElementKind.TABLE_ROW
                ):
                    raise ValueError("table_cell parent must be table_row")

            for locator in element.locators:
                if locator.locator_type != expected_locator_type:
                    raise ValueError(
                        "locator type must match the document source type"
                    )

        _validate_acyclic(element_parents, hierarchy_name="element")
        return self


NormalizedDocumentInput = Union[NormalizedDocument, Mapping[str, Any]]


def validate_normalized_document(
    artifact: NormalizedDocumentInput,
) -> NormalizedDocument:
    payload = (
        artifact.model_dump(mode="json")
        if isinstance(artifact, NormalizedDocument)
        else artifact
    )
    return NormalizedDocument.model_validate(payload)


def canonical_normalized_document_bytes(
    artifact: NormalizedDocumentInput,
) -> bytes:
    document = validate_normalized_document(artifact)
    canonical_json = json.dumps(
        document.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return f"{canonical_json}\n".encode("utf-8")


def normalized_document_sha256(artifact: NormalizedDocumentInput) -> str:
    return hashlib.sha256(canonical_normalized_document_bytes(artifact)).hexdigest()
