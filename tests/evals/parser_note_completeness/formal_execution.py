"""Minimal fail-closed formal execution identity and publication contracts.

The existing runner remains the execution/history/receipt/store implementation.
This module adds only the missing immutable bindings.  It cannot represent a
pending authority state as a formal manifest.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Annotated, Any, Literal, Mapping, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, StrictStr, model_validator


FORMAL_MANIFEST_SCHEMA_VERSION = "parser-note-completeness-formal-manifest/1.0.0"
FORMAL_PROVENANCE_SCHEMA_VERSION = "parser-note-completeness-formal-provenance/1.0.0"
FROZEN_CASE_IDS = (
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
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_IMAGE_PATTERN = r"^[a-z0-9][a-z0-9._/-]*@sha256:[0-9a-f]{64}$"
Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class FormalCaseBinding(_StrictFrozenModel):
    case_id: StrictStr = Field(min_length=1)
    fixture_revision: StrictStr = Field(pattern=r"^revision-[0-9]{3}$")
    source_sha256: Digest
    reference_sha256: Digest
    gold_sha256: Digest
    fixture_authority_sha256: Digest
    gold_authority_sha256: Digest


class FormalExecutionManifest(_StrictFrozenModel):
    schema_version: Literal["parser-note-completeness-formal-manifest/1.0.0"] = FORMAL_MANIFEST_SCHEMA_VERSION
    artifact_type: Literal["parser_note_completeness_formal_manifest"] = "parser_note_completeness_formal_manifest"
    membership: Literal["formal"] = "formal"
    authority_status: Literal["independent_closure_complete"] = "independent_closure_complete"
    compatibility_policy: Literal["exact_fail_closed"] = "exact_fail_closed"
    benchmark_manifest_sha256: Digest
    profile_sha256: Digest
    cases: Tuple[FormalCaseBinding, ...]
    parser_registry_sha256: Digest
    parser_implementation_sha256: Digest
    parser_authority_sha256: Digest
    candidate_build_sha256: Digest
    execution_plan_sha256: Digest
    dependency_lock_sha256: Digest
    container_image_digest: StrictStr = Field(pattern=_IMAGE_PATTERN)
    launcher_policy_sha256: Digest
    governance_authority_sha256: Digest
    no_egress_authority_sha256: Digest

    @model_validator(mode="after")
    def _validate_exact_case_membership(self) -> "FormalExecutionManifest":
        if tuple(binding.case_id for binding in self.cases) != FROZEN_CASE_IDS:
            raise ValueError("formal manifest requires the exact frozen 13-case order")
        return self


class FormalRunProvenance(_StrictFrozenModel):
    schema_version: Literal["parser-note-completeness-formal-provenance/1.0.0"] = FORMAL_PROVENANCE_SCHEMA_VERSION
    repository_revision: StrictStr = Field(min_length=1)
    working_tree_diff_sha256: Digest
    dependency_lock_sha256: Digest
    python_version: StrictStr = Field(min_length=1)
    platform_identity: StrictStr = Field(min_length=1)
    container_image_digest: StrictStr = Field(pattern=_IMAGE_PATTERN)
    launcher_policy_sha256: Digest
    model_identity: StrictStr = Field(min_length=1)
    seed: StrictStr = Field(min_length=1)


def _canonical_mapping_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            dict(payload),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_formal_manifest_bytes(
    payload: FormalExecutionManifest | Mapping[str, Any],
) -> bytes:
    model = payload if isinstance(payload, FormalExecutionManifest) else FormalExecutionManifest.model_validate(payload)
    return _canonical_mapping_bytes(model.model_dump(mode="json"))


def formal_manifest_sha256(payload: FormalExecutionManifest | Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_formal_manifest_bytes(payload)).hexdigest()


def derive_formal_run_id(
    manifest: FormalExecutionManifest,
    *,
    allowlisted_configuration: Mapping[str, Any],
    execution_environment: Mapping[str, Any],
    provenance: FormalRunProvenance,
) -> str:
    identity = {
        "formal_manifest_sha256": formal_manifest_sha256(manifest),
        "allowlisted_configuration": dict(allowlisted_configuration),
        "execution_environment": dict(execution_environment),
        "provenance": provenance.model_dump(mode="json"),
    }
    return hashlib.sha256(_canonical_mapping_bytes(identity)).hexdigest()


def publish_terminal_pointer(
    store: Path,
    manifest: FormalExecutionManifest,
    run_id: str,
    terminal_package_sha256: str,
) -> Path:
    """Create one immutable local publication pointer after authority closure.

    Requiring a validated FormalExecutionManifest makes pending authority
    inexpressible at this boundary.  The caller must separately validate the
    terminal package and replay before invoking this function.
    """

    for label, value in (("run_id", run_id), ("terminal package digest", terminal_package_sha256)):
        if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
            raise ValueError(f"invalid {label}")
    publication_root = store / "publications"
    publication_root.mkdir(parents=True, exist_ok=True)
    path = publication_root / f"{run_id}.json"
    payload = _canonical_mapping_bytes(
        {
            "artifact_type": "formal_terminal_publication_pointer",
            "formal_manifest_sha256": formal_manifest_sha256(manifest),
            "run_id": run_id,
            "terminal_package_sha256": terminal_package_sha256,
        }
    )
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    return path

