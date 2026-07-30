from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel, Field


class TelegramChatPayload(BaseModel):
    id: int


class TelegramUserPayload(BaseModel):
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
    from_user: Optional[TelegramUserPayload] = Field(default=None, alias="from")
    text: Optional[str] = None
    caption: Optional[str] = None
    media_group_id: Optional[str] = None
    document: Optional[TelegramDocumentPayload] = None
    photo: List[TelegramPhotoPayload] = Field(default_factory=list)


class TelegramCallbackQueryPayload(BaseModel):
    id: str
    from_user: TelegramUserPayload = Field(alias="from")
    message: Optional[TelegramMessagePayload] = None
    data: Optional[str] = None


class TelegramWebhookRequest(BaseModel):
    update_id: Optional[int] = None
    message: Optional[TelegramMessagePayload] = None
    callback_query: Optional[TelegramCallbackQueryPayload] = None


class TelegramWebhookResponse(BaseModel):
    workflow_run_id: Optional[int] = None
    status: str
    handled: bool
    command: Optional[str] = None
    reply_text: Optional[str] = None
    telegram_message_id: Optional[int] = None
    skipped_reason: Optional[str] = None
    source_document_id: Optional[int] = None
    change_request_id: Optional[int] = None
    source_type: Optional[str] = None
    target_notion_page_id: Optional[str] = None
    qa_workflow_run_id: Optional[int] = None
    insufficient_info: Optional[bool] = None
    citations: List[str] = Field(default_factory=list)
    review_workflow_run_id: Optional[int] = None
    review_action: Optional[str] = None
    change_request_status: Optional[str] = None
    target_set: bool = False
    business_status: str = "not_started"
    callback_ack_status: Optional[str] = None
    preview_delivery_status: Optional[str] = None
