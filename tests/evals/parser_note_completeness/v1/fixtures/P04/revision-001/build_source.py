"""Build the deterministic mixed native-text and scanned P04 PDF draft fixture."""

from __future__ import annotations

import argparse
import zlib
from pathlib import Path
from typing import Mapping, Sequence

from PIL import Image, ImageDraw, ImageFont


PAGE_WIDTH = 640
PAGE_HEIGHT = 900
FONT_PATH = "/System/Library/Fonts/\u30d2\u30e9\u30ae\u30ce\u89d2\u30b4\u30b7\u30c3\u30af W3.ttc"
FONT_SIZE = 27
SKEW_FACTOR = 0.014
NOISE_MODULUS = 991

NATIVE_PAGES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "公式與表格 / Formula and Table",
        (
            "Native text records the English measurement note and its Chinese label.",
            "公式 / Formula: F = m * a",
            "表格保留單位與欄位關係，方便逐格定位。",
        ),
    ),
    (
        "雙語處理 / Bilingual Processing",
        (
            "Native paragraphs remain selectable while scanned pages retain image regions.",
            "中文與 English 可以在同一份 mixed PDF 中並存。",
            "The source modality changes at the page boundary, not in the profile contract.",
        ),
    ),
)

SCANNED_PAGES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "第二頁：掃描觀測",
        ("這一頁以固定 recipe 產生掃描影像與輕微傾斜。", "區域文字保留原始檢閱位置。"),
    ),
    (
        "第四頁：檢閱 Review",
        ("這一頁是 scanned page，包含中文說明與 English review label。", "影像區域可由 normalized geometry 回到來源。"),
    ),
)


