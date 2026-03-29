"""Heuristic engine — thin wrapper around Rust inferwall_core."""

from __future__ import annotations

from typing import Any

import inferwall_core

from inferwall.engines.base import BaseEngine, ScanResult
from inferwall.signatures.schema import SignatureDefinition


class HeuristicEngine(BaseEngine):
    """Heuristic detection engine backed by Rust extension."""

    @property
    def engine_type(self) -> str:
        return "heuristic"

    def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
        """Scan text using Rust heuristic engine."""
        if not text or not signatures:
            return []

        rust_sigs = []
        for sig in signatures:
            if isinstance(sig, SignatureDefinition):
                rust_sigs.append(self._convert_signature(sig))
            else:
                rust_sigs.append(sig)

        preprocess_result, matches = inferwall_core.scan_heuristic_with_preprocess(
            text, rust_sigs
        )

        return [
            ScanResult(
                signature_id=m.signature_id,
                matched_text=m.matched_text,
                score=m.score,
                offset=m.offset,
                length=m.length,
            )
            for m in matches
        ]

    def _convert_signature(
        self, sig: SignatureDefinition
    ) -> inferwall_core.PyHeuristicSignature:
        """Convert a SignatureDefinition to a Rust-compatible signature."""
        patterns = []
        if sig.detection.patterns:
            for p in sig.detection.patterns:
                patterns.append(
                    inferwall_core.PyHeuristicPattern(
                        pattern_type=p.type.value,
                        value=p.value or "",
                        case_insensitive=p.case_insensitive or True,
                    )
                )

        return inferwall_core.PyHeuristicSignature(
            id=sig.signature.id,
            patterns=patterns,
            condition=sig.detection.condition.value,
            anomaly_points=float(sig.scoring.anomaly_points),
        )
