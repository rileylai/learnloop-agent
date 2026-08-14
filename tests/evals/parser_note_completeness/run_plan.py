"""Strict C2 run-plan, receipt, collection, and offline contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import PurePosixPath
from typing import Annotated, Any, Literal, Mapping, Optional, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, model_validator

RUNNER_VERSION = "parser-note-completeness-runner/1.0.0"
RUN_PLAN_SCHEMA_VERSION = "run-plan/1.0.0"
ATTESTATION_SCHEMA_VERSION = "network-denial-attestation/1.0.0"
START_RECEIPT_SCHEMA_VERSION = "runner-start-receipt/1.0.0"
TERMINAL_RECEIPT_SCHEMA_VERSION = "runner-terminal-receipt/1.0.0"
COLLECTION_SCHEMA_VERSION = "collection-revision/1.0.0"

_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
Digest = Annotated[StrictStr, Field(pattern=_DIGEST_PATTERN)]
Identifier = Annotated[StrictStr, Field(pattern=_ID_PATTERN)]
PositiveOrdinal = Annotated[StrictInt, Field(ge=1)]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class RunSlot(_StrictFrozenModel):
    slot_id: Identifier
    case_id: StrictStr = Field(min_length=1)
    operation: Literal["validate_reference"]
    reference_path: StrictStr = Field(min_length=1)
    digest_path: StrictStr = Field(min_length=1)
    reference_sha256: Digest
    membership: Literal["diagnostic"]

    @model_validator(mode="after")
    def _validate_relative_paths(self) -> "RunSlot":
        for field_name in ("reference_path", "digest_path"):
            value = getattr(self, field_name)
            if (
                value.startswith("/")
                or "\\" in value
                or (len(value) >= 2 and value[1] == ":")
                or PurePosixPath(value).is_absolute()
                or any(part in {"", ".", ".."} for part in value.split("/"))
                or PurePosixPath(value).as_posix() != value
            ):
                raise ValueError(f"{field_name} must be a normalized relative POSIX path")
        return self


class RunPlan(_StrictFrozenModel):
    schema_version: Literal[RUN_PLAN_SCHEMA_VERSION]
    runner_version: Literal[RUNNER_VERSION]
    artifact_type: Literal["parser_note_completeness_run_plan"]
    plan_id: Identifier
    plan_revision: Identifier
    execution_mode: Literal["development"]
    slots: Tuple[RunSlot, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_ordered_unique_slots(self) -> "RunPlan":
        slot_ids = tuple(slot.slot_id for slot in self.slots)
        if len(slot_ids) != len(set(slot_ids)):
            raise ValueError("run-plan slot IDs must be unique")
        return self


class NetworkDenialAttestation(_StrictFrozenModel):
    schema_version: Literal[ATTESTATION_SCHEMA_VERSION]
    runner_version: Literal[RUNNER_VERSION]
    artifact_type: Literal["network_denial_attestation"]
    plan_sha256: Digest
    invocation_id: Identifier
    invocation_sha256: Digest
    outer_boundary_mechanism: Literal["os_container_no_egress"]
    network_denial: Literal["enforced"]
    failed_socket_probe: Literal["failed"]
    socket_probe_target: StrictStr = Field(min_length=1)


class StartReceipt(_StrictFrozenModel):
    schema_version: Literal[START_RECEIPT_SCHEMA_VERSION]
    runner_version: Literal[RUNNER_VERSION]
    artifact_type: Literal["runner_start_receipt"]
    operation: Literal["validate_reference"]
    plan_sha256: Digest
    invocation_id: Identifier
    reference_sha256: Digest
    invocation_sha256: Digest
    slot_id: Identifier
    case_id: StrictStr = Field(min_length=1)
    attempt_ordinal: PositiveOrdinal
    membership: Literal["diagnostic"]
    offline_attestation: Literal["attested", "missing"]
    status: Literal["started"]


class TerminalReceipt(_StrictFrozenModel):
    schema_version: Literal[TERMINAL_RECEIPT_SCHEMA_VERSION]
    runner_version: Literal[RUNNER_VERSION]
    artifact_type: Literal["runner_terminal_receipt"]
    operation: Literal["validate_reference"]
    plan_sha256: Digest
    invocation_id: Identifier
    reference_sha256: Digest
    invocation_sha256: Digest
    slot_id: Identifier
    case_id: StrictStr = Field(min_length=1)
    attempt_ordinal: PositiveOrdinal
    membership: Literal["diagnostic"]
    offline_attestation: Literal["attested", "missing"]
    exit_code: Literal[0, 1, 2]
    terminal_status: Literal[
        "contract_valid",
        "invalid_input",
        "operational_failure",
    ]
    result_sha256: Optional[Digest] = None

    @model_validator(mode="after")
    def _validate_terminal_outcome(self) -> "TerminalReceipt":
        expected = {
            0: ("contract_valid", True),
            1: ("operational_failure", False),
            2: ("invalid_input", False),
        }[self.exit_code]
        if self.terminal_status != expected[0] or (self.result_sha256 is not None) != expected[1]:
            raise ValueError("terminal receipt outcome is inconsistent")
        return self


class CollectionSlot(_StrictFrozenModel):
    slot_id: Identifier
    case_id: StrictStr = Field(min_length=1)
    attempt_ordinals: Tuple[PositiveOrdinal, ...]
    state: Literal["closed", "invalid", "operational", "unclosed", "missing"]

    @model_validator(mode="after")
    def _validate_collection_state(self) -> "CollectionSlot":
        ordinals = tuple(self.attempt_ordinals)
        if self.state == "missing":
            if ordinals:
                raise ValueError("missing collection slot cannot have attempts")
            return self
        if not ordinals or ordinals != tuple(range(1, len(ordinals) + 1)):
            raise ValueError("collection attempt ordinals must be contiguous from one")
        return self


class CollectionRevision(_StrictFrozenModel):
    schema_version: Literal[COLLECTION_SCHEMA_VERSION]
    runner_version: Literal[RUNNER_VERSION]
    artifact_type: Literal["development_collection_revision"]
    operation: Literal["execute_plan"]
    plan_sha256: Digest
    invocation_id: Identifier
    invocation_sha256: Digest
    revision_ordinal: PositiveOrdinal
    membership: Literal["diagnostic"]
    offline_attestation: Literal["attested", "missing"]
    slots: Tuple[CollectionSlot, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_slot_order(self) -> "CollectionRevision":
        slot_ids = tuple(slot.slot_id for slot in self.slots)
        if len(slot_ids) != len(set(slot_ids)):
            raise ValueError("collection slot IDs must be unique")
        return self


RunPlanArtifact = Union[RunPlan]
ReceiptArtifact = Union[StartReceipt, TerminalReceipt]


def _canonical_model_bytes(model: BaseModel) -> bytes:
    return (
        json.dumps(
            model.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_run_plan_bytes(payload: Union[RunPlan, Mapping[str, Any]]) -> bytes:
    model = payload if isinstance(payload, RunPlan) else RunPlan.model_validate(payload)
    return _canonical_model_bytes(model)


def run_plan_sha256(payload: Union[RunPlan, Mapping[str, Any]]) -> str:
    return hashlib.sha256(canonical_run_plan_bytes(payload)).hexdigest()


def canonical_attestation_bytes(
    payload: Union[NetworkDenialAttestation, Mapping[str, Any]],
) -> bytes:
    model = (
        payload
        if isinstance(payload, NetworkDenialAttestation)
        else NetworkDenialAttestation.model_validate(payload)
    )
    return _canonical_model_bytes(model)


def canonical_invocation_bytes(payload: Mapping[str, Any]) -> bytes:
    """Canonicalize the non-secret invocation facts bound by an attestation."""

    if not isinstance(payload, Mapping):
        raise TypeError("invocation must be a mapping")
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


def invocation_sha256(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_invocation_bytes(payload)).hexdigest()


def canonical_receipt_bytes(payload: ReceiptArtifact) -> bytes:
    return _canonical_model_bytes(payload)


def canonical_collection_bytes(
    payload: Union[CollectionRevision, Mapping[str, Any]],
) -> bytes:
    model = (
        payload
        if isinstance(payload, CollectionRevision)
        else CollectionRevision.model_validate(payload)
    )
    return _canonical_model_bytes(model)


def artifact_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
