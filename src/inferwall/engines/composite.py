"""Composite engine — chains multiple engines with conditional logic."""

from __future__ import annotations

from typing import Any

from inferwall.engines.base import BaseEngine, ScanResult


class CompositeEngine(BaseEngine):
    """Chains multiple engines with conditional escalation.

    Example: heuristic first, escalate to classifier if uncertain.
    """

    def __init__(self, engines: list[BaseEngine] | None = None) -> None:
        self._engines = engines or []

    @property
    def engine_type(self) -> str:
        return "composite"

    def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
        """Scan through chained engines."""
        if not text or not signatures:
            return []

        all_results: list[ScanResult] = []
        for engine in self._engines:
            results = engine.scan(text, signatures)
            all_results.extend(results)
            # Could implement early exit or conditional escalation here

        return all_results
