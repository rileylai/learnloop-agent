from __future__ import annotations

import json
import hashlib
import shlex
import uuid
from dataclasses import asdict, dataclass
from http import HTTPStatus
from typing import Any, Optional

from src.observability.redaction import sanitize_sensitive_text
from src.queue import QueueClient, QueueRetryPolicy, get_callable_import_path
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
    target_set: bool = False


@dataclass
class TelegramCallbackAttachment:
    callback_query_id: str
    callback_data: str


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
        user_id: Optional[str] = None,
        message_id: Optional[int] = None,
        media_group_id: Optional[str] = None,
        callback: Optional[TelegramCallbackAttachment] = None,
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
            user_id=user_id,
            message_id=message_id,
            media_group_id=media_group_id,
            callback=callback,
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
        user_id: Optional[str] = None,
        message_id: Optional[int] = None,
        media_group_id: Optional[str] = None,
        callback: Optional[TelegramCallbackAttachment] = None,
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
            user_id=user_id,
            message_id=message_id,
            media_group_id=media_group_id,
            callback=callback,
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
        user_id: Optional[str] = None,
        message_id: Optional[int] = None,
        media_group_id: Optional[str] = None,
        callback: Optional[TelegramCallbackAttachment] = None,
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
                user_id=user_id,
                message_id=message_id,
                media_group_id=media_group_id,
                callback=callback,
                request_workflow_id=request_workflow_id,
            )

        retry_policy = QueueRetryPolicy(max_retries=2, retry_intervals=(5, 30))
        try:
            from src.worker.telegram import (
                TELEGRAM_WEBHOOK_JOB_PATH,
                process_telegram_webhook_job,
            )

            if (
                get_callable_import_path(process_telegram_webhook_job)
                != TELEGRAM_WEBHOOK_JOB_PATH
            ):
                raise RuntimeError("Telegram worker callable path is not canonical")

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
                    user_id,
                    message_id,
                    media_group_id,
                    asdict(callback) if callback is not None else None,
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
        user_id: Optional[str],
        message_id: Optional[int],
        media_group_id: Optional[str],
        callback: Optional[TelegramCallbackAttachment],
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
                user_id=user_id,
                message_id=message_id,
                media_group_id=media_group_id,
                callback=callback,
                request_workflow_id=request_workflow_id,
            )
        except TelegramGatewayError as exc:
            await self._notify_user_of_gateway_error(
                error=exc,
                chat_id=chat_id,
                callback=callback,
                request_workflow_id=request_workflow_id,
            )
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

    async def _notify_user_of_gateway_error(
        self,
        *,
        error: TelegramGatewayError,
        chat_id: Optional[str],
        callback: Optional[TelegramCallbackAttachment],
        request_workflow_id: str,
    ) -> None:
        if error.error_code not in {
            "UPLOAD_SESSION_EXPIRED",
            "UPLOAD_SESSION_INVALID",
            "INVALID_CALLBACK",
            "TELEGRAM_QUEUE_UNAVAILABLE",
            "EMPTY_UPLOAD",
        }:
            return
        safe_message = sanitize_sensitive_text(error.message)[:190]
        try:
            if callback is not None:
                await self._tool_registry.call_tool(
                    TELEGRAM_BOT_TOOL_NAME,
                    context=ToolContext(
                        workflow_id=request_workflow_id,
                        metadata={"operation": "telegram_callback_error"},
                    ),
                    arguments={
                        "action": "answer_callback_query",
                        "callback_query_id": callback.callback_query_id,
                        "text": safe_message,
                    },
                )
            elif chat_id:
                await self._tool_registry.call_tool(
                    TELEGRAM_BOT_TOOL_NAME,
                    context=ToolContext(
                        workflow_id=request_workflow_id,
                        metadata={
                            "operation": "telegram_error_reply",
                            "chat_id": chat_id,
                        },
                    ),
                    arguments={"chat_id": chat_id, "text": safe_message},
                )
        except Exception:
            # The original deterministic gateway error remains authoritative.
            return

    async def _handle_new_webhook(
        self,
        *,
        update_id: Optional[int],
        chat_id: Optional[str],
        text: Optional[str],
        caption: Optional[str],
        document: Optional[TelegramDocumentAttachment],
        photos: list[TelegramPhotoAttachment],
        user_id: Optional[str],
        message_id: Optional[int],
        media_group_id: Optional[str],
        callback: Optional[TelegramCallbackAttachment],
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
            normalized_input_text = self._select_command_text(
                text=normalized_text,
                caption=normalized_caption,
            )
            normalized_chat_id = (chat_id or "").strip()
            normalized_user_id = (user_id or normalized_chat_id).strip()
            has_media = (document is not None) or bool(photos)

            if not normalized_chat_id or (
                not normalized_input_text and not has_media and callback is None
            ):
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
            if command == "start":
                command = "help"
            source_document_id: Optional[int] = None
            change_request_id: Optional[int] = None
            source_type: Optional[str] = None
            target_notion_page_id: Optional[str] = None
            target_notion_path: Optional[str] = None
            target_set = False
            qa_workflow_run_id: Optional[int] = None
            insufficient_info: Optional[bool] = None
            citations: list[str] = []
            review_workflow_run_id: Optional[int] = None
            review_action: Optional[str] = None
            change_request_status: Optional[str] = None
            reply_markup: Optional[dict[str, Any]] = None
            callback_query_id: Optional[str] = None
            ingestion_result = None
            reply_text = ""
            if callback is not None:
                command = "callback"
                callback_query_id = callback.callback_query_id
                callback_action = self._resolve_callback_action(
                    callback=callback,
                    chat_id=normalized_chat_id,
                    user_id=normalized_user_id,
                )
                if callback_action.action == "select_target":
                    if self._telegram_ingestion_orchestrator is None:
                        raise TelegramGatewayError(
                            error_code="TELEGRAM_INGESTION_NOT_CONFIGURED",
                            message="Telegram ingestion orchestrator is not configured",
                            http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            failure_reason="UNKNOWN_ERROR",
                        )
                    target_notion_page_id = callback_action.target_notion_page_id
                    target_notion_path = callback_action.target_notion_path
                    if not target_notion_page_id or not target_notion_path:
                        raise TelegramGatewayError(
                            error_code="INVALID_CALLBACK",
                            message="This page selection is invalid. Please upload again.",
                            http_status_code=HTTPStatus.BAD_REQUEST,
                            failure_reason="INVALID_ARGUMENT",
                        )
                    ingestion_result = await self._telegram_ingestion_orchestrator.handle_target_selection(
                        session_id=callback_action.session_id,
                        chat_id=normalized_chat_id,
                        user_id=normalized_user_id,
                        target_notion_page_id=target_notion_page_id,
                        target_notion_path=target_notion_path,
                        request_workflow_id=request_workflow_id,
                    )
                    source_document_id = ingestion_result.source_document_id
                    change_request_id = ingestion_result.change_request_id
                    source_type = ingestion_result.source_type
                    target_set = bool(ingestion_result.target_notion_page_id)
                    reply_text = ingestion_result.reply_text
                    if change_request_id is not None:
                        if ingestion_result.session_id and self._telegram_ingestion_orchestrator.claim_upload_preview(
                            session_id=ingestion_result.session_id,
                            chat_id=normalized_chat_id,
                            user_id=normalized_user_id,
                        ):
                            reply_markup = self._build_review_markup(
                                ingestion_result=ingestion_result,
                                chat_id=normalized_chat_id,
                                user_id=normalized_user_id,
                            )
                        else:
                            reply_text = "This proposal is already ready for review."
                elif callback_action.action in {"accept", "reject"}:
                    if self._telegram_review_orchestrator is None:
                        raise TelegramGatewayError(
                            error_code="TELEGRAM_REVIEW_NOT_CONFIGURED",
                            message="Telegram review orchestrator is not configured",
                            http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            failure_reason="UNKNOWN_ERROR",
                        )
                    if callback_action.change_request_id is None:
                        raise TelegramGatewayError(
                            error_code="INVALID_CALLBACK",
                            message="This review action is invalid.",
                            http_status_code=HTTPStatus.BAD_REQUEST,
                            failure_reason="INVALID_ARGUMENT",
                        )
                    review_command = f"/{callback_action.action} {callback_action.change_request_id}"
                    review_result = await self._telegram_review_orchestrator.handle_review_command(
                        command=callback_action.action,
                        command_text=review_command,
                        chat_id=normalized_chat_id,
                        request_workflow_id=request_workflow_id,
                    )
                    reply_text = review_result.reply_text
                    review_workflow_run_id = review_result.review_workflow_run_id
                    change_request_id = review_result.change_request_id
                    change_request_status = review_result.change_request_status
                    review_action = review_result.review_action
                elif callback_action.action == "change_target":
                    if self._telegram_page_orchestrator is None:
                        raise TelegramGatewayError(
                            error_code="TELEGRAM_PAGES_NOT_CONFIGURED",
                            message="Telegram page orchestrator is not configured",
                            http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            failure_reason="UNKNOWN_ERROR",
                        )
                    if callback_action.change_request_id is None:
                        raise TelegramGatewayError(
                            error_code="INVALID_CALLBACK",
                            message="This target action is invalid.",
                            http_status_code=HTTPStatus.BAD_REQUEST,
                            failure_reason="INVALID_ARGUMENT",
                        )
                    reply_text, reply_markup = self._build_review_target_picker(
                        change_request_id=callback_action.change_request_id,
                        chat_id=normalized_chat_id,
                        user_id=normalized_user_id,
                    )
                    change_request_id = callback_action.change_request_id
                elif callback_action.action == "change_target_select":
                    if (
                        self._telegram_review_orchestrator is None
                        or callback_action.change_request_id is None
                        or not callback_action.target_notion_page_id
                    ):
                        raise TelegramGatewayError(
                            error_code="INVALID_CALLBACK",
                            message="This target selection is invalid.",
                            http_status_code=HTTPStatus.BAD_REQUEST,
                            failure_reason="INVALID_ARGUMENT",
                        )
                    review_result = await self._telegram_review_orchestrator.handle_change_target(
                        change_request_id=callback_action.change_request_id,
                        target_notion_page_id=callback_action.target_notion_page_id,
                        chat_id=normalized_chat_id,
                        request_workflow_id=request_workflow_id,
                    )
                    reply_text = review_result.reply_text
                    review_workflow_run_id = review_result.review_workflow_run_id
                    change_request_id = review_result.change_request_id
                    change_request_status = review_result.change_request_status
                    review_action = review_result.review_action
                    target_notion_page_id = callback_action.target_notion_page_id
                    target_notion_path = callback_action.target_notion_path
                    target_set = bool(target_notion_page_id)
                    reply_markup = self._build_review_markup_for_change_request(
                        change_request_id=int(change_request_id),
                        session_id=callback_action.session_id,
                        chat_id=normalized_chat_id,
                        user_id=normalized_user_id,
                    )
                else:
                    raise TelegramGatewayError(
                        error_code="INVALID_CALLBACK",
                        message="This button is no longer valid. Please upload again.",
                        http_status_code=HTTPStatus.BAD_REQUEST,
                        failure_reason="INVALID_ARGUMENT",
                    )
            elif command == "health":
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
                target_notion_page_id = self._parse_ingest_target(normalized_input_text)
                if target_notion_page_id is not None and not has_media:
                    session = self._telegram_ingestion_orchestrator.get_latest_upload(
                        chat_id=normalized_chat_id,
                        user_id=normalized_user_id,
                    )
                    if session is None:
                        raise TelegramGatewayError(
                            error_code="UPLOAD_SESSION_EXPIRED",
                            message="No unexpired upload session was found. Please upload the file again.",
                            http_status_code=HTTPStatus.GONE,
                            failure_reason="UPLOAD_SESSION_EXPIRED",
                        )
                    target_page = self._find_page(target_notion_page_id)
                    if target_page is None:
                        raise TelegramGatewayError(
                            error_code="NOTION_PAGE_NOT_FOUND",
                            message="The selected Notion page is no longer indexed. Use /pages and choose again.",
                            http_status_code=HTTPStatus.NOT_FOUND,
                            failure_reason="NOTION_PAGE_NOT_FOUND",
                        )
                    ingestion_result = await self._telegram_ingestion_orchestrator.handle_target_selection(
                        session_id=session.session_id,
                        chat_id=normalized_chat_id,
                        user_id=normalized_user_id,
                        target_notion_page_id=target_page.page_id,
                        target_notion_path=target_page.notion_path,
                        request_workflow_id=request_workflow_id,
                    )
                elif target_notion_page_id is None and not has_media:
                    session = self._telegram_ingestion_orchestrator.get_latest_upload(
                        chat_id=normalized_chat_id,
                        user_id=normalized_user_id,
                    )
                    if session is None:
                        raise TelegramGatewayError(
                            error_code="UPLOAD_SESSION_EXPIRED",
                            message="No unexpired upload session was found. Please upload a PDF or image first.",
                            http_status_code=HTTPStatus.GONE,
                            failure_reason="UPLOAD_SESSION_EXPIRED",
                        )
                    reply_text, reply_markup = self._build_page_picker(
                        session_id=session.session_id,
                        chat_id=normalized_chat_id,
                        user_id=normalized_user_id,
                    )
                    target_notion_page_id = session.target_notion_page_id
                elif target_notion_page_id is not None:
                    ingestion_result = await self._telegram_ingestion_orchestrator.handle_ingest_command(
                        chat_id=normalized_chat_id,
                        document=document,
                        photos=photos,
                        request_workflow_id=request_workflow_id,
                        target_notion_page_id=target_notion_page_id,
                    )
                    target_set = True
                else:
                    session_id = self._build_upload_session_id(
                        update_id=update_id,
                        message_id=message_id,
                        media_group_id=media_group_id,
                    )
                    session = self._telegram_ingestion_orchestrator.store_upload(
                        session_id=session_id,
                        chat_id=normalized_chat_id,
                        user_id=normalized_user_id,
                        media_group_id=media_group_id,
                        document=document,
                        photos=photos,
                        command_text=normalized_input_text or None,
                    )
                    if media_group_id:
                        if self._queue_client is None:
                            raise TelegramGatewayError(
                                error_code="TELEGRAM_QUEUE_UNAVAILABLE",
                                message=(
                                    "Media groups require the Redis/RQ queue; "
                                    "please try a single PDF or image instead."
                                ),
                                http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                                failure_reason="TELEGRAM_QUEUE_UNAVAILABLE",
                            )
                        if self._telegram_ingestion_orchestrator.claim_upload_settle(
                            session_id=session.session_id,
                            chat_id=normalized_chat_id,
                            user_id=normalized_user_id,
                        ):
                            self._schedule_upload_settle(
                                session_id=session.session_id,
                                chat_id=normalized_chat_id,
                                user_id=normalized_user_id,
                                request_workflow_id=request_workflow_id,
                            )
                        if not self._telegram_ingestion_orchestrator.claim_upload_receipt(
                            session_id=session.session_id,
                            chat_id=normalized_chat_id,
                            user_id=normalized_user_id,
                        ):
                            reply_text = ""
                        else:
                            reply_text = (
                                f"Received media group ({len(session.attachments)} file(s)). "
                                "I will group the files, then show target pages."
                            )
                    else:
                        reply_text, reply_markup = self._build_page_picker(
                            session_id=session.session_id,
                            chat_id=normalized_chat_id,
                            user_id=normalized_user_id,
                        )
                    target_notion_page_id = session.target_notion_page_id
                if ingestion_result is not None:
                    source_document_id = ingestion_result.source_document_id
                    change_request_id = ingestion_result.change_request_id
                    source_type = ingestion_result.source_type
                    target_notion_page_id = ingestion_result.target_notion_page_id
                    target_notion_path = ingestion_result.target_notion_path
                    target_set = bool(target_notion_page_id)
                    if not reply_text:
                        reply_text = ingestion_result.reply_text
                    if (
                        change_request_id is not None
                        and target_set
                        and reply_markup is None
                    ):
                        reply_markup = self._build_review_markup(
                            ingestion_result=ingestion_result,
                            chat_id=normalized_chat_id,
                            user_id=normalized_user_id,
                        )
            else:
                reply_text = self._build_reply_for_command(command)

            telegram_message_id: Optional[int] = None
            if callback_query_id is not None:
                callback_result = await self._tool_registry.call_tool(
                    TELEGRAM_BOT_TOOL_NAME,
                    context=ToolContext(
                        workflow_id=request_workflow_id,
                        metadata={
                            "operation": "telegram_callback_answer",
                            "chat_id": normalized_chat_id,
                        },
                    ),
                    arguments={
                        "action": "answer_callback_query",
                        "callback_query_id": callback_query_id,
                    },
                )
                if callback_result.is_error:
                    error_code = callback_result.error.code if callback_result.error else "UNKNOWN_ERROR"
                    raise TelegramGatewayError(
                        error_code=error_code,
                        message="Telegram callback acknowledgement failed",
                        http_status_code=self._http_status_for_tool_error(error_code),
                        failure_reason=self._normalize_failure_reason(error_code),
                    )

            if reply_text:
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
                        **({"reply_markup": reply_markup} if reply_markup else {}),
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
                        "target_set": target_set,
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
                target_set=target_set,
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

    async def settle_upload_session(
        self,
        *,
        session_id: str,
        chat_id: str,
        user_id: str,
        request_workflow_id: str,
    ) -> None:
        if self._telegram_ingestion_orchestrator is None:
            raise TelegramGatewayError(
                error_code="TELEGRAM_INGESTION_NOT_CONFIGURED",
                message="Telegram ingestion orchestrator is not configured",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
            )
        session = self._telegram_ingestion_orchestrator.get_upload(
            session_id=session_id,
            chat_id=chat_id,
            user_id=user_id,
        )
        if session is None:
            raise TelegramGatewayError(
                error_code="UPLOAD_SESSION_EXPIRED",
                message="This media group session expired before it could be settled.",
                http_status_code=HTTPStatus.GONE,
                failure_reason="UPLOAD_SESSION_EXPIRED",
            )
        if not session.attachments:
            self._telegram_ingestion_orchestrator.fail_upload(
                session_id=session_id,
                chat_id=chat_id,
                user_id=user_id,
                failure_reason="EMPTY_UPLOAD",
            )
            raise TelegramGatewayError(
                error_code="EMPTY_UPLOAD",
                message="No media was found in this upload session. Please upload the file again.",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="EMPTY_UPLOAD",
            )
        if not self._telegram_ingestion_orchestrator.claim_upload_picker(
            session_id=session_id,
            chat_id=chat_id,
            user_id=user_id,
        ):
            return
        reply_text, reply_markup = self._build_page_picker(
            session_id=session_id,
            chat_id=chat_id,
            user_id=user_id,
            claim_picker=False,
        )
        tool_result = await self._tool_registry.call_tool(
            TELEGRAM_BOT_TOOL_NAME,
            context=ToolContext(
                workflow_id=request_workflow_id,
                metadata={
                    "operation": "telegram_media_group_picker",
                    "chat_id": chat_id,
                    "session_id": session_id,
                },
            ),
            arguments={
                "chat_id": chat_id,
                "text": reply_text,
                "reply_markup": reply_markup,
            },
        )
        if tool_result.is_error:
            error_code = tool_result.error.code if tool_result.error else "TELEGRAM_SEND_FAILED"
            raise TelegramGatewayError(
                error_code=error_code,
                message="Telegram page picker could not be sent.",
                http_status_code=self._http_status_for_tool_error(error_code),
                failure_reason=self._normalize_failure_reason(error_code),
            )

    def _parse_command(self, text: str) -> str:
        if not text.strip():
            return "unknown"
        command_text = text.split(maxsplit=1)[0].strip().lower()
        if command_text.startswith("/"):
            command_text = command_text[1:]
        if not command_text:
            return "unknown"
        return command_text

    def _select_command_text(self, *, text: str, caption: str) -> str:
        for candidate in (text, caption):
            if candidate.startswith("/"):
                return candidate
        return text or caption

    def _build_upload_session_id(
        self,
        *,
        update_id: Optional[int],
        message_id: Optional[int],
        media_group_id: Optional[str],
    ) -> str:
        if media_group_id:
            digest = hashlib.sha256(media_group_id.encode("utf-8")).hexdigest()[:24]
            return f"group-{digest}"
        if update_id is not None:
            return f"single-update-{update_id}"
        if message_id is not None:
            return f"single-message-{message_id}"
        return f"single-{uuid.uuid4().hex}"

    def _find_page(self, page_id: str):
        if self._telegram_page_orchestrator is None:
            return None
        pages = self._telegram_page_orchestrator.list_pages().pages
        return next((page for page in pages if page.page_id == page_id), None)

    def _resolve_callback_action(
        self,
        *,
        callback: TelegramCallbackAttachment,
        chat_id: str,
        user_id: str,
    ):
        raw_data = callback.callback_data.strip()
        if not raw_data.startswith("ll:"):
            raise TelegramGatewayError(
                error_code="INVALID_CALLBACK",
                message="This button is invalid or expired. Please upload the file again.",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="INVALID_ARGUMENT",
            )
        token = raw_data[3:].strip()
        if not token or self._telegram_ingestion_orchestrator is None:
            raise TelegramGatewayError(
                error_code="INVALID_CALLBACK",
                message="This button is invalid or expired. Please upload the file again.",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="INVALID_ARGUMENT",
            )
        action = self._telegram_ingestion_orchestrator.resolve_callback(
            token=token,
            chat_id=chat_id,
            user_id=user_id,
        )
        if action is None:
            raise TelegramGatewayError(
                error_code="INVALID_CALLBACK",
                message="This button is invalid or expired. Please upload the file again.",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="INVALID_ARGUMENT",
            )
        return action

    def _build_page_picker(
        self,
        *,
        session_id: str,
        chat_id: str,
        user_id: str,
        claim_picker: bool = True,
    ) -> tuple[str, dict[str, Any]]:
        if self._telegram_page_orchestrator is None or self._telegram_ingestion_orchestrator is None:
            raise TelegramGatewayError(
                error_code="TELEGRAM_PAGES_NOT_CONFIGURED",
                message="Telegram page picker is not configured",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
            )
        pages = self._telegram_page_orchestrator.list_pages().pages
        if not pages:
            raise TelegramGatewayError(
                error_code="NOTION_PAGES_EMPTY",
                message="No indexed Notion pages are available. Index Notion pages, then upload again.",
                http_status_code=HTTPStatus.CONFLICT,
                failure_reason="NOTION_PAGE_NOT_FOUND",
            )
        buttons = []
        for index, page in enumerate(pages, start=1):
            token = self._telegram_ingestion_orchestrator.create_callback(
                session_id=session_id,
                chat_id=chat_id,
                user_id=user_id,
                action="select_target",
                target_notion_page_id=page.page_id,
                target_notion_path=page.notion_path,
            )
            buttons.append(
                {
                    "text": f"{index}. {page.title} · {page.notion_path}",
                    "callback_data": f"ll:{token}",
                }
            )
        if claim_picker:
            self._telegram_ingestion_orchestrator.claim_upload_picker(
                session_id=session_id,
                chat_id=chat_id,
                user_id=user_id,
            )
        return (
            "File received. Choose the Notion target page. Parent and child pages are separate targets.",
            {"inline_keyboard": [[button] for button in buttons]},
        )

    def _build_review_markup(
        self,
        *,
        ingestion_result,
        chat_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        if self._telegram_ingestion_orchestrator is None or ingestion_result.change_request_id is None:
            return {}
        return self._build_review_markup_for_change_request(
            change_request_id=int(ingestion_result.change_request_id),
            session_id=ingestion_result.session_id,
            chat_id=chat_id,
            user_id=user_id,
        )

    def _build_review_markup_for_change_request(
        self,
        *,
        change_request_id: int,
        session_id: Optional[str],
        chat_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        if self._telegram_ingestion_orchestrator is None:
            return {}
        accept_token = self._telegram_ingestion_orchestrator.create_callback(
            session_id=session_id or f"proposal-{change_request_id}",
            chat_id=chat_id,
            user_id=user_id,
            action="accept",
            change_request_id=change_request_id,
        )
        reject_token = self._telegram_ingestion_orchestrator.create_callback(
            session_id=session_id or f"proposal-{change_request_id}",
            chat_id=chat_id,
            user_id=user_id,
            action="reject",
            change_request_id=change_request_id,
        )
        change_target_token = self._telegram_ingestion_orchestrator.create_callback(
            session_id=session_id or f"proposal-{change_request_id}",
            chat_id=chat_id,
            user_id=user_id,
            action="change_target",
            change_request_id=change_request_id,
        )
        return {
            "inline_keyboard": [
                [
                    {"text": "Accept", "callback_data": f"ll:{accept_token}"},
                    {"text": "Reject", "callback_data": f"ll:{reject_token}"},
                ],
                [{"text": "Change target", "callback_data": f"ll:{change_target_token}"}],
            ]
        }

    def _build_review_target_picker(
        self,
        *,
        change_request_id: int,
        chat_id: str,
        user_id: str,
    ) -> tuple[str, dict[str, Any]]:
        pages = self._telegram_page_orchestrator.list_pages().pages if self._telegram_page_orchestrator else []
        if not pages or self._telegram_ingestion_orchestrator is None:
            raise TelegramGatewayError(
                error_code="NOTION_PAGES_EMPTY",
                message="No indexed Notion pages are available.",
                http_status_code=HTTPStatus.CONFLICT,
                failure_reason="NOTION_PAGE_NOT_FOUND",
            )
        buttons = []
        session_id = f"proposal-{change_request_id}"
        for index, page in enumerate(pages, start=1):
            token = self._telegram_ingestion_orchestrator.create_callback(
                session_id=session_id,
                chat_id=chat_id,
                user_id=user_id,
                action="change_target_select",
                change_request_id=change_request_id,
                target_notion_page_id=page.page_id,
                target_notion_path=page.notion_path,
            )
            buttons.append(
                {
                    "text": f"{index}. {page.title} · {page.notion_path}",
                    "callback_data": f"ll:{token}",
                }
            )
        return (
            "Choose a new target page. The pending proposal remains review-only.",
            {"inline_keyboard": [[button] for button in buttons]},
        )

    def _schedule_upload_settle(
        self,
        *,
        session_id: str,
        chat_id: str,
        user_id: str,
        request_workflow_id: str,
    ) -> None:
        if self._queue_client is None:
            raise TelegramGatewayError(
                error_code="TELEGRAM_QUEUE_UNAVAILABLE",
                message="Media-group settling requires the Redis/RQ queue.",
                http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                failure_reason="TELEGRAM_QUEUE_UNAVAILABLE",
            )
        from src.worker.telegram import process_telegram_upload_settle_job

        self._queue_client.enqueue_in(
            queue_name="telegram",
            function=process_telegram_upload_settle_job,
            seconds=1,
            args=(session_id, chat_id, user_id, request_workflow_id),
            description="Settle one Telegram media group upload session",
            retry_policy=QueueRetryPolicy(max_retries=2, retry_intervals=(1, 3)),
        )

    def _build_reply_for_command(self, command: str) -> str:
        if command == "health":
            return "LearnLoop Agent status: ok"
        if command == "help":
            return (
                "LearnLoop Agent commands:\n"
                "/start or /help — show this guide\n"
                "/pages — list indexed Notion pages with full hierarchy paths\n"
                "/ingest — upload a PDF or image, then choose a target page button\n"
                "/ingest --page <external_page_id> — text fallback for automation\n"
                "/ask <question> — ask about indexed notes; optional --page/--section scopes\n"
                "/accept <proposal_id> — explicitly accept one pending proposal\n"
                "/reject <proposal_id> <reason> — reject without a Notion write\n"
                "/health — check bot status\n\n"
                "You do not need to type a Notion UUID for ingestion. "
                "After upload, choose the parent or child page from the buttons. "
                "Accept is always an explicit human action; proposals without a "
                "target cannot be accepted."
            )
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
