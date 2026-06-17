from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from urllib import request as urllib_request

from pydantic import BaseModel, Field

from src.observability.redaction import sanitize_sensitive_text


class EmbeddingRequest(BaseModel):
    inputs: List[str] = Field(min_length=1)
    model: Optional[str] = None
    dimensions: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class EmbeddingResponse(BaseModel):
    provider: str
    model: str
    embeddings: List[List[float]]
    token_input: Optional[int] = None
    raw_response: Optional[Dict[str, Any]] = None


class EmbeddingClientError(Exception):
    pass


class EmbeddingClient(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError


TransportFn = Callable[[str, Dict[str, str], Dict[str, Any]], Dict[str, Any]]


class OpenAIEmbeddingClient(EmbeddingClient):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        default_model: str = "text-embedding-3-small",
        transport: Optional[TransportFn] = None,
    ) -> None:
        normalized_key = api_key.strip()
        if not normalized_key:
            raise EmbeddingClientError("api_key must not be empty")

        normalized_model = default_model.strip()
        if not normalized_model:
            raise EmbeddingClientError("default_model must not be empty")

        self._api_key = normalized_key
        self._base_url = base_url.rstrip("/")
        self._default_model = normalized_model
        self._transport = transport or _default_transport

    @property
    def name(self) -> str:
        return "openai"

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model_name = (request.model or self._default_model).strip()
        if not model_name:
            raise EmbeddingClientError("model must not be empty")

        payload: Dict[str, Any] = {
            "model": model_name,
            "input": request.inputs,
        }
        if request.dimensions is not None:
            payload["dimensions"] = request.dimensions

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self._base_url}/embeddings"

        try:
            raw_response = await asyncio.to_thread(self._transport, url, headers, payload)
        except Exception as exc:
            raise EmbeddingClientError(
                f"Embedding request failed: {sanitize_sensitive_text(str(exc))}"
            ) from exc

        try:
            data = raw_response["data"]
            embeddings = [item["embedding"] for item in data]
            usage = raw_response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens")
        except (KeyError, TypeError) as exc:
            raise EmbeddingClientError(
                "Embedding response schema is invalid"
            ) from exc

        return EmbeddingResponse(
            provider=self.name,
            model=model_name,
            embeddings=embeddings,
            token_input=prompt_tokens,
            raw_response=raw_response,
        )


def _default_transport(
    url: str,
    headers: Dict[str, str],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib_request.Request(url=url, data=body, headers=headers, method="POST")
    with urllib_request.urlopen(req, timeout=60) as response:
        response_body = response.read().decode("utf-8")
    return json.loads(response_body)
