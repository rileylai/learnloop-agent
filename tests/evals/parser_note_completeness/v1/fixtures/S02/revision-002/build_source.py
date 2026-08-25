"""Build deterministic project-owned screenshot-set artifacts for S02."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(PROJECT_ROOT))

from tests.evals.parser_note_completeness.v1.fixture_rendering import (  # noqa: E402
    CONTROLLED_FONT_SHA256,
    load_controlled_font,
)


IMAGE_SIZE = (640, 360)
ASSET_ROOT = Path(__file__).resolve().parents[3]
FONT_PATH = ASSET_ROOT / "assets" / "fonts" / "NotoSansCJKtc-Regular.otf"
FONT_SHA256 = CONTROLLED_FONT_SHA256


def _font(size: int) -> ImageFont.FreeTypeFont:
    return load_controlled_font(FONT_PATH, size=size, expected_sha256=FONT_SHA256)


def _draw_screen(image_index: int) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (244, 247, 251))
    draw = ImageDraw.Draw(image)
    title = "畫面一 / Screen One" if image_index == 1 else "畫面二 / Screen Two"
    overlay = "重疊標籤 / Overlay Badge" if image_index == 1 else "後續狀態 / Follow-up State"
    draw.rectangle((0, 0, 639, 359), outline=(28, 45, 68), width=2)
    draw.rectangle((24, 16, 616, 78), fill=(28, 75, 116))
    draw.text((40, 28), title, font=_font(24), fill=(255, 255, 255))
    draw.rounded_rectangle((72, 126, 432, 184), radius=10, fill=(211, 232, 247), outline=(48, 105, 146), width=2)
    draw.text((88, 143), "共同內容 / Shared Content", font=_font(20), fill=(22, 50, 75))
    draw.rounded_rectangle((380, 112, 560, 168), radius=12, fill=(248, 199, 96), outline=(162, 103, 28), width=2)
    draw.text((392, 128), overlay, font=_font(15), fill=(75, 45, 12))
    return image


def _canonical_json(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _write_digest(path: Path, digest: str, target_name: str) -> None:
    path.write_text(f"{digest}  {target_name}\n", encoding="ascii")


def build_artifacts(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    images: list[dict[str, Any]] = []
    for image_index in (1, 2):
        image_path = output_dir / f"source-{image_index:03d}.png"
        _draw_screen(image_index).save(
            image_path,
            format="PNG",
            optimize=False,
            compress_level=9,
        )
        digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
        _write_digest(output_dir / f"source-{image_index:03d}.sha256", digest, image_path.name)
        images.append(
            {
                "image_index": image_index,
                "path": image_path.name,
                "sha256": digest,
                "width": IMAGE_SIZE[0],
                "height": IMAGE_SIZE[1],
            }
        )

    manifest = {
        "images": images,
        "order_policy": "ascending_image_index",
        "offline": True,
        "shared_content": ["共同內容 / Shared Content"],
        "snapshot_version": "screenshot-set/1.0.0",
        "source_type": "screenshots",
    }
    manifest_path = output_dir / "source_manifest.json"
    manifest_path.write_bytes(_canonical_json(manifest))
    manifest_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    _write_digest(output_dir / "source.sha256", manifest_digest, "source_manifest.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the S02 screenshot set")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    build_artifacts(args.output_dir)


if __name__ == "__main__":
    main()
