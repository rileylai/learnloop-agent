from __future__ import annotations

import json
import re
from typing import List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

_JSON_CODE_BLOCK_PATTERN = re.compile(
    r"^```(?:json)?\s*(?P<body>[\s\S]*?)\s*```$",
    re.IGNORECASE,
)


class SupplementProposalValidationError(Exception):
    def __init__(self, message: str, *, field: Optional[str] = None) -> None:
        super().__init__(message)
        self.error_code = "LLM_OUTPUT_INVALID"
        self.failure_reason = "LLM_OUTPUT_INVALID"
        self.message = message
        self.field = field


class SupplementProposalSourceSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_type: str = Field(min_length=1)
    source_display_name: str = Field(min_length=1)


class SupplementProposalCitationSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_type: Optional[str] = Field(default=None, min_length=1)
    source_display_name: Optional[str] = Field(default=None, min_length=1)
    notion_path: Optional[str] = Field(default=None, min_length=1)
    page_id: Optional[str] = Field(default=None, min_length=1)
    quote: Optional[str] = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _require_citation_reference(self) -> "SupplementProposalCitationSchema":
        if not any(
            value is not None
            for value in (
                self.source_display_name,
                self.notion_path,
                self.page_id,
                self.quote,
            )
        ):
            raise ValueError(
                "citation must include source_display_name, notion_path, page_id, or quote"
            )
        return self


class SupplementProposalSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1)
    target_path: str = Field(min_length=1)
    source: SupplementProposalSourceSchema
    summary: str = Field(min_length=1)
    concepts: List[str] = Field(min_length=1)
    notes: List[str]
    citations: List[SupplementProposalCitationSchema] = Field(default_factory=list)

    @field_validator("concepts", "notes")
    @classmethod
    def _validate_non_empty_string_items(cls, items: List[str]) -> List[str]:
        normalized_items: List[str] = []
        for index, value in enumerate(items):
            if not isinstance(value, str):
                raise ValueError(f"item at index {index} must be a string")
            normalized_value = value.strip()
            if not normalized_value:
                raise ValueError(f"item at index {index} must not be empty")
            normalized_items.append(normalized_value)
        return normalized_items


def parse_supplement_proposal_json(llm_output: str) -> SupplementProposalSchema:
    normalized_output = llm_output.strip()
    if not normalized_output:
        raise SupplementProposalValidationError("LLM output is empty")

    json_payload = _extract_json_payload(normalized_output)
    try:
        parsed_value = json.loads(json_payload)
    except json.JSONDecodeError as exc:
        raise SupplementProposalValidationError(
            "LLM output is not valid JSON"
        ) from exc

    if not isinstance(parsed_value, dict):
        raise SupplementProposalValidationError(
            "LLM output JSON must be an object"
        )

    try:
        return SupplementProposalSchema.model_validate(parsed_value)
    except ValidationError as exc:
        first_error = exc.errors()[0]
        error_loc = ".".join(str(part) for part in first_error.get("loc", []))
        error_message = first_error.get("msg", "schema validation failed")
        raise SupplementProposalValidationError(
            f"LLM output schema validation failed at '{error_loc}': {error_message}"
        ) from exc


def _extract_json_payload(llm_output: str) -> str:
    code_block_match = _JSON_CODE_BLOCK_PATTERN.match(llm_output)
    if code_block_match:
        return code_block_match.group("body").strip()
    return llm_output
