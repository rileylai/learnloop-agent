"""Minimal scorer boundary for the parser-note completeness runner."""

from typing import Protocol

from .normalized_document import NormalizedDocument


class QualityFailure(Exception):
    """A scorer observation that must not become runner operational failure."""


class Scorer(Protocol):
    """Future metric implementations may evaluate a validated artifact here."""

    def evaluate(self, document: NormalizedDocument) -> None:
        """Observe quality without defining metrics, thresholds, or decisions."""

