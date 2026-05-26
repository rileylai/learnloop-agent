from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from src.orchestrators import DEFAULT_SUPPLEMENT_MODEL, DEFAULT_SUPPLEMENT_PROVIDER_NAME


class SupplementProposeRequest(BaseModel):
    source_document_id: int = Field(
        ge=1,
        description="Source document id used to generate a supplement proposal.",
    )
    provider_name: str = Field(
        default=DEFAULT_SUPPLEMENT_PROVIDER_NAME,
        min_length=1,
        description="LLM provider name routed by ProviderRouter.",
    )
    model: str = Field(
        default=DEFAULT_SUPPLEMENT_MODEL,
        min_length=1,
        description="LLM model name for proposal generation.",
    )
    target_notion_page_id: Optional[int] = Field(
        default=None,
        ge=1,
        description="Optional target Notion page db id for the pending change request.",
    )


class SupplementProposeResponse(BaseModel):
    workflow_run_id: int
    status: str
    change_request_id: int
    change_request_status: str
    source_document_id: int
    duplicate_detected: bool
    duplicate_notion_path: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    token_input: Optional[int] = None
    token_output: Optional[int] = None
