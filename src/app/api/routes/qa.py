from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.dependencies import get_provider_router
from src.app.schemas import QACitation, QARequest, QAResponse
from src.db.session import get_db_session
from src.orchestrators import QAOrchestrator, QAOrchestratorError
from src.providers import ProviderRouter
from src.rag import ProductionChunkRetriever
from src.repositories import ChunkRepository, WorkflowRunRepository
from src.services import WorkflowRunService

router = APIRouter()


def _build_qa_orchestrator(
    *,
    db_session: Session,
    provider_router: ProviderRouter,
) -> QAOrchestrator:
    return QAOrchestrator(
        retriever=ProductionChunkRetriever(
            chunk_repository=ChunkRepository(db_session),
        ),
        provider_router=provider_router,
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
    )


@router.post("/api/qa", response_model=QAResponse)
async def run_qa(
    payload: QARequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    provider_router: ProviderRouter = Depends(get_provider_router),
) -> QAResponse:
    orchestrator = _build_qa_orchestrator(
        db_session=db_session,
        provider_router=provider_router,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))

    try:
        result = await orchestrator.answer_question(
            query=payload.query,
            top_k=payload.top_k,
            page_ids=payload.page_ids,
            section_paths=payload.section_paths,
            source_kinds=payload.source_kinds,
            provider_name=payload.provider_name,
            model=payload.model,
            request_workflow_id=request_workflow_id,
        )
    except QAOrchestratorError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc

    return QAResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        answer=result.answer,
        insufficient_info=result.insufficient_info,
        retrieved_chunk_count=result.retrieved_chunk_count,
        citations=[
            QACitation(
                notion_path=citation.notion_path,
                page_id=citation.page_id,
                score=citation.score,
            )
            for citation in result.citations
        ],
        provider=result.provider,
        model=result.model,
        token_input=result.token_input,
        token_output=result.token_output,
    )
