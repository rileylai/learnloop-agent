from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from typing import Optional

from src.app.dependencies import get_readiness_service
from src.app.main import app
from src.services import ReadinessService


class _FakeReadinessProbe:
    def __init__(self, *, failed_check: Optional[str] = None) -> None:
        self._failed_check = failed_check

    def check_database(self) -> bool:
        return self._failed_check != "database"

    def check_migration(self) -> bool:
        return self._failed_check != "migration"

    def check_vector_extension(self) -> bool:
        return self._failed_check != "vector"


def _override_readiness_service(
    *,
    failed_check: Optional[str] = None,
    mode: str = "test",
    openai_configured: bool = False,
) -> ReadinessService:
    return ReadinessService(
        probe=_FakeReadinessProbe(failed_check=failed_check),
        mode=mode,
        openai_configured=openai_configured,
    )


def test_ready_returns_200_when_all_dependencies_are_available() -> None:
    app.dependency_overrides[get_readiness_service] = _override_readiness_service

    try:
        response = TestClient(app).get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["mode"] == "test"
    assert {name: check["status"] for name, check in payload["checks"].items()} == {
        "database": "ok",
        "migration": "ok",
        "vector": "ok",
        "mode": "ok",
    }


@pytest.mark.parametrize(
    ("failed_check", "failure_reason"),
    [
        ("database", "DATABASE_UNAVAILABLE"),
        ("migration", "MIGRATION_NOT_CURRENT"),
        ("vector", "VECTOR_EXTENSION_UNAVAILABLE"),
    ],
)
def test_ready_returns_503_for_dependency_failures(
    failed_check: str,
    failure_reason: str,
) -> None:
    app.dependency_overrides[get_readiness_service] = lambda: _override_readiness_service(
        failed_check=failed_check
    )

    try:
        response = TestClient(app).get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "not_ready"
    assert payload["checks"][failed_check]["status"] == "failed"
    assert payload["checks"][failed_check]["failure_reason"] == failure_reason


def test_ready_returns_503_when_local_mode_lacks_openai_configuration() -> None:
    app.dependency_overrides[get_readiness_service] = lambda: _override_readiness_service(
        mode="local",
        openai_configured=False,
    )

    try:
        response = TestClient(app).get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["checks"]["mode"]["failure_reason"] == (
        "OPENAI_API_KEY_NOT_CONFIGURED"
    )


def test_health_remains_liveness_when_readiness_is_unavailable() -> None:
    app.dependency_overrides[get_readiness_service] = lambda: _override_readiness_service(
        failed_check="database"
    )

    try:
        response = TestClient(app).get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
