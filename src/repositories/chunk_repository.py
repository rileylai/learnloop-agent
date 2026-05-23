from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.models import KnowledgeChunk, NotionBlock


class ChunkRepositoryError(Exception):
    pass


class ChunkBlockMappingError(ChunkRepositoryError):
    pass


@dataclass
class NotionChunkUpsert:
    chunk_index: int
    chunk_text: str
    notion_path: str
    notion_block_ids: List[str] = field(default_factory=list)
    source_kind: str = "notion"
    embedding: Optional[List[float]] = None


class ChunkRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _allocate_chunk_id_for_sqlite(self) -> int:
        max_id_in_db = int(self._session.query(func.max(KnowledgeChunk.id)).scalar() or 0)
        max_id_in_identity_map = 0
        for instance in self._session.identity_map.values():
            if isinstance(instance, KnowledgeChunk) and instance.id is not None:
                max_id_in_identity_map = max(max_id_in_identity_map, int(instance.id))
        return max(max_id_in_db, max_id_in_identity_map) + 1

    def upsert_chunks(
        self,
        *,
        notion_page_db_id: int,
        chunks: List[NotionChunkUpsert],
    ) -> List[KnowledgeChunk]:
        page_blocks = (
            self._session.query(NotionBlock.id, NotionBlock.notion_block_id)
            .filter(NotionBlock.notion_page_id == notion_page_db_id)
            .all()
        )
        block_db_ids = [row.id for row in page_blocks]
        block_id_map = {
            row.notion_block_id: row.id
            for row in page_blocks
        }

        if block_db_ids:
            self._session.query(KnowledgeChunk).filter(
                KnowledgeChunk.source_kind == "notion",
                KnowledgeChunk.notion_block_id.in_(block_db_ids),
            ).delete(synchronize_session=False)
            self._session.flush()

        inserted: List[KnowledgeChunk] = []
        for chunk in sorted(chunks, key=lambda item: item.chunk_index):
            if chunk.source_kind != "notion":
                raise ChunkRepositoryError(
                    f"Unsupported source_kind for upsert_chunks: {chunk.source_kind}"
                )
            notion_block_db_id = self._select_chunk_block_id(
                notion_block_ids=chunk.notion_block_ids,
                block_id_map=block_id_map,
            )

            knowledge_chunk = KnowledgeChunk(
                source_document_id=None,
                notion_block_id=notion_block_db_id,
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.chunk_text,
                notion_path=chunk.notion_path,
                embedding_text=self._serialize_embedding(chunk.embedding),
                source_kind="notion",
            )
            if self._session.bind is not None and self._session.bind.dialect.name == "sqlite":
                knowledge_chunk.id = self._allocate_chunk_id_for_sqlite()
            self._session.add(knowledge_chunk)
            self._session.flush()
            inserted.append(knowledge_chunk)

        self._session.commit()
        for chunk in inserted:
            self._session.refresh(chunk)
        return inserted

    def _select_chunk_block_id(
        self,
        *,
        notion_block_ids: List[str],
        block_id_map: dict[str, int],
    ) -> int:
        for notion_block_id in notion_block_ids:
            block_db_id = block_id_map.get(notion_block_id)
            if block_db_id is not None:
                return block_db_id
        raise ChunkBlockMappingError(
            "Cannot map chunk to notion block in current page"
        )

    def _serialize_embedding(self, embedding: Optional[List[float]]) -> Optional[str]:
        if embedding is None:
            return None
        return json.dumps(embedding)
