from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from time import perf_counter
from typing import Optional

from src.db.unit_of_work import UnitOfWorkFactory
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
from src.repositories import (
    ChangeRequestRepository,
    NotionPageRepository,
    SourceDocumentRepository,
)
from src.services import (
    CostTracker,
    DuplicateKnowledgeChecker,
    DuplicateMatch,
    PROMPT_ID_SUPPLEMENT_PROPOSAL,
    PROMPT_SAFETY_VERSION,
    PromptTemplateLoader,
    PromptTemplateLoaderError,
    STANDARD_FAILURE_REASONS,
    WorkflowRunAuditUpdateError,
    WorkflowRunService,
    build_supplement_target_path,
    format_untrusted_prompt_block,
    is_safe_supplement_target_path,
    normalize_notion_path,
    normalize_supplement_target_path,
)
from src.services.latency_evidence import LatencyEvidence, elapsed_ms
from src.services.screenshot_quality import (
    ScreenshotSourceSnapshot,
    build_screenshot_source_snapshot,
    detect_screenshot_language,
    validate_screenshot_proposal_with_title_fallback,
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
    target_notion_page_id: Optional[str]
    target_notion_path: Optional[str]
    provider: Optional[str]
    model: Optional[str]
    token_input: Optional[int]
    token_output: Optional[int]
    latency_metadata: dict[str, float]
    title_fallback_used: bool = False


class SupplementProposeError(Exception):
    def __init__(
        self,
        *,
        error_code: str,
        message: str,
        http_status_code: int,
        failure_reason: str = "UNKNOWN_ERROR",
        workflow_run_id: Optional[int] = None,
        metadata: Optional[dict[str, object]] = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.http_status_code = http_status_code
        self.failure_reason = failure_reason
        self.workflow_run_id = workflow_run_id
        self.metadata = dict(metadata or {})


class SupplementProposeOrchestrator:
    def __init__(
        self,
        *,
        provider_router: ProviderRouter,
        cost_tracker: CostTracker,
        prompt_template_loader: PromptTemplateLoader,
        source_document_repository: SourceDocumentRepository,
        notion_page_repository: NotionPageRepository,
        change_request_repository: ChangeRequestRepository,
        unit_of_work_factory: UnitOfWorkFactory,
        duplicate_checker: DuplicateKnowledgeChecker,
        workflow_run_service: WorkflowRunService,
    ) -> None:
        self._provider_router = provider_router
        self._cost_tracker = cost_tracker
        self._prompt_template_loader = prompt_template_loader
        self._source_document_repository = source_document_repository
        self._notion_page_repository = notion_page_repository
        self._change_request_repository = change_request_repository
        self._unit_of_work_factory = unit_of_work_factory
        self._duplicate_checker = duplicate_checker
        self._workflow_run_service = workflow_run_service

    async def propose_change_request(
        self,
        *,
        source_document_id: int,
        provider_name: str,
        model: str,
        request_workflow_id: str,
        target_notion_page_id: Optional[str] = None,
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
        normalized_target_notion_page_id = (
            target_notion_page_id.strip() if target_notion_page_id is not None else None
        )
        if target_notion_page_id is not None and not normalized_target_notion_page_id:
            raise SupplementProposeError(
                error_code="INVALID_ARGUMENT",
                message="target_notion_page_id must not be empty when provided",
                http_status_code=HTTPStatus.BAD_REQUEST,
            )

        business_started = perf_counter()
        workflow_run = self._workflow_run_service.start_workflow(
            workflow_type="supplement",
            metadata_json=json.dumps(
                {
                    "operation": "propose_change_request",
                    "source_document_id": source_document_id,
                    "target_notion_page_id": normalized_target_notion_page_id,
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
        title_fallback_used = False
        latency = LatencyEvidence()
        target_page_path: Optional[str] = None
        allowed_target_path: Optional[str] = None
        source_snapshot: Optional[ScreenshotSourceSnapshot] = None
        validation_diagnostics: Optional[dict[str, object]] = None
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
            if source_document.source_type == "screenshot":
                source_snapshot = build_screenshot_source_snapshot(
                    source_document.raw_text
                )

            target_page_db_id: Optional[int] = None
            if normalized_target_notion_page_id is not None:
                target_page = self._notion_page_repository.get_by_notion_page_id(
                    normalized_target_notion_page_id
                )
                if target_page is None:
                    raise SupplementProposeError(
                        error_code="NOTION_PAGE_NOT_FOUND",
                        message=(
                            "Target Notion page is not found: "
                            f"target_notion_page_id={normalized_target_notion_page_id}"
                        ),
                        http_status_code=HTTPStatus.NOT_FOUND,
                        failure_reason="NOTION_PAGE_NOT_FOUND",
                    )
                target_page_db_id = int(target_page.id)
                target_page_path = normalize_notion_path(target_page.notion_path)
                allowed_target_path = build_supplement_target_path(
                    target_page_path=target_page_path or ""
                )
                if target_page_path is None or allowed_target_path is None:
                    raise SupplementProposeError(
                        error_code="NOTION_PAGE_NOT_FOUND",
                        message="Target Notion page has no usable canonical path",
                        http_status_code=HTTPStatus.NOT_FOUND,
                        failure_reason="NOTION_PAGE_NOT_FOUND",
                    )

            duplicate_match = self._check_duplicate(source_document.raw_text)

            provider = None
            model_name = None
            if duplicate_match is None:
                system_message, user_message = prompt_bundle.render_messages(
                    variables={
                        "source_type": format_untrusted_prompt_block(
                            label="SOURCE_TYPE",
                            value=source_document.source_type,
                        ),
                        "source_display_name": format_untrusted_prompt_block(
                            label="SOURCE_DISPLAY_NAME",
                            value=source_document.source_display_name,
                        ),
                        "selected_target_path": format_untrusted_prompt_block(
                            label="SELECTED_TARGET_PATH",
                            value=allowed_target_path or "NONE (no selected target page)",
                        ),
                        "source_text": format_untrusted_prompt_block(
                            label="SOURCE_TEXT",
                            value=(
                                source_snapshot.text
                                if source_snapshot is not None
                                else source_document.raw_text
                            ),
                        ),
                        "source_language": detect_screenshot_language(
                            source_snapshot.text
                            if source_snapshot is not None
                            else source_document.raw_text
                        ).instruction
                        if source_document.source_type == "screenshot"
                        else "the main language of the source text",
                    }
                )
                llm_started = perf_counter()
                try:
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
                                "prompt_safety_version": PROMPT_SAFETY_VERSION,
                                "provider_name": normalized_provider_name,
                                "model": normalized_model,
                            },
                        ),
                    )
                finally:
                    latency.add(llm_ms=elapsed_ms(llm_started))
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
                    target_page_path=target_page_path,
                )
                if source_document.source_type == "screenshot":
                    validation_result = validate_screenshot_proposal_with_title_fallback(
                        proposal=proposal,
                        source_text=(
                            source_snapshot.text
                            if source_snapshot is not None
                            else source_document.raw_text
                        ),
                        source_snapshot=source_snapshot,
                    )
                    proposal = validation_result.proposal
                    title_fallback_used = validation_result.title_fallback_used
                    validation_diagnostics = (
                        validation_result.diagnostics.as_dict()
                        if validation_result.diagnostics is not None
                        else None
                    )
                duplicate_match = self._check_duplicate(
                    self._build_duplicate_candidate_from_proposal(proposal)
                )
                if duplicate_match is not None:
                    proposal = self._build_duplicate_reference_proposal(
                        source_type=source_document.source_type,
                        source_display_name=source_document.source_display_name,
                        duplicate_match=duplicate_match,
                        target_path=allowed_target_path,
                    )
            else:
                proposal = self._build_duplicate_reference_proposal(
                    source_type=source_document.source_type,
                    source_display_name=source_document.source_display_name,
                    duplicate_match=duplicate_match,
                    target_path=allowed_target_path,
                )

            persist_started = perf_counter()
            with self._unit_of_work_factory() as unit_of_work:
                change_request = unit_of_work.change_requests.create_change_request(
                    source_document_id=source_document.id,
                    target_notion_page_id=target_page_db_id,
                    status=CHANGE_REQUEST_STATUS_PENDING,
                    proposal_json=json.dumps(proposal.model_dump(), sort_keys=True),
                    failure_reason=None,
                )
                change_request_id = int(change_request.id)
                change_request_status = change_request.status
            latency.add(persist_ms=elapsed_ms(persist_started))
            latency.add(total_business_ms=elapsed_ms(business_started))

            self._workflow_run_service.mark_workflow_succeeded(
                workflow_run.id,
                metadata_json=json.dumps(
                    {
                        "operation": "propose_change_request",
                        "change_request_id": change_request_id,
                        "source_document_id": source_document.id,
                        "change_request_status": CHANGE_REQUEST_STATUS_PENDING,
                        "target_notion_page_id": normalized_target_notion_page_id,
                        "duplicate_detected": duplicate_match is not None,
                        "duplicate_notion_path": (
                            duplicate_match.notion_path if duplicate_match is not None else None
                        ),
                        "provider_name": normalized_provider_name,
                        "model": normalized_model,
                        "prompt_id": prompt_id,
                        "prompt_version": prompt_version,
                        "prompt_safety_version": PROMPT_SAFETY_VERSION,
                        "token_input": token_input,
                        "token_output": token_output,
                        "estimated_cost": estimated_cost,
                        "title_fallback_used": title_fallback_used,
                        **(validation_diagnostics or {}),
                        **latency.as_dict(),
                    },
                    sort_keys=True,
                ),
            )

            return SupplementProposeResult(
                workflow_run_id=workflow_run.id,
                status="succeeded",
                change_request_id=change_request_id,
                change_request_status=change_request_status,
                source_document_id=source_document.id,
                duplicate_detected=duplicate_match is not None,
                duplicate_notion_path=(
                    duplicate_match.notion_path if duplicate_match is not None else None
                ),
                target_notion_page_id=normalized_target_notion_page_id,
                target_notion_path=target_page_path,
                provider=provider,
                model=model_name,
                token_input=token_input,
                token_output=token_output,
                latency_metadata=latency.as_dict(),
                title_fallback_used=title_fallback_used,
            )
        except WorkflowRunAuditUpdateError:
            raise
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
                metadata=exc.metadata,
            ) from exc
        except SupplementProposalValidationError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason="LLM_OUTPUT_INVALID",
                error_code="LLM_OUTPUT_INVALID",
                source_document_id=source_document_id,
                failure_stage="proposal_validation",
                validation_field=exc.field,
                latency_metadata=latency.as_dict(),
                validation_diagnostics=exc.diagnostics,
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
                metadata={
                    "source_document_id": source_document_id,
                    **exc.diagnostics,
                    "proposal_workflow_run_id": workflow_run.id,
                    "failure_stage": "proposal_validation",
                    "validation_field": exc.field,
                    **latency.as_dict(),
                },
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
        target_page_path: Optional[str],
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
        if not is_safe_supplement_target_path(
            target_path=proposal.target_path,
            target_page_path=target_page_path,
        ):
            raise SupplementProposalValidationError(
                "LLM output target_path must equal the selected page's AI Supplement Zone"
            )
        normalized_target_path = normalize_supplement_target_path(
            target_path=proposal.target_path,
            target_page_path=target_page_path,
        )
        if normalized_target_path is None:
            raise SupplementProposalValidationError(
                "LLM output target_path must equal the selected page's AI Supplement Zone"
            )
        return proposal.model_copy(update={"target_path": normalized_target_path})

    def _build_duplicate_reference_proposal(
        self,
        *,
        source_type: str,
        source_display_name: str,
        duplicate_match: DuplicateMatch,
        target_path: Optional[str] = None,
    ) -> SupplementProposalSchema:
        return SupplementProposalSchema.model_validate(
            {
                "title": f"Duplicate knowledge reference ({source_display_name})",
                "target_path": target_path or duplicate_match.notion_path,
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
                "citations": [
                    {"notion_path": duplicate_match.notion_path},
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
        source_document_id: Optional[int] = None,
        failure_stage: Optional[str] = None,
        validation_field: Optional[str] = None,
        latency_metadata: Optional[dict[str, float]] = None,
        validation_diagnostics: Optional[dict[str, object]] = None,
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
                    "source_document_id": source_document_id,
                    "failure_stage": failure_stage,
                    "validation_field": validation_field,
                    "provider_name": provider_name,
                    "model": model,
                    "prompt_id": prompt_id,
                    "prompt_version": prompt_version,
                    "prompt_safety_version": PROMPT_SAFETY_VERSION,
                    "token_input": token_input,
                    "token_output": token_output,
                    "estimated_cost": estimated_cost,
                    **(validation_diagnostics or {}),
                    **(latency_metadata or {}),
                },
                sort_keys=True,
            ),
        )
