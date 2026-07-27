from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.dependencies import (
    get_cost_tracker,
    get_embedding_client,
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
from src.db.session import (
    SessionFactory,
    UnitOfWorkFactory,
    get_db_session,
    get_db_session_factory,
    get_unit_of_work_factory,
)
from src.orchestrators import (
    NotionPageIndexOrchestrator,
    SupplementProposeError,
    SupplementProposeOrchestrator,
    SupplementReviewError,
    SupplementReviewOrchestrator,
)
from src.providers import EmbeddingClient, ProviderRouter
from src.repositories import (
    ChangeRequestRepository,
    ChunkRepository,
    NotionPageRepository,
    SourceDocumentRepository,
)
from src.services import (
    CostTracker,
    DuplicateKnowledgeChecker,
    PromptTemplateLoader,
    WorkflowRunService,
)
from src.tools import ToolRegistry

router = APIRouter()


def _build_supplement_propose_orchestrator(
    *,
    db_session: Session,
    db_session_factory: SessionFactory,
    provider_router: ProviderRouter,
    cost_tracker: CostTracker,
    prompt_template_loader: PromptTemplateLoader,
) -> SupplementProposeOrchestrator:
    return SupplementProposeOrchestrator(
        provider_router=provider_router,
        cost_tracker=cost_tracker,
        prompt_template_loader=prompt_template_loader,
        source_document_repository=SourceDocumentRepository(db_session),
        change_request_repository=ChangeRequestRepository(db_session),
        duplicate_checker=DuplicateKnowledgeChecker(
            chunk_repository=ChunkRepository(db_session),
        ),
        workflow_run_service=WorkflowRunService(db_session_factory),
    )


def _build_supplement_review_orchestrator(
    *,
    db_session: Session,
    db_session_factory: SessionFactory,
    unit_of_work_factory: UnitOfWorkFactory,
    tool_registry: ToolRegistry,
    embedding_client: Optional[EmbeddingClient],
    cost_tracker: CostTracker,
) -> SupplementReviewOrchestrator:
    page_index_orchestrator = NotionPageIndexOrchestrator(
        tool_registry=tool_registry,
        unit_of_work_factory=unit_of_work_factory,
        workflow_run_service=WorkflowRunService(db_session_factory),
        embedding_client=embedding_client,
        cost_tracker=cost_tracker,
    )
    return SupplementReviewOrchestrator(
        change_request_repository=ChangeRequestRepository(db_session),
        notion_page_repository=NotionPageRepository(db_session),
        tool_registry=tool_registry,
        page_index_orchestrator=page_index_orchestrator,
        workflow_run_service=WorkflowRunService(db_session_factory),
    )


@router.post("/api/supplement/propose", response_model=SupplementProposeResponse)
async def propose_supplement_change_request(
    payload: SupplementProposeRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    db_session_factory: SessionFactory = Depends(get_db_session_factory),
    provider_router: ProviderRouter = Depends(get_provider_router),
    cost_tracker: CostTracker = Depends(get_cost_tracker),
    prompt_template_loader: PromptTemplateLoader = Depends(get_prompt_template_loader),
) -> SupplementProposeResponse:
    orchestrator = _build_supplement_propose_orchestrator(
        db_session=db_session,
        db_session_factory=db_session_factory,
        provider_router=provider_router,
        cost_tracker=cost_tracker,
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
    db_session_factory: SessionFactory = Depends(get_db_session_factory),
    unit_of_work_factory: UnitOfWorkFactory = Depends(get_unit_of_work_factory),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
    embedding_client: Optional[EmbeddingClient] = Depends(get_embedding_client),
    cost_tracker: CostTracker = Depends(get_cost_tracker),
) -> SupplementReviewResponse:
    orchestrator = _build_supplement_review_orchestrator(
        db_session=db_session,
        db_session_factory=db_session_factory,
        unit_of_work_factory=unit_of_work_factory,
        tool_registry=tool_registry,
        embedding_client=embedding_client,
        cost_tracker=cost_tracker,
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
    db_session_factory: SessionFactory = Depends(get_db_session_factory),
    unit_of_work_factory: UnitOfWorkFactory = Depends(get_unit_of_work_factory),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
    embedding_client: Optional[EmbeddingClient] = Depends(get_embedding_client),
    cost_tracker: CostTracker = Depends(get_cost_tracker),
) -> SupplementReviewResponse:
    orchestrator = _build_supplement_review_orchestrator(
        db_session=db_session,
        db_session_factory=db_session_factory,
        unit_of_work_factory=unit_of_work_factory,
        tool_registry=tool_registry,
        embedding_client=embedding_client,
        cost_tracker=cost_tracker,
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
    db_session_factory: SessionFactory = Depends(get_db_session_factory),
    unit_of_work_factory: UnitOfWorkFactory = Depends(get_unit_of_work_factory),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
    embedding_client: Optional[EmbeddingClient] = Depends(get_embedding_client),
    cost_tracker: CostTracker = Depends(get_cost_tracker),
) -> SupplementReviewResponse:
    orchestrator = _build_supplement_review_orchestrator(
        db_session=db_session,
        db_session_factory=db_session_factory,
        unit_of_work_factory=unit_of_work_factory,
        tool_registry=tool_registry,
        embedding_client=embedding_client,
        cost_tracker=cost_tracker,
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
