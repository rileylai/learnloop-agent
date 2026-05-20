from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Tuple

from src.queue.models import EnqueuedJob


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
    ) -> EnqueuedJob:
        raise NotImplementedError
