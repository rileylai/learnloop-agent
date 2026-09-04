"""Build the approved W03 visible-figure-text successor reference candidate."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[7]))

from tests.evals.parser_note_completeness.v1.successor_artifacts import write_successor_reference


if __name__ == "__main__":
    write_successor_reference("W03", "revision-001", "revision-002")
