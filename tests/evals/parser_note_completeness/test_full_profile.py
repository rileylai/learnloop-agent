from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tests.evals.parser_note_completeness.full_profile import (
    FULL_CASE_IDS,
    FullProfile,
    build_full_profile,
    canonical_full_profile_bytes,
    full_profile_sha256,
    load_full_profile,
    read_external_sha256_record,
    validate_full_profile_artifacts,
)


ROOT = Path(__file__).parent / "v1"
PROFILE_ROOT = ROOT / "manifests" / "full" / "revision-001"
PROFILE_PATH = PROFILE_ROOT / "profile.json"
PROFILE_DIGEST_PATH = PROFILE_ROOT / "profile.sha256"
PROFILE_V2_ROOT = ROOT / "manifests" / "full" / "revision-002"
PROFILE_V2_PATH = PROFILE_V2_ROOT / "profile.json"
PROFILE_V2_DIGEST_PATH = PROFILE_V2_ROOT / "profile.sha256"
SMOKE_PROFILE_PATH = ROOT / "manifests" / "smoke" / "revision-001" / "profile.json"
SMOKE_PROFILE_DIGEST = "49cfde8bb9aef1d96316665b8e9c55f9c78bf7a68fe8a93929ac8b136ebbf9a9"


def _payload() -> dict[str, Any]:
    return json.loads(PROFILE_PATH.read_bytes())


def test_full_profile_is_canonical_versioned_and_exactly_ordered() -> None:
    profile = load_full_profile(PROFILE_PATH, PROFILE_DIGEST_PATH, ROOT)

    assert tuple(case.case_id for case in profile.cases) == FULL_CASE_IDS
    assert len(profile.cases) == 13
    assert tuple(case.fixture_revision for case in profile.cases) == ("revision-001",) * 13
    assert PROFILE_PATH.read_bytes() == canonical_full_profile_bytes(profile)
    assert read_external_sha256_record(PROFILE_DIGEST_PATH, "profile.json") == full_profile_sha256(profile)
    assert profile.schema_version == "full-profile/1.0.0"
    assert profile.artifact_type == "parser_note_completeness_full_profile"
    assert profile.execution_mode == "development"
    assert profile.membership == "diagnostic"


def test_full_profile_rebuild_is_byte_deterministic_from_existing_artifacts() -> None:
    rebuilt = build_full_profile(ROOT)
    assert canonical_full_profile_bytes(rebuilt) == PROFILE_PATH.read_bytes()
    assert full_profile_sha256(rebuilt) == "0f00e4a1b89d7f5bdb218d51fe6a75fd9c7e3b5e88e1ce1a806eaed5df71d4a9"


def test_full_profile_revision_002_binds_only_the_new_fixture_revisions() -> None:
    profile = load_full_profile(PROFILE_V2_PATH, PROFILE_V2_DIGEST_PATH, ROOT)
    assert profile.profile_revision == "revision-002"
    assert tuple(case.fixture_revision for case in profile.cases) == (
        "revision-001",
        "revision-001",
        "revision-002",
        "revision-002",
        "revision-001",
        "revision-001",
        "revision-001",
        "revision-001",
        "revision-001",
        "revision-001",
        "revision-001",
        "revision-001",
        "revision-002",
    )
    assert PROFILE_V2_PATH.read_bytes() == canonical_full_profile_bytes(profile)
    assert read_external_sha256_record(PROFILE_V2_DIGEST_PATH, "profile.json") == full_profile_sha256(profile)


def test_full_profile_rejects_case_addition_removal_reordering_and_duplicates() -> None:
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
            FullProfile.model_validate({**payload, "cases": mutated_cases})


def test_full_profile_rejects_digest_tampering() -> None:
    payload = _payload()
    tampered = copy.deepcopy(payload)
    tampered["cases"][0]["source_sha256"] = "0" * 64
    profile = FullProfile.model_validate(tampered)

    with pytest.raises(ValueError, match="source artifact digest mismatch"):
        validate_full_profile_artifacts(profile, ROOT)


