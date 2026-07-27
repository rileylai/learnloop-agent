from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.base import Base
from src.db.models import NotionBlock, NotionPage
from src.repositories import (
    NotionBlockRepository,
    NotionBlockSnapshot,
    NotionPageRepository,
)


def _build_test_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            NotionPage.__table__,
            NotionBlock.__table__,
        ],
    )
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return local_session()


def test_notion_page_repository_upsert_flushes_without_commit() -> None:
    session = _build_test_session()
    repository = NotionPageRepository(session)

    page = repository.upsert_page_snapshot(
        notion_page_id="page-flush-only",
        title="Flush Only",
        notion_path="Knowledge/Flush Only",
    )

    assert page.id == 1
    assert session.query(NotionPage).count() == 1

    session.rollback()

    assert session.query(NotionPage).count() == 0


def test_notion_block_repository_replace_flushes_without_commit() -> None:
    session = _build_test_session()
    page = NotionPage(
        id=1,
        notion_page_id="page-blocks",
        title="Blocks",
        notion_path="Knowledge/Blocks",
    )
    session.add(page)
    session.commit()
    repository = NotionBlockRepository(session)

    inserted_blocks = repository.replace_page_blocks(
        notion_page_db_id=page.id,
        root_blocks=[
            NotionBlockSnapshot(
                notion_block_id="block-1",
                block_type="paragraph",
                content_text="Block 1",
                block_path="Knowledge/Blocks/Block 1",
            )
        ],
    )

    assert len(inserted_blocks) == 1
    assert session.query(NotionBlock).count() == 1

    session.rollback()

    assert session.query(NotionBlock).count() == 0
