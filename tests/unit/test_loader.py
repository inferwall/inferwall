"""Tests for signature loader — written BEFORE implementation (TDD)."""

from pathlib import Path

import pytest
import yaml

from inferwall.signatures.loader import SignatureLoader

# --- Test signature data ---


def _make_sig(
    sig_id: str,
    engine: str = "heuristic",
    direction: str = "input",
    category: str = "prompt-injection",
    points: int = 8,
) -> dict:
    return {
        "signature": {"id": sig_id, "name": f"Test {sig_id}", "version": "1.0.0"},
        "meta": {
            "category": category,
            "subcategory": "direct",
            "technique": "test-technique",
            "severity": "high",
            "confidence": "high",
            "performance_cost": "low",
        },
        "detection": {
            "engine": engine,
            "direction": direction,
            "patterns": [{"type": "regex", "value": r"test"}],
            "condition": "any",
        },
        "scoring": {"anomaly_points": points},
        "tuning": {
            "enabled": True,
            "default_enabled": True,
            "default_action": "enforce",
        },
    }


def _write_sig(directory: Path, sig_id: str, **kwargs) -> Path:  # type: ignore[no-untyped-def]
    data = _make_sig(sig_id, **kwargs)
    path = directory / f"{sig_id}.yaml"
    path.write_text(yaml.dump(data))
    return path


class TestSignatureLoaderLoad:
    """Test loading signatures from a directory."""

    def test_load_empty_directory(self, tmp_path: Path) -> None:
        loader = SignatureLoader(tmp_path)
        sigs = loader.load()
        assert len(sigs) == 0

    def test_load_single_signature(self, tmp_path: Path) -> None:
        _write_sig(tmp_path, "INJ-D-001")
        loader = SignatureLoader(tmp_path)
        sigs = loader.load()
        assert len(sigs) == 1
        assert sigs[0].signature.id == "INJ-D-001"

    def test_load_multiple_signatures(self, tmp_path: Path) -> None:
        _write_sig(tmp_path, "INJ-D-001")
        _write_sig(tmp_path, "INJ-D-002")
        _write_sig(tmp_path, "INJ-D-003")
        loader = SignatureLoader(tmp_path)
        sigs = loader.load()
        assert len(sigs) == 3

    def test_load_ignores_non_yaml_files(self, tmp_path: Path) -> None:
        _write_sig(tmp_path, "INJ-D-001")
        (tmp_path / "README.md").write_text("not a signature")
        (tmp_path / "config.json").write_text("{}")
        loader = SignatureLoader(tmp_path)
        sigs = loader.load()
        assert len(sigs) == 1

    def test_load_handles_yml_extension(self, tmp_path: Path) -> None:
        data = _make_sig("INJ-D-001")
        (tmp_path / "INJ-D-001.yml").write_text(yaml.dump(data))
        loader = SignatureLoader(tmp_path)
        sigs = loader.load()
        assert len(sigs) == 1


class TestSignatureLoaderIndexing:
    """Test that loaded signatures are indexed by ID."""

    def test_get_by_id(self, tmp_path: Path) -> None:
        _write_sig(tmp_path, "INJ-D-001")
        _write_sig(tmp_path, "INJ-D-002")
        loader = SignatureLoader(tmp_path)
        loader.load()
        sig = loader.get_by_id("INJ-D-001")
        assert sig is not None
        assert sig.signature.id == "INJ-D-001"

    def test_get_by_id_missing(self, tmp_path: Path) -> None:
        _write_sig(tmp_path, "INJ-D-001")
        loader = SignatureLoader(tmp_path)
        loader.load()
        sig = loader.get_by_id("NONEXISTENT")
        assert sig is None

    def test_get_all_ids(self, tmp_path: Path) -> None:
        _write_sig(tmp_path, "INJ-D-001")
        _write_sig(tmp_path, "INJ-D-002")
        loader = SignatureLoader(tmp_path)
        loader.load()
        ids = loader.get_all_ids()
        assert set(ids) == {"INJ-D-001", "INJ-D-002"}


class TestSignatureLoaderGroupByEngine:
    """Test grouping signatures by engine type."""

    def test_group_by_engine(self, tmp_path: Path) -> None:
        _write_sig(tmp_path, "INJ-D-001", engine="heuristic")
        _write_sig(tmp_path, "INJ-D-002", engine="heuristic")
        _write_sig(tmp_path, "CS-T-001", engine="classifier")
        loader = SignatureLoader(tmp_path)
        loader.load()
        groups = loader.group_by_engine()
        assert len(groups["heuristic"]) == 2
        assert len(groups["classifier"]) == 1

    def test_group_by_engine_empty(self, tmp_path: Path) -> None:
        loader = SignatureLoader(tmp_path)
        loader.load()
        groups = loader.group_by_engine()
        assert len(groups) == 0


class TestSignatureLoaderErrorHandling:
    """Test handling of corrupt/invalid signature files."""

    def test_invalid_yaml_skipped_with_error(self, tmp_path: Path) -> None:
        (tmp_path / "bad.yaml").write_text("{{invalid yaml::")
        _write_sig(tmp_path, "INJ-D-001")
        loader = SignatureLoader(tmp_path)
        sigs = loader.load()
        assert len(sigs) == 1
        assert len(loader.errors) == 1

    def test_invalid_schema_skipped_with_error(self, tmp_path: Path) -> None:
        bad_data = {"signature": {"id": "bad"}}
        (tmp_path / "bad-schema.yaml").write_text(yaml.dump(bad_data))
        _write_sig(tmp_path, "INJ-D-001")
        loader = SignatureLoader(tmp_path)
        sigs = loader.load()
        assert len(sigs) == 1
        assert len(loader.errors) == 1

    def test_error_includes_filename(self, tmp_path: Path) -> None:
        (tmp_path / "broken.yaml").write_text("{{invalid")
        loader = SignatureLoader(tmp_path)
        loader.load()
        assert "broken.yaml" in loader.errors[0]

    def test_nonexistent_directory_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            SignatureLoader(Path("/nonexistent/path"))


class TestSignatureLoaderSubdirectories:
    """Test loading from nested directories."""

    def test_load_from_subdirectories(self, tmp_path: Path) -> None:
        injection_dir = tmp_path / "injection"
        injection_dir.mkdir()
        dl_dir = tmp_path / "data-leakage"
        dl_dir.mkdir()
        _write_sig(injection_dir, "INJ-D-001")
        _write_sig(dl_dir, "DL-P-001", category="data-leakage")
        loader = SignatureLoader(tmp_path)
        sigs = loader.load()
        assert len(sigs) == 2
