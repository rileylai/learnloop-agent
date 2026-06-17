from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import List, Optional

from src.providers import (
    LLMMessage,
    LLMRequest,
    LLMClientError,
    ProviderNotFoundError,
    ProviderRouter,
    ProviderRouterError,
)
from src.rag import ProductionChunkRetriever, RetrievedChunk
from src.services import (
    CostTracker,
    PROMPT_ID_QA_ANSWER,
    PromptTemplateLoader,
    PromptTemplateLoaderError,
    STANDARD_FAILURE_REASONS,
    WorkflowRunService,
)

INSUFFICIENT_INFO_ANSWER = (
    "I do not have enough information in production notes to answer safely."
)
DEFAULT_QA_TOP_K = 5
DEFAULT_QA_PROVIDER_NAME = "openai"
DEFAULT_QA_MODEL = "gpt-4o-mini"


@dataclass
class QACitationResult:
    notion_path: str
    page_id: Optional[str]
    score: float


@dataclass
class QAResult:
    workflow_run_id: int
    status: str
    answer: str
    insufficient_info: bool
    retrieved_chunk_count: int
    citations: List[QACitationResult]
    provider: Optional[str]
    model: Optional[str]
    token_input: Optional[int]
    token_output: Optional[int]


class QAOrchestratorError(Exception):
    def __init__(
        self,
        *,
        error_code: str,
        message: str,
        http_status_code: int,
        failure_reason: str = "UNKNOWN_ERROR",
        workflow_run_id: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.http_status_code = http_status_code
        self.failure_reason = failure_reason
        self.workflow_run_id = workflow_run_id


class QAOrchestrator:
    def __init__(
        self,
        *,
        retriever: ProductionChunkRetriever,
        provider_router: ProviderRouter,
        cost_tracker: CostTracker,
        prompt_template_loader: PromptTemplateLoader,
        workflow_run_service: WorkflowRunService,
    ) -> None:
        self._retriever = retriever
        self._provider_router = provider_router
        self._cost_tracker = cost_tracker
        self._prompt_template_loader = prompt_template_loader
        self._workflow_run_service = workflow_run_service

    async def answer_question(
        self,
        *,
        query: str,
        top_k: int,
        page_ids: Optional[List[str]],
        section_paths: Optional[List[str]],
        source_kinds: Optional[List[str]],
        provider_name: str,
        model: str,
        request_workflow_id: str,
    ) -> QAResult:
        normalized_query = query.strip()
        normalized_provider_name = provider_name.strip()
        normalized_model = model.strip()

        if not normalized_query:
            raise QAOrchestratorError(
                error_code="INVALID_ARGUMENT",
                message="query must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )
        if not normalized_provider_name:
            raise QAOrchestratorError(
                error_code="INVALID_ARGUMENT",
                message="provider_name must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )
        if not normalized_model:
            raise QAOrchestratorError(
                error_code="INVALID_ARGUMENT",
                message="model must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )

        workflow_run = self._workflow_run_service.start_workflow(
            workflow_type="qa",
            metadata_json=json.dumps(
                {
                    "operation": "qa_answer",
                    "query_length": len(normalized_query),
                    "top_k": top_k,
                    "provider_name": normalized_provider_name,
                    "model": normalized_model,
                    "request_workflow_id": request_workflow_id,
                },
                sort_keys=True,
            ),
        )

        prompt_id = PROMPT_ID_QA_ANSWER
        prompt_version: Optional[str] = None
        llm_token_input: Optional[int] = None
        llm_token_output: Optional[int] = None
        estimated_cost: Optional[float] = None
        try:
            prompt_bundle = self._prompt_template_loader.load_bundle(prompt_id)
            prompt_version = prompt_bundle.version
            retrieved_chunks = self._retriever.retrieve(
                query_text=normalized_query,
                top_k=top_k,
                page_ids=page_ids,
                section_paths=section_paths,
                source_kinds=source_kinds,
            )
            citations = self._build_citations(retrieved_chunks)
            if not retrieved_chunks or not citations:
                self._workflow_run_service.mark_workflow_succeeded(
                    workflow_run.id,
                    metadata_json=json.dumps(
                        {
                            "operation": "qa_answer",
                            "insufficient_info": True,
                            "retrieved_chunk_count": len(retrieved_chunks),
                            "citation_count": len(citations),
                            "provider_name": normalized_provider_name,
                            "model": normalized_model,
                            "prompt_id": prompt_id,
                            "prompt_version": prompt_version,
                            "token_input": None,
                            "token_output": None,
                            "estimated_cost": None,
                        },
                        sort_keys=True,
                    ),
                )
                return QAResult(
                    workflow_run_id=workflow_run.id,
                    status="succeeded",
                    answer=INSUFFICIENT_INFO_ANSWER,
                    insufficient_info=True,
                    retrieved_chunk_count=len(retrieved_chunks),
                    citations=citations,
                    provider=None,
                    model=None,
                    token_input=None,
                    token_output=None,
                )

            context_text = self._build_context_text(retrieved_chunks)
            system_message, user_message = prompt_bundle.render_messages(
                variables={
                    "query": normalized_query,
                    "context_text": context_text,
                }
            )
            llm_response = await self._provider_router.route(
                normalized_provider_name,
                LLMRequest(
                    model=normalized_model,
                    messages=[
                        LLMMessage(
                            role="system",
                            content=system_message,
                        ),
                        LLMMessage(
                            role="user",
                            content=user_message,
                        ),
                    ],
                    temperature=0.2,
                    max_tokens=500,
                    metadata={
                        "workflow_id": request_workflow_id,
                        "operation": "qa_answer",
                        "prompt_id": prompt_id,
                        "prompt_version": prompt_version,
                        "provider_name": normalized_provider_name,
                        "model": normalized_model,
                    },
                ),
            )
            llm_token_input = llm_response.token_input
            llm_token_output = llm_response.token_output
            estimated_cost = self._cost_tracker.estimate_llm_cost(
                provider_name=llm_response.provider,
                model=llm_response.model,
                token_input=llm_token_input,
                token_output=llm_token_output,
            )
            answer_text = llm_response.output_text.strip()
            if not answer_text:
                raise QAOrchestratorError(
                    error_code="LLM_OUTPUT_INVALID",
                    message="LLM output is empty",
                    http_status_code=HTTPStatus.BAD_GATEWAY,
                    failure_reason="LLM_OUTPUT_INVALID",
                )

            self._workflow_run_service.mark_workflow_succeeded(
                workflow_run.id,
                metadata_json=json.dumps(
                    {
                        "operation": "qa_answer",
                        "insufficient_info": False,
                        "retrieved_chunk_count": len(retrieved_chunks),
                        "citation_count": len(citations),
                        "provider_name": normalized_provider_name,
                        "model": normalized_model,
                        "prompt_id": prompt_id,
                        "prompt_version": prompt_version,
                        "token_input": llm_token_input,
                        "token_output": llm_token_output,
                        "estimated_cost": estimated_cost,
                    },
                    sort_keys=True,
                ),
            )
            return QAResult(
                workflow_run_id=workflow_run.id,
                status="succeeded",
                answer=answer_text,
                insufficient_info=False,
                retrieved_chunk_count=len(retrieved_chunks),
                citations=citations,
                provider=llm_response.provider,
                model=llm_response.model,
                token_input=llm_response.token_input,
                token_output=llm_response.token_output,
            )
        except QAOrchestratorError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason=exc.failure_reason,
                error_code=exc.error_code,
                provider_name=normalized_provider_name,
                model=normalized_model,
                prompt_id=prompt_id,
                prompt_version=prompt_version,
                token_input=llm_token_input,
                token_output=llm_token_output,
                estimated_cost=estimated_cost,
            )
            raise QAOrchestratorError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=exc.http_status_code,
                failure_reason=exc.failure_reason,
                workflow_run_id=workflow_run.id,
            ) from exc
        except ProviderNotFoundError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason="PROVIDER_NOT_FOUND",
                error_code="PROVIDER_NOT_FOUND",
                provider_name=normalized_provider_name,
                model=normalized_model,
                prompt_id=prompt_id,
                prompt_version=prompt_version,
                token_input=llm_token_input,
                token_output=llm_token_output,
                estimated_cost=estimated_cost,
            )
            raise QAOrchestratorError(
                error_code="PROVIDER_NOT_FOUND",
                message=str(exc),
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="PROVIDER_NOT_FOUND",
                workflow_run_id=workflow_run.id,
            ) from exc
        except (LLMClientError, ProviderRouterError) as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason="LLM_PROVIDER_ERROR",
                error_code="LLM_PROVIDER_ERROR",
                provider_name=normalized_provider_name,
                model=normalized_model,
                prompt_id=prompt_id,
                prompt_version=prompt_version,
                token_input=llm_token_input,
                token_output=llm_token_output,
                estimated_cost=estimated_cost,
            )
            raise QAOrchestratorError(
                error_code="LLM_PROVIDER_ERROR",
                message=f"LLM provider request failed: {exc}",
                http_status_code=HTTPStatus.BAD_GATEWAY,
                failure_reason="LLM_PROVIDER_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc
        except ValueError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason="UNKNOWN_ERROR",
                error_code="INVALID_ARGUMENT",
                provider_name=normalized_provider_name,
                model=normalized_model,
                prompt_id=prompt_id,
                prompt_version=prompt_version,
                token_input=llm_token_input,
                token_output=llm_token_output,
                estimated_cost=estimated_cost,
            )
            raise QAOrchestratorError(
                error_code="INVALID_ARGUMENT",
                message=str(exc),
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc
        except PromptTemplateLoaderError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason="UNKNOWN_ERROR",
                error_code="PROMPT_TEMPLATE_INVALID",
                provider_name=normalized_provider_name,
                model=normalized_model,
                prompt_id=prompt_id,
                prompt_version=prompt_version,
                token_input=llm_token_input,
                token_output=llm_token_output,
                estimated_cost=estimated_cost,
            )
            raise QAOrchestratorError(
                error_code="PROMPT_TEMPLATE_INVALID",
                message=f"Prompt template load failed: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc
        except Exception as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason="UNKNOWN_ERROR",
                error_code="QA_WORKFLOW_FAILED",
                provider_name=normalized_provider_name,
                model=normalized_model,
                prompt_id=prompt_id,
                prompt_version=prompt_version,
                token_input=llm_token_input,
                token_output=llm_token_output,
                estimated_cost=estimated_cost,
            )
            raise QAOrchestratorError(
                error_code="QA_WORKFLOW_FAILED",
                message=f"QA workflow failed: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc

    def _build_context_text(self, retrieved_chunks: List[RetrievedChunk]) -> str:
        context_lines = []
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            context_lines.append(
                f"[C{idx}] path={chunk.notion_path} score={chunk.score:.4f}\n{chunk.chunk_text}"
            )
        return "\n\n".join(context_lines)

    def _build_citations(self, retrieved_chunks: List[RetrievedChunk]) -> List[QACitationResult]:
        citations: List[QACitationResult] = []
        seen_paths = set()
        for chunk in retrieved_chunks:
            path = chunk.notion_path.strip()
            if not path or path in seen_paths:
                continue
            seen_paths.add(path)
            citations.append(
                QACitationResult(
                    notion_path=path,
                    page_id=chunk.notion_page_id,
                    score=round(chunk.score, 6),
                )
            )
        return citations

    def _mark_failed_workflow(
        self,
        *,
        workflow_run_id: int,
        failure_reason: str,
        error_code: str,
        provider_name: str,
        model: str,
        prompt_id: str,
        prompt_version: Optional[str],
        token_input: Optional[int] = None,
        token_output: Optional[int] = None,
        estimated_cost: Optional[float] = None,
    ) -> None:
        normalized_failure_reason = self._normalize_failure_reason(failure_reason)
        self._workflow_run_service.mark_workflow_failed(
            workflow_run_id,
            failure_reason=normalized_failure_reason,
            metadata_json=json.dumps(
                {
                    "operation": "qa_answer",
                    "error_code": error_code,
                    "provider_name": provider_name,
                    "model": model,
                    "prompt_id": prompt_id,
                    "prompt_version": prompt_version,
                    "token_input": token_input,
                    "token_output": token_output,
                    "estimated_cost": estimated_cost,
                },
                sort_keys=True,
            ),
        )

    def _normalize_failure_reason(self, failure_reason: str) -> str:
        normalized = failure_reason.strip().upper()
        if normalized in STANDARD_FAILURE_REASONS:
            return normalized
        return "UNKNOWN_ERROR"
