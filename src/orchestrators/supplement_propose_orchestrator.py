from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from src.orchestrators.supplement_proposal_schema import (
    SupplementProposalSchema,
    SupplementProposalValidationError,
    parse_supplement_proposal_json,
)
from src.providers import (
    LLMClientError,
    LLMMessage,
    LLMRequest,
    ProviderNotFoundError,
    ProviderRouter,
    ProviderRouterError,
)
from src.repositories import ChangeRequestRepository, SourceDocumentRepository
from src.services import (
    CostTracker,
    DuplicateKnowledgeChecker,
    DuplicateMatch,
    PROMPT_ID_SUPPLEMENT_PROPOSAL,
    PromptTemplateLoader,
    PromptTemplateLoaderError,
    STANDARD_FAILURE_REASONS,
    WorkflowRunService,
)

CHANGE_REQUEST_STATUS_PENDING = "pending"
DEFAULT_SUPPLEMENT_PROVIDER_NAME = "openai"
DEFAULT_SUPPLEMENT_MODEL = "gpt-4o-mini"


@dataclass
class SupplementProposeResult:
    workflow_run_id: int
    status: str
    change_request_id: int
    change_request_status: str
    source_document_id: int
    duplicate_detected: bool
    duplicate_notion_path: Optional[str]
    provider: Optional[str]
    model: Optional[str]
    token_input: Optional[int]
    token_output: Optional[int]


class SupplementProposeError(Exception):
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


