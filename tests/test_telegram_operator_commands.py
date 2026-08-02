from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import (
    get_embedding_client,
    get_telegram_index_session_store,
    get_telegram_session_store,
    get_telegram_sync_session_store,
    get_tool_registry,
    get_workflow_observability_service,
)
from src.app.main import app
from src.db.base import Base
from src.db.models import TelegramUpdateLedger, WorkflowRun
from src.db.session import get_db_session_factory, get_unit_of_work_factory
from src.db.session import get_db_session
from src.db.unit_of_work import SqlAlchemyUnitOfWork
from src.services import (
    CostBudgetService,
    InMemoryTelegramIndexSessionStore,
    InMemoryTelegramSessionStore,
    InMemoryTelegramSyncSessionStore,
    WorkflowObservabilityService,
    WorkflowRunService,
)
from src.tools import InMemoryTelegramBotClient, TelegramBotTool, ToolRegistry


def _session_factory():
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


def _configure(*, session_factory, telegram_client, observability_service):
    def db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def tool_registry_override() -> ToolRegistry:
        registry = ToolRegistry()
        registry.register_tool(TelegramBotTool(telegram_client))
        return registry

    app.dependency_overrides[get_db_session] = db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_tool_registry] = tool_registry_override
    app.dependency_overrides[get_embedding_client] = lambda: None
    app.dependency_overrides[get_telegram_session_store] = (
        lambda: InMemoryTelegramSessionStore()
    )
    app.dependency_overrides[get_telegram_sync_session_store] = (
        lambda: InMemoryTelegramSyncSessionStore()
    )
    app.dependency_overrides[get_telegram_index_session_store] = (
        lambda: InMemoryTelegramIndexSessionStore()
    )
    app.dependency_overrides[get_workflow_observability_service] = (
        lambda: observability_service
    )


def _seed_workflow(
    session_factory,
    *,
    workflow_type: str,
    metadata: dict[str, object],
    started_at: datetime | None = None,
) -> int:
    workflow = WorkflowRunService(session_factory).start_workflow(
        workflow_type=workflow_type,
        metadata_json=json.dumps(metadata, sort_keys=True),
    )
    session = session_factory()
    try:
        stored = session.get(WorkflowRun, workflow.id)
        assert stored is not None
        stored.status = "succeeded"
        stored.finished_at = datetime.now(timezone.utc)
        if started_at is not None:
            stored.started_at = started_at
        session.commit()
    finally:
        session.close()
    return int(workflow.id)


def _telegram_update(update_id: int, text: str) -> dict[str, object]:
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "chat": {"id": 123},
            "from": {"id": 456},
            "text": text,
        },
    }


def test_cost_scopes_preserve_unknowns_and_split_recorded_cost() -> None:
    now = datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc)
    today = WorkflowRun(
        id=1,
        workflow_type="qa",
        status="succeeded",
        started_at=now,
        metadata_json=json.dumps(
            {"estimated_cost": 0.3, "embedding_estimated_cost": 0.2}
        ),
    )
    unknown = WorkflowRun(
        id=2,
        workflow_type="indexing",
        status="succeeded",
        started_at=now,
        metadata_json=json.dumps({"embedding_estimated_cost": None}),
    )
    old = WorkflowRun(
        id=3,
        workflow_type="qa",
        status="succeeded",
        started_at=now - timedelta(days=8),
        metadata_json=json.dumps({"estimated_cost": 0.9}),
    )
    month_recent = WorkflowRun(
        id=4,
        workflow_type="qa",
        status="succeeded",
        started_at=now - timedelta(days=2),
        metadata_json=json.dumps({"estimated_cost": 0.9}),
    )
    service = CostBudgetService(daily_budget_usd=1.0, workflow_budget_usd=0.4)

    today_summary = service.summarize_scope(
        [today, unknown, old], scope="today", now=now
    )
    assert today_summary.total_cost_usd == pytest.approx(0.5)
    assert today_summary.llm_cost_usd == pytest.approx(0.3)
    assert today_summary.embedding_cost_usd == pytest.approx(0.2)
    assert today_summary.unknown_cost_workflow_count == 1
    assert today_summary.budget_status == "unknown"

    seven_day_summary = service.summarize_scope(
        [today, unknown, old, month_recent], scope="7d", now=now
    )
    assert seven_day_summary.workflow_count == 3
    assert seven_day_summary.total_cost_usd == pytest.approx(1.4)

    month_summary = service.summarize_scope(
        [today, unknown, old, month_recent], scope="month", now=now
    )
    assert month_summary.workflow_count == 3
    assert month_summary.total_cost_usd == pytest.approx(1.4)

    workflow_summary = service.summarize_scope(
        [unknown], scope="workflow", workflow_run_id=2, now=now
    )
    assert workflow_summary.budget_status == "unknown"
    assert workflow_summary.unknown_cost_workflow_count == 1


