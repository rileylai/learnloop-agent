from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel, Field


class TelegramChatPayload(BaseModel):
    id: int


class TelegramDocumentPayload(BaseModel):
    file_id: str
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class TelegramPhotoPayload(BaseModel):
    file_id: str
    file_unique_id: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None


class TelegramMessagePayload(BaseModel):
    message_id: int
    chat: TelegramChatPayload
    text: Optional[str] = None
    caption: Optional[str] = None
    document: Optional[TelegramDocumentPayload] = None
    photo: List[TelegramPhotoPayload] = Field(default_factory=list)


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
    source_document_id: Optional[int] = None
    change_request_id: Optional[int] = None
    source_type: Optional[str] = None
