from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from src.tools.base import Tool
from src.tools.models import ToolContext, ToolResult, ToolSpec


@dataclass
class ParsedURLArticle:
    url: str
    raw_text: str


class URLArticleParserClientError(Exception):
    pass


class URLArticleParserClient:
    def parse_article(self, *, url: str) -> ParsedURLArticle:
        raise NotImplementedError


class TrafilaturaURLArticleParserClient(URLArticleParserClient):
    def parse_article(self, *, url: str) -> ParsedURLArticle:
        try:
            import trafilatura
        except ModuleNotFoundError as exc:
            raise URLArticleParserClientError("trafilatura dependency is missing") from exc

        html = self._download_html(url)
        try:
            extracted = trafilatura.extract(html)
        except Exception as exc:
            raise URLArticleParserClientError(f"Failed to extract article text: {exc}") from exc

        if extracted is None:
            raise URLArticleParserClientError("No extractable text found in URL article")

        normalized_text = extracted.strip()
        if not normalized_text:
            raise URLArticleParserClientError("No extractable text found in URL article")

        return ParsedURLArticle(url=url, raw_text=normalized_text)

    def _download_html(self, url: str) -> str:
        request = Request(
            url=url,
            headers={"User-Agent": "LearnLoopAgent/0.1 (+https://local.learnloop)"},
            method="GET",
        )
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
                charset = response.headers.get_content_charset() or "utf-8"
        except Exception as exc:
            raise URLArticleParserClientError(f"Failed to fetch URL content: {exc}") from exc

        try:
            return body.decode(charset, errors="replace")
        except Exception as exc:
            raise URLArticleParserClientError(f"Failed to decode URL content: {exc}") from exc


class URLArticleParserTool(Tool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="url_article_parser",
            description="Fetch one URL article and extract normalized plain text.",
            input_schema={
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {"type": "string"},
                },
            },
            output_schema={
                "type": "object",
                "required": ["url", "raw_text", "char_count"],
                "properties": {
                    "url": {"type": "string"},
                    "raw_text": {"type": "string"},
                    "char_count": {"type": "integer"},
                },
            },
        )

    def __init__(self, parser_client: URLArticleParserClient) -> None:
        self._parser_client = parser_client

    async def run(self, context: ToolContext, arguments: Dict[str, Any]) -> ToolResult:
        _ = context
        url = str(arguments.get("url", "")).strip()
        if not url:
            return ToolResult.failure(
                code="INVALID_ARGUMENT",
                message="url is required",
            )
        if not self._is_supported_url(url):
            return ToolResult.failure(
                code="INVALID_ARGUMENT",
                message="url must be an absolute http/https URL",
            )

        try:
            parsed = self._parser_client.parse_article(url=url)
        except URLArticleParserClientError as exc:
            return ToolResult.failure(
                code="URL_FETCH_FAILED",
                message=str(exc),
            )

        normalized_raw_text = parsed.raw_text.strip()
        if not normalized_raw_text:
            return ToolResult.failure(
                code="URL_FETCH_FAILED",
                message="No extractable text found in URL article",
            )

        return ToolResult.success(
            content=f"parsed url={url} char_count={len(normalized_raw_text)}",
            structured_content={
                "url": parsed.url,
                "raw_text": normalized_raw_text,
                "char_count": len(normalized_raw_text),
            },
        )

    def _is_supported_url(self, value: str) -> bool:
        parsed = urlparse(value)
        if parsed.scheme.lower() not in {"http", "https"}:
            return False
        if not parsed.netloc:
            return False
        return True
