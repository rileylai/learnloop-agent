"""Build the approved P03 visible-label successor reference candidate."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[7]))

from tests.evals.parser_note_completeness.v1.successor_artifacts import write_successor_reference


if __name__ == "__main__":
    write_successor_reference("P03", "revision-002", "revision-003")
