"""Tests for model registry and downloader."""

from pathlib import Path

from inferwall.models.downloader import ModelDownloader
from inferwall.models.registry import (
    MODELS,
    get_model,
    get_models_for_profile,
)


class TestModelRegistry:
    def test_lite_profile_no_models(self) -> None:
        models = get_models_for_profile("lite")
        assert len(models) == 0

    def test_standard_profile_models(self) -> None:
        models = get_models_for_profile("standard")
        assert len(models) == 3
        names = {m.name for m in models}
        assert "deberta-injection" in names
        assert "distilbert-toxicity" in names
        assert "minilm-embeddings" in names

    def test_full_profile_includes_all(self) -> None:
        models = get_models_for_profile("full")
        assert len(models) == len(MODELS)
        assert any(m.name == "phi4-mini-judge" for m in models)

    def test_get_model_by_name(self) -> None:
        spec = get_model("deberta-injection")
        assert spec is not None
        assert spec.repo_id == "protectai/deberta-v3-base-prompt-injection-v2"
        assert spec.engine == "classifier"

    def test_get_model_missing(self) -> None:
        assert get_model("nonexistent") is None

    def test_all_models_have_required_fields(self) -> None:
        for name, spec in MODELS.items():
            assert spec.name == name
            assert spec.repo_id
            assert spec.engine in (
                "classifier",
                "semantic",
                "llm-judge",
            )
            assert spec.profile in ("standard", "full")
            assert spec.size_mb > 0


class TestModelDownloader:
    def test_cache_dir_created(self, tmp_path: Path) -> None:
        cache = tmp_path / "models"
        downloader = ModelDownloader(cache_dir=cache)
        assert cache.exists()
        assert downloader.cache_dir == cache

    def test_model_path(self, tmp_path: Path) -> None:
        downloader = ModelDownloader(cache_dir=tmp_path)
        spec = get_model("deberta-injection")
        assert spec is not None
        path = downloader.model_path(spec)
        assert "protectai--deberta-v3-base-prompt-injection-v2" in str(path)

    def test_not_downloaded_by_default(self, tmp_path: Path) -> None:
        downloader = ModelDownloader(cache_dir=tmp_path)
        spec = get_model("deberta-injection")
        assert spec is not None
        assert downloader.is_downloaded(spec) is False

    def test_list_empty(self, tmp_path: Path) -> None:
        downloader = ModelDownloader(cache_dir=tmp_path)
        assert downloader.list_downloaded() == []

    def test_sha256(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"hello world")
        h = ModelDownloader.compute_sha256(test_file)
        assert len(h) == 64  # SHA-256 hex


class TestEngineGracefulDegradation:
    """Test that engines work without ML deps installed."""

    def test_classifier_no_models_returns_empty(self) -> None:
        from inferwall.engines.classifier import ClassifierEngine

        engine = ClassifierEngine()
        results = engine.scan("test text", ["sig1"])
        assert results == []

    def test_classifier_loaded_models_empty(self) -> None:
        from inferwall.engines.classifier import ClassifierEngine

        engine = ClassifierEngine()
        assert engine.loaded_models == []

    def test_semantic_no_index_returns_empty(self) -> None:
        from inferwall.engines.semantic import SemanticEngine

        engine = SemanticEngine()
        results = engine.scan("test text", ["sig1"])
        assert results == []

    def test_semantic_not_loaded(self) -> None:
        from inferwall.engines.semantic import SemanticEngine

        engine = SemanticEngine()
        assert engine.is_loaded is False

    def test_composite_no_engines_returns_empty(self) -> None:
        from inferwall.engines.composite import CompositeEngine

        engine = CompositeEngine()
        results = engine.scan("test text", ["sig1"])
        assert results == []
