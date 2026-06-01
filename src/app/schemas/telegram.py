from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TelegramChatPayload(BaseModel):
    id: int


class TelegramMessagePayload(BaseModel):
    message_id: int
    chat: TelegramChatPayload
    text: Optional[str] = None


class TelegramWebhookRequest(BaseModel):
    update_id: Optional[int] = None
    message: Optional[TelegramMessagePayload] = None


class TelegramWebhookResponse(BaseModel):
    workflow_run_id: int
    status: str
    handled: bool
    command: Optional[str] = None
    reply_text: Optional[str] = None
    telegram_message_id: Optional[int] = None
    skipped_reason: Optional[str] = None
