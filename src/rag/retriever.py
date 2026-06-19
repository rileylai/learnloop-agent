from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from typing import List, Optional

from src.repositories import (
    ChunkRepository,
    RetrievalChunkCandidate,
    SemanticChunkMatch,
)

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


@dataclass
class RetrievedChunk:
    chunk_id: int
    chunk_index: int
    chunk_text: str
    notion_path: str
    notion_page_id: Optional[str]
    source_kind: str
    score: float


class ProductionChunkRetriever:
    def __init__(self, *, chunk_repository: ChunkRepository) -> None:
        self._chunk_repository = chunk_repository

    def retrieve(
        self,
        *,
        query_text: str,
        top_k: int = 5,
        page_ids: Optional[List[str]] = None,
        section_paths: Optional[List[str]] = None,
        source_kinds: Optional[List[str]] = None,
        query_embedding: Optional[List[float]] = None,
    ) -> List[RetrievedChunk]:
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        normalized_query_text = self._normalize_text(query_text)
        query_tokens = set(self._tokenize(normalized_query_text))
        normalized_query_embedding = self._normalize_embedding(query_embedding)

        if not normalized_query_text and normalized_query_embedding is None:
            return []

        if normalized_query_embedding is not None and self._chunk_repository.supports_vector_query():
            semantic_matches = self._chunk_repository.list_production_chunks_by_vector(
                query_embedding=normalized_query_embedding,
                top_k=top_k,
                page_ids=page_ids,
                section_paths=section_paths,
                source_kinds=source_kinds,
            )
            if semantic_matches:
                return [
                    self._to_retrieved_chunk(match)
                    for match in semantic_matches
                ]

        candidates = self._chunk_repository.list_production_chunks(
            page_ids=page_ids,
            section_paths=section_paths,
            source_kinds=source_kinds,
        )

        ranked: List[RetrievedChunk] = []
        for candidate in candidates:
            lexical_score = self._score_lexical(
                query_tokens=query_tokens,
                normalized_query_text=normalized_query_text,
                chunk_text=candidate.chunk_text,
            )
            embedding_score = self._score_embedding(
                query_embedding=normalized_query_embedding,
                chunk_embedding_text=candidate.embedding_text,
            )
            score = self._combine_scores(
                lexical_score=lexical_score,
                embedding_score=embedding_score,
                has_query_tokens=bool(query_tokens),
            )
            if score <= 0:
                continue
            ranked.append(
                RetrievedChunk(
                    chunk_id=candidate.chunk_id,
                    chunk_index=candidate.chunk_index,
                    chunk_text=candidate.chunk_text,
                    notion_path=candidate.notion_path,
                    notion_page_id=candidate.notion_page_id,
                    source_kind=candidate.source_kind,
                    score=score,
                )
            )

        ranked.sort(key=lambda item: (-item.score, item.chunk_id))
        return ranked[:top_k]

    def _to_retrieved_chunk(self, match: SemanticChunkMatch) -> RetrievedChunk:
        return RetrievedChunk(
            chunk_id=match.chunk_id,
            chunk_index=match.chunk_index,
            chunk_text=match.chunk_text,
            notion_path=match.notion_path,
            notion_page_id=match.notion_page_id,
            source_kind=match.source_kind,
            score=match.score,
        )

    def _score_lexical(
        self,
        *,
        query_tokens: set[str],
        normalized_query_text: str,
        chunk_text: str,
    ) -> float:
        if not query_tokens and not normalized_query_text:
            return 0.0

        normalized_chunk_text = self._normalize_text(chunk_text)
        chunk_tokens = set(self._tokenize(normalized_chunk_text))

        overlap_count = len(query_tokens.intersection(chunk_tokens))
        phrase_bonus = 0.0
        if normalized_query_text and normalized_query_text in normalized_chunk_text:
            phrase_bonus = 0.15

        if overlap_count == 0 and phrase_bonus == 0.0:
            return 0.0

        coverage_score = 0.0
        density_score = 0.0
        if query_tokens:
            coverage_score = overlap_count / len(query_tokens)
        if chunk_tokens:
            density_score = overlap_count / len(chunk_tokens)

        score = (coverage_score * 0.75) + (density_score * 0.25) + phrase_bonus
        return min(score, 1.0)

    def _score_embedding(
        self,
        *,
        query_embedding: Optional[List[float]],
        chunk_embedding_text: Optional[str],
    ) -> Optional[float]:
        if query_embedding is None or chunk_embedding_text is None:
            return None

        chunk_embedding = self._parse_embedding(chunk_embedding_text)
        if chunk_embedding is None or len(chunk_embedding) != len(query_embedding):
            return None

        dot = sum(left * right for left, right in zip(query_embedding, chunk_embedding))
        query_norm = math.sqrt(sum(value * value for value in query_embedding))
        chunk_norm = math.sqrt(sum(value * value for value in chunk_embedding))
        if query_norm == 0 or chunk_norm == 0:
            return None

        cosine_similarity = dot / (query_norm * chunk_norm)
        return max(0.0, min(cosine_similarity, 1.0))

    def _combine_scores(
        self,
        *,
        lexical_score: float,
        embedding_score: Optional[float],
        has_query_tokens: bool,
    ) -> float:
        if embedding_score is None:
            return lexical_score
        if not has_query_tokens:
            return embedding_score
        return (embedding_score * 0.8) + (lexical_score * 0.2)

    def _normalize_text(self, text: str) -> str:
        return " ".join(text.lower().split())

    def _tokenize(self, text: str) -> List[str]:
        return _TOKEN_PATTERN.findall(text)

    def _normalize_embedding(self, values: Optional[List[float]]) -> Optional[List[float]]:
        if values is None:
            return None
        normalized = []
        for value in values:
            try:
                normalized.append(float(value))
            except (TypeError, ValueError):
                return None
        if not normalized:
            return None
        return normalized

    def _parse_embedding(self, value: str) -> Optional[List[float]]:
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, list):
            return None

        normalized = []
        for item in parsed:
            try:
                normalized.append(float(item))
            except (TypeError, ValueError):
                return None
        if not normalized:
            return None
        return normalized
