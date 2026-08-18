"""Versioned five-case diagnostic smoke-profile contract."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Mapping, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator, model_validator

from .normalized_document import ArtifactRole, NormalizedDocument, SourceType, canonical_normalized_document_bytes

SMOKE_PROFILE_SCHEMA_VERSION = "smoke-profile/1.0.0"
SMOKE_PROFILE_ARTIFACT_TYPE = "parser_note_completeness_smoke_profile"
BENCHMARK_CONTRACT = "parser-note-completeness-v1"
SMOKE_PROFILE_ID = "smoke"
SMOKE_PROFILE_REVISION = "revision-001"
SMOKE_CASE_IDS = ("P01", "W01", "Y01", "C01", "S01")

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_SHA256_RE = re.compile(_SHA256_PATTERN)
_ALLOWED_ARTIFACT_ROOTS = frozenset({"fixtures", "governance", "reference_documents"})

Sha256 = Annotated[StrictStr, Field(pattern=_SHA256_PATTERN)]
SmokeCaseId = Literal["P01", "W01", "Y01", "C01", "S01"]


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


_EXPECTED_PATHS = {
    "P01": {
        "source_artifact_path": "fixtures/P01/revision-001/source.pdf",
        "source_digest_path": "fixtures/P01/revision-001/source.sha256",
        "producer_configuration_path": "governance/P01/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/P01/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/P01/revision-001/normalized_document.sha256",
    },
    "W01": {
        "source_artifact_path": "fixtures/W01/revision-001/source.html",
        "source_digest_path": "fixtures/W01/revision-001/source.sha256",
        "producer_configuration_path": "governance/W01/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/W01/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/W01/revision-001/normalized_document.sha256",
    },
    "Y01": {
        "source_artifact_path": "fixtures/Y01/revision-001/source_snapshot.json",
        "source_digest_path": "fixtures/Y01/revision-001/source_snapshot.sha256",
        "producer_configuration_path": "governance/Y01/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/Y01/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/Y01/revision-001/normalized_document.sha256",
    },
    "C01": {
        "source_artifact_path": "fixtures/C01/revision-001/source.json",
        "source_digest_path": "fixtures/C01/revision-001/source.sha256",
        "producer_configuration_path": "governance/C01/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/C01/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/C01/revision-001/normalized_document.sha256",
    },
    "S01": {
        "source_artifact_path": "fixtures/S01/revision-001/source.png",
        "source_digest_path": "fixtures/S01/revision-001/source.sha256",
        "producer_configuration_path": "governance/S01/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/S01/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/S01/revision-001/normalized_document.sha256",
    },
}

_EXPECTED_SOURCE_TYPES = {
    "P01": SourceType.PDF,
    "W01": SourceType.WEB,
    "Y01": SourceType.YOUTUBE,
    "C01": SourceType.CHAT,
    "S01": SourceType.SCREENSHOTS,
}


def _validate_relative_artifact_path(value: str) -> str:
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
        raise ValueError("artifact paths must be normalized benchmark-root-relative POSIX paths")
    return value


class SmokeCase(_StrictFrozenModel):
    case_id: SmokeCaseId
    fixture_revision: Literal["revision-001"]
    source_artifact_path: StrictStr = Field(min_length=1)
    source_digest_path: StrictStr = Field(min_length=1)
    source_sha256: Sha256
    producer_configuration_path: StrictStr = Field(min_length=1)
    producer_configuration_sha256: Sha256
    reference_path: StrictStr = Field(min_length=1)
    reference_digest_path: StrictStr = Field(min_length=1)
    reference_sha256: Sha256

    @field_validator(
        "source_artifact_path",
        "source_digest_path",
        "producer_configuration_path",
        "reference_path",
        "reference_digest_path",
    )
    @classmethod
    def _validate_paths(cls, value: str) -> str:
        return _validate_relative_artifact_path(value)

    @model_validator(mode="after")
    def _validate_revision_paths(self) -> "SmokeCase":
        expected = _EXPECTED_PATHS[self.case_id]
        for field_name, expected_path in expected.items():
            if getattr(self, field_name) != expected_path:
                raise ValueError(f"{self.case_id} must bind its revision-001 canonical artifact paths")
        return self


class SmokeProfile(_StrictFrozenModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
        json_schema_extra={
            "$id": f"https://learnloop.local/schemas/{SMOKE_PROFILE_SCHEMA_VERSION}",
        },
    )

    schema_version: Literal["smoke-profile/1.0.0"]
    artifact_type: Literal["parser_note_completeness_smoke_profile"]
    benchmark_contract: Literal["parser-note-completeness-v1"]
    profile_id: Literal["smoke"]
    profile_revision: Literal["revision-001"]
    execution_mode: Literal["development"]
    membership: Literal["diagnostic"]
    cases: Tuple[SmokeCase, ...] = Field(min_length=5, max_length=5)

    @model_validator(mode="after")
    def _validate_case_topology(self) -> "SmokeProfile":
        case_ids = tuple(case.case_id for case in self.cases)
        if case_ids != SMOKE_CASE_IDS:
            raise ValueError("smoke profile cases must be exactly P01, W01, Y01, C01, S01 in order")
        return self


SmokeProfileInput = Union[SmokeProfile, Mapping[str, Any]]


def validate_smoke_profile(profile: SmokeProfileInput) -> SmokeProfile:
    if isinstance(profile, SmokeProfile):
        return profile
    return SmokeProfile.model_validate(profile)


def canonical_smoke_profile_bytes(profile: SmokeProfileInput) -> bytes:
    model = validate_smoke_profile(profile)
    payload = json.dumps(
        model.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return f"{payload}\n".encode("utf-8")


def smoke_profile_sha256(profile: SmokeProfileInput) -> str:
    return hashlib.sha256(canonical_smoke_profile_bytes(profile)).hexdigest()


def _parse_external_sha256_record(data: bytes, expected_filename: str) -> str:
    try:
        fields = data.decode("ascii").strip().split()
    except UnicodeError as exc:
        raise ValueError("external digest record is unavailable") from exc
    if len(fields) != 2 or fields[1] != expected_filename or _SHA256_RE.fullmatch(fields[0]) is None:
        raise ValueError("invalid external digest record")
    return fields[0]


def read_external_sha256_record(path: Path, expected_filename: str) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ValueError("external digest record is unavailable") from exc
    return _parse_external_sha256_record(data, expected_filename)


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


def validate_smoke_profile_artifacts(
    profile: SmokeProfileInput,
    benchmark_root: Path,
) -> SmokeProfile:
    """Validate every profile binding against immutable bytes under ``benchmark_root``."""

    model = validate_smoke_profile(profile)
    root = Path(benchmark_root)
    for case in model.cases:
        source_bytes = _read_bounded_artifact(root, case.source_artifact_path, "source artifact")
        _assert_digest("source artifact", source_bytes, case.source_sha256)
        source_digest = _parse_external_sha256_record(
            _read_bounded_artifact(root, case.source_digest_path, "source checksum record"),
            PurePosixPath(case.source_artifact_path).name,
        )
        if source_digest != case.source_sha256:
            raise ValueError("source checksum record does not match profile")
        if hashlib.sha256(source_bytes).hexdigest() != source_digest:
            raise ValueError("source checksum record does not match source bytes")

        configuration_bytes = _read_bounded_artifact(
            root,
            case.producer_configuration_path,
            "producer configuration",
        )
        _assert_digest(
            "producer configuration",
            configuration_bytes,
            case.producer_configuration_sha256,
        )
        try:
            configuration = json.loads(configuration_bytes)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
            raise ValueError("producer configuration JSON is invalid") from exc
        if not isinstance(configuration, dict):
            raise ValueError("producer configuration must be a JSON object")

        reference_bytes = _read_bounded_artifact(root, case.reference_path, "canonical reference")
        _assert_digest("canonical reference", reference_bytes, case.reference_sha256)
        reference_digest = _parse_external_sha256_record(
            _read_bounded_artifact(root, case.reference_digest_path, "reference checksum record"),
            PurePosixPath(case.reference_path).name,
        )
        if reference_digest != case.reference_sha256:
            raise ValueError("reference checksum record does not match profile")
        if hashlib.sha256(reference_bytes).hexdigest() != reference_digest:
            raise ValueError("reference checksum record does not match reference bytes")
        try:
            reference_payload = json.loads(reference_bytes)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
            raise ValueError("canonical reference JSON is invalid") from exc
        try:
            document = NormalizedDocument.model_validate(reference_payload)
        except ValueError as exc:
            raise ValueError("canonical reference schema validation failed") from exc
        if document.artifact_role != ArtifactRole.REFERENCE_DOCUMENT:
            raise ValueError("canonical reference must be a reference_document")
        if document.document_id != case.case_id:
            raise ValueError("canonical reference document ID does not match case")
        if document.source.source_type != _EXPECTED_SOURCE_TYPES[case.case_id]:
            raise ValueError("canonical reference source type does not match case")
        if reference_bytes != canonical_normalized_document_bytes(document):
            raise ValueError("canonical reference bytes are not canonical NormalizedDocument bytes")
        if document.source.source_snapshot_sha256 != case.source_sha256:
            raise ValueError("canonical reference is not bound to the source artifact")
        if document.producer_provenance.configuration_sha256 != case.producer_configuration_sha256:
            raise ValueError("canonical reference is not bound to the producer configuration")

        if case.case_id == "Y01" and not case.source_artifact_path.endswith("/source_snapshot.json"):
            raise ValueError("Y01 must bind source_snapshot.json")

    return model


def load_smoke_profile(
    profile_path: Path,
    digest_path: Path,
    benchmark_root: Path,
) -> SmokeProfile:
    """Load a canonical profile, verify its external digest, then validate bindings."""

    try:
        profile_bytes = profile_path.read_bytes()
    except OSError as exc:
        raise ValueError("smoke profile is unavailable") from exc
    expected_digest = read_external_sha256_record(digest_path, profile_path.name)
    if hashlib.sha256(profile_bytes).hexdigest() != expected_digest:
        raise ValueError("smoke profile digest mismatch")
    try:
        payload = json.loads(profile_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
        raise ValueError("smoke profile JSON is invalid") from exc
    model = validate_smoke_profile(payload)
    if profile_bytes != canonical_smoke_profile_bytes(model):
        raise ValueError("smoke profile bytes are not canonical")
    return validate_smoke_profile_artifacts(model, benchmark_root)


__all__ = [
    "BENCHMARK_CONTRACT",
    "SMOKE_CASE_IDS",
    "SMOKE_PROFILE_ARTIFACT_TYPE",
    "SMOKE_PROFILE_ID",
    "SMOKE_PROFILE_REVISION",
    "SMOKE_PROFILE_SCHEMA_VERSION",
    "SmokeCase",
    "SmokeProfile",
    "canonical_smoke_profile_bytes",
    "load_smoke_profile",
    "read_external_sha256_record",
    "smoke_profile_sha256",
    "validate_smoke_profile",
    "validate_smoke_profile_artifacts",
]
