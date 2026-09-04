"""Shared fail-closed rendering inputs for parser benchmark fixtures."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, Mapping

from PIL import ImageFont


CONTROLLED_FONT_SHA256 = "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4"
TYPE3_RASTER_SIZE = 64
TYPE3_THRESHOLD = 96


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


def _pdf_number(value: float) -> str:
    rounded = round(value, 4)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.4f}".rstrip("0").rstrip(".")


def _type3_charproc(font: ImageFont.FreeTypeFont, char: str) -> tuple[bytes, float, tuple[float, float, float, float]]:
    mask, (offset_x, offset_y) = font.getmask2(char, mode="L", anchor="ls")
    width, height = mask.size
    scale = 1000.0 / TYPE3_RASTER_SIZE
    advance = float(font.getlength(char)) * scale
    bounds = (
        offset_x * scale,
        -(offset_y + height) * scale,
        (offset_x + width) * scale,
        -offset_y * scale,
    )
    commands = [
        " ".join(
            (
                _pdf_number(advance),
                "0",
                *(_pdf_number(value) for value in bounds),
                "d1\n",
            )
        )
    ]
    pixels = bytes(mask)
    for row in range(height):
        start: int | None = None
        for column in range(width + 1):
            active = column < width and pixels[row * width + column] >= TYPE3_THRESHOLD
            if active and start is None:
                start = column
            elif not active and start is not None:
                commands.append(
                    " ".join(
                        (
                            _pdf_number((offset_x + start) * scale),
                            _pdf_number(-(offset_y + row + 1) * scale),
                            _pdf_number((column - start) * scale),
                            _pdf_number(scale),
                            "re\n",
                        )
                    )
                )
                start = None
    commands.append("f\n")
    return "".join(commands).encode("ascii"), advance, bounds


def _type3_tounicode_cmap(char_to_code: Mapping[str, int]) -> bytes:
    entries = [
        f"<{code:02x}> <{ord(char):04x}>"
        for char, code in sorted(char_to_code.items(), key=lambda item: item[1])
    ]
    return "\n".join(
        (
            "/CIDInit /ProcSet findresource begin",
            "12 dict begin",
            "begincmap",
            "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def",
            "/CMapName /Adobe-Identity-UCS def",
            "/CMapType 2 def",
            "1 begincodespacerange",
            "<00> <ff>",
            "endcodespacerange",
            f"{len(entries)} beginbfchar",
            *entries,
            "endbfchar",
            "endcmap",
            "CMapName currentdict /CMap defineresource pop",
            "end",
            "end",
        )
    ).encode("ascii")


def build_type3_font_objects(
    *,
    font_path: Path,
    characters: Iterable[str],
    font_object_id: int,
    cmap_object_id: int,
    first_charproc_object_id: int,
    expected_sha256: str = CONTROLLED_FONT_SHA256,
) -> tuple[dict[int, bytes], dict[str, int]]:
    """Build a self-contained, selectable Type 3 font from controlled glyphs."""

    unique_characters = sorted(set(characters))
    if not unique_characters:
        raise ValueError("Type 3 font requires at least one character")
    if len(unique_characters) > 255:
        raise ValueError("Type 3 font supports at most 255 benchmark characters")
    font = load_controlled_font(
        font_path,
        size=TYPE3_RASTER_SIZE,
        expected_sha256=expected_sha256,
    )
    char_to_code = {char: index for index, char in enumerate(unique_characters, start=1)}
    objects: dict[int, bytes] = {}
    widths: list[str] = []
    charproc_entries: list[str] = []
    font_bounds: list[tuple[float, float, float, float]] = []
    glyph_names: list[str] = []
    for index, char in enumerate(unique_characters):
        glyph_name = f"g{index + 1}"
        glyph_names.append(glyph_name)
        object_id = first_charproc_object_id + index
        stream, advance, bounds = _type3_charproc(font, char)
        widths.append(_pdf_number(advance))
        font_bounds.append(bounds)
        charproc_entries.append(f"/{glyph_name} {object_id} 0 R")
        objects[object_id] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
            + stream
            + b"endstream"
        )
    cmap = _type3_tounicode_cmap(char_to_code)
    objects[cmap_object_id] = (
        f"<< /Length {len(cmap)} >>\nstream\n".encode("ascii")
        + cmap
        + b"\nendstream"
    )
    bbox = (
        min(item[0] for item in font_bounds),
        min(item[1] for item in font_bounds),
        max(item[2] for item in font_bounds),
        max(item[3] for item in font_bounds),
    )
    objects[font_object_id] = " ".join(
        (
            "<< /Type /Font /Subtype /Type3 /Name /F1",
            f"/FontBBox [{' '.join(_pdf_number(value) for value in bbox)}]",
            "/FontMatrix [0.001 0 0 0.001 0 0]",
            f"/CharProcs << {' '.join(charproc_entries)} >>",
            f"/Encoding << /Type /Encoding /Differences [1 {' '.join('/' + name for name in glyph_names)}] >>",
            f"/FirstChar 1 /LastChar {len(unique_characters)}",
            f"/Widths [{' '.join(widths)}]",
            "/Resources << >>",
            f"/ToUnicode {cmap_object_id} 0 R >>",
        )
    ).encode("ascii")
    return objects, char_to_code


__all__ = [
    "CONTROLLED_FONT_SHA256",
    "build_type3_font_objects",
    "load_controlled_font",
]
