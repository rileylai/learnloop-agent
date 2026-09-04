from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from .docker_no_egress import (
    DockerCommandResult,
    DockerNoEgressPolicy,
    bind_no_egress_execution_evidence,
    build_create_command,
    canonical_docker_attestation_bytes,
    canonical_no_egress_execution_binding_bytes,
    execute_no_egress_probe,
)


DIGEST = "a" * 64


def _policy(tmp_path: Path) -> DockerNoEgressPolicy:
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    return DockerNoEgressPolicy(
        image=f"learnloop-benchmark@sha256:{DIGEST}",
        input_root=str(input_root),
        output_root=str(output_root),
        invocation_sha256="b" * 64,
    )


def test_create_command_uses_only_required_native_docker_isolation(tmp_path) -> None:
    command = build_create_command(_policy(tmp_path))

    assert command[:2] == ("docker", "create")
    assert ("--network", "none") == command[command.index("--network") : command.index("--network") + 2]
    assert "--read-only" in command
    assert ("--cap-drop", "ALL") == command[command.index("--cap-drop") : command.index("--cap-drop") + 2]
    assert "no-new-privileges:true" in command
    assert all("docker.sock" not in field for field in command)
    assert all(".env" not in field for field in command)
    assert command[-3:] == (
        "python",
        "-m",
        "tests.evals.parser_note_completeness.no_egress_probe",
    )


def test_policy_rejects_broad_or_overlapping_mount_roots(tmp_path) -> None:
    output_root = tmp_path / "output"
    output_root.mkdir()
    with pytest.raises(ValueError, match="filesystem root"):
        DockerNoEgressPolicy(
            image=f"learnloop-benchmark@sha256:{DIGEST}",
            input_root="/",
            output_root=str(output_root),
            invocation_sha256="b" * 64,
        )

    nested = output_root / "nested"
    nested.mkdir()
    with pytest.raises(ValueError, match="contain"):
        DockerNoEgressPolicy(
            image=f"learnloop-benchmark@sha256:{DIGEST}",
            input_root=str(output_root),
            output_root=str(nested),
            invocation_sha256="b" * 64,
        )


def test_launcher_inspects_boundary_and_requires_all_three_denied_probes(tmp_path) -> None:
    calls: list[tuple[str, ...]] = []
    probe = {
        "schema_version": "no-egress-probe/1.0.0",
        "dns": "denied",
        "literal_ip_socket": "denied",
        "http": "denied",
    }

    def run(command: tuple[str, ...]) -> DockerCommandResult:
        calls.append(command)
        if command[1] == "create":
            return DockerCommandResult(0, "container-123\n", "")
        if command[1] == "inspect":
            return DockerCommandResult(
                0,
                json.dumps(
                    {
                        "NetworkMode": "none",
                        "ReadonlyRootfs": True,
                        "CapDrop": ["ALL"],
                        "SecurityOpt": ["no-new-privileges:true"],
                    }
                ),
                "",
            )
        if command[1] == "start":
            return DockerCommandResult(0, json.dumps(probe) + "\n", "")
        if command[1] == "rm":
            return DockerCommandResult(0, "container-123\n", "")
        raise AssertionError(command)

    attestation = execute_no_egress_probe(_policy(tmp_path), command_runner=run)

    assert attestation.network_mode == "none"
    assert attestation.dns_probe == "denied"
    assert attestation.literal_ip_socket_probe == "denied"
    assert attestation.http_probe == "denied"
    assert [command[1] for command in calls] == ["create", "inspect", "start", "rm"]

    binding = bind_no_egress_execution_evidence(
        attestation,
        formal_manifest_sha256="c" * 64,
        run_id="d" * 64,
        terminal_package_sha256="e" * 64,
    )
    assert binding.conformance_attestation_sha256 == hashlib.sha256(
        canonical_docker_attestation_bytes(attestation)
    ).hexdigest()
    assert binding.terminal_package_sha256 == "e" * 64
    assert binding.authority_status == "independent_review_pending"
    assert binding.formal_authority is False
    assert b'"terminal_package_sha256"' in canonical_no_egress_execution_binding_bytes(binding)


def test_launcher_fails_closed_when_docker_inspect_is_not_network_none(tmp_path) -> None:
    def run(command: tuple[str, ...]) -> DockerCommandResult:
        if command[1] == "create":
            return DockerCommandResult(0, "container-123\n", "")
        if command[1] == "inspect":
            return DockerCommandResult(
                0,
                json.dumps(
                    {
                        "NetworkMode": "bridge",
                        "ReadonlyRootfs": True,
                        "CapDrop": ["ALL"],
                        "SecurityOpt": ["no-new-privileges:true"],
                    }
                ),
                "",
            )
        if command[1] == "rm":
            return DockerCommandResult(0, "container-123\n", "")
        raise AssertionError(command)

    with pytest.raises(RuntimeError, match="network none"):
        execute_no_egress_probe(_policy(tmp_path), command_runner=run)
