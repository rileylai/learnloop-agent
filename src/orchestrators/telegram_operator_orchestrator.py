from __future__ import annotations

import shlex
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Optional

from src.observability.redaction import sanitize_sensitive_text
from src.services import (
    COST_SCOPE_7D,
    COST_SCOPE_MONTH,
    COST_SCOPE_TODAY,
    COST_SCOPE_WORKFLOW,
    CostScopeSnapshot,
    WorkflowObservabilityService,
)
from src.services.workflow_observability import WorkflowStatusView


@dataclass(frozen=True)
class TelegramCostResult:
    status: str
    reply_text: str
    scope: str
    workflow_run_id: Optional[int]
    total_cost_usd: float
    llm_cost_usd: float
    embedding_cost_usd: float
    unknown_cost_workflow_count: int
    budget_status: str
    budget_usd: Optional[float]
    workflow_budget_exceeded_count: int
    workflow_budget_usd: Optional[float]


@dataclass(frozen=True)
class TelegramWorkflowResult:
    status: str
    reply_text: str
    workflow_run_id: Optional[int]
    workflow_type: Optional[str]
    workflow_status: Optional[str]
    failure_reason: Optional[str]
    age_seconds: Optional[float]
    stale: Optional[bool]
    estimated_cost_usd: Optional[float]
    recent_workflow_count: int


