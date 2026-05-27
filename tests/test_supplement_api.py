from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import get_provider_router
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
from src.db.session import get_db_session
from src.providers import LLMProvider, LLMRequest, LLMResponse, ProviderRouter


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


def _seed_change_request(
    session: Session,
    *,
    change_request_id: int,
    status: str = "pending",
    proposal_json: str = '{"title":"Draft proposal"}',
) -> None:
    session.add(
        ChangeRequest(
            id=change_request_id,
            source_document_id=None,
            target_notion_page_id=None,
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
            assert verify_session.query(ChangeRequest).count() == 0
        finally:
            verify_session.close()
    finally:
        app.dependency_overrides.clear()


def test_supplement_accept_api_transitions_pending_to_accepted() -> None:
    session_factory = _build_session_factory()
    seed_session = session_factory()
    try:
        _seed_change_request(seed_session, change_request_id=11, status="pending")
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
        finally:
            verify_session.close()
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

    app.dependency_overrides[get_db_session] = _db_override

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

    app.dependency_overrides[get_db_session] = _db_override

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

    app.dependency_overrides[get_db_session] = _db_override

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

    app.dependency_overrides[get_db_session] = _db_override

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
