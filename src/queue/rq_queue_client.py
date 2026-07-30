from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional, Tuple

from rq import Queue, Retry

from src.queue.base import QueueClient, get_callable_import_path
from src.queue.models import EnqueuedJob, QueueRetryPolicy


class RQQueueClient(QueueClient):
    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def enqueue(
        self,
        *,
        queue_name: str,
        function: Callable[..., Any],
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        retry_policy: Optional[QueueRetryPolicy] = None,
    ) -> EnqueuedJob:
        queue = Queue(name=queue_name, connection=self._connection)
        function_path = get_callable_import_path(function)
        enqueue_kwargs: Dict[str, Any] = {
            "description": description,
        }
        if retry_policy is not None and retry_policy.max_retries:
            enqueue_kwargs["retry"] = Retry(
                max=retry_policy.max_retries,
                interval=list(retry_policy.retry_intervals),
            )
        job = queue.enqueue(
            function,
            *args,
            **enqueue_kwargs,
            **(kwargs or {}),
        )
        return EnqueuedJob(
            job_id=job.id,
            queue_name=queue_name,
            function_name=job.func_name or function_path,
            args=args,
            kwargs=kwargs or {},
            retry_policy=retry_policy,
        )

    def is_available(self) -> bool:
        try:
            return bool(self._connection.ping())
        except Exception:
            return False

    def is_scheduler_available(self, *, queue_name: str) -> bool:
        """Check the RQ scheduler lock without mutating any registry."""

        try:
            return (
                Queue(name=queue_name, connection=self._connection).scheduler_pid
                is not None
            )
        except Exception:
            return False

    def inspect_state(
        self,
        *,
        queue_name: str,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Return redacted queue state without registry cleanup or deletion."""

        if limit < 1:
            raise ValueError("limit must be positive")
        from rq.registry import StartedJobRegistry

        queue = Queue(name=queue_name, connection=self._connection)
        scheduled = queue.scheduled_job_registry
        started = StartedJobRegistry(name=queue_name, connection=self._connection)
        scheduled_ids = scheduled.get_job_ids(
            start=0,
            end=limit - 1,
            cleanup=False,
        )
        scheduled_jobs = []
        for job_id in scheduled_ids:
            job = queue.fetch_job(job_id)
            if job is None:
                scheduled_jobs.append(
                    {"job_id": job_id, "status": "missing_job_record"}
                )
                continue
            try:
                scheduled_at = scheduled.get_expiration_time(job)
            except Exception:
                scheduled_at = None
            scheduled_jobs.append(
                {
                    "job_id": job.id,
                    "function": job.func_name,
                    "status": job.get_status(refresh=False),
                    "scheduled_at": (
                        scheduled_at.isoformat() if scheduled_at is not None else None
                    ),
                    "enqueued_at": (
                        job.enqueued_at.isoformat()
                        if job.enqueued_at is not None
                        else None
                    ),
                    "retries_left": job.retries_left,
                }
            )

        return {
            "queue_name": queue_name,
            "scheduler_running": queue.scheduler_pid is not None,
            "queued": queue.count,
            "started": started.get_job_count(cleanup=False),
            "scheduled": scheduled.get_job_count(cleanup=False),
            "scheduled_jobs": scheduled_jobs,
            "inspection_mutates_redis": False,
        }

    def enqueue_in(
        self,
        *,
        queue_name: str,
        function: Callable[..., Any],
        seconds: int,
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        retry_policy: Optional[QueueRetryPolicy] = None,
    ) -> EnqueuedJob:
        if seconds < 0:
            raise ValueError("seconds must be non-negative")
        queue = Queue(name=queue_name, connection=self._connection)
        function_path = get_callable_import_path(function)
        enqueue_kwargs: Dict[str, Any] = {
            "description": description,
            "scheduled_time": datetime.now(timezone.utc) + timedelta(seconds=seconds),
        }
        if retry_policy is not None and retry_policy.max_retries:
            enqueue_kwargs["retry"] = Retry(
                max=retry_policy.max_retries,
                interval=list(retry_policy.retry_intervals),
            )
        job = queue.enqueue_at(
            enqueue_kwargs.pop("scheduled_time"),
            function,
            *args,
            **enqueue_kwargs,
            **(kwargs or {}),
        )
        return EnqueuedJob(
            job_id=job.id,
            queue_name=queue_name,
            function_name=job.func_name or function_path,
            args=args,
            kwargs=kwargs or {},
            retry_policy=retry_policy,
        )
