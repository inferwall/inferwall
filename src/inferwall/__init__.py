"""InferenceWall — Signature-based AI application firewall."""

from __future__ import annotations

from typing import Any

from inferwall.core.pipeline import Pipeline, ScanResponse

__version__ = "0.1.1"

# Global singleton
_default_pipeline: Pipeline | None = None


def _get_pipeline() -> Pipeline:
    global _default_pipeline  # noqa: PLW0603
    if _default_pipeline is None:
        _default_pipeline = Pipeline()
    return _default_pipeline


def scan_input(text: str, **kwargs: Any) -> ScanResponse:
    """Scan input text (user prompt) for threats.

    Usage:
        import inferwall
        result = inferwall.scan_input("user prompt here")
        if result.decision == "block":
            # handle blocked request
    """
    return _get_pipeline().scan_input(text, **kwargs)


def scan_output(text: str, **kwargs: Any) -> ScanResponse:
    """Scan output text (LLM response) for data leakage.

    Usage:
        import inferwall
        result = inferwall.scan_output("LLM response here")
    """
    return _get_pipeline().scan_output(text, **kwargs)
