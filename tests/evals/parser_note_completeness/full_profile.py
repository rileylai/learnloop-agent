"""Versioned thirteen-case diagnostic full-profile contract."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Mapping, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator, model_validator

from .normalized_document import (
    ArtifactRole,
    NormalizedDocument,
    SourceType,
    canonical_normalized_document_bytes,
)


FULL_PROFILE_SCHEMA_VERSION = "full-profile/1.0.0"
FULL_PROFILE_ARTIFACT_TYPE = "parser_note_completeness_full_profile"
BENCHMARK_CONTRACT = "parser-note-completeness-v1"
FULL_PROFILE_ID = "full"
FULL_PROFILE_REVISION = "revision-001"
FULL_CASE_IDS = (
    "P01",
    "P02",
    "P03",
    "P04",
    "W01",
    "W02",
    "W03",
    "Y01",
    "Y02",
    "C01",
    "C02",
    "S01",
    "S02",
)

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_SHA256_RE = re.compile(_SHA256_PATTERN)
_ALLOWED_ARTIFACT_ROOTS = frozenset({"fixtures", "governance", "reference_documents"})

Sha256 = Annotated[StrictStr, Field(pattern=_SHA256_PATTERN)]
FullCaseId = Literal[
    "P01",
    "P02",
    "P03",
    "P04",
    "W01",
    "W02",
    "W03",
    "Y01",
    "Y02",
    "C01",
    "C02",
    "S01",
    "S02",
]


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


_EXPECTED_PATHS = {
    "P01": {
        "source_artifact_path": "fixtures/P01/revision-001/source.pdf",
        "source_digest_path": "fixtures/P01/revision-001/source.sha256",
        "producer_configuration_path": "governance/P01/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/P01/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/P01/revision-001/normalized_document.sha256",
    },
    "P02": {
        "source_artifact_path": "fixtures/P02/revision-001/source.pdf",
        "source_digest_path": "fixtures/P02/revision-001/source.sha256",
        "producer_configuration_path": "governance/P02/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/P02/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/P02/revision-001/normalized_document.sha256",
    },
    "P03": {
        "source_artifact_path": "fixtures/P03/revision-001/source.pdf",
        "source_digest_path": "fixtures/P03/revision-001/source.sha256",
        "producer_configuration_path": "governance/P03/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/P03/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/P03/revision-001/normalized_document.sha256",
    },
    "P04": {
        "source_artifact_path": "fixtures/P04/revision-001/source.pdf",
        "source_digest_path": "fixtures/P04/revision-001/source.sha256",
        "producer_configuration_path": "governance/P04/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/P04/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/P04/revision-001/normalized_document.sha256",
    },
    "W01": {
        "source_artifact_path": "fixtures/W01/revision-001/source.html",
        "source_digest_path": "fixtures/W01/revision-001/source.sha256",
        "producer_configuration_path": "governance/W01/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/W01/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/W01/revision-001/normalized_document.sha256",
    },
    "W02": {
        "source_artifact_path": "fixtures/W02/revision-001/source.html",
        "source_digest_path": "fixtures/W02/revision-001/source.sha256",
        "producer_configuration_path": "governance/W02/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/W02/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/W02/revision-001/normalized_document.sha256",
    },
    "W03": {
        "source_artifact_path": "fixtures/W03/revision-001/source.html",
        "source_digest_path": "fixtures/W03/revision-001/source.sha256",
        "producer_configuration_path": "governance/W03/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/W03/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/W03/revision-001/normalized_document.sha256",
    },
    "Y01": {
        "source_artifact_path": "fixtures/Y01/revision-001/source_snapshot.json",
        "source_digest_path": "fixtures/Y01/revision-001/source_snapshot.sha256",
        "producer_configuration_path": "governance/Y01/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/Y01/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/Y01/revision-001/normalized_document.sha256",
    },
    "Y02": {
        "source_artifact_path": "fixtures/Y02/revision-001/source_snapshot.json",
        "source_digest_path": "fixtures/Y02/revision-001/source_snapshot.sha256",
        "producer_configuration_path": "governance/Y02/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/Y02/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/Y02/revision-001/normalized_document.sha256",
    },
    "C01": {
        "source_artifact_path": "fixtures/C01/revision-001/source.json",
        "source_digest_path": "fixtures/C01/revision-001/source.sha256",
        "producer_configuration_path": "governance/C01/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/C01/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/C01/revision-001/normalized_document.sha256",
    },
    "C02": {
        "source_artifact_path": "fixtures/C02/revision-001/source.json",
        "source_digest_path": "fixtures/C02/revision-001/source.sha256",
        "producer_configuration_path": "governance/C02/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/C02/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/C02/revision-001/normalized_document.sha256",
    },
    "S01": {
        "source_artifact_path": "fixtures/S01/revision-001/source.png",
        "source_digest_path": "fixtures/S01/revision-001/source.sha256",
        "producer_configuration_path": "governance/S01/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/S01/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/S01/revision-001/normalized_document.sha256",
    },
    "S02": {
        "source_artifact_path": "fixtures/S02/revision-001/source_manifest.json",
        "source_digest_path": "fixtures/S02/revision-001/source.sha256",
        "producer_configuration_path": "governance/S02/revision-001/producer_configuration.json",
        "reference_path": "reference_documents/S02/revision-001/normalized_document.json",
        "reference_digest_path": "reference_documents/S02/revision-001/normalized_document.sha256",
    },
}

_EXPECTED_SOURCE_TYPES = {
    "P01": SourceType.PDF,
    "P02": SourceType.PDF,
    "P03": SourceType.PDF,
    "P04": SourceType.PDF,
    "W01": SourceType.WEB,
    "W02": SourceType.WEB,
    "W03": SourceType.WEB,
    "Y01": SourceType.YOUTUBE,
    "Y02": SourceType.YOUTUBE,
    "C01": SourceType.CHAT,
    "C02": SourceType.CHAT,
    "S01": SourceType.SCREENSHOTS,
    "S02": SourceType.SCREENSHOTS,
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


class FullCase(_StrictFrozenModel):
    case_id: FullCaseId
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
    def _validate_revision_paths(self) -> "FullCase":
        expected = _EXPECTED_PATHS[self.case_id]
        for field_name, expected_path in expected.items():
            if getattr(self, field_name) != expected_path:
                raise ValueError(f"{self.case_id} must bind its revision-001 canonical artifact paths")
        return self


class FullProfile(_StrictFrozenModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
        json_schema_extra={
            "$id": f"https://learnloop.local/schemas/{FULL_PROFILE_SCHEMA_VERSION}",
        },
    )

    schema_version: Literal["full-profile/1.0.0"]
    artifact_type: Literal["parser_note_completeness_full_profile"]
    benchmark_contract: Literal["parser-note-completeness-v1"]
    profile_id: Literal["full"]
    profile_revision: Literal["revision-001"]
    execution_mode: Literal["development"]
    membership: Literal["diagnostic"]
    cases: Tuple[FullCase, ...] = Field(min_length=13, max_length=13)

    @model_validator(mode="after")
    def _validate_case_topology(self) -> "FullProfile":
        case_ids = tuple(case.case_id for case in self.cases)
        if case_ids != FULL_CASE_IDS:
            raise ValueError(
                "full profile cases must be exactly P01-P04, W01-W03, Y01-Y02, C01-C02, S01-S02 in order"
            )
        return self


FullProfileInput = Union[FullProfile, Mapping[str, Any]]


def validate_full_profile(profile: FullProfileInput) -> FullProfile:
    if isinstance(profile, FullProfile):
        return profile
    return FullProfile.model_validate(profile)


def canonical_full_profile_bytes(profile: FullProfileInput) -> bytes:
    model = validate_full_profile(profile)
    payload = json.dumps(
        model.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return f"{payload}\n".encode("utf-8")


def full_profile_sha256(profile: FullProfileInput) -> str:
    return hashlib.sha256(canonical_full_profile_bytes(profile)).hexdigest()


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


def validate_full_profile_artifacts(
    profile: FullProfileInput,
    benchmark_root: Path,
) -> FullProfile:
    """Validate every full-profile binding against bytes bounded by ``benchmark_root``."""

    model = validate_full_profile(profile)
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
        _assert_digest("producer configuration", configuration_bytes, case.producer_configuration_sha256)
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

    return model


def build_full_profile(benchmark_root: Path) -> FullProfile:
    """Build profile bindings from existing immutable artifacts under ``benchmark_root``."""

    root = Path(benchmark_root)
    cases = []
    for case_id in FULL_CASE_IDS:
        paths = _EXPECTED_PATHS[case_id]
        source_bytes = _read_bounded_artifact(root, paths["source_artifact_path"], "source artifact")
        configuration_bytes = _read_bounded_artifact(root, paths["producer_configuration_path"], "producer configuration")
        reference_bytes = _read_bounded_artifact(root, paths["reference_path"], "canonical reference")
        cases.append(
            {
                "case_id": case_id,
                "fixture_revision": "revision-001",
                **paths,
                "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "producer_configuration_sha256": hashlib.sha256(configuration_bytes).hexdigest(),
                "reference_sha256": hashlib.sha256(reference_bytes).hexdigest(),
            }
        )
    return FullProfile.model_validate(
        {
            "schema_version": FULL_PROFILE_SCHEMA_VERSION,
            "artifact_type": FULL_PROFILE_ARTIFACT_TYPE,
            "benchmark_contract": BENCHMARK_CONTRACT,
            "profile_id": FULL_PROFILE_ID,
            "profile_revision": FULL_PROFILE_REVISION,
            "execution_mode": "development",
            "membership": "diagnostic",
            "cases": cases,
        }
    )


def write_full_profile(profile_path: Path, digest_path: Path, benchmark_root: Path) -> FullProfile:
    profile = validate_full_profile_artifacts(build_full_profile(benchmark_root), benchmark_root)
    profile_bytes = canonical_full_profile_bytes(profile)
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_bytes(profile_bytes)
    digest_path.write_text(
        f"{hashlib.sha256(profile_bytes).hexdigest()}  {profile_path.name}\n",
        encoding="ascii",
    )
    return profile


def load_full_profile(
    profile_path: Path,
    digest_path: Path,
    benchmark_root: Path,
) -> FullProfile:
    try:
        profile_bytes = profile_path.read_bytes()
    except OSError as exc:
        raise ValueError("full profile is unavailable") from exc
    expected_digest = read_external_sha256_record(digest_path, profile_path.name)
    if hashlib.sha256(profile_bytes).hexdigest() != expected_digest:
        raise ValueError("full profile digest mismatch")
    try:
        payload = json.loads(profile_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
        raise ValueError("full profile JSON is invalid") from exc
    model = validate_full_profile(payload)
    if profile_bytes != canonical_full_profile_bytes(model):
        raise ValueError("full profile bytes are not canonical")
    return validate_full_profile_artifacts(model, benchmark_root)


__all__ = [
    "BENCHMARK_CONTRACT",
    "FULL_CASE_IDS",
    "FULL_PROFILE_ARTIFACT_TYPE",
    "FULL_PROFILE_ID",
    "FULL_PROFILE_REVISION",
    "FULL_PROFILE_SCHEMA_VERSION",
    "FullCase",
    "FullProfile",
    "build_full_profile",
    "canonical_full_profile_bytes",
    "full_profile_sha256",
    "load_full_profile",
    "read_external_sha256_record",
    "validate_full_profile",
    "validate_full_profile_artifacts",
    "write_full_profile",
]