def test_telegram_cost_and_workflow_commands_are_bounded_and_read_only() -> None:
    session_factory = _session_factory()
    seeded_workflow_id = _seed_workflow(
        session_factory,
        workflow_type="qa",
        metadata={
            "operation": "qa_answer",
            "estimated_cost": 0.25,
            "prompt": "private prompt content",
            "source_text": "private source content",
            "api_key": "private secret",
            "citation_count": 2,
        },
    )
    _seed_workflow(
        session_factory,
        workflow_type="indexing",
        metadata={"operation": "index_full", "embedding_estimated_cost": None},
    )
    observability_service = WorkflowObservabilityService(
        session_factory,
        cost_budget_service=CostBudgetService(
            daily_budget_usd=1.0,
            workflow_budget_usd=0.5,
        ),
    )
    telegram_client = InMemoryTelegramBotClient()
    _configure(
        session_factory=session_factory,
        telegram_client=telegram_client,
        observability_service=observability_service,
    )

    try:
        client = TestClient(app)
        cost = client.post("/api/telegram/webhook", json=_telegram_update(7101, "/cost"))
        assert cost.status_code == 200
        cost_payload = cost.json()
        assert cost_payload["cost_scope"] == "today"
        assert cost_payload["cost_llm_usd"] == pytest.approx(0.25)
        assert cost_payload["cost_unknown_workflow_count"] == 1
        assert "Pricing: unknown" in cost_payload["reply_text"]
        assert "private prompt content" not in cost_payload["reply_text"]

        for update_id, command_text in ((7106, "/cost 7d"), (7107, "/cost month")):
            scoped = client.post(
                "/api/telegram/webhook",
                json=_telegram_update(update_id, command_text),
            )
            assert scoped.status_code == 200
            assert scoped.json()["cost_scope"] in {"7d", "month"}

        workflow_cost = client.post(
            "/api/telegram/webhook",
            json=_telegram_update(7108, f"/cost workflow {seeded_workflow_id}"),
        )
        assert workflow_cost.status_code == 200
        assert workflow_cost.json()["cost_scope"] == "workflow"
        assert workflow_cost.json()["cost_workflow_run_id"] == seeded_workflow_id

        workflow = client.post(
            "/api/telegram/webhook",
            json=_telegram_update(7102, f"/workflow {seeded_workflow_id}"),
        )
        assert workflow.status_code == 200
        workflow_payload = workflow.json()
        assert workflow_payload["workflow_detail_run_id"] == seeded_workflow_id
        assert workflow_payload["workflow_detail_type"] == "qa"
        assert "qa_answer" in workflow_payload["reply_text"]
        assert "private prompt content" not in workflow_payload["reply_text"]
        assert "private source content" not in workflow_payload["reply_text"]
        assert "private secret" not in workflow_payload["reply_text"]

        recent = client.post(
            "/api/telegram/webhook",
            json=_telegram_update(7103, "/workflow"),
        )
        assert recent.status_code == 200
        assert recent.json()["workflow_recent_count"] >= 1
        assert "Recent workflows:" in recent.json()["reply_text"]

        invalid = client.post(
            "/api/telegram/webhook",
            json=_telegram_update(7104, "/cost 30d"),
        )
        assert invalid.status_code == 400
        assert invalid.json()["detail"]["error_code"] == "INVALID_ARGUMENT"

        missing = client.post(
            "/api/telegram/webhook",
            json=_telegram_update(7105, "/workflow 999999"),
        )
        assert missing.status_code == 404
        assert missing.json()["detail"]["error_code"] == "WORKFLOW_NOT_FOUND"
    finally:
        app.dependency_overrides.clear()
