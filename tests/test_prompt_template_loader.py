from __future__ import annotations

from src.services import (
    PROMPT_ID_QA_ANSWER,
    PROMPT_ID_SUPPLEMENT_PROPOSAL,
    PromptTemplateLoader,
)


def test_prompt_template_loader_loads_and_renders_qa_prompt() -> None:
    loader = PromptTemplateLoader()

    bundle = loader.load_bundle(PROMPT_ID_QA_ANSWER)
    system_message, user_message = bundle.render_messages(
        variables={
            "query": "What does positional encoding do?",
            "context_text": "[C1] path=Knowledge/NLP/Week5\nPositional encoding adds order.",
        }
    )

    assert bundle.prompt_id == PROMPT_ID_QA_ANSWER
    assert bundle.version == "qa_answer_v1"
    assert "Answer only from the provided context." in system_message
    assert "What does positional encoding do?" in user_message
    assert "Knowledge/NLP/Week5" in user_message


def test_prompt_template_loader_loads_and_renders_supplement_prompt() -> None:
    loader = PromptTemplateLoader()

    bundle = loader.load_bundle(PROMPT_ID_SUPPLEMENT_PROPOSAL)
    system_message, user_message = bundle.render_messages(
        variables={
            "source_type": "chat_text",
            "source_display_name": "chat-2026-06-17",
            "source_text": "Source notes about residual connections and layer normalization.",
        }
    )

    assert bundle.prompt_id == PROMPT_ID_SUPPLEMENT_PROPOSAL
    assert bundle.version == "supplement_proposal_v1"
    assert "Return one strict JSON object" in system_message
    assert "source_type=chat_text" in user_message
    assert "chat-2026-06-17" in user_message
