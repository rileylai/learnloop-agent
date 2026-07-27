from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional
from urllib import error, request
from urllib.parse import quote, urlencode

from src.rag import BlockPathNode, BlockPathSnapshot, build_block_paths
from src.tools.notion_reader_tool import (
    NotionBlockNode,
    NotionPageTree,
    NotionReaderClient,
    NotionReaderClientError,
)

DEFAULT_NOTION_API_BASE_URL = "https://api.notion.com"
DEFAULT_NOTION_VERSION = "2022-06-28"
DEFAULT_NOTION_PAGE_PATH_PREFIX = "Knowledge"
MAX_NOTION_PAGE_SIZE = 100


@dataclass(frozen=True)
class NotionHTTPResponse:
    status_code: int
    payload: Optional[Dict[str, Any]]


class NotionHTTPTransportError(Exception):
    """Transport failure without upstream response details."""


class NotionHTTPTransport:
    def get_json(
        self,
        *,
        path: str,
        query: Mapping[str, str],
        headers: Mapping[str, str],
    ) -> NotionHTTPResponse:
        raise NotImplementedError


class UrllibNotionHTTPTransport(NotionHTTPTransport):
    """Small stdlib transport for the Notion REST API."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_NOTION_API_BASE_URL,
        timeout_seconds: float = 10.0,
    ) -> None:
        normalized_base_url = base_url.strip().rstrip("/")
        if not normalized_base_url:
            raise ValueError("base_url must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._base_url = normalized_base_url
        self._timeout_seconds = timeout_seconds

    def get_json(
        self,
        *,
        path: str,
        query: Mapping[str, str],
        headers: Mapping[str, str],
    ) -> NotionHTTPResponse:
        url = f"{self._base_url}/{path.lstrip('/')}"
        if query:
            url = f"{url}?{urlencode(dict(query))}"
        req = request.Request(url=url, headers=dict(headers), method="GET")
        try:
            with request.urlopen(req, timeout=self._timeout_seconds) as response:
                status_code = int(response.status)
                response_body = response.read()
        except error.HTTPError as exc:
            # The body may contain private page text or upstream diagnostics.
            # Read it so the connection can be reused, but never expose it.
            try:
                exc.read()
            except OSError:
                pass
            return NotionHTTPResponse(status_code=int(exc.code), payload=None)
        except (error.URLError, OSError, TimeoutError) as exc:
            _ = exc
            raise NotionHTTPTransportError(
                "Notion API transport request failed"
            ) from None

        try:
            parsed_payload = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            parsed_payload = None
        if not isinstance(parsed_payload, dict):
            parsed_payload = None
        return NotionHTTPResponse(status_code=status_code, payload=parsed_payload)


class NotionAPIClientError(NotionReaderClientError):
    pass


class NotionAPIReaderClient(NotionReaderClient):
    """Read one Notion page and all nested blocks without write capabilities."""

    def __init__(
        self,
        *,
        token: str,
        transport: Optional[NotionHTTPTransport] = None,
        base_url: str = DEFAULT_NOTION_API_BASE_URL,
        notion_version: str = DEFAULT_NOTION_VERSION,
        page_path_prefix: str = DEFAULT_NOTION_PAGE_PATH_PREFIX,
        page_size: int = MAX_NOTION_PAGE_SIZE,
        timeout_seconds: float = 10.0,
    ) -> None:
        normalized_token = token.strip()
        if not normalized_token:
            raise NotionAPIClientError(
                code="NOTION_NOT_CONFIGURED",
                message="Notion token is not configured. Set NOTION_TOKEN.",
            )
        normalized_version = notion_version.strip()
        if not normalized_version:
            raise ValueError("notion_version must not be empty")
        normalized_prefix = "/".join(
            part.strip() for part in page_path_prefix.split("/") if part.strip()
        )
        if not normalized_prefix:
            raise ValueError("page_path_prefix must not be empty")
        if not 1 <= page_size <= MAX_NOTION_PAGE_SIZE:
            raise ValueError(f"page_size must be between 1 and {MAX_NOTION_PAGE_SIZE}")

        self._token = normalized_token
        self._notion_version = normalized_version
        self._page_path_prefix = normalized_prefix
        self._page_size = page_size
        self._transport = transport or UrllibNotionHTTPTransport(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
        )

    def fetch_page_tree(self, page_id: str) -> Optional[NotionPageTree]:
        normalized_page_id = page_id.strip()
        if not normalized_page_id:
            raise NotionAPIClientError(
                code="INVALID_ARGUMENT",
                message="page_id is required",
            )

        page_payload = self._request_json(
            path=f"/v1/pages/{quote(normalized_page_id, safe='')}",
            query={},
            not_found_code="NOTION_PAGE_NOT_FOUND",
        )
        if page_payload is None:
            return None

        title = _extract_page_title(page_payload)
        block_payloads = self._fetch_children(normalized_page_id)
        block_nodes = [
            self._build_block_node(block_payload) for block_payload in block_payloads
        ]
        notion_path = _normalize_path(f"{self._page_path_prefix}/{title}")
        block_paths = build_block_paths(
            page_path=notion_path,
            blocks=block_nodes,
        )
        return NotionPageTree(
            page_id=normalized_page_id,
            title=title,
            notion_path=notion_path,
            last_edited_time=_parse_datetime(page_payload.get("last_edited_time")),
            blocks=[_to_notion_block_node(block) for block in block_paths],
        )

    def _fetch_children(self, parent_id: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        cursor: Optional[str] = None
        seen_cursors = set()
        while True:
            query = {"page_size": str(self._page_size)}
            if cursor is not None:
                query["start_cursor"] = cursor
            payload = self._request_json(
                path=f"/v1/blocks/{quote(parent_id, safe='')}/children",
                query=query,
            )
            if payload is None:
                raise NotionAPIClientError(
                    code="NOTION_BLOCK_FETCH_FAILED",
                    message="Notion block response is missing",
                )
            raw_results = payload.get("results")
            if not isinstance(raw_results, list):
                raise NotionAPIClientError(
                    code="NOTION_BLOCK_FETCH_FAILED",
                    message="Notion block response is invalid",
                )
            for item in raw_results:
                if not isinstance(item, dict):
                    raise NotionAPIClientError(
                        code="NOTION_BLOCK_FETCH_FAILED",
                        message="Notion block response is invalid",
                    )
                results.append(item)

            has_more = payload.get("has_more") is True
            next_cursor = payload.get("next_cursor")
            if not has_more:
                return results
            if not isinstance(next_cursor, str) or not next_cursor.strip():
                raise NotionAPIClientError(
                    code="NOTION_BLOCK_FETCH_FAILED",
                    message="Notion block pagination cursor is invalid",
                )
            normalized_cursor = next_cursor.strip()
            if normalized_cursor in seen_cursors:
                raise NotionAPIClientError(
                    code="NOTION_BLOCK_FETCH_FAILED",
                    message="Notion block pagination cursor repeated",
                )
            seen_cursors.add(normalized_cursor)
            cursor = normalized_cursor

    def _build_block_node(self, payload: Dict[str, Any]) -> BlockPathNode:
        block_id = payload.get("id")
        block_type = payload.get("type")
        if not isinstance(block_id, str) or not block_id.strip():
            raise NotionAPIClientError(
                code="NOTION_BLOCK_FETCH_FAILED",
                message="Notion block response is missing block id",
            )
        if not isinstance(block_type, str) or not block_type.strip():
            raise NotionAPIClientError(
                code="NOTION_BLOCK_FETCH_FAILED",
                message="Notion block response is missing block type",
            )

        raw_children: List[Dict[str, Any]] = []
        if payload.get("has_children") is True:
            raw_children = self._fetch_children(block_id.strip())
        return BlockPathNode(
            block_id=block_id.strip(),
            block_type=block_type.strip(),
            content_text=_extract_block_text(payload, block_type.strip()),
            children=[self._build_block_node(child) for child in raw_children],
        )

    def _request_json(
        self,
        *,
        path: str,
        query: Mapping[str, str],
        not_found_code: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            response = self._transport.get_json(
                path=path,
                query=query,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Notion-Version": self._notion_version,
                    "Accept": "application/json",
                },
            )
        except NotionHTTPTransportError:
            raise NotionAPIClientError(
                code="NOTION_BLOCK_FETCH_FAILED",
                message="Notion API transport request failed",
            ) from None
        except Exception:
            raise NotionAPIClientError(
                code="NOTION_BLOCK_FETCH_FAILED",
                message="Notion API request failed",
            ) from None

        if response.status_code in (401, 403):
            raise NotionAPIClientError(
                code="NOTION_AUTH_FAILED",
                message="Notion authorization failed",
            )
        if response.status_code == 404 and not_found_code is not None:
            return None
        if response.status_code < 200 or response.status_code >= 300:
            raise NotionAPIClientError(
                code="NOTION_BLOCK_FETCH_FAILED",
                message="Notion API request failed",
            )
        if not isinstance(response.payload, dict):
            raise NotionAPIClientError(
                code="NOTION_BLOCK_FETCH_FAILED",
                message="Notion API response is invalid",
            )
        return response.payload


def _extract_page_title(page_payload: Mapping[str, Any]) -> str:
    properties = page_payload.get("properties")
    if isinstance(properties, dict):
        for property_payload in properties.values():
            if not isinstance(property_payload, dict):
                continue
            title_items = property_payload.get("title")
            if isinstance(title_items, list):
                title = _extract_rich_text(title_items)
                if title:
                    return title
    return "Untitled Notion Page"


def _extract_block_text(payload: Mapping[str, Any], block_type: str) -> str:
    content = payload.get(block_type)
    if not isinstance(content, dict):
        return ""
    for key in ("rich_text", "title", "caption"):
        items = content.get(key)
        if isinstance(items, list):
            text = _extract_rich_text(items)
            if text:
                return text
    expression = content.get("expression")
    if isinstance(expression, str):
        return expression.strip()
    url = content.get("url")
    if isinstance(url, str):
        return url.strip()
    return ""


def _extract_rich_text(items: List[Any]) -> str:
    parts: List[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        plain_text = item.get("plain_text")
        if isinstance(plain_text, str) and plain_text:
            parts.append(plain_text)
            continue
        text_payload = item.get("text")
        if isinstance(text_payload, dict):
            content = text_payload.get("content")
            if isinstance(content, str) and content:
                parts.append(content)
    return "".join(parts).strip()


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _to_notion_block_node(block: BlockPathSnapshot) -> NotionBlockNode:
    return NotionBlockNode(
        block_id=block.block_id,
        block_type=block.block_type,
        content_text=block.content_text,
        block_path=block.block_path,
        children=[_to_notion_block_node(child) for child in block.children],
    )


def _normalize_path(value: str) -> str:
    return "/".join(part.strip() for part in value.split("/") if part.strip())
