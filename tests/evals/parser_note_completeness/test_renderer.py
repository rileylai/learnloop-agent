from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from tests.evals.parser_note_completeness.benchmark_note import (
    LineageMappingState,
    benchmark_note_sha256,
    canonical_benchmark_note_bytes,
)
from tests.evals.parser_note_completeness.full_profile import load_full_profile
from tests.evals.parser_note_completeness.generation_lane import build_pre_render_note
from tests.evals.parser_note_completeness.normalized_document import NormalizedDocument
from tests.evals.parser_note_completeness.renderer import (
    RendererContractError,
    build_renderer_capture,
    canonical_renderer_capture_bytes,
    parse_rendered_note_projection,
    render_pre_render_note_to_html,
    renderer_capture_sha256,
    renderer_configuration_sha256,
    validate_renderer_capture,
)


ROOT = Path(__file__).parent / "v1"
PROFILE_ROOT = ROOT / "manifests" / "full" / "revision-001"


def _full_profile() -> Any:
    return load_full_profile(
        PROFILE_ROOT / "profile.json",
        PROFILE_ROOT / "profile.sha256",
        ROOT,
    )


def test_renderer_replay_is_byte_and_digest_identical_for_all_q26_kinds() -> None:
    profile = _full_profile()
    rendered_kinds: set[str] = set()

    for case in profile.cases:
        note = build_pre_render_note(case, ROOT)
        first = render_pre_render_note_to_html(note)
        second = render_pre_render_note_to_html(note)
        assert first == second
        assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()
        assert renderer_configuration_sha256()
        assert first.startswith(b"<!doctype html>")
        assert first.endswith(b"</html>")
        assert b"\r" not in first
        assert not first.endswith(b"\n")
        assert b"<script" not in first
        assert b"<style" not in first
        assert b"http://" not in first
        assert b"https://" not in first
        rendered_kinds.update(node.kind.value for node in note.nodes)

    assert rendered_kinds == {
        "heading",
        "paragraph",
        "list_item",
        "quote",
        "code_block",
        "table",
        "table_row",
        "table_cell",
        "figure",
        "caption",
        "formula",
        "transcript_segment",
        "message",
    }


def test_durable_html_readback_materializes_real_lineage() -> None:
    profile = _full_profile()
    case = next(case for case in profile.cases if case.case_id == "P01")
    note = build_pre_render_note(case, ROOT)
    output = render_pre_render_note_to_html(note)
    note_digest = benchmark_note_sha256(note)
    capture = build_renderer_capture(
        note,
        pre_render_note_sha256=note_digest,
        renderer_output=output,
    )

    assert capture.renderer_output_sha256 == hashlib.sha256(output).hexdigest()
    assert canonical_renderer_capture_bytes(capture)
    assert renderer_capture_sha256(capture) == renderer_capture_sha256(
        capture.model_dump(mode="json")
    )
    validate_renderer_capture(
        capture,
        note=note,
        pre_render_note_sha256=note_digest,
        renderer_output=output,
    )
    projection = parse_rendered_note_projection(
        output,
        pre_render_note=note,
        reference_document=NormalizedDocument.model_validate(
            json.loads((ROOT / case.reference_path).read_bytes())
        ),
        pre_render_note_sha256=note_digest,
    )
    assert projection.lineage.parent_artifact_sha256 == note_digest
    assert projection.lineage.mapping_state == LineageMappingState.PROVIDED
    assert output != canonical_benchmark_note_bytes(note)
    assert projection.nodes == note.nodes
    assert projection.nodes[0].content == note.nodes[0].content


def test_empty_note_allows_unavailable_lineage_only_when_there_are_no_nodes() -> None:
    profile = _full_profile()
    case = next(
        case
        for case in profile.cases
        if not (candidate := build_pre_render_note(case, ROOT)).nodes
    )
    note = build_pre_render_note(case, ROOT)
    note_digest = benchmark_note_sha256(note)
    output = render_pre_render_note_to_html(note)
    projection = parse_rendered_note_projection(
        output,
        pre_render_note=note,
        reference_document=NormalizedDocument.model_validate(
            json.loads((ROOT / case.reference_path).read_bytes())
        ),
        pre_render_note_sha256=note_digest,
    )

    assert note.nodes == ()
    assert projection.nodes == ()
    assert projection.lineage.mapping_state == LineageMappingState.UNAVAILABLE
    assert projection.lineage.mappings == ()
    assert output.startswith(b"<!doctype html>")
    assert output != canonical_benchmark_note_bytes(note)


def test_non_empty_note_cannot_downgrade_renderer_lineage_to_unavailable() -> None:
    profile = _full_profile()
    case = next(case for case in profile.cases if case.case_id == "P01")
    note = build_pre_render_note(case, ROOT)
    assert note.nodes

    output = render_pre_render_note_to_html(note)
    projection = parse_rendered_note_projection(
        output,
        pre_render_note=note,
        reference_document=NormalizedDocument.model_validate(
            json.loads((ROOT / case.reference_path).read_bytes())
        ),
        pre_render_note_sha256=benchmark_note_sha256(note),
    )

    assert projection.lineage.mapping_state == LineageMappingState.PROVIDED
    assert len(projection.lineage.mappings) == len(note.nodes)
    assert all(
        mapping.source_node_ids == mapping.target_node_ids
        and len(mapping.source_node_ids) == 1
        for mapping in projection.lineage.mappings
    )
    assert output != canonical_benchmark_note_bytes(note)


def test_direct_copy_and_malformed_output_are_rejected() -> None:
    profile = _full_profile()
    case = next(case for case in profile.cases if case.case_id == "P01")
    note = build_pre_render_note(case, ROOT)
    with pytest.raises(RendererContractError):
        parse_rendered_note_projection(
            canonical_benchmark_note_bytes(note),
            pre_render_note=note,
            reference_document=note,
            pre_render_note_sha256=benchmark_note_sha256(note),
        )

    output = render_pre_render_note_to_html(note)
    with pytest.raises(RendererContractError):
        parse_rendered_note_projection(
            output[:-1] + b"x",
            pre_render_note=note,
            reference_document=note,
            pre_render_note_sha256=benchmark_note_sha256(note),
        )
