from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.db.models import WorkflowRun


class WorkflowRunRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_workflow_run(
        self,
        *,
        workflow_type: str,
        status: str,
        workflow_run_id: Optional[int] = None,
        failure_reason: Optional[str] = None,
        metadata_json: Optional[str] = None,
        finished_at: Optional[datetime] = None,
    ) -> WorkflowRun:
        workflow_run = WorkflowRun(
            workflow_type=workflow_type,
            status=status,
            failure_reason=failure_reason,
            metadata_json=metadata_json,
            finished_at=finished_at,
        )
        if workflow_run_id is not None:
            workflow_run.id = workflow_run_id

        self._session.add(workflow_run)
        self._session.commit()
        self._session.refresh(workflow_run)
        return workflow_run

    def get_workflow_run_by_id(self, workflow_run_id: int) -> Optional[WorkflowRun]:
        return self._session.get(WorkflowRun, workflow_run_id)

    def update_workflow_run(
        self,
        workflow_run_id: int,
        *,
        status: str,
        failure_reason: Optional[str] = None,
        metadata_json: Optional[str] = None,
        finished_at: Optional[datetime] = None,
    ) -> Optional[WorkflowRun]:
        workflow_run = self.get_workflow_run_by_id(workflow_run_id)
        if workflow_run is None:
            return None

        workflow_run.status = status
        workflow_run.failure_reason = failure_reason
        workflow_run.metadata_json = metadata_json
        workflow_run.finished_at = finished_at
        self._session.commit()
        self._session.refresh(workflow_run)
        return workflow_run
