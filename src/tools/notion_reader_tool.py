from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.tools.base import Tool
from src.tools.models import ToolContext, ToolResult, ToolSpec


@dataclass
class NotionBlockNode:
    block_id: str
    block_type: str
    content_text: str
    block_path: str
    children: List["NotionBlockNode"] = field(default_factory=list)


@dataclass
class NotionPageTree:
    page_id: str
    title: str
    notion_path: str
    blocks: List[NotionBlockNode] = field(default_factory=list)


class NotionReaderClient:
    def fetch_page_tree(self, page_id: str) -> Optional[NotionPageTree]:
        raise NotImplementedError


class InMemoryNotionReaderClient(NotionReaderClient):
    def __init__(self, pages: Dict[str, NotionPageTree]) -> None:
        self._pages = pages

    def fetch_page_tree(self, page_id: str) -> Optional[NotionPageTree]:
        return self._pages.get(page_id)


class NotionReaderTool(Tool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="notion_reader",
            description="Read one Notion page as a read-only block tree with paths.",
            input_schema={
                "type": "object",
                "required": ["page_id"],
                "properties": {
                    "page_id": {"type": "string"},
                },
            },
            output_schema={
                "type": "object",
                "required": ["page", "blocks", "printable_tree"],
                "properties": {
                    "page": {"type": "object"},
                    "blocks": {"type": "array"},
                    "printable_tree": {"type": "string"},
                },
            },
        )

    def __init__(self, notion_reader_client: NotionReaderClient) -> None:
        self._notion_reader_client = notion_reader_client

    async def run(self, context: ToolContext, arguments: Dict[str, Any]) -> ToolResult:
        _ = context
        page_id = str(arguments.get("page_id", "")).strip()
        if not page_id:
            return ToolResult.failure(
                code="INVALID_ARGUMENT",
                message="page_id is required",
            )

        try:
            page_tree = self._notion_reader_client.fetch_page_tree(page_id)
        except Exception as exc:
            return ToolResult.failure(
                code="NOTION_BLOCK_FETCH_FAILED",
                message=f"Failed to fetch Notion block tree: {exc}",
            )

        if page_tree is None:
            return ToolResult.failure(
                code="NOTION_PAGE_NOT_FOUND",
                message=f"Notion page is not found: page_id={page_id}",
            )

        printable_tree = self._render_printable_tree(page_tree)
        return ToolResult.success(
            content=printable_tree,
            structured_content={
                "page": {
                    "page_id": page_tree.page_id,
                    "title": page_tree.title,
                    "notion_path": page_tree.notion_path,
                },
                "blocks": [self._block_to_dict(block) for block in page_tree.blocks],
                "printable_tree": printable_tree,
            },
        )

    def _render_printable_tree(self, page_tree: NotionPageTree) -> str:
        lines = [
            f"Page: {page_tree.title} ({page_tree.page_id})",
            f"Path: {page_tree.notion_path}",
        ]
        for block in page_tree.blocks:
            self._append_block_lines(lines=lines, block=block, level=0)
        return "\n".join(lines)

    def _append_block_lines(
        self, *, lines: List[str], block: NotionBlockNode, level: int
    ) -> None:
        indent = "  " * level
        lines.append(
            f"{indent}- {block.block_type} [{block.block_id}] {block.content_text} | path={block.block_path}"
        )
        for child in block.children:
            self._append_block_lines(lines=lines, block=child, level=level + 1)

    def _block_to_dict(self, block: NotionBlockNode) -> Dict[str, Any]:
        return {
            "block_id": block.block_id,
            "block_type": block.block_type,
            "content_text": block.content_text,
            "block_path": block.block_path,
            "children": [self._block_to_dict(child) for child in block.children],
        }
