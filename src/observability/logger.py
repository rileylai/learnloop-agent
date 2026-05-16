from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }

        for key in ("workflow_id", "path", "method", "status_code", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        return json.dumps(payload, ensure_ascii=True)


def _parse_log_level(log_level: str) -> int:
    level = getattr(logging, log_level.upper(), None)
    if isinstance(level, int):
        return level
    return logging.INFO


def configure_logging(log_level: str) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(_parse_log_level(log_level))

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root_logger.handlers = [handler]


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
