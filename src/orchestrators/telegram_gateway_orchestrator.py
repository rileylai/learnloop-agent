from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Dict, Optional

from src.services import STANDARD_FAILURE_REASONS, WorkflowRunService
from src.tools import ToolContext, ToolRegistry

TELEGRAM_BOT_TOOL_NAME = "telegram_bot"


@dataclass
class TelegramGatewayResult:
    workflow_run_id: int
    status: str
    handled: bool
    command: Optional[str]
    reply_text: Optional[str]
    telegram_message_id: Optional[int]
    skipped_reason: Optional[str]


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
    ) -> None:
        self._tool_registry = tool_registry
        self._workflow_run_service = workflow_run_service

    async def handle_webhook(
        self,
        *,
        update_id: Optional[int],
        chat_id: Optional[str],
        text: Optional[str],
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
                },
                sort_keys=True,
            ),
        )

        try:
            normalized_text = (text or "").strip()
            normalized_chat_id = (chat_id or "").strip()
            if not normalized_chat_id or not normalized_text:
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
                )

            command = self._parse_command(normalized_text)
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
            )
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
                message=f"Telegram gateway workflow failed: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
                workflow_run_id=workflow_run.id,
            ) from exc

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
            return "Available commands: /help, /health"
        return "Unsupported command. Use /help."

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
