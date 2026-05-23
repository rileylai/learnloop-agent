from __future__ import annotations

import hashlib
from dataclasses import dataclass

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import get_tool_registry
from src.app.main import app
from src.db.base import Base
from src.db.models import NotionBlock, NotionPage, SourceDocument, WorkflowRun
from src.db.session import get_db_session
from src.tools import PDFParserClient, PDFParserClientError, PDFParserTool, ToolRegistry


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


def _build_session_factory():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            SourceDocument.__table__,
            WorkflowRun.__table__,
            NotionPage.__table__,
            NotionBlock.__table__,
        ],
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _build_tool_registry_with_pdf_parser(parser_client: PDFParserClient) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register_tool(PDFParserTool(parser_client))
    return registry


def test_ingest_source_api_creates_one_document_per_supported_source_type() -> None:
    session_factory = _build_session_factory()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = _db_override

    try:
        client = TestClient(app)
        payloads = [
            ("pdf", "lecture1.pdf", "Transformer notes from lecture 1"),
            ("url", "https://example.com/nlp", "Article summary about attention"),
            ("youtube", "NLP Crash Course", "Transcript text for decoder block"),
            ("screenshot", "week5-screenshots", "OCR text from three screenshots"),
            ("chat_text", "chat-2026-05-24", "Pasted chat text with key concepts"),
        ]

        response_bodies = []
        for source_type, display_name, raw_text in payloads:
            response = client.post(
                "/api/ingest/source",
                json={
                    "source_type": source_type,
                    "source_display_name": display_name,
                    "raw_text": raw_text,
                },
            )
            assert response.status_code == 200
            body = response.json()
            assert body["status"] == "succeeded"
            assert body["source_type"] == source_type
            assert body["source_display_name"] == display_name
            assert body["content_hash"] == hashlib.sha256(
                raw_text.encode("utf-8")
            ).hexdigest()
            response_bodies.append(body)

        session: Session = session_factory()
        try:
            source_documents = session.query(SourceDocument).order_by(SourceDocument.id.asc()).all()
            assert len(source_documents) == len(payloads)
            assert {row.source_type for row in source_documents} == {
                "pdf",
                "url",
                "youtube",
                "screenshot",
                "chat_text",
            }

            workflow_runs = session.query(WorkflowRun).order_by(WorkflowRun.id.asc()).all()
            assert len(workflow_runs) == len(payloads)
            assert {row.workflow_type for row in workflow_runs} == {"ingestion"}
            assert {row.status for row in workflow_runs} == {"succeeded"}

            returned_source_ids = {body["source_document_id"] for body in response_bodies}
            persisted_source_ids = {row.id for row in source_documents}
            assert returned_source_ids == persisted_source_ids
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_ingest_source_api_rejects_unsupported_source_type() -> None:
    session_factory = _build_session_factory()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = _db_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/ingest/source",
            json={
                "source_type": "audio",
                "source_display_name": "podcast-episode",
                "raw_text": "audio transcript text",
            },
        )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert detail["error_code"] == "INVALID_ARGUMENT"
        assert detail["failure_reason"] == "UNKNOWN_ERROR"

        session: Session = session_factory()
        try:
            assert session.query(SourceDocument).count() == 0
            assert session.query(WorkflowRun).count() == 0
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_ingest_source_api_rejects_blank_raw_text() -> None:
    session_factory = _build_session_factory()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = _db_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/ingest/source",
            json={
                "source_type": "chat_text",
                "source_display_name": "chat-empty",
                "raw_text": "   ",
            },
        )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert detail["error_code"] == "INVALID_ARGUMENT"
        assert detail["message"] == "raw_text must not be empty"

        session: Session = session_factory()
        try:
            assert session.query(SourceDocument).count() == 0
            assert session.query(WorkflowRun).count() == 0
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_ingest_document_api_persists_extracted_pdf_text_and_filename() -> None:
    session_factory = _build_session_factory()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_tool_registry_with_pdf_parser(
            _FakePDFParserClient(raw_text="Transformer attention summary", page_count=2)
        )

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/ingest/document",
            files={
                "document": (
                    "lecture-week5.pdf",
                    b"%PDF-1.4 fake-pdf-content",
                    "application/pdf",
                )
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["source_type"] == "pdf"
        assert payload["source_display_name"] == "lecture-week5.pdf"
        assert payload["content_hash"] == hashlib.sha256(
            "Transformer attention summary".encode("utf-8")
        ).hexdigest()

        session: Session = session_factory()
        try:
            source_document = session.get(SourceDocument, payload["source_document_id"])
            assert source_document is not None
            assert source_document.source_type == "pdf"
            assert source_document.source_display_name == "lecture-week5.pdf"
            assert source_document.raw_text == "Transformer attention summary"

            workflow_run = session.get(WorkflowRun, payload["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.workflow_type == "ingestion"
            assert workflow_run.status == "succeeded"
            assert workflow_run.failure_reason is None

            # Step 21 must not perform Notion writes.
            assert session.query(NotionPage).count() == 0
            assert session.query(NotionBlock).count() == 0
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_ingest_document_api_returns_pdf_parse_failed() -> None:
    session_factory = _build_session_factory()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_tool_registry_with_pdf_parser(
            _FakePDFParserClient(
                should_fail=True,
                failure_message="no extractable text",
            )
        )

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/ingest/document",
            files={
                "document": (
                    "bad.pdf",
                    b"%PDF-1.4 invalid",
                    "application/pdf",
                )
            },
        )
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert detail["error_code"] == "PDF_PARSE_FAILED"
        assert detail["failure_reason"] == "PDF_PARSE_FAILED"
        assert detail["workflow_run_id"] is not None

        session: Session = session_factory()
        try:
            assert session.query(SourceDocument).count() == 0
            workflow_run = session.get(WorkflowRun, detail["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.workflow_type == "ingestion"
            assert workflow_run.status == "failed"
            assert workflow_run.failure_reason == "PDF_PARSE_FAILED"
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()
