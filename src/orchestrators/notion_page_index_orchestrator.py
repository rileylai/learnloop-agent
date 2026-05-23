from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError

from src.repositories import (
    NotionBlockRepository,
    NotionBlockSnapshot,
    NotionPageRepository,
)
from src.services import STANDARD_FAILURE_REASONS, WorkflowRunService
from src.tools import ToolContext, ToolRegistry

NOTION_READER_TOOL_NAME = "notion_reader"

TOOL_ERROR_TO_HTTP_STATUS: Dict[str, int] = {
    "INVALID_ARGUMENT": HTTPStatus.BAD_REQUEST,
    "NOTION_PAGE_NOT_FOUND": HTTPStatus.NOT_FOUND,
    "NOTION_BLOCK_FETCH_FAILED": HTTPStatus.BAD_GATEWAY,
}


@dataclass
class NotionPageIndexResult:
    workflow_run_id: int
    status: str
    notion_page_id: str
    page_title: str
    notion_path: str
    indexed_block_count: int


class NotionPageIndexError(Exception):
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


class _ToolPagePayload(BaseModel):
    page_id: str
    title: str
    notion_path: str


class _ToolBlockPayload(BaseModel):
    block_id: str
    block_type: str
    content_text: str = ""
    block_path: str = ""
    children: List["_ToolBlockPayload"] = Field(default_factory=list)


class NotionPageIndexOrchestrator:
    def __init__(
        self,
        *,
        tool_registry: ToolRegistry,
        notion_page_repository: NotionPageRepository,
        notion_block_repository: NotionBlockRepository,
        workflow_run_service: WorkflowRunService,
    ) -> None:
        self._tool_registry = tool_registry
        self._notion_page_repository = notion_page_repository
        self._notion_block_repository = notion_block_repository
        self._workflow_run_service = workflow_run_service

    async def index_page(
        self,
        *,
        page_id: str,
        request_workflow_id: str,
    ) -> NotionPageIndexResult:
        normalized_page_id = page_id.strip()
        if not normalized_page_id:
            raise NotionPageIndexError(
                error_code="INVALID_ARGUMENT",
                message="page_id must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            )

        workflow_run = self._workflow_run_service.start_workflow(
            workflow_type="indexing",
            metadata_json=json.dumps(
                {
                    "sync_mode": "manual",
                    "operation": "index_page",
                    "page_id": normalized_page_id,
                    "request_workflow_id": request_workflow_id,
                },
                sort_keys=True,
            ),
        )

        tool_result = await self._tool_registry.call_tool(
            NOTION_READER_TOOL_NAME,
            context=ToolContext(
                workflow_id=request_workflow_id,
                metadata={
                    "operation": "index_page",
                    "page_id": normalized_page_id,
                },
            ),
            arguments={"page_id": normalized_page_id},
        )

        if tool_result.is_error:
            error_code = "UNKNOWN_ERROR"
            message = "Notion reader failed"
            if tool_result.error is not None:
                error_code = tool_result.error.code
                message = tool_result.error.message

            failure_reason = self._normalize_failure_reason(error_code)
            self._workflow_run_service.mark_workflow_failed(
                workflow_run.id,
                failure_reason=failure_reason,
                metadata_json=json.dumps(
                    {
                        "operation": "index_page",
                        "page_id": normalized_page_id,
                        "tool_error_code": error_code,
                    },
                    sort_keys=True,
                ),
            )
            raise NotionPageIndexError(
                error_code=error_code,
                message=message,
                http_status_code=self._http_status_for_tool_error(error_code),
                failure_reason=failure_reason,
                workflow_run_id=workflow_run.id,
            )

        try:
            page_payload, block_payloads = self._parse_tool_payload(
                tool_result.structured_content
            )
            notion_page = self._notion_page_repository.upsert_page_snapshot(
                notion_page_id=page_payload.page_id,
                title=page_payload.title,
                notion_path=page_payload.notion_path,
            )
            inserted_blocks = self._notion_block_repository.replace_page_blocks(
                notion_page_db_id=notion_page.id,
                root_blocks=[self._to_block_snapshot(block) for block in block_payloads],
            )
            self._workflow_run_service.mark_workflow_succeeded(
                workflow_run.id,
                metadata_json=json.dumps(
                    {
                        "operation": "index_page",
                        "page_id": normalized_page_id,
                        "indexed_block_count": len(inserted_blocks),
                    },
                    sort_keys=True,
                ),
            )
        except NotionPageIndexError:
            self._workflow_run_service.mark_workflow_failed(
                workflow_run.id,
                failure_reason="UNKNOWN_ERROR",
                metadata_json=json.dumps(
                    {
                        "operation": "index_page",
                        "page_id": normalized_page_id,
                        "error_code": "TOOL_OUTPUT_INVALID",
                    },
                    sort_keys=True,
                ),
            )
            raise
        except Exception as exc:
            self._workflow_run_service.mark_workflow_failed(
                workflow_run.id,
                failure_reason="UNKNOWN_ERROR",
                metadata_json=json.dumps(
                    {
                        "operation": "index_page",
                        "page_id": normalized_page_id,
                        "error_code": "INDEX_PAGE_PERSIST_FAILED",
                    },
                    sort_keys=True,
                ),
            )
            raise NotionPageIndexError(
                error_code="INDEX_PAGE_PERSIST_FAILED",
                message=f"Failed to persist indexed page: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc

        return NotionPageIndexResult(
            workflow_run_id=workflow_run.id,
            status="succeeded",
            notion_page_id=notion_page.notion_page_id,
            page_title=notion_page.title,
            notion_path=notion_page.notion_path,
            indexed_block_count=len(inserted_blocks),
        )

    def _http_status_for_tool_error(self, error_code: str) -> int:
        return TOOL_ERROR_TO_HTTP_STATUS.get(
            error_code, HTTPStatus.INTERNAL_SERVER_ERROR
        )

    def _normalize_failure_reason(self, error_code: str) -> str:
        normalized = error_code.strip().upper()
        if normalized in STANDARD_FAILURE_REASONS:
            return normalized
        return "UNKNOWN_ERROR"

    def _parse_tool_payload(
        self,
        structured_content: Optional[Dict[str, Any]],
    ) -> Tuple[_ToolPagePayload, List[_ToolBlockPayload]]:
        if structured_content is None:
            raise NotionPageIndexError(
                error_code="TOOL_OUTPUT_INVALID",
                message="Tool output structured_content is missing",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
            )

        try:
            page_payload = _ToolPagePayload(**structured_content["page"])
            block_payloads = [
                _ToolBlockPayload(**block) for block in structured_content["blocks"]
            ]
            return page_payload, block_payloads
        except (KeyError, TypeError, ValidationError) as exc:
            raise NotionPageIndexError(
                error_code="TOOL_OUTPUT_INVALID",
                message=f"Tool output schema is invalid: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
            ) from exc

    def _to_block_snapshot(self, block: _ToolBlockPayload) -> NotionBlockSnapshot:
        return NotionBlockSnapshot(
            notion_block_id=block.block_id,
            block_type=block.block_type,
            content_text=block.content_text,
            block_path=block.block_path,
            children=[self._to_block_snapshot(child) for child in block.children],
        )
