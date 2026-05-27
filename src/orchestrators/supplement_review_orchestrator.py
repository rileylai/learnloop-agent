from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from src.repositories import ChangeRequestRepository
from src.services import STANDARD_FAILURE_REASONS, WorkflowRunService

CHANGE_REQUEST_STATUS_PENDING = "pending"
CHANGE_REQUEST_STATUS_ACCEPTED = "accepted"
CHANGE_REQUEST_STATUS_REJECTED = "rejected"
REVIEW_ACTION_ACCEPT = "accept"
REVIEW_ACTION_REJECT = "reject"
REVIEW_ACTION_EDIT_LATER = "edit_later"


@dataclass
class SupplementReviewResult:
    workflow_run_id: int
    status: str
    change_request_id: int
    change_request_status: str
    review_action: str
    reviewer: Optional[str]
    reason: Optional[str]


class SupplementReviewError(Exception):
    def __init__(
        self,
        *,
        error_code: str,
        message: str,
        http_status_code: int,
        failure_reason: str = "UNKNOWN_ERROR",
        workflow_run_id: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.http_status_code = http_status_code
        self.failure_reason = failure_reason
        self.workflow_run_id = workflow_run_id


class SupplementReviewOrchestrator:
    def __init__(
        self,
        *,
        change_request_repository: ChangeRequestRepository,
        workflow_run_service: WorkflowRunService,
    ) -> None:
        self._change_request_repository = change_request_repository
        self._workflow_run_service = workflow_run_service

    async def accept_change_request(
        self,
        *,
        change_request_id: int,
        reviewer: Optional[str],
        request_workflow_id: str,
    ) -> SupplementReviewResult:
        return self._execute_review_action(
            change_request_id=change_request_id,
            review_action=REVIEW_ACTION_ACCEPT,
            reviewer=reviewer,
            reason=None,
            request_workflow_id=request_workflow_id,
        )

    async def reject_change_request(
        self,
        *,
        change_request_id: int,
        reviewer: Optional[str],
        reason: str,
        request_workflow_id: str,
    ) -> SupplementReviewResult:
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise SupplementReviewError(
                error_code="INVALID_ARGUMENT",
                message="reason must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )
        return self._execute_review_action(
            change_request_id=change_request_id,
            review_action=REVIEW_ACTION_REJECT,
            reviewer=reviewer,
            reason=normalized_reason,
            request_workflow_id=request_workflow_id,
        )

    async def mark_edit_later(
        self,
        *,
        change_request_id: int,
        reviewer: Optional[str],
        reason: Optional[str],
        request_workflow_id: str,
    ) -> SupplementReviewResult:
        normalized_reason: Optional[str] = None
        if reason is not None:
            candidate = reason.strip()
            if candidate:
                normalized_reason = candidate

        return self._execute_review_action(
            change_request_id=change_request_id,
            review_action=REVIEW_ACTION_EDIT_LATER,
            reviewer=reviewer,
            reason=normalized_reason,
            request_workflow_id=request_workflow_id,
        )

    def _execute_review_action(
        self,
        *,
        change_request_id: int,
        review_action: str,
        reviewer: Optional[str],
        reason: Optional[str],
        request_workflow_id: str,
    ) -> SupplementReviewResult:
        if change_request_id <= 0:
            raise SupplementReviewError(
                error_code="INVALID_ARGUMENT",
                message="change_request_id must be positive",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )

        normalized_reviewer: Optional[str] = None
        if reviewer is not None:
            candidate = reviewer.strip()
            if candidate:
                normalized_reviewer = candidate

        workflow_run = self._workflow_run_service.start_workflow(
            workflow_type="supplement",
            metadata_json=json.dumps(
                {
                    "operation": "review_change_request",
                    "review_action": review_action,
                    "change_request_id": change_request_id,
                    "reviewer": normalized_reviewer,
                    "reason": reason,
                    "request_workflow_id": request_workflow_id,
                },
                sort_keys=True,
            ),
        )

        try:
            change_request = self._change_request_repository.get_change_request_by_id(
                change_request_id
            )
            if change_request is None:
                raise SupplementReviewError(
                    error_code="CHANGE_REQUEST_NOT_FOUND",
                    message=(
                        "Change request is not found: "
                        f"change_request_id={change_request_id}"
                    ),
                    http_status_code=HTTPStatus.NOT_FOUND,
                    failure_reason="CHANGE_REQUEST_NOT_FOUND",
                )

            current_status = change_request.status.strip().lower()
            next_status = self._resolve_next_status(
                review_action=review_action,
                current_status=current_status,
            )

            if next_status != current_status:
                updated = self._change_request_repository.update_change_request_status(
                    change_request_id,
                    status=next_status,
                    failure_reason=None,
                )
                if updated is None:
                    raise SupplementReviewError(
                        error_code="CHANGE_REQUEST_NOT_FOUND",
                        message=(
                            "Change request is not found during update: "
                            f"change_request_id={change_request_id}"
                        ),
                        http_status_code=HTTPStatus.NOT_FOUND,
                        failure_reason="CHANGE_REQUEST_NOT_FOUND",
                    )
                change_request = updated

            self._workflow_run_service.mark_workflow_succeeded(
                workflow_run.id,
                metadata_json=json.dumps(
                    {
                        "operation": "review_change_request",
                        "review_action": review_action,
                        "change_request_id": change_request.id,
                        "change_request_status": change_request.status,
                        "reviewer": normalized_reviewer,
                        "reason": reason,
                    },
                    sort_keys=True,
                ),
            )

            return SupplementReviewResult(
                workflow_run_id=workflow_run.id,
                status="succeeded",
                change_request_id=change_request.id,
                change_request_status=change_request.status,
                review_action=review_action,
                reviewer=normalized_reviewer,
                reason=reason,
            )
        except SupplementReviewError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason=exc.failure_reason,
                error_code=exc.error_code,
                review_action=review_action,
            )
            raise SupplementReviewError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=exc.http_status_code,
                failure_reason=exc.failure_reason,
                workflow_run_id=workflow_run.id,
            ) from exc
        except Exception as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason="UNKNOWN_ERROR",
                error_code="REVIEW_WORKFLOW_FAILED",
                review_action=review_action,
            )
            raise SupplementReviewError(
                error_code="REVIEW_WORKFLOW_FAILED",
                message=f"Failed to review change request: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc

    def _resolve_next_status(self, *, review_action: str, current_status: str) -> str:
        if current_status != CHANGE_REQUEST_STATUS_PENDING:
            raise SupplementReviewError(
                error_code="INVALID_STATE_TRANSITION",
                message=(
                    "Only pending change requests can be reviewed: "
                    f"current_status={current_status}"
                ),
                http_status_code=HTTPStatus.CONFLICT,
            )

        if review_action == REVIEW_ACTION_ACCEPT:
            return CHANGE_REQUEST_STATUS_ACCEPTED
        if review_action == REVIEW_ACTION_REJECT:
            return CHANGE_REQUEST_STATUS_REJECTED
        if review_action == REVIEW_ACTION_EDIT_LATER:
            return CHANGE_REQUEST_STATUS_PENDING
        raise SupplementReviewError(
            error_code="INVALID_ARGUMENT",
            message=f"Unknown review action: {review_action}",
            http_status_code=HTTPStatus.BAD_REQUEST,
        )

    def _normalize_failure_reason(self, failure_reason: str) -> str:
        normalized = failure_reason.strip().upper()
        if normalized in STANDARD_FAILURE_REASONS:
            return normalized
        return "UNKNOWN_ERROR"

    def _mark_failed_workflow(
        self,
        *,
        workflow_run_id: int,
        failure_reason: str,
        error_code: str,
        review_action: str,
    ) -> None:
        self._workflow_run_service.mark_workflow_failed(
            workflow_run_id,
            failure_reason=self._normalize_failure_reason(failure_reason),
            metadata_json=json.dumps(
                {
                    "operation": "review_change_request",
                    "review_action": review_action,
                    "error_code": error_code,
                },
                sort_keys=True,
            ),
        )
