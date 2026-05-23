import asyncio
from typing import Any, Dict

import pytest

from src.providers import (
    EmbeddingClientError,
    EmbeddingRequest,
    OpenAIEmbeddingClient,
)


def test_openai_embedding_client_returns_embeddings_with_mock_transport() -> None:
    captured_payload: Dict[str, Any] = {}
    captured_headers: Dict[str, str] = {}
    captured_url = ""

    def fake_transport(
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        nonlocal captured_url
        captured_url = url
        captured_headers.update(headers)
        captured_payload.update(payload)
        return {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]},
            ],
            "usage": {"prompt_tokens": 12},
        }

    client = OpenAIEmbeddingClient(
        api_key="test-key",
        default_model="text-embedding-3-small",
        transport=fake_transport,
    )
    request = EmbeddingRequest(
        inputs=["chunk-a", "chunk-b"],
        metadata={"workflow_id": "wf-1"},
    )

    response = asyncio.run(client.embed(request))

    assert captured_url == "https://api.openai.com/v1/embeddings"
    assert captured_headers["Authorization"] == "Bearer test-key"
    assert captured_payload["model"] == "text-embedding-3-small"
    assert captured_payload["input"] == ["chunk-a", "chunk-b"]
    assert response.provider == "openai"
    assert response.model == "text-embedding-3-small"
    assert response.token_input == 12
    assert response.embeddings == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]


def test_openai_embedding_client_uses_request_model_and_dimensions() -> None:
    captured_payload: Dict[str, Any] = {}

    def fake_transport(
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        _ = url, headers
        captured_payload.update(payload)
        return {"data": [{"embedding": [0.01, 0.02]}]}

    client = OpenAIEmbeddingClient(
        api_key="test-key",
        default_model="text-embedding-3-small",
        transport=fake_transport,
    )
    request = EmbeddingRequest(
        inputs=["chunk-a"],
        model="text-embedding-3-large",
        dimensions=2,
    )

    response = asyncio.run(client.embed(request))

    assert captured_payload["model"] == "text-embedding-3-large"
    assert captured_payload["dimensions"] == 2
    assert response.model == "text-embedding-3-large"
    assert response.embeddings == [[0.01, 0.02]]


def test_openai_embedding_client_raises_error_for_invalid_transport_output() -> None:
    def fake_transport(
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        _ = url, headers, payload
        return {"unexpected": "shape"}

    client = OpenAIEmbeddingClient(
        api_key="test-key",
        transport=fake_transport,
    )
    request = EmbeddingRequest(inputs=["chunk-a"])

    with pytest.raises(EmbeddingClientError):
        asyncio.run(client.embed(request))


def test_openai_embedding_client_rejects_empty_api_key() -> None:
    with pytest.raises(EmbeddingClientError):
        OpenAIEmbeddingClient(api_key="  ")
