from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from rq import Queue, Retry

from src.queue.base import QueueClient
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
            function_name=function.__name__,
            args=args,
            kwargs=kwargs or {},
            retry_policy=retry_policy,
        )

    def is_available(self) -> bool:
        try:
            return bool(self._connection.ping())
        except Exception:
            return False
