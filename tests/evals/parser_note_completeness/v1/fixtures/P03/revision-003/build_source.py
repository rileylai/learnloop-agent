"""Rebuild the byte-identical P03 source for the corrected reference revision."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[7]))

from tests.evals.parser_note_completeness.v1.successor_artifacts import clone_predecessor_source


if __name__ == "__main__":
    clone_predecessor_source(
        case_id="P03",
        predecessor_revision="revision-002",
        output=Path(__file__).with_name("source.pdf"),
    )
