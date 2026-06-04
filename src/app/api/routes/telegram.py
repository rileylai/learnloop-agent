from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.dependencies import get_provider_router, get_tool_registry
from src.app.schemas import TelegramWebhookRequest, TelegramWebhookResponse
from src.db.session import get_db_session
from src.orchestrators import (
    DocumentIngestionOrchestrator,
    ImageOCRIngestionOrchestrator,
    QAOrchestrator,
    SupplementProposeOrchestrator,
    TelegramDocumentAttachment,
    TelegramGatewayError,
    TelegramGatewayOrchestrator,
    TelegramIngestionOrchestrator,
    TelegramPhotoAttachment,
    TelegramQAOrchestrator,
)
from src.providers import ProviderRouter
from src.repositories import (
    ChangeRequestRepository,
    ChunkRepository,
    SourceDocumentRepository,
    WorkflowRunRepository,
)
from src.rag import ProductionChunkRetriever
from src.services import DuplicateKnowledgeChecker, WorkflowRunService
from src.tools import ToolRegistry

router = APIRouter()


def _build_telegram_gateway_orchestrator(
    *,
    db_session: Session,
    tool_registry: ToolRegistry,
    provider_router: ProviderRouter,
) -> TelegramGatewayOrchestrator:
    workflow_run_service = WorkflowRunService(WorkflowRunRepository(db_session))

    telegram_ingestion_orchestrator = TelegramIngestionOrchestrator(
        tool_registry=tool_registry,
        document_ingestion_orchestrator=DocumentIngestionOrchestrator(
            tool_registry=tool_registry,
            source_document_repository=SourceDocumentRepository(db_session),
            workflow_run_service=workflow_run_service,
        ),
        image_ocr_ingestion_orchestrator=ImageOCRIngestionOrchestrator(
            tool_registry=tool_registry,
            source_document_repository=SourceDocumentRepository(db_session),
            workflow_run_service=workflow_run_service,
        ),
        supplement_propose_orchestrator=SupplementProposeOrchestrator(
            provider_router=provider_router,
            source_document_repository=SourceDocumentRepository(db_session),
            change_request_repository=ChangeRequestRepository(db_session),
            duplicate_checker=DuplicateKnowledgeChecker(
                chunk_repository=ChunkRepository(db_session),
            ),
            workflow_run_service=workflow_run_service,
        ),
    )
    telegram_qa_orchestrator = TelegramQAOrchestrator(
        qa_orchestrator=QAOrchestrator(
            retriever=ProductionChunkRetriever(
                chunk_repository=ChunkRepository(db_session),
            ),
            provider_router=provider_router,
            workflow_run_service=workflow_run_service,
        )
    )

    return TelegramGatewayOrchestrator(
        tool_registry=tool_registry,
        workflow_run_service=workflow_run_service,
        telegram_ingestion_orchestrator=telegram_ingestion_orchestrator,
        telegram_qa_orchestrator=telegram_qa_orchestrator,
    )


@router.post("/api/telegram/webhook", response_model=TelegramWebhookResponse)
async def handle_telegram_webhook(
    payload: TelegramWebhookRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
    provider_router: ProviderRouter = Depends(get_provider_router),
) -> TelegramWebhookResponse:
    orchestrator = _build_telegram_gateway_orchestrator(
        db_session=db_session,
        tool_registry=tool_registry,
        provider_router=provider_router,
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

    return TelegramWebhookResponse(
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
        qa_workflow_run_id=result.qa_workflow_run_id,
        insufficient_info=result.insufficient_info,
        citations=result.citations,
    )
