from __future__ import annotations

from typing import List

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


class NotionIncrementalIndexRequest(BaseModel):
    page_ids: List[str] = Field(
        min_length=1,
        description="Changed Notion page ids to reconcile using manual incremental sync.",
    )


class NotionIncrementalIndexedPage(BaseModel):
    page_id: str
    page_title: str
    notion_path: str
    indexed_block_count: int


class NotionIncrementalIndexResponse(BaseModel):
    workflow_run_id: int
    status: str
    sync_mode: str
    processed_page_count: int
    indexed_pages: List[NotionIncrementalIndexedPage]
