"""Immutable benchmark-release manifest bindings."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Mapping, Union

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator, model_validator

from .full_profile import (
    load_full_profile,
    read_external_sha256_record,
)
from .smoke_profile import load_smoke_profile


BENCHMARK_MANIFEST_SCHEMA_VERSION = "benchmark-manifest/1.0.0"
BENCHMARK_MANIFEST_ARTIFACT_TYPE = "parser_note_completeness_benchmark_manifest"
BENCHMARK_CONTRACT = "parser-note-completeness-v1"
BENCHMARK_VERSION_001: Literal["parser-note-completeness/1.0.0"] = "parser-note-completeness/1.0.0"
BENCHMARK_VERSION_002: Literal["parser-note-completeness/1.0.1"] = "parser-note-completeness/1.0.1"
BenchmarkVersion = Literal[
    "parser-note-completeness/1.0.0",
    "parser-note-completeness/1.0.1",
]

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_ALLOWED_ARTIFACT_ROOTS = frozenset({"manifests"})

Sha256 = Annotated[StrictStr, Field(pattern=_SHA256_PATTERN)]


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


_EXPECTED_BINDINGS: dict[BenchmarkVersion, dict[str, str]] = {
    BENCHMARK_VERSION_001: {
        "full_profile_revision": "revision-001",
        "full_profile_path": "manifests/full/revision-001/profile.json",
        "full_profile_digest_path": "manifests/full/revision-001/profile.sha256",
        "full_profile_sha256": "0f00e4a1b89d7f5bdb218d51fe6a75fd9c7e3b5e88e1ce1a806eaed5df71d4a9",
    },
    BENCHMARK_VERSION_002: {
        "full_profile_revision": "revision-002",
        "full_profile_path": "manifests/full/revision-002/profile.json",
        "full_profile_digest_path": "manifests/full/revision-002/profile.sha256",
        "full_profile_sha256": "59e1ab02dfc5bcb87731c22e78e707de2d2ff550f664d81da121f8c3ac8f0c39",
    },
}

_SMOKE_PROFILE_PATH = "manifests/smoke/revision-001/profile.json"
_SMOKE_PROFILE_DIGEST_PATH = "manifests/smoke/revision-001/profile.sha256"
_SMOKE_PROFILE_SHA256 = "49cfde8bb9aef1d96316665b8e9c55f9c78bf7a68fe8a93929ac8b136ebbf9a9"


def _validate_manifest_relative_path(value: str) -> str:
    parts = value.split("/")
    if (
        value.startswith("/")
        or "\\" in value
        or (len(value) >= 2 and value[1] == ":")
        or PurePosixPath(value).is_absolute()
        or any(part in {"", ".", ".."} for part in parts)
        or PurePosixPath(value).as_posix() != value
        or parts[0] not in _ALLOWED_ARTIFACT_ROOTS
    ):
        raise ValueError("manifest paths must be normalized benchmark-root-relative POSIX paths")
    return value


class BenchmarkManifest(_StrictFrozenModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
        json_schema_extra={
            "$id": f"https://learnloop.local/schemas/{BENCHMARK_MANIFEST_SCHEMA_VERSION}",
        },
    )

    schema_version: Literal["benchmark-manifest/1.0.0"]
    artifact_type: Literal["parser_note_completeness_benchmark_manifest"]
    benchmark_contract: Literal["parser-note-completeness-v1"]
    benchmark_version: BenchmarkVersion
    full_profile_id: Literal["full"]
    full_profile_revision: Literal["revision-001", "revision-002"]
    full_profile_path: StrictStr = Field(min_length=1)
    full_profile_digest_path: StrictStr = Field(min_length=1)
    full_profile_sha256: Sha256
    smoke_profile_id: Literal["smoke"]
    smoke_profile_revision: Literal["revision-001"]
    smoke_profile_path: StrictStr = Field(min_length=1)
    smoke_profile_digest_path: StrictStr = Field(min_length=1)
    smoke_profile_sha256: Sha256

    @field_validator(
        "full_profile_path",
        "full_profile_digest_path",
        "smoke_profile_path",
        "smoke_profile_digest_path",
    )
    @classmethod
    def _validate_paths(cls, value: str) -> str:
        return _validate_manifest_relative_path(value)

    @model_validator(mode="after")
    def _validate_version_bindings(self) -> "BenchmarkManifest":
        expected = _EXPECTED_BINDINGS[self.benchmark_version]
        for field_name, expected_value in expected.items():
            if getattr(self, field_name) != expected_value:
                raise ValueError(f"{self.benchmark_version} must bind its immutable full-profile identity")
        if (
            self.smoke_profile_revision != "revision-001"
            or self.smoke_profile_path != _SMOKE_PROFILE_PATH
            or self.smoke_profile_digest_path != _SMOKE_PROFILE_DIGEST_PATH
            or self.smoke_profile_sha256 != _SMOKE_PROFILE_SHA256
        ):
            raise ValueError(f"{self.benchmark_version} must bind the immutable smoke profile identity")
        return self


BenchmarkManifestInput = Union[BenchmarkManifest, Mapping[str, Any]]


def validate_benchmark_manifest(manifest: BenchmarkManifestInput) -> BenchmarkManifest:
    if isinstance(manifest, BenchmarkManifest):
        return BenchmarkManifest.model_validate(manifest.model_dump(mode="python"))
    return BenchmarkManifest.model_validate(manifest)


def canonical_benchmark_manifest_bytes(manifest: BenchmarkManifestInput) -> bytes:
    model = validate_benchmark_manifest(manifest)
    payload = json.dumps(
        model.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return f"{payload}\n".encode("utf-8")


def benchmark_manifest_sha256(manifest: BenchmarkManifestInput) -> str:
    return hashlib.sha256(canonical_benchmark_manifest_bytes(manifest)).hexdigest()


def _read_bounded_artifact(root: Path, relative_path: str, label: str) -> bytes:
    try:
        root_resolved = root.resolve(strict=True)
        artifact_path = (root / relative_path).resolve(strict=True)
        artifact_path.relative_to(root_resolved)
        return artifact_path.read_bytes()
    except (OSError, ValueError) as exc:
        raise ValueError(f"{label} is unavailable or outside the benchmark root") from exc


def _assert_digest(label: str, data: bytes, expected: str) -> None:
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise ValueError(f"{label} digest mismatch")


def validate_benchmark_manifest_artifacts(
    manifest: BenchmarkManifestInput,
    benchmark_root: Path,
) -> BenchmarkManifest:
    """Validate profile identities and all transitive fixture bindings."""

    model = validate_benchmark_manifest(manifest)
    root = Path(benchmark_root)
    full_profile_path = root / model.full_profile_path
    full_profile_digest_path = root / model.full_profile_digest_path
    full_profile_bytes = _read_bounded_artifact(root, model.full_profile_path, "full profile")
    _assert_digest("full profile", full_profile_bytes, model.full_profile_sha256)
    if read_external_sha256_record(full_profile_digest_path, full_profile_path.name) != model.full_profile_sha256:
        raise ValueError("full profile checksum record does not match benchmark manifest")
    full_profile = load_full_profile(full_profile_path, full_profile_digest_path, root)
    if full_profile.profile_id != model.full_profile_id or full_profile.profile_revision != model.full_profile_revision:
        raise ValueError("full profile identity does not match benchmark manifest")

    smoke_profile_path = root / model.smoke_profile_path
    smoke_profile_digest_path = root / model.smoke_profile_digest_path
    smoke_profile_bytes = _read_bounded_artifact(root, model.smoke_profile_path, "smoke profile")
    _assert_digest("smoke profile", smoke_profile_bytes, model.smoke_profile_sha256)
    if read_external_sha256_record(smoke_profile_digest_path, smoke_profile_path.name) != model.smoke_profile_sha256:
        raise ValueError("smoke profile checksum record does not match benchmark manifest")
    smoke_profile = load_smoke_profile(smoke_profile_path, smoke_profile_digest_path, root)
    if smoke_profile.profile_id != model.smoke_profile_id or smoke_profile.profile_revision != model.smoke_profile_revision:
        raise ValueError("smoke profile identity does not match benchmark manifest")
    return model


def build_benchmark_manifest(
    benchmark_root: Path,
    *,
    benchmark_version: BenchmarkVersion,
) -> BenchmarkManifest:
    """Build one release manifest from already-frozen profile artifacts."""

    root = Path(benchmark_root)
    expected = _EXPECTED_BINDINGS[benchmark_version]
    full_profile_path = root / expected["full_profile_path"]
    full_profile_digest_path = root / expected["full_profile_digest_path"]
    smoke_profile_path = root / _SMOKE_PROFILE_PATH
    smoke_profile_digest_path = root / _SMOKE_PROFILE_DIGEST_PATH
    load_full_profile(full_profile_path, full_profile_digest_path, root)
    load_smoke_profile(smoke_profile_path, smoke_profile_digest_path, root)
    return BenchmarkManifest.model_validate(
        {
            "schema_version": BENCHMARK_MANIFEST_SCHEMA_VERSION,
            "artifact_type": BENCHMARK_MANIFEST_ARTIFACT_TYPE,
            "benchmark_contract": BENCHMARK_CONTRACT,
            "benchmark_version": benchmark_version,
            "full_profile_id": "full",
            "full_profile_revision": expected["full_profile_revision"],
            "full_profile_path": expected["full_profile_path"],
            "full_profile_digest_path": expected["full_profile_digest_path"],
            "full_profile_sha256": hashlib.sha256(full_profile_path.read_bytes()).hexdigest(),
            "smoke_profile_id": "smoke",
            "smoke_profile_revision": "revision-001",
            "smoke_profile_path": _SMOKE_PROFILE_PATH,
            "smoke_profile_digest_path": _SMOKE_PROFILE_DIGEST_PATH,
            "smoke_profile_sha256": hashlib.sha256(smoke_profile_path.read_bytes()).hexdigest(),
        }
    )


def write_benchmark_manifest(
    manifest_path: Path,
    digest_path: Path,
    benchmark_root: Path,
    *,
    benchmark_version: BenchmarkVersion,
) -> BenchmarkManifest:
    manifest = validate_benchmark_manifest_artifacts(
        build_benchmark_manifest(benchmark_root, benchmark_version=benchmark_version),
        benchmark_root,
    )
    manifest_bytes = canonical_benchmark_manifest_bytes(manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(manifest_bytes)
    digest_path.write_text(
        f"{hashlib.sha256(manifest_bytes).hexdigest()}  {manifest_path.name}\n",
        encoding="ascii",
    )
    return manifest


def load_benchmark_manifest(
    manifest_path: Path,
    digest_path: Path,
    benchmark_root: Path,
) -> BenchmarkManifest:
    try:
        manifest_bytes = manifest_path.read_bytes()
    except OSError as exc:
        raise ValueError("benchmark manifest is unavailable") from exc
    expected_digest = read_external_sha256_record(digest_path, manifest_path.name)
    if hashlib.sha256(manifest_bytes).hexdigest() != expected_digest:
        raise ValueError("benchmark manifest digest mismatch")
    try:
        payload = json.loads(manifest_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
        raise ValueError("benchmark manifest JSON is invalid") from exc
    model = validate_benchmark_manifest(payload)
    if manifest_bytes != canonical_benchmark_manifest_bytes(model):
        raise ValueError("benchmark manifest bytes are not canonical")
    return validate_benchmark_manifest_artifacts(model, benchmark_root)


__all__ = [
    "BENCHMARK_CONTRACT",
    "BENCHMARK_MANIFEST_ARTIFACT_TYPE",
    "BENCHMARK_MANIFEST_SCHEMA_VERSION",
    "BENCHMARK_VERSION_001",
    "BENCHMARK_VERSION_002",
    "BenchmarkManifest",
    "BenchmarkVersion",
    "benchmark_manifest_sha256",
    "build_benchmark_manifest",
    "canonical_benchmark_manifest_bytes",
    "load_benchmark_manifest",
    "validate_benchmark_manifest",
    "validate_benchmark_manifest_artifacts",
    "write_benchmark_manifest",
]
