from __future__ import annotations

from pydantic import BaseModel, Field


class NotionPageIndexRequest(BaseModel):
    page_id: str = Field(min_length=1, description="Notion page id to index.")


class NotionPageIndexResponse(BaseModel):
    workflow_run_id: int
    status: str
    page_id: str
    page_title: str
    notion_path: str
    indexed_block_count: int
