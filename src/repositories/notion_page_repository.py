from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.models import NotionPage


class NotionPageRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _allocate_page_id_for_sqlite(self) -> int:
        max_id = self._session.query(func.max(NotionPage.id)).scalar()
        return int(max_id or 0) + 1

    def get_by_notion_page_id(self, notion_page_id: str) -> Optional[NotionPage]:
        return (
            self._session.query(NotionPage)
            .filter(NotionPage.notion_page_id == notion_page_id)
            .one_or_none()
        )

    def get_by_id(self, page_db_id: int) -> Optional[NotionPage]:
        return self._session.get(NotionPage, page_db_id)

    def upsert_page_snapshot(
        self,
        *,
        notion_page_id: str,
        title: str,
        notion_path: str,
        last_edited_time: Optional[datetime] = None,
    ) -> NotionPage:
        page = self.get_by_notion_page_id(notion_page_id)
        if page is None:
            page = NotionPage(
                notion_page_id=notion_page_id,
                title=title,
                notion_path=notion_path,
                last_edited_time=last_edited_time,
            )
            if self._session.bind is not None and self._session.bind.dialect.name == "sqlite":
                page.id = self._allocate_page_id_for_sqlite()
            self._session.add(page)
        else:
            page.title = title
            page.notion_path = notion_path
            page.last_edited_time = last_edited_time

        self._session.flush()
        self._session.refresh(page)
        return page
