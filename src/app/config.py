from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field


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
    notion_token: Optional[str] = None
    openai_api_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "local"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database_url=_read_optional_env("DATABASE_URL"),
            redis_url=_read_optional_env("REDIS_URL"),
            notion_token=_read_optional_env("NOTION_TOKEN"),
            openai_api_key=_read_optional_env("OPENAI_API_KEY"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
