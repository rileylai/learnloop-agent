from __future__ import annotations

from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import get_embedding_client, get_tool_registry
from src.app.main import app
from src.db.base import Base
from src.db.models import KnowledgeChunk, NotionBlock, NotionPage, WorkflowRun
from src.db.session import get_db_session, get_db_session_factory, get_unit_of_work_factory
from src.db.unit_of_work import SqlAlchemyUnitOfWork
from src.providers import EmbeddingClient, EmbeddingRequest, EmbeddingResponse
from src.tools import (
    InMemoryNotionReaderClient,
    NotionBlockNode,
    NotionPageTree,
    NotionReaderTool,
    ToolRegistry,
)


class _FakeEmbeddingClient(EmbeddingClient):
    @property
    def name(self) -> str:
        return "openai"

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(
            provider="openai",
            model="text-embedding-3-small",
            embeddings=[[1.0] * 1536 for _ in request.inputs],
            token_input=len(request.inputs) * 10,
        )


def _build_session_factory():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            NotionPage.__table__,
            NotionBlock.__table__,
            KnowledgeChunk.__table__,
            WorkflowRun.__table__,
        ],
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _tree(page_id: str, title: str, block_id: str, text: str) -> NotionPageTree:
    path = f"Knowledge/{title}"
    return NotionPageTree(
        page_id=page_id,
        title=title,
        notion_path=path,
        blocks=[
            NotionBlockNode(
                block_id=block_id,
                block_type="heading_2",
                content_text=text,
                block_path=f"{path}/{text}",
            )
        ],
    )


def _configure_overrides(
    session_factory,
    pages: Dict[str, NotionPageTree],
) -> None:
    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        registry = ToolRegistry()
        registry.register_tool(
            NotionReaderTool(InMemoryNotionReaderClient(pages))
        )
        return registry

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_tool_registry] = _tool_registry_override
    app.dependency_overrides[get_embedding_client] = _FakeEmbeddingClient


def test_full_index_discovers_external_page_ids_and_status() -> None:
    session_factory = _build_session_factory()
    pages = {
        "external-page-1": _tree(
            "external-page-1", "Page One", "block-one", "Section One"
        ),
        "external-page-2": _tree(
            "external-page-2", "Page Two", "block-two", "Section Two"
        ),
    }
    _configure_overrides(session_factory, pages)

    try:
        client = TestClient(app)
        response = client.post("/api/notion/index/full")

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["discovered_page_count"] == 2
        assert payload["processed_page_count"] == 2
        assert {page["page_id"] for page in payload["indexed_pages"]} == {
            "external-page-1",
            "external-page-2",
        }

        status_response = client.get(
            "/api/notion/index/status",
            params={"workflow_run_id": payload["workflow_run_id"]},
        )
        assert status_response.status_code == 200
        status = status_response.json()
        assert status["workflow_run_id"] == payload["workflow_run_id"]
        assert status["status"] == "succeeded"
        assert status["metadata"]["operation"] == "index_full"
        assert status["metadata"]["discovered_page_count"] == 2

        session: Session = session_factory()
        try:
            assert session.query(NotionPage).count() == 2
            assert session.query(NotionBlock).count() == 2
            assert session.query(KnowledgeChunk).count() == 2
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_repeated_full_index_replaces_stale_blocks_without_duplicates() -> None:
    session_factory = _build_session_factory()
    pages = {
        "external-page-1": _tree(
            "external-page-1", "Page One", "old-block", "Old Section"
        )
    }
    _configure_overrides(session_factory, pages)

    try:
        client = TestClient(app)
        first_response = client.post("/api/notion/index/full")
        assert first_response.status_code == 200

        pages["external-page-1"] = _tree(
            "external-page-1", "Page One", "new-block", "New Section"
        )
        second_response = client.post("/api/notion/index/full")
        assert second_response.status_code == 200

        session: Session = session_factory()
        try:
            assert session.query(NotionPage).count() == 1
            blocks = session.query(NotionBlock).all()
            assert {block.notion_block_id for block in blocks} == {"new-block"}
            chunks = session.query(KnowledgeChunk).all()
            assert len(chunks) == 1
            workflow_runs = (
                session.query(WorkflowRun)
                .order_by(WorkflowRun.id.asc())
                .all()
            )
            assert len(workflow_runs) == 2
            assert all(run.status == "succeeded" for run in workflow_runs)
        finally:
            session.close()

        latest_status = client.get("/api/notion/index/status")
        assert latest_status.status_code == 200
        assert latest_status.json()["workflow_run_id"] == second_response.json()[
            "workflow_run_id"
        ]
    finally:
        app.dependency_overrides.clear()


def test_index_status_returns_not_found_for_unknown_workflow() -> None:
    session_factory = _build_session_factory()
    _configure_overrides(session_factory, {})

    try:
        client = TestClient(app)
        response = client.get(
            "/api/notion/index/status",
            params={"workflow_run_id": 999},
        )
        assert response.status_code == 404
        assert response.json()["detail"]["error_code"] == (
            "NOTION_INDEX_STATUS_NOT_FOUND"
        )
    finally:
        app.dependency_overrides.clear()
