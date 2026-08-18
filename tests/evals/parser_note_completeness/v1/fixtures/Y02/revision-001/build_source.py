"""Build deterministic offline YouTube caption-snapshot artifacts for Y02."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


CAPTIONS = """WEBVTT

00:00:00.000 --> 00:00:04.000
先固定契約，再開始實作。 Freeze the contract before implementation.

00:00:04.000 --> 00:00:08.500
中英字幕共享同一個 cue。 Chinese and English captions share one cue.

00:00:08.500 --> 00:00:13.000
每個段落都保留可追蹤的時間邊界。 Each segment keeps traceable time boundaries.

00:00:13.000 --> 00:00:17.500
章節只是導覽，不會創造平台身份。 Chapters guide reading without inventing platform identity.

00:00:17.500 --> 00:00:22.000
離線 snapshot 可以重現相同 bytes。 An offline snapshot reproduces the same bytes.

00:00:22.000 --> 00:00:27.500
字幕來源是專案自有內容。 The caption source is project-owned content.

00:00:27.500 --> 00:00:32.000
我們保留 cue 順序與毫秒範圍。 We preserve cue order and millisecond ranges.

00:00:32.000 --> 00:00:36.000
這份草稿只用於 development validation。 This draft is for development validation only.
"""

CHAPTERS: dict[str, Any] = {
    "chapters": [
        {
            "chapter_id": "y02-chapter-1",
            "title": "契約 / Contract",
            "start_cue_index": 0,
            "end_cue_index": 1,
            "start_ms": 0,
            "end_ms": 8500,
        },
        {
            "chapter_id": "y02-chapter-2",
            "title": "邊界 / Boundaries",
            "start_cue_index": 2,
            "end_cue_index": 4,
            "start_ms": 8500,
            "end_ms": 22000,
        },
        {
            "chapter_id": "y02-chapter-3",
            "title": "重現 / Reproduction",
            "start_cue_index": 5,
            "end_cue_index": 7,
            "start_ms": 22000,
            "end_ms": 36000,
        },
    ]
}


def _canonical_json(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _write_digest(path: Path, digest: str, target_name: str) -> None:
    path.write_text(f"{digest}  {target_name}\n", encoding="ascii")


def build_artifacts(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    captions_path = output_dir / "captions.vtt"
    chapters_path = output_dir / "chapters.json"
    captions_path.write_bytes(CAPTIONS.encode("utf-8"))
    chapters_path.write_bytes(_canonical_json(CHAPTERS))

    captions_digest = hashlib.sha256(captions_path.read_bytes()).hexdigest()
    chapters_digest = hashlib.sha256(chapters_path.read_bytes()).hexdigest()
    _write_digest(output_dir / "captions.sha256", captions_digest, "captions.vtt")
    _write_digest(output_dir / "chapters.sha256", chapters_digest, "chapters.json")

    snapshot = {
        "caption_format": "webvtt",
        "components": [
            {"path": "captions.vtt", "sha256": captions_digest},
            {"path": "chapters.json", "sha256": chapters_digest},
        ],
        "cue_count": 8,
        "identity_policy": "synthetic_platform_identity_unavailable",
        "languages": ["zh-Hant", "en"],
        "offline": True,
        "source_type": "youtube",
        "snapshot_version": "youtube-caption-snapshot/1.0.0",
    }
    snapshot_path = output_dir / "source_snapshot.json"
    snapshot_path.write_bytes(_canonical_json(snapshot))
    snapshot_digest = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    _write_digest(output_dir / "source_snapshot.sha256", snapshot_digest, "source_snapshot.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Y02 offline caption snapshot")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    build_artifacts(args.output_dir)


if __name__ == "__main__":
    main()
