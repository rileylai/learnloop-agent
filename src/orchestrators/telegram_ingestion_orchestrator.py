from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from http import HTTPStatus
from typing import Dict, List, Optional

from src.orchestrators.document_ingestion_orchestrator import (
    DocumentIngestionError,
    DocumentIngestionOrchestrator,
)
from src.orchestrators.image_ocr_ingestion_orchestrator import (
    ImageOCRIngestionError,
    ImageOCRIngestionOrchestrator,
    ImageUploadInput,
)
from src.orchestrators.supplement_propose_orchestrator import (
    DEFAULT_SUPPLEMENT_MODEL,
    DEFAULT_SUPPLEMENT_PROVIDER_NAME,
    SupplementProposeError,
    SupplementProposeOrchestrator,
)
from src.services import STANDARD_FAILURE_REASONS
from src.tools import ToolContext, ToolRegistry

TELEGRAM_BOT_TOOL_NAME = "telegram_bot"

TOOL_ERROR_TO_HTTP_STATUS: Dict[str, int] = {
    "INVALID_ARGUMENT": HTTPStatus.BAD_REQUEST,
    "TELEGRAM_NOT_CONFIGURED": HTTPStatus.SERVICE_UNAVAILABLE,
    "TELEGRAM_FILE_DOWNLOAD_FAILED": HTTPStatus.BAD_GATEWAY,
}


@dataclass
class TelegramDocumentAttachment:
    file_id: str
    file_name: Optional[str] = None


@dataclass
class TelegramPhotoAttachment:
    file_id: str
    file_unique_id: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class TelegramIngestionCommandResult:
    reply_text: str
    source_document_id: Optional[int]
    change_request_id: Optional[int]
    source_type: Optional[str]


class TelegramIngestionError(Exception):
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


