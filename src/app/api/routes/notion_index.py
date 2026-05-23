from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.dependencies import get_tool_registry
from src.app.schemas import NotionPageIndexRequest, NotionPageIndexResponse
from src.db.session import get_db_session
from src.orchestrators import NotionPageIndexError, NotionPageIndexOrchestrator
from src.repositories import (
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
