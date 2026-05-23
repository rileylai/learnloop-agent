from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.schemas import SourceDocumentCreateRequest, SourceDocumentCreateResponse
from src.db.session import get_db_session
from src.orchestrators import SourceDocumentOrchestrator, SourceDocumentWorkflowError
from src.repositories import SourceDocumentRepository, WorkflowRunRepository
from src.services import WorkflowRunService

router = APIRouter()


def _build_source_document_orchestrator(
    *,
    db_session: Session,
) -> SourceDocumentOrchestrator:
    return SourceDocumentOrchestrator(
        source_document_repository=SourceDocumentRepository(db_session),
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
    )


@router.post("/api/ingest/source", response_model=SourceDocumentCreateResponse)
async def create_source_document(
    payload: SourceDocumentCreateRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> SourceDocumentCreateResponse:
    orchestrator = _build_source_document_orchestrator(db_session=db_session)
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))

    try:
        result = await orchestrator.create_source_document(
            source_type=payload.source_type,
            source_display_name=payload.source_display_name,
            raw_text=payload.raw_text,
            request_workflow_id=request_workflow_id,
        )
    except SourceDocumentWorkflowError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc

    return SourceDocumentCreateResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        source_document_id=result.source_document_id,
        source_type=result.source_type,
        source_display_name=result.source_display_name,
        content_hash=result.content_hash,
    )
