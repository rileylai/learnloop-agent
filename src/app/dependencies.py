from __future__ import annotations

from functools import lru_cache

from src.tools import InMemoryNotionReaderClient, NotionReaderTool, ToolRegistry


@lru_cache(maxsize=1)
def get_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register_tool(NotionReaderTool(InMemoryNotionReaderClient(pages={})))
    return registry
