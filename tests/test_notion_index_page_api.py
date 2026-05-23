from __future__ import annotations

from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import get_tool_registry
from src.app.main import app
from src.db.base import Base
from src.db.models import NotionBlock, NotionPage, WorkflowRun
from src.db.session import get_db_session
from src.tools import (
    InMemoryNotionReaderClient,
    NotionBlockNode,
    NotionPageTree,
    NotionReaderTool,
    ToolRegistry,
)


def _build_session_factory():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[NotionPage.__table__, NotionBlock.__table__, WorkflowRun.__table__],
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _build_tool_registry(pages: Dict[str, NotionPageTree]) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register_tool(NotionReaderTool(InMemoryNotionReaderClient(pages)))
    return registry


def _sample_tree_v1() -> NotionPageTree:
    return NotionPageTree(
        page_id="page-1",
        title="NLP Week 5",
        notion_path="Knowledge/NLP/Week5",
        blocks=[
            NotionBlockNode(
                block_id="blk-attention",
                block_type="heading_2",
                content_text="Attention",
                block_path="Knowledge/NLP/Week5/Attention",
                children=[
                    NotionBlockNode(
                        block_id="blk-sdp",
                        block_type="bulleted_list_item",
                        content_text="Scaled dot-product attention",
                        block_path="Knowledge/NLP/Week5/Attention/Scaled dot-product attention",
                    )
                ],
            )
        ],
    )


def _sample_tree_v2() -> NotionPageTree:
    return NotionPageTree(
        page_id="page-1",
        title="NLP Week 5 (Updated)",
        notion_path="Knowledge/NLP/Week5",
        blocks=[
            NotionBlockNode(
                block_id="blk-summary",
                block_type="paragraph",
                content_text="Transformer recap",
                block_path="Knowledge/NLP/Week5/Transformer recap",
            )
        ],
    )


def test_index_page_api_persists_page_and_nested_blocks() -> None:
    session_factory = _build_session_factory()
    pages = {"page-1": _sample_tree_v1()}

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_tool_registry(pages)

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post("/api/notion/index/page", json={"page_id": "page-1"})

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["page_id"] == "page-1"
        assert payload["indexed_block_count"] == 2

        session: Session = session_factory()
        try:
            page = (
                session.query(NotionPage)
                .filter(NotionPage.notion_page_id == "page-1")
                .one_or_none()
            )
            assert page is not None
            assert page.title == "NLP Week 5"

            blocks = (
                session.query(NotionBlock)
                .filter(NotionBlock.notion_page_id == page.id)
                .all()
            )
            assert len(blocks) == 2

            parent_block = next(
                block for block in blocks if block.notion_block_id == "blk-attention"
            )
            child_block = next(
                block for block in blocks if block.notion_block_id == "blk-sdp"
            )
            assert parent_block.parent_block_id is None
            assert child_block.parent_block_id == parent_block.id

            workflow_run = session.get(WorkflowRun, payload["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.status == "succeeded"
            assert workflow_run.failure_reason is None
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_index_page_api_replaces_existing_page_blocks() -> None:
    session_factory = _build_session_factory()
    pages = {"page-1": _sample_tree_v1()}

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_tool_registry(pages)

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        first_response = client.post("/api/notion/index/page", json={"page_id": "page-1"})
        assert first_response.status_code == 200

        pages["page-1"] = _sample_tree_v2()
        second_response = client.post("/api/notion/index/page", json={"page_id": "page-1"})
        assert second_response.status_code == 200
        second_payload = second_response.json()
        assert second_payload["page_title"] == "NLP Week 5 (Updated)"
        assert second_payload["indexed_block_count"] == 1

        session: Session = session_factory()
        try:
            pages_in_db = session.query(NotionPage).all()
            assert len(pages_in_db) == 1
            assert pages_in_db[0].title == "NLP Week 5 (Updated)"

            blocks = (
                session.query(NotionBlock)
                .filter(NotionBlock.notion_page_id == pages_in_db[0].id)
                .all()
            )
            assert len(blocks) == 1
            assert blocks[0].notion_block_id == "blk-summary"
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_index_page_api_returns_not_found_when_page_missing() -> None:
    session_factory = _build_session_factory()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_tool_registry({})

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post("/api/notion/index/page", json={"page_id": "missing-page"})

        assert response.status_code == 404
        detail = response.json()["detail"]
        assert detail["error_code"] == "NOTION_PAGE_NOT_FOUND"
        assert detail["failure_reason"] == "NOTION_PAGE_NOT_FOUND"

        session: Session = session_factory()
        try:
            workflow_runs = session.query(WorkflowRun).all()
            assert len(workflow_runs) == 1
            assert workflow_runs[0].status == "failed"
            assert workflow_runs[0].failure_reason == "NOTION_PAGE_NOT_FOUND"
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()
