from __future__ import annotations

import json
from typing import Dict

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import (
    get_embedding_client,
    get_provider_router,
    get_tool_registry,
)
from src.app.main import app
from src.db.base import Base
from src.db.models import (
    ChangeRequest,
    KnowledgeChunk,
    NotionBlock,
    NotionPage,
    SourceDocument,
    WorkflowRun,
)
from src.db.session import get_db_session, get_db_session_factory, get_unit_of_work_factory
from src.db.unit_of_work import SqlAlchemyUnitOfWork
from src.providers import (
    EmbeddingClient,
    EmbeddingClientError,
    EmbeddingRequest,
    EmbeddingResponse,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ProviderRouter,
)
from src.tools import (
    InMemoryNotionPageSnapshot,
    InMemoryNotionWriterClient,
    NotionBlockNode,
    NotionPageTree,
    NotionReaderClient,
    NotionReaderTool,
    NotionWriterTool,
    ToolRegistry,
)


class _FakeProposalProvider(LLMProvider):
    def __init__(self, *, output_text: str) -> None:
        self._output_text = output_text

    @property
    def name(self) -> str:
        return "openai"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        _ = request
        return LLMResponse(
            provider="openai",
            model="gpt-4o-mini",
            output_text=self._output_text,
            token_input=120,
            token_output=90,
        )


class _SnapshotBackedNotionReaderClient(NotionReaderClient):
    def __init__(self, pages: Dict[str, InMemoryNotionPageSnapshot]) -> None:
        self._pages = pages

    def fetch_page_tree(self, page_id: str) -> NotionPageTree | None:
        snapshot = self._pages.get(page_id)
        if snapshot is None:
            return None

        blocks = [
            NotionBlockNode(
                block_id=f"{snapshot.page_id}-orig-{index}",
                block_type="paragraph",
                content_text=text,
                block_path=f"{snapshot.notion_path}/Original/{index}",
            )
            for index, text in enumerate(snapshot.original_blocks, start=1)
        ]
        for entry in snapshot.ai_supplement_entries:
            blocks.append(
                NotionBlockNode(
                    block_id=f"{snapshot.page_id}-ai-{entry.change_request_id}-title",
                    block_type="heading_3",
                    content_text=entry.topic_title,
                    block_path=entry.target_path,
                )
            )
            blocks.extend(
                NotionBlockNode(
                    block_id=(
                        f"{snapshot.page_id}-ai-{entry.change_request_id}"
                        f"-line-{line_index}"
                    ),
                    block_type="paragraph",
                    content_text=line,
                    block_path=f"{entry.target_path}/line-{line_index}",
                )
                for line_index, line in enumerate(entry.section_lines, start=1)
            )

        return NotionPageTree(
            page_id=snapshot.page_id,
            title=snapshot.title,
            notion_path=snapshot.notion_path,
            blocks=blocks,
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


class _FailOnceEmbeddingClient(_FakeEmbeddingClient):
    def __init__(self) -> None:
        self._failed = False

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        if not self._failed:
            self._failed = True
            raise EmbeddingClientError("injected re-index failure")
        return await super().embed(request)


def _build_review_tool_registry(
    snapshot_pages: Dict[str, InMemoryNotionPageSnapshot],
) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register_tool(
        NotionReaderTool(_SnapshotBackedNotionReaderClient(snapshot_pages))
    )
    registry.register_tool(NotionWriterTool(InMemoryNotionWriterClient(snapshot_pages)))
    return registry


def _embedding_client_override() -> EmbeddingClient:
    return _FakeEmbeddingClient()


def _build_session_factory():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            SourceDocument.__table__,
            WorkflowRun.__table__,
            ChangeRequest.__table__,
            NotionPage.__table__,
            NotionBlock.__table__,
            KnowledgeChunk.__table__,
        ],
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _seed_source_document(
    session: Session,
    *,
    source_document_id: int,
    source_type: str,
    source_display_name: str,
    raw_text: str,
) -> None:
    session.add(
        SourceDocument(
            id=source_document_id,
            source_type=source_type,
            source_display_name=source_display_name,
            content_hash=f"hash-{source_document_id}",
            raw_text=raw_text,
        )
    )
    session.commit()


