from __future__ import annotations

import pytest

from src.app.config import (
    NotionBackendConfigurationError,
    get_settings,
    normalize_notion_backend,
)
from src.app.dependencies import get_tool_registry
from src.tools import (
    InMemoryNotionWriterClient,
    JSONMockNotionReaderClient,
    NotionAPIReaderClient,
    NotionAPIWriterClient,
)


def _clear_caches() -> None:
    get_settings.cache_clear()
    get_tool_registry.cache_clear()


def test_notion_backend_defaults_to_mock(monkeypatch) -> None:
    monkeypatch.delenv("NOTION_BACKEND", raising=False)
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    _clear_caches()

    registry = get_tool_registry()

    reader = registry.get_tool("notion_reader")._notion_reader_client
    writer = registry.get_tool("notion_writer")._notion_writer_client
    assert isinstance(reader, JSONMockNotionReaderClient)
    assert isinstance(writer, InMemoryNotionWriterClient)
    assert set(writer._pages) == {page.page_id for page in reader.list_pages()}


def test_live_backend_uses_api_reader_and_writer(monkeypatch) -> None:
    monkeypatch.setenv("NOTION_BACKEND", "live")
    monkeypatch.setenv("NOTION_TOKEN", "placeholder-token")
    _clear_caches()

    registry = get_tool_registry()

    reader = registry.get_tool("notion_reader")._notion_reader_client
    writer = registry.get_tool("notion_writer")._notion_writer_client
    assert isinstance(reader, NotionAPIReaderClient)
    assert isinstance(writer, NotionAPIWriterClient)


def test_live_backend_without_token_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("NOTION_BACKEND", "live")
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    _clear_caches()

    with pytest.raises(
        NotionBackendConfigurationError,
        match="NOTION_BACKEND=live requires NOTION_TOKEN",
    ):
        get_tool_registry()


def test_invalid_backend_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("NOTION_BACKEND", "remote")
    _clear_caches()

    with pytest.raises(NotionBackendConfigurationError, match="mock, live"):
        get_tool_registry()


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, "mock"), (" MOCK ", "mock"), ("Live", "live")],
)
def test_normalize_notion_backend(value: str | None, expected: str) -> None:
    assert normalize_notion_backend(value) == expected
