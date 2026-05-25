from __future__ import annotations

import pytest

from src.orchestrators import (
    SupplementProposalValidationError,
    parse_supplement_proposal_json,
)


def test_parse_supplement_proposal_json_accepts_valid_object() -> None:
    parsed = parse_supplement_proposal_json(
        """
        {
          "title": "Attention recap from source",
          "target_path": "Knowledge/NLP/Week5/AI Supplement Zone/Attention",
          "source": {
            "source_type": "pdf",
            "source_display_name": "lecture1.pdf"
          },
          "summary": "Summarizes scaled dot-product attention.",
          "concepts": ["scaled dot-product attention", "softmax weighting"],
          "notes": ["Connect this with week4 self-attention notes."]
        }
        """
    )

    assert parsed.title == "Attention recap from source"
    assert parsed.target_path == "Knowledge/NLP/Week5/AI Supplement Zone/Attention"
    assert parsed.source.source_type == "pdf"
    assert parsed.source.source_display_name == "lecture1.pdf"
    assert parsed.summary == "Summarizes scaled dot-product attention."
    assert parsed.concepts == [
        "scaled dot-product attention",
        "softmax weighting",
    ]
    assert parsed.notes == ["Connect this with week4 self-attention notes."]


def test_parse_supplement_proposal_json_supports_markdown_json_fence() -> None:
    parsed = parse_supplement_proposal_json(
        """```json
        {
          "title": "Week 5 concept patch",
          "target_path": "Knowledge/NLP/Week5/AI Supplement Zone",
          "source": {
            "source_type": "url",
            "source_display_name": "https://example.com/attention"
          },
          "summary": "Adds one concise clarification.",
          "concepts": ["attention pooling"],
          "notes": ["Review against existing week5 examples."]
        }
        ```"""
    )

    assert parsed.title == "Week 5 concept patch"
    assert parsed.source.source_type == "url"


def test_parse_supplement_proposal_json_rejects_invalid_json() -> None:
    with pytest.raises(SupplementProposalValidationError) as exc_info:
        parse_supplement_proposal_json("{not-valid-json}")

    assert exc_info.value.error_code == "LLM_OUTPUT_INVALID"
    assert exc_info.value.failure_reason == "LLM_OUTPUT_INVALID"
    assert "not valid JSON" in exc_info.value.message


def test_parse_supplement_proposal_json_rejects_missing_required_field() -> None:
    with pytest.raises(SupplementProposalValidationError) as exc_info:
        parse_supplement_proposal_json(
            """
            {
              "title": "Missing target path",
              "source": {
                "source_type": "chat_text",
                "source_display_name": "chat-2026-05-25"
              },
              "summary": "Summary text",
              "concepts": ["concept a"],
              "notes": ["note a"]
            }
            """
        )

    assert exc_info.value.error_code == "LLM_OUTPUT_INVALID"
    assert "target_path" in exc_info.value.message


def test_parse_supplement_proposal_json_rejects_non_string_list_item() -> None:
    with pytest.raises(SupplementProposalValidationError) as exc_info:
        parse_supplement_proposal_json(
            """
            {
              "title": "Type mismatch",
              "target_path": "Knowledge/NLP/Week5/AI Supplement Zone",
              "source": {
                "source_type": "screenshot",
                "source_display_name": "Screenshot batch (3 images)"
              },
              "summary": "Summary text",
              "concepts": ["concept a", 2],
              "notes": ["note a"]
            }
            """
        )

    assert exc_info.value.error_code == "LLM_OUTPUT_INVALID"
    assert "concepts" in exc_info.value.message
