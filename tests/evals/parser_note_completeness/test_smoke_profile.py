from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tests.evals.parser_note_completeness.smoke_profile import (
    SMOKE_CASE_IDS,
    SmokeProfile,
    canonical_smoke_profile_bytes,
    load_smoke_profile,
    read_external_sha256_record,
    smoke_profile_sha256,
    validate_smoke_profile_artifacts,
)


ROOT = Path(__file__).parent / "v1"
PROFILE_ROOT = ROOT / "manifests" / "smoke" / "revision-001"
PROFILE_PATH = PROFILE_ROOT / "profile.json"
PROFILE_DIGEST_PATH = PROFILE_ROOT / "profile.sha256"


def _payload() -> dict[str, Any]:
    return json.loads(PROFILE_PATH.read_bytes())


def test_smoke_profile_is_canonical_versioned_and_exactly_ordered() -> None:
    profile = load_smoke_profile(PROFILE_PATH, PROFILE_DIGEST_PATH, ROOT)

    assert tuple(case.case_id for case in profile.cases) == SMOKE_CASE_IDS
    assert tuple(case.fixture_revision for case in profile.cases) == ("revision-001",) * 5
    assert PROFILE_PATH.read_bytes() == canonical_smoke_profile_bytes(profile)
    assert read_external_sha256_record(PROFILE_DIGEST_PATH, "profile.json") == smoke_profile_sha256(profile)
    assert profile.execution_mode == "development"
    assert profile.membership == "diagnostic"


def test_profile_rejects_case_addition_removal_reordering_and_duplicates() -> None:
    payload = _payload()
    cases = payload["cases"]
    assert isinstance(cases, list)

    for mutated_cases in (
        cases[:-1],
        cases + [copy.deepcopy(cases[0])],
        list(reversed(cases)),
        [copy.deepcopy(cases[0]), *cases[1:]],
    ):
        if mutated_cases == cases:
            mutated_cases[1] = copy.deepcopy(mutated_cases[0])
        with pytest.raises(ValidationError):
            SmokeProfile.model_validate({**payload, "cases": mutated_cases})


def test_profile_artifact_validation_rejects_digest_tampering() -> None:
    payload = _payload()
    cases = payload["cases"]
    assert isinstance(cases, list)
    tampered = copy.deepcopy(payload)
    tampered_cases = tampered["cases"]
    assert isinstance(tampered_cases, list)
    tampered_cases[0]["source_sha256"] = "0" * 64
    profile = SmokeProfile.model_validate(tampered)

    with pytest.raises(ValueError, match="source artifact digest mismatch"):
        validate_smoke_profile_artifacts(profile, ROOT)


def test_profile_loader_rejects_tampered_external_profile_digest(tmp_path: Path) -> None:
    profile_copy = tmp_path / "profile.json"
    digest_copy = tmp_path / "profile.sha256"
    profile_copy.write_bytes(PROFILE_PATH.read_bytes())
    digest_copy.write_text("0" * 64 + "  profile.json\n", encoding="ascii")

    with pytest.raises(ValueError, match="smoke profile digest mismatch"):
        load_smoke_profile(profile_copy, digest_copy, ROOT)


def test_source_digest_symlink_outside_benchmark_root_is_rejected(tmp_path: Path) -> None:
    profile = load_smoke_profile(PROFILE_PATH, PROFILE_DIGEST_PATH, ROOT)
    benchmark_root = tmp_path / "benchmark-root"
    shutil.copytree(ROOT, benchmark_root)
    source_digest_path = benchmark_root / profile.cases[0].source_digest_path
    source_digest_path.unlink()
    outside_digest_path = tmp_path / "outside-source.sha256"
    outside_digest_path.write_text("0" * 64 + "  source.pdf\n", encoding="ascii")
    source_digest_path.symlink_to(outside_digest_path)

    with pytest.raises(ValueError, match="source checksum record.*outside the benchmark root"):
        validate_smoke_profile_artifacts(profile, benchmark_root)


