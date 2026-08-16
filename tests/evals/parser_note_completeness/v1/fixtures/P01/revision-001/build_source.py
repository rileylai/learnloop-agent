"""Build the deterministic, native-text P01 PDF with Python's standard library."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


PAGE_WIDTH = 612
PAGE_HEIGHT = 792

PAGES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    (
        "Reliable Queue Workers",
        (
            ("paragraph", "A project-authored field guide to dependable background work."),
            ("paragraph", "The examples use a small queue, explicit ownership, and observable state."),
            ("list_item", "Use a stable job identifier for every unit of work."),
            ("list_item", "Make handlers safe to run again after a process loss."),
            ("list_item", "Record the reason for every terminal outcome."),
        ),
    ),
    (
        "1. Queue Contracts",
        (
            ("paragraph", "A queue contract names the work, its owner, and the acknowledgement boundary."),
            ("paragraph", "The worker may claim a job, but it must not claim success before durable completion."),
            ("list_item", "Payloads are versioned before they enter the queue."),
            ("list_item", "A lease has a visible expiry and a renewal rule."),
            ("list_item", "Acknowledgement follows the durable write."),
        ),
    ),
    (
        "2. Idempotent Jobs",
        (
            ("paragraph", "Idempotency turns a replay from a duplicate side effect into a safe observation."),
            ("paragraph", "Persist the job key with the effect so the check and write share one transaction."),
            ("code_block", "def handle(job, store):\n    if store.was_applied(job.key):\n        return \"already-applied\"\n    store.apply(job.key, job.payload)\n    return \"applied\""),
        ),
    ),
    (
        "3. Retries and Backoff",
        (
            ("paragraph", "Retries are bounded observations of a failure, not a promise that work will eventually succeed."),
            ("list_item", "Classify failures before deciding whether a retry is safe."),
            ("list_item", "Increase the delay between attempts without hiding the attempt count."),
            ("list_item", "Send exhausted work to an explicit review path."),
            ("code_block", "attempt=2\ndelay=$((attempt * 5))\nprintf 'retry in %s seconds\\n' \"$delay\""),
        ),
    ),
    (
        "4. Visibility and Heartbeats",
        (
            ("paragraph", "A worker should make ownership and progress visible without logging private payloads."),
            ("paragraph", "Heartbeat records describe the lease, not the contents of the job."),
            ("list_item", "Measure time since the last accepted heartbeat."),
            ("list_item", "Expose queue depth and age as raw operational facts."),
            ("list_item", "Keep provider and host details in bounded receipts."),
        ),
    ),
    (
        "5. Shutdown and Recovery",
        (
            ("paragraph", "Graceful shutdown stops new claims, finishes safe work, and leaves open leases visible."),
            ("paragraph", "Recovery must distinguish a closed result from a process that disappeared mid-attempt."),
            ("code_block", "def stop(worker):\n    worker.stop_claiming()\n    worker.drain_safe_work()\n    worker.record_open_leases()"),
            ("list_item", "Never convert an interrupted attempt into a fabricated success."),
        ),
    ),
    (
        "6. Testing Worker Behavior",
        (
            ("paragraph", "Tests should exercise the boundary between queue state and application state."),
            ("list_item", "Replay the same job key and verify one durable effect."),
            ("list_item", "Interrupt after claim and collect the open attempt."),
            ("list_item", "Reject malformed payloads before a handler runs."),
            ("code_block", "python -m pytest tests/test_worker.py -q\npython -m compileall worker.py"),
        ),
    ),
    (
        "7. Operational Checklist",
        (
            ("paragraph", "Use this short checklist before enabling a new worker in a local environment."),
            ("list_item", "Confirm the queue contract and idempotency key are documented."),
            ("list_item", "Confirm terminal receipts cannot be overwritten."),
            ("list_item", "Confirm failures remain distinguishable from incomplete work."),
            ("code_block", "./worker --check-contract\n./worker --print-lease-policy"),
        ),
    ),
)


def _pdf_text(value: str) -> bytes:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("ascii")


def _content_stream(blocks: Iterable[tuple[str, str]]) -> bytes:
    commands: list[bytes] = [b"BT", b"72 720 Td"]
    for kind, content in blocks:
        if kind == "heading":
            commands.extend((b"/F1 20 Tf", b"0 -28 Td", b"(" + _pdf_text(content) + b") Tj"))
            continue
        if kind == "code_block":
            commands.extend((b"/F2 9 Tf", b"0 -24 Td"))
            for line in content.splitlines():
                commands.extend((b"(" + _pdf_text(line) + b") Tj", b"0 -13 Td"))
            continue
        if kind == "list_item":
            commands.extend(
                (
                    b"/F1 11 Tf",
                    b"12 -20 Td",
                    b"(- ) Tj",
                    b"(" + _pdf_text(content) + b") Tj",
                    b"-12 0 Td",
                )
            )
            continue
        commands.extend((b"/F1 11 Tf", b"0 -20 Td", b"(" + _pdf_text(content) + b") Tj"))
    commands.append(b"ET")
    return b"\n".join(commands) + b"\n"


def _page_body(content_id: int) -> bytes:
    return (
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
        f"/Resources << /Font << /F1 11 0 R /F2 12 0 R >> >> /Contents {content_id} 0 R >>"
    ).encode("ascii")


def build_pdf() -> bytes:
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        11: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        12: b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>",
    }
    page_ids = list(range(3, 3 + len(PAGES)))
    content_ids = list(range(13, 13 + len(PAGES)))
    objects[2] = (
        f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] "
        f"/Count {len(PAGES)} >>"
    ).encode("ascii")
    for page_id, content_id, (heading, blocks) in zip(page_ids, content_ids, PAGES):
        objects[page_id] = _page_body(content_id)
        stream = _content_stream((("heading", heading), *blocks))
        objects[content_id] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"endstream"
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
        f"trailer\n<< /Size {highest_id + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the P01 native-text PDF")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("source.pdf"))
    args = parser.parse_args()
    args.output.write_bytes(build_pdf())


if __name__ == "__main__":
    main()
