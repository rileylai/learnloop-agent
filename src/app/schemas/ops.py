from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel


class ReadinessCheck(BaseModel):
    status: str
    detail: str
    failure_reason: Optional[str] = None


class ReadinessResponse(BaseModel):
    status: str
    mode: str
    checks: Dict[str, ReadinessCheck]
