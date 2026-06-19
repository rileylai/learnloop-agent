from __future__ import annotations

import json
from typing import Dict

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import get_embedding_client, get_tool_registry
from src.app.main import app
from src.db.base import Base
from src.db.models import KnowledgeChunk, NotionBlock, NotionPage, WorkflowRun
from src.db.session import get_db_session
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
        embeddings = [
            [float(index + 1)] * 1536
            for index, _ in enumerate(request.inputs)
        ]
        return EmbeddingResponse(
            provider="openai",
            model="text-embedding-3-small",
            embeddings=embeddings,
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


def _build_tool_registry(pages: Dict[str, NotionPageTree]) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register_tool(NotionReaderTool(InMemoryNotionReaderClient(pages)))
    return registry


def _embedding_client_override() -> EmbeddingClient:
    return _FakeEmbeddingClient()


def _embedding_vector(fill_value: float) -> list[float]:
    return [fill_value] * 1536


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


def _sample_tree_mixed_types_with_untrusted_paths() -> NotionPageTree:
    return NotionPageTree(
        page_id="page-mixed",
        title="Mixed Path Page",
        notion_path="Knowledge/Mixed",
        blocks=[
            NotionBlockNode(
                block_id="blk-h1",
                block_type="heading_2",
                content_text="Root Heading",
                block_path="INVALID/PATH",
                children=[
                    NotionBlockNode(
                        block_id="blk-toggle",
                        block_type="toggle",
                        content_text="Toggle Topic",
                        block_path="INVALID/PATH",
                        children=[
                            NotionBlockNode(
                                block_id="blk-child-page",
                                block_type="child_page",
                                content_text="Child Page A",
                                block_path="INVALID/PATH",
                                children=[
                                    NotionBlockNode(
                                        block_id="blk-leaf",
                                        block_type="paragraph",
                                        content_text="Leaf Note",
                                        block_path="INVALID/PATH",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        ],
    )


def _sample_incremental_v1() -> NotionPageTree:
    return NotionPageTree(
        page_id="page-sync",
        title="Sync Test Page",
        notion_path="Knowledge/Sync",
        blocks=[
            NotionBlockNode(
                block_id="blk-old-a",
                block_type="heading_2",
                content_text="Old Section A",
                block_path="Knowledge/Sync/Old Section A",
                children=[
                    NotionBlockNode(
                        block_id="blk-old-a-p",
                        block_type="paragraph",
                        content_text="Old note A",
                        block_path="Knowledge/Sync/Old Section A/Old note A",
                    )
                ],
            ),
            NotionBlockNode(
                block_id="blk-old-b",
                block_type="heading_2",
                content_text="Old Section B",
                block_path="Knowledge/Sync/Old Section B",
                children=[
                    NotionBlockNode(
                        block_id="blk-old-b-p",
                        block_type="paragraph",
                        content_text="Old note B",
                        block_path="Knowledge/Sync/Old Section B/Old note B",
                    )
                ],
            ),
        ],
    )


def _sample_incremental_v2_after_manual_delete() -> NotionPageTree:
    return NotionPageTree(
        page_id="page-sync",
        title="Sync Test Page",
        notion_path="Knowledge/Sync",
        blocks=[
            NotionBlockNode(
                block_id="blk-old-b",
                block_type="heading_2",
                content_text="Old Section B",
                block_path="Knowledge/Sync/Old Section B",
                children=[
                    NotionBlockNode(
                        block_id="blk-old-b-p",
                        block_type="paragraph",
                        content_text="Old note B (edited)",
                        block_path="Knowledge/Sync/Old Section B/Old note B (edited)",
                    )
                ],
            )
        ],
    )


def _sample_legacy_backfill_page() -> NotionPageTree:
    return NotionPageTree(
        page_id="page-legacy-a",
        title="Legacy Vector Page",
        notion_path="Knowledge/Legacy/A",
        blocks=[
            NotionBlockNode(
                block_id="blk-legacy-a-heading",
                block_type="heading_2",
                content_text="Recovered Section",
                block_path="Knowledge/Legacy/A/Recovered Section",
                children=[
                    NotionBlockNode(
                        block_id="blk-legacy-a-note",
                        block_type="paragraph",
                        content_text="Legacy page re-index restores vector state",
                        block_path=(
                            "Knowledge/Legacy/A/Recovered Section/"
                            "Legacy page re-index restores vector state"
                        ),
                    )
                ],
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
    app.dependency_overrides[get_embedding_client] = _embedding_client_override

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

            chunks = (
                session.query(KnowledgeChunk)
                .join(NotionBlock, KnowledgeChunk.notion_block_id == NotionBlock.id)
                .filter(NotionBlock.notion_page_id == page.id)
                .order_by(KnowledgeChunk.chunk_index.asc())
                .all()
            )
            assert len(chunks) == 1
            assert chunks[0].embedding == [1.0] * 1536
            assert chunks[0].embedding_text is not None

            workflow_run = session.get(WorkflowRun, payload["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.status == "succeeded"
            assert workflow_run.failure_reason is None
            workflow_metadata = json.loads(workflow_run.metadata_json or "{}")
            assert workflow_metadata["embedding_provider"] == "openai"
            assert workflow_metadata["embedding_model"] == "text-embedding-3-small"
            assert workflow_metadata["embedding_dimensions"] == 1536
            assert workflow_metadata["embedding_token_input"] == 10
            assert workflow_metadata["embedding_estimated_cost"] == pytest.approx(0.0000002)
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_index_page_api_builds_paths_from_block_hierarchy() -> None:
    session_factory = _build_session_factory()
    pages = {"page-mixed": _sample_tree_mixed_types_with_untrusted_paths()}

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
    app.dependency_overrides[get_embedding_client] = _embedding_client_override

    try:
        client = TestClient(app)
        response = client.post("/api/notion/index/page", json={"page_id": "page-mixed"})

        assert response.status_code == 200

        session: Session = session_factory()
        try:
            page = (
                session.query(NotionPage)
                .filter(NotionPage.notion_page_id == "page-mixed")
                .one_or_none()
            )
            assert page is not None

            blocks = {
                block.notion_block_id: block
                for block in session.query(NotionBlock)
                .filter(NotionBlock.notion_page_id == page.id)
                .all()
            }
            assert blocks["blk-h1"].block_path == "Knowledge/Mixed/Root Heading"
            assert (
                blocks["blk-toggle"].block_path
                == "Knowledge/Mixed/Root Heading/Toggle Topic"
            )
            assert (
                blocks["blk-child-page"].block_path
                == "Knowledge/Mixed/Root Heading/Toggle Topic/Child Page A"
            )
            assert (
                blocks["blk-leaf"].block_path
                == "Knowledge/Mixed/Root Heading/Toggle Topic/Child Page A/Leaf Note"
            )
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
    app.dependency_overrides[get_embedding_client] = _embedding_client_override

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
    app.dependency_overrides[get_embedding_client] = _embedding_client_override

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


def test_index_page_api_fails_closed_when_embedding_provider_missing() -> None:
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
    app.dependency_overrides[get_embedding_client] = lambda: None

    try:
        client = TestClient(app)
        response = client.post("/api/notion/index/page", json={"page_id": "page-1"})

        assert response.status_code == 503
        detail = response.json()["detail"]
        assert detail["error_code"] == "EMBEDDING_PROVIDER_NOT_CONFIGURED"
        assert detail["failure_reason"] == "EMBEDDING_PROVIDER_NOT_CONFIGURED"

        session: Session = session_factory()
        try:
            assert session.query(NotionPage).count() == 0
            assert session.query(NotionBlock).count() == 0
            assert session.query(KnowledgeChunk).count() == 0

            workflow_run = session.get(WorkflowRun, detail["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.status == "failed"
            assert workflow_run.failure_reason == "EMBEDDING_PROVIDER_NOT_CONFIGURED"
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_index_incremental_api_reconciles_manual_deletion_with_page_replacement() -> None:
    session_factory = _build_session_factory()
    pages = {"page-sync": _sample_incremental_v1()}

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
    app.dependency_overrides[get_embedding_client] = _embedding_client_override

    try:
        client = TestClient(app)
        first_response = client.post("/api/notion/index/page", json={"page_id": "page-sync"})
        assert first_response.status_code == 200

        session: Session = session_factory()
        try:
            page = (
                session.query(NotionPage)
                .filter(NotionPage.notion_page_id == "page-sync")
                .one_or_none()
            )
            assert page is not None
            original_chunk_count = (
                session.query(KnowledgeChunk)
                .join(NotionBlock, KnowledgeChunk.notion_block_id == NotionBlock.id)
                .filter(NotionBlock.notion_page_id == page.id)
                .count()
            )
            assert original_chunk_count == 2
        finally:
            session.close()

        pages["page-sync"] = _sample_incremental_v2_after_manual_delete()
        incremental_response = client.post(
            "/api/notion/index/incremental",
            json={"page_ids": ["page-sync"]},
        )
        assert incremental_response.status_code == 200
        payload = incremental_response.json()
        assert payload["status"] == "succeeded"
        assert payload["sync_mode"] == "manual"
        assert payload["processed_page_count"] == 1
        assert payload["indexed_pages"][0]["page_id"] == "page-sync"
        assert payload["indexed_pages"][0]["indexed_block_count"] == 2

        session = session_factory()
        try:
            page = (
                session.query(NotionPage)
                .filter(NotionPage.notion_page_id == "page-sync")
                .one_or_none()
            )
            assert page is not None
            blocks = (
                session.query(NotionBlock)
                .filter(NotionBlock.notion_page_id == page.id)
                .all()
            )
            assert len(blocks) == 2
            assert {block.notion_block_id for block in blocks} == {"blk-old-b", "blk-old-b-p"}

            chunks = (
                session.query(KnowledgeChunk)
                .join(NotionBlock, KnowledgeChunk.notion_block_id == NotionBlock.id)
                .filter(NotionBlock.notion_page_id == page.id)
                .all()
            )
            assert len(chunks) == 1
            assert chunks[0].chunk_text == "Old Section B\nOld note B (edited)"
            assert chunks[0].embedding == [1.0] * 1536
            assert chunks[0].embedding_text is not None

            workflow_run = session.get(WorkflowRun, payload["workflow_run_id"])
            assert workflow_run is not None
            metadata = json.loads(workflow_run.metadata_json or "{}")
            assert metadata["embedding_provider"] == "openai"
            assert metadata["embedding_model"] == "text-embedding-3-small"
            assert metadata["embedding_dimensions"] == 1536
            assert metadata["embedding_token_input"] == 10
            assert metadata["embedding_estimated_cost"] == pytest.approx(0.0000002)
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_index_incremental_api_returns_not_found_when_any_page_missing() -> None:
    session_factory = _build_session_factory()
    pages = {"page-sync": _sample_incremental_v1()}

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
    app.dependency_overrides[get_embedding_client] = _embedding_client_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/notion/index/incremental",
            json={"page_ids": ["page-sync", "missing-page"]},
        )
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert detail["error_code"] == "NOTION_PAGE_NOT_FOUND"
        assert detail["failure_reason"] == "NOTION_PAGE_NOT_FOUND"
        assert detail["workflow_run_id"] is not None

        session: Session = session_factory()
        try:
            workflow_runs = session.query(WorkflowRun).order_by(WorkflowRun.id.asc()).all()
            assert len(workflow_runs) == 1
            assert workflow_runs[0].status == "failed"
            assert workflow_runs[0].failure_reason == "NOTION_PAGE_NOT_FOUND"
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_index_incremental_api_backfills_only_requested_legacy_page_vectors() -> None:
    session_factory = _build_session_factory()
    pages = {"page-legacy-a": _sample_legacy_backfill_page()}

    seed_session = session_factory()
    try:
        legacy_page = NotionPage(
            id=101,
            notion_page_id="page-legacy-a",
            title="Legacy Vector Page",
            notion_path="Knowledge/Legacy/A",
        )
        untouched_page = NotionPage(
            id=102,
            notion_page_id="page-legacy-b",
            title="Untouched Vector Page",
            notion_path="Knowledge/Legacy/B",
        )
        seed_session.add_all([legacy_page, untouched_page])
        seed_session.flush()

        legacy_block = NotionBlock(
            id=201,
            notion_block_id="blk-legacy-a-old",
            notion_page_id=legacy_page.id,
            parent_block_id=None,
            block_type="paragraph",
            content_text="Old legacy chunk without vectors",
            block_path="Knowledge/Legacy/A/Old Legacy Chunk",
            block_order=0,
        )
        untouched_block = NotionBlock(
            id=202,
            notion_block_id="blk-legacy-b-stable",
            notion_page_id=untouched_page.id,
            parent_block_id=None,
            block_type="paragraph",
            content_text="Existing live vector chunk",
            block_path="Knowledge/Legacy/B/Stable Vector Chunk",
            block_order=0,
        )
        seed_session.add_all([legacy_block, untouched_block])
        seed_session.flush()

        seed_session.add_all(
            [
                KnowledgeChunk(
                    id=301,
                    source_document_id=None,
                    notion_block_id=legacy_block.id,
                    chunk_index=0,
                    chunk_text="Old legacy chunk without vectors",
                    notion_path="Knowledge/Legacy/A/Old Legacy Chunk",
                    embedding=None,
                    embedding_text=None,
                    source_kind="notion",
                ),
                KnowledgeChunk(
                    id=302,
                    source_document_id=None,
                    notion_block_id=untouched_block.id,
                    chunk_index=0,
                    chunk_text="Existing live vector chunk",
                    notion_path="Knowledge/Legacy/B/Stable Vector Chunk",
                    embedding=_embedding_vector(9.0),
                    embedding_text=json.dumps(_embedding_vector(9.0)),
                    source_kind="notion",
                ),
            ]
        )
        seed_session.commit()
    finally:
        seed_session.close()

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
    app.dependency_overrides[get_embedding_client] = _embedding_client_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/notion/index/incremental",
            json={"page_ids": ["page-legacy-a"]},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["processed_page_count"] == 1
        assert payload["indexed_pages"][0]["page_id"] == "page-legacy-a"

        verify_session = session_factory()
        try:
            legacy_chunks = (
                verify_session.query(KnowledgeChunk)
                .join(NotionBlock, KnowledgeChunk.notion_block_id == NotionBlock.id)
                .join(NotionPage, NotionBlock.notion_page_id == NotionPage.id)
                .filter(NotionPage.notion_page_id == "page-legacy-a")
                .order_by(KnowledgeChunk.chunk_index.asc())
                .all()
            )
            assert len(legacy_chunks) == 1
            assert legacy_chunks[0].chunk_text == (
                "Recovered Section\nLegacy page re-index restores vector state"
            )
            assert legacy_chunks[0].embedding == _embedding_vector(1.0)
            assert legacy_chunks[0].embedding_text is not None

            untouched_chunks = (
                verify_session.query(KnowledgeChunk)
                .join(NotionBlock, KnowledgeChunk.notion_block_id == NotionBlock.id)
                .join(NotionPage, NotionBlock.notion_page_id == NotionPage.id)
                .filter(NotionPage.notion_page_id == "page-legacy-b")
                .order_by(KnowledgeChunk.id.asc())
                .all()
            )
            assert len(untouched_chunks) == 1
            assert untouched_chunks[0].chunk_text == "Existing live vector chunk"
            assert untouched_chunks[0].embedding == _embedding_vector(9.0)
            assert untouched_chunks[0].embedding_text == json.dumps(_embedding_vector(9.0))
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()
