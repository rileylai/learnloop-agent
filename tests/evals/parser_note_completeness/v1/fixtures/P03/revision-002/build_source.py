"""Build the deterministic raster-only P03 scanned PDF draft fixture."""

from __future__ import annotations

import argparse
import hashlib
import sys
import zlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(PROJECT_ROOT))

from tests.evals.parser_note_completeness.v1.fixture_rendering import (  # noqa: E402
    CONTROLLED_FONT_SHA256,
    load_controlled_font,
)


PAGE_WIDTH = 640
PAGE_HEIGHT = 900
ASSET_ROOT = Path(__file__).resolve().parents[3]
FONT_PATH = ASSET_ROOT / "assets" / "fonts" / "NotoSansCJKtc-Regular.otf"
FONT_SHA256 = CONTROLLED_FONT_SHA256
FONT_SIZE = 27
SKEW_FACTOR = 0.018
NOISE_MODULUS = 997

PAGES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("第一頁：穩定資料流程", ("固定角度與微量雜訊保留掃描來源的真實形狀。", "本頁說明資料如何從來源進入處理流程。")),
    ("第二頁：分段與順序", ("每一頁都依照原始閱讀順序保存，段落不重新排列。", "分段記錄讓後續轉錄能回到影像區域。")),
    ("第三頁：錯誤與重試", ("失敗必須被記錄，重試不能掩蓋原始的處理結果。", "雜訊不代表內容遺失，而是掃描條件的一部分。")),
    ("第四頁：檢閱與來源", ("檢閱者可以使用頁碼與區域定位原始文字。", "這份 project-owned 草稿不包含外部連結或私人資料。")),
    ("第五頁：恢復與結論", ("恢復程序保留每一頁的來源影像與轉錄順序。", "固定 recipe 讓每次建置得到相同的 PDF bytes。")),
)


def _font() -> ImageFont.FreeTypeFont:
    return load_controlled_font(FONT_PATH, size=FONT_SIZE, expected_sha256=FONT_SHA256)


def _raster_page(page_number: int, title: str, paragraphs: tuple[str, ...]) -> tuple[int, int, bytes]:
    image = Image.new("L", (PAGE_WIDTH, PAGE_HEIGHT), color=248)
    draw = ImageDraw.Draw(image)
    font = _font()
    draw.rectangle((42, 38, PAGE_WIDTH - 42, PAGE_HEIGHT - 42), outline=42, width=2)
    draw.text((70, 72), title, fill=22, font=font)
    draw.text((70, 135), f"掃描頁碼 {page_number}", fill=35, font=font)
    y = 215
    for paragraph in paragraphs:
        draw.text((70, y), paragraph, fill=30, font=font)
        y += 58
    for index in range(5):
        line_y = 390 + index * 62
        draw.line((70, line_y, PAGE_WIDTH - 72, line_y), fill=94 if index % 2 else 62, width=2)
    draw.rectangle((70, 720, 315, 816), outline=70, width=3)
    draw.rectangle((350, 720, PAGE_WIDTH - 72, 816), outline=70, width=3)
    draw.text((88, 750), "區域甲", fill=40, font=font)
    draw.text((368, 750), "區域乙", fill=40, font=font)

    skewed = image.transform(
        image.size,
        Image.Transform.AFFINE,
        (1.0, -SKEW_FACTOR, PAGE_HEIGHT * SKEW_FACTOR / 2, 0.0, 1.0, 0.0),
        resample=Image.Resampling.BICUBIC,
        fillcolor=250,
    )
    pixels = skewed.load()
    for y in range(PAGE_HEIGHT):
        for x in range(PAGE_WIDTH):
            marker = (x * 17 + y * 31 + page_number * 101) % NOISE_MODULUS
            if marker == 0:
                pixels[x, y] = 0
            elif marker == NOISE_MODULUS - 1:
                pixels[x, y] = 255
            elif marker % 173 == 0:
                pixels[x, y] = max(0, pixels[x, y] - 10)
    return PAGE_WIDTH, PAGE_HEIGHT, skewed.tobytes()


def _image_pdf(images: list[tuple[int, int, bytes]]) -> bytes:
    page_ids = list(range(3, 3 + len(images)))
    content_ids = list(range(3 + len(images), 3 + 2 * len(images)))
    image_ids = list(range(3 + 2 * len(images), 3 + 3 * len(images)))
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: (
            f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] /Count {len(images)} >>"
        ).encode("ascii"),
    }
    for page_id, content_id, image_id, (width, height, pixels) in zip(page_ids, content_ids, image_ids, images):
        content = f"q {width} 0 0 {height} 0 0 cm /Im1 Do Q\n".encode("ascii")
        compressed = zlib.compress(pixels, level=9)
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] "
            f"/Resources << /XObject << /Im1 {image_id} 0 R >> >> /Contents {content_id} 0 R >>"
        ).encode("ascii")
        objects[content_id] = f"<< /Length {len(content)} >>\nstream\n".encode("ascii") + content + b"endstream"
        objects[image_id] = (
            f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
            f"/ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode /Length {len(compressed)} >>\nstream\n".encode("ascii")
            + compressed
            + b"\nendstream"
        )
    highest_id = max(objects)
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0] * (highest_id + 1)
    for object_id in range(1, highest_id + 1):
        offsets[object_id] = len(output)
        output.extend(f"{object_id} 0 obj\n".encode("ascii"))
        output.extend(objects[object_id])
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {highest_id + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {highest_id + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)


def build_pdf() -> bytes:
    images = [_raster_page(index, title, paragraphs) for index, (title, paragraphs) in enumerate(PAGES, start=1)]
    return _image_pdf(images)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the P03 deterministic raster-only scanned PDF")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("source.pdf"))
    args = parser.parse_args()
    data = build_pdf()
    args.output.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    args.output.with_name("source.sha256").write_text(
        f"{digest}  {args.output.name}\n",
        encoding="ascii",
    )


if __name__ == "__main__":
    main()
