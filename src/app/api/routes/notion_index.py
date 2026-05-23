from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.dependencies import get_tool_registry
from src.app.schemas import (
    NotionIncrementalIndexRequest,
    NotionIncrementalIndexResponse,
    NotionIncrementalIndexedPage,
    NotionPageIndexRequest,
    NotionPageIndexResponse,
)
from src.db.session import get_db_session
from src.orchestrators import (
    NotionIncrementalIndexOrchestrator,
    NotionPageIndexError,
    NotionPageIndexOrchestrator,
)
from src.repositories import (
    ChunkRepository,
    NotionBlockRepository,
    NotionPageRepository,
    WorkflowRunRepository,
)
from src.services import WorkflowRunService
from src.tools import ToolRegistry

router = APIRouter()


def _build_index_orchestrator(
    *,
    db_session: Session,
    tool_registry: ToolRegistry,
) -> NotionPageIndexOrchestrator:
    return NotionPageIndexOrchestrator(
        tool_registry=tool_registry,
        notion_page_repository=NotionPageRepository(db_session),
        notion_block_repository=NotionBlockRepository(db_session),
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
        chunk_repository=ChunkRepository(db_session),
    )


def _build_incremental_orchestrator(
    *,
    db_session: Session,
    tool_registry: ToolRegistry,
) -> NotionIncrementalIndexOrchestrator:
    return NotionIncrementalIndexOrchestrator(
        page_index_orchestrator=_build_index_orchestrator(
            db_session=db_session,
            tool_registry=tool_registry,
        ),
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
    )


@router.post("/api/notion/index/page", response_model=NotionPageIndexResponse)
async def index_notion_page(
    payload: NotionPageIndexRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
) -> NotionPageIndexResponse:
    orchestrator = _build_index_orchestrator(
        db_session=db_session,
        tool_registry=tool_registry,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))

    try:
        result = await orchestrator.index_page(
            page_id=payload.page_id,
            request_workflow_id=request_workflow_id,
        )
    except NotionPageIndexError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc

    return NotionPageIndexResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        page_id=result.notion_page_id,
        page_title=result.page_title,
        notion_path=result.notion_path,
        indexed_block_count=result.indexed_block_count,
    )


@router.post(
    "/api/notion/index/incremental",
    response_model=NotionIncrementalIndexResponse,
)
async def index_notion_incremental(
    payload: NotionIncrementalIndexRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
) -> NotionIncrementalIndexResponse:
    orchestrator = _build_incremental_orchestrator(
        db_session=db_session,
        tool_registry=tool_registry,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))

    try:
        result = await orchestrator.sync_pages(
            page_ids=payload.page_ids,
            request_workflow_id=request_workflow_id,
        )
    except NotionPageIndexError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc

    return NotionIncrementalIndexResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        sync_mode=result.sync_mode,
        processed_page_count=result.processed_page_count,
        indexed_pages=[
            NotionIncrementalIndexedPage(
                page_id=page.page_id,
                page_title=page.page_title,
                notion_path=page.notion_path,
                indexed_block_count=page.indexed_block_count,
            )
            for page in result.indexed_pages
        ],
    )
