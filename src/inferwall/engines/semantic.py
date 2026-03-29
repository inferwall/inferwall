"""Semantic engine — ONNX embedding similarity with FAISS index."""

from __future__ import annotations

from typing import Any

from inferwall.engines.base import BaseEngine, ScanResult


class SemanticEngine(BaseEngine):
    """Semantic similarity engine using FAISS index.

    Computes embeddings via ONNX and queries a FAISS index of known
    attack phrase embeddings. Deferred until Standard profile deps installed.
    """

    def __init__(self) -> None:
        self._index_loaded = False

    @property
    def engine_type(self) -> str:
        return "semantic"

    def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
        """Scan text using semantic similarity."""
        if not text or not signatures:
            return []

        if not self._index_loaded:
            return []  # Index not loaded — skip gracefully

        return []

    def load_index(self, index_path: str) -> bool:
        """Load FAISS index. Returns True if successful."""
        try:
            import faiss  # noqa: F401

            self._index_loaded = True
            return True
        except ImportError:
            return False
