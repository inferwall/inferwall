"""Classifier engine — ONNX Runtime DeBERTa/DistilBERT inference."""

from __future__ import annotations

from typing import Any

from inferwall.engines.base import BaseEngine, ScanResult


class ClassifierEngine(BaseEngine):
    """ML classifier engine using ONNX Runtime.

    Wraps DeBERTa (injection detection) and DistilBERT (toxicity).
    Actual model loading deferred until Standard profile deps are installed.
    """

    def __init__(self) -> None:
        self._model_loaded = False
        self._model: Any = None
        self._tokenizer: Any = None

    @property
    def engine_type(self) -> str:
        return "classifier"

    def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
        """Scan text using classifier model."""
        if not text or not signatures:
            return []

        if not self._model_loaded:
            return []  # Model not loaded — skip gracefully

        # Model inference would go here when ONNX Runtime is available
        return []

    def load_model(self, model_path: str) -> bool:
        """Load ONNX model. Returns True if successful."""
        try:
            import onnxruntime  # noqa: F401

            # Model loading would happen here
            self._model_loaded = True
            return True
        except ImportError:
            return False
