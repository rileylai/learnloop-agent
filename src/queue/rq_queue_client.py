from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from rq import Queue

from src.queue.base import QueueClient
from src.queue.models import EnqueuedJob


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
    ) -> EnqueuedJob:
        queue = Queue(name=queue_name, connection=self._connection)
        job = queue.enqueue(
            function,
            *args,
            description=description,
            **(kwargs or {}),
        )
        return EnqueuedJob(
            job_id=job.id,
            queue_name=queue_name,
            function_name=function.__name__,
            args=args,
            kwargs=kwargs or {},
        )