def _tounicode_cmap(char_to_cid: Mapping[str, int]) -> bytes:
    entries = [f"<{cid:04x}> <{ord(char):04x}>" for char, cid in sorted(char_to_cid.items(), key=lambda item: item[1])]
    return "\n".join(
        (
            "/CIDInit /ProcSet findresource begin",
            "12 dict begin",
            "begincmap",
            "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def",
            "/CMapName /Adobe-Identity-UCS def",
            "/CMapType 2 def",
            "1 begincodespacerange",
            "<0000> <ffff>",
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


def _text_command(text: str, char_to_cid: Mapping[str, int], x: int, y: int, size: int) -> bytes:
    encoded = "".join(f"{char_to_cid[char]:04x}" for char in text)
    return f"BT /F1 {size} Tf {x} {y} Td <{encoded}> Tj ET\n".encode("ascii")


def _native_content(page_number: int, title: str, lines: Sequence[str], char_to_cid: Mapping[str, int]) -> bytes:
    output = bytearray(_text_command(title, char_to_cid, 72, 730, 16))
    y = 680
    for line in lines:
        output.extend(_text_command(line, char_to_cid, 72, y, 11))
        y -= 32
    if page_number == 1:
        left, top, row_height = 72, 500, 38
        widths = (180, 150, 120)
        total_width = sum(widths)
        total_height = row_height * 3
        output.extend(f"q 0 0 0 RG 0.8 w {left} {top - total_height} {total_width} {total_height} re S\n".encode("ascii"))
        for row in range(1, 3):
            y = top - row * row_height
            output.extend(f"{left} {y} m {left + total_width} {y} l S\n".encode("ascii"))
        x = left
        for width in widths[:-1]:
            x += width
            output.extend(f"{x} {top} m {x} {top - total_height} l S\n".encode("ascii"))
        for row, values in enumerate((("Measure", "Value", "Unit"), ("Force", "12", "N"), ("Mass", "3", "kg"))):
            x = left + 8
            for value, width in zip(values, widths):
                output.extend(_text_command(value, char_to_cid, x, top - 25 - row * row_height, 9))
                x += width
        output.extend(b"Q\n")
    return bytes(output)


def _font() -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, FONT_SIZE, index=0)


def _raster_page(page_number: int, title: str, paragraphs: tuple[str, ...]) -> tuple[int, int, bytes]:
    image = Image.new("L", (PAGE_WIDTH, PAGE_HEIGHT), color=247)
    draw = ImageDraw.Draw(image)
    font = _font()
    draw.rectangle((42, 38, PAGE_WIDTH - 42, PAGE_HEIGHT - 42), outline=45, width=2)
    draw.text((70, 72), title, fill=24, font=font)
    y = 175
    for paragraph in paragraphs:
        draw.text((70, y), paragraph, fill=32, font=font)
        y += 62
    for index in range(6):
        line_y = 360 + index * 58
        draw.line((70, line_y, PAGE_WIDTH - 70, line_y), fill=70 if index % 2 else 100, width=2)
    draw.rectangle((70, 735, 300, 820), outline=65, width=3)
    draw.rectangle((340, 735, PAGE_WIDTH - 70, 820), outline=65, width=3)
    draw.text((88, 760), "區域 A", fill=45, font=font)
    draw.text((358, 760), "Review B", fill=45, font=font)
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
            marker = (x * 19 + y * 29 + page_number * 97) % NOISE_MODULUS
            if marker == 0:
                pixels[x, y] = 0
            elif marker == NOISE_MODULUS - 1:
                pixels[x, y] = 255
            elif marker % 181 == 0:
                pixels[x, y] = max(0, pixels[x, y] - 12)
    return PAGE_WIDTH, PAGE_HEIGHT, skewed.tobytes()


def _build_pdf(native_contents: Mapping[int, bytes], scanned_images: Mapping[int, tuple[int, int, bytes]]) -> bytes:
    page_count = 4
    page_ids = list(range(3, 3 + page_count))
    content_ids = list(range(3 + page_count, 3 + 2 * page_count))
    font_id, descendant_id, cmap_id = 11, 12, 13
    image_ids = {page: 13 + index for index, page in enumerate(sorted(scanned_images), start=1)}
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] /Count {page_count} >>".encode("ascii"),
        font_id: b"<< /Type /Font /Subtype /Type0 /BaseFont /P04-Bilingual /Encoding /Identity-H /DescendantFonts [12 0 R] /ToUnicode 13 0 R >>",
        descendant_id: b"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /P04-Bilingual /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> /DW 600 >>",
    }
    all_chars = sorted({char for title, lines in NATIVE_PAGES for text in (title, *lines, "Measure", "Value", "Unit", "Force", "Mass", "12", "3", "N", "kg") for char in text})
    char_to_cid = {char: index for index, char in enumerate(all_chars, start=1)}
    cmap = _tounicode_cmap(char_to_cid)
    objects[cmap_id] = f"<< /Length {len(cmap)} >>\nstream\n".encode("ascii") + cmap + b"\nendstream"
    for page, page_id in enumerate(page_ids, start=1):
        content_id = content_ids[page - 1]
        if page in native_contents:
            content = native_contents[page]
            resources = f"/Font << /F1 {font_id} 0 R >>"
        else:
            width, height, _ = scanned_images[page]
            image_id = image_ids[page]
            content = f"q {width} 0 0 {height} 0 0 cm /Im1 Do Q\n".encode("ascii")
            resources = f"/XObject << /Im1 {image_id} 0 R >>"
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] /Resources << {resources} >> /Contents {content_id} 0 R >>"
        ).encode("ascii")
        objects[content_id] = f"<< /Length {len(content)} >>\nstream\n".encode("ascii") + content + b"endstream"
    for page, (width, height, pixels) in scanned_images.items():
        compressed = zlib.compress(pixels, level=9)
        image_id = image_ids[page]
        objects[image_id] = (
            f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} /ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode /Length {len(compressed)} >>\nstream\n".encode("ascii")
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
    output.extend(f"trailer\n<< /Size {highest_id + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    return bytes(output)


def build_pdf() -> bytes:
    native_contents = {
        1: _native_content(1, NATIVE_PAGES[0][0], NATIVE_PAGES[0][1], {char: index for index, char in enumerate(sorted({char for title, lines in NATIVE_PAGES for text in (title, *lines, "Measure", "Value", "Unit", "Force", "Mass", "12", "3", "N", "kg") for char in text}), start=1)}),
        3: _native_content(3, NATIVE_PAGES[1][0], NATIVE_PAGES[1][1], {char: index for index, char in enumerate(sorted({char for title, lines in NATIVE_PAGES for text in (title, *lines, "Measure", "Value", "Unit", "Force", "Mass", "12", "3", "N", "kg") for char in text}), start=1)}),
    }
    scanned_images = {
        2: _raster_page(2, SCANNED_PAGES[0][0], SCANNED_PAGES[0][1]),
        4: _raster_page(4, SCANNED_PAGES[1][0], SCANNED_PAGES[1][1]),
    }
    return _build_pdf(native_contents, scanned_images)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the P04 mixed native and scanned PDF")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("source.pdf"))
    args = parser.parse_args()
    args.output.write_bytes(build_pdf())


if __name__ == "__main__":
    main()
