from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Protocol

from src.queue import QueueClient


READINESS_OK = "ok"
READINESS_FAILED = "failed"


@dataclass(frozen=True)
class ReadinessCheckResult:
    status: str
    detail: str
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class ReadinessReport:
    mode: str
    checks: Dict[str, ReadinessCheckResult]

    @property
    def is_ready(self) -> bool:
        return all(check.status == READINESS_OK for check in self.checks.values())


class ReadinessProbe(Protocol):
    def check_database(self) -> bool:
        ...

    def check_migration(self) -> bool:
        ...

    def check_vector_extension(self) -> bool:
        ...


class ReadinessService:
    def __init__(
        self,
        *,
        probe: ReadinessProbe,
        mode: str,
        openai_configured: bool,
        queue_client: Optional[QueueClient] = None,
        queue_required: bool = False,
    ) -> None:
        self._probe = probe
        self._mode = mode
        self._openai_configured = openai_configured
        self._queue_client = queue_client
        self._queue_required = queue_required

    def check(self) -> ReadinessReport:
        checks = {
            "database": self._run_probe(
                self._probe.check_database,
                detail="database connection is available",
                failure_reason="DATABASE_UNAVAILABLE",
            ),
            "migration": self._run_probe(
                self._probe.check_migration,
                detail="database migration is current",
                failure_reason="MIGRATION_NOT_CURRENT",
            ),
            "vector": self._run_probe(
                self._probe.check_vector_extension,
                detail="pgvector extension is available",
                failure_reason="VECTOR_EXTENSION_UNAVAILABLE",
            ),
            "mode": self._check_mode_dependency(),
        }
        if self._queue_required:
            checks["queue"] = self._check_queue_dependency()
        return ReadinessReport(mode=self._mode, checks=checks)

    def _check_queue_dependency(self) -> ReadinessCheckResult:
        if self._queue_client is None:
            return ReadinessCheckResult(
                status=READINESS_FAILED,
                detail="Redis queue configuration is missing",
                failure_reason="REDIS_URL_NOT_CONFIGURED",
            )
        if self._queue_client.is_available():
            return ReadinessCheckResult(
                status=READINESS_OK,
                detail="Redis queue is available",
            )
        return ReadinessCheckResult(
            status=READINESS_FAILED,
            detail="Redis queue is unavailable",
            failure_reason="REDIS_UNAVAILABLE",
        )

    def _check_mode_dependency(self) -> ReadinessCheckResult:
        if self._mode in {"test", "demo", "mock"}:
            return ReadinessCheckResult(
                status=READINESS_OK,
                detail="live provider dependency is not required in this mode",
            )
        if self._openai_configured:
            return ReadinessCheckResult(
                status=READINESS_OK,
                detail="OpenAI embedding configuration is present",
            )
        return ReadinessCheckResult(
            status=READINESS_FAILED,
            detail="OpenAI embedding configuration is missing",
            failure_reason="OPENAI_API_KEY_NOT_CONFIGURED",
        )

    @staticmethod
    def _run_probe(
        probe,
        *,
        detail: str,
        failure_reason: str,
    ) -> ReadinessCheckResult:
        try:
            passed = bool(probe())
        except Exception:
            passed = False
        if passed:
            return ReadinessCheckResult(status=READINESS_OK, detail=detail)
        return ReadinessCheckResult(
            status=READINESS_FAILED,
            detail=failure_reason.lower().replace("_", " "),
            failure_reason=failure_reason,
        )
