from __future__ import annotations

import hashlib

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.main import app
from src.db.base import Base
from src.db.models import SourceDocument, WorkflowRun
from src.db.session import get_db_session


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
        ],
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


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
