from __future__ import annotations

from functools import lru_cache
from typing import Optional

from fastapi import Depends

from src.app.config import get_settings
from src.db.readiness import SqlAlchemyReadinessProbe
from src.db.session import (
    SessionFactory,
    UnitOfWorkFactory,
    engine,
    get_db_session_factory,
)
from src.db.unit_of_work import SqlAlchemyUnitOfWork
from src.providers import (
    EmbeddingClient,
    OpenAIClient,
    OpenAIEmbeddingClient,
    ProviderRouter,
)
from src.services import CostTracker, PromptTemplateLoader, ReadinessService
from src.tools import (
    DEFAULT_MOCK_NOTION_DATA_DIR,
    DisabledTelegramBotClient,
    ImageOCRTool,
    InMemoryNotionReaderClient,
    InMemoryNotionWriterClient,
    JSONMockNotionReaderClient,
    NotionReaderTool,
    NotionWriterTool,
    PDFParserTool,
    PyPDFParserClient,
    TelegramBotTool,
    TelegramHTTPBotClient,
    TesseractImageOCRParserClient,
    TrafilaturaURLArticleParserClient,
    ToolRegistry,
    URLArticleParserTool,
    YouTubeTranscriptAPIClient,
    YouTubeTranscriptTool,
)


def get_business_unit_of_work_factory(
    session_factory: SessionFactory = Depends(get_db_session_factory),
) -> UnitOfWorkFactory:
    return lambda: SqlAlchemyUnitOfWork(session_factory)


def get_readiness_service() -> ReadinessService:
    settings = get_settings()
    return ReadinessService(
        probe=SqlAlchemyReadinessProbe(engine=engine),
        mode=settings.app_env,
        openai_configured=bool(settings.openai_api_key),
    )


@lru_cache(maxsize=1)
def get_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    settings = get_settings()
    notion_reader_client = InMemoryNotionReaderClient(pages={})
    if settings.mock_notion_data_dir:
        notion_reader_client = JSONMockNotionReaderClient.from_directory(
            settings.mock_notion_data_dir
        )
    elif DEFAULT_MOCK_NOTION_DATA_DIR.is_dir():
        notion_reader_client = JSONMockNotionReaderClient.from_directory(
            DEFAULT_MOCK_NOTION_DATA_DIR
        )
    registry.register_tool(NotionReaderTool(notion_reader_client))
    registry.register_tool(NotionWriterTool(InMemoryNotionWriterClient(pages={})))
    registry.register_tool(PDFParserTool(PyPDFParserClient()))
    registry.register_tool(URLArticleParserTool(TrafilaturaURLArticleParserClient()))
    registry.register_tool(YouTubeTranscriptTool(YouTubeTranscriptAPIClient()))
    registry.register_tool(ImageOCRTool(TesseractImageOCRParserClient()))
    if settings.telegram_bot_token:
        telegram_client = TelegramHTTPBotClient(
            bot_token=settings.telegram_bot_token,
        )
    else:
        telegram_client = DisabledTelegramBotClient()
    registry.register_tool(TelegramBotTool(telegram_client))
    return registry


@lru_cache(maxsize=1)
def get_provider_router() -> ProviderRouter:
    router = ProviderRouter()
    settings = get_settings()
    if settings.openai_api_key:
        router.register_provider(OpenAIClient(api_key=settings.openai_api_key))
    return router


@lru_cache(maxsize=1)
def get_embedding_client() -> Optional[EmbeddingClient]:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    return OpenAIEmbeddingClient(api_key=settings.openai_api_key)


@lru_cache(maxsize=1)
def get_prompt_template_loader() -> PromptTemplateLoader:
    return PromptTemplateLoader()


@lru_cache(maxsize=1)
def get_cost_tracker() -> CostTracker:
    return CostTracker()