def _seed_duplicate_reference_chunk(session: Session, *, chunk_text: str, notion_path: str) -> None:
    page = NotionPage(
        id=1,
        notion_page_id="page-nlp-week5",
        title="NLP Week 5",
        notion_path="Knowledge/NLP/Week5",
    )
    session.add(page)
    session.flush()

    block = NotionBlock(
        id=1,
        notion_block_id="blk-attn",
        notion_page_id=page.id,
        parent_block_id=None,
        block_type="paragraph",
        content_text=chunk_text,
        block_path=notion_path,
        block_order=0,
    )
    session.add(block)
    session.flush()

    session.add(
        KnowledgeChunk(
            id=1,
            source_document_id=None,
            notion_block_id=block.id,
            chunk_index=0,
            chunk_text=chunk_text,
            notion_path=notion_path,
            embedding_text=None,
            source_kind="notion",
        )
    )
    session.commit()


def _seed_notion_page(
    session: Session,
    *,
    page_db_id: int,
    notion_page_id: str,
    title: str,
    notion_path: str,
) -> None:
    session.add(
        NotionPage(
            id=page_db_id,
            notion_page_id=notion_page_id,
            title=title,
            notion_path=notion_path,
        )
    )
    session.commit()


def _seed_change_request(
    session: Session,
    *,
    change_request_id: int,
    status: str = "pending",
    target_notion_page_id: int | None = None,
    proposal_json: str = '{"title":"Draft proposal"}',
) -> None:
    session.add(
        ChangeRequest(
            id=change_request_id,
            source_document_id=None,
            target_notion_page_id=target_notion_page_id,
            status=status,
            proposal_json=proposal_json,
            failure_reason=None,
        )
    )
    session.commit()


