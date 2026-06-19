import json

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.base import Base
from src.db.models import KnowledgeChunk, NotionBlock, NotionPage, SourceDocument
from src.rag import ProductionChunkRetriever
from src.repositories import ChunkRepository


def _build_test_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            NotionPage.__table__,
            NotionBlock.__table__,
            SourceDocument.__table__,
            KnowledgeChunk.__table__,
        ],
    )
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return local_session()


def _seed_retrieval_data(session: Session) -> None:
    page_nlp = NotionPage(
        id=1,
        notion_page_id="page-nlp-week5",
        title="NLP Week 5",
        notion_path="Knowledge/NLP/Week5",
    )
    page_ml = NotionPage(
        id=2,
        notion_page_id="page-ml-week1",
        title="ML Week 1",
        notion_path="Knowledge/ML/Week1",
    )
    session.add_all([page_nlp, page_ml])
    session.flush()

    block_attention = NotionBlock(
        id=1,
        notion_block_id="blk-attn",
        notion_page_id=page_nlp.id,
        parent_block_id=None,
        block_type="paragraph",
        content_text="Attention uses query key value vectors",
        block_path="Knowledge/NLP/Week5/Attention",
        block_order=0,
    )
    block_transformer = NotionBlock(
        id=2,
        notion_block_id="blk-transformer",
        notion_page_id=page_nlp.id,
        parent_block_id=None,
        block_type="paragraph",
        content_text="Transformer encoder has multi-head attention",
        block_path="Knowledge/NLP/Week5/Transformer",
        block_order=1,
    )
    block_regression = NotionBlock(
        id=3,
        notion_block_id="blk-regression",
        notion_page_id=page_ml.id,
        parent_block_id=None,
        block_type="paragraph",
        content_text="Linear regression basics",
        block_path="Knowledge/ML/Week1/Regression",
        block_order=0,
    )
    session.add_all([block_attention, block_transformer, block_regression])
    session.flush()

    source_document = SourceDocument(
        id=11,
        source_type="pdf",
        source_display_name="ml-paper.pdf",
        content_hash="hash-1",
        raw_text="private source text",
    )
    session.add(source_document)
    session.flush()

    chunks = [
        KnowledgeChunk(
            id=1,
            source_document_id=None,
            notion_block_id=block_attention.id,
            chunk_index=0,
            chunk_text="Attention uses query key value vectors",
            notion_path="Knowledge/NLP/Week5/Attention",
            embedding_text=json.dumps([0.9, 0.1]),
            source_kind="notion",
        ),
        KnowledgeChunk(
            id=2,
            source_document_id=None,
            notion_block_id=block_transformer.id,
            chunk_index=1,
            chunk_text="Transformer encoder has multi-head attention",
            notion_path="Knowledge/NLP/Week5/Transformer",
            embedding_text=json.dumps([0.8, 0.2]),
            source_kind="notion",
        ),
        KnowledgeChunk(
            id=3,
            source_document_id=None,
            notion_block_id=block_regression.id,
            chunk_index=0,
            chunk_text="Linear regression basics",
            notion_path="Knowledge/ML/Week1/Regression",
            embedding_text=json.dumps([0.1, 0.9]),
            source_kind="notion",
        ),
        KnowledgeChunk(
            id=4,
            source_document_id=source_document.id,
            notion_block_id=None,
            chunk_index=0,
            chunk_text="External PDF source attention note",
            notion_path=None,
            embedding_text=json.dumps([1.0, 0.0]),
            source_kind="source_document",
        ),
    ]
    session.add_all(chunks)
    session.commit()


def test_retriever_returns_ranked_notion_chunks_only_in_production_scope() -> None:
    session = _build_test_session()
    _seed_retrieval_data(session)
    retriever = ProductionChunkRetriever(chunk_repository=ChunkRepository(session))

    results = retriever.retrieve(query_text="attention transformer", top_k=3)

    assert len(results) == 2
    assert [chunk.chunk_id for chunk in results] == [2, 1]
    assert all(chunk.source_kind == "notion" for chunk in results)


def test_retriever_filters_by_page_scope() -> None:
    session = _build_test_session()
    _seed_retrieval_data(session)
    retriever = ProductionChunkRetriever(chunk_repository=ChunkRepository(session))

    results = retriever.retrieve(
        query_text="regression",
        page_ids=["page-ml-week1"],
        top_k=5,
    )

    assert len(results) == 1
    assert results[0].notion_page_id == "page-ml-week1"
    assert results[0].notion_path == "Knowledge/ML/Week1/Regression"


def test_retriever_filters_by_section_scope() -> None:
    session = _build_test_session()
    _seed_retrieval_data(session)
    retriever = ProductionChunkRetriever(chunk_repository=ChunkRepository(session))

    results = retriever.retrieve(
        query_text="attention",
        section_paths=["Knowledge/NLP/Week5/Attention"],
        top_k=5,
    )

    assert len(results) == 1
    assert results[0].notion_path == "Knowledge/NLP/Week5/Attention"


def test_retriever_applies_source_kind_filter() -> None:
    session = _build_test_session()
    _seed_retrieval_data(session)
    retriever = ProductionChunkRetriever(chunk_repository=ChunkRepository(session))

    results = retriever.retrieve(
        query_text="attention",
        source_kinds=["source_document"],
        top_k=5,
    )

    assert results == []


def test_retriever_supports_embedding_only_query() -> None:
    session = _build_test_session()
    _seed_retrieval_data(session)
    retriever = ProductionChunkRetriever(chunk_repository=ChunkRepository(session))

    results = retriever.retrieve(
        query_text="",
        query_embedding=[1.0, 0.0],
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].chunk_id == 1


def test_retriever_lexical_path_remains_safe_with_mixed_vector_state() -> None:
    session = _build_test_session()
    _seed_retrieval_data(session)

    legacy_chunk = session.get(KnowledgeChunk, 1)
    assert legacy_chunk is not None
    legacy_chunk.embedding_text = None
    session.commit()

    retriever = ProductionChunkRetriever(chunk_repository=ChunkRepository(session))

    results = retriever.retrieve(
        query_text="attention query key value",
        top_k=2,
    )

    assert len(results) == 2
    assert [chunk.chunk_id for chunk in results] == [1, 2]
    assert results[0].notion_path == "Knowledge/NLP/Week5/Attention"