def test_full_profile_loader_rejects_tampered_external_profile_digest(tmp_path: Path) -> None:
    profile_copy = tmp_path / "profile.json"
    digest_copy = tmp_path / "profile.sha256"
    profile_copy.write_bytes(PROFILE_PATH.read_bytes())
    digest_copy.write_text("0" * 64 + "  profile.json\n", encoding="ascii")

    with pytest.raises(ValueError, match="full profile digest mismatch"):
        load_full_profile(profile_copy, digest_copy, ROOT)


@pytest.mark.parametrize("field_name, value", [("source_artifact_path", "../source.pdf"), ("source_artifact_path", "/tmp/source.pdf"), ("source_artifact_path", "fixtures\\P01\\revision-001\\source.pdf"), ("source_artifact_path", "fixtures/P01/./revision-001/source.pdf")])
def test_full_profile_rejects_path_traversal_and_non_posix_paths(field_name: str, value: str) -> None:
    payload = _payload()
    case = copy.deepcopy(payload["cases"][0])
    case[field_name] = value

    with pytest.raises(ValidationError):
        FullProfile.model_validate({**payload, "cases": [case, *payload["cases"][1:]]})


def test_full_profile_and_cases_are_extra_forbid() -> None:
    payload = _payload()
    with pytest.raises(ValidationError):
        FullProfile.model_validate({**payload, "unexpected": True})

    case = copy.deepcopy(payload["cases"][0])
    case["unexpected"] = True
    with pytest.raises(ValidationError):
        FullProfile.model_validate({**payload, "cases": [case, *payload["cases"][1:]]})


@pytest.mark.parametrize("path_field", ["source_artifact_path", "producer_configuration_path", "reference_path"])
def test_full_profile_rejects_artifact_symlink_escape(tmp_path: Path, path_field: str) -> None:
    profile = load_full_profile(PROFILE_PATH, PROFILE_DIGEST_PATH, ROOT)
    benchmark_root = tmp_path / "benchmark-root"
    shutil.copytree(ROOT, benchmark_root)
    case = profile.cases[0]
    escaped_path = benchmark_root / getattr(case, path_field)
    escaped_path.unlink()
    outside_path = tmp_path / f"outside-{path_field}.bin"
    outside_path.write_bytes(b"outside benchmark root")
    escaped_path.symlink_to(outside_path)

    with pytest.raises(ValueError, match="outside the benchmark root"):
        validate_full_profile_artifacts(profile, benchmark_root)


def test_full_profile_has_no_formal_or_adoption_authority_and_all_candidates_remain_draft() -> None:
    profile = load_full_profile(PROFILE_PATH, PROFILE_DIGEST_PATH, ROOT)
    assert {
        "authority",
        "authority_status",
        "result_role",
        "quality_decision",
        "gate_decision",
        "comparison_decision",
        "adoption_decision",
        "threshold",
        "thresholds",
    }.isdisjoint(profile.model_dump(mode="json"))

    for case in profile.cases:
        candidate = json.loads((ROOT / "governance" / case.case_id / case.fixture_revision / "candidate.json").read_bytes())
        assert candidate["candidate_status"] == "draft_candidate"
        assert candidate["formal_manifest_present"] is False
        assert candidate["authority"] == {
            "approved": False,
            "baseline_gate_authority": False,
            "canonical_dataset": False,
            "formal": False,
        }
        assert "result_role" not in candidate
        assert any(item.startswith("Q22:") for item in candidate["pending_evidence"])
        assert any(item.startswith("Q25:") for item in candidate["pending_evidence"])
        assert all(not Path(value).is_absolute() for value in candidate["artifacts"].values())
        assert not (ROOT / "manifests" / f"{case.case_id}-revision-001.json").exists()


def test_full_profile_manifest_directory_contains_bindings_only_and_smoke_is_unchanged() -> None:
    assert sorted(path.name for path in PROFILE_ROOT.iterdir()) == ["profile.json", "profile.sha256"]
    assert hashlib.sha256(SMOKE_PROFILE_PATH.read_bytes()).hexdigest() == SMOKE_PROFILE_DIGEST
