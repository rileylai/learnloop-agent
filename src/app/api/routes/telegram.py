from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.app.dependencies import (
    get_cost_tracker,
    get_embedding_client,
    get_prompt_template_loader,
    get_provider_router,
    get_trust_boundary,
    get_tool_registry,
)
from src.app.schemas import TelegramWebhookRequest, TelegramWebhookResponse
from src.db.session import (
    SessionFactory,
    UnitOfWorkFactory,
    get_db_session,
    get_db_session_factory,
    get_unit_of_work_factory,
)
from src.orchestrators import (
    DocumentIngestionOrchestrator,
    ImageOCRIngestionOrchestrator,
    NotionPageIndexOrchestrator,
    QAOrchestrator,
    SupplementProposeOrchestrator,
    SupplementReviewOrchestrator,
    SupplementQueryOrchestrator,
    TelegramDocumentAttachment,
    TelegramGatewayError,
    TelegramGatewayOrchestrator,
    TelegramIngestionOrchestrator,
    TelegramPhotoAttachment,
    TelegramPageOrchestrator,
    TelegramQAOrchestrator,
    TelegramReviewOrchestrator,
)
from src.providers import EmbeddingClient, ProviderRouter
from src.repositories import (
    ChangeRequestRepository,
    ChunkRepository,
    NotionPageRepository,
    SourceDocumentRepository,
)
from src.rag import ProductionChunkRetriever
from src.services import (
    CostTracker,
    DuplicateKnowledgeChecker,
    PromptTemplateLoader,
    TrustBoundaryError,
    TrustBoundaryService,
    TelegramUpdateIdempotencyService,
    WorkflowRunService,
)
from src.tools import ToolRegistry

router = APIRouter()


def _build_telegram_gateway_orchestrator(
    *,
    db_session: Session,
    db_session_factory: SessionFactory,
    unit_of_work_factory: UnitOfWorkFactory,
    tool_registry: ToolRegistry,
    provider_router: ProviderRouter,
    embedding_client: Optional[EmbeddingClient],
    cost_tracker: CostTracker,
    prompt_template_loader: PromptTemplateLoader,
    trust_boundary: TrustBoundaryService,
) -> TelegramGatewayOrchestrator:
    workflow_run_service = WorkflowRunService(db_session_factory)
    update_idempotency_service = TelegramUpdateIdempotencyService(
        db_session_factory
    )

    telegram_ingestion_orchestrator = TelegramIngestionOrchestrator(
        tool_registry=tool_registry,
        document_ingestion_orchestrator=DocumentIngestionOrchestrator(
            tool_registry=tool_registry,
            unit_of_work_factory=unit_of_work_factory,
            workflow_run_service=workflow_run_service,
        ),
        image_ocr_ingestion_orchestrator=ImageOCRIngestionOrchestrator(
            tool_registry=tool_registry,
            unit_of_work_factory=unit_of_work_factory,
            workflow_run_service=workflow_run_service,
        ),
        supplement_propose_orchestrator=SupplementProposeOrchestrator(
            provider_router=provider_router,
            cost_tracker=cost_tracker,
            prompt_template_loader=prompt_template_loader,
            source_document_repository=SourceDocumentRepository(db_session),
            notion_page_repository=NotionPageRepository(db_session),
            change_request_repository=ChangeRequestRepository(db_session),
            unit_of_work_factory=unit_of_work_factory,
            duplicate_checker=DuplicateKnowledgeChecker(
                chunk_repository=ChunkRepository(db_session),
            ),
            workflow_run_service=workflow_run_service,
        ),
        supplement_query_orchestrator=SupplementQueryOrchestrator(
            change_request_repository=ChangeRequestRepository(db_session),
            notion_page_repository=NotionPageRepository(db_session),
        ),
    )
    telegram_qa_orchestrator = TelegramQAOrchestrator(
        qa_orchestrator=QAOrchestrator(
            retriever=ProductionChunkRetriever(
                chunk_repository=ChunkRepository(db_session),
            ),
            embedding_client=embedding_client,
            provider_router=provider_router,
            cost_tracker=cost_tracker,
            prompt_template_loader=prompt_template_loader,
            workflow_run_service=workflow_run_service,
        )
    )
    telegram_review_orchestrator = TelegramReviewOrchestrator(
        supplement_review_orchestrator=SupplementReviewOrchestrator(
            change_request_repository=ChangeRequestRepository(db_session),
            notion_page_repository=NotionPageRepository(db_session),
            unit_of_work_factory=unit_of_work_factory,
            tool_registry=tool_registry,
            page_index_orchestrator=NotionPageIndexOrchestrator(
                tool_registry=tool_registry,
                unit_of_work_factory=unit_of_work_factory,
                workflow_run_service=workflow_run_service,
                embedding_client=embedding_client,
                cost_tracker=cost_tracker,
            ),
            workflow_run_service=workflow_run_service,
        )
    )
    telegram_page_orchestrator = TelegramPageOrchestrator(
        notion_page_repository=NotionPageRepository(db_session)
    )

    return TelegramGatewayOrchestrator(
        tool_registry=tool_registry,
        workflow_run_service=workflow_run_service,
        telegram_ingestion_orchestrator=telegram_ingestion_orchestrator,
        telegram_qa_orchestrator=telegram_qa_orchestrator,
        telegram_review_orchestrator=telegram_review_orchestrator,
        telegram_page_orchestrator=telegram_page_orchestrator,
        trust_boundary=trust_boundary,
        update_idempotency_service=update_idempotency_service,
    )


