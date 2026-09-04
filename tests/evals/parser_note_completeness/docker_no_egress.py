"""Thin Docker-native no-egress conformance launcher.

This is intentionally not a container orchestration layer.  It creates one
container, inspects the required native Docker controls, runs the bounded probe,
and removes that exact container.  A resulting record remains non-authoritative
until independent review binds it to the formal governance record.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal, Mapping, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, StrictStr, model_validator


_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_IMAGE_PATTERN = r"^[a-z0-9][a-z0-9._/-]*@sha256:[0-9a-f]{64}$"


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class DockerNoEgressPolicy(_StrictFrozenModel):
    schema_version: Literal["docker-no-egress-policy/1.0.0"] = "docker-no-egress-policy/1.0.0"
    image: StrictStr = Field(pattern=_IMAGE_PATTERN)
    input_root: StrictStr = Field(min_length=1)
    output_root: StrictStr = Field(min_length=1)
    invocation_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    network_mode: Literal["none"] = "none"
    read_only_root: Literal[True] = True
    cap_drop: Literal["ALL"] = "ALL"
    no_new_privileges: Literal[True] = True
    tmpfs_size: Literal["16m"] = "16m"

    @model_validator(mode="after")
    def _validate_mount_roots(self) -> "DockerNoEgressPolicy":
        input_root = Path(self.input_root)
        output_root = Path(self.output_root)
        if not input_root.is_absolute() or not output_root.is_absolute():
            raise ValueError("Docker mount roots must be absolute")
        if not input_root.is_dir() or not output_root.is_dir():
            raise ValueError("Docker mount roots must exist as directories")
        resolved_input = input_root.resolve()
        resolved_output = output_root.resolve()
        if Path("/") in {resolved_input, resolved_output}:
            raise ValueError("Docker mount roots cannot be the filesystem root")
        if resolved_input == resolved_output:
            raise ValueError("Docker input and output roots must differ")
        if resolved_input in resolved_output.parents or resolved_output in resolved_input.parents:
            raise ValueError("Docker input and output roots cannot contain one another")
        return self


class DockerNoEgressAttestation(_StrictFrozenModel):
    schema_version: Literal["docker-no-egress-attestation/1.0.0"] = "docker-no-egress-attestation/1.0.0"
    artifact_type: Literal["docker_no_egress_conformance_attestation"] = "docker_no_egress_conformance_attestation"
    authority_status: Literal["independent_review_pending"] = "independent_review_pending"
    formal_authority: Literal[False] = False
    invocation_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    policy_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    image_digest: StrictStr = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    container_id: StrictStr = Field(pattern=r"^[0-9A-Za-z_.-]+$")
    inspect_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    network_mode: Literal["none"]
    read_only_root: Literal[True]
    cap_drop_all: Literal[True]
    no_new_privileges: Literal[True]
    dns_probe: Literal["denied"]
    literal_ip_socket_probe: Literal["denied"]
    http_probe: Literal["denied"]
    probe_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)


class NoEgressExecutionEvidenceBinding(_StrictFrozenModel):
    schema_version: Literal["no-egress-execution-evidence-binding/1.0.0"] = "no-egress-execution-evidence-binding/1.0.0"
    artifact_type: Literal["no_egress_execution_evidence_binding"] = "no_egress_execution_evidence_binding"
    authority_status: Literal["independent_review_pending"] = "independent_review_pending"
    formal_authority: Literal[False] = False
    formal_manifest_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    run_id: StrictStr = Field(pattern=_DIGEST_PATTERN)
    terminal_package_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    conformance_attestation_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    invocation_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)
    image_digest: StrictStr = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    policy_sha256: StrictStr = Field(pattern=_DIGEST_PATTERN)


@dataclass(frozen=True)
class DockerCommandResult:
    returncode: int
    stdout: str
    stderr: str


DockerCommandRunner = Callable[[Tuple[str, ...]], DockerCommandResult]


def _canonical_bytes(payload: Mapping[str, object]) -> bytes:
    return (
        json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def docker_no_egress_policy_sha256(policy: DockerNoEgressPolicy) -> str:
    return hashlib.sha256(_canonical_bytes(policy.model_dump(mode="json"))).hexdigest()


def canonical_docker_attestation_bytes(attestation: DockerNoEgressAttestation) -> bytes:
    return _canonical_bytes(attestation.model_dump(mode="json"))


def bind_no_egress_execution_evidence(
    attestation: DockerNoEgressAttestation,
    *,
    formal_manifest_sha256: str,
    run_id: str,
    terminal_package_sha256: str,
) -> NoEgressExecutionEvidenceBinding:
    """Bind genuine conformance evidence to one exact terminal package."""

    return NoEgressExecutionEvidenceBinding(
        formal_manifest_sha256=formal_manifest_sha256,
        run_id=run_id,
        terminal_package_sha256=terminal_package_sha256,
        conformance_attestation_sha256=hashlib.sha256(
            canonical_docker_attestation_bytes(attestation)
        ).hexdigest(),
        invocation_sha256=attestation.invocation_sha256,
        image_digest=attestation.image_digest,
        policy_sha256=attestation.policy_sha256,
    )


def canonical_no_egress_execution_binding_bytes(
    binding: NoEgressExecutionEvidenceBinding,
) -> bytes:
    return _canonical_bytes(binding.model_dump(mode="json"))


def build_create_command(policy: DockerNoEgressPolicy) -> Tuple[str, ...]:
    name = f"learnloop-benchmark-{policy.invocation_sha256[:16]}"
    return (
        "docker",
        "create",
        "--name",
        name,
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges:true",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,nodev,size=16m",
        "--mount",
        f"type=bind,src={Path(policy.input_root).resolve()},dst=/benchmark-input,readonly",
        "--mount",
        f"type=bind,src={Path(policy.output_root).resolve()},dst=/benchmark-output",
        policy.image,
        "python",
        "-m",
        "tests.evals.parser_note_completeness.no_egress_probe",
    )


def _subprocess_runner(command: Tuple[str, ...]) -> DockerCommandResult:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return DockerCommandResult(completed.returncode, completed.stdout, completed.stderr)


def _require_success(result: DockerCommandResult, operation: str) -> str:
    if result.returncode != 0:
        raise RuntimeError(f"Docker {operation} failed")
    return result.stdout.strip()


def execute_no_egress_probe(
    policy: DockerNoEgressPolicy,
    *,
    command_runner: Optional[DockerCommandRunner] = None,
) -> DockerNoEgressAttestation:
    """Run one bounded conformance probe and return pending-review evidence."""

    run = command_runner or _subprocess_runner
    container_id = _require_success(run(build_create_command(policy)), "create")
    if re.fullmatch(r"[0-9A-Za-z_.-]+", container_id) is None:
        raise RuntimeError("Docker returned an invalid container identity")

    inspect_payload: dict[str, object]
    probe_payload: dict[str, object]
    try:
        inspect_text = _require_success(
            run(("docker", "inspect", "--format", "{{json .HostConfig}}", container_id)),
            "inspect",
        )
        try:
            loaded_inspect = json.loads(inspect_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Docker inspect output is invalid") from exc
        if not isinstance(loaded_inspect, dict):
            raise RuntimeError("Docker inspect output is invalid")
        inspect_payload = loaded_inspect
        if inspect_payload.get("NetworkMode") != "none":
            raise RuntimeError("Docker boundary does not enforce network none")
        if inspect_payload.get("ReadonlyRootfs") is not True:
            raise RuntimeError("Docker boundary does not enforce a read-only root")
        if "ALL" not in (inspect_payload.get("CapDrop") or []):
            raise RuntimeError("Docker boundary does not drop all capabilities")
        if "no-new-privileges:true" not in (inspect_payload.get("SecurityOpt") or []):
            raise RuntimeError("Docker boundary does not enforce no-new-privileges")

        probe_text = _require_success(run(("docker", "start", "--attach", container_id)), "probe")
        try:
            loaded_probe = json.loads(probe_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("no-egress probe output is invalid") from exc
        if not isinstance(loaded_probe, dict):
            raise RuntimeError("no-egress probe output is invalid")
        probe_payload = loaded_probe
        expected = {
            "schema_version": "no-egress-probe/1.0.0",
            "dns": "denied",
            "literal_ip_socket": "denied",
            "http": "denied",
        }
        if probe_payload != expected:
            raise RuntimeError("not every bounded no-egress probe was denied")
    finally:
        cleanup = run(("docker", "rm", "--force", container_id))
        if cleanup.returncode != 0:
            raise RuntimeError("Docker probe container cleanup failed")

    image_digest = policy.image.rsplit("@", 1)[1]
    return DockerNoEgressAttestation(
        invocation_sha256=policy.invocation_sha256,
        policy_sha256=docker_no_egress_policy_sha256(policy),
        image_digest=image_digest,
        container_id=container_id,
        inspect_sha256=hashlib.sha256(_canonical_bytes(inspect_payload)).hexdigest(),
        network_mode="none",
        read_only_root=True,
        cap_drop_all=True,
        no_new_privileges=True,
        dns_probe="denied",
        literal_ip_socket_probe="denied",
        http_probe="denied",
        probe_sha256=hashlib.sha256(_canonical_bytes(probe_payload)).hexdigest(),
    )
