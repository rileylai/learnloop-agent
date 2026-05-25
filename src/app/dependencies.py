from __future__ import annotations

from functools import lru_cache

from src.app.config import get_settings
from src.providers import OpenAIClient, ProviderRouter
from src.tools import (
    InMemoryNotionReaderClient,
    NotionReaderTool,
    PDFParserTool,
    PyPDFParserClient,
    TrafilaturaURLArticleParserClient,
    ToolRegistry,
    URLArticleParserTool,
)


@lru_cache(maxsize=1)
def get_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register_tool(NotionReaderTool(InMemoryNotionReaderClient(pages={})))
    registry.register_tool(PDFParserTool(PyPDFParserClient()))
    registry.register_tool(URLArticleParserTool(TrafilaturaURLArticleParserClient()))
    return registry


@lru_cache(maxsize=1)
def get_provider_router() -> ProviderRouter:
    router = ProviderRouter()
    settings = get_settings()
    if settings.openai_api_key:
        router.register_provider(OpenAIClient(api_key=settings.openai_api_key))
    return router
