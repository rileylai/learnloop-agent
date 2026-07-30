from src.app.config import get_settings


def _clear_settings_cache() -> None:
    get_settings.cache_clear()


def test_settings_load_without_optional_env(monkeypatch) -> None:
    env_keys = [
        "APP_ENV",
        "LOG_LEVEL",
        "DATABASE_URL",
        "REDIS_URL",
        "MOCK_NOTION_DATA_DIR",
        "NOTION_BACKEND",
        "NOTION_TOKEN",
        "OPENAI_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "API_BEARER_TOKEN",
        "TELEGRAM_WEBHOOK_SECRET",
        "TELEGRAM_ALLOWED_CHAT_IDS",
        "MAX_WORKFLOW_COST_USD",
        "MAX_DAILY_COST_USD",
        "WORKFLOW_STALE_AFTER_SECONDS",
    ]
    for key in env_keys:
        monkeypatch.delenv(key, raising=False)

    _clear_settings_cache()
    settings = get_settings()

    assert settings.app_env == "local"
    assert settings.log_level == "INFO"
    assert settings.database_url is None
    assert settings.redis_url is None
    assert settings.mock_notion_data_dir is None
    assert settings.notion_backend == "mock"
    assert settings.notion_token is None
    assert settings.openai_api_key is None
    assert settings.telegram_bot_token is None
    assert settings.api_bearer_token is None
    assert settings.telegram_webhook_secret is None
    assert settings.telegram_allowed_chat_ids == frozenset()
    assert settings.max_workflow_cost_usd is None
    assert settings.max_daily_cost_usd is None
    assert settings.workflow_stale_after_seconds == 3600


def test_settings_load_with_env_override(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost:5432/learnloop")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("MOCK_NOTION_DATA_DIR", "mock_data/notion_pages")
    monkeypatch.setenv("NOTION_BACKEND", "live")
    monkeypatch.setenv("NOTION_TOKEN", "placeholder-notion-token")
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder-openai-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "placeholder-telegram-token")
    monkeypatch.setenv("API_BEARER_TOKEN", "placeholder-api-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "placeholder-webhook-secret")
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "555, -100123, 555")
    monkeypatch.setenv("MAX_WORKFLOW_COST_USD", "0.25")
    monkeypatch.setenv("MAX_DAILY_COST_USD", "5")
    monkeypatch.setenv("WORKFLOW_STALE_AFTER_SECONDS", "900")

    _clear_settings_cache()
    settings = get_settings()

    assert settings.app_env == "test"
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "postgresql://localhost:5432/learnloop"
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.mock_notion_data_dir == "mock_data/notion_pages"
    assert settings.notion_backend == "live"
    assert settings.notion_token == "placeholder-notion-token"
    assert settings.openai_api_key == "placeholder-openai-key"
    assert settings.telegram_bot_token == "placeholder-telegram-token"
    assert settings.api_bearer_token == "placeholder-api-token"
    assert settings.telegram_webhook_secret == "placeholder-webhook-secret"
    assert settings.telegram_allowed_chat_ids == frozenset({"555", "-100123"})
    assert settings.max_workflow_cost_usd == 0.25
    assert settings.max_daily_cost_usd == 5.0
    assert settings.workflow_stale_after_seconds == 900
