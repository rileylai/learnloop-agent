from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from pypdf import PdfReader

from tests.evals.parser_note_completeness.normalized_document import (
    NormalizedDocument,
    canonical_normalized_document_bytes,
)


ROOT = Path(__file__).parent / "v1"
SUCCESSORS = {
    "P02": ("revision-002", "source.pdf", "557f0ff7047a6399359c12ff84c4d8a0d7d534427faa8ace2d246653d63ab41f", "890114cc77194b1a92f4456e9dbb1000998e1ff0e72e0abf423a9672e86c2ec8", "761f503f60114b90834051c36aaf2fb665fb0738070edd72977fc821dfc32541"),
    "P03": ("revision-003", "source.pdf", "a5fceec1d03317f6c7ca7dab576ef18b54124d31a1ef68b53511ed36741b4e26", "510914d0e45c7452cc97901b2e62f6e57f298026f6d1dbd59753ce2524dc7d0e", "75129a78bb1178300c9f8c75e6a3cca987f1a62ff1fb6d46661b7b783157fb48"),
    "P04": ("revision-003", "source.pdf", "055115cf9f24f8116366399c07d43dc88ce2f48966339c7cc3dea096ca1e566d", "54d6f59d6a39c7ef04c2da120be948fbdf567b9b0da495b1d91c7fae2eb99b68", "bb205531ab92477ea847dbc36302c89f73307395161b3d9b74941a8d6d39dfa1"),
    "W02": ("revision-002", "source.html", "368f3bf9192bb7c9099e83f95e8d0b72cffbc0dab3ee04ac81e4415fcca32e51", "0d0abf603cf59c0b23cc123cfff5ea5f75f98008244b9aed7f792afd801e9e11", "847de8b00366be9059c0f732e6e11f108de3ba8e8e268f1249793af140315dd9"),
    "W03": ("revision-002", "source.html", "a6b8495a77d7d5fd95fb4ba9ca98aa56e9043c09447f42b15090bd1dc134f2df", "0c97e05e8d9c0ce0fd42030671f6af3bda3eafe9b7eeffdabed57cf5b3d097b0", "f63a94e5d3061c9c116afa07fef7c666a3e6f1249b8d34f3b280b1d307f0647b"),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_source_builder(case_id: str, revision: str):
    path = ROOT / "fixtures" / case_id / revision / "build_source.py"
    spec = importlib.util.spec_from_file_location(f"successor_{case_id.lower()}_{revision}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_successor_sources_configurations_and_references_are_digest_bound() -> None:
    for case_id, (revision, source_name, source_digest, config_digest, reference_digest) in SUCCESSORS.items():
        fixture = ROOT / "fixtures" / case_id / revision
        governance = ROOT / "governance" / case_id / revision
        reference = ROOT / "reference_documents" / case_id / revision
        assert _sha256(fixture / source_name) == source_digest
        assert (fixture / "source.sha256").read_text(encoding="ascii").split() == [source_digest, source_name]
        assert _sha256(governance / "producer_configuration.json") == config_digest
        assert _sha256(reference / "normalized_document.json") == reference_digest
        assert (reference / "normalized_document.sha256").read_text(encoding="ascii").split() == [reference_digest, "normalized_document.json"]
        document = NormalizedDocument.model_validate_json((reference / "normalized_document.json").read_bytes())
        assert document.source.source_snapshot_sha256 == source_digest
        assert document.producer_provenance.configuration_sha256 == config_digest
        assert canonical_normalized_document_bytes(document) == (reference / "normalized_document.json").read_bytes()


def test_p02_and_p04_native_pages_use_self_contained_selectable_type3_text() -> None:
    for case_id, revision, native_pages in (("P02", "revision-002", (0, 1, 2, 3)), ("P04", "revision-003", (0, 2))):
        reader = PdfReader(ROOT / "fixtures" / case_id / revision / "source.pdf")
        for page_index in native_pages:
            page = reader.pages[page_index]
            font = page["/Resources"]["/Font"]["/F1"].get_object()
            assert font["/Subtype"] == "/Type3"
            assert font.get("/ToUnicode") is not None
            assert len(font["/CharProcs"]) > 0
            assert (page.extract_text() or "").strip()
            assert "/XObject" not in page.get("/Resources", {})


def test_p02_and_p04_successor_builders_reproduce_exact_pdf_bytes() -> None:
    for case_id, revision in (("P02", "revision-002"), ("P04", "revision-003")):
        fixture = ROOT / "fixtures" / case_id / revision
        assert _load_source_builder(case_id, revision).build_pdf() == (fixture / "source.pdf").read_bytes()


def test_corrected_references_include_every_owner_selected_visible_item() -> None:
    payloads = {
        case_id: json.loads((ROOT / "reference_documents" / case_id / revision / "normalized_document.json").read_bytes())
        for case_id, (revision, *_rest) in SUCCESSORS.items()
    }
    content = {case_id: {element["content"] for element in payload["elements"] if element["content"] is not None} for case_id, payload in payloads.items()}
    assert {"文字、表格與圖形都保留在同一份 native-text PDF 中。", "This draft is for development validation only.", "Stage / 階段", "Median ms / 中位毫秒", "Owner / 負責人", "圖1 / Figure 1", "圖2 / Figure 2"} <= content["P02"]
    assert {f"掃描頁碼 {page}" for page in range(1, 6)} <= content["P03"]
    assert sum(element["content"] == "區域甲" for element in payloads["P03"]["elements"]) == 5
    assert sum(element["content"] == "區域乙" for element in payloads["P03"]["elements"]) == 5
    assert {"表格保留單位與欄位關係，方便逐格定位。", "公式 / Formula: F = m * a", "區域 A", "Review B"} <= content["P04"]
    assert "[Input] → [Normalize] → [Review]" in content["W02"]
    assert "[Snapshot] → [Structure] → [Reference]" in content["W03"]


def test_unchanged_successor_source_bytes_remain_identical_to_owner_approved_bytes() -> None:
    assert (ROOT / "fixtures" / "P03" / "revision-003" / "source.pdf").read_bytes() == (ROOT / "fixtures" / "P03" / "revision-002" / "source.pdf").read_bytes()
    for case_id in ("W02", "W03"):
        assert (ROOT / "fixtures" / case_id / "revision-002" / "source.html").read_bytes() == (ROOT / "fixtures" / case_id / "revision-001" / "source.html").read_bytes()


def test_owner_annotation_records_are_digest_bound_and_non_authoritative() -> None:
    records = (
        (ROOT / "governance" / "C01" / "revision-002" / "owner-primary-annotation.json", "bd1b9d409dd7111022336cd5c0bc57c400ee677f242eff27241e6aa69034802c"),
        (ROOT / "governance" / "C02" / "revision-002" / "owner-speaker-identity-assertions.json", "bfabff5fa7bf9ce6ae5380065151b08a5c5b8da1e7f845d2cd74ed149e7ab424"),
    )
    for path, digest in records:
        payload = json.loads(path.read_bytes())
        assert _sha256(path) == digest
        assert path.with_suffix(".sha256").read_text(encoding="ascii").split() == [digest, path.name]
        assert payload["formal_authority"] is False
        assert payload["authority_status"] == "owner_approved_independent_review_pending"
        assert payload["independent_review"]["status"] == "pending"
    c01 = json.loads(records[0][0].read_bytes())
    assert [claim["importance"] for claim in c01["expected_claims"]] == ["critical", "major", "critical"]
    assert len(c01["source_references"]) == len(c01["evidence_items"]) == len(c01["expected_claims"]) == 3
    c02 = json.loads(records[1][0].read_bytes())
    assert len(c02["speaker_identity_assertions"]) == 6
    assert {item["speaker_id"] for item in c02["speaker_identity_assertions"]} == {"speaker-alice", "speaker-bob", "speaker-chen"}
