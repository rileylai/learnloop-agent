from __future__ import annotations

import asyncio
import json
from typing import List, Optional

from src.observability.external_error import (
    ExternalErrorCategory,
    ExternalErrorDiagnostic,
)
from src.providers import (
    EmbeddingClient,
    EmbeddingClientError,
    EmbeddingRequest,
    EmbeddingResponse,
)
from src.tools import (
    InMemoryNotionReaderClient,
    NotionBlockNode,
    NotionPageTree,
)

from .large_page_failure_diagnostic import (
    DIAGNOSTIC_NOTION_TIMEOUT_SECONDS,
    RUN_FLAG_ENV,
    LargePageDiagnosticReport,
    _build_live_clients,
    run_diagnostic_workflow,
    run_large_page_failure_diagnostic,
)


class _RecordingEmbeddingClient(EmbeddingClient):
    def __init__(self, *, fail_at_input_count: Optional[int] = None) -> None:
        self.fail_at_input_count = fail_at_input_count
        self.input_counts: List[int] = []

    @property
    def name(self) -> str:
        return "openai"

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        self.input_counts.append(len(request.inputs))
        if self.fail_at_input_count == len(request.inputs):
            raise EmbeddingClientError(
                diagnostic=ExternalErrorDiagnostic(
                    category=ExternalErrorCategory.REQUEST_TOO_LARGE,
                    retryable=False,
                    http_status=400,
                )
            )
        return EmbeddingResponse(
            provider="openai",
            model="text-embedding-3-small",
            embeddings=[[1.0] * 1536 for _ in request.inputs],
        )


def _reader(block_count: int = 8) -> InMemoryNotionReaderClient:
    blocks = [
        NotionBlockNode(
            block_id=f"block-{index}",
            block_type="heading_2",
            content_text=f"Synthetic diagnostic section {index}",
            block_path=f"Knowledge/Synthetic/Section {index}",
        )
        for index in range(block_count)
    ]
    page = NotionPageTree(
        page_id="synthetic-page",
        title="Synthetic Diagnostic",
        notion_path="Knowledge/Synthetic",
        blocks=blocks,
    )
    return InMemoryNotionReaderClient({page.page_id: page})


def test_default_diagnostic_is_opt_in_and_makes_no_external_calls() -> None:
    report = run_large_page_failure_diagnostic(
        include_live=False,
        approved=False,
        environment={},
    )

    assert report == LargePageDiagnosticReport(
        status="skipped",
        diagnosis="unresolved",
        message="live large-page diagnostic is disabled",
    )


def test_live_diagnostic_requires_independent_flag_and_approval() -> None:
    report = run_large_page_failure_diagnostic(
        include_live=True,
        approved=False,
        environment={RUN_FLAG_ENV: "1"},
    )

    assert report.status == "failed"
    assert report.diagnosis == "unresolved"
    assert report.cases == []


def test_diagnostic_runs_cases_sequentially_and_stops_on_failure() -> None:
    embedding_client = _RecordingEmbeddingClient(fail_at_input_count=8)

    report = asyncio.run(
        run_diagnostic_workflow(
            reader_client=_reader(),
            embedding_client=embedding_client,
            target_page_id="synthetic-page",
            bounded_batch_count=8,
        )
    )

    assert embedding_client.input_counts == [1, 4, 8]
    assert report.status == "failed"
    assert report.diagnosis == "established"
    assert [case.diagnostic_case for case in report.cases] == [
        "single_input",
        "small_batch",
        "bounded_batch",
    ]
    assert report.cases[-1].provider_error_category == "request_too_large"
    assert report.cases[-1].http_status == 400
    assert report.cases[-1].retryable is False


def test_diagnostic_progresses_under_explicit_request_budget() -> None:
    embedding_client = _RecordingEmbeddingClient()

    report = asyncio.run(
        run_diagnostic_workflow(
            reader_client=_reader(),
            embedding_client=embedding_client,
            target_page_id="synthetic-page",
            bounded_batch_count=8,
            max_request_count=2,
        )
    )

    assert embedding_client.input_counts == [1, 4]
    assert report.status == "inconclusive"
    assert report.diagnosis == "unresolved"
    assert report.message == "diagnostic request budget exhausted"


def test_bounded_case_counts_progress_without_concurrency_or_retry() -> None:
    embedding_client = _RecordingEmbeddingClient()

    report = asyncio.run(
        run_diagnostic_workflow(
            reader_client=_reader(block_count=32),
            embedding_client=embedding_client,
            target_page_id="synthetic-page",
            bounded_batch_count=32,
        )
    )

    assert embedding_client.input_counts == [1, 4, 8, 16, 32]
    assert report.status == "passed"


def test_aggregate_size_budget_prevents_oversized_probe() -> None:
    embedding_client = _RecordingEmbeddingClient()

    report = asyncio.run(
        run_diagnostic_workflow(
            reader_client=_reader(),
            embedding_client=embedding_client,
            target_page_id="synthetic-page",
            bounded_batch_count=8,
            max_aggregate_bytes=1,
        )
    )

    assert embedding_client.input_counts == []
    assert report.status == "inconclusive"
    assert report.message == "diagnostic request budget exhausted"


def test_live_client_factory_uses_diagnostic_30_second_timeout() -> None:
    reader_client, _ = _build_live_clients(
        notion_token="synthetic-token",
        openai_api_key="synthetic-key",
    )

    assert DIAGNOSTIC_NOTION_TIMEOUT_SECONDS == 30.0
    assert reader_client._transport._timeout_seconds == 30.0


def test_authentication_failure_does_not_establish_http_400_root_cause() -> None:
    class _AuthenticationFailureClient(_RecordingEmbeddingClient):
        async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
            self.input_counts.append(len(request.inputs))
            raise EmbeddingClientError(
                diagnostic=ExternalErrorDiagnostic(
                    category=ExternalErrorCategory.AUTHENTICATION_FAILED,
                    retryable=False,
                    http_status=401,
                )
            )

    report = asyncio.run(
        run_diagnostic_workflow(
            reader_client=_reader(),
            embedding_client=_AuthenticationFailureClient(),
            target_page_id="synthetic-page",
            bounded_batch_count=8,
        )
    )

    assert report.status == "failed"
    assert report.diagnosis == "unresolved"


def test_safe_report_contains_no_page_or_input_content() -> None:
    report = asyncio.run(
        run_diagnostic_workflow(
            reader_client=_reader(),
            embedding_client=_RecordingEmbeddingClient(),
            target_page_id="synthetic-page",
            bounded_batch_count=8,
        )
    )

    serialized = json.dumps(report.to_safe_dict(), sort_keys=True)
    assert "synthetic-page" not in serialized
    assert "Synthetic Diagnostic" not in serialized
    assert "Synthetic diagnostic section" not in serialized
    assert "payload" not in serialized
    assert '"embeddings"' not in serialized
