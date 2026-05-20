from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import uuid4

from src.queue.base import QueueClient
from src.queue.models import EnqueuedJob


class FakeQueueClient(QueueClient):
    def __init__(self) -> None:
        self.enqueued_jobs: List[EnqueuedJob] = []

    def enqueue(
        self,
        *,
        queue_name: str,
        function: Callable[..., Any],
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> EnqueuedJob:
        _ = description
        job = EnqueuedJob(
            job_id=str(uuid4()),
            queue_name=queue_name,
            function_name=function.__name__,
            args=args,
            kwargs=kwargs or {},
        )
        self.enqueued_jobs.append(job)
        return job
