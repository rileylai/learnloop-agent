from __future__ import annotations

import json
import shlex
from dataclasses import asdict, dataclass
from http import HTTPStatus
from typing import Optional

from src.observability.redaction import sanitize_sensitive_text
from src.queue import QueueClient, QueueRetryPolicy
from src.orchestrators.telegram_ingestion_orchestrator import (
    TelegramDocumentAttachment,
    TelegramIngestionError,
    TelegramIngestionOrchestrator,
    TelegramPhotoAttachment,
)
from src.orchestrators.telegram_qa_orchestrator import (
    TelegramQAError,
    TelegramQAOrchestrator,
)
from src.orchestrators.telegram_review_orchestrator import (
    TelegramReviewError,
    TelegramReviewOrchestrator,
)
from src.orchestrators.telegram_page_orchestrator import TelegramPageOrchestrator
from src.services import (
    STANDARD_FAILURE_REASONS,
    WorkflowRunAuditUpdateError,
    WorkflowRunService,
    TrustBoundaryError,
    TrustBoundaryService,
    TelegramUpdateClaim,
    TelegramUpdateIdempotencyError,
    TelegramUpdateIdempotencyService,
)
from src.tools import ToolContext, ToolRegistry

TELEGRAM_BOT_TOOL_NAME = "telegram_bot"


@dataclass
class TelegramGatewayResult:
    workflow_run_id: Optional[int]
    status: str
    handled: bool
    command: Optional[str]
    reply_text: Optional[str]
    telegram_message_id: Optional[int]
    skipped_reason: Optional[str]
    source_document_id: Optional[int]
    change_request_id: Optional[int]
    source_type: Optional[str]
    target_notion_page_id: Optional[str]
    qa_workflow_run_id: Optional[int]
    insufficient_info: Optional[bool]
    citations: list[str]
    review_workflow_run_id: Optional[int]
    review_action: Optional[str]
    change_request_status: Optional[str]


class TelegramGatewayError(Exception):
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


