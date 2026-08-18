"""Build the deterministic structured multi-speaker chat source for C02."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SOURCE: dict[str, Any] = {
    "conversation_id": "c02-synthetic-conversation-001",
    "messages": [
        {
            "message_id": "c02-message-001",
            "speaker_id": "speaker-alice",
            "speaker_name": "Alice / 愛麗絲",
            "thread_id": "c02-thread-main",
            "reply_to_message_id": None,
            "sequence": 0,
            "text": "先固定 parser contract，再開始實作。 Freeze the parser contract before implementation.",
            "parts": [{"kind": "text", "text": "先固定 parser contract，再開始實作。 Freeze the parser contract before implementation."}],
        },
        {
            "message_id": "c02-message-002",
            "speaker_id": "speaker-bob",
            "speaker_name": "Bob / 鮑伯",
            "thread_id": "c02-thread-main",
            "reply_to_message_id": "c02-message-001",
            "sequence": 1,
            "text": "同意，先保留 source binding。 Agreed, keep the source binding first.",
            "parts": [
                {"kind": "text", "text": "同意，先保留 source binding。 Agreed, keep the source binding first."},
                {"kind": "quote", "text": "先固定 parser contract，再開始實作。 Freeze the parser contract before implementation."},
            ],
        },
        {
            "message_id": "c02-message-003",
            "speaker_id": "speaker-chen",
            "speaker_name": "Chen / 陳",
            "thread_id": "c02-thread-main",
            "reply_to_message_id": "c02-message-002",
            "sequence": 2,
            "text": "我會用固定 bytes 驗證 digest。 I will verify the digest with fixed bytes.",
            "parts": [
                {"kind": "text", "text": "我會用固定 bytes 驗證 digest。 I will verify the digest with fixed bytes."},
                {"kind": "code", "language": "python", "text": "digest = sha256(source_bytes).hexdigest()"},
            ],
        },
        {
            "message_id": "c02-message-004",
            "speaker_id": "speaker-alice",
            "speaker_name": "Alice / 愛麗絲",
            "thread_id": "c02-thread-main",
            "reply_to_message_id": "c02-message-003",
            "sequence": 3,
            "text": "收到，review 只看 evidence，不改變契約。 Received; review evidence without changing the contract.",
            "parts": [{"kind": "text", "text": "收到，review 只看 evidence，不改變契約。 Received; review evidence without changing the contract."}],
        },
        {
            "message_id": "c02-message-005",
            "speaker_id": "speaker-chen",
            "speaker_name": "Chen / 陳",
            "thread_id": "c02-thread-followup",
            "reply_to_message_id": None,
            "sequence": 4,
            "text": "補充：中英內容要維持原順序。 Follow-up: preserve the original bilingual order.",
            "parts": [{"kind": "text", "text": "補充：中英內容要維持原順序。 Follow-up: preserve the original bilingual order."}],
        },
        {
            "message_id": "c02-message-006",
            "speaker_id": "speaker-bob",
            "speaker_name": "Bob / 鮑伯",
            "thread_id": "c02-thread-followup",
            "reply_to_message_id": "c02-message-005",
            "sequence": 5,
            "text": "可以，這個 thread 仍然獨立。 Yes, this thread remains independent.",
            "parts": [{"kind": "text", "text": "可以，這個 thread 仍然獨立。 Yes, this thread remains independent."}],
        },
    ],
}


def build_source_bytes() -> bytes:
    return (
        json.dumps(SOURCE, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the C02 structured chat source")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("source.json"))
    args = parser.parse_args()
    source_bytes = build_source_bytes()
    args.output.write_bytes(source_bytes)
    digest = hashlib.sha256(source_bytes).hexdigest()
    args.output.with_name("source.sha256").write_text(
        f"{digest}  {args.output.name}\n", encoding="ascii"
    )


if __name__ == "__main__":
    main()
