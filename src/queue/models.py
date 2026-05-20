from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class EnqueuedJob:
    job_id: str
    queue_name: str
    function_name: str
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
