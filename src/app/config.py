from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field


NOTION_BACKEND_MOCK = "mock"
NOTION_BACKEND_LIVE = "live"
SUPPORTED_NOTION_BACKENDS = frozenset(
    {NOTION_BACKEND_MOCK, NOTION_BACKEND_LIVE}
)


class NotionBackendConfigurationError(ValueError):
    """Raised when Notion backend selection cannot be used safely."""


def _read_optional_env(name: str) -> Optional[str]:
    value = os.getenv(name)
    if value is None:
        return None

    stripped = value.strip()
    return stripped or None


class Settings(BaseModel):
    app_env: str = Field(default="local")
    log_level: str = Field(default="INFO")
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    mock_notion_data_dir: Optional[str] = None
    notion_backend: str = Field(default=NOTION_BACKEND_MOCK)
    notion_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "local"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database_url=_read_optional_env("DATABASE_URL"),
            redis_url=_read_optional_env("REDIS_URL"),
            mock_notion_data_dir=_read_optional_env("MOCK_NOTION_DATA_DIR"),
            notion_backend=_read_optional_env("NOTION_BACKEND")
            or NOTION_BACKEND_MOCK,
            notion_token=_read_optional_env("NOTION_TOKEN"),
            openai_api_key=_read_optional_env("OPENAI_API_KEY"),
            telegram_bot_token=_read_optional_env("TELEGRAM_BOT_TOKEN"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()


def normalize_notion_backend(value: Optional[str]) -> str:
    normalized = (value or NOTION_BACKEND_MOCK).strip().lower()
    if normalized not in SUPPORTED_NOTION_BACKENDS:
        supported = ", ".join((NOTION_BACKEND_MOCK, NOTION_BACKEND_LIVE))
        raise NotionBackendConfigurationError(
            f"NOTION_BACKEND must be one of: {supported}"
        )
    return normalized
