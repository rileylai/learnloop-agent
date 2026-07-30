from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.repositories import NotionPageRepository


@dataclass
class TelegramPageItem:
    page_id: str
    title: str
    notion_path: str


@dataclass
class TelegramPagesResult:
    reply_text: str
    pages: List[TelegramPageItem]


class TelegramPageOrchestrator:
    def __init__(self, *, notion_page_repository: NotionPageRepository) -> None:
        self._notion_page_repository = notion_page_repository

    def list_pages(self, *, limit: int = 50) -> TelegramPagesResult:
        pages = [
            TelegramPageItem(
                page_id=page.notion_page_id,
                title=page.title,
                notion_path=page.notion_path,
            )
            for page in self._notion_page_repository.list_pages(limit=limit)
        ]
        pages.sort(key=lambda item: (item.notion_path, item.title, item.page_id))
        if not pages:
            return TelegramPagesResult(
                reply_text=(
                    "No indexed Notion pages are available. "
                    "Run a Notion index first."
                ),
                pages=[],
            )

        lines = ["Available Notion pages:"]
        lines.extend(
            f"- {page.page_id} | {page.title} | {page.notion_path}"
            for page in pages
        )
        lines.append(
            "For ingestion, upload a PDF or image and choose a page button; "
            "parent and child pages are independent targets."
        )
        return TelegramPagesResult(reply_text="\n".join(lines), pages=pages)