class TelegramGatewayOrchestrator:
    def __init__(
        self,
        *,
        tool_registry: ToolRegistry,
        workflow_run_service: WorkflowRunService,
        telegram_ingestion_orchestrator: Optional[TelegramIngestionOrchestrator] = None,
        telegram_qa_orchestrator: Optional[TelegramQAOrchestrator] = None,
        telegram_review_orchestrator: Optional[TelegramReviewOrchestrator] = None,
        telegram_page_orchestrator: Optional[TelegramPageOrchestrator] = None,
        trust_boundary: Optional[TrustBoundaryService] = None,
        update_idempotency_service: Optional[TelegramUpdateIdempotencyService] = None,
        queue_client: Optional[QueueClient] = None,
    ) -> None:
        self._tool_registry = tool_registry
        self._workflow_run_service = workflow_run_service
        self._telegram_ingestion_orchestrator = telegram_ingestion_orchestrator
        self._telegram_qa_orchestrator = telegram_qa_orchestrator
        self._telegram_review_orchestrator = telegram_review_orchestrator
        self._telegram_page_orchestrator = telegram_page_orchestrator
        self._trust_boundary = trust_boundary
        self._update_idempotency_service = update_idempotency_service
        self._queue_client = queue_client

    async def handle_webhook(
        self,
        *,
        update_id: Optional[int],
        chat_id: Optional[str],
        text: Optional[str],
        caption: Optional[str],
        document: Optional[TelegramDocumentAttachment],
        photos: list[TelegramPhotoAttachment],
        request_workflow_id: str,
    ) -> TelegramGatewayResult:
        self._require_allowed_chat(chat_id)
        claim = self._claim_update(update_id)
        if claim is not None and not claim.owner:
            return self._replay_or_report_duplicate(claim)

        return await self._process_claimed_webhook(
            update_id=update_id,
            chat_id=chat_id,
            text=text,
            caption=caption,
            document=document,
            photos=photos,
            request_workflow_id=request_workflow_id,
        )

    async def handle_claimed_webhook(
        self,
        *,
        update_id: Optional[int],
        chat_id: Optional[str],
        text: Optional[str],
        caption: Optional[str],
        document: Optional[TelegramDocumentAttachment],
        photos: list[TelegramPhotoAttachment],
        request_workflow_id: str,
    ) -> TelegramGatewayResult:
        """Process work after the API route has claimed the update ledger."""

        self._require_allowed_chat(chat_id)
        return await self._process_claimed_webhook(
            update_id=update_id,
            chat_id=chat_id,
            text=text,
            caption=caption,
            document=document,
            photos=photos,
            request_workflow_id=request_workflow_id,
        )

    async def enqueue_webhook(
        self,
        *,
        update_id: Optional[int],
        chat_id: Optional[str],
        text: Optional[str],
        caption: Optional[str],
        document: Optional[TelegramDocumentAttachment],
        photos: list[TelegramPhotoAttachment],
        request_workflow_id: str,
    ) -> TelegramGatewayResult:
        """Claim and enqueue a Telegram update, returning without long work."""

        self._require_allowed_chat(chat_id)
        claim = self._claim_update(update_id)
        if claim is not None and not claim.owner:
            return self._replay_or_report_duplicate(claim)

        if self._queue_client is None:
            return await self._process_claimed_webhook(
                update_id=update_id,
                chat_id=chat_id,
                text=text,
                caption=caption,
                document=document,
                photos=photos,
                request_workflow_id=request_workflow_id,
            )

        from src.worker.telegram import process_telegram_webhook_job

        retry_policy = QueueRetryPolicy(max_retries=2, retry_intervals=(5, 30))
        try:
            self._queue_client.enqueue(
                queue_name="telegram",
                function=process_telegram_webhook_job,
                args=(
                    update_id,
                    chat_id,
                    text,
                    caption,
                    asdict(document) if document is not None else None,
                    [asdict(photo) for photo in photos],
                    request_workflow_id,
                ),
                description="Process one Telegram webhook update",
                retry_policy=retry_policy,
            )
        except Exception as exc:
            error = TelegramGatewayError(
                error_code="TELEGRAM_QUEUE_UNAVAILABLE",
                message="Telegram background queue is unavailable",
                http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                failure_reason="TELEGRAM_QUEUE_UNAVAILABLE",
            )
            self._mark_update_failed(update_id, error)
            raise error from exc

        return TelegramGatewayResult(
            workflow_run_id=None,
            status="running",
            handled=False,
            command=None,
            reply_text=None,
            telegram_message_id=None,
            skipped_reason="QUEUED",
            source_document_id=None,
            change_request_id=None,
            source_type=None,
            target_notion_page_id=None,
            qa_workflow_run_id=None,
            insufficient_info=None,
            citations=[],
            review_workflow_run_id=None,
            review_action=None,
            change_request_status=None,
        )

    async def _process_claimed_webhook(
        self,
        *,
        update_id: Optional[int],
        chat_id: Optional[str],
        text: Optional[str],
        caption: Optional[str],
        document: Optional[TelegramDocumentAttachment],
        photos: list[TelegramPhotoAttachment],
        request_workflow_id: str,
    ) -> TelegramGatewayResult:

        try:
            result = await self._handle_new_webhook(
                update_id=update_id,
                chat_id=chat_id,
                text=text,
                caption=caption,
                document=document,
                photos=photos,
                request_workflow_id=request_workflow_id,
            )
        except TelegramGatewayError as exc:
            self._mark_update_failed(update_id, exc)
            raise
        except WorkflowRunAuditUpdateError as exc:
            self._mark_update_failed(
                update_id,
                TelegramGatewayError(
                    error_code=exc.error_code,
                    message="Telegram workflow audit update failed",
                    http_status_code=exc.http_status_code,
                    failure_reason=exc.failure_reason,
                    workflow_run_id=exc.workflow_run_id,
                ),
            )
            raise
        except Exception as exc:
            self._mark_update_failed(
                update_id,
                TelegramGatewayError(
                    error_code="TELEGRAM_GATEWAY_FAILED",
                    message="Telegram gateway workflow failed",
                    http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    failure_reason="UNKNOWN_ERROR",
                ),
            )
            raise

        if self._update_idempotency_service is not None:
            try:
                self._update_idempotency_service.mark_succeeded(
                    update_id,
                    workflow_run_id=result.workflow_run_id,
                    result=asdict(result),
                )
            except Exception as exc:
                raise TelegramGatewayError(
                    error_code="TELEGRAM_UPDATE_LEDGER_FAILED",
                    message="Telegram update ledger could not be completed",
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                    failure_reason="TELEGRAM_UPDATE_LEDGER_FAILED",
                    workflow_run_id=result.workflow_run_id,
                ) from exc
        return result

    async def _handle_new_webhook(
        self,
        *,
        update_id: Optional[int],
        chat_id: Optional[str],
        text: Optional[str],
        caption: Optional[str],
        document: Optional[TelegramDocumentAttachment],
        photos: list[TelegramPhotoAttachment],
        request_workflow_id: str,
    ) -> TelegramGatewayResult:
        workflow_run = self._workflow_run_service.start_workflow(
            workflow_type="telegram",
            metadata_json=json.dumps(
                {
                    "operation": "telegram_webhook",
                    "update_id": update_id,
                    "chat_id": chat_id,
                    "request_workflow_id": request_workflow_id,
                    "has_document": document is not None,
                    "photo_count": len(photos),
                },
                sort_keys=True,
            ),
        )

        try:
            normalized_text = (text or "").strip()
            normalized_caption = (caption or "").strip()
            normalized_input_text = normalized_text or normalized_caption
            normalized_chat_id = (chat_id or "").strip()
            has_media = (document is not None) or bool(photos)

            if not normalized_chat_id or (not normalized_input_text and not has_media):
                skipped_reason = "NO_TEXT_MESSAGE"
                self._workflow_run_service.mark_workflow_succeeded(
                    workflow_run.id,
                    metadata_json=json.dumps(
                        {
                            "operation": "telegram_webhook",
                            "handled": False,
                            "skipped_reason": skipped_reason,
                        },
                        sort_keys=True,
                    ),
                )
                return TelegramGatewayResult(
                    workflow_run_id=workflow_run.id,
                    status="succeeded",
                    handled=False,
                    command=None,
                    reply_text=None,
                    telegram_message_id=None,
                    skipped_reason=skipped_reason,
                    source_document_id=None,
                    change_request_id=None,
                    source_type=None,
                    target_notion_page_id=None,
                    qa_workflow_run_id=None,
                    insufficient_info=None,
                    citations=[],
                    review_workflow_run_id=None,
                    review_action=None,
                    change_request_status=None,
                )

            command = self._parse_command(normalized_input_text)
            source_document_id: Optional[int] = None
            change_request_id: Optional[int] = None
            source_type: Optional[str] = None
            target_notion_page_id: Optional[str] = None
            qa_workflow_run_id: Optional[int] = None
            insufficient_info: Optional[bool] = None
            citations: list[str] = []
            review_workflow_run_id: Optional[int] = None
            review_action: Optional[str] = None
            change_request_status: Optional[str] = None
            if command == "health":
                reply_text = self._build_reply_for_command(command)
            elif command == "help":
                reply_text = self._build_reply_for_command(command)
            elif command == "pages":
                if self._telegram_page_orchestrator is None:
                    raise TelegramGatewayError(
                        error_code="TELEGRAM_PAGES_NOT_CONFIGURED",
                        message="Telegram page orchestrator is not configured",
                        http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        failure_reason="UNKNOWN_ERROR",
                    )
                pages_result = self._telegram_page_orchestrator.list_pages()
                reply_text = pages_result.reply_text
            elif command == "ask":
                if self._telegram_qa_orchestrator is None:
                    raise TelegramGatewayError(
                        error_code="TELEGRAM_QA_NOT_CONFIGURED",
                        message="Telegram QA orchestrator is not configured",
                        http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        failure_reason="UNKNOWN_ERROR",
                    )
                qa_result = await self._telegram_qa_orchestrator.handle_ask_command(
                    command_text=normalized_input_text,
                    request_workflow_id=request_workflow_id,
                )
                reply_text = qa_result.reply_text
                qa_workflow_run_id = qa_result.qa_workflow_run_id
                insufficient_info = qa_result.insufficient_info
                citations = qa_result.citation_paths
            elif command in {"accept", "reject"}:
                if self._telegram_review_orchestrator is None:
                    raise TelegramGatewayError(
                        error_code="TELEGRAM_REVIEW_NOT_CONFIGURED",
                        message="Telegram review orchestrator is not configured",
                        http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        failure_reason="UNKNOWN_ERROR",
                    )
                review_result = await self._telegram_review_orchestrator.handle_review_command(
                    command=command,
                    command_text=normalized_input_text,
                    chat_id=normalized_chat_id,
                    request_workflow_id=request_workflow_id,
                )
                reply_text = review_result.reply_text
                review_workflow_run_id = review_result.review_workflow_run_id
                change_request_id = review_result.change_request_id
                change_request_status = review_result.change_request_status
                review_action = review_result.review_action
            elif command == "ingest" or (has_media and command == "unknown"):
                if self._telegram_ingestion_orchestrator is None:
                    raise TelegramGatewayError(
                        error_code="TELEGRAM_INGESTION_NOT_CONFIGURED",
                        message="Telegram ingestion orchestrator is not configured",
                        http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        failure_reason="UNKNOWN_ERROR",
                    )
                command = "ingest"
                target_notion_page_id = self._parse_ingest_target(
                    normalized_input_text
                )
                ingestion_result = await self._telegram_ingestion_orchestrator.handle_ingest_command(
                    chat_id=normalized_chat_id,
                    document=document,
                    photos=photos,
                    request_workflow_id=request_workflow_id,
                    target_notion_page_id=target_notion_page_id,
                )
                reply_text = ingestion_result.reply_text
                source_document_id = ingestion_result.source_document_id
                change_request_id = ingestion_result.change_request_id
                source_type = ingestion_result.source_type
                target_notion_page_id = ingestion_result.target_notion_page_id
            else:
                reply_text = self._build_reply_for_command(command)

            tool_result = await self._tool_registry.call_tool(
                TELEGRAM_BOT_TOOL_NAME,
                context=ToolContext(
                    workflow_id=request_workflow_id,
                    metadata={
                        "operation": "telegram_reply",
                        "command": command,
                        "chat_id": normalized_chat_id,
                    },
                ),
                arguments={
                    "chat_id": normalized_chat_id,
                    "text": reply_text,
                },
            )
            if tool_result.is_error:
                error_code = "UNKNOWN_ERROR"
                error_message = "Telegram reply failed"
                if tool_result.error is not None:
                    error_code = tool_result.error.code
                    error_message = tool_result.error.message
                raise TelegramGatewayError(
                    error_code=error_code,
                    message=error_message,
                    http_status_code=self._http_status_for_tool_error(error_code),
                    failure_reason=self._normalize_failure_reason(error_code),
                )

            structured_content = tool_result.structured_content or {}
            raw_message_id = structured_content.get("message_id")
            telegram_message_id: Optional[int] = None
            if isinstance(raw_message_id, int):
                telegram_message_id = raw_message_id

            self._workflow_run_service.mark_workflow_succeeded(
                workflow_run.id,
                metadata_json=json.dumps(
                    {
                        "operation": "telegram_webhook",
                        "handled": True,
                        "command": command,
                        "chat_id": normalized_chat_id,
                        "telegram_message_id": telegram_message_id,
                        "source_document_id": source_document_id,
                        "change_request_id": change_request_id,
                        "source_type": source_type,
                        "target_notion_page_id": target_notion_page_id,
                        "qa_workflow_run_id": qa_workflow_run_id,
                        "insufficient_info": insufficient_info,
                        "citation_count": len(citations),
                        "review_workflow_run_id": review_workflow_run_id,
                        "review_action": review_action,
                        "change_request_status": change_request_status,
                    },
                    sort_keys=True,
                ),
            )

            return TelegramGatewayResult(
                workflow_run_id=workflow_run.id,
                status="succeeded",
                handled=True,
                command=command,
                reply_text=reply_text,
                telegram_message_id=telegram_message_id,
                skipped_reason=None,
                source_document_id=source_document_id,
                change_request_id=change_request_id,
                source_type=source_type,
                target_notion_page_id=target_notion_page_id,
                qa_workflow_run_id=qa_workflow_run_id,
                insufficient_info=insufficient_info,
                citations=citations,
                review_workflow_run_id=review_workflow_run_id,
                review_action=review_action,
                change_request_status=change_request_status,
            )
        except WorkflowRunAuditUpdateError:
            raise
        except TelegramIngestionError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason=exc.failure_reason,
                error_code=exc.error_code,
            )
            raise TelegramGatewayError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=exc.http_status_code,
                failure_reason=self._normalize_failure_reason(exc.failure_reason),
                workflow_run_id=workflow_run.id,
            ) from exc

        except TelegramQAError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason=exc.failure_reason,
                error_code=exc.error_code,
            )
            raise TelegramGatewayError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=exc.http_status_code,
                failure_reason=self._normalize_failure_reason(exc.failure_reason),
                workflow_run_id=workflow_run.id,
            ) from exc
        except TelegramReviewError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason=exc.failure_reason,
                error_code=exc.error_code,
            )
            raise TelegramGatewayError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=exc.http_status_code,
                failure_reason=self._normalize_failure_reason(exc.failure_reason),
                workflow_run_id=workflow_run.id,
            ) from exc
        except TelegramGatewayError as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason=exc.failure_reason,
                error_code=exc.error_code,
            )
            raise TelegramGatewayError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=exc.http_status_code,
                failure_reason=exc.failure_reason,
                workflow_run_id=workflow_run.id,
            ) from exc
        except Exception as exc:
            self._mark_failed_workflow(
                workflow_run_id=workflow_run.id,
                failure_reason="UNKNOWN_ERROR",
                error_code="TELEGRAM_GATEWAY_FAILED",
            )
            raise TelegramGatewayError(
                error_code="TELEGRAM_GATEWAY_FAILED",
                message=(
                    "Telegram gateway workflow failed: "
                    f"{sanitize_sensitive_text(str(exc))}"
                ),
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc

    def _require_allowed_chat(self, chat_id: Optional[str]) -> None:
        if self._trust_boundary is None:
            return
        try:
            self._trust_boundary.require_allowed_telegram_chat(chat_id)
        except TrustBoundaryError as exc:
            raise TelegramGatewayError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=exc.http_status_code,
                failure_reason=exc.failure_reason,
            ) from exc

    def _claim_update(self, update_id: Optional[int]) -> Optional[TelegramUpdateClaim]:
        if self._update_idempotency_service is None:
            return None
        try:
            return self._update_idempotency_service.claim(update_id)
        except TelegramUpdateIdempotencyError as exc:
            raise TelegramGatewayError(
                error_code="TELEGRAM_UPDATE_LEDGER_FAILED",
                message="Telegram update ledger could not be claimed",
                http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                failure_reason="TELEGRAM_UPDATE_LEDGER_FAILED",
            ) from exc

    def _replay_or_report_duplicate(
        self,
        claim: TelegramUpdateClaim,
    ) -> TelegramGatewayResult:
        if claim.status == "succeeded":
            if not claim.result_json:
                raise TelegramGatewayError(
                    error_code="TELEGRAM_UPDATE_LEDGER_FAILED",
                    message="Telegram update ledger result is missing",
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                    failure_reason="TELEGRAM_UPDATE_LEDGER_FAILED",
                    workflow_run_id=claim.workflow_run_id,
                )
            try:
                return TelegramGatewayResult(**json.loads(claim.result_json))
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise TelegramGatewayError(
                    error_code="TELEGRAM_UPDATE_LEDGER_FAILED",
                    message="Telegram update ledger result is invalid",
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                    failure_reason="TELEGRAM_UPDATE_LEDGER_FAILED",
                    workflow_run_id=claim.workflow_run_id,
                ) from exc

        if claim.status == "failed":
            failure = {}
            if claim.failure_json:
                try:
                    failure = json.loads(claim.failure_json)
                except (TypeError, ValueError, json.JSONDecodeError):
                    failure = {}
            raise TelegramGatewayError(
                error_code=str(failure.get("error_code", "TELEGRAM_GATEWAY_FAILED")),
                message=str(failure.get("message", "Telegram update previously failed")),
                http_status_code=int(failure.get("http_status_code", HTTPStatus.INTERNAL_SERVER_ERROR)),
                failure_reason=str(failure.get("failure_reason", "UNKNOWN_ERROR")),
                workflow_run_id=claim.workflow_run_id,
            )

        return TelegramGatewayResult(
            workflow_run_id=claim.workflow_run_id,
            status="running",
            handled=False,
            command=None,
            reply_text=None,
            telegram_message_id=None,
            skipped_reason="DUPLICATE_UPDATE_IN_PROGRESS",
            source_document_id=None,
            change_request_id=None,
            source_type=None,
            target_notion_page_id=None,
            qa_workflow_run_id=None,
            insufficient_info=None,
            citations=[],
            review_workflow_run_id=None,
            review_action=None,
            change_request_status=None,
        )

    def _mark_update_failed(
        self,
        update_id: Optional[int],
        error: TelegramGatewayError,
    ) -> None:
        if self._update_idempotency_service is None:
            return
        self._update_idempotency_service.mark_failed(
            update_id,
            workflow_run_id=error.workflow_run_id,
            failure={
                "error_code": error.error_code,
                "message": error.message,
                "http_status_code": error.http_status_code,
                "failure_reason": error.failure_reason,
            },
        )

    def _parse_command(self, text: str) -> str:
        command_text = text.split(maxsplit=1)[0].strip().lower()
        if command_text.startswith("/"):
            command_text = command_text[1:]
        if not command_text:
            return "unknown"
        return command_text

    def _build_reply_for_command(self, command: str) -> str:
        if command == "health":
            return "LearnLoop Agent status: ok"
        if command == "help":
            return "Available commands: /help, /health, /ingest, /ask, /accept, /reject"
        return "Unsupported command. Use /help."

    def _parse_ingest_target(self, command_text: str) -> Optional[str]:
        try:
            tokens = shlex.split(command_text)
        except ValueError as exc:
            raise TelegramGatewayError(
                error_code="INVALID_ARGUMENT",
                message=f"Invalid /ingest command: {exc}",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            ) from exc

        target_notion_page_id: Optional[str] = None
        index = 1
        while index < len(tokens):
            token = tokens[index]
            if token == "--page":
                if index + 1 >= len(tokens):
                    raise TelegramGatewayError(
                        error_code="INVALID_ARGUMENT",
                        message="Usage: /ingest [--page <page_id>] with a PDF or screenshot",
                        http_status_code=HTTPStatus.BAD_REQUEST,
                        failure_reason="UNKNOWN_ERROR",
                    )
                target_notion_page_id = tokens[index + 1].strip()
                index += 2
                continue
            if token.startswith("--page="):
                target_notion_page_id = token.split("=", 1)[1].strip()
                if not target_notion_page_id:
                    raise TelegramGatewayError(
                        error_code="INVALID_ARGUMENT",
                        message="Usage: /ingest [--page <page_id>] with a PDF or screenshot",
                        http_status_code=HTTPStatus.BAD_REQUEST,
                        failure_reason="UNKNOWN_ERROR",
                    )
                index += 1
                continue
            raise TelegramGatewayError(
                error_code="INVALID_ARGUMENT",
                message="Usage: /ingest [--page <page_id>] with a PDF or screenshot",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            )
        return target_notion_page_id

    def _normalize_failure_reason(self, failure_reason: str) -> str:
        normalized = failure_reason.strip().upper()
        if normalized in STANDARD_FAILURE_REASONS:
            return normalized
        return "UNKNOWN_ERROR"

    def _http_status_for_tool_error(self, error_code: str) -> int:
        normalized = error_code.strip().upper()
        if normalized == "INVALID_ARGUMENT":
            return HTTPStatus.BAD_REQUEST
        if normalized == "TELEGRAM_NOT_CONFIGURED":
            return HTTPStatus.SERVICE_UNAVAILABLE
        if normalized == "TELEGRAM_SEND_FAILED":
            return HTTPStatus.BAD_GATEWAY
        return HTTPStatus.INTERNAL_SERVER_ERROR

    def _mark_failed_workflow(
        self,
        *,
        workflow_run_id: int,
        failure_reason: str,
        error_code: str,
    ) -> None:
        self._workflow_run_service.mark_workflow_failed(
            workflow_run_id,
            failure_reason=self._normalize_failure_reason(failure_reason),
            metadata_json=json.dumps(
                {
                    "operation": "telegram_webhook",
                    "error_code": error_code,
                },
                sort_keys=True,
            ),
        )