@router.post("/api/telegram/webhook", response_model=TelegramWebhookResponse)
async def handle_telegram_webhook(
    payload: TelegramWebhookRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    db_session_factory: SessionFactory = Depends(get_db_session_factory),
    unit_of_work_factory: UnitOfWorkFactory = Depends(get_unit_of_work_factory),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
    provider_router: ProviderRouter = Depends(get_provider_router),
    embedding_client: Optional[EmbeddingClient] = Depends(get_embedding_client),
    cost_tracker: CostTracker = Depends(get_cost_tracker),
    prompt_template_loader: PromptTemplateLoader = Depends(get_prompt_template_loader),
    telegram_webhook_secret: Optional[str] = Header(
        default=None,
        alias="X-Telegram-Bot-Api-Secret-Token",
    ),
    trust_boundary: TrustBoundaryService = Depends(get_trust_boundary),
) -> TelegramWebhookResponse:
    try:
        trust_boundary.require_telegram_webhook_secret(telegram_webhook_secret)
    except TrustBoundaryError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": None,
            },
        ) from exc

    orchestrator = _build_telegram_gateway_orchestrator(
        db_session=db_session,
        db_session_factory=db_session_factory,
        unit_of_work_factory=unit_of_work_factory,
        tool_registry=tool_registry,
        provider_router=provider_router,
        embedding_client=embedding_client,
        cost_tracker=cost_tracker,
        prompt_template_loader=prompt_template_loader,
        trust_boundary=trust_boundary,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))
    message = payload.message
    chat_id = str(message.chat.id) if message is not None else None
    text = message.text if message is not None else None
    caption = message.caption if message is not None else None

    document = None
    photos: list[TelegramPhotoAttachment] = []
    if message is not None and message.document is not None:
        document = TelegramDocumentAttachment(
            file_id=message.document.file_id,
            file_name=message.document.file_name,
        )
    if message is not None:
        photos = [
            TelegramPhotoAttachment(
                file_id=photo.file_id,
                file_unique_id=photo.file_unique_id,
                file_size=photo.file_size,
            )
            for photo in message.photo
        ]

    try:
        result = await orchestrator.handle_webhook(
            update_id=payload.update_id,
            chat_id=chat_id,
            text=text,
            caption=caption,
            document=document,
            photos=photos,
            request_workflow_id=request_workflow_id,
        )
    except TelegramGatewayError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc

    response = TelegramWebhookResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        handled=result.handled,
        command=result.command,
        reply_text=result.reply_text,
        telegram_message_id=result.telegram_message_id,
        skipped_reason=result.skipped_reason,
        source_document_id=result.source_document_id,
        change_request_id=result.change_request_id,
        source_type=result.source_type,
        target_notion_page_id=result.target_notion_page_id,
        qa_workflow_run_id=result.qa_workflow_run_id,
        insufficient_info=result.insufficient_info,
        citations=result.citations,
        review_workflow_run_id=result.review_workflow_run_id,
        review_action=result.review_action,
        change_request_status=result.change_request_status,
    )
    if result.status == "running":
        content = (
            response.model_dump()
            if hasattr(response, "model_dump")
            else response.dict()
        )
        return JSONResponse(status_code=202, content=content)
    return response
