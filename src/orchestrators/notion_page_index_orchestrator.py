from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError

from src.rag import (
    BlockPathNode,
    BlockPathSnapshot,
    ChunkerBlock,
    ChunkerPage,
    build_block_paths,
    chunk_notion_page,
)
from src.repositories import (
    ChunkRepository,
    ChunkRepositoryError,
    NotionBlockRepository,
    NotionBlockSnapshot,
    NotionChunkUpsert,
    NotionPageRepository,
)
from src.services import STANDARD_FAILURE_REASONS, WorkflowRunService
from src.tools import ToolContext, ToolRegistry

NOTION_READER_TOOL_NAME = "notion_reader"
SYNC_MODE_MANUAL = "manual"
SYNC_MODE_AUTO_AFTER_ACCEPT = "auto_after_accept"
ALLOWED_SYNC_MODES = {SYNC_MODE_MANUAL, SYNC_MODE_AUTO_AFTER_ACCEPT}

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


@dataclass
class NotionIndexedPageSnapshot:
    notion_page_db_id: int
    notion_page_id: str
    page_title: str
    notion_path: str
    indexed_block_count: int
    indexed_chunk_count: int


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
    children: List["_ToolBlockPayload"] = Field(default_factory=list)


class NotionPageIndexOrchestrator:
    def __init__(
        self,
        *,
        tool_registry: ToolRegistry,
        notion_page_repository: NotionPageRepository,
        notion_block_repository: NotionBlockRepository,
        workflow_run_service: WorkflowRunService,
        chunk_repository: Optional[ChunkRepository] = None,
    ) -> None:
        self._tool_registry = tool_registry
        self._notion_page_repository = notion_page_repository
        self._notion_block_repository = notion_block_repository
        self._workflow_run_service = workflow_run_service
        self._chunk_repository = chunk_repository

    async def index_page(
        self,
        *,
        page_id: str,
        request_workflow_id: str,
        sync_mode: str = SYNC_MODE_MANUAL,
    ) -> NotionPageIndexResult:
        normalized_page_id = page_id.strip()
        if not normalized_page_id:
            raise NotionPageIndexError(
                error_code="INVALID_ARGUMENT",
                message="page_id must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            )
        normalized_sync_mode = sync_mode.strip().lower()
        if normalized_sync_mode not in ALLOWED_SYNC_MODES:
            raise NotionPageIndexError(
                error_code="INVALID_ARGUMENT",
                message=(
                    "sync_mode must be one of: "
                    f"{', '.join(sorted(ALLOWED_SYNC_MODES))}"
                ),
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            )

        workflow_run = self._workflow_run_service.start_workflow(
            workflow_type="indexing",
            metadata_json=json.dumps(
                {
                    "sync_mode": normalized_sync_mode,
                    "operation": "index_page",
                    "page_id": normalized_page_id,
                    "request_workflow_id": request_workflow_id,
                },
                sort_keys=True,
            ),
        )

        try:
            snapshot = await self.index_page_snapshot(
                page_id=normalized_page_id,
                request_workflow_id=request_workflow_id,
            )
            self._workflow_run_service.mark_workflow_succeeded(
                workflow_run.id,
                metadata_json=json.dumps(
                    {
                        "operation": "index_page",
                        "sync_mode": normalized_sync_mode,
                        "page_id": normalized_page_id,
                        "indexed_block_count": snapshot.indexed_block_count,
                        "indexed_chunk_count": snapshot.indexed_chunk_count,
                    },
                    sort_keys=True,
                ),
            )
        except NotionPageIndexError as exc:
            self._workflow_run_service.mark_workflow_failed(
                workflow_run.id,
                failure_reason=exc.failure_reason,
                metadata_json=json.dumps(
                    {
                        "operation": "index_page",
                        "sync_mode": normalized_sync_mode,
                        "page_id": normalized_page_id,
                        "error_code": exc.error_code,
                    },
                    sort_keys=True,
                ),
            )
            raise NotionPageIndexError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=exc.http_status_code,
                failure_reason=exc.failure_reason,
                workflow_run_id=workflow_run.id,
            ) from exc

        return NotionPageIndexResult(
            workflow_run_id=workflow_run.id,
            status="succeeded",
            notion_page_id=snapshot.notion_page_id,
            page_title=snapshot.page_title,
            notion_path=snapshot.notion_path,
            indexed_block_count=snapshot.indexed_block_count,
        )

    async def index_page_snapshot(
        self,
        *,
        page_id: str,
        request_workflow_id: str,
    ) -> NotionIndexedPageSnapshot:
        normalized_page_id = page_id.strip()
        if not normalized_page_id:
            raise NotionPageIndexError(
                error_code="INVALID_ARGUMENT",
                message="page_id must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            )

        tool_result = await self._tool_registry.call_tool(
            NOTION_READER_TOOL_NAME,
            context=ToolContext(
                workflow_id=request_workflow_id,
                metadata={
                    "operation": "index_page_snapshot",
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
            raise NotionPageIndexError(
                error_code=error_code,
                message=message,
                http_status_code=self._http_status_for_tool_error(error_code),
                failure_reason=self._normalize_failure_reason(error_code),
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
            block_paths = build_block_paths(
                page_path=page_payload.notion_path,
                blocks=[
                    self._to_block_path_node(block_payload)
                    for block_payload in block_payloads
                ],
            )
            inserted_blocks = self._notion_block_repository.replace_page_blocks(
                notion_page_db_id=notion_page.id,
                root_blocks=[
                    self._to_block_snapshot(block_snapshot)
                    for block_snapshot in block_paths
                ],
            )
            indexed_chunk_count = 0
            if self._chunk_repository is not None:
                chunk_upserts = self._build_chunk_upserts(
                    page_payload=page_payload,
                    block_paths=block_paths,
                )
                self._chunk_repository.upsert_chunks(
                    notion_page_db_id=notion_page.id,
                    chunks=chunk_upserts,
                )
                indexed_chunk_count = len(chunk_upserts)
        except NotionPageIndexError:
            raise
        except ChunkRepositoryError as exc:
            raise NotionPageIndexError(
                error_code="VECTOR_UPSERT_FAILED",
                message=f"Failed to upsert notion chunks: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="VECTOR_UPSERT_FAILED",
            ) from exc
        except Exception as exc:
            raise NotionPageIndexError(
                error_code="INDEX_PAGE_PERSIST_FAILED",
                message=f"Failed to persist indexed page: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
            ) from exc

        return NotionIndexedPageSnapshot(
            notion_page_db_id=notion_page.id,
            notion_page_id=notion_page.notion_page_id,
            page_title=notion_page.title,
            notion_path=notion_page.notion_path,
            indexed_block_count=len(inserted_blocks),
            indexed_chunk_count=indexed_chunk_count,
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

    def _build_chunk_upserts(
        self,
        *,
        page_payload: _ToolPagePayload,
        block_paths: List[BlockPathSnapshot],
    ) -> List[NotionChunkUpsert]:
        chunk_drafts = chunk_notion_page(
            ChunkerPage(
                notion_page_id=page_payload.page_id,
                title=page_payload.title,
                notion_path=page_payload.notion_path,
                blocks=[
                    self._to_chunker_block(block_snapshot)
                    for block_snapshot in block_paths
                ],
            )
        )
        return [
            NotionChunkUpsert(
                chunk_index=draft.chunk_index,
                chunk_text=draft.chunk_text,
                notion_path=draft.notion_path,
                notion_block_ids=self._extract_chunk_block_ids(draft.citation_meta),
                source_kind=draft.source_kind,
            )
            for draft in chunk_drafts
        ]

    def _extract_chunk_block_ids(self, citation_meta: Dict[str, Any]) -> List[str]:
        value = citation_meta.get("notion_block_ids")
        if not isinstance(value, list):
            return []
        return [str(block_id).strip() for block_id in value if str(block_id).strip()]

    def _to_block_path_node(self, block: _ToolBlockPayload) -> BlockPathNode:
        return BlockPathNode(
            block_id=block.block_id,
            block_type=block.block_type,
            content_text=block.content_text,
            children=[self._to_block_path_node(child) for child in block.children],
        )

    def _to_block_snapshot(self, block: BlockPathSnapshot) -> NotionBlockSnapshot:
        return NotionBlockSnapshot(
            notion_block_id=block.block_id,
            block_type=block.block_type,
            content_text=block.content_text,
            block_path=block.block_path,
            children=[self._to_block_snapshot(child) for child in block.children],
        )

    def _to_chunker_block(self, block: BlockPathSnapshot) -> ChunkerBlock:
        return ChunkerBlock(
            notion_block_id=block.block_id,
            block_type=block.block_type,
            content_text=block.content_text,
            block_path=block.block_path,
            children=[self._to_chunker_block(child) for child in block.children],
        )
