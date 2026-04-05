"""Semantic engine — ONNX embedding + FAISS similarity search.

Computes text embeddings and compares against an index of known
attack phrases. Falls back gracefully when deps not installed.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from inferwall.engines.base import BaseEngine, ScanResult

logger = logging.getLogger(__name__)


class SemanticEngine(BaseEngine):
    """Semantic similarity engine using ONNX embeddings + FAISS index.

    When models/index are not loaded, scan() returns empty results.
    """

    def __init__(self, similarity_threshold: float = 0.85) -> None:
        self._session: Any = None
        self._tokenizer: Any = None
        self._index: Any = None
        self._index_labels: list[str] = []
        self._threshold = similarity_threshold
        self._available = False

        try:
            import faiss  # noqa: F401
            import onnxruntime  # noqa: F401

            self._available = True
        except ImportError:
            logger.info(
                "faiss-cpu or onnxruntime not installed — semantic engine disabled. "
                "Install with: pip install inferwall[standard]"
            )

    @property
    def engine_type(self) -> str:
        return "semantic"

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def is_loaded(self) -> bool:
        return self._session is not None and self._index is not None

    def load_model(self, model_dir: Path) -> bool:
        """Load the ONNX embedding model."""
        if not self._available:
            return False

        import onnxruntime as ort  # noqa: F811
        from tokenizers import Tokenizer

        model_path = model_dir / "model.onnx"
        if not model_path.exists():
            model_path = model_dir / "onnx" / "model.onnx"
        if not model_path.exists():
            logger.error("No model.onnx in %s", model_dir)
            return False

        tokenizer_path = model_dir / "tokenizer.json"
        if not tokenizer_path.exists():
            logger.error("No tokenizer.json in %s", model_dir)
            return False

        try:
            self._session = ort.InferenceSession(
                str(model_path), providers=["CPUExecutionProvider"]
            )
            self._tokenizer = Tokenizer.from_file(str(tokenizer_path))
            logger.info("Loaded semantic embedding model from %s", model_dir)
            return True
        except Exception:
            logger.exception("Failed to load semantic model")
            return False

    def load_index(self, index_path: Path) -> bool:
        """Load a pre-built FAISS index."""
        if not self._available:
            return False

        import faiss  # noqa: F811

        try:
            self._index = faiss.read_index(str(index_path))
            logger.info("Loaded FAISS index: %d vectors", self._index.ntotal)
            return True
        except Exception:
            logger.exception("Failed to load FAISS index")
            return False

    def build_index(self, phrases: list[str], labels: list[str]) -> bool:
        """Build a FAISS index from reference attack phrases."""
        if not self._available or self._session is None:
            return False

        import faiss  # noqa: F811
        import numpy as np

        embeddings = [self._embed(phrase) for phrase in phrases]
        matrix = np.array(embeddings, dtype=np.float32)

        # Normalize for cosine similarity
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1
        matrix = matrix / norms

        dim = matrix.shape[1]
        self._index = faiss.IndexFlatIP(dim)  # Inner product = cosine on normalized
        self._index.add(matrix)
        self._index_labels = labels
        logger.info("Built FAISS index: %d phrases, %d dims", len(phrases), dim)
        return True

    def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
        """Scan text against semantic similarity signatures."""
        if not text or not signatures or not self.is_loaded:
            return []

        import numpy as np

        try:
            embedding = self._embed(text)
            query = np.array([embedding], dtype=np.float32)
            norms = np.linalg.norm(query, axis=1, keepdims=True)
            norms[norms == 0] = 1
            query = query / norms

            k = min(10, self._index.ntotal)
            distances, indices = self._index.search(query, k)

            # Collect best similarity per signature ID
            best_per_sig: dict[str, float] = {}
            for dist, idx in zip(distances[0], indices[0], strict=True):
                if idx < 0:
                    continue
                label = self._index_labels[idx] if idx < len(self._index_labels) else ""
                if label and dist > best_per_sig.get(label, 0.0):
                    best_per_sig[label] = float(dist)

            # Match against signatures using per-sig threshold
            results: list[ScanResult] = []
            matched_ids: set[str] = set()
            for sig in signatures:
                sig_id = self._sig_id(sig)
                if sig_id in matched_ids:
                    continue
                similarity = best_per_sig.get(sig_id, 0.0)
                threshold = self._sig_threshold(sig)
                if similarity >= threshold:
                    matched_ids.add(sig_id)
                    points = self._sig_points(sig)
                    results.append(
                        ScanResult(
                            signature_id=sig_id,
                            matched_text=f"semantic similarity={similarity:.3f}",
                            score=float(points),
                            offset=0,
                            length=len(text),
                            confidence=similarity,
                        )
                    )

            return results
        except Exception:
            logger.warning("Semantic scan failed", exc_info=True)
            return []

    def _embed(self, text: str) -> list[float]:
        """Compute embedding for a text string."""
        import numpy as np

        encoding = self._tokenizer.encode(text)
        ids = np.array([encoding.ids], dtype=np.int64)
        mask = np.array([encoding.attention_mask], dtype=np.int64)

        input_names = {inp.name for inp in self._session.get_inputs()}
        inputs: dict[str, Any] = {}
        if "input_ids" in input_names:
            inputs["input_ids"] = ids
        if "attention_mask" in input_names:
            inputs["attention_mask"] = mask
        if "token_type_ids" in input_names:
            inputs["token_type_ids"] = np.zeros_like(ids)

        outputs = self._session.run(None, inputs)
        # Mean pooling over token embeddings
        token_embeddings = outputs[0][0]  # (seq_len, hidden_dim)
        attention = mask[0].astype(np.float32)
        pooled = (token_embeddings * attention[:, None]).sum(axis=0)
        pooled = pooled / max(attention.sum(), 1)
        result: list[float] = pooled.tolist()
        return result

    def _sig_id(self, sig: Any) -> str:
        return sig.signature.id if hasattr(sig, "signature") else str(sig)

    def _sig_points(self, sig: Any) -> int:
        return sig.scoring.anomaly_points if hasattr(sig, "scoring") else 5

    def _sig_threshold(self, sig: Any) -> float:
        """Get per-signature similarity threshold, falling back to engine default."""
        if hasattr(sig, "detection") and sig.detection.patterns:
            for p in sig.detection.patterns:
                if p.similarity_threshold is not None:
                    return float(p.similarity_threshold)
        return self._threshold
