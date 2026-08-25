"""Shared fail-closed rendering inputs for parser benchmark fixtures."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import ImageFont


CONTROLLED_FONT_SHA256 = "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4"


def load_controlled_font(
    font_path: Path,
    *,
    size: int,
    expected_sha256: str = CONTROLLED_FONT_SHA256,
) -> ImageFont.FreeTypeFont:
    """Load the repository font only after validating its exact bytes."""

    try:
        font_bytes = font_path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"controlled benchmark font is unavailable: {font_path}") from exc
    actual_sha256 = hashlib.sha256(font_bytes).hexdigest()
    if actual_sha256 != expected_sha256:
        raise RuntimeError("controlled benchmark font digest mismatch")
    try:
        return ImageFont.truetype(str(font_path), size=size, index=0)
    except OSError as exc:
        raise RuntimeError("controlled benchmark font cannot be loaded") from exc


__all__ = ["CONTROLLED_FONT_SHA256", "load_controlled_font"]
