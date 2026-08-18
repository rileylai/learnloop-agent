"""Build the deterministic, native-text bilingual P02 PDF draft fixture."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Mapping, Sequence


PAGE_WIDTH = 612
PAGE_HEIGHT = 792

PAGES: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    (
        "雙語資料系統報告 / Bilingual Data Systems Report",
        (
            "本報告以專案自有內容說明可追蹤的資料處理流程。",
            "This project-owned report describes an observable data workflow.",
            "文字、表格與圖形都保留在同一份 native-text PDF 中。",
            "Text, tables, and vector figures remain in one native-text PDF.",
        ),
        (),
    ),
    (
        "表一 / Table One: 事件延遲 / Event Latency",
        (
            "第一張表格比較不同處理階段的延遲。",
            "The first table compares latency across processing stages.",
        ),
        (
            "Stage / 階段|Median ms / 中位毫秒|Owner / 負責人",
            "Parse / 解析|18|Parser",
            "Index / 索引|42|Indexer",
            "Review / 審核|75|Operator",
        ),
    ),
    (
        "表二 / Table Two: 來源覆蓋 / Source Coverage",
        (
            "第二張表格保留中英文欄位名稱與數值。",
            "The second table preserves bilingual labels and values.",
        ),
        (
            "Source / 來源|Native / 原生|Reviewed / 已審核",
            "PDF|yes / 是|pending / 待處理",
            "Web|yes / 是|pending / 待處理",
            "Scan|image / 影像|pending / 待處理",
        ),
    ),
    (
        "結論 / Conclusion",
        (
            "圖一與圖二以向量線條呈現，不依賴外部影像資產。",
            "Figure One and Figure Two use vector paths without external images.",
            "這份 draft 僅用於 development validation。",
            "This draft is for development validation only.",
        ),
        (),
    ),
)


def _tounicode_cmap(char_to_cid: Mapping[str, int]) -> bytes:
    entries = []
    for char, cid in sorted(char_to_cid.items(), key=lambda item: item[1]):
        entries.append(f"<{cid:04x}> <{ord(char):04x}>")
    cmap = "\n".join(
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
    )
    return cmap.encode("ascii")


def _text_command(text: str, char_to_cid: Mapping[str, int], x: int, y: int, size: int) -> bytes:
    encoded = "".join(f"{char_to_cid[char]:04x}" for char in text)
    return f"BT /F1 {size} Tf {x} {y} Td <{encoded}> Tj ET\n".encode("ascii")


def _table_commands(rows: Sequence[str], char_to_cid: Mapping[str, int], top: int) -> bytes:
    left = 72
    row_height = 34
    column_widths = (190, 170, 108)
    lines: list[bytes] = []
    total_width = sum(column_widths)
    total_height = row_height * len(rows)
    lines.append(f"q 0 0 0 RG 0.8 w {left} {top - total_height} {total_width} {total_height} re S\n".encode("ascii"))
    for row_index in range(1, len(rows)):
        y = top - row_index * row_height
        lines.append(f"{left} {y} m {left + total_width} {y} l S\n".encode("ascii"))
    x = left
    for width in column_widths[:-1]:
        x += width
        lines.append(f"{x} {top} m {x} {top - total_height} l S\n".encode("ascii"))
    for row_index, row in enumerate(rows):
        y = top - 23 - row_index * row_height
        x = left + 8
        for cell, width in zip(row.split("|"), column_widths):
            lines.append(_text_command(cell, char_to_cid, x, y, 9))
            x += width
    lines.append(b"Q\n")
    return b"".join(lines)


def _figure_commands(number: int, char_to_cid: Mapping[str, int], top: int) -> bytes:
    left = 360
    lines = [
        f"q 0.15 0.35 0.75 rg {left} {top - 112} 170 92 re f\n".encode("ascii"),
        f"q 1 1 1 RG 2 w {left + 12} {top - 88} m {left + 75} {top - 34} l {left + 150} {top - 96} l S Q\n".encode("ascii"),
        _text_command(f"圖{number} / Figure {number}", char_to_cid, left + 20, top - 132, 9),
        b"Q\n",
    ]
    return b"".join(lines)


def _page_content(
    page_number: int,
    title: str,
    paragraphs: Iterable[str],
    rows: Sequence[str],
    char_to_cid: Mapping[str, int],
) -> bytes:
    output = bytearray()
    output.extend(_text_command(title, char_to_cid, 72, 730, 16))
    y = 690
    for paragraph in paragraphs:
        output.extend(_text_command(paragraph, char_to_cid, 72, y, 11))
        y -= 25
    if rows:
        output.extend(_table_commands(rows, char_to_cid, 570))
        output.extend(_figure_commands(1 if page_number == 2 else 2, char_to_cid, 550))
    return bytes(output)


def _build_pdf(objects: Mapping[int, bytes], page_count: int) -> bytes:
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
        f"trailer\n<< /Size {highest_id + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(output)


def build_pdf() -> bytes:
    characters = sorted({char for title, paragraphs, rows in PAGES for text in (title, *paragraphs, *rows) for char in text})
    char_to_cid = {char: index for index, char in enumerate(characters, start=1)}
    page_ids = list(range(3, 3 + len(PAGES)))
    content_ids = list(range(10, 10 + len(PAGES)))
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: (
            f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] /Count {len(PAGES)} >>"
        ).encode("ascii"),
        7: b"<< /Type /Font /Subtype /Type0 /BaseFont /P02-Bilingual /Encoding /Identity-H /DescendantFonts [8 0 R] /ToUnicode 9 0 R >>",
        8: b"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /P02-Bilingual /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> /DW 600 >>",
        9: (
            f"<< /Length {len(_tounicode_cmap(char_to_cid))} >>\nstream\n".encode("ascii")
            + _tounicode_cmap(char_to_cid)
            + b"\nendstream"
        ),
    }
    for page_number, (title, paragraphs, rows) in enumerate(PAGES, start=1):
        page_id = page_ids[page_number - 1]
        content_id = content_ids[page_number - 1]
        content = _page_content(page_number, title, paragraphs, rows, char_to_cid)
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 7 0 R >> >> /Contents {content_id} 0 R >>"
        ).encode("ascii")
        objects[content_id] = f"<< /Length {len(content)} >>\nstream\n".encode("ascii") + content + b"endstream"
    return _build_pdf(objects, len(PAGES))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the P02 native-text bilingual PDF")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("source.pdf"))
    args = parser.parse_args()
    args.output.write_bytes(build_pdf())


if __name__ == "__main__":
    main()
