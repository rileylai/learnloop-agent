from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.dependencies import (
    get_prompt_template_loader,
    get_provider_router,
    get_tool_registry,
)
from src.app.schemas import (
    SupplementAcceptRequest,
    SupplementEditLaterRequest,
    SupplementProposeRequest,
    SupplementProposeResponse,
    SupplementRejectRequest,
    SupplementReviewResponse,
)
from src.db.session import get_db_session
from src.orchestrators import (
    NotionPageIndexOrchestrator,
    SupplementProposeError,
    SupplementProposeOrchestrator,
    SupplementReviewError,
    SupplementReviewOrchestrator,
)
from src.providers import ProviderRouter
from src.repositories import (
    ChangeRequestRepository,
    ChunkRepository,
    NotionBlockRepository,
    NotionPageRepository,
    SourceDocumentRepository,
    WorkflowRunRepository,
)
from src.services import (
    DuplicateKnowledgeChecker,
    PromptTemplateLoader,
    WorkflowRunService,
)
from src.tools import ToolRegistry

router = APIRouter()


def _build_supplement_propose_orchestrator(
    *,
    db_session: Session,
    provider_router: ProviderRouter,
    prompt_template_loader: PromptTemplateLoader,
) -> SupplementProposeOrchestrator:
    return SupplementProposeOrchestrator(
        provider_router=provider_router,
        prompt_template_loader=prompt_template_loader,
        source_document_repository=SourceDocumentRepository(db_session),
        change_request_repository=ChangeRequestRepository(db_session),
        duplicate_checker=DuplicateKnowledgeChecker(
            chunk_repository=ChunkRepository(db_session),
        ),
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
    )


def _build_supplement_review_orchestrator(
    *,
    db_session: Session,
    tool_registry: ToolRegistry,
) -> SupplementReviewOrchestrator:
    page_index_orchestrator = NotionPageIndexOrchestrator(
        tool_registry=tool_registry,
        notion_page_repository=NotionPageRepository(db_session),
        notion_block_repository=NotionBlockRepository(db_session),
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
        chunk_repository=ChunkRepository(db_session),
    )
    return SupplementReviewOrchestrator(
        change_request_repository=ChangeRequestRepository(db_session),
        notion_page_repository=NotionPageRepository(db_session),
        tool_registry=tool_registry,
        page_index_orchestrator=page_index_orchestrator,
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
    )


@router.post("/api/supplement/propose", response_model=SupplementProposeResponse)
async def propose_supplement_change_request(
    payload: SupplementProposeRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    provider_router: ProviderRouter = Depends(get_provider_router),
    prompt_template_loader: PromptTemplateLoader = Depends(get_prompt_template_loader),
) -> SupplementProposeResponse:
    orchestrator = _build_supplement_propose_orchestrator(
        db_session=db_session,
        provider_router=provider_router,
        prompt_template_loader=prompt_template_loader,
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


@router.post("/api/supplement/accept", response_model=SupplementReviewResponse)
async def accept_supplement_change_request(
    payload: SupplementAcceptRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
) -> SupplementReviewResponse:
    orchestrator = _build_supplement_review_orchestrator(
        db_session=db_session,
        tool_registry=tool_registry,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))

    try:
        result = await orchestrator.accept_change_request(
            change_request_id=payload.change_request_id,
            reviewer=payload.reviewer,
            request_workflow_id=request_workflow_id,
        )
    except SupplementReviewError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc

    return SupplementReviewResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        change_request_id=result.change_request_id,
        change_request_status=result.change_request_status,
        review_action=result.review_action,
        reviewer=result.reviewer,
        reason=result.reason,
    )


@router.post("/api/supplement/reject", response_model=SupplementReviewResponse)
async def reject_supplement_change_request(
    payload: SupplementRejectRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
) -> SupplementReviewResponse:
    orchestrator = _build_supplement_review_orchestrator(
        db_session=db_session,
        tool_registry=tool_registry,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))

    try:
        result = await orchestrator.reject_change_request(
            change_request_id=payload.change_request_id,
            reviewer=payload.reviewer,
            reason=payload.reason,
            request_workflow_id=request_workflow_id,
        )
    except SupplementReviewError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc

    return SupplementReviewResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        change_request_id=result.change_request_id,
        change_request_status=result.change_request_status,
        review_action=result.review_action,
        reviewer=result.reviewer,
        reason=result.reason,
    )


@router.post("/api/supplement/edit-later", response_model=SupplementReviewResponse)
async def edit_later_supplement_change_request(
    payload: SupplementEditLaterRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
) -> SupplementReviewResponse:
    orchestrator = _build_supplement_review_orchestrator(
        db_session=db_session,
        tool_registry=tool_registry,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))

    try:
        result = await orchestrator.mark_edit_later(
            change_request_id=payload.change_request_id,
            reviewer=payload.reviewer,
            reason=payload.reason,
            request_workflow_id=request_workflow_id,
        )
    except SupplementReviewError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc

    return SupplementReviewResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        change_request_id=result.change_request_id,
        change_request_status=result.change_request_status,
        review_action=result.review_action,
        reviewer=result.reviewer,
        reason=result.reason,
    )
