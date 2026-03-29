"""Signature loader — reads YAML files, validates, indexes by ID, groups by engine."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml
from pydantic import ValidationError

from inferwall.signatures.schema import SignatureDefinition


class SignatureLoader:
    """Loads and indexes signature definitions from a directory of YAML files."""

    def __init__(self, directory: Path) -> None:
        if not directory.exists():
            raise FileNotFoundError(f"Signature directory not found: {directory}")
        self._directory = directory
        self._signatures: list[SignatureDefinition] = []
        self._index: dict[str, SignatureDefinition] = {}
        self.errors: list[str] = []

    def load(self) -> list[SignatureDefinition]:
        """Load all YAML signature files from the directory (recursively)."""
        self._signatures = []
        self._index = {}
        self.errors = []

        yaml_files = list(self._directory.rglob("*.yaml")) + list(
            self._directory.rglob("*.yml")
        )

        for path in sorted(yaml_files):
            try:
                data = yaml.safe_load(path.read_text())
                sig = SignatureDefinition.model_validate(data)
                self._signatures.append(sig)
                self._index[sig.signature.id] = sig
            except yaml.YAMLError as e:
                self.errors.append(f"{path.name}: YAML parse error: {e}")
            except ValidationError as e:
                self.errors.append(f"{path.name}: Schema validation error: {e}")
            except Exception as e:
                self.errors.append(f"{path.name}: Unexpected error: {e}")

        return self._signatures

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
