from __future__ import annotations

import json
from dataclasses import dataclass

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import get_provider_router, get_tool_registry
from src.app.main import app
from src.db.base import Base
from src.db.models import (
    ChangeRequest,
    KnowledgeChunk,
    NotionBlock,
    NotionPage,
    SourceDocument,
    WorkflowRun,
)
from src.db.session import get_db_session
from src.providers import LLMProvider, LLMRequest, LLMResponse, ProviderRouter
from src.tools import (
    DisabledTelegramBotClient,
    ImageOCRParserClient,
    ImageOCRTool,
    InMemoryTelegramBotClient,
    OCRImageInput,
    PDFParserClient,
    PDFParserClientError,
    PDFParserTool,
    ParsedImageOCR,
    TelegramBotTool,
    ToolRegistry,
)


@dataclass
class _FakeParsedPDF:
    raw_text: str
    page_count: int


class _FakePDFParserClient(PDFParserClient):
    def __init__(
        self,
        *,
        raw_text: str = "",
        page_count: int = 1,
        should_fail: bool = False,
        failure_message: str = "parse failed",
    ) -> None:
        self._raw_text = raw_text
        self._page_count = page_count
        self._should_fail = should_fail
        self._failure_message = failure_message

    def parse_document(self, *, file_name: str, file_bytes: bytes):
        _ = file_name
        _ = file_bytes
        if self._should_fail:
            raise PDFParserClientError(self._failure_message)
        return _FakeParsedPDF(raw_text=self._raw_text, page_count=self._page_count)


class _FakeImageOCRParserClient(ImageOCRParserClient):
    def parse_images(self, *, images: list[OCRImageInput]) -> ParsedImageOCR:
        lines = [
            f"OCR[{index}] {image.file_name}"
            for index, image in enumerate(images, start=1)
        ]
        return ParsedImageOCR(
            raw_text="\n".join(lines),
            image_count=len(images),
        )


class _FakeProposalProvider(LLMProvider):
    def __init__(self, *, output_text: str) -> None:
        self._output_text = output_text

    @property
    def name(self) -> str:
        return "openai"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        _ = request
        return LLMResponse(
            provider="openai",
            model="gpt-4o-mini",
            output_text=self._output_text,
            token_input=120,
            token_output=80,
        )


