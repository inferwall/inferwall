"""Classifier engine — ONNX Runtime transformer inference.

Wraps DeBERTa (injection detection) and DistilBERT (toxicity).
Falls back gracefully when onnxruntime is not installed (Lite profile).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from inferwall.engines.base import BaseEngine, ScanResult

logger = logging.getLogger(__name__)


class ClassifierEngine(BaseEngine):
    """ML classifier engine using ONNX Runtime.

    Loads ONNX models for binary/multi-class text classification.
    When models are not loaded, scan() returns empty results.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, Any] = {}
        self._tokenizers: dict[str, Any] = {}
        self._label_maps: dict[str, dict[int, str]] = {}
        self._ort_available = False
        self._tok_available = False
        self._threshold = 0.5

        try:
            import onnxruntime  # noqa: F401

            self._ort_available = True
        except ImportError:
            logger.info(
                "onnxruntime not installed — classifier engine disabled. "
                "Install with: pip install inferwall[standard]"
            )
        try:
            import tokenizers  # noqa: F401

            self._tok_available = True
        except ImportError:
            pass

    @property
    def engine_type(self) -> str:
        return "classifier"

    @property
    def is_available(self) -> bool:
        return self._ort_available and self._tok_available

    @property
    def loaded_models(self) -> list[str]:
        return list(self._sessions.keys())

    def load_model(self, name: str, model_dir: Path) -> bool:
        """Load an ONNX model + tokenizer from a directory."""
        if not self.is_available:
            return False

        import json

        import onnxruntime as ort  # noqa: F811
        from tokenizers import Tokenizer

        model_path = model_dir / "model.onnx"
        if not model_path.exists():
            model_path = model_dir / "onnx" / "model.onnx"
        if not model_path.exists():
            logger.error("No model.onnx found in %s", model_dir)
            return False

        tokenizer_path = model_dir / "tokenizer.json"
        if not tokenizer_path.exists():
            logger.error("No tokenizer.json found in %s", model_dir)
            return False

        # Load label mapping from config.json
        config_path = model_dir / "config.json"
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text())
                id2label = config.get("id2label", {})
                self._label_maps[name] = {int(k): v for k, v in id2label.items()}
            except Exception:
                self._label_maps[name] = {}
        else:
            self._label_maps[name] = {}

        try:
            session = ort.InferenceSession(
                str(model_path),
                providers=["CPUExecutionProvider"],
            )
            tokenizer = Tokenizer.from_file(str(tokenizer_path))
            self._sessions[name] = session
            self._tokenizers[name] = tokenizer
            logger.info("Loaded classifier model: %s", name)
            return True
        except Exception:
            logger.exception("Failed to load model %s", name)
            return False

    def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
        """Scan text against classifier-type signatures."""
        if not text or not signatures or not self._sessions:
            return []

        results: list[ScanResult] = []
        for sig in signatures:
            model_name = self._resolve_model(sig)
            if model_name not in self._sessions:
                continue

            try:
                confidence, label = self._infer(
                    model_name,
                    self._sessions[model_name],
                    self._tokenizers[model_name],
                    text,
                )
                if label not in self.BENIGN_LABELS and confidence >= self._threshold:
                    results.append(
                        ScanResult(
                            signature_id=self._sig_id(sig),
                            matched_text=text[:100],
                            score=float(self._sig_points(sig)),
                            offset=0,
                            length=len(text),
                            confidence=confidence,
                        )
                    )
            except Exception:
                logger.warning(
                    "Inference failed for %s", self._sig_id(sig), exc_info=True
                )

        return results

    # Labels considered benign (not flagged) across different model conventions
    BENIGN_LABELS = {
        "BENIGN", "SAFE", "LABEL_0", "not_toxic",
        "not-toxic", "safe", "ham",
    }

    def _infer(
        self, model_name: str, session: Any, tokenizer: Any, text: str
    ) -> tuple[float, str]:
        """Run ONNX inference. Returns (confidence, label)."""
        import numpy as np

        encoding = tokenizer.encode(text)
        ids = np.array([encoding.ids], dtype=np.int64)
        mask = np.array([encoding.attention_mask], dtype=np.int64)

        input_names = {inp.name for inp in session.get_inputs()}
        inputs: dict[str, Any] = {}
        if "input_ids" in input_names:
            inputs["input_ids"] = ids
        if "attention_mask" in input_names:
            inputs["attention_mask"] = mask
        if "token_type_ids" in input_names:
            inputs["token_type_ids"] = np.zeros_like(ids)

        logits = session.run(None, inputs)[0][0]
        probs = np.exp(logits - logits.max())
        probs = probs / probs.sum()

        idx = int(np.argmax(probs))

        # Resolve label from config.json id2label, fallback to DeBERTa convention
        label_map = self._label_maps.get(model_name, {})
        if label_map:
            label = label_map.get(idx, f"LABEL_{idx}")
        else:
            # Legacy fallback: DeBERTa convention (0=BENIGN, 1=INJECTION)
            label = "INJECTION" if idx == 1 else "BENIGN"

        return float(probs[idx]), label

    def _resolve_model(self, sig: Any) -> str:
        if hasattr(sig, "detection") and sig.detection.model:
            return str(sig.detection.model)
        if hasattr(sig, "meta"):
            cat = getattr(sig.meta.category, "value", sig.meta.category)
            if cat == "content-safety":
                return "distilbert-toxicity"
        return "deberta-injection"

    def _sig_id(self, sig: Any) -> str:
        return sig.signature.id if hasattr(sig, "signature") else str(sig)

    def _sig_points(self, sig: Any) -> int:
        return sig.scoring.anomaly_points if hasattr(sig, "scoring") else 5
