from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import (
    get_queue_client,
    get_tool_registry,
)
from src.app.main import app
from src.db.base import Base
from src.db.models import TelegramUpdateLedger, WorkflowRun
from src.db.unit_of_work import SqlAlchemyUnitOfWork
from src.db.session import (
    get_db_session,
    get_db_session_factory,
    get_unit_of_work_factory,
)
from src.orchestrators import TelegramGatewayOrchestrator
from src.queue import FakeQueueClient
from src.services import TelegramUpdateIdempotencyService, WorkflowRunService
from src.tools import InMemoryTelegramBotClient, TelegramBotTool, ToolRegistry


def _build_session_factory():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[WorkflowRun.__table__, TelegramUpdateLedger.__table__],
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def test_gateway_claims_once_and_enqueues_once() -> None:
    import asyncio

    session_factory = _build_session_factory()
    queue_client = FakeQueueClient()
    gateway = TelegramGatewayOrchestrator(
        tool_registry=ToolRegistry(),
        workflow_run_service=WorkflowRunService(session_factory),
        update_idempotency_service=TelegramUpdateIdempotencyService(
            session_factory
        ),
        queue_client=queue_client,
    )

    first = asyncio.run(
        gateway.enqueue_webhook(
            update_id=7001,
            chat_id="555",
            text="/ask private question",
            caption=None,
            document=None,
            photos=[],
            request_workflow_id="request-7001",
        )
    )
    second = asyncio.run(
        gateway.enqueue_webhook(
            update_id=7001,
            chat_id="555",
            text="/ask private question",
            caption=None,
            document=None,
            photos=[],
            request_workflow_id="request-7001-retry",
        )
    )

    assert first.status == "running"
    assert first.skipped_reason == "QUEUED"
    assert second.status == "running"
    assert second.skipped_reason == "DUPLICATE_UPDATE_IN_PROGRESS"
    assert len(queue_client.enqueued_jobs) == 1

    session = session_factory()
    try:
        ledger = session.get(TelegramUpdateLedger, 7001)
        assert ledger is not None
        assert ledger.status == "running"
    finally:
        session.close()


def test_webhook_returns_fast_ack_when_queue_is_configured() -> None:
    session_factory = _build_session_factory()
    queue_client = FakeQueueClient()
    telegram_client = InMemoryTelegramBotClient()
    registry = ToolRegistry()
    registry.register_tool(TelegramBotTool(telegram_client))

    def db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_tool_registry] = lambda: registry
    app.dependency_overrides[get_queue_client] = lambda: queue_client

    try:
        response = TestClient(app).post(
            "/api/telegram/webhook",
            json={
                "update_id": 7002,
                "message": {
                    "message_id": 1,
                    "chat": {"id": 555},
                    "text": "/health",
                },
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json()["status"] == "running"
    assert response.json()["skipped_reason"] == "QUEUED"
    assert len(queue_client.enqueued_jobs) == 1
    assert telegram_client.list_sent_messages() == []
