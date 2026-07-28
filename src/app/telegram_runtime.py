from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from src.db.session import SessionFactory, UnitOfWorkFactory
from src.orchestrators import (
    DocumentIngestionOrchestrator,
    ImageOCRIngestionOrchestrator,
    NotionPageIndexOrchestrator,
    QAOrchestrator,
    SupplementProposeOrchestrator,
    SupplementReviewOrchestrator,
    SupplementQueryOrchestrator,
    TelegramGatewayOrchestrator,
    TelegramIngestionOrchestrator,
    TelegramPageOrchestrator,
    TelegramQAOrchestrator,
    TelegramReviewOrchestrator,
)
from src.providers import EmbeddingClient, ProviderRouter
from src.queue import QueueClient
from src.rag import ProductionChunkRetriever
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
    TelegramUpdateIdempotencyService,
    TrustBoundaryService,
    WorkflowRunService,
)
from src.tools import ToolRegistry


def build_telegram_gateway_orchestrator(
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
    queue_client: Optional[QueueClient] = None,
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
        queue_client=queue_client,
    )
