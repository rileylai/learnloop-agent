from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import get_tool_registry
from src.app.main import app
from src.db.base import Base
from src.db.models import WorkflowRun
from src.db.session import get_db_session
from src.tools import (
    DisabledTelegramBotClient,
    InMemoryTelegramBotClient,
    TelegramBotTool,
    ToolRegistry,
)


def _build_session_factory():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[WorkflowRun.__table__],
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
        assert payload["reply_text"] == "Available commands: /help, /health"
        assert payload["telegram_message_id"] == 1
        assert payload["skipped_reason"] is None

        sent_messages = telegram_client.list_sent_messages()
        assert len(sent_messages) == 1
        assert sent_messages[0].chat_id == "555"
        assert sent_messages[0].text == "Available commands: /help, /health"

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