def _build_session_factory():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            WorkflowRun.__table__,
            SourceDocument.__table__,
            ChangeRequest.__table__,
            KnowledgeChunk.__table__,
            NotionBlock.__table__,
            NotionPage.__table__,
        ],
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def test_telegram_webhook_help_command_sends_reply() -> None:
    session_factory = _build_session_factory()
    telegram_client = InMemoryTelegramBotClient()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        registry = ToolRegistry()
        registry.register_tool(TelegramBotTool(telegram_client))
        return registry

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/telegram/webhook",
            json={
                "update_id": 1001,
                "message": {
                    "message_id": 11,
                    "chat": {"id": 555},
                    "text": "/help",
                },
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["handled"] is True
        assert payload["command"] == "help"
        assert payload["reply_text"] == "Available commands: /help, /health, /ingest"
        assert payload["telegram_message_id"] == 1
        assert payload["skipped_reason"] is None
        assert payload["source_document_id"] is None
        assert payload["change_request_id"] is None
        assert payload["source_type"] is None

        sent_messages = telegram_client.list_sent_messages()
        assert len(sent_messages) == 1
        assert sent_messages[0].chat_id == "555"
        assert sent_messages[0].text == "Available commands: /help, /health, /ingest"

        verify_session: Session = session_factory()
        try:
            workflow_run = verify_session.get(WorkflowRun, payload["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.workflow_type == "telegram"
            assert workflow_run.status == "succeeded"
            metadata = json.loads(workflow_run.metadata_json or "{}")
            assert metadata["operation"] == "telegram_webhook"
            assert metadata["command"] == "help"
            assert metadata["handled"] is True
            assert metadata["telegram_message_id"] == 1
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_telegram_webhook_skips_non_text_message() -> None:
    session_factory = _build_session_factory()
    telegram_client = InMemoryTelegramBotClient()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        registry = ToolRegistry()
        registry.register_tool(TelegramBotTool(telegram_client))
        return registry

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/telegram/webhook",
            json={
                "update_id": 1002,
                "message": {
                    "message_id": 12,
                    "chat": {"id": 888},
                    "text": "   ",
                },
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["handled"] is False
        assert payload["command"] is None
        assert payload["reply_text"] is None
        assert payload["telegram_message_id"] is None
        assert payload["skipped_reason"] == "NO_TEXT_MESSAGE"
        assert telegram_client.list_sent_messages() == []
    finally:
        app.dependency_overrides.clear()


def test_telegram_webhook_returns_service_unavailable_when_not_configured() -> None:
    session_factory = _build_session_factory()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        registry = ToolRegistry()
        registry.register_tool(TelegramBotTool(DisabledTelegramBotClient()))
        return registry

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/telegram/webhook",
            json={
                "update_id": 1003,
                "message": {
                    "message_id": 13,
                    "chat": {"id": 999},
                    "text": "/health",
                },
            },
        )

        assert response.status_code == 503
        detail = response.json()["detail"]
        assert detail["error_code"] == "TELEGRAM_NOT_CONFIGURED"
        assert detail["failure_reason"] == "UNKNOWN_ERROR"
        assert detail["workflow_run_id"] is not None

        verify_session: Session = session_factory()
        try:
            workflow_run = verify_session.get(WorkflowRun, detail["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.workflow_type == "telegram"
            assert workflow_run.status == "failed"
            assert workflow_run.failure_reason == "UNKNOWN_ERROR"
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_telegram_webhook_ingest_pdf_creates_pending_change_request() -> None:
    session_factory = _build_session_factory()
    telegram_client = InMemoryTelegramBotClient()
    telegram_client.add_file(
        file_id="pdf-file-1",
        file_bytes=b"%PDF-1.4 fake content",
        file_name="lesson.pdf",
    )

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        registry = ToolRegistry()
        registry.register_tool(TelegramBotTool(telegram_client))
        registry.register_tool(
            PDFParserTool(
                _FakePDFParserClient(
                    raw_text="Transformer training notes from week 5",
                    page_count=1,
                )
            )
        )
        registry.register_tool(ImageOCRTool(_FakeImageOCRParserClient()))
        return registry

    def _provider_router_override() -> ProviderRouter:
        router = ProviderRouter()
        router.register_provider(
            _FakeProposalProvider(
                output_text=json.dumps(
                    {
                        "title": "Transformer Week 5 Supplement",
                        "target_path": "Knowledge/NLP/Week5/AI Supplement Zone/Transformer Week 5",
                        "source": {
                            "source_type": "pdf",
                            "source_display_name": "lesson.pdf",
                        },
                        "summary": "Summarizes transformer training notes from the source PDF.",
                        "concepts": ["transformer", "training stability"],
                        "notes": ["Review optimizer and warmup settings."],
                    }
                )
            )
        )
        return router

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_tool_registry] = _tool_registry_override
    app.dependency_overrides[get_provider_router] = _provider_router_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/telegram/webhook",
            json={
                "update_id": 2001,
                "message": {
                    "message_id": 21,
                    "chat": {"id": 12345},
                    "caption": "/ingest",
                    "document": {
                        "file_id": "pdf-file-1",
                        "file_name": "lesson.pdf",
                        "mime_type": "application/pdf",
                    },
                },
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["handled"] is True
        assert payload["command"] == "ingest"
        assert payload["source_type"] == "pdf"
        assert payload["source_document_id"] is not None
        assert payload["change_request_id"] is not None
        assert "status=pending" in (payload["reply_text"] or "")

        sent_messages = telegram_client.list_sent_messages()
        assert len(sent_messages) == 1
        assert sent_messages[0].chat_id == "12345"
        assert "change_request_id" in sent_messages[0].text

        verify_session: Session = session_factory()
        try:
            source_documents = verify_session.query(SourceDocument).all()
            assert len(source_documents) == 1
            assert source_documents[0].source_type == "pdf"
            assert source_documents[0].source_display_name == "lesson.pdf"

            change_requests = verify_session.query(ChangeRequest).all()
            assert len(change_requests) == 1
            assert change_requests[0].status == "pending"
            assert change_requests[0].source_document_id == source_documents[0].id

            workflow_runs = verify_session.query(WorkflowRun).all()
            assert any(row.workflow_type == "telegram" for row in workflow_runs)
            assert any(row.workflow_type == "ingestion" for row in workflow_runs)
            assert any(row.workflow_type == "supplement" for row in workflow_runs)
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_telegram_webhook_ingest_screenshot_batch_creates_one_source_and_change_request() -> None:
    session_factory = _build_session_factory()
    telegram_client = InMemoryTelegramBotClient()
    telegram_client.add_file(
        file_id="photo-a",
        file_bytes=b"image-a-bytes",
        file_name="screenshot-a.png",
    )
    telegram_client.add_file(
        file_id="photo-b",
        file_bytes=b"image-b-bytes",
        file_name="screenshot-b.png",
    )

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        registry = ToolRegistry()
        registry.register_tool(TelegramBotTool(telegram_client))
        registry.register_tool(
            PDFParserTool(
                _FakePDFParserClient(
                    raw_text="fallback pdf text",
                    page_count=1,
                )
            )
        )
        registry.register_tool(ImageOCRTool(_FakeImageOCRParserClient()))
        return registry

    def _provider_router_override() -> ProviderRouter:
        router = ProviderRouter()
        router.register_provider(
            _FakeProposalProvider(
                output_text=json.dumps(
                    {
                        "title": "OCR Screenshot Supplement",
                        "target_path": "Knowledge/NLP/Week5/AI Supplement Zone/OCR Screenshot Supplement",
                        "source": {
                            "source_type": "screenshot",
                            "source_display_name": "Screenshot batch (2 images)",
                        },
                        "summary": "Summarizes OCR text extracted from screenshot batch.",
                        "concepts": ["ocr capture", "batch notes"],
                        "notes": ["Validate extracted terms before accept."],
                    }
                )
            )
        )
        return router

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_tool_registry] = _tool_registry_override
    app.dependency_overrides[get_provider_router] = _provider_router_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/telegram/webhook",
            json={
                "update_id": 2002,
                "message": {
                    "message_id": 22,
                    "chat": {"id": 54321},
                    "caption": "/ingest",
                    "photo": [
                        {
                            "file_id": "photo-a",
                            "file_unique_id": "uniq-a",
                            "width": 1200,
                            "height": 800,
                            "file_size": 80000,
                        },
                        {
                            "file_id": "photo-b",
                            "file_unique_id": "uniq-b",
                            "width": 1200,
                            "height": 800,
                            "file_size": 81000,
                        },
                    ],
                },
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["handled"] is True
        assert payload["command"] == "ingest"
        assert payload["source_type"] == "screenshot"
        assert payload["source_document_id"] is not None
        assert payload["change_request_id"] is not None
        assert "screenshots=2" in (payload["reply_text"] or "")

        verify_session: Session = session_factory()
        try:
            source_documents = verify_session.query(SourceDocument).all()
            assert len(source_documents) == 1
            assert source_documents[0].source_type == "screenshot"
            assert source_documents[0].source_display_name == "Screenshot batch (2 images)"

            change_requests = verify_session.query(ChangeRequest).all()
            assert len(change_requests) == 1
            assert change_requests[0].status == "pending"
            assert change_requests[0].source_document_id == source_documents[0].id
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()
