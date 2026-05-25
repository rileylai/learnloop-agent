from __future__ import annotations

import asyncio

from src.tools import (
    ParsedURLArticle,
    ToolContext,
    URLArticleParserClient,
    URLArticleParserClientError,
    URLArticleParserTool,
)


class _FakeURLArticleParserClient(URLArticleParserClient):
    def __init__(
        self,
        *,
        raw_text: str = "Extracted URL article text",
        should_fail: bool = False,
    ) -> None:
        self._raw_text = raw_text
        self._should_fail = should_fail

    def parse_article(self, *, url: str) -> ParsedURLArticle:
        if self._should_fail:
            raise URLArticleParserClientError("fetch failed")
        return ParsedURLArticle(url=url, raw_text=self._raw_text)


def test_url_article_parser_tool_returns_extracted_text() -> None:
    tool = URLArticleParserTool(
        _FakeURLArticleParserClient(raw_text="Attention is all you need")
    )

    result = asyncio.run(
        tool.run(
            context=ToolContext(workflow_id="wf-1"),
            arguments={"url": "https://example.com/article"},
        )
    )

    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["url"] == "https://example.com/article"
    assert result.structured_content["raw_text"] == "Attention is all you need"
    assert result.structured_content["char_count"] == len("Attention is all you need")


def test_url_article_parser_tool_rejects_non_http_url() -> None:
    tool = URLArticleParserTool(_FakeURLArticleParserClient())

    result = asyncio.run(
        tool.run(
            context=ToolContext(workflow_id="wf-2"),
            arguments={"url": "ftp://example.com/article"},
        )
    )

    assert result.is_error is True
    assert result.error is not None
    assert result.error.code == "INVALID_ARGUMENT"


def test_url_article_parser_tool_maps_client_error_to_url_fetch_failed() -> None:
    tool = URLArticleParserTool(_FakeURLArticleParserClient(should_fail=True))

    result = asyncio.run(
        tool.run(
            context=ToolContext(workflow_id="wf-3"),
            arguments={"url": "https://example.com/fail"},
        )
    )

    assert result.is_error is True
    assert result.error is not None
    assert result.error.code == "URL_FETCH_FAILED"
    assert result.error.message == "fetch failed"
