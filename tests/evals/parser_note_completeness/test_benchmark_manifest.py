from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tests.evals.parser_note_completeness.benchmark_manifest import (
    BENCHMARK_VERSION_001,
    BENCHMARK_VERSION_002,
    BenchmarkManifest,
    benchmark_manifest_sha256,
    build_benchmark_manifest,
    canonical_benchmark_manifest_bytes,
    load_benchmark_manifest,
    read_external_sha256_record,
    validate_benchmark_manifest_artifacts,
)


ROOT = Path(__file__).parent / "v1"
MANIFESTS = {
    BENCHMARK_VERSION_001: ROOT / "manifests" / "benchmark" / "1.0.0",
    BENCHMARK_VERSION_002: ROOT / "manifests" / "benchmark" / "1.0.1",
}


@pytest.mark.parametrize("benchmark_version", [BENCHMARK_VERSION_001, BENCHMARK_VERSION_002])
def test_benchmark_manifest_is_canonical_and_validates_transitive_bindings(benchmark_version: str) -> None:
    manifest_root = MANIFESTS[benchmark_version]
    manifest_path = manifest_root / "manifest.json"
    digest_path = manifest_root / "manifest.sha256"
    manifest = load_benchmark_manifest(manifest_path, digest_path, ROOT)

    assert manifest.benchmark_version == benchmark_version
    assert manifest_path.read_bytes() == canonical_benchmark_manifest_bytes(manifest)
    assert read_external_sha256_record(digest_path, "manifest.json") == benchmark_manifest_sha256(manifest)
    assert validate_benchmark_manifest_artifacts(manifest, ROOT) == manifest


def test_benchmark_manifest_100_preserves_old_profile_and_101_selects_revision_002() -> None:
    old = load_benchmark_manifest(
        MANIFESTS[BENCHMARK_VERSION_001] / "manifest.json",
        MANIFESTS[BENCHMARK_VERSION_001] / "manifest.sha256",
        ROOT,
    )
    new = load_benchmark_manifest(
        MANIFESTS[BENCHMARK_VERSION_002] / "manifest.json",
        MANIFESTS[BENCHMARK_VERSION_002] / "manifest.sha256",
        ROOT,
    )

    assert old.benchmark_version == "parser-note-completeness/1.0.0"
    assert old.full_profile_revision == "revision-001"
    assert old.full_profile_sha256 == "0f00e4a1b89d7f5bdb218d51fe6a75fd9c7e3b5e88e1ce1a806eaed5df71d4a9"
    assert new.benchmark_version == "parser-note-completeness/1.0.1"
    assert new.full_profile_revision == "revision-002"
    assert new.full_profile_sha256 == "4e32c4d31c9fc4359ae15c693d6f35e0d56712a37214965adeede587bb5ebc27"


def test_benchmark_manifest_build_is_byte_deterministic() -> None:
    for benchmark_version, manifest_root in MANIFESTS.items():
        manifest = build_benchmark_manifest(ROOT, benchmark_version=benchmark_version)
        assert canonical_benchmark_manifest_bytes(manifest) == (manifest_root / "manifest.json").read_bytes()


def test_benchmark_manifest_rejects_wrong_profile_binding() -> None:
    manifest_path = MANIFESTS[BENCHMARK_VERSION_002] / "manifest.json"
    payload = json.loads(manifest_path.read_bytes())
    mutated = copy.deepcopy(payload)
    mutated["full_profile_revision"] = "revision-001"

    with pytest.raises(ValidationError):
        BenchmarkManifest.model_validate(mutated)


def test_benchmark_manifest_rejects_tampered_profile_bytes(tmp_path: Path) -> None:
    manifest = load_benchmark_manifest(
        MANIFESTS[BENCHMARK_VERSION_002] / "manifest.json",
        MANIFESTS[BENCHMARK_VERSION_002] / "manifest.sha256",
        ROOT,
    )
    copied_root = tmp_path / "benchmark-root"
    copied_root.mkdir()
    source_root = ROOT
    for relative_path in (
        manifest.full_profile_path,
        manifest.full_profile_digest_path,
        manifest.smoke_profile_path,
        manifest.smoke_profile_digest_path,
    ):
        target = copied_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((source_root / relative_path).read_bytes())
    profile_path = copied_root / manifest.full_profile_path
    profile_path.write_bytes(profile_path.read_bytes() + b" ")

    with pytest.raises(ValueError, match="full profile digest mismatch"):
        validate_benchmark_manifest_artifacts(manifest, copied_root)
