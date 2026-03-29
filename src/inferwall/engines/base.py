"""Engine abstraction — BaseEngine with scan() interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ScanResult:
    """Result of a single signature match from an engine scan."""

    signature_id: str
    matched_text: str
    score: float
    offset: int
    length: int


class BaseEngine(ABC):
    """Abstract base class for all detection engines."""

    @property
    @abstractmethod
    def engine_type(self) -> str:
        """Return the engine type identifier (e.g., 'heuristic', 'classifier')."""
        ...

    @abstractmethod
    def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
        """Scan text against the given signatures and return matches.

        Args:
            text: The input text to scan.
            signatures: List of signature definitions relevant to this engine.

        Returns:
            List of ScanResult objects for each match found.
        """
        ...
