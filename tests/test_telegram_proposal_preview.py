from __future__ import annotations

from src.services.telegram_proposal_preview import (
    format_bounded_note_lines,
    truncate_telegram_preview,
)


def test_notes_render_as_bounded_bullets_and_preview_truncates_safely() -> None:
    lines = format_bounded_note_lines(["first note", "second note"])
    assert lines == ["- first note", "- second note"]

    preview = truncate_telegram_preview("\n".join(lines) + "\n" + ("x" * 5000))
    assert len(preview) <= 4096
    assert preview.startswith("- first note\n- second note")
    assert preview.endswith("…")
