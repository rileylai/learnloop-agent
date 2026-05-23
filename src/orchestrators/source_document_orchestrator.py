from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from src.repositories import SourceDocumentRepository
from src.services import WorkflowRunService

SUPPORTED_SOURCE_TYPES = {"pdf", "url", "youtube", "screenshot", "chat_text"}


@dataclass
class SourceDocumentCreateResult:
    workflow_run_id: int
    status: str
    source_document_id: int
    source_type: str
    source_display_name: str
    content_hash: str


class SourceDocumentWorkflowError(Exception):
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


class SourceDocumentOrchestrator:
    def __init__(
        self,
        *,
        source_document_repository: SourceDocumentRepository,
        workflow_run_service: WorkflowRunService,
    ) -> None:
        self._source_document_repository = source_document_repository
        self._workflow_run_service = workflow_run_service

    async def create_source_document(
        self,
        *,
        source_type: str,
        source_display_name: str,
        raw_text: str,
        request_workflow_id: str,
    ) -> SourceDocumentCreateResult:
        normalized_source_type = source_type.strip().lower()
        normalized_display_name = source_display_name.strip()
        normalized_raw_text = raw_text.strip()

        if normalized_source_type not in SUPPORTED_SOURCE_TYPES:
            raise SourceDocumentWorkflowError(
                error_code="INVALID_ARGUMENT",
                message=(
                    "source_type must be one of: "
                    "pdf, url, youtube, screenshot, chat_text"
                ),
                http_status_code=HTTPStatus.BAD_REQUEST,
            )
        if not normalized_display_name:
            raise SourceDocumentWorkflowError(
                error_code="INVALID_ARGUMENT",
                message="source_display_name must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )
        if not normalized_raw_text:
            raise SourceDocumentWorkflowError(
                error_code="INVALID_ARGUMENT",
                message="raw_text must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )

        workflow_run = self._workflow_run_service.start_workflow(
            workflow_type="ingestion",
            metadata_json=json.dumps(
                {
                    "operation": "create_source_document",
                    "source_type": normalized_source_type,
                    "source_display_name": normalized_display_name,
                    "raw_text_length": len(normalized_raw_text),
                    "request_workflow_id": request_workflow_id,
                },
                sort_keys=True,
            ),
        )

        try:
            content_hash = self._build_content_hash(normalized_raw_text)
            source_document = self._source_document_repository.create_source_document(
                source_type=normalized_source_type,
                source_display_name=normalized_display_name,
                raw_text=raw_text,
                content_hash=content_hash,
            )
            self._workflow_run_service.mark_workflow_succeeded(
                workflow_run.id,
                metadata_json=json.dumps(
                    {
                        "operation": "create_source_document",
                        "source_document_id": source_document.id,
                        "source_type": normalized_source_type,
                        "content_hash": content_hash,
                    },
                    sort_keys=True,
                ),
            )
        except Exception as exc:
            self._workflow_run_service.mark_workflow_failed(
                workflow_run.id,
                failure_reason="UNKNOWN_ERROR",
                metadata_json=json.dumps(
                    {
                        "operation": "create_source_document",
                        "source_type": normalized_source_type,
                        "error_code": "SOURCE_DOCUMENT_CREATE_FAILED",
                    },
                    sort_keys=True,
                ),
            )
            raise SourceDocumentWorkflowError(
                error_code="SOURCE_DOCUMENT_CREATE_FAILED",
                message=f"Failed to create source document: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc

        return SourceDocumentCreateResult(
            workflow_run_id=workflow_run.id,
            status="succeeded",
            source_document_id=source_document.id,
            source_type=source_document.source_type,
            source_display_name=source_document.source_display_name,
            content_hash=source_document.content_hash,
        )

    def _build_content_hash(self, raw_text: str) -> str:
        return hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
