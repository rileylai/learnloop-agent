from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Tuple

from src.queue.models import EnqueuedJob, QueueRetryPolicy


class QueueClient(ABC):
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether the queue backend can accept work now."""
        raise NotImplementedError