def test_reference_digest_symlink_outside_benchmark_root_is_rejected(tmp_path: Path) -> None:
    profile = load_smoke_profile(PROFILE_PATH, PROFILE_DIGEST_PATH, ROOT)
    benchmark_root = tmp_path / "benchmark-root"
    shutil.copytree(ROOT, benchmark_root)
    reference_digest_path = benchmark_root / profile.cases[0].reference_digest_path
    reference_digest_path.unlink()
    outside_digest_path = tmp_path / "outside-reference.sha256"
    outside_digest_path.write_text("0" * 64 + "  normalized_document.json\n", encoding="ascii")
    reference_digest_path.symlink_to(outside_digest_path)

    with pytest.raises(ValueError, match="reference checksum record.*outside the benchmark root"):
        validate_smoke_profile_artifacts(profile, benchmark_root)


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("source_artifact_path", "../source.pdf"),
        ("source_artifact_path", "/tmp/source.pdf"),
        ("source_artifact_path", "fixtures\\P01\\revision-001\\source.pdf"),
        ("source_artifact_path", "fixtures/P01/./revision-001/source.pdf"),
    ],
)
def test_profile_rejects_path_traversal_and_non_posix_paths(field_name: str, value: str) -> None:
    payload = _payload()
    case = copy.deepcopy(payload["cases"][0])
    case[field_name] = value

    with pytest.raises(ValidationError):
        SmokeProfile.model_validate({**payload, "cases": [case, *payload["cases"][1:]]})


def test_profile_and_case_are_extra_forbid() -> None:
    payload = _payload()
    with pytest.raises(ValidationError):
        SmokeProfile.model_validate({**payload, "unexpected": True})

    case = copy.deepcopy(payload["cases"][0])
    case["unexpected"] = True
    with pytest.raises(ValidationError):
        SmokeProfile.model_validate({**payload, "cases": [case, *payload["cases"][1:]]})


def test_profile_has_no_quality_or_authority_decision_surface_and_candidates_remain_draft() -> None:
    profile = load_smoke_profile(PROFILE_PATH, PROFILE_DIGEST_PATH, ROOT)
    forbidden_fields = {
        "authority",
        "authority_status",
        "result_role",
        "quality_decision",
        "gate_decision",
        "comparison_decision",
        "adoption_decision",
        "threshold",
        "thresholds",
    }
    assert forbidden_fields.isdisjoint(profile.model_dump(mode="json"))
    assert all(
        not any(term in json.dumps(case.model_dump(mode="json")).lower() for term in (
            "canonical",
            "approved",
            "formal",
            "full",
            "baseline",
            "comparison",
            "gate",
            "adoption",
        ))
        for case in profile.cases
    )
    for case in profile.cases:
        candidate = json.loads(
            (ROOT / "governance" / case.case_id / case.fixture_revision / "candidate.json").read_bytes()
        )
        assert candidate["formal_manifest_present"] is False
        assert "result_role" not in candidate


def test_y01_binds_snapshot_artifact_and_reference_source_digest() -> None:
    profile = load_smoke_profile(PROFILE_PATH, PROFILE_DIGEST_PATH, ROOT)
    y01 = profile.cases[2]

    assert y01.case_id == "Y01"
    assert y01.source_artifact_path == "fixtures/Y01/revision-001/source_snapshot.json"
    assert y01.source_digest_path == "fixtures/Y01/revision-001/source_snapshot.sha256"
    assert y01.source_sha256 == "66765dcc81f041b8d20c1484db4651f063d9ed53cac82d3bc900123ea97d873a"

    tampered = _payload()
    tampered_cases = tampered["cases"]
    assert isinstance(tampered_cases, list)
    tampered_cases[2] = {
        **tampered_cases[2],
        "source_artifact_path": "fixtures/Y01/revision-001/captions.vtt",
        "source_digest_path": "fixtures/Y01/revision-001/captions.sha256",
        "source_sha256": "fcba02596d324e983b2a38fd99855065ce5bffb2bcfbb33ded1c433c8b821c3f",
    }
    with pytest.raises(ValidationError):
        SmokeProfile.model_validate(tampered)


def test_manifest_directory_contains_bindings_only() -> None:
    assert sorted(path.name for path in PROFILE_ROOT.iterdir()) == ["profile.json", "profile.sha256"]
