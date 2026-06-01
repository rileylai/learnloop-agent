from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib import error, request

from src.tools.base import Tool
from src.tools.models import ToolContext, ToolResult, ToolSpec


class TelegramBotClientError(Exception):
    pass


class TelegramBotNotConfiguredError(TelegramBotClientError):
    pass


class TelegramBotSendError(TelegramBotClientError):
    pass


@dataclass
class TelegramSentMessage:
    chat_id: str
    text: str
    message_id: int


class TelegramBotClient:
    def send_message(self, *, chat_id: str, text: str) -> TelegramSentMessage:
        raise NotImplementedError


class DisabledTelegramBotClient(TelegramBotClient):
    def send_message(self, *, chat_id: str, text: str) -> TelegramSentMessage:
        _ = chat_id
        _ = text
        raise TelegramBotNotConfiguredError(
            "Telegram bot token is not configured. Set TELEGRAM_BOT_TOKEN."
        )


class InMemoryTelegramBotClient(TelegramBotClient):
    def __init__(self) -> None:
        self._sent_messages: List[TelegramSentMessage] = []

    def send_message(self, *, chat_id: str, text: str) -> TelegramSentMessage:
        message = TelegramSentMessage(
            chat_id=chat_id,
            text=text,
            message_id=len(self._sent_messages) + 1,
        )
        self._sent_messages.append(message)
        return message

    def list_sent_messages(self) -> List[TelegramSentMessage]:
        return list(self._sent_messages)


class TelegramHTTPBotClient(TelegramBotClient):
    def __init__(
        self,
        *,
        bot_token: str,
        timeout_seconds: float = 10.0,
    ) -> None:
        normalized_token = bot_token.strip()
        if not normalized_token:
            raise TelegramBotNotConfiguredError(
                "Telegram bot token is empty. Set TELEGRAM_BOT_TOKEN."
            )
        self._bot_token = normalized_token
        self._timeout_seconds = timeout_seconds

    def send_message(self, *, chat_id: str, text: str) -> TelegramSentMessage:
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        req = request.Request(
            url=f"https://api.telegram.org/bot{self._bot_token}/sendMessage",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self._timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except error.URLError as exc:
            raise TelegramBotSendError(f"Telegram request failed: {exc}") from exc

        try:
            parsed = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise TelegramBotSendError(
                "Telegram response is not valid JSON"
            ) from exc

        if not isinstance(parsed, dict) or not parsed.get("ok"):
            description = ""
            if isinstance(parsed, dict):
                description = str(parsed.get("description", "")).strip()
            if description:
                raise TelegramBotSendError(f"Telegram sendMessage failed: {description}")
            raise TelegramBotSendError("Telegram sendMessage failed")

        result = parsed.get("result")
        if not isinstance(result, dict):
            raise TelegramBotSendError("Telegram response missing result object")

        raw_message_id = result.get("message_id")
        try:
            message_id = int(raw_message_id)
        except (TypeError, ValueError) as exc:
            raise TelegramBotSendError(
                "Telegram response missing valid message_id"
            ) from exc

        return TelegramSentMessage(
            chat_id=chat_id,
            text=text,
            message_id=message_id,
        )


class TelegramBotTool(Tool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="telegram_bot",
            description="Send Telegram messages through the bot API adapter.",
            input_schema={
                "type": "object",
                "required": ["chat_id", "text"],
                "properties": {
                    "chat_id": {"type": "string"},
                    "text": {"type": "string"},
                },
            },
            output_schema={
                "type": "object",
                "required": ["chat_id", "text", "message_id"],
                "properties": {
                    "chat_id": {"type": "string"},
                    "text": {"type": "string"},
                    "message_id": {"type": "integer"},
                },
            },
        )

    def __init__(self, telegram_client: TelegramBotClient) -> None:
        self._telegram_client = telegram_client

    async def run(self, context: ToolContext, arguments: Dict[str, Any]) -> ToolResult:
        _ = context
        chat_id = str(arguments.get("chat_id", "")).strip()
        text = str(arguments.get("text", "")).strip()

        if not chat_id:
            return ToolResult.failure(
                code="INVALID_ARGUMENT",
                message="chat_id is required",
            )
        if not text:
            return ToolResult.failure(
                code="INVALID_ARGUMENT",
                message="text is required",
            )

        try:
            sent = self._telegram_client.send_message(chat_id=chat_id, text=text)
        except TelegramBotNotConfiguredError as exc:
            return ToolResult.failure(code="TELEGRAM_NOT_CONFIGURED", message=str(exc))
        except TelegramBotSendError as exc:
            return ToolResult.failure(code="TELEGRAM_SEND_FAILED", message=str(exc))
        except TelegramBotClientError as exc:
            return ToolResult.failure(code="UNKNOWN_ERROR", message=str(exc))

        return ToolResult.success(
            content=f"sent telegram message to chat_id={sent.chat_id}",
            structured_content={
                "chat_id": sent.chat_id,
                "text": sent.text,
                "message_id": sent.message_id,
            },
        )
