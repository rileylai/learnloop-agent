from src.app.config import get_settings
from src.db.session import DEFAULT_DATABASE_URL, get_database_url


def _clear_settings_cache() -> None:
    get_settings.cache_clear()


def test_database_url_uses_default_when_env_missing(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    _clear_settings_cache()

    assert get_database_url() == DEFAULT_DATABASE_URL


def test_database_url_uses_env_override(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://custom:custom@localhost:5432/custom")

    _clear_settings_cache()

    assert get_database_url() == "postgresql+psycopg://custom:custom@localhost:5432/custom"