class TelegramOperatorError(Exception):
    def __init__(
        self,
        *,
        error_code: str,
        message: str,
        http_status_code: int,
        failure_reason: str = "UNKNOWN_ERROR",
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.http_status_code = http_status_code
        self.failure_reason = failure_reason


class TelegramOperatorOrchestrator:
    """Expose bounded, read-only Telegram cost and workflow views."""

    _RECENT_WORKFLOW_LIMIT = 5
    _SAFE_METADATA_KEYS = (
        "operation",
        "sync_mode",
        "discovered_page_count",
        "processed_page_count",
        "failed_page_count",
        "remaining_page_count",
        "indexed_block_count",
        "indexed_chunk_count",
        "retrieved_chunk_count",
        "citation_count",
        "change_request_status",
        "business_status",
    )

    def __init__(
        self,
        *,
        workflow_observability_service: WorkflowObservabilityService,
    ) -> None:
        self._workflow_observability_service = workflow_observability_service

    def get_cost(self, *, command_text: str) -> TelegramCostResult:
        scope, workflow_run_id = self._parse_cost_command(command_text)
        summary = self._workflow_observability_service.cost_summary(
            scope=scope,
            workflow_run_id=workflow_run_id,
            limit=10000,
        )
        if summary is None:
            raise TelegramOperatorError(
                error_code="WORKFLOW_NOT_FOUND",
                message="The requested workflow cost was not found.",
                http_status_code=HTTPStatus.NOT_FOUND,
                failure_reason="UNKNOWN_ERROR",
            )
        return self._cost_result(summary)

    def get_workflow(self, *, command_text: str) -> TelegramWorkflowResult:
        workflow_run_id = self._parse_workflow_command(command_text)
        if workflow_run_id is None:
            workflows = self._workflow_observability_service.list_workflows(
                limit=self._RECENT_WORKFLOW_LIMIT
            )
            return TelegramWorkflowResult(
                status="succeeded",
                reply_text=self._recent_workflow_reply(workflows),
                workflow_run_id=None,
                workflow_type=None,
                workflow_status=None,
                failure_reason=None,
                age_seconds=None,
                stale=None,
                estimated_cost_usd=None,
                recent_workflow_count=len(workflows),
            )

        workflow = self._workflow_observability_service.get_workflow(workflow_run_id)
        if workflow is None:
            raise TelegramOperatorError(
                error_code="WORKFLOW_NOT_FOUND",
                message="The requested workflow was not found.",
                http_status_code=HTTPStatus.NOT_FOUND,
                failure_reason="UNKNOWN_ERROR",
            )
        return TelegramWorkflowResult(
            status=workflow.status,
            reply_text=self._workflow_detail_reply(workflow),
            workflow_run_id=workflow.workflow_run_id,
            workflow_type=self._safe_label(workflow.workflow_type),
            workflow_status=self._safe_label(workflow.status),
            failure_reason=self._safe_failure_reason(workflow.failure_reason),
            age_seconds=workflow.age_seconds,
            stale=workflow.stale,
            estimated_cost_usd=workflow.estimated_cost_usd,
            recent_workflow_count=1,
        )

    @classmethod
    def _parse_cost_command(cls, command_text: str) -> tuple[str, Optional[int]]:
        tokens = cls._parse_tokens(command_text, usage="/cost [today|7d|month|workflow <workflow_id>]")
        if len(tokens) == 1:
            return COST_SCOPE_TODAY, None
        if len(tokens) == 2 and tokens[1] in {
            COST_SCOPE_TODAY,
            COST_SCOPE_7D,
            COST_SCOPE_MONTH,
        }:
            return tokens[1], None
        if len(tokens) == 3 and tokens[1] == COST_SCOPE_WORKFLOW:
            return COST_SCOPE_WORKFLOW, cls._parse_workflow_id(tokens[2])
        raise TelegramOperatorError(
            error_code="INVALID_ARGUMENT",
            message="Usage: /cost [today|7d|month|workflow <workflow_id>]",
            http_status_code=HTTPStatus.BAD_REQUEST,
            failure_reason="UNKNOWN_ERROR",
        )

    @classmethod
    def _parse_workflow_command(cls, command_text: str) -> Optional[int]:
        tokens = cls._parse_tokens(command_text, usage="/workflow [workflow_id]")
        if len(tokens) == 1:
            return None
        if len(tokens) == 2:
            return cls._parse_workflow_id(tokens[1])
        raise TelegramOperatorError(
            error_code="INVALID_ARGUMENT",
            message="Usage: /workflow [workflow_id]",
            http_status_code=HTTPStatus.BAD_REQUEST,
            failure_reason="UNKNOWN_ERROR",
        )

    @staticmethod
    def _parse_tokens(command_text: str, *, usage: str) -> list[str]:
        try:
            tokens = shlex.split(command_text)
        except ValueError as exc:
            raise TelegramOperatorError(
                error_code="INVALID_ARGUMENT",
                message=f"Usage: {usage}",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            ) from exc
        if not tokens or tokens[0].lstrip("/").lower() != usage.split()[0].lstrip("/"):
            raise TelegramOperatorError(
                error_code="INVALID_ARGUMENT",
                message=f"Usage: {usage}",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            )
        return tokens

    @staticmethod
    def _parse_workflow_id(value: str) -> int:
        try:
            workflow_run_id = int(value)
        except (TypeError, ValueError) as exc:
            raise TelegramOperatorError(
                error_code="INVALID_ARGUMENT",
                message="workflow_id must be a positive integer",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            ) from exc
        if workflow_run_id <= 0:
            raise TelegramOperatorError(
                error_code="INVALID_ARGUMENT",
                message="workflow_id must be a positive integer",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            )
        return workflow_run_id

    @classmethod
    def _cost_result(cls, summary: CostScopeSnapshot) -> TelegramCostResult:
        return TelegramCostResult(
            status=summary.budget_status,
            reply_text=cls._cost_reply(summary),
            scope=summary.scope,
            workflow_run_id=summary.workflow_run_id,
            total_cost_usd=summary.total_cost_usd,
            llm_cost_usd=summary.llm_cost_usd,
            embedding_cost_usd=summary.embedding_cost_usd,
            unknown_cost_workflow_count=summary.unknown_cost_workflow_count,
            budget_status=summary.budget_status,
            budget_usd=summary.budget_usd,
            workflow_budget_exceeded_count=summary.workflow_budget_exceeded_count,
            workflow_budget_usd=summary.workflow_budget_usd,
        )

    @classmethod
    def _cost_reply(cls, summary: CostScopeSnapshot) -> str:
        scope_label = summary.scope
        if summary.scope == COST_SCOPE_WORKFLOW:
            scope_label = f"workflow #{summary.workflow_run_id}"
        lines = [
            f"Cost scope: {scope_label}",
            f"Workflows: {summary.workflow_count}",
            f"Recorded cost (known): {cls._format_cost(summary.total_cost_usd)}",
            f"LLM cost (proposal/QA): {cls._format_cost(summary.llm_cost_usd)}",
            f"Embedding cost (indexing): {cls._format_cost(summary.embedding_cost_usd)}",
            f"Unknown-cost workflows: {summary.unknown_cost_workflow_count}",
        ]
        if summary.unknown_cost_workflow_count:
            lines.append(
                "Pricing: unknown for "
                f"{summary.unknown_cost_workflow_count} workflow(s)"
            )
        if summary.budget_usd is None:
            lines.append(f"Budget status: {summary.budget_status}")
        else:
            lines.append(
                f"Budget: {cls._format_cost(summary.budget_usd)} "
                f"(status: {summary.budget_status})"
            )
        lines.append(
            f"Workflow-budget exceeded: {summary.workflow_budget_exceeded_count}"
        )
        return "\n".join(lines)

    @classmethod
    def _recent_workflow_reply(cls, workflows: list[WorkflowStatusView]) -> str:
        if not workflows:
            return "No workflow runs found."
        lines = ["Recent workflows:"]
        for workflow in workflows:
            lines.append(
                f"#{workflow.workflow_run_id} {cls._safe_label(workflow.workflow_type)} "
                f"— {cls._safe_label(workflow.status)} "
                f"— stale: {'yes' if workflow.stale else 'no'}"
            )
        return "\n".join(lines)

    @classmethod
    def _workflow_detail_reply(cls, workflow: WorkflowStatusView) -> str:
        lines = [
            f"Workflow #{workflow.workflow_run_id}",
            f"Type: {cls._safe_label(workflow.workflow_type)}",
            f"Status: {cls._safe_label(workflow.status)}",
            f"Age: {workflow.age_seconds:.3f}s",
            f"Stale: {'yes' if workflow.stale else 'no'}",
            f"Recorded cost: {cls._format_optional_cost(workflow.estimated_cost_usd)}",
        ]
        failure_reason = cls._safe_failure_reason(workflow.failure_reason)
        if failure_reason:
            lines.append(f"Failure reason: {failure_reason}")
        for key in cls._SAFE_METADATA_KEYS:
            value = workflow.metadata.get(key)
            if value is None:
                continue
            if isinstance(value, bool):
                display = "yes" if value else "no"
            elif isinstance(value, int) and not isinstance(value, bool):
                display = str(max(0, value))
            elif isinstance(value, str):
                display = cls._safe_label(value)
            else:
                continue
            lines.append(f"{key}: {display}")
        return "\n".join(lines)

    @staticmethod
    def _safe_label(value: object) -> str:
        normalized = sanitize_sensitive_text(str(value)).strip()
        return normalized[:80] or "unknown"

    @classmethod
    def _safe_failure_reason(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        normalized = cls._safe_label(value).upper()
        return normalized if all(char.isalnum() or char == "_" for char in normalized) else "UNKNOWN_ERROR"

    @staticmethod
    def _format_cost(value: float) -> str:
        return f"${value:.6f}"

    @staticmethod
    def _format_optional_cost(value: Optional[float]) -> str:
        return TelegramOperatorOrchestrator._format_cost(value) if value is not None else "unknown"
