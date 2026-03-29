"""Shared test fixtures for InferenceWall tests."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_signatures_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with sample signature YAML files."""
    sig_dir = tmp_path / "signatures"
    sig_dir.mkdir()
    return sig_dir