class TelegramIngestionOrchestrator:
    def __init__(
        self,
        *,
        tool_registry: ToolRegistry,
        document_ingestion_orchestrator: DocumentIngestionOrchestrator,
        image_ocr_ingestion_orchestrator: ImageOCRIngestionOrchestrator,
        supplement_propose_orchestrator: SupplementProposeOrchestrator,
    ) -> None:
        self._tool_registry = tool_registry
        self._document_ingestion_orchestrator = document_ingestion_orchestrator
        self._image_ocr_ingestion_orchestrator = image_ocr_ingestion_orchestrator
        self._supplement_propose_orchestrator = supplement_propose_orchestrator

    async def handle_ingest_command(
        self,
        *,
        chat_id: str,
        document: Optional[TelegramDocumentAttachment],
        photos: List[TelegramPhotoAttachment],
        request_workflow_id: str,
    ) -> TelegramIngestionCommandResult:
        _ = chat_id
        normalized_photos = self._deduplicate_photos(photos)
        if document is None and not normalized_photos:
            return TelegramIngestionCommandResult(
                reply_text=(
                    "Use /ingest with one PDF document or one/more screenshots."
                ),
                source_document_id=None,
                change_request_id=None,
                source_type=None,
            )

        try:
            if document is not None:
                source_result = await self._ingest_pdf_document(
                    document=document,
                    request_workflow_id=request_workflow_id,
                )
                source_count = 1
            else:
                source_result = await self._ingest_screenshot_batch(
                    photos=normalized_photos,
                    request_workflow_id=request_workflow_id,
                )
                source_count = len(normalized_photos)

            proposal_result = await self._supplement_propose_orchestrator.propose_change_request(
                source_document_id=source_result.source_document_id,
                provider_name=DEFAULT_SUPPLEMENT_PROVIDER_NAME,
                model=DEFAULT_SUPPLEMENT_MODEL,
                request_workflow_id=request_workflow_id,
            )
        except (DocumentIngestionError, ImageOCRIngestionError, SupplementProposeError) as exc:
            raise TelegramIngestionError(
                error_code=exc.error_code,
                message=exc.message,
                http_status_code=exc.http_status_code,
                failure_reason=self._normalize_failure_reason(exc.failure_reason),
                workflow_run_id=exc.workflow_run_id,
            ) from exc

        return TelegramIngestionCommandResult(
            reply_text=self._build_success_reply(
                source_type=source_result.source_type,
                source_document_id=source_result.source_document_id,
                change_request_id=proposal_result.change_request_id,
                source_count=source_count,
            ),
            source_document_id=source_result.source_document_id,
            change_request_id=proposal_result.change_request_id,
            source_type=source_result.source_type,
        )

    async def _ingest_pdf_document(
        self,
        *,
        document: TelegramDocumentAttachment,
        request_workflow_id: str,
    ):
        downloaded = await self._download_telegram_file(
            file_id=document.file_id,
            request_workflow_id=request_workflow_id,
        )

        source_file_name = (document.file_name or "").strip() or downloaded.file_name
        if not source_file_name.lower().endswith(".pdf"):
            raise TelegramIngestionError(
                error_code="INVALID_ARGUMENT",
                message="/ingest document must be a .pdf file",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            )

        return await self._document_ingestion_orchestrator.ingest_document(
            file_name=source_file_name,
            file_bytes=downloaded.file_bytes,
            request_workflow_id=request_workflow_id,
        )

    async def _ingest_screenshot_batch(
        self,
        *,
        photos: List[TelegramPhotoAttachment],
        request_workflow_id: str,
    ):
        image_inputs: List[ImageUploadInput] = []
        for index, photo in enumerate(photos, start=1):
            downloaded = await self._download_telegram_file(
                file_id=photo.file_id,
                request_workflow_id=request_workflow_id,
            )
            image_file_name = downloaded.file_name.strip() or f"telegram-screenshot-{index}.jpg"
            image_inputs.append(
                ImageUploadInput(
                    file_name=image_file_name,
                    file_bytes=downloaded.file_bytes,
                )
            )

        return await self._image_ocr_ingestion_orchestrator.ingest_image_ocr(
            images=image_inputs,
            request_workflow_id=request_workflow_id,
        )

    async def _download_telegram_file(
        self,
        *,
        file_id: str,
        request_workflow_id: str,
    ):
        normalized_file_id = file_id.strip()
        if not normalized_file_id:
            raise TelegramIngestionError(
                error_code="INVALID_ARGUMENT",
                message="file_id is required",
                http_status_code=HTTPStatus.BAD_REQUEST,
                failure_reason="UNKNOWN_ERROR",
            )

        tool_result = await self._tool_registry.call_tool(
            TELEGRAM_BOT_TOOL_NAME,
            context=ToolContext(
                workflow_id=request_workflow_id,
                metadata={
                    "operation": "telegram_file_download",
                    "file_id": normalized_file_id,
                },
            ),
            arguments={
                "action": "download_file",
                "file_id": normalized_file_id,
            },
        )
        if tool_result.is_error:
            error_code = "UNKNOWN_ERROR"
            error_message = "Telegram file download failed"
            if tool_result.error is not None:
                error_code = tool_result.error.code
                error_message = tool_result.error.message
            raise TelegramIngestionError(
                error_code=error_code,
                message=error_message,
                http_status_code=TOOL_ERROR_TO_HTTP_STATUS.get(
                    error_code,
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                ),
                failure_reason=self._normalize_failure_reason(error_code),
            )

        structured_content = tool_result.structured_content or {}
        encoded = str(structured_content.get("file_bytes_base64", "")).strip()
        if not encoded:
            raise TelegramIngestionError(
                error_code="TOOL_OUTPUT_INVALID",
                message="telegram_bot download_file output missing file_bytes_base64",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
            )
        try:
            file_bytes = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise TelegramIngestionError(
                error_code="TOOL_OUTPUT_INVALID",
                message=f"telegram_bot download_file output is invalid base64: {exc}",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
            ) from exc
        if not file_bytes:
            raise TelegramIngestionError(
                error_code="TOOL_OUTPUT_INVALID",
                message="telegram_bot download_file output contains empty bytes",
                http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                failure_reason="UNKNOWN_ERROR",
            )

        file_name = str(structured_content.get("file_name", "")).strip()
        if not file_name:
            file_name = f"{normalized_file_id}.bin"

        return _DownloadedTelegramFile(
            file_name=file_name,
            file_bytes=file_bytes,
        )

    def _deduplicate_photos(
        self,
        photos: List[TelegramPhotoAttachment],
    ) -> List[TelegramPhotoAttachment]:
        deduplicated: Dict[str, TelegramPhotoAttachment] = {}
        for photo in photos:
            normalized_file_id = photo.file_id.strip()
            if not normalized_file_id:
                continue
            dedupe_key = (photo.file_unique_id or "").strip() or normalized_file_id
            current = deduplicated.get(dedupe_key)
            if current is None:
                deduplicated[dedupe_key] = TelegramPhotoAttachment(
                    file_id=normalized_file_id,
                    file_unique_id=(photo.file_unique_id or "").strip() or None,
                    file_size=photo.file_size,
                )
                continue

            current_size = current.file_size or 0
            incoming_size = photo.file_size or 0
            if incoming_size > current_size:
                deduplicated[dedupe_key] = TelegramPhotoAttachment(
                    file_id=normalized_file_id,
                    file_unique_id=(photo.file_unique_id or "").strip() or None,
                    file_size=photo.file_size,
                )

        return list(deduplicated.values())

    def _build_success_reply(
        self,
        *,
        source_type: str,
        source_document_id: int,
        change_request_id: int,
        source_count: int,
    ) -> str:
        if source_type == "screenshot":
            return (
                "Ingestion succeeded "
                f"(screenshots={source_count}, source_document_id={source_document_id}, "
                f"change_request_id={change_request_id}, status=pending)."
            )
        return (
            "Ingestion succeeded "
            f"(source_type={source_type}, source_document_id={source_document_id}, "
            f"change_request_id={change_request_id}, status=pending)."
        )

    def _normalize_failure_reason(self, failure_reason: str) -> str:
        normalized = failure_reason.strip().upper()
        if normalized in STANDARD_FAILURE_REASONS:
            return normalized
        return "UNKNOWN_ERROR"


@dataclass
class _DownloadedTelegramFile:
    file_name: str
    file_bytes: bytes
