from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from .formal_execution import (
    FROZEN_CASE_IDS,
    FormalCaseBinding,
    FormalExecutionManifest,
    FormalRunProvenance,
    canonical_formal_manifest_bytes,
    derive_formal_run_id,
    publish_terminal_pointer,
)


DIGEST = "a" * 64


def _case(case_id: str) -> FormalCaseBinding:
    return FormalCaseBinding(
        case_id=case_id,
        fixture_revision="revision-001",
        source_sha256=DIGEST,
        reference_sha256=DIGEST,
        gold_sha256=DIGEST,
        fixture_authority_sha256=DIGEST,
        gold_authority_sha256=DIGEST,
    )


def _manifest() -> FormalExecutionManifest:
    return FormalExecutionManifest(
        benchmark_manifest_sha256=DIGEST,
        profile_sha256=DIGEST,
        cases=tuple(_case(case_id) for case_id in FROZEN_CASE_IDS),
        parser_registry_sha256=DIGEST,
        parser_implementation_sha256=DIGEST,
        parser_authority_sha256=DIGEST,
        candidate_build_sha256=DIGEST,
        execution_plan_sha256=DIGEST,
        dependency_lock_sha256=DIGEST,
        container_image_digest=f"learnloop-benchmark@sha256:{DIGEST}",
        launcher_policy_sha256=DIGEST,
        governance_authority_sha256=DIGEST,
        no_egress_authority_sha256=DIGEST,
    )


def test_formal_manifest_is_fail_closed_and_binds_exactly_thirteen_cases() -> None:
    manifest = _manifest()
    payload = canonical_formal_manifest_bytes(manifest)

    assert tuple(binding.case_id for binding in manifest.cases) == FROZEN_CASE_IDS
    assert b'"authority_status":"independent_closure_complete"' in payload
    assert b'"membership":"formal"' in payload


def test_formal_manifest_rejects_missing_or_duplicate_case_membership() -> None:
    values = _manifest().model_dump(mode="python")
    values["cases"] = values["cases"][:-1]
    with pytest.raises(ValidationError, match="exact frozen 13-case order"):
        FormalExecutionManifest.model_validate(values)

    values = _manifest().model_dump(mode="python")
    values["cases"] = (*values["cases"][:-1], values["cases"][0])
    with pytest.raises(ValidationError, match="exact frozen 13-case order"):
        FormalExecutionManifest.model_validate(values)


def test_pending_authority_cannot_be_encoded_as_a_formal_manifest() -> None:
    values = _manifest().model_dump(mode="python")
    values["authority_status"] = "pending"
    with pytest.raises(ValidationError):
        FormalExecutionManifest.model_validate(values)


def test_run_id_binds_manifest_configuration_environment_and_provenance() -> None:
    provenance = FormalRunProvenance(
        repository_revision="deadbeef",
        working_tree_diff_sha256=DIGEST,
        dependency_lock_sha256=DIGEST,
        python_version="3.12.11",
        platform_identity="linux-aarch64",
        container_image_digest=f"learnloop-benchmark@sha256:{DIGEST}",
        launcher_policy_sha256=DIGEST,
        model_identity="not_applicable",
        seed="not_applicable",
    )
    first = derive_formal_run_id(
        _manifest(),
        allowlisted_configuration={"parser": "current"},
        execution_environment={"docker_engine": "28.5.1"},
        provenance=provenance,
    )
    second = derive_formal_run_id(
        _manifest(),
        allowlisted_configuration={"parser": "current"},
        execution_environment={"docker_engine": "28.5.1"},
        provenance=provenance,
    )
    changed = derive_formal_run_id(
        _manifest(),
        allowlisted_configuration={"parser": "different"},
        execution_environment={"docker_engine": "28.5.1"},
        provenance=provenance,
    )

    assert first == second
    assert first != changed


def test_publication_pointer_is_content_addressed_and_never_overwritten(tmp_path) -> None:
    path = publish_terminal_pointer(tmp_path, _manifest(), "b" * 64, "c" * 64)
    assert json.loads(path.read_text(encoding="utf-8"))["terminal_package_sha256"] == "c" * 64

    with pytest.raises(FileExistsError):
        publish_terminal_pointer(tmp_path, _manifest(), "b" * 64, "d" * 64)
