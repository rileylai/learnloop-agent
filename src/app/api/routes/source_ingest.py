from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from src.app.dependencies import get_tool_registry
from src.app.schemas import (
    SourceDocumentCreateRequest,
    SourceDocumentCreateResponse,
    URLIngestionRequest,
)
from src.db.session import get_db_session
from src.orchestrators import (
    DocumentIngestionError,
    DocumentIngestionOrchestrator,
    SourceDocumentOrchestrator,
    SourceDocumentWorkflowError,
    URLIngestionError,
    URLIngestionOrchestrator,
)
from src.repositories import SourceDocumentRepository, WorkflowRunRepository
from src.services import WorkflowRunService
from src.tools import ToolRegistry

router = APIRouter()


def _build_source_document_orchestrator(
    *,
    db_session: Session,
) -> SourceDocumentOrchestrator:
    return SourceDocumentOrchestrator(
        source_document_repository=SourceDocumentRepository(db_session),
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
    )


def _build_document_ingestion_orchestrator(
    *,
    db_session: Session,
    tool_registry: ToolRegistry,
) -> DocumentIngestionOrchestrator:
    return DocumentIngestionOrchestrator(
        tool_registry=tool_registry,
        source_document_repository=SourceDocumentRepository(db_session),
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
    )


def _build_url_ingestion_orchestrator(
    *,
    db_session: Session,
    tool_registry: ToolRegistry,
) -> URLIngestionOrchestrator:
    return URLIngestionOrchestrator(
        tool_registry=tool_registry,
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


@router.post("/api/ingest/url", response_model=SourceDocumentCreateResponse)
async def ingest_url_article(
    payload: URLIngestionRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
) -> SourceDocumentCreateResponse:
    orchestrator = _build_url_ingestion_orchestrator(
        db_session=db_session,
        tool_registry=tool_registry,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))

    try:
        result = await orchestrator.ingest_url(
            url=payload.url,
            request_workflow_id=request_workflow_id,
        )
    except URLIngestionError as exc:
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


@router.post("/api/ingest/document", response_model=SourceDocumentCreateResponse)
async def ingest_pdf_document(
    request: Request,
    document: UploadFile = File(...),
    db_session: Session = Depends(get_db_session),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
) -> SourceDocumentCreateResponse:
    orchestrator = _build_document_ingestion_orchestrator(
        db_session=db_session,
        tool_registry=tool_registry,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))

    try:
        document_bytes = await document.read()
        result = await orchestrator.ingest_document(
            file_name=document.filename or "",
            file_bytes=document_bytes,
            request_workflow_id=request_workflow_id,
        )
    except DocumentIngestionError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc
    finally:
        await document.close()

    return SourceDocumentCreateResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        source_document_id=result.source_document_id,
        source_type=result.source_type,
        source_display_name=result.source_display_name,
        content_hash=result.content_hash,
    )
