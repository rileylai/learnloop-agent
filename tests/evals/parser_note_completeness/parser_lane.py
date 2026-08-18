"""Offline, benchmark-owned Parser lane projections for diagnostic runs.

This module deliberately does not call the application's network-backed or
plain-text ingestion adapters.  It projects only facts that can be read from
the project-owned fixture bytes and records unsupported observations with the
existing NormalizedDocument unavailable semantics.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Literal, Mapping, Optional, Sequence, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, ValidationError

from .full_profile import FullCase
from .normalized_document import (
    CAPABILITY_NAMES,
    ArtifactRole,
    CapabilityDeclaration,
    CapabilityStatus,
    Capabilities,
    ChatLocator,
    CodeMetadata,
    Element,
    ElementKind,
    HeaderRole,
    ListKind,
    ListMetadata,
    NormalizedDocument,
    PdfLocator,
    ProducerProvenance,
    ScreenshotLocator,
    Section,
    SourceMetadata,
    SourceType,
    TableCellMetadata,
    TypedIdentity,
    WebLocator,
    YouTubeLocator,
    canonical_normalized_document_bytes,
)
from .smoke_profile import SmokeCase


RUNNER_VERSION = "parser-note-completeness-runner/1.0.0"
PARSER_LANE_RESULT_SCHEMA_VERSION = "parser-lane-result/1.0.0"
PARSER_LANE_ATTEMPT_SCHEMA_VERSION = "parser-lane-attempt/1.0.0"
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_DIGEST_RE = re.compile(_DIGEST_PATTERN)
_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")

ProfileCase = Union[SmokeCase, FullCase]


class ParserLaneContractError(Exception):
    """A parser input or candidate contract was rejected."""


class ParserLaneOperationalError(Exception):
    """A deterministic parser could not complete its local work."""


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class ParserLaneResultArtifact(_StrictFrozenModel):
    schema_version: Literal["parser-lane-result/1.0.0"] = "parser-lane-result/1.0.0"
    runner_version: Literal["parser-note-completeness-runner/1.0.0"] = "parser-note-completeness-runner/1.0.0"
    artifact_type: Literal["parser_lane_diagnostic_result"] = "parser_lane_diagnostic_result"
    operation: Literal["parse_source"] = "parse_source"
    case_id: StrictStr = Field(min_length=1)
    source_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    producer_configuration_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    candidate_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    candidate_bytes: StrictInt = Field(ge=0)
    attempt_id: StrictStr = Field(min_length=1, pattern=_ID_PATTERN.pattern)
    status: Literal["contract_valid"] = "contract_valid"
    unavailable_capabilities: Tuple[StrictStr, ...] = ()


class ParserLaneAttemptArtifact(_StrictFrozenModel):
    schema_version: Literal["parser-lane-attempt/1.0.0"] = "parser-lane-attempt/1.0.0"
    runner_version: Literal["parser-note-completeness-runner/1.0.0"] = "parser-note-completeness-runner/1.0.0"
    artifact_type: Literal["parser_lane_diagnostic_attempt"] = "parser_lane_diagnostic_attempt"
    operation: Literal["parse_source"] = "parse_source"
    case_id: StrictStr = Field(min_length=1)
    source_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    producer_configuration_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    candidate_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    result_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    attempt_id: StrictStr = Field(min_length=1, pattern=_ID_PATTERN.pattern)
    status: Literal["contract_valid"] = "contract_valid"


ParserLaneArtifact = Union[ParserLaneResultArtifact, ParserLaneAttemptArtifact]


@dataclass(frozen=True)
class ParserLaneOutcome:
    exit_code: int
    status: str
    candidate_digest: Optional[str] = None
    result_digest: Optional[str] = None
    attempt_digest: Optional[str] = None
    unavailable_capabilities: Tuple[str, ...] = ()
    error: Optional[str] = None


def _canonical_model_bytes(model: BaseModel) -> bytes:
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


def canonical_parser_lane_artifact_bytes(
    payload: Union[ParserLaneArtifact, Mapping[str, Any]],
) -> bytes:
    if isinstance(payload, (ParserLaneResultArtifact, ParserLaneAttemptArtifact)):
        model = payload
    else:
        if not isinstance(payload, Mapping):
            raise TypeError("parser lane artifact must be a mapping or model")
        artifact_type = payload.get("artifact_type")
        if artifact_type == "parser_lane_diagnostic_result":
            model = ParserLaneResultArtifact.model_validate(payload)
        elif artifact_type == "parser_lane_diagnostic_attempt":
            model = ParserLaneAttemptArtifact.model_validate(payload)
        else:
            raise ValueError("unknown parser lane artifact type")
    return _canonical_model_bytes(model)


def parser_lane_artifact_sha256(
    payload: Union[ParserLaneArtifact, Mapping[str, Any]],
) -> str:
    return hashlib.sha256(canonical_parser_lane_artifact_bytes(payload)).hexdigest()


def _read_bounded_contract(root: Path, relative_path: str, label: str) -> bytes:
    try:
        root_resolved = root.resolve(strict=True)
        target = (root / relative_path).resolve(strict=True)
        target.relative_to(root_resolved)
        if not target.is_file():
            raise OSError("not a regular file")
        return target.read_bytes()
    except ValueError as exc:
        raise ParserLaneContractError(f"{label} outside benchmark root") from exc
    except OSError as exc:
        raise ParserLaneOperationalError(f"{label} unavailable") from exc


def _read_external_digest(data: bytes, expected_filename: str) -> str:
    try:
        fields = data.decode("ascii").strip().split()
    except UnicodeDecodeError as exc:
        raise ParserLaneContractError("invalid external digest record") from exc
    if len(fields) != 2 or fields[1] != expected_filename or _DIGEST_RE.fullmatch(fields[0]) is None:
        raise ParserLaneContractError("invalid external digest record")
    return fields[0]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _case_inputs(
    case: ProfileCase,
    benchmark_root: Path,
) -> Tuple[bytes, str, Dict[str, Any], str]:
    source_bytes = _read_bounded_contract(
        benchmark_root,
        case.source_artifact_path,
        "source artifact",
    )
    source_digest_bytes = _read_bounded_contract(
        benchmark_root,
        case.source_digest_path,
        "source checksum record",
    )
    source_record = _read_external_digest(
        source_digest_bytes,
        PurePosixPath(case.source_artifact_path).name,
    )
    actual_source_digest = _sha256(source_bytes)
    if source_record != case.source_sha256 or actual_source_digest != case.source_sha256:
        raise ParserLaneContractError("source digest binding mismatch")

    configuration_bytes = _read_bounded_contract(
        benchmark_root,
        case.producer_configuration_path,
        "producer configuration",
    )
    if _sha256(configuration_bytes) != case.producer_configuration_sha256:
        raise ParserLaneContractError("producer configuration digest mismatch")
    try:
        configuration = json.loads(configuration_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise ParserLaneContractError("producer configuration JSON is invalid") from exc
    if not isinstance(configuration, dict):
        raise ParserLaneContractError("producer configuration must be an object")
    return source_bytes, actual_source_digest, configuration, case.producer_configuration_sha256


_LANGUAGES = {
    "P01": ("en",),
    "P02": ("zh-Hant", "en"),
    "P03": ("zh-Hant",),
    "P04": ("zh-Hant", "en"),
    "W01": ("en",),
    "W02": ("zh-Hant", "en"),
    "W03": ("zh-Hant", "en"),
    "Y01": ("en",),
    "Y02": ("zh-Hant", "en"),
    "C01": ("en",),
    "C02": ("zh-Hant", "en"),
    "S01": ("en",),
    "S02": ("zh-Hant", "en"),
}


def _capability(status: CapabilityStatus, reason: Optional[str] = None) -> CapabilityDeclaration:
    return CapabilityDeclaration(status=status, reason=reason)


def _capabilities(
    *,
    hierarchy: Tuple[CapabilityStatus, Optional[str]],
    language: Tuple[CapabilityStatus, Optional[str]],
    geometry: Tuple[CapabilityStatus, Optional[str]],
    table: Tuple[CapabilityStatus, Optional[str]],
    code: Tuple[CapabilityStatus, Optional[str]],
    source_modality: Tuple[CapabilityStatus, Optional[str]],
    locators: Tuple[CapabilityStatus, Optional[str]],
) -> Capabilities:
    return Capabilities(
        hierarchy=_capability(*hierarchy),
        language_identification=_capability(*language),
        geometry=_capability(*geometry),
        table_structure=_capability(*table),
        code_metadata=_capability(*code),
        source_modality=_capability(*source_modality),
        typed_locators=_capability(*locators),
    )


def _element(
    *,
    case_id: str,
    order: int,
    kind: ElementKind,
    section_id: str,
    languages: Tuple[str, ...],
    locator: Any,
    content: Optional[str] = None,
    parent_element_id: Optional[str] = None,
    list_metadata: Optional[ListMetadata] = None,
    table_cell_metadata: Optional[Any] = None,
    code_metadata: Optional[CodeMetadata] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "element_id": f"{case_id.lower()}-element-{order:04d}",
        "kind": kind,
        "order": order,
        "section_id": section_id,
        "languages": languages,
        "locators": (locator,),
    }
    if content is not None:
        payload["content"] = content
    if parent_element_id is not None:
        payload["parent_element_id"] = parent_element_id
    if list_metadata is not None:
        payload["list_metadata"] = list_metadata
    if table_cell_metadata is not None:
        payload["table_cell_metadata"] = table_cell_metadata
    if code_metadata is not None:
        payload["code_metadata"] = code_metadata
    return payload


def _build_document(
    *,
    case_id: str,
    source_type: SourceType,
    source_digest: str,
    configuration_digest: str,
    elements: Sequence[Mapping[str, Any]],
    capabilities: Capabilities,
    processing_method: str,
    segmentation_semantics: str,
    source_identity: Optional[str] = None,
    display_name: Optional[str] = None,
) -> NormalizedDocument:
    if not elements:
        raise ParserLaneContractError("parser produced no representable elements")
    materialized_elements = tuple(Element.model_validate(dict(element)) for element in elements)
    heading_id = next(
        (element.element_id for element in materialized_elements if element.kind == ElementKind.HEADING),
        None,
    )
    document = NormalizedDocument(
        schema_version="normalized-document/1.0.0",
        artifact_role=ArtifactRole.PARSER_OUTPUT,
        document_id=case_id,
        source=SourceMetadata(
            source_type=source_type,
            source_identity=source_identity or f"project-owned-{case_id}-revision-001",
            display_name=display_name or f"{case_id} diagnostic source",
            source_snapshot_sha256=source_digest,
            languages=_LANGUAGES[case_id],
        ),
        capabilities=capabilities,
        sections=(
            Section(
                section_id="section-0",
                heading_element_id=heading_id,
                start_order=0,
                end_order=len(materialized_elements) - 1,
            ),
        ),
        elements=materialized_elements,
        producer_provenance=ProducerProvenance(
            producer_name="parser-note-completeness-diagnostic-parser",
            producer_version="1.0.0",
            configuration_sha256=configuration_digest,
            segmentation_semantics=segmentation_semantics,
            processing_method=processing_method,
            processing_stage="parser_lane_diagnostic",
        ),
    )
    return document


def _unavailable_capabilities(document: NormalizedDocument) -> Tuple[str, ...]:
    unavailable: List[str] = []
    for name in CAPABILITY_NAMES:
        declaration = getattr(document.capabilities, name)
        if declaration.status in {CapabilityStatus.PARTIAL, CapabilityStatus.UNAVAILABLE}:
            unavailable.append(name)
    return tuple(unavailable)


def _pdf_candidate(
    case_id: str,
    source_bytes: bytes,
    source_digest: str,
    configuration_digest: str,
) -> NormalizedDocument:
    try:
        from pypdf import PdfReader
    except ModuleNotFoundError as exc:
        raise ParserLaneOperationalError("PDF parser dependency unavailable") from exc
    try:
        reader = PdfReader(BytesIO(source_bytes))
        page_texts = []
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = (page.extract_text() or "").strip()
            except Exception as exc:
                raise ParserLaneOperationalError("PDF parser execution failed") from exc
            page_texts.append((page_number, text))
    except ParserLaneOperationalError:
        raise
    except Exception as exc:
        raise ParserLaneOperationalError("PDF parser execution failed") from exc

    elements: List[Mapping[str, Any]] = []
    for page_number, text in page_texts:
        locator = PdfLocator(locator_type="pdf", status="available", page=page_number)
        if text:
            elements.append(
                _element(
                    case_id=case_id,
                    order=len(elements),
                    kind=ElementKind.PARAGRAPH,
                    section_id="section-0",
                    languages=_LANGUAGES[case_id],
                    locator=locator,
                    content=text,
                )
            )
        else:
            elements.append(
                _element(
                    case_id=case_id,
                    order=len(elements),
                    kind=ElementKind.PAGE_BREAK,
                    section_id="section-0",
                    languages=_LANGUAGES[case_id],
                    locator=locator,
                )
            )
    return _build_document(
        case_id=case_id,
        source_type=SourceType.PDF,
        source_digest=source_digest,
        configuration_digest=configuration_digest,
        elements=elements,
        capabilities=_capabilities(
            hierarchy=(CapabilityStatus.PARTIAL, "pdf_page_text_projection"),
            language=(CapabilityStatus.PARTIAL, "source_declared_languages"),
            geometry=(CapabilityStatus.UNAVAILABLE, "pdf_geometry_not_projected"),
            table=(CapabilityStatus.UNAVAILABLE, "pdf_table_structure_not_projected"),
            code=(CapabilityStatus.UNAVAILABLE, "pdf_code_metadata_not_projected"),
            source_modality=(CapabilityStatus.AVAILABLE, None),
            locators=(CapabilityStatus.AVAILABLE, None),
        ),
        processing_method="deterministic_pdf_text_projection",
        segmentation_semantics="parser-lane-pdf-page-text-v1",
    )


@dataclass
class _WebNode:
    tag: str
    path: str
    attrs: Dict[str, str]
    text_parts: List[str]
    element_id: Optional[str] = None
    kind: Optional[ElementKind] = None
    parent_element_id: Optional[str] = None
    code_language: Optional[str] = None
    table_row_index: Optional[int] = None
    table_column_index: Optional[int] = None
    table_header: bool = False


class _WebDiagnosticParser(HTMLParser):
    _VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"})
    _TEXT_BLOCKS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "caption", "td", "th"}

    def __init__(self, case_id: str, source_digest: str) -> None:
        super().__init__(convert_charrefs=True)
        self.case_id = case_id
        self.source_digest = source_digest
        self.stack: List[_WebNode] = []
        self.child_counts: List[Dict[str, int]] = []
        self.elements: List[Mapping[str, Any]] = []
        self.has_table = False
        self.has_code = False
        self.has_figure = False
        self.list_depth = 0
        self.table_rows: List[Tuple[str, int]] = []
        self.current_row_cells: List[int] = []

    def _path_for(self, tag: str) -> str:
        if not self.child_counts:
            return f"{tag}[1]"
        counts = self.child_counts[-1]
        counts[tag] = counts.get(tag, 0) + 1
        prefix = self.stack[-1].path if self.stack else ""
        return f"{prefix}/{tag}[{counts[tag]}]"

    def _locator(self, path: str) -> WebLocator:
        return WebLocator(
            locator_type="web",
            status="available",
            snapshot_sha256=self.source_digest,
            dom_path=path,
        )

    def _append_nontext(self, node: _WebNode, kind: ElementKind, parent_id: Optional[str] = None) -> None:
        node.element_id = f"{self.case_id.lower()}-element-{len(self.elements):04d}"
        node.kind = kind
        node.parent_element_id = parent_id
        self.elements.append(
            _element(
                case_id=self.case_id,
                order=len(self.elements),
                kind=kind,
                section_id="section-0",
                languages=_LANGUAGES[self.case_id],
                locator=self._locator(node.path),
                parent_element_id=parent_id,
            )
        )

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        normalized_tag = tag.casefold()
        if normalized_tag in self._VOID_TAGS:
            return
        attr_map = {name.casefold(): value or "" for name, value in attrs}
        path = self._path_for(normalized_tag)
        node = _WebNode(normalized_tag, path, attr_map, [])
        parent_id = self.stack[-1].element_id if self.stack and self.stack[-1].kind == ElementKind.FIGURE else None
        if normalized_tag == "table":
            self.has_table = True
            self._append_nontext(node, ElementKind.TABLE)
            self.table_rows.append((node.element_id or "", 0))
        elif normalized_tag == "tr":
            table_id = self.table_rows[-1][0] if self.table_rows else None
            row_index = self.table_rows[-1][1] if self.table_rows else 0
            self._append_nontext(node, ElementKind.TABLE_ROW, table_id)
            node.table_row_index = row_index
            if self.table_rows:
                self.table_rows[-1] = (self.table_rows[-1][0], self.table_rows[-1][1] + 1)
            self.current_row_cells.append(0)
        elif normalized_tag in {"td", "th"}:
            row_node = next((candidate for candidate in reversed(self.stack) if candidate.tag == "tr"), None)
            row_id = row_node.element_id if row_node is not None else None
            column_index = self.current_row_cells[-1] if self.current_row_cells else 0
            if self.current_row_cells:
                self.current_row_cells[-1] += 1
            node.kind = ElementKind.TABLE_CELL
            node.parent_element_id = row_id
            node.table_row_index = row_node.table_row_index if row_node is not None else 0
            node.table_column_index = column_index
            node.table_header = normalized_tag == "th"
        elif normalized_tag == "figure":
            self.has_figure = True
            self._append_nontext(node, ElementKind.FIGURE)
        elif normalized_tag in {"ul", "ol"}:
            self.list_depth += 1
        elif normalized_tag == "code" and self.stack and self.stack[-1].tag == "pre":
            language = attr_map.get("class", "")
            node_language = next((part.removeprefix("language-") for part in language.split() if part.startswith("language-")), None)
            self.stack[-1].code_language = node_language or "plain-text"
            self.has_code = True
        self.stack.append(node)
        self.child_counts.append({})

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1].tag == tag.casefold():
            self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        for node in self.stack:
            node.text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.casefold()
        if not self.stack:
            return
        index = next((index for index in range(len(self.stack) - 1, -1, -1) if self.stack[index].tag == normalized_tag), None)
        if index is None:
            return
        while len(self.stack) > index:
            node = self.stack.pop()
            self.child_counts.pop()
            self._close_node(node)

    def _close_node(self, node: _WebNode) -> None:
        if node.tag in {"ul", "ol"}:
            self.list_depth = max(self.list_depth - 1, 0)
            return
        if node.tag == "tr" and self.current_row_cells:
            self.current_row_cells.pop()
            return
        if node.tag == "table" and self.table_rows:
            self.table_rows.pop()
            return
        if node.tag not in self._TEXT_BLOCKS:
            return
        raw_text = "".join(node.text_parts)
        content = raw_text.strip() if node.tag != "pre" else raw_text.strip("\n")
        if not content:
            return
        kind = (
            ElementKind.HEADING if node.tag.startswith("h") else
            ElementKind.LIST_ITEM if node.tag == "li" else
            ElementKind.CODE_BLOCK if node.tag == "pre" else
            ElementKind.CAPTION if node.tag == "caption" else
            ElementKind.TABLE_CELL if node.tag in {"td", "th"} else
            ElementKind.PARAGRAPH
        )
        parent_id = node.parent_element_id
        if kind == ElementKind.CAPTION:
            parent_id = next((candidate.element_id for candidate in reversed(self.stack) if candidate.tag == "figure"), None)
        list_metadata = None
        if kind == ElementKind.LIST_ITEM:
            parent_list = next((candidate for candidate in reversed(self.stack) if candidate.tag in {"ul", "ol"}), None)
            list_metadata = ListMetadata(
                list_kind=ListKind.ORDERED if parent_list and parent_list.tag == "ol" else ListKind.UNORDERED,
                nesting_level=max(self.list_depth, 1),
            )
        code_metadata = None
        if kind == ElementKind.CODE_BLOCK:
            code_metadata = CodeMetadata(
                language_hint=node.code_language or "plain-text",
                source_supplied=node.code_language is not None,
            )
        table_cell_metadata = None
        if kind == ElementKind.TABLE_CELL:
            table_cell_metadata = TableCellMetadata(
                row_index=node.table_row_index or 0,
                column_index=node.table_column_index or 0,
                header_role=HeaderRole.COLUMN if node.table_header else None,
            )
        element = _element(
            case_id=self.case_id,
            order=len(self.elements),
            kind=kind,
            section_id="section-0",
            languages=_LANGUAGES[self.case_id],
            locator=self._locator(node.path),
            content=content,
            parent_element_id=parent_id,
            list_metadata=list_metadata,
            table_cell_metadata=table_cell_metadata,
            code_metadata=code_metadata,
        )
        self.elements.append(element)


def _web_candidate(
    case_id: str,
    source_bytes: bytes,
    source_digest: str,
    configuration_digest: str,
) -> NormalizedDocument:
    try:
        html = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ParserLaneContractError("web source is not UTF-8") from exc
    parser = _WebDiagnosticParser(case_id, source_digest)
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        raise ParserLaneOperationalError("web parser execution failed") from exc
    return _build_document(
        case_id=case_id,
        source_type=SourceType.WEB,
        source_digest=source_digest,
        configuration_digest=configuration_digest,
        elements=parser.elements,
        capabilities=_capabilities(
            hierarchy=(CapabilityStatus.PARTIAL, "flat_section_projection"),
            language=(CapabilityStatus.PARTIAL, "source_declared_languages"),
            geometry=(CapabilityStatus.UNAVAILABLE, "dom_geometry_not_projected"),
            table=(CapabilityStatus.AVAILABLE, None) if parser.has_table else (CapabilityStatus.NOT_APPLICABLE, None),
            code=(CapabilityStatus.AVAILABLE, None) if parser.has_code else (CapabilityStatus.NOT_APPLICABLE, None),
            source_modality=(CapabilityStatus.AVAILABLE, None),
            locators=(CapabilityStatus.AVAILABLE, None),
        ),
        processing_method="deterministic_html_structure_projection",
        segmentation_semantics="parser-lane-web-blocks-v1",
    )


def _parse_timestamp(value: str) -> int:
    match = re.fullmatch(r"(\d+):(\d{2}):(\d{2})\.(\d{3})", value.strip())
    if match is None:
        raise ParserLaneContractError("invalid WebVTT timestamp")
    hours, minutes, seconds, milliseconds = (int(part) for part in match.groups())
    if minutes >= 60 or seconds >= 60:
        raise ParserLaneContractError("invalid WebVTT timestamp")
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + milliseconds


def _parse_vtt(data: bytes) -> List[Tuple[int, int, str]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ParserLaneContractError("caption source is not UTF-8") from exc
    lines = text.splitlines()
    if not lines or lines[0].strip() != "WEBVTT":
        raise ParserLaneContractError("caption source is not WebVTT")
    cues: List[Tuple[int, int, str]] = []
    index = 1
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if "-->" not in line:
            index += 1
            continue
        start_text, end_text = (part.strip() for part in line.split("-->", 1))
        start_ms = _parse_timestamp(start_text)
        end_ms = _parse_timestamp(end_text.split()[0])
        index += 1
        cue_lines: List[str] = []
        while index < len(lines) and lines[index].strip():
            cue_lines.append(lines[index])
            index += 1
        content = "\n".join(cue_lines).strip()
        if not content or end_ms < start_ms:
            raise ParserLaneContractError("invalid WebVTT cue")
        cues.append((start_ms, end_ms, content))
    if not cues:
        raise ParserLaneContractError("caption source has no cues")
    return cues


def _component_path(base: str, relative: str) -> str:
    path = PurePosixPath(relative)
    if (
        path.is_absolute()
        or "\\" in relative
        or any(part in {"", ".", ".."} for part in relative.split("/"))
    ):
        raise ParserLaneContractError(f"{base} component path is invalid")
    return str(path)


def _youtube_candidate(
    case: ProfileCase,
    benchmark_root: Path,
    source_bytes: bytes,
    source_digest: str,
    configuration_digest: str,
) -> NormalizedDocument:
    try:
        snapshot = json.loads(source_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise ParserLaneContractError("YouTube source snapshot JSON is invalid") from exc
    if not isinstance(snapshot, dict) or snapshot.get("source_type") != "youtube":
        raise ParserLaneContractError("YouTube source snapshot contract is invalid")
    components = snapshot.get("components")
    if not isinstance(components, list):
        raise ParserLaneContractError("YouTube source components are invalid")
    case_root = PurePosixPath(case.source_artifact_path).parent.as_posix()
    captions: Optional[bytes] = None
    for component in components:
        if not isinstance(component, dict) or not isinstance(component.get("path"), str) or not isinstance(component.get("sha256"), str):
            raise ParserLaneContractError("YouTube source component is invalid")
        relative = _component_path("YouTube", component["path"])
        component_relative = f"{case_root}/{relative}"
        component_bytes = _read_bounded_contract(benchmark_root, component_relative, "YouTube component")
        component_digest = _sha256(component_bytes)
        if component_digest != component["sha256"]:
            raise ParserLaneContractError("YouTube component digest mismatch")
        digest_relative = f"{case_root}/{PurePosixPath(relative).with_suffix('.sha256').as_posix()}"
        record = _read_bounded_contract(benchmark_root, digest_relative, "YouTube component checksum record")
        if _read_external_digest(record, PurePosixPath(relative).name) != component_digest:
            raise ParserLaneContractError("YouTube component checksum mismatch")
        if relative.endswith("captions.vtt"):
            captions = component_bytes
    if captions is None:
        raise ParserLaneContractError("YouTube caption component is missing")

    identity_reason = "synthetic_platform_identity_unavailable"
    elements: List[Mapping[str, Any]] = []
    for cue_index, (start_ms, end_ms, content) in enumerate(_parse_vtt(captions)):
        locator = YouTubeLocator(
            locator_type="youtube",
            status="available",
            video_identity=TypedIdentity(status="unavailable", reason=identity_reason),
            caption_track_identity=TypedIdentity(status="unavailable", reason=identity_reason),
            cue_index=cue_index,
            start_ms=start_ms,
            end_ms=end_ms,
        )
        elements.append(
            _element(
                case_id=case.case_id,
                order=len(elements),
                kind=ElementKind.TRANSCRIPT_SEGMENT,
                section_id="section-0",
                languages=_LANGUAGES[case.case_id],
                locator=locator,
                content=content,
            )
        )
    return _build_document(
        case_id=case.case_id,
        source_type=SourceType.YOUTUBE,
        source_digest=source_digest,
        configuration_digest=configuration_digest,
        elements=elements,
        capabilities=_capabilities(
            hierarchy=(CapabilityStatus.PARTIAL, "chapter_structure_not_projected"),
            language=(CapabilityStatus.PARTIAL, "caption_languages_declared"),
            geometry=(CapabilityStatus.NOT_APPLICABLE, None),
            table=(CapabilityStatus.NOT_APPLICABLE, None),
            code=(CapabilityStatus.NOT_APPLICABLE, None),
            source_modality=(CapabilityStatus.AVAILABLE, None),
            locators=(CapabilityStatus.AVAILABLE, None),
        ),
        processing_method="deterministic_offline_webvtt_projection",
        segmentation_semantics="parser-lane-youtube-cues-v1",
    )


def _chat_candidate(
    case_id: str,
    source_bytes: bytes,
    source_digest: str,
    configuration_digest: str,
) -> NormalizedDocument:
    try:
        source = json.loads(source_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise ParserLaneContractError("chat source JSON is invalid") from exc
    if not isinstance(source, dict) or not isinstance(source.get("messages"), list):
        raise ParserLaneContractError("chat source contract is invalid")
    elements: List[Mapping[str, Any]] = []
    has_code = False
    conversation_id = source.get("conversation_id")
    if not isinstance(conversation_id, str) or not conversation_id:
        raise ParserLaneContractError("chat conversation identity is invalid")
    for expected_sequence, message in enumerate(source["messages"]):
        if not isinstance(message, dict):
            raise ParserLaneContractError("chat message is invalid")
        message_id = message.get("message_id")
        sequence = message.get("sequence")
        text = message.get("text")
        thread_id = message.get("thread_id")
        if not isinstance(message_id, str) or not isinstance(sequence, int) or sequence != expected_sequence or not isinstance(text, str) or not text.strip() or not isinstance(thread_id, str):
            raise ParserLaneContractError("chat message binding is invalid")
        locator_kwargs = {
            "locator_type": "chat",
            "status": "available",
            "message_id": message_id,
            "source_sequence": sequence,
            "thread_id": thread_id,
            "reply_to_message_id": message.get("reply_to_message_id"),
        }
        message_locator = ChatLocator.model_validate(locator_kwargs)
        message_id_element = f"{case_id.lower()}-element-{len(elements):04d}"
        elements.append(
            _element(
                case_id=case_id,
                order=len(elements),
                kind=ElementKind.MESSAGE,
                section_id="section-0",
                languages=_LANGUAGES[case_id],
                locator=message_locator,
                content=text,
            )
        )
        parts = message.get("parts", [])
        if not isinstance(parts, list):
            raise ParserLaneContractError("chat message parts are invalid")
        for part in parts:
            if not isinstance(part, dict) or not isinstance(part.get("kind"), str) or not isinstance(part.get("text"), str):
                raise ParserLaneContractError("chat message part is invalid")
            kind_name = part["kind"]
            if kind_name == "text":
                continue
            if kind_name == "quote":
                kind = ElementKind.QUOTE
            elif kind_name == "code":
                kind = ElementKind.CODE_BLOCK
                has_code = True
            else:
                raise ParserLaneContractError("unsupported chat message part")
            locator = ChatLocator.model_validate(locator_kwargs)
            code_metadata = None
            if kind == ElementKind.CODE_BLOCK:
                language_hint = part.get("language")
                if not isinstance(language_hint, str) or not language_hint:
                    raise ParserLaneContractError("chat code language is invalid")
                code_metadata = CodeMetadata(language_hint=language_hint, source_supplied=True)
            elements.append(
                _element(
                    case_id=case_id,
                    order=len(elements),
                    kind=kind,
                    section_id="section-0",
                    languages=_LANGUAGES[case_id],
                    locator=locator,
                    content=part["text"],
                    parent_element_id=message_id_element,
                    code_metadata=code_metadata,
                )
            )
    return _build_document(
        case_id=case_id,
        source_type=SourceType.CHAT,
        source_digest=source_digest,
        configuration_digest=configuration_digest,
        elements=elements,
        capabilities=_capabilities(
            hierarchy=(CapabilityStatus.AVAILABLE, None),
            language=(CapabilityStatus.PARTIAL, "source_declared_languages"),
            geometry=(CapabilityStatus.NOT_APPLICABLE, None),
            table=(CapabilityStatus.NOT_APPLICABLE, None),
            code=(CapabilityStatus.AVAILABLE, None) if has_code else (CapabilityStatus.NOT_APPLICABLE, None),
            source_modality=(CapabilityStatus.AVAILABLE, None),
            locators=(CapabilityStatus.AVAILABLE, None),
        ),
        processing_method="deterministic_structured_chat_projection",
        segmentation_semantics="parser-lane-chat-messages-v1",
        source_identity=conversation_id,
    )


def _screenshot_images(
    case: ProfileCase,
    benchmark_root: Path,
    source_bytes: bytes,
) -> List[Tuple[int, str]]:
    case_root = PurePosixPath(case.source_artifact_path).parent.as_posix()
    if case.case_id == "S01":
        return [(1, case.source_sha256)]
    try:
        manifest = json.loads(source_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise ParserLaneContractError("screenshot manifest JSON is invalid") from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("images"), list):
        raise ParserLaneContractError("screenshot manifest contract is invalid")
    images: List[Tuple[int, str]] = []
    for expected_index, item in enumerate(manifest["images"], start=1):
        if not isinstance(item, dict) or item.get("image_index") != expected_index or not isinstance(item.get("path"), str) or not isinstance(item.get("sha256"), str):
            raise ParserLaneContractError("screenshot image manifest is invalid")
        relative = _component_path("screenshot", item["path"])
        image_relative = f"{case_root}/{relative}"
        image_bytes = _read_bounded_contract(benchmark_root, image_relative, "screenshot image")
        image_digest = _sha256(image_bytes)
        if image_digest != item["sha256"]:
            raise ParserLaneContractError("screenshot image digest mismatch")
        record_relative = f"{case_root}/{PurePosixPath(relative).with_suffix('.sha256').as_posix()}"
        record = _read_bounded_contract(benchmark_root, record_relative, "screenshot image checksum record")
        if _read_external_digest(record, PurePosixPath(relative).name) != image_digest:
            raise ParserLaneContractError("screenshot image checksum mismatch")
        images.append((expected_index, image_digest))
    if not images:
        raise ParserLaneContractError("screenshot manifest has no images")
    return images


def _screenshot_candidate(
    case: ProfileCase,
    benchmark_root: Path,
    source_bytes: bytes,
    source_digest: str,
    configuration_digest: str,
) -> NormalizedDocument:
    elements: List[Mapping[str, Any]] = []
    for image_index, image_digest in _screenshot_images(case, benchmark_root, source_bytes):
        locator = ScreenshotLocator(
            locator_type="screenshots",
            status="available",
            image_index=image_index,
            image_sha256=image_digest,
        )
        elements.append(
            _element(
                case_id=case.case_id,
                order=len(elements),
                kind=ElementKind.PAGE_BREAK,
                section_id="section-0",
                languages=_LANGUAGES[case.case_id],
                locator=locator,
            )
        )
    return _build_document(
        case_id=case.case_id,
        source_type=SourceType.SCREENSHOTS,
        source_digest=source_digest,
        configuration_digest=configuration_digest,
        elements=elements,
        capabilities=_capabilities(
            hierarchy=(CapabilityStatus.NOT_APPLICABLE, None),
            language=(CapabilityStatus.UNAVAILABLE, "ocr_not_run"),
            geometry=(CapabilityStatus.UNAVAILABLE, "ocr_geometry_not_projected"),
            table=(CapabilityStatus.NOT_APPLICABLE, None),
            code=(CapabilityStatus.NOT_APPLICABLE, None),
            source_modality=(CapabilityStatus.AVAILABLE, None),
            locators=(CapabilityStatus.AVAILABLE, None),
        ),
        processing_method="deterministic_screenshot_identity_projection",
        segmentation_semantics="parser-lane-screenshot-images-v1",
        source_identity=f"project-owned-{case.case_id}-image-set",
    )


def build_parser_candidate(
    case: ProfileCase,
    benchmark_root: Path,
) -> Tuple[NormalizedDocument, str, str, Tuple[str, ...]]:
    """Parse one profile case and return candidate plus binding facts."""

    source_bytes, source_digest, configuration, configuration_digest = _case_inputs(
        case,
        benchmark_root,
    )
    _ = configuration
    if case.case_id.startswith("P"):
        document = _pdf_candidate(case.case_id, source_bytes, source_digest, configuration_digest)
    elif case.case_id.startswith("W"):
        document = _web_candidate(case.case_id, source_bytes, source_digest, configuration_digest)
    elif case.case_id.startswith("Y"):
        document = _youtube_candidate(case, benchmark_root, source_bytes, source_digest, configuration_digest)
    elif case.case_id.startswith("C"):
        document = _chat_candidate(case.case_id, source_bytes, source_digest, configuration_digest)
    elif case.case_id.startswith("S"):
        document = _screenshot_candidate(case, benchmark_root, source_bytes, source_digest, configuration_digest)
    else:
        raise ParserLaneContractError("unsupported parser case family")
    if document.source.source_snapshot_sha256 != source_digest:
        raise ParserLaneContractError("candidate source binding mismatch")
    if document.producer_provenance.configuration_sha256 != configuration_digest:
        raise ParserLaneContractError("candidate configuration binding mismatch")
    candidate_bytes = canonical_normalized_document_bytes(document)
    if NormalizedDocument.model_validate(json.loads(candidate_bytes)) != document:
        raise ParserLaneContractError("candidate canonical validation failed")
    return document, source_digest, configuration_digest, _unavailable_capabilities(document)


def _write_once(path: Path, data: bytes) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
    except FileExistsError as exc:
        raise ParserLaneOperationalError("parser output already exists") from exc
    except OSError as exc:
        raise ParserLaneOperationalError("parser output write failed") from exc


def _write_external(path: Path, data: bytes) -> str:
    digest = _sha256(data)
    _write_once(path, data)
    try:
        _write_once(path.with_suffix(".sha256"), f"{digest}  {path.name}\n".encode("ascii"))
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    return digest


def execute_parser_case(
    case: ProfileCase,
    benchmark_root: Path,
    output_dir: Path,
    *,
    attempt_id: str,
) -> ParserLaneOutcome:
    """Run one deterministic parser case and write candidate/result artifacts."""

    try:
        document, source_digest, configuration_digest, unavailable = build_parser_candidate(
            case,
            benchmark_root,
        )
        candidate_bytes = canonical_normalized_document_bytes(document)
        candidate_digest = _write_external(output_dir / "candidate.json", candidate_bytes)
        result_model = ParserLaneResultArtifact(
            case_id=case.case_id,
            source_sha256=source_digest,
            producer_configuration_sha256=configuration_digest,
            candidate_sha256=candidate_digest,
            candidate_bytes=len(candidate_bytes),
            attempt_id=attempt_id,
            unavailable_capabilities=unavailable,
        )
        result_bytes = canonical_parser_lane_artifact_bytes(result_model)
        result_digest = _write_external(output_dir / "result.json", result_bytes)
        attempt_model = ParserLaneAttemptArtifact(
            case_id=case.case_id,
            source_sha256=source_digest,
            producer_configuration_sha256=configuration_digest,
            candidate_sha256=candidate_digest,
            result_sha256=result_digest,
            attempt_id=attempt_id,
        )
        attempt_bytes = canonical_parser_lane_artifact_bytes(attempt_model)
        attempt_digest = _write_external(output_dir / "attempt.json", attempt_bytes)
        return ParserLaneOutcome(
            0,
            "contract_valid",
            candidate_digest=candidate_digest,
            result_digest=result_digest,
            attempt_digest=attempt_digest,
            unavailable_capabilities=unavailable,
        )
    except ParserLaneContractError as exc:
        return ParserLaneOutcome(2, "invalid_input", error=str(exc))
    except ParserLaneOperationalError as exc:
        return ParserLaneOutcome(1, "operational_failure", error=str(exc))
    except (OSError, ValidationError) as exc:
        return ParserLaneOutcome(1, "operational_failure", error="parser execution failed")


__all__ = [
    "PARSER_LANE_ATTEMPT_SCHEMA_VERSION",
    "PARSER_LANE_RESULT_SCHEMA_VERSION",
    "ParserLaneAttemptArtifact",
    "ParserLaneContractError",
    "ParserLaneOutcome",
    "ParserLaneResultArtifact",
    "build_parser_candidate",
    "canonical_parser_lane_artifact_bytes",
    "execute_parser_case",
    "parser_lane_artifact_sha256",
]
