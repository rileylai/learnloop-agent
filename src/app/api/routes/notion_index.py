from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.dependencies import (
    get_cost_tracker,
    get_embedding_client,
    get_tool_registry,
)
from src.app.schemas import (
    NotionIncrementalIndexRequest,
    NotionIncrementalIndexResponse,
    NotionIncrementalIndexedPage,
    NotionPageIndexRequest,
    NotionPageIndexResponse,
)
from src.db.session import SessionFactory, get_db_session, get_db_session_factory
from src.orchestrators import (
    NotionIncrementalIndexOrchestrator,
    NotionPageIndexError,
    NotionPageIndexOrchestrator,
)
from src.providers import EmbeddingClient
from src.repositories import (
    ChunkRepository,
    NotionBlockRepository,
    NotionPageRepository,
)
from src.services import CostTracker, WorkflowRunService
from src.tools import ToolRegistry

router = APIRouter()


def _build_index_orchestrator(
    *,
    db_session: Session,
    db_session_factory: SessionFactory,
    tool_registry: ToolRegistry,
    embedding_client: Optional[EmbeddingClient],
    cost_tracker: CostTracker,
) -> NotionPageIndexOrchestrator:
    return NotionPageIndexOrchestrator(
        tool_registry=tool_registry,
        notion_page_repository=NotionPageRepository(db_session),
        notion_block_repository=NotionBlockRepository(db_session),
        workflow_run_service=WorkflowRunService(db_session_factory),
        chunk_repository=ChunkRepository(db_session),
        embedding_client=embedding_client,
        cost_tracker=cost_tracker,
    )


def _build_incremental_orchestrator(
    *,
    db_session: Session,
    db_session_factory: SessionFactory,
    tool_registry: ToolRegistry,
    embedding_client: Optional[EmbeddingClient],
    cost_tracker: CostTracker,
) -> NotionIncrementalIndexOrchestrator:
    return NotionIncrementalIndexOrchestrator(
        page_index_orchestrator=_build_index_orchestrator(
            db_session=db_session,
            db_session_factory=db_session_factory,
            tool_registry=tool_registry,
            embedding_client=embedding_client,
            cost_tracker=cost_tracker,
        ),
        workflow_run_service=WorkflowRunService(db_session_factory),
    )


@router.post("/api/notion/index/page", response_model=NotionPageIndexResponse)
async def index_notion_page(
    payload: NotionPageIndexRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    db_session_factory: SessionFactory = Depends(get_db_session_factory),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
    embedding_client: Optional[EmbeddingClient] = Depends(get_embedding_client),
    cost_tracker: CostTracker = Depends(get_cost_tracker),
) -> NotionPageIndexResponse:
    orchestrator = _build_index_orchestrator(
        db_session=db_session,
        db_session_factory=db_session_factory,
        tool_registry=tool_registry,
        embedding_client=embedding_client,
        cost_tracker=cost_tracker,
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
    db_session_factory: SessionFactory = Depends(get_db_session_factory),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
    embedding_client: Optional[EmbeddingClient] = Depends(get_embedding_client),
    cost_tracker: CostTracker = Depends(get_cost_tracker),
) -> NotionIncrementalIndexResponse:
    orchestrator = _build_incremental_orchestrator(
        db_session=db_session,
        db_session_factory=db_session_factory,
        tool_registry=tool_registry,
        embedding_client=embedding_client,
        cost_tracker=cost_tracker,
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
