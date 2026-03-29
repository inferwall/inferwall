"""Tests for three-layer catalog merge and user config directories."""

from pathlib import Path

import yaml

from inferwall.signatures.loader import SignatureLoader


def _make_sig(
    sig_id: str,
    engine: str = "heuristic",
    direction: str = "input",
    points: int = 8,
) -> dict:
    return {
        "signature": {
            "id": sig_id,
            "name": f"Test {sig_id}",
            "version": "1.0.0",
        },
        "meta": {
            "category": "prompt-injection",
            "subcategory": "direct",
            "technique": "test",
            "severity": "high",
            "confidence": "high",
            "performance_cost": "low",
        },
        "detection": {
            "engine": engine,
            "direction": direction,
            "patterns": [{"type": "regex", "value": "test"}],
            "condition": "any",
        },
        "scoring": {"anomaly_points": points},
        "tuning": {
            "enabled": True,
            "default_enabled": True,
            "default_action": "enforce",
        },
    }


def _write_sig(directory: Path, sig_id: str, **kwargs: object) -> Path:
    data = _make_sig(sig_id, **kwargs)  # type: ignore[arg-type]
    path = directory / f"{sig_id}.yaml"
    path.write_text(yaml.dump(data))
    return path


class TestThreeLayerMerge:
    """Test the three-layer catalog merge system."""

    def test_shipped_catalog_loads_by_default(self) -> None:
        """Default load_merged picks up shipped catalog."""
        loader = SignatureLoader()
        sigs = loader.load_merged()
        assert len(sigs) == 70
        assert len(loader.errors) == 0

    def test_custom_sigs_override_shipped(
        self, tmp_path: Path, monkeypatch: object
    ) -> None:
        """Custom signatures with same ID override shipped ones."""
        custom_dir = tmp_path / "custom_sigs"
        custom_dir.mkdir()

        # Create a custom override of INJ-D-001 with different points
        _write_sig(custom_dir, "INJ-D-001", points=15)

        # Point env var to custom dir
        import os

        os.environ["IW_SIGNATURES_DIR"] = str(custom_dir)
        try:
            loader = SignatureLoader()
            sigs = loader.load_merged()

            # Should still have 70 sigs (override, not add)
            assert len(sigs) == 70

            # The overridden sig should have new points
            sig = loader.get_by_id("INJ-D-001")
            assert sig is not None
            assert sig.scoring.anomaly_points == 15
        finally:
            os.environ.pop("IW_SIGNATURES_DIR", None)

    def test_custom_sigs_add_new(self, tmp_path: Path) -> None:
        """Custom signatures with new IDs are added."""
        custom_dir = tmp_path / "custom_sigs"
        custom_dir.mkdir()

        _write_sig(custom_dir, "CUSTOM-001", points=10)

        import os

        os.environ["IW_SIGNATURES_DIR"] = str(custom_dir)
        try:
            loader = SignatureLoader()
            sigs = loader.load_merged()

            # 70 shipped + 1 custom
            assert len(sigs) == 71

            custom = loader.get_by_id("CUSTOM-001")
            assert custom is not None
            assert custom.scoring.anomaly_points == 10
        finally:
            os.environ.pop("IW_SIGNATURES_DIR", None)

    def test_env_var_custom_dir(self, tmp_path: Path) -> None:
        """IW_SIGNATURES_DIR env var is respected."""
        custom_dir = tmp_path / "my_sigs"
        custom_dir.mkdir()
        _write_sig(custom_dir, "ENV-001")

        import os

        os.environ["IW_SIGNATURES_DIR"] = str(custom_dir)
        try:
            loader = SignatureLoader()
            loader.load_merged()
            assert loader.get_by_id("ENV-001") is not None
        finally:
            os.environ.pop("IW_SIGNATURES_DIR", None)

    def test_nonexistent_custom_dir_ignored(self) -> None:
        """Missing custom dir doesn't break loading."""
        import os

        os.environ["IW_SIGNATURES_DIR"] = "/nonexistent/path"
        try:
            loader = SignatureLoader()
            sigs = loader.load_merged()
            assert len(sigs) == 70  # Just shipped
        finally:
            os.environ.pop("IW_SIGNATURES_DIR", None)

    def test_backward_compatible_single_dir(self, tmp_path: Path) -> None:
        """Old-style single-directory loading still works."""
        _write_sig(tmp_path, "COMPAT-001")
        loader = SignatureLoader(tmp_path)
        sigs = loader.load()
        assert len(sigs) == 1
        assert sigs[0].signature.id == "COMPAT-001"


class TestCustomPolicy:
    """Test custom policy loading."""

    def test_env_var_policy_path(self, tmp_path: Path) -> None:
        """IW_POLICY_PATH env var loads custom policy."""
        policy_data = {
            "name": "custom",
            "version": "1.0.0",
            "mode": "monitor",
            "thresholds": {
                "inbound_flag": 3,
                "inbound_block": 10,
                "outbound_flag": 3,
                "outbound_block": 7,
                "early_exit": 20,
            },
            "signatures": {},
        }
        policy_path = tmp_path / "custom.yaml"
        policy_path.write_text(yaml.dump(policy_data))

        import os

        os.environ["IW_POLICY_PATH"] = str(policy_path)
        try:
            from inferwall.core.pipeline import Pipeline

            pipeline = Pipeline()
            assert pipeline.policy.is_monitor_mode is True
            assert pipeline.policy.inbound_block_threshold == 10
        finally:
            os.environ.pop("IW_POLICY_PATH", None)

    def test_default_policy_when_no_env(self) -> None:
        """Default shipped policy loads when no env var set."""
        import os

        os.environ.pop("IW_POLICY_PATH", None)
        os.environ.pop("IW_SIGNATURES_DIR", None)

        from inferwall.core.pipeline import Pipeline

        pipeline = Pipeline()
        assert pipeline.policy.is_monitor_mode is False
        assert pipeline.policy.inbound_block_threshold == 15
