from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.dependencies import get_provider_router
from src.app.schemas import SupplementProposeRequest, SupplementProposeResponse
from src.db.session import get_db_session
from src.orchestrators import (
    SupplementProposeError,
    SupplementProposeOrchestrator,
)
from src.providers import ProviderRouter
from src.repositories import (
    ChangeRequestRepository,
    ChunkRepository,
    SourceDocumentRepository,
    WorkflowRunRepository,
)
from src.services import DuplicateKnowledgeChecker, WorkflowRunService

router = APIRouter()


def _build_supplement_propose_orchestrator(
    *,
    db_session: Session,
    provider_router: ProviderRouter,
) -> SupplementProposeOrchestrator:
    return SupplementProposeOrchestrator(
        provider_router=provider_router,
        source_document_repository=SourceDocumentRepository(db_session),
        change_request_repository=ChangeRequestRepository(db_session),
        duplicate_checker=DuplicateKnowledgeChecker(
            chunk_repository=ChunkRepository(db_session),
        ),
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
    )


@router.post("/api/supplement/propose", response_model=SupplementProposeResponse)
async def propose_supplement_change_request(
    payload: SupplementProposeRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    provider_router: ProviderRouter = Depends(get_provider_router),
) -> SupplementProposeResponse:
    orchestrator = _build_supplement_propose_orchestrator(
        db_session=db_session,
        provider_router=provider_router,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))

    try:
        result = await orchestrator.propose_change_request(
            source_document_id=payload.source_document_id,
            provider_name=payload.provider_name,
            model=payload.model,
            request_workflow_id=request_workflow_id,
            target_notion_page_id=payload.target_notion_page_id,
        )
    except SupplementProposeError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc

    return SupplementProposeResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        change_request_id=result.change_request_id,
        change_request_status=result.change_request_status,
        source_document_id=result.source_document_id,
        duplicate_detected=result.duplicate_detected,
        duplicate_notion_path=result.duplicate_notion_path,
        provider=result.provider,
        model=result.model,
        token_input=result.token_input,
        token_output=result.token_output,
    )