def test_supplement_propose_api_creates_pending_change_request() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    try:
        _seed_source_document(
            seed_session,
            source_document_id=1,
            source_type="chat_text",
            source_display_name="chat-2026-05-26",
            raw_text="Notes about positional encoding and sequence modeling trade-offs.",
        )
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _provider_router_override() -> ProviderRouter:
        router = ProviderRouter()
        router.register_provider(
            _FakeProposalProvider(
                output_text=json.dumps(
                    {
                        "title": "Positional Encoding Supplement",
                        "target_path": "Knowledge/NLP/Week5/AI Supplement Zone/Positional Encoding",
                        "source": {
                            "source_type": "chat_text",
                            "source_display_name": "chat-2026-05-26",
                        },
                        "summary": "Adds concise notes about positional encoding trade-offs.",
                        "concepts": ["positional encoding", "sequence length generalization"],
                        "notes": ["Compare sinusoidal and learned embeddings briefly."],
                    }
                )
            )
        )
        return router

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_provider_router] = _provider_router_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/supplement/propose",
            json={
                "source_document_id": 1,
                "provider_name": "openai",
                "model": "gpt-4o-mini",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["change_request_status"] == "pending"
        assert payload["source_document_id"] == 1
        assert payload["duplicate_detected"] is False
        assert payload["duplicate_notion_path"] is None
        assert payload["provider"] == "openai"
        assert payload["model"] == "gpt-4o-mini"
        assert payload["token_input"] == 120
        assert payload["token_output"] == 90

        verify_session = session_factory()
        try:
            change_request = verify_session.get(ChangeRequest, payload["change_request_id"])
            assert change_request is not None
            assert change_request.status == "pending"
            assert change_request.source_document_id == 1
            proposal_payload = json.loads(change_request.proposal_json)
            assert proposal_payload["title"] == "Positional Encoding Supplement"
            assert (
                proposal_payload["target_path"]
                == "Knowledge/NLP/Week5/AI Supplement Zone/Positional Encoding"
            )

            workflow_run = verify_session.get(WorkflowRun, payload["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.workflow_type == "supplement"
            assert workflow_run.status == "succeeded"
            assert workflow_run.failure_reason is None
            metadata = json.loads(workflow_run.metadata_json or "{}")
            assert metadata["provider_name"] == "openai"
            assert metadata["model"] == "gpt-4o-mini"
            assert metadata["prompt_id"] == "supplement_proposal"
            assert metadata["prompt_version"] == "supplement_proposal_v4"
            assert metadata["estimated_cost"] == pytest.approx(0.000072)

            # Step 28 must not write to Notion.
            assert verify_session.query(NotionPage).count() == 0
            assert verify_session.query(NotionBlock).count() == 0
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_supplement_propose_api_uses_duplicate_reference_without_provider() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    duplicate_text = "Transformer attention uses query key value vectors for context weighting."
    duplicate_path = "Knowledge/NLP/Week5/Attention"
    try:
        _seed_source_document(
            seed_session,
            source_document_id=2,
            source_type="pdf",
            source_display_name="week5-attention.pdf",
            raw_text=duplicate_text,
        )
        _seed_duplicate_reference_chunk(
            seed_session,
            chunk_text=duplicate_text,
            notion_path=duplicate_path,
        )
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _provider_router_override() -> ProviderRouter:
        # No provider registered; duplicate path should bypass LLM call.
        return ProviderRouter()

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_provider_router] = _provider_router_override

    try:
        client = TestClient(app)
        response = client.post("/api/supplement/propose", json={"source_document_id": 2})

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["duplicate_detected"] is True
        assert payload["duplicate_notion_path"] == duplicate_path
        assert payload["provider"] is None
        assert payload["model"] is None

        verify_session = session_factory()
        try:
            change_request = verify_session.get(ChangeRequest, payload["change_request_id"])
            assert change_request is not None
            assert change_request.status == "pending"

            proposal_payload = json.loads(change_request.proposal_json)
            assert proposal_payload["target_path"] == duplicate_path
            assert "duplicate" in proposal_payload["summary"].lower()
            assert duplicate_path in proposal_payload["notes"][1]

            workflow_run = verify_session.get(WorkflowRun, payload["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.workflow_type == "supplement"
            assert workflow_run.status == "succeeded"
            assert workflow_run.failure_reason is None
            metadata = json.loads(workflow_run.metadata_json or "{}")
            assert metadata["provider_name"] == "openai"
            assert metadata["model"] == "gpt-4o-mini"
            assert metadata["prompt_id"] == "supplement_proposal"
            assert metadata["prompt_version"] == "supplement_proposal_v4"
            assert metadata["estimated_cost"] is None

            # No Notion write should happen. Existing seeded rows remain unchanged.
            assert verify_session.query(NotionPage).count() == 1
            assert verify_session.query(NotionBlock).count() == 1
            assert verify_session.query(KnowledgeChunk).count() == 1
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_supplement_propose_api_returns_llm_output_invalid() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    try:
        _seed_source_document(
            seed_session,
            source_document_id=3,
            source_type="url",
            source_display_name="https://example.com/nlp-week5",
            raw_text="Article text about attention and residual connections.",
        )
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _provider_router_override() -> ProviderRouter:
        router = ProviderRouter()
        router.register_provider(_FakeProposalProvider(output_text="{invalid-json}"))
        return router

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_provider_router] = _provider_router_override

    try:
        client = TestClient(app)
        response = client.post("/api/supplement/propose", json={"source_document_id": 3})

        assert response.status_code == 502
        detail = response.json()["detail"]
        assert detail["error_code"] == "LLM_OUTPUT_INVALID"
        assert detail["failure_reason"] == "LLM_OUTPUT_INVALID"
        assert detail["workflow_run_id"] is not None

        verify_session = session_factory()
        try:
            workflow_run = verify_session.get(WorkflowRun, detail["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.workflow_type == "supplement"
            assert workflow_run.status == "failed"
            assert workflow_run.failure_reason == "LLM_OUTPUT_INVALID"
            metadata = json.loads(workflow_run.metadata_json or "{}")
            assert metadata["provider_name"] == "openai"
            assert metadata["model"] == "gpt-4o-mini"
            assert metadata["prompt_id"] == "supplement_proposal"
            assert metadata["prompt_version"] == "supplement_proposal_v4"
            assert metadata["estimated_cost"] == pytest.approx(0.000072)
            assert verify_session.query(ChangeRequest).count() == 0
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_supplement_propose_api_returns_provider_not_found_when_provider_missing() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    try:
        _seed_source_document(
            seed_session,
            source_document_id=4,
            source_type="chat_text",
            source_display_name="chat-2026-06-17",
            raw_text="Notes about residual connections and layer normalization.",
        )
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _provider_router_override() -> ProviderRouter:
        return ProviderRouter()

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_provider_router] = _provider_router_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/supplement/propose",
            json={
                "source_document_id": 4,
                "provider_name": "openai",
                "model": "gpt-4o-mini",
            },
        )

        assert response.status_code == 500
        detail = response.json()["detail"]
        assert detail["error_code"] == "PROVIDER_NOT_FOUND"
        assert detail["failure_reason"] == "PROVIDER_NOT_FOUND"
        assert detail["workflow_run_id"] is not None

        verify_session = session_factory()
        try:
            workflow_run = verify_session.get(WorkflowRun, detail["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.workflow_type == "supplement"
            assert workflow_run.status == "failed"
            assert workflow_run.failure_reason == "PROVIDER_NOT_FOUND"
            metadata = json.loads(workflow_run.metadata_json or "{}")
            assert metadata["provider_name"] == "openai"
            assert metadata["model"] == "gpt-4o-mini"
            assert metadata["prompt_id"] == "supplement_proposal"
            assert metadata["prompt_version"] == "supplement_proposal_v4"
            assert metadata["estimated_cost"] is None
            assert verify_session.query(ChangeRequest).count() == 0
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_supplement_accept_api_appends_and_reindexes_before_accepting() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    snapshot_pages = {
        "page-accept-1": InMemoryNotionPageSnapshot(
            page_id="page-accept-1",
            title="NLP Week 5",
            notion_path="Knowledge/NLP/Week5",
            original_blocks=[
                "Attention aligns query and key vectors.",
            ],
        )
    }
    try:
        _seed_notion_page(
            seed_session,
            page_db_id=101,
            notion_page_id="page-accept-1",
            title="NLP Week 5",
            notion_path="Knowledge/NLP/Week5",
        )
        _seed_change_request(
            seed_session,
            change_request_id=11,
            status="pending",
            target_notion_page_id=101,
            proposal_json=json.dumps(
                {
                    "title": "Positional Encoding Supplement",
                    "target_path": "Knowledge/NLP/Week5/AI Supplement Zone/Positional Encoding Supplement",
                    "source": {
                        "source_type": "pdf",
                        "source_display_name": "week5-attention.pdf",
                    },
                    "summary": "Adds concise positional encoding notes for Week 5.",
                    "concepts": ["positional encoding", "length generalization"],
                    "notes": ["Compare sinusoidal and learned embeddings."],
                }
            ),
        )
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_review_tool_registry(snapshot_pages)

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_tool_registry] = _tool_registry_override
    app.dependency_overrides[get_embedding_client] = _embedding_client_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/supplement/accept",
            json={"change_request_id": 11, "reviewer": "reviewer-a"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["change_request_id"] == 11
        assert payload["change_request_status"] == "accepted"
        assert payload["review_action"] == "accept"
        assert payload["reviewer"] == "reviewer-a"
        assert payload["reason"] is None

        verify_session = session_factory()
        try:
            change_request = verify_session.get(ChangeRequest, 11)
            assert change_request is not None
            assert change_request.status == "accepted"

            workflow_run = verify_session.get(WorkflowRun, payload["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.workflow_type == "supplement"
            assert workflow_run.status == "succeeded"
            assert workflow_run.failure_reason is None

            indexing_runs = (
                verify_session.query(WorkflowRun)
                .filter(WorkflowRun.workflow_type == "indexing")
                .all()
            )
            assert len(indexing_runs) == 1
            assert indexing_runs[0].status == "succeeded"
            assert indexing_runs[0].failure_reason is None
            indexing_metadata = json.loads(indexing_runs[0].metadata_json or "{}")
            assert indexing_metadata["sync_mode"] == "auto_after_accept"
            assert indexing_metadata["embedding_provider"] == "openai"
            assert indexing_metadata["embedding_model"] == "text-embedding-3-small"
            assert indexing_metadata["embedding_dimensions"] == 1536
            assert indexing_metadata["embedding_token_input"] >= 10
            assert indexing_metadata["embedding_estimated_cost"] is not None

            page = (
                verify_session.query(NotionPage)
                .filter(NotionPage.notion_page_id == "page-accept-1")
                .one_or_none()
            )
            assert page is not None
            blocks = (
                verify_session.query(NotionBlock)
                .filter(NotionBlock.notion_page_id == page.id)
                .all()
            )
            assert len(blocks) >= 5
            assert any(
                "Summary: Adds concise positional encoding notes for Week 5."
                in (block.content_text or "")
                for block in blocks
            )

            chunks = (
                verify_session.query(KnowledgeChunk)
                .filter(KnowledgeChunk.source_kind == "notion")
                .all()
            )
            assert len(chunks) >= 1
            assert any(
                "Summary: Adds concise positional encoding notes for Week 5."
                in chunk.chunk_text
                for chunk in chunks
            )
            assert all(chunk.embedding is not None for chunk in chunks)
            assert all(chunk.embedding_text is not None for chunk in chunks)
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_supplement_accept_api_requires_target_page_for_safe_append() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    try:
        _seed_change_request(
            seed_session,
            change_request_id=111,
            status="pending",
            target_notion_page_id=None,
            proposal_json=json.dumps(
                {
                    "title": "Missing Target Page",
                    "target_path": "Knowledge/NLP/Week5/AI Supplement Zone/Missing Target Page",
                    "source": {
                        "source_type": "chat_text",
                        "source_display_name": "chat-source",
                    },
                    "summary": "Should fail before write because target page is missing.",
                    "concepts": ["safety check"],
                    "notes": ["target_notion_page_id is required for accept append."],
                }
            ),
        )
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_review_tool_registry({})

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/supplement/accept",
            json={"change_request_id": 111, "reviewer": "reviewer-a"},
        )

        assert response.status_code == 409
        detail = response.json()["detail"]
        assert detail["error_code"] == "WRITE_POLICY_VIOLATION"
        assert detail["failure_reason"] == "WRITE_POLICY_VIOLATION"
        assert detail["workflow_run_id"] is not None

        verify_session = session_factory()
        try:
            change_request = verify_session.get(ChangeRequest, 111)
            assert change_request is not None
            assert change_request.status == "pending"

            indexing_runs = (
                verify_session.query(WorkflowRun)
                .filter(WorkflowRun.workflow_type == "indexing")
                .all()
            )
            assert len(indexing_runs) == 0
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_supplement_accept_retry_reuses_verified_append_after_reindex_failure() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    snapshot_pages = {
        "page-accept-retry": InMemoryNotionPageSnapshot(
            page_id="page-accept-retry",
            title="Retry Page",
            notion_path="Knowledge/Retry",
            original_blocks=["Original note remains unchanged."],
        )
    }
    writer_client = InMemoryNotionWriterClient(snapshot_pages)
    embedding_client = _FailOnceEmbeddingClient()
    try:
        _seed_notion_page(
            seed_session,
            page_db_id=112,
            notion_page_id="page-accept-retry",
            title="Retry Page",
            notion_path="Knowledge/Retry",
        )
        _seed_change_request(
            seed_session,
            change_request_id=112,
            status="pending",
            target_notion_page_id=112,
            proposal_json=json.dumps(
                {
                    "title": "Retryable Supplement",
                    "target_path": "Knowledge/Retry/AI Supplement Zone/Retryable Supplement",
                    "source": {
                        "source_type": "chat_text",
                        "source_display_name": "retry-source",
                    },
                    "summary": "A supplement that can be retried safely.",
                    "concepts": ["durable append"],
                    "notes": ["Do not duplicate the visible entry."],
                }
            ),
        )
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        registry = ToolRegistry()
        registry.register_tool(
            NotionReaderTool(_SnapshotBackedNotionReaderClient(snapshot_pages))
        )
        registry.register_tool(NotionWriterTool(writer_client))
        return registry

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_tool_registry] = _tool_registry_override
    app.dependency_overrides[get_embedding_client] = lambda: embedding_client

    try:
        client = TestClient(app)
        first_response = client.post(
            "/api/supplement/accept",
            json={"change_request_id": 112, "reviewer": "retry-reviewer"},
        )
        assert first_response.status_code == 502
        first_detail = first_response.json()["detail"]
        assert first_detail["error_code"] == "PAGE_REINDEX_FAILED"

        verify_session = session_factory()
        try:
            first_change_request = verify_session.get(ChangeRequest, 112)
            assert first_change_request is not None
            assert first_change_request.status == "pending"
        finally:
            verify_session.close()

        second_response = client.post(
            "/api/supplement/accept",
            json={"change_request_id": 112, "reviewer": "retry-reviewer"},
        )
        assert second_response.status_code == 200
        assert second_response.json()["change_request_status"] == "accepted"

        page_snapshot = snapshot_pages["page-accept-retry"]
        assert len(page_snapshot.ai_supplement_entries) == 1
        assert len(writer_client.list_operations(page_id="page-accept-retry")) == 1
    finally:
        app.dependency_overrides.clear()


def test_supplement_reject_api_transitions_pending_to_rejected_without_notion_write() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    try:
        _seed_change_request(seed_session, change_request_id=12, status="pending")
        _seed_duplicate_reference_chunk(
            seed_session,
            chunk_text="Existing notion text",
            notion_path="Knowledge/NLP/Week5/Existing",
        )
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_review_tool_registry({})

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        before_session = session_factory()
        try:
            before_page_count = before_session.query(NotionPage).count()
            before_block_count = before_session.query(NotionBlock).count()
            before_chunk_count = before_session.query(KnowledgeChunk).count()
        finally:
            before_session.close()

        response = client.post(
            "/api/supplement/reject",
            json={
                "change_request_id": 12,
                "reviewer": "reviewer-b",
                "reason": "Out of scope for current note.",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["change_request_status"] == "rejected"
        assert payload["review_action"] == "reject"
        assert payload["reason"] == "Out of scope for current note."

        verify_session = session_factory()
        try:
            change_request = verify_session.get(ChangeRequest, 12)
            assert change_request is not None
            assert change_request.status == "rejected"

            # Step 29 reject path must not perform Notion writes.
            assert verify_session.query(NotionPage).count() == before_page_count
            assert verify_session.query(NotionBlock).count() == before_block_count
            assert verify_session.query(KnowledgeChunk).count() == before_chunk_count
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_supplement_edit_later_api_keeps_pending_status() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    try:
        _seed_change_request(seed_session, change_request_id=13, status="pending")
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_review_tool_registry({})

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/supplement/edit-later",
            json={
                "change_request_id": 13,
                "reviewer": "reviewer-c",
                "reason": "Need more examples before final decision.",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "succeeded"
        assert payload["change_request_status"] == "pending"
        assert payload["review_action"] == "edit_later"
        assert payload["reason"] == "Need more examples before final decision."

        verify_session = session_factory()
        try:
            change_request = verify_session.get(ChangeRequest, 13)
            assert change_request is not None
            assert change_request.status == "pending"
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_supplement_review_api_rejects_invalid_state_transition() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    try:
        _seed_change_request(seed_session, change_request_id=14, status="accepted")
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_review_tool_registry({})

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/supplement/reject",
            json={
                "change_request_id": 14,
                "reason": "Should fail because already accepted.",
            },
        )
        assert response.status_code == 409
        detail = response.json()["detail"]
        assert detail["error_code"] == "INVALID_STATE_TRANSITION"
        assert detail["failure_reason"] == "UNKNOWN_ERROR"
        assert detail["workflow_run_id"] is not None

        verify_session = session_factory()
        try:
            workflow_run = verify_session.get(WorkflowRun, detail["workflow_run_id"])
            assert workflow_run is not None
            assert workflow_run.workflow_type == "supplement"
            assert workflow_run.status == "failed"
            assert workflow_run.failure_reason == "UNKNOWN_ERROR"
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_supplement_review_api_returns_change_request_not_found() -> None:
    session_factory = _build_session_factory()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _tool_registry_override() -> ToolRegistry:
        return _build_review_tool_registry({})

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_tool_registry] = _tool_registry_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/supplement/accept",
            json={"change_request_id": 99999},
        )
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert detail["error_code"] == "CHANGE_REQUEST_NOT_FOUND"
        assert detail["failure_reason"] == "CHANGE_REQUEST_NOT_FOUND"
        assert detail["workflow_run_id"] is not None
    finally:
        app.dependency_overrides.clear()


def test_supplement_pending_list_and_detail_expose_review_content_and_external_target() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    proposal_json = json.dumps(
        {
            "title": "Reviewable supplement",
            "target_path": "Knowledge/NLP/Week5/AI Supplement Zone/Reviewable",
            "source": {
                "source_type": "pdf",
                "source_display_name": "week5.pdf",
            },
            "summary": "A grounded review summary.",
            "concepts": ["attention"],
            "notes": ["Check the source before accepting."],
            "citations": [
                {
                    "notion_path": "Knowledge/NLP/Week5/Attention",
                    "quote": "Query and key vectors determine relevance.",
                }
            ],
        }
    )
    try:
        _seed_notion_page(
            seed_session,
            page_db_id=201,
            notion_page_id="notion-page-external-201",
            title="NLP Week 5",
            notion_path="Knowledge/NLP/Week5",
        )
        _seed_change_request(
            seed_session,
            change_request_id=201,
            status="pending",
            target_notion_page_id=201,
            proposal_json=proposal_json,
        )
        _seed_change_request(
            seed_session,
            change_request_id=202,
            status="accepted",
            target_notion_page_id=201,
            proposal_json=proposal_json,
        )
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = _db_override
    try:
        client = TestClient(app)
        list_response = client.get("/api/supplement/pending")
        assert list_response.status_code == 200
        list_payload = list_response.json()
        assert list_payload["status"] == "succeeded"
        assert list_payload["count"] == 1
        item = list_payload["items"][0]
        assert item["change_request_id"] == 201
        assert item["target_notion_page_id"] == "notion-page-external-201"
        assert item["target_page"]["title"] == "NLP Week 5"
        assert item["proposal"]["summary"] == "A grounded review summary."
        assert item["citations"][0]["notion_path"] == "Knowledge/NLP/Week5/Attention"
        assert item["citations"][0]["quote"] == "Query and key vectors determine relevance."

        detail_response = client.get("/api/supplement/201")
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()
        assert detail_payload["status"] == "pending"
        assert detail_payload["proposal"]["title"] == "Reviewable supplement"
        assert detail_payload["citations"] == item["citations"]
    finally:
        app.dependency_overrides.clear()


def test_supplement_propose_resolves_external_target_and_rejects_unknown_target() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    try:
        _seed_source_document(
            seed_session,
            source_document_id=203,
            source_type="chat_text",
            source_display_name="chat-target",
            raw_text="Notes about external Notion page targeting.",
        )
        _seed_notion_page(
            seed_session,
            page_db_id=203,
            notion_page_id="notion-page-external-203",
            title="Targetable page",
            notion_path="Knowledge/Targetable",
        )
    finally:
        seed_session.close()

    def _db_override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def _provider_router_override() -> ProviderRouter:
        router = ProviderRouter()
        router.register_provider(
            _FakeProposalProvider(
                output_text=json.dumps(
                    {
                        "title": "Targeted proposal",
                        "target_path": "Knowledge/Targetable/AI Supplement Zone",
                        "source": {
                            "source_type": "chat_text",
                            "source_display_name": "chat-target",
                        },
                        "summary": "Targeted content.",
                        "concepts": ["targeting"],
                        "notes": ["Review before accept."],
                    }
                )
            )
        )
        return router

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_db_session_factory] = lambda: session_factory
    app.dependency_overrides[get_unit_of_work_factory] = lambda: (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_provider_router] = _provider_router_override

    try:
        client = TestClient(app)
        response = client.post(
            "/api/supplement/propose",
            json={
                "source_document_id": 203,
                "target_notion_page_id": "notion-page-external-203",
            },
        )
        assert response.status_code == 200
        assert response.json()["target_notion_page_id"] == "notion-page-external-203"

        verify_session = session_factory()
        try:
            stored = verify_session.get(ChangeRequest, response.json()["change_request_id"])
            assert stored is not None
            assert stored.target_notion_page_id == 203
        finally:
            verify_session.close()

        unknown_response = client.post(
            "/api/supplement/propose",
            json={
                "source_document_id": 203,
                "target_notion_page_id": "notion-page-does-not-exist",
            },
        )
        assert unknown_response.status_code == 404
        assert unknown_response.json()["detail"]["error_code"] == "NOTION_PAGE_NOT_FOUND"
        assert unknown_response.json()["detail"]["failure_reason"] == "NOTION_PAGE_NOT_FOUND"
    finally:
        app.dependency_overrides.clear()
