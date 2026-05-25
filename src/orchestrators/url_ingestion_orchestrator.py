from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Dict, Optional

from src.repositories import SourceDocumentRepository
from src.services import STANDARD_FAILURE_REASONS, WorkflowRunService
from src.tools import ToolContext, ToolRegistry

URL_ARTICLE_PARSER_TOOL_NAME = "url_article_parser"

TOOL_ERROR_TO_HTTP_STATUS: Dict[str, int] = {
    "INVALID_ARGUMENT": HTTPStatus.BAD_REQUEST,
    "URL_FETCH_FAILED": HTTPStatus.UNPROCESSABLE_ENTITY,
}


@dataclass
class URLIngestionResult:
    workflow_run_id: int
    status: str
    source_document_id: int
    source_type: str
    source_display_name: str
    content_hash: str


class URLIngestionError(Exception):
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


class URLIngestionOrchestrator:
    def __init__(
        self,
        *,
        tool_registry: ToolRegistry,
        source_document_repository: SourceDocumentRepository,
        workflow_run_service: WorkflowRunService,
    ) -> None:
        self._tool_registry = tool_registry
        self._source_document_repository = source_document_repository
        self._workflow_run_service = workflow_run_service

    async def ingest_url(
        self,
        *,
        url: str,
        request_workflow_id: str,
    ) -> URLIngestionResult:
        normalized_url = url.strip()
        if not normalized_url:
            raise URLIngestionError(
                error_code="INVALID_ARGUMENT",
                message="url must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )

        workflow_run = self._workflow_run_service.start_workflow(
            workflow_type="ingestion",
            metadata_json=json.dumps(
                {
                    "operation": "ingest_url",
                    "source_type": "url",
                    "source_display_name": normalized_url,
                    "source_url": normalized_url,
                    "request_workflow_id": request_workflow_id,
                },
                sort_keys=True,
            ),
        )

        try:
            parsed = await self._parse_url_article(
                url=normalized_url,
                request_workflow_id=request_workflow_id,
            )
            raw_text = self._extract_raw_text(parsed)
            content_hash = self._build_content_hash(raw_text)
            source_document = self._source_document_repository.create_source_document(
                source_type="url",
                source_display_name=normalized_url,
                raw_text=raw_text,
                content_hash=content_hash,
            )

            self._workflow_run_service.mark_workflow_succeeded(
                workflow_run.id,
                metadata_json=json.dumps(
                    {
                        "operation": "ingest_url",
                        "source_document_id": source_document.id,
                        "source_type": "url",
                        "source_display_name": normalized_url,
                        "source_url": parsed.get("url", normalized_url),
                        "content_hash": content_hash,
                        "char_count": len(raw_text),
                    },
                    sort_keys=True,
                ),
            )
        except URLIngestionError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason=exc.failure_reason,
                error_code=exc.error_code,
            )
            raise URLIngestionError(
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
                error_code="SOURCE_DOCUMENT_CREATE_FAILED",
            )
            raise URLIngestionError(
                error_code="SOURCE_DOCUMENT_CREATE_FAILED",
                message=f"Failed to ingest URL article: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc

        return URLIngestionResult(
            workflow_run_id=workflow_run.id,
            status="succeeded",
            source_document_id=source_document.id,
            source_type=source_document.source_type,
            source_display_name=source_document.source_display_name,
            content_hash=source_document.content_hash,
        )

    async def _parse_url_article(
        self,
        *,
        url: str,
        request_workflow_id: str,
    ) -> Dict[str, Any]:
        tool_result = await self._tool_registry.call_tool(
            URL_ARTICLE_PARSER_TOOL_NAME,
            context=ToolContext(
                workflow_id=request_workflow_id,
                metadata={
                    "operation": "ingest_url",
                    "source_type": "url",
                    "source_url": url,
                },
            ),
            arguments={"url": url},
        )

        if tool_result.is_error:
            error_code = "UNKNOWN_ERROR"
            message = "URL parser failed"
            if tool_result.error is not None:
                error_code = tool_result.error.code
                message = tool_result.error.message
            raise URLIngestionError(
                error_code=error_code,
                message=message,
                http_status_code=TOOL_ERROR_TO_HTTP_STATUS.get(
                    error_code, HTTPStatus.INTERNAL_SERVER_ERROR
                ),
                failure_reason=self._normalize_failure_reason(error_code),
            )

        structured_content = tool_result.structured_content
        if structured_content is None:
            raise URLIngestionError(
                error_code="TOOL_OUTPUT_INVALID",
                message="URL parser structured_content is missing",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
            )
        return structured_content

    def _extract_raw_text(self, parser_output: Dict[str, Any]) -> str:
        raw_text = parser_output.get("raw_text")
        if not isinstance(raw_text, str):
            raise URLIngestionError(
                error_code="TOOL_OUTPUT_INVALID",
                message="URL parser raw_text is invalid",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
            )
        normalized_raw_text = raw_text.strip()
        if not normalized_raw_text:
            raise URLIngestionError(
                error_code="URL_FETCH_FAILED",
                message="No extractable text found in URL article",
                http_status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                failure_reason="URL_FETCH_FAILED",
            )
        return normalized_raw_text

    def _build_content_hash(self, raw_text: str) -> str:
        return hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    def _normalize_failure_reason(self, error_code: str) -> str:
        normalized = error_code.strip().upper()
        if normalized in STANDARD_FAILURE_REASONS:
            return normalized
        return "UNKNOWN_ERROR"

    def _mark_failed_workflow(
        self,
        *,
        workflow_run_id: int,
        failure_reason: str,
        error_code: str,
    ) -> None:
        self._workflow_run_service.mark_workflow_failed(
            workflow_run_id,
            failure_reason=self._normalize_failure_reason(failure_reason),
            metadata_json=json.dumps(
                {
                    "operation": "ingest_url",
                    "source_type": "url",
                    "error_code": error_code,
                },
                sort_keys=True,
            ),
        )
