from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.base import Base
from src.db.models import WorkflowRun
from src.repositories import WorkflowRunRepository
from src.services import (
    WORKFLOW_STATUS_FAILED,
    WORKFLOW_STATUS_RUNNING,
    WORKFLOW_STATUS_SUCCEEDED,
    WorkflowRunNotFoundError,
    WorkflowRunService,
    WorkflowRunValidationError,
)


def _build_test_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[WorkflowRun.__table__])
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return local_session()


def test_workflow_run_service_start_workflow_persists_running_status() -> None:
    session = _build_test_session()
    repository = WorkflowRunRepository(session)
    service = WorkflowRunService(repository=repository)

    created = service.start_workflow(
        workflow_type="indexing",
        metadata_json='{"sync_mode":"manual"}',
    )

    assert created.id == 1
    assert created.status == WORKFLOW_STATUS_RUNNING
    assert created.failure_reason is None
    assert created.metadata_json == '{"sync_mode":"manual"}'


def test_workflow_run_service_mark_succeeded_updates_status() -> None:
    session = _build_test_session()
    repository = WorkflowRunRepository(session)
    service = WorkflowRunService(repository=repository)

    created = service.start_workflow(workflow_type="ingestion")
    updated = service.mark_workflow_succeeded(
        created.id,
        metadata_json='{"result":"ok"}',
    )

    assert updated.status == WORKFLOW_STATUS_SUCCEEDED
    assert updated.failure_reason is None
    assert updated.metadata_json == '{"result":"ok"}'
    assert updated.finished_at is not None


def test_workflow_run_service_mark_failed_updates_standardized_failure_reason() -> None:
    session = _build_test_session()
    repository = WorkflowRunRepository(session)
    service = WorkflowRunService(repository=repository)

    created = service.start_workflow(workflow_type="ingestion")
    updated = service.mark_workflow_failed(
        created.id,
        failure_reason="url_fetch_failed",
        metadata_json='{"url":"https://example.com"}',
    )

    assert updated.status == WORKFLOW_STATUS_FAILED
    assert updated.failure_reason == "URL_FETCH_FAILED"
    assert updated.finished_at is not None


def test_workflow_run_service_rejects_unknown_failure_reason() -> None:
    session = _build_test_session()
    repository = WorkflowRunRepository(session)
    service = WorkflowRunService(repository=repository)

    created = service.start_workflow(workflow_type="qa")
    with pytest.raises(WorkflowRunValidationError):
        service.mark_workflow_failed(created.id, failure_reason="INVALID_REASON")


def test_workflow_run_service_raises_not_found_on_missing_workflow_run() -> None:
    session = _build_test_session()
    repository = WorkflowRunRepository(session)
    fixed_now = datetime.now(timezone.utc)
    service = WorkflowRunService(repository=repository, now_provider=lambda: fixed_now)

    with pytest.raises(WorkflowRunNotFoundError):
        service.mark_workflow_succeeded(999)