class SupplementProposeOrchestrator:
    def __init__(
        self,
        *,
        provider_router: ProviderRouter,
        cost_tracker: CostTracker,
        prompt_template_loader: PromptTemplateLoader,
        source_document_repository: SourceDocumentRepository,
        change_request_repository: ChangeRequestRepository,
        duplicate_checker: DuplicateKnowledgeChecker,
        workflow_run_service: WorkflowRunService,
    ) -> None:
        self._provider_router = provider_router
        self._cost_tracker = cost_tracker
        self._prompt_template_loader = prompt_template_loader
        self._source_document_repository = source_document_repository
        self._change_request_repository = change_request_repository
        self._duplicate_checker = duplicate_checker
        self._workflow_run_service = workflow_run_service

    async def propose_change_request(
        self,
        *,
        source_document_id: int,
        provider_name: str,
        model: str,
        request_workflow_id: str,
        target_notion_page_id: Optional[int] = None,
    ) -> SupplementProposeResult:
        if source_document_id <= 0:
            raise SupplementProposeError(
                error_code="INVALID_ARGUMENT",
                message="source_document_id must be positive",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )

        normalized_provider_name = provider_name.strip()
        normalized_model = model.strip()
        if not normalized_provider_name:
            raise SupplementProposeError(
                error_code="INVALID_ARGUMENT",
                message="provider_name must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )
        if not normalized_model:
            raise SupplementProposeError(
                error_code="INVALID_ARGUMENT",
                message="model must not be empty",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )
        if target_notion_page_id is not None and target_notion_page_id <= 0:
            raise SupplementProposeError(
                error_code="INVALID_ARGUMENT",
                message="target_notion_page_id must be positive when provided",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )

        workflow_run = self._workflow_run_service.start_workflow(
            workflow_type="supplement",
            metadata_json=json.dumps(
                {
                    "operation": "propose_change_request",
                    "source_document_id": source_document_id,
                    "target_notion_page_id": target_notion_page_id,
                    "provider_name": normalized_provider_name,
                    "model": normalized_model,
                    "request_workflow_id": request_workflow_id,
                },
                sort_keys=True,
            ),
        )

        prompt_id = PROMPT_ID_SUPPLEMENT_PROPOSAL
        prompt_version: Optional[str] = None
        token_input: Optional[int] = None
        token_output: Optional[int] = None
        estimated_cost: Optional[float] = None
        try:
            prompt_bundle = self._prompt_template_loader.load_bundle(prompt_id)
            prompt_version = prompt_bundle.version
            source_document = self._source_document_repository.get_source_document_by_id(
                source_document_id
            )
            if source_document is None:
                raise SupplementProposeError(
                    error_code="SOURCE_DOCUMENT_NOT_FOUND",
                    message=(
                        "Source document is not found: "
                        f"source_document_id={source_document_id}"
                    ),
                    http_status_code=HTTPStatus.NOT_FOUND,
                )

            duplicate_match = self._check_duplicate(source_document.raw_text)

            provider = None
            model_name = None
            if duplicate_match is None:
                system_message, user_message = prompt_bundle.render_messages(
                    variables={
                        "source_type": source_document.source_type,
                        "source_display_name": source_document.source_display_name,
                        "source_text": source_document.raw_text,
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
                        max_tokens=900,
                        metadata={
                            "workflow_id": request_workflow_id,
                            "operation": "propose_change_request",
                            "prompt_id": prompt_id,
                            "prompt_version": prompt_version,
                            "provider_name": normalized_provider_name,
                            "model": normalized_model,
                        },
                    ),
                )
                provider = llm_response.provider
                model_name = llm_response.model
                token_input = llm_response.token_input
                token_output = llm_response.token_output
                estimated_cost = self._cost_tracker.estimate_llm_cost(
                    provider_name=llm_response.provider,
                    model=llm_response.model,
                    token_input=token_input,
                    token_output=token_output,
                )
                proposal = self._validate_llm_output(
                    llm_output=llm_response.output_text,
                    source_type=source_document.source_type,
                    source_display_name=source_document.source_display_name,
                )
                duplicate_match = self._check_duplicate(
                    self._build_duplicate_candidate_from_proposal(proposal)
                )
                if duplicate_match is not None:
                    proposal = self._build_duplicate_reference_proposal(
                        source_type=source_document.source_type,
                        source_display_name=source_document.source_display_name,
                        duplicate_match=duplicate_match,
                    )
            else:
                proposal = self._build_duplicate_reference_proposal(
                    source_type=source_document.source_type,
                    source_display_name=source_document.source_display_name,
                    duplicate_match=duplicate_match,
                )

            change_request = self._change_request_repository.create_change_request(
                source_document_id=source_document.id,
                target_notion_page_id=target_notion_page_id,
                status=CHANGE_REQUEST_STATUS_PENDING,
                proposal_json=json.dumps(proposal.model_dump(), sort_keys=True),
                failure_reason=None,
            )

            self._workflow_run_service.mark_workflow_succeeded(
                workflow_run.id,
                metadata_json=json.dumps(
                    {
                        "operation": "propose_change_request",
                        "change_request_id": change_request.id,
                        "source_document_id": source_document.id,
                        "change_request_status": CHANGE_REQUEST_STATUS_PENDING,
                        "duplicate_detected": duplicate_match is not None,
                        "duplicate_notion_path": (
                            duplicate_match.notion_path if duplicate_match is not None else None
                        ),
                        "provider_name": normalized_provider_name,
                        "model": normalized_model,
                        "prompt_id": prompt_id,
                        "prompt_version": prompt_version,
                        "token_input": token_input,
                        "token_output": token_output,
                        "estimated_cost": estimated_cost,
                    },
                    sort_keys=True,
                ),
            )

            return SupplementProposeResult(
                workflow_run_id=workflow_run.id,
                status="succeeded",
                change_request_id=change_request.id,
                change_request_status=change_request.status,
                source_document_id=source_document.id,
                duplicate_detected=duplicate_match is not None,
                duplicate_notion_path=(
                    duplicate_match.notion_path if duplicate_match is not None else None
                ),
                provider=provider,
                model=model_name,
                token_input=token_input,
                token_output=token_output,
            )
        except SupplementProposeError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason=exc.failure_reason,
                error_code=exc.error_code,
                provider_name=normalized_provider_name,
                model=normalized_model,
                prompt_id=prompt_id,
                prompt_version=prompt_version,
                token_input=token_input,
                token_output=token_output,
                estimated_cost=estimated_cost,
            )
            raise SupplementProposeError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=exc.http_status_code,
                failure_reason=exc.failure_reason,
                workflow_run_id=workflow_run.id,
            ) from exc
        except SupplementProposalValidationError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason="LLM_OUTPUT_INVALID",
                error_code="LLM_OUTPUT_INVALID",
                provider_name=normalized_provider_name,
                model=normalized_model,
                prompt_id=prompt_id,
                prompt_version=prompt_version,
                token_input=token_input,
                token_output=token_output,
                estimated_cost=estimated_cost,
            )
            raise SupplementProposeError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=HTTPStatus.BAD_GATEWAY,
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
                token_input=token_input,
                token_output=token_output,
                estimated_cost=estimated_cost,
            )
            raise SupplementProposeError(
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
                token_input=token_input,
                token_output=token_output,
                estimated_cost=estimated_cost,
            )
            raise SupplementProposeError(
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
                token_input=token_input,
                token_output=token_output,
                estimated_cost=estimated_cost,
            )
            raise SupplementProposeError(
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
                token_input=token_input,
                token_output=token_output,
                estimated_cost=estimated_cost,
            )
            raise SupplementProposeError(
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
                error_code="SUPPLEMENT_PROPOSAL_FAILED",
                provider_name=normalized_provider_name,
                model=normalized_model,
                prompt_id=prompt_id,
                prompt_version=prompt_version,
                token_input=token_input,
                token_output=token_output,
                estimated_cost=estimated_cost,
            )
            raise SupplementProposeError(
                error_code="SUPPLEMENT_PROPOSAL_FAILED",
                message=f"Failed to propose supplement change request: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc

    def _validate_llm_output(
        self,
        *,
        llm_output: str,
        source_type: str,
        source_display_name: str,
    ) -> SupplementProposalSchema:
        proposal = parse_supplement_proposal_json(llm_output)
        if proposal.source.source_type != source_type:
            raise SupplementProposalValidationError(
                "LLM output source.source_type does not match input source"
            )
        if proposal.source.source_display_name != source_display_name:
            raise SupplementProposalValidationError(
                "LLM output source.source_display_name does not match input source"
            )
        return proposal

    def _build_duplicate_reference_proposal(
        self,
        *,
        source_type: str,
        source_display_name: str,
        duplicate_match: DuplicateMatch,
    ) -> SupplementProposalSchema:
        return SupplementProposalSchema.model_validate(
            {
                "title": f"Duplicate knowledge reference ({source_display_name})",
                "target_path": duplicate_match.notion_path,
                "source": {
                    "source_type": source_type,
                    "source_display_name": source_display_name,
                },
                "summary": (
                    "This source appears to duplicate existing knowledge. "
                    f"Use citation path: {duplicate_match.notion_path}"
                ),
                "concepts": ["duplicate knowledge reference"],
                "notes": [
                    "Do not rewrite the same content.",
                    f"Cite existing path: {duplicate_match.notion_path}",
                ],
            }
        )

    def _build_duplicate_candidate_from_proposal(
        self,
        proposal: SupplementProposalSchema,
    ) -> str:
        parts = [proposal.title, proposal.summary]
        parts.extend(proposal.concepts)
        parts.extend(proposal.notes)
        return "\n".join(parts)

    def _check_duplicate(self, candidate_text: str) -> Optional[DuplicateMatch]:
        check_result = self._duplicate_checker.check_duplicate(candidate_text=candidate_text)
        return check_result.matched

    def _normalize_failure_reason(self, failure_reason: str) -> str:
        normalized = failure_reason.strip().upper()
        if normalized in STANDARD_FAILURE_REASONS:
            return normalized
        return "UNKNOWN_ERROR"

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
        self._workflow_run_service.mark_workflow_failed(
            workflow_run_id,
            failure_reason=self._normalize_failure_reason(failure_reason),
            metadata_json=json.dumps(
                {
                    "operation": "propose_change_request",
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
