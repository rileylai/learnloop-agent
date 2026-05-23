from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

from src.orchestrators.notion_page_index_orchestrator import (
    NotionPageIndexError,
    NotionPageIndexOrchestrator,
)
from src.services import WorkflowRunService


@dataclass
class NotionIncrementalIndexedPageResult:
    page_id: str
    page_title: str
    notion_path: str
    indexed_block_count: int


@dataclass
class NotionIncrementalIndexResult:
    workflow_run_id: int
    status: str
    sync_mode: str
    processed_page_count: int
    indexed_pages: List[NotionIncrementalIndexedPageResult]


class NotionIncrementalIndexOrchestrator:
    def __init__(
        self,
        *,
        page_index_orchestrator: NotionPageIndexOrchestrator,
        workflow_run_service: WorkflowRunService,
    ) -> None:
        self._page_index_orchestrator = page_index_orchestrator
        self._workflow_run_service = workflow_run_service

    async def sync_pages(
        self,
        *,
        page_ids: List[str],
        request_workflow_id: str,
    ) -> NotionIncrementalIndexResult:
        normalized_page_ids = self._normalize_page_ids(page_ids)
        if not normalized_page_ids:
            raise NotionPageIndexError(
                error_code="INVALID_ARGUMENT",
                message="page_ids must contain at least one non-empty value",
                http_status_code=400,
                failure_reason="UNKNOWN_ERROR",
            )

        workflow_run = self._workflow_run_service.start_workflow(
            workflow_type="indexing",
            metadata_json=json.dumps(
                {
                    "sync_mode": "manual",
                    "operation": "index_incremental",
                    "page_ids": normalized_page_ids,
                    "request_workflow_id": request_workflow_id,
                    "reconciliation_strategy": "page_level_replacement",
                },
                sort_keys=True,
            ),
        )

        indexed_pages: List[NotionIncrementalIndexedPageResult] = []
        current_page_id = ""
        try:
            for page_id in normalized_page_ids:
                current_page_id = page_id
                snapshot = await self._page_index_orchestrator.index_page_snapshot(
                    page_id=page_id,
                    request_workflow_id=request_workflow_id,
                )
                indexed_pages.append(
                    NotionIncrementalIndexedPageResult(
                        page_id=snapshot.notion_page_id,
                        page_title=snapshot.page_title,
                        notion_path=snapshot.notion_path,
                        indexed_block_count=snapshot.indexed_block_count,
                    )
                )

            self._workflow_run_service.mark_workflow_succeeded(
                workflow_run.id,
                metadata_json=json.dumps(
                    {
                        "operation": "index_incremental",
                        "sync_mode": "manual",
                        "processed_page_count": len(indexed_pages),
                        "page_ids": normalized_page_ids,
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
                        "operation": "index_incremental",
                        "sync_mode": "manual",
                        "failed_page_id": current_page_id,
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

        return NotionIncrementalIndexResult(
            workflow_run_id=workflow_run.id,
            status="succeeded",
            sync_mode="manual",
            processed_page_count=len(indexed_pages),
            indexed_pages=indexed_pages,
        )

    def _normalize_page_ids(self, page_ids: List[str]) -> List[str]:
        seen = set()
        normalized: List[str] = []
        for page_id in page_ids:
            candidate = str(page_id).strip()
            if not candidate:
                continue
            if candidate in seen:
                continue
            seen.add(candidate)
            normalized.append(candidate)
        return normalized
