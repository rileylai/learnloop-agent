import json
import logging

from src.observability.logger import JsonFormatter


def test_json_formatter_emits_structured_payload() -> None:
    logger = logging.getLogger("tests.logger")
    record = logger.makeRecord(
        name="tests.logger",
        level=logging.INFO,
        fn=__file__,
        lno=10,
        msg="request_completed",
        args=(),
        exc_info=None,
        extra={
            "workflow_id": "wf-123",
            "path": "/health",
            "method": "GET",
            "status_code": 200,
            "duration_ms": 1.23,
        },
    )

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["event"] == "request_completed"
    assert payload["workflow_id"] == "wf-123"
    assert payload["path"] == "/health"
    assert payload["method"] == "GET"
    assert payload["status_code"] == 200
    assert payload["duration_ms"] == 1.23
    assert "timestamp" in payload
