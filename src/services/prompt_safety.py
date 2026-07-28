from __future__ import annotations

from typing import Optional

PROMPT_SAFETY_VERSION = "prompt_safety_v1"
AI_SUPPLEMENT_ZONE = "AI Supplement Zone"


def format_untrusted_prompt_block(*, label: str, value: str) -> str:
    """Mark source data as untrusted and prevent delimiter breakout."""
    normalized_label = label.strip().upper()
    if not normalized_label or not normalized_label.replace("_", "").isalnum():
        raise ValueError("label must contain only letters, digits, and underscores")
    normalized_value = str(value)
    end_marker = f"[END UNTRUSTED {normalized_label}]"
    escaped_value = normalized_value.replace(
        end_marker,
        f"[ESCAPED {end_marker}]",
    )
    return (
        f"[BEGIN UNTRUSTED {normalized_label}]\n"
        f"{escaped_value}\n"
        f"{end_marker}"
    )


def is_safe_supplement_target_path(
    *,
    target_path: str,
    target_page_path: Optional[str],
) -> bool:
    """Keep a proposed display target under the selected page's supplement zone."""
    if target_page_path is None:
        return True
    normalized_target = _normalize_path(target_path)
    normalized_page = _normalize_path(target_page_path)
    if not normalized_target or not normalized_page:
        return False
    required_prefix = f"{normalized_page}/{AI_SUPPLEMENT_ZONE}/"
    if not normalized_target.startswith(required_prefix):
        return False
    suffix = normalized_target[len(required_prefix) :]
    return bool(suffix) and ".." not in suffix.split("/")


def _normalize_path(value: str) -> str:
    return "/".join(part.strip() for part in str(value).strip().split("/") if part.strip())
