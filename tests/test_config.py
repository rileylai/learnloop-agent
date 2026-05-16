from app.config import get_settings


def _clear_settings_cache() -> None:
    get_settings.cache_clear()


def test_settings_load_without_optional_env(monkeypatch) -> None:
    env_keys = [
        "APP_ENV",
        "LOG_LEVEL",
        "DATABASE_URL",
        "REDIS_URL",
        "NOTION_TOKEN",
        "OPENAI_API_KEY",
    ]
    for key in env_keys:
        monkeypatch.delenv(key, raising=False)

    _clear_settings_cache()
    settings = get_settings()

    assert settings.app_env == "local"
    assert settings.log_level == "INFO"
    assert settings.database_url is None
    assert settings.redis_url is None
    assert settings.notion_token is None
    assert settings.openai_api_key is None


def test_settings_load_with_env_override(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost:5432/learnloop")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("NOTION_TOKEN", "placeholder-notion-token")
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder-openai-key")

    _clear_settings_cache()
    settings = get_settings()

    assert settings.app_env == "test"
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "postgresql://localhost:5432/learnloop"
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.notion_token == "placeholder-notion-token"
    assert settings.openai_api_key == "placeholder-openai-key"
