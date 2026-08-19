"""Deterministic offline renderer and Q26 projection readback."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Annotated, Any, Literal, Mapping, Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field, StrictStr, model_validator

from .benchmark_note import (
    BENCHMARK_NOTE_SCHEMA_VERSION,
    CaptureMethod,
    LineageMappingShape,
    LineageMappingState,
    LineageParentRole,
    NoteLineage,
    NoteLineageMapping,
    NoteNode,
    NoteNodeKind,
    NoteProducerProvenance,
    NoteProducerRole,
    RenderedNoteProjection,
    benchmark_note_mapping_id,
    benchmark_note_sha256,
    canonical_benchmark_note_bytes,
    validate_benchmark_note_artifact,
    BenchmarkNoteDocument,
)

RENDERER_ID = "benchmark-deterministic-html-renderer"
RENDERER_VERSION = "1.0.0"
RENDERER_CONFIGURATION_SCHEMA_VERSION = "benchmark-html-renderer-configuration/1.0.0"
RENDERER_CAPTURE_SCHEMA_VERSION = "benchmark-renderer-capture/1.0.0"
RENDERER_PROCESSING_METHOD = "q26_note_to_canonical_html"
RENDERER_PROCESSING_STAGE = "rendered_projection_capture"
RENDERER_CAPTURE_METHOD = CaptureMethod.AUTHORITATIVE_OUTPUT

_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]
Identifier = Annotated[StrictStr, Field(pattern=_ID_PATTERN)]
CaptureId = Annotated[StrictStr, Field(pattern=r"^capture-[0-9a-f]{64}$")]


class RendererContractError(ValueError):
    """Renderer, capture, or projection contract rejection."""


class RendererOperationalError(Exception):
    """Renderer or immutable-store operational failure."""


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class RendererCaptureArtifact(_StrictFrozenModel):
    schema_version: Literal["benchmark-renderer-capture/1.0.0"] = (
        "benchmark-renderer-capture/1.0.0"
    )
    artifact_role: Literal["renderer_capture"] = "renderer_capture"
    capture_id: CaptureId
    document_id: Identifier
    reference_document_sha256: Digest
    pre_render_note_sha256: Digest
    renderer_output_sha256: Digest
    producer_provenance: NoteProducerProvenance

    @model_validator(mode="after")
    def _validate_contract(self) -> "RendererCaptureArtifact":
        provenance = self.producer_provenance
        if provenance.producer_role != NoteProducerRole.RENDERER:
            raise ValueError("renderer capture requires renderer provenance")
        if provenance.producer_name != RENDERER_ID:
            raise ValueError("renderer identity mismatch")
        if provenance.producer_version != RENDERER_VERSION:
            raise ValueError("renderer version mismatch")
        if provenance.processing_method != RENDERER_PROCESSING_METHOD:
            raise ValueError("renderer processing method mismatch")
        if provenance.processing_stage != RENDERER_PROCESSING_STAGE:
            raise ValueError("renderer processing stage mismatch")
        if provenance.capture_method != RENDERER_CAPTURE_METHOD:
            raise ValueError("renderer capture method must be authoritative_output")
        return self


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def renderer_configuration_payload() -> dict[str, Any]:
    return {
        "schema_version": RENDERER_CONFIGURATION_SCHEMA_VERSION,
        "renderer_id": RENDERER_ID,
        "renderer_version": RENDERER_VERSION,
        "document_wrapper": "html5-head-body-article",
        "charset": "utf-8",
        "line_endings": "lf",
        "trailing_newline": False,
        "whitespace": "compact",
        "external_resources": "forbidden",
        "scripts": "forbidden",
        "styles": "forbidden",
        "attribute_escape": "html5-fixed-v1",
        "node_tag_policy": "closed-q26-kind-map-v1",
        "citation_policy": "empty-span-markers-v1",
        "mapping_policy": "data-node-id-one-to-one-v1",
        "unsupported_node_policy": "typed-div",
    }


def canonical_renderer_configuration_bytes() -> bytes:
    return _canonical_json_bytes(renderer_configuration_payload())


def renderer_configuration_sha256() -> str:
    return _sha256(canonical_renderer_configuration_bytes())


def canonical_renderer_capture_bytes(
    payload: RendererCaptureArtifact | Mapping[str, Any],
) -> bytes:
    artifact = (
        payload
        if isinstance(payload, RendererCaptureArtifact)
        else RendererCaptureArtifact.model_validate(payload)
    )
    return _canonical_json_bytes(artifact.model_dump(mode="json"))


def renderer_capture_sha256(
    payload: RendererCaptureArtifact | Mapping[str, Any],
) -> str:
    return _sha256(canonical_renderer_capture_bytes(payload))


def renderer_provenance() -> NoteProducerProvenance:
    return NoteProducerProvenance(
        producer_role=NoteProducerRole.RENDERER,
        producer_name=RENDERER_ID,
        producer_version=RENDERER_VERSION,
        configuration_sha256=renderer_configuration_sha256(),
        processing_method=RENDERER_PROCESSING_METHOD,
        processing_stage=RENDERER_PROCESSING_STAGE,
        capture_method=RENDERER_CAPTURE_METHOD,
    )


_TAG_BY_KIND = {
    NoteNodeKind.HEADING: "h2",
    NoteNodeKind.PARAGRAPH: "p",
    NoteNodeKind.TRANSCRIPT_SEGMENT: "p",
    NoteNodeKind.MESSAGE: "p",
    NoteNodeKind.LIST_ITEM: "div",
    NoteNodeKind.TABLE_ROW: "div",
    NoteNodeKind.TABLE_CELL: "div",
    NoteNodeKind.FORMULA: "div",
    NoteNodeKind.QUOTE: "blockquote",
    NoteNodeKind.CODE_BLOCK: "pre",
    NoteNodeKind.TABLE: "section",
    NoteNodeKind.FIGURE: "figure",
    NoteNodeKind.CAPTION: "figcaption",
}


def _normalize_line_endings(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _escape_text(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _escape_attribute(value: str) -> str:
    return (
        _escape_text(value)
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def _attributes(items: Sequence[tuple[str, str]]) -> str:
    return "".join(
        f' {name}="{_escape_attribute(value)}"' for name, value in items
    )


def _node_metadata(node: NoteNode) -> str:
    payload = node.model_dump(
        mode="json",
        include={
            "parent_node_id",
            "languages",
            "list_metadata",
            "table_cell_metadata",
            "code_metadata",
            "citations",
        },
    )
    return _canonical_json_bytes(payload).decode("utf-8")


def _citation_marker(citation: Any) -> str:
    indexes = ",".join(str(item.locator_index) for item in citation.locator_refs)
    attrs = _attributes(
        (
            ("data-citation-id", citation.citation_id),
            ("data-reference-document-id", citation.reference_document_id),
            ("data-element-id", citation.element_id),
            ("data-mode", citation.mode.value),
            ("data-locator-indexes", indexes),
        )
    )
    return f"<span{attrs}></span>"


def render_pre_render_note_to_html(note: BenchmarkNoteDocument) -> bytes:
    """Transform one already validated Q26 pre-render note into HTML bytes."""

    if not isinstance(note, BenchmarkNoteDocument):
        raise RendererContractError("renderer accepts only a Q26 pre-render note")
    if note.schema_version != BENCHMARK_NOTE_SCHEMA_VERSION:
        raise RendererContractError("renderer input schema is invalid")
    if note.artifact_role != "pre_render_note":
        raise RendererContractError("renderer input role is invalid")

    root_attrs = _attributes(
        (
            ("data-document-id", note.document_id),
            ("data-reference-document-sha256", note.reference_document_sha256),
        )
    )
    parts = [
        '<!doctype html><html><head><meta charset="utf-8"></head><body><article',
        root_attrs,
        ">",
    ]
    for node in note.nodes:
        tag = _TAG_BY_KIND.get(node.kind)
        if tag is None:
            raise RendererContractError(f"unsupported Q26 node kind: {node.kind.value}")
        node_attrs: list[tuple[str, str]] = [
            ("data-node-id", node.node_id),
            ("data-node-kind", node.kind.value),
            ("data-order", str(node.order)),
        ]
        if node.parent_node_id is not None:
            node_attrs.append(("data-parent-node-id", node.parent_node_id))
        node_attrs.append(("data-q26-meta", _node_metadata(node)))
        content = "" if node.content is None else _escape_text(
            _normalize_line_endings(node.content)
        )
        parts.extend((f"<{tag}", _attributes(node_attrs), ">", content))
        parts.extend(_citation_marker(citation) for citation in node.citations)
        parts.append(f"</{tag}>")
    parts.append("</article></body></html>")
    return "".join(parts).encode("utf-8")


def _capture_id_seed(
    *,
    document_id: str,
    reference_document_sha256: str,
    pre_render_note_sha256: str,
    renderer_output_sha256: str,
    provenance: NoteProducerProvenance,
) -> dict[str, Any]:
    return {
        "artifact_role": "renderer_capture",
        "document_id": document_id,
        "pre_render_note_sha256": pre_render_note_sha256,
        "producer_provenance": provenance.model_dump(mode="json"),
        "reference_document_sha256": reference_document_sha256,
        "renderer_output_sha256": renderer_output_sha256,
        "schema_version": RENDERER_CAPTURE_SCHEMA_VERSION,
    }


def build_renderer_capture(
    note: BenchmarkNoteDocument,
    *,
    pre_render_note_sha256: str,
    renderer_output: bytes,
) -> RendererCaptureArtifact:
    if benchmark_note_sha256(note) != pre_render_note_sha256:
        raise RendererContractError("pre-render note digest mismatch")
    provenance = renderer_provenance()
    output_digest = _sha256(renderer_output)
    capture_id = "capture-" + _sha256(
        _canonical_json_bytes(
            _capture_id_seed(
                document_id=note.document_id,
                reference_document_sha256=note.reference_document_sha256,
                pre_render_note_sha256=pre_render_note_sha256,
                renderer_output_sha256=output_digest,
                provenance=provenance,
            )
        )
    )
    return RendererCaptureArtifact(
        capture_id=capture_id,
        document_id=note.document_id,
        reference_document_sha256=note.reference_document_sha256,
        pre_render_note_sha256=pre_render_note_sha256,
        renderer_output_sha256=output_digest,
        producer_provenance=provenance,
    )


def validate_renderer_capture(
    capture: RendererCaptureArtifact,
    *,
    note: BenchmarkNoteDocument,
    pre_render_note_sha256: str,
    renderer_output: bytes,
) -> RendererCaptureArtifact:
    expected_output = _sha256(renderer_output)
    expected_note = benchmark_note_sha256(note)
    if capture.document_id != note.document_id:
        raise RendererContractError("renderer capture document mismatch")
    if capture.reference_document_sha256 != note.reference_document_sha256:
        raise RendererContractError("renderer capture reference mismatch")
    if capture.pre_render_note_sha256 != pre_render_note_sha256:
        raise RendererContractError("renderer capture parent mismatch")
    if expected_note != pre_render_note_sha256:
        raise RendererContractError("renderer capture parent digest is invalid")
    if capture.renderer_output_sha256 != expected_output:
        raise RendererContractError("renderer output digest mismatch")
    expected_id = "capture-" + _sha256(
        _canonical_json_bytes(
            _capture_id_seed(
                document_id=note.document_id,
                reference_document_sha256=note.reference_document_sha256,
                pre_render_note_sha256=pre_render_note_sha256,
                renderer_output_sha256=expected_output,
                provenance=capture.producer_provenance,
            )
        )
    )
    if capture.capture_id != expected_id:
        raise RendererContractError("renderer capture identity mismatch")
    return capture


@dataclass
class _ParsedNode:
    tag: str
    attrs: list[tuple[str, str]]
    content_parts: list[str] = field(default_factory=list)
    citation_attrs: list[list[tuple[str, str]]] = field(default_factory=list)


class _CanonicalHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.document_id: Optional[str] = None
        self.reference_document_sha256: Optional[str] = None
        self.nodes: list[_ParsedNode] = []
        self.current: Optional[_ParsedNode] = None
        self.failed: Optional[str] = None
        self.declaration_seen = False

    def _fail(self, message: str) -> None:
        if self.failed is None:
            self.failed = message
        raise RendererContractError(message)

    @staticmethod
    def _attrs(attrs: list[tuple[str, Optional[str]]]) -> list[tuple[str, str]]:
        if any(value is None for _, value in attrs):
            raise RendererContractError("HTML boolean attributes are forbidden")
        return [(name, value or "") for name, value in attrs]

    def handle_decl(self, decl: str) -> None:
        if decl != "doctype html" or self.declaration_seen:
            self._fail("HTML doctype is invalid")
        self.declaration_seen = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        values = self._attrs(attrs)
        if tag == "html" and not self.stack:
            if not self.declaration_seen or values:
                self._fail("HTML root is invalid")
            self.stack.append(tag)
            return
        if tag == "head" and self.stack == ["html"] and not values:
            self.stack.append(tag)
            return
        if tag == "meta" and self.stack == ["html", "head"]:
            if values != [("charset", "utf-8")]:
                self._fail("HTML meta tag is invalid")
            return
        if tag == "body" and self.stack == ["html"] and not values:
            self.stack.append(tag)
            return
        if tag == "article" and self.stack == ["html", "body"]:
            if [name for name, _ in values] != [
                "data-document-id",
                "data-reference-document-sha256",
            ]:
                self._fail("HTML article attributes are invalid")
            self.document_id = values[0][1]
            self.reference_document_sha256 = values[1][1]
            self.stack.append(tag)
            return
        if self.stack == ["html", "body", "article"] and self.current is None:
            if tag not in set(_TAG_BY_KIND.values()):
                self._fail("HTML node tag is invalid")
            if [name for name, _ in values[:3]] != [
                "data-node-id",
                "data-node-kind",
                "data-order",
            ]:
                self._fail("HTML node attributes are invalid")
            optional_parent = (
                values[3:4]
                if len(values) > 3 and values[3][0] == "data-parent-node-id"
                else []
            )
            if len(values) > 3 and not optional_parent and values[3][0] != "data-q26-meta":
                self._fail("HTML parent attribute is invalid")
            meta_index = 4 if optional_parent else 3
            if len(values) != meta_index + 1 or values[meta_index][0] != "data-q26-meta":
                self._fail("HTML node metadata attribute is invalid")
            try:
                meta = json.loads(values[meta_index][1])
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise RendererContractError("HTML node metadata is invalid") from exc
            if not isinstance(meta, dict):
                self._fail("HTML node metadata must be an object")
            if set(meta) != {
                "parent_node_id",
                "languages",
                "list_metadata",
                "table_cell_metadata",
                "code_metadata",
                "citations",
            }:
                self._fail("HTML node metadata fields are invalid")
            expected_parent = optional_parent[0][1] if optional_parent else None
            if meta["parent_node_id"] != expected_parent:
                self._fail("HTML parent metadata mismatch")
            self.current = _ParsedNode(tag=tag, attrs=values)
            self.stack.append(tag)
            return
        if self.current is not None and self.stack[-1] == self.current.tag and tag == "span":
            expected_names = [
                "data-citation-id",
                "data-reference-document-id",
                "data-element-id",
                "data-mode",
                "data-locator-indexes",
            ]
            if [name for name, _ in values] != expected_names:
                self._fail("HTML citation marker attributes are invalid")
            self.current.citation_attrs.append(values)
            self.stack.append(tag)
            return
        self._fail("HTML structure is invalid")

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            self._fail("HTML closing tag is invalid")
        self.stack.pop()
        if self.current is not None and tag == self.current.tag:
            self.nodes.append(self.current)
            self.current = None

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self._fail("HTML self-closing tags are forbidden")

    def handle_data(self, data: str) -> None:
        if self.current is None:
            if data:
                self._fail("HTML contains unexpected text")
            return
        if self.stack[-1] != self.current.tag:
            self._fail("HTML citation marker contains text")
        self.current.content_parts.append(data)

    def handle_comment(self, data: str) -> None:
        self._fail("HTML comments are forbidden")

    def close(self) -> None:
        super().close()
        if self.failed is not None:
            raise RendererContractError(self.failed)
        if self.stack or not self.declaration_seen or self.current is not None:
            raise RendererContractError("HTML document is incomplete")


def _expected_marker_attrs(citation: Any) -> list[tuple[str, str]]:
    indexes = ",".join(str(item.locator_index) for item in citation.locator_refs)
    return [
        ("data-citation-id", citation.citation_id),
        ("data-reference-document-id", citation.reference_document_id),
        ("data-element-id", citation.element_id),
        ("data-mode", citation.mode.value),
        ("data-locator-indexes", indexes),
    ]


def parse_rendered_note_projection(
    renderer_output: bytes,
    *,
    pre_render_note: BenchmarkNoteDocument,
    reference_document: Any,
    pre_render_note_sha256: str,
) -> RenderedNoteProjection:
    """Read durable renderer bytes and materialize a Q26 projection."""

    if _sha256(renderer_output) != _sha256(
        render_pre_render_note_to_html(pre_render_note)
    ):
        raise RendererContractError("renderer output is not the frozen HTML projection")
    parser = _CanonicalHtmlParser()
    try:
        parser.feed(renderer_output.decode("utf-8"))
        parser.close()
    except (UnicodeDecodeError, RendererContractError) as exc:
        if isinstance(exc, RendererContractError):
            raise
        raise RendererContractError("renderer output is not valid UTF-8") from exc
    if parser.document_id != pre_render_note.document_id:
        raise RendererContractError("renderer output document mismatch")
    if parser.reference_document_sha256 != pre_render_note.reference_document_sha256:
        raise RendererContractError("renderer output reference mismatch")
    if len(parser.nodes) != len(pre_render_note.nodes):
        raise RendererContractError("renderer output node count mismatch")

    nodes: list[NoteNode] = []
    for parsed, source in zip(parser.nodes, pre_render_note.nodes):
        attrs = dict(parsed.attrs)
        if attrs["data-node-id"] != source.node_id:
            raise RendererContractError("renderer output node identity mismatch")
        if attrs["data-node-kind"] != source.kind.value:
            raise RendererContractError("renderer output node kind mismatch")
        if attrs["data-order"] != str(source.order):
            raise RendererContractError("renderer output node order mismatch")
        expected_parent = source.parent_node_id
        actual_parent = attrs.get("data-parent-node-id")
        if actual_parent != expected_parent:
            raise RendererContractError("renderer output parent mismatch")
        try:
            meta = json.loads(dict(parsed.attrs)["data-q26-meta"])
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise RendererContractError("renderer output metadata is invalid") from exc
        content = "".join(parsed.content_parts)
        node_payload = {
            "node_id": source.node_id,
            "kind": source.kind.value,
            "order": source.order,
            "parent_node_id": source.parent_node_id,
            "content": content if source.content is not None else None,
            **meta,
        }
        try:
            node = NoteNode.model_validate(node_payload)
        except (TypeError, ValueError) as exc:
            raise RendererContractError("renderer output Q26 node is invalid") from exc
        expected_content = (
            None
            if source.content is None
            else _normalize_line_endings(source.content)
        )
        if (
            node.model_dump(mode="json", exclude={"content"})
            != source.model_dump(mode="json", exclude={"content"})
            or node.content != expected_content
        ):
            raise RendererContractError("renderer output node content/metadata mismatch")
        if parsed.citation_attrs != [
            _expected_marker_attrs(citation) for citation in source.citations
        ]:
            raise RendererContractError("renderer output citation mismatch")
        nodes.append(node)

    if nodes:
        mappings = tuple(
            NoteLineageMapping(
                mapping_id=benchmark_note_mapping_id((node.node_id,), (node.node_id,), index),
                source_node_ids=(node.node_id,),
                target_node_ids=(node.node_id,),
                mapping_shape=LineageMappingShape.ONE_TO_ONE,
            )
            for index, node in enumerate(nodes)
        )
        mapping_state = LineageMappingState.PROVIDED
    else:
        mappings = ()
        mapping_state = LineageMappingState.UNAVAILABLE
    projection = RenderedNoteProjection(
        schema_version="benchmark-rendered-note-projection/1.0.0",
        artifact_role="rendered_note_projection",
        document_id=pre_render_note.document_id,
        reference_document_sha256=pre_render_note.reference_document_sha256,
        nodes=tuple(nodes),
        producer_provenance=renderer_provenance(),
        lineage=NoteLineage(
            parent_artifact_role=LineageParentRole.PRE_RENDER_NOTE,
            parent_artifact_sha256=pre_render_note_sha256,
            mapping_state=mapping_state,
            mappings=mappings,
        ),
    )
    validate_benchmark_note_artifact(
        projection,
        reference_document,
        parent_artifact=pre_render_note,
    )
    if benchmark_note_sha256(pre_render_note) != pre_render_note_sha256:
        raise RendererContractError("projection parent digest mismatch")
    if canonical_benchmark_note_bytes(projection) != canonical_benchmark_note_bytes(
        projection.model_dump(mode="json")
    ):
        raise RendererContractError("projection canonicalization mismatch")
    return projection


__all__ = [
    "RENDERER_CAPTURE_METHOD",
    "RENDERER_CAPTURE_SCHEMA_VERSION",
    "RENDERER_CONFIGURATION_SCHEMA_VERSION",
    "RENDERER_ID",
    "RENDERER_PROCESSING_METHOD",
    "RENDERER_PROCESSING_STAGE",
    "RENDERER_VERSION",
    "RendererCaptureArtifact",
    "RendererContractError",
    "RendererOperationalError",
    "build_renderer_capture",
    "canonical_renderer_capture_bytes",
    "canonical_renderer_configuration_bytes",
    "parse_rendered_note_projection",
    "render_pre_render_note_to_html",
    "renderer_capture_sha256",
    "renderer_configuration_payload",
    "renderer_configuration_sha256",
    "renderer_provenance",
    "validate_renderer_capture",
]
