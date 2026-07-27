from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional, Set, TypeVar

from sqlalchemy.orm import Session

from src.db.models import WorkflowRun
from src.repositories import WorkflowRunRepository

WORKFLOW_STATUS_RUNNING = "running"
WORKFLOW_STATUS_SUCCEEDED = "succeeded"
WORKFLOW_STATUS_FAILED = "failed"

STANDARD_FAILURE_REASONS: Set[str] = {
    "NOTION_AUTH_FAILED",
    "NOTION_PAGE_NOT_FOUND",
    "NOTION_BLOCK_FETCH_FAILED",
    "NOTION_APPEND_NOT_VERIFIED",
    "STALE_PAGE_SNAPSHOT",
    "OCR_FAILED",
    "PDF_PARSE_FAILED",
    "URL_FETCH_FAILED",
    "YOUTUBE_TRANSCRIPT_NOT_FOUND",
    "PROVIDER_NOT_FOUND",
    "LLM_PROVIDER_ERROR",
    "LLM_OUTPUT_INVALID",
    "EMBEDDING_PROVIDER_NOT_CONFIGURED",
    "EMBEDDING_PROVIDER_ERROR",
    "VECTOR_DIMENSION_MISMATCH",
    "VECTOR_QUERY_FAILED",
    "VECTOR_UPSERT_FAILED",
    "CHANGE_REQUEST_NOT_FOUND",
    "WRITE_POLICY_VIOLATION",
    "DUPLICATE_SOURCE",
    "TELEGRAM_NOT_CONFIGURED",
    "TELEGRAM_SEND_FAILED",
    "TELEGRAM_FILE_DOWNLOAD_FAILED",
    "UNKNOWN_ERROR",
}

T = TypeVar("T")
SessionFactory = Callable[[], Session]


class WorkflowRunServiceError(Exception):
    pass


class WorkflowRunValidationError(WorkflowRunServiceError):
    pass


class WorkflowRunNotFoundError(WorkflowRunServiceError):
    pass


class WorkflowRunService:
    def __init__(
        self,
        session_factory: SessionFactory,
        now_provider: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self._session_factory = session_factory
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    def _with_repository(self, operation: Callable[[WorkflowRunRepository], T]) -> T:
        session = self._session_factory()
        try:
            return operation(WorkflowRunRepository(session))
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def start_workflow(
        self,
        *,
        workflow_type: str,
        metadata_json: Optional[str] = None,
    ) -> WorkflowRun:
        normalized_type = workflow_type.strip()
        if not normalized_type:
            raise WorkflowRunValidationError("workflow_type must not be empty")

        return self._with_repository(
            lambda repository: repository.create_workflow_run(
                workflow_type=normalized_type,
                status=WORKFLOW_STATUS_RUNNING,
                metadata_json=metadata_json,
            )
        )

    def mark_workflow_succeeded(
        self,
        workflow_run_id: int,
        *,
        metadata_json: Optional[str] = None,
    ) -> WorkflowRun:
        workflow_run = self._with_repository(
            lambda repository: repository.update_workflow_run(
                workflow_run_id,
                status=WORKFLOW_STATUS_SUCCEEDED,
                failure_reason=None,
                metadata_json=metadata_json,
                finished_at=self._now_provider(),
            )
        )
        if workflow_run is None:
            raise WorkflowRunNotFoundError(
                f"Workflow run is not found: workflow_run_id={workflow_run_id}"
            )
        return workflow_run

    def mark_workflow_failed(
        self,
        workflow_run_id: int,
        *,
        failure_reason: str,
        metadata_json: Optional[str] = None,
    ) -> WorkflowRun:
        normalized_failure_reason = failure_reason.strip().upper()
        if normalized_failure_reason not in STANDARD_FAILURE_REASONS:
            raise WorkflowRunValidationError(
                f"failure_reason is invalid: '{failure_reason}'"
            )

        workflow_run = self._with_repository(
            lambda repository: repository.update_workflow_run(
                workflow_run_id,
                status=WORKFLOW_STATUS_FAILED,
                failure_reason=normalized_failure_reason,
                metadata_json=metadata_json,
                finished_at=self._now_provider(),
            )
        )
        if workflow_run is None:
            raise WorkflowRunNotFoundError(
                f"Workflow run is not found: workflow_run_id={workflow_run_id}"
            )
        return workflow_run
