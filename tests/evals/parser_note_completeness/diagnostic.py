"""Deterministic wiring from diagnostic profiles to local run plans."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Tuple, Union

from .full_profile import FullProfile, load_full_profile, canonical_full_profile_bytes
from .run_plan import RunPlan, RunSlot, canonical_run_plan_bytes, run_plan_sha256
from .smoke_profile import (
    SmokeProfile,
    canonical_smoke_profile_bytes,
    load_smoke_profile,
)


DiagnosticProfile = Union[SmokeProfile, FullProfile]
_PROFILE_ARTIFACT_TYPES = {
    "parser_note_completeness_smoke_profile": "smoke",
    "parser_note_completeness_full_profile": "full",
}


def _bounded_profile_file(benchmark_root: Path, path: Path, label: str) -> Path:
    try:
        root = benchmark_root.resolve(strict=True)
        resolved = path.resolve(strict=True)
        resolved.relative_to(root)
        if not resolved.is_file():
            raise OSError("not a regular file")
        return resolved
    except (OSError, ValueError) as exc:
        raise ValueError(f"{label} is unavailable or outside the benchmark root") from exc


def load_diagnostic_profile(
    profile_path: Path,
    profile_digest_path: Path,
    benchmark_root: Path,
) -> Tuple[DiagnosticProfile, str]:
    """Load one supported profile and return it with its verified byte digest."""

    root = Path(benchmark_root)
    safe_profile_path = _bounded_profile_file(root, Path(profile_path), "diagnostic profile")
    safe_digest_path = _bounded_profile_file(
        root,
        Path(profile_digest_path),
        "diagnostic profile digest",
    )
    try:
        payload = json.loads(safe_profile_path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise ValueError("diagnostic profile JSON is invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("diagnostic profile JSON must be an object")
    artifact_type = payload.get("artifact_type")
    profile_kind = (
        _PROFILE_ARTIFACT_TYPES.get(artifact_type)
        if isinstance(artifact_type, str)
        else None
    )
    if profile_kind == "smoke":
        profile: DiagnosticProfile = load_smoke_profile(
            safe_profile_path,
            safe_digest_path,
            root,
        )
    elif profile_kind == "full":
        profile = load_full_profile(safe_profile_path, safe_digest_path, root)
    else:
        raise ValueError("unsupported diagnostic profile artifact type")
    try:
        profile_digest = hashlib.sha256(safe_profile_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ValueError("diagnostic profile is unavailable") from exc
    return profile, profile_digest


def _profile_bytes(profile: DiagnosticProfile) -> bytes:
    if isinstance(profile, SmokeProfile):
        return canonical_smoke_profile_bytes(profile)
    return canonical_full_profile_bytes(profile)


def materialize_diagnostic_run_plan(
    profile: DiagnosticProfile,
    profile_digest: str,
) -> Tuple[RunPlan, str]:
    """Materialize a profile into the existing immutable diagnostic plan contract."""

    profile_bytes = _profile_bytes(profile)
    actual_profile_digest = hashlib.sha256(profile_bytes).hexdigest()
    if actual_profile_digest != profile_digest:
        raise ValueError("diagnostic profile digest mismatch")

    slots = tuple(
        RunSlot(
            slot_id=f"{profile.profile_id}-{case.case_id}",
            case_id=case.case_id,
            operation="validate_reference",
            reference_path=case.reference_path,
            digest_path=case.reference_digest_path,
            reference_sha256=case.reference_sha256,
            membership="diagnostic",
        )
        for case in profile.cases
    )
    plan = RunPlan(
        schema_version="run-plan/1.0.0",
        runner_version="parser-note-completeness-runner/1.0.0",
        artifact_type="parser_note_completeness_run_plan",
        plan_id=f"{profile.profile_id}-{profile.profile_revision}-{profile_digest}",
        plan_revision=profile.profile_revision,
        execution_mode="development",
        slots=slots,
    )
    return plan, run_plan_sha256(plan)


def materialize_profile_run_plan(
    profile_path: Path,
    profile_digest_path: Path,
    benchmark_root: Path,
) -> Tuple[RunPlan, str]:
    """Load and validate a profile, then deterministically materialize its plan."""

    profile, profile_digest = load_diagnostic_profile(
        profile_path,
        profile_digest_path,
        benchmark_root,
    )
    return materialize_diagnostic_run_plan(profile, profile_digest)


def _write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def write_diagnostic_run_plan(
    profile_path: Path,
    profile_digest_path: Path,
    benchmark_root: Path,
    plan_path: Path,
    plan_digest_path: Path,
) -> Tuple[RunPlan, str]:
    """Write a canonical immutable run plan and its external SHA-256 record."""

    if Path(plan_path) == Path(plan_digest_path):
        raise ValueError("run plan and digest paths must differ")
    plan, digest = materialize_profile_run_plan(
        profile_path,
        profile_digest_path,
        benchmark_root,
    )
    plan_bytes = canonical_run_plan_bytes(plan)
    _write_once(Path(plan_path), plan_bytes)
    try:
        _write_once(
            Path(plan_digest_path),
            f"{digest}  {Path(plan_path).name}\n".encode("ascii"),
        )
    except Exception:
        try:
            Path(plan_path).unlink()
        except OSError:
            pass
        raise
    return plan, digest


__all__ = [
    "DiagnosticProfile",
    "load_diagnostic_profile",
    "materialize_diagnostic_run_plan",
    "materialize_profile_run_plan",
    "write_diagnostic_run_plan",
]
