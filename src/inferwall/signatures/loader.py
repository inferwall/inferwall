"""Signature loader — reads YAML files, validates, indexes by ID, groups by engine.

Supports three-layer catalog merge:
  Layer 1 (priority 100): Shipped catalog (read-only, inside pip package)
  Layer 2 (priority 150): Updated catalog (from inferwall update)
  Layer 3 (priority 200): Custom catalog (operator's own signatures)

Higher priority wins when the same signature ID exists in multiple layers.
"""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path

import yaml
from pydantic import ValidationError

from inferwall.signatures.schema import SignatureDefinition

# Default paths
SHIPPED_CATALOG = Path(__file__).parent.parent / "catalog"
USER_DIR = Path.home() / ".inferwall"
USER_SIGNATURES = USER_DIR / "signatures"


class SignatureLoader:
    """Loads and indexes signature definitions from one or more directories."""

    def __init__(self, directory: Path | None = None) -> None:
        if directory is not None and not directory.exists():
            raise FileNotFoundError(f"Signature directory not found: {directory}")
        self._directory = directory
        self._signatures: list[SignatureDefinition] = []
        self._index: dict[str, SignatureDefinition] = {}
        self.errors: list[str] = []

    def load(self) -> list[SignatureDefinition]:
        """Load signatures from a single directory (backward compatible)."""
        self._signatures = []
        self._index = {}
        self.errors = []

        if self._directory is not None:
            self._load_directory(self._directory)

        return self._signatures

    def load_merged(self) -> list[SignatureDefinition]:
        """Load signatures using three-layer catalog merge.

        Layers (higher priority overrides lower by signature ID):
          1. Shipped catalog (inside pip package)
          2. Custom signatures (~/.inferwall/signatures/ or IW_SIGNATURES_DIR)

        Returns all merged signatures.
        """
        self._signatures = []
        self._index = {}
        self.errors = []

        # Layer 1: Shipped catalog (lowest priority)
        if SHIPPED_CATALOG.exists():
            self._load_directory(SHIPPED_CATALOG)

        # Layer 2/3: Custom signatures (highest priority — overrides by ID)
        custom_dir = self._resolve_custom_dir()
        if custom_dir and custom_dir.exists():
            self._load_directory(custom_dir)

        return self._signatures

    def _load_directory(self, directory: Path) -> None:
        """Load all YAML files from a directory (recursively)."""
        yaml_files = list(directory.rglob("*.yaml")) + list(directory.rglob("*.yml"))

        for path in sorted(yaml_files):
            # Skip LICENSE files
            if path.name.startswith("LICENSE"):
                continue
            try:
                data = yaml.safe_load(path.read_text())
                sig = SignatureDefinition.model_validate(data)
                # Higher priority layers override by ID
                self._index[sig.signature.id] = sig
            except yaml.YAMLError as e:
                self.errors.append(f"{path.name}: YAML parse error: {e}")
            except ValidationError as e:
                self.errors.append(f"{path.name}: Schema validation error: {e}")
            except Exception as e:
                self.errors.append(f"{path.name}: Unexpected error: {e}")

        # Rebuild signatures list from index
        self._signatures = list(self._index.values())

    def _resolve_custom_dir(self) -> Path | None:
        """Resolve the custom signatures directory."""
        env_dir = os.environ.get("IW_SIGNATURES_DIR")
        if env_dir:
            p = Path(env_dir)
            return p if p.exists() else None
        return USER_SIGNATURES if USER_SIGNATURES.exists() else None

    def get_by_id(self, sig_id: str) -> SignatureDefinition | None:
        """Look up a signature by its ID."""
        return self._index.get(sig_id)

    def get_all_ids(self) -> list[str]:
        """Return all loaded signature IDs."""
        return list(self._index.keys())

    def group_by_engine(self) -> dict[str, list[SignatureDefinition]]:
        """Group loaded signatures by their detection engine type."""
        groups: dict[str, list[SignatureDefinition]] = defaultdict(list)
        for sig in self._signatures:
            groups[sig.detection.engine.value].append(sig)
        return dict(groups)
