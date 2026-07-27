from __future__ import annotations

import asyncio
from typing import Dict, List, Mapping, Tuple

import pytest

from src.tools import (
    NotionAPIReaderClient,
    NotionHTTPResponse,
    NotionHTTPTransport,
    NotionReaderTool,
    ToolContext,
)


class _FakeNotionHTTPTransport(NotionHTTPTransport):
    def __init__(self, responses: List[NotionHTTPResponse]) -> None:
        self._responses = list(responses)
        self.calls: List[Tuple[str, Dict[str, str], Dict[str, str]]] = []

    def get_json(
        self,
        *,
        path: str,
        query: Mapping[str, str],
        headers: Mapping[str, str],
    ) -> NotionHTTPResponse:
        self.calls.append((path, dict(query), dict(headers)))
        return self._responses.pop(0)


def _page_response() -> NotionHTTPResponse:
    return NotionHTTPResponse(
        status_code=200,
        payload={
            "last_edited_time": "2026-07-27T10:00:00.000Z",
            "properties": {
                "Name": {
                    "id": "title",
                    "type": "title",
                    "title": [{"type": "text", "plain_text": "Live Page"}],
                }
            },
        },
    )


def test_notion_api_reader_fetches_paginated_nested_read_only_tree() -> None:
    transport = _FakeNotionHTTPTransport(
        [
            _page_response(),
            NotionHTTPResponse(
                status_code=200,
                payload={
                    "results": [
                        {
                            "id": "heading-1",
                            "type": "heading_2",
                            "has_children": True,
                            "heading_2": {
                                "rich_text": [
                                    {"type": "text", "plain_text": "Attention"}
                                ]
                            },
                        }
                    ],
                    "has_more": True,
                    "next_cursor": "cursor-1",
                },
            ),
            NotionHTTPResponse(
                status_code=200,
                payload={
                    "results": [
                        {
                            "id": "paragraph-2",
                            "type": "paragraph",
                            "has_children": False,
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "plain_text": "Second page"}
                                ]
                            },
                        }
                    ],
                    "has_more": False,
                    "next_cursor": None,
                },
            ),
            NotionHTTPResponse(
                status_code=200,
                payload={
                    "results": [
                        {
                            "id": "paragraph-1-child",
                            "type": "paragraph",
                            "has_children": False,
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "plain_text": "Nested note"}
                                ]
                            },
                        }
                    ],
                    "has_more": False,
                    "next_cursor": None,
                },
            ),
        ]
    )
    client = NotionAPIReaderClient(
        token="secret-token",
        transport=transport,
        page_size=1,
    )

    page = client.fetch_page_tree("page/with id")

    assert page is not None
    assert page.title == "Live Page"
    assert page.notion_path == "Knowledge/Live Page"
    assert page.last_edited_time is not None
    assert page.last_edited_time.isoformat() == "2026-07-27T10:00:00+00:00"
    assert len(page.blocks) == 2
    assert page.blocks[0].block_path == "Knowledge/Live Page/Attention"
    assert page.blocks[0].children[0].content_text == "Nested note"
    assert (
        page.blocks[0].children[0].block_path
        == "Knowledge/Live Page/Attention/Nested note"
    )
    assert [call[0] for call in transport.calls] == [
        "/v1/pages/page%2Fwith%20id",
        "/v1/blocks/page%2Fwith%20id/children",
        "/v1/blocks/page%2Fwith%20id/children",
        "/v1/blocks/heading-1/children",
    ]
    assert transport.calls[2][1] == {"page_size": "1", "start_cursor": "cursor-1"}
    assert transport.calls[0][2]["Authorization"] == "Bearer secret-token"
    assert transport.calls[0][2]["Notion-Version"] == "2022-06-28"


def test_notion_api_reader_returns_none_for_missing_page() -> None:
    transport = _FakeNotionHTTPTransport(
        [NotionHTTPResponse(status_code=404, payload={"message": "private body"})]
    )
    client = NotionAPIReaderClient(token="secret-token", transport=transport)

    assert client.fetch_page_tree("missing-page") is None
    assert len(transport.calls) == 1


def test_notion_api_reader_tool_maps_auth_and_http_errors_without_redaction_leaks() -> None:
    secret = "secret-token"
    transport = _FakeNotionHTTPTransport(
        [
            NotionHTTPResponse(
                status_code=401,
                payload={
                    "message": f"Bearer {secret} raw_text=private page contents"
                },
            )
        ]
    )
    tool = NotionReaderTool(
        NotionAPIReaderClient(token=secret, transport=transport)
    )

    result = asyncio.run(
        tool.run(
            context=ToolContext(workflow_id="wf-live-notion"),
            arguments={"page_id": "page-1"},
        )
    )

    assert result.is_error is True
    assert result.error is not None
    assert result.error.code == "NOTION_AUTH_FAILED"
    assert result.error.message == "Notion authorization failed"
    assert secret not in result.error.message
    assert "private page contents" not in result.error.message


def test_notion_api_reader_maps_invalid_http_payload_to_safe_block_error() -> None:
    transport = _FakeNotionHTTPTransport(
        [NotionHTTPResponse(status_code=200, payload=None)]
    )
    client = NotionAPIReaderClient(token="secret-token", transport=transport)

    with pytest.raises(Exception) as exc_info:
        client.fetch_page_tree("page-1")
    assert type(exc_info.value).__name__ == "NotionAPIClientError"
    assert str(exc_info.value) == "Notion API response is invalid"


def test_notion_api_reader_maps_upstream_failure_without_response_body() -> None:
    transport = _FakeNotionHTTPTransport(
        [
            NotionHTTPResponse(
                status_code=500,
                payload={"message": "raw_text=private page contents"},
            )
        ]
    )
    tool = NotionReaderTool(
        NotionAPIReaderClient(token="secret-token", transport=transport)
    )

    result = asyncio.run(
        tool.run(
            context=ToolContext(workflow_id="wf-live-notion"),
            arguments={"page_id": "page-1"},
        )
    )

    assert result.is_error is True
    assert result.error is not None
    assert result.error.code == "NOTION_BLOCK_FETCH_FAILED"
    assert result.error.message == "Notion API request failed"
    assert "private page contents" not in result.error.message
