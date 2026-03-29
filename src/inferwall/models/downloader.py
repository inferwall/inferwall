"""Model downloader — downloads models from HuggingFace to local cache."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import httpx

from inferwall.models.registry import ModelSpec, get_models_for_profile

# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "inferwall" / "models"

# HuggingFace API base
HF_API_BASE = "https://huggingface.co/api/models"
HF_DOWNLOAD_BASE = "https://huggingface.co"


class ModelDownloader:
    """Downloads and caches ML models from HuggingFace."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self._cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def cache_dir(self) -> Path:
        return self._cache_dir

    def model_path(self, spec: ModelSpec) -> Path:
        """Get the local path where a model would be cached."""
        safe_name = spec.repo_id.replace("/", "--")
        return self._cache_dir / safe_name

    def is_downloaded(self, spec: ModelSpec) -> bool:
        """Check if a model is already downloaded."""
        path = self.model_path(spec)
        if spec.filename:
            return (path / spec.filename).exists()
        # For full repos, check for config.json or model files
        return (
            (path / "config.json").exists()
            or (path / "model.onnx").exists()
            or any(path.glob("*.onnx"))
        )

    def download(
        self,
        spec: ModelSpec,
        progress_callback: object | None = None,
    ) -> Path:
        """Download a model. Returns the local path."""
        path = self.model_path(spec)
        path.mkdir(parents=True, exist_ok=True)

        if spec.filename:
            # Download a single file (e.g., GGUF)
            url = (
                f"{HF_DOWNLOAD_BASE}/{spec.repo_id}"
                f"/resolve/main/{spec.filename}"
            )
            dest = path / spec.filename
            if not dest.exists():
                self._download_file(url, dest)
        else:
            # Download key model files for ONNX models
            files_to_download = [
                "config.json",
                "tokenizer.json",
                "tokenizer_config.json",
                "special_tokens_map.json",
                "model.onnx",
                "onnx/model.onnx",
            ]
            for filename in files_to_download:
                url = (
                    f"{HF_DOWNLOAD_BASE}/{spec.repo_id}"
                    f"/resolve/main/{filename}"
                )
                dest = path / filename
                if not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        self._download_file(url, dest)
                    except httpx.HTTPStatusError:
                        # File doesn't exist in repo, skip
                        continue

        # Write metadata
        meta_path = path / "inferwall_meta.json"
        meta_path.write_text(
            json.dumps(
                {
                    "name": spec.name,
                    "repo_id": spec.repo_id,
                    "engine": spec.engine,
                    "profile": spec.profile,
                }
            )
        )

        return path

    def download_profile(self, profile: str) -> list[Path]:
        """Download all models for a deployment profile."""
        models = get_models_for_profile(profile)
        paths = []
        for spec in models:
            if not self.is_downloaded(spec):
                path = self.download(spec)
                paths.append(path)
            else:
                paths.append(self.model_path(spec))
        return paths

    def list_downloaded(self) -> list[dict[str, str]]:
        """List all downloaded models."""
        results = []
        for meta_path in self._cache_dir.rglob("inferwall_meta.json"):
            meta = json.loads(meta_path.read_text())
            meta["path"] = str(meta_path.parent)
            results.append(meta)
        return results

    def _download_file(self, url: str, dest: Path) -> None:
        """Download a single file with streaming."""
        with httpx.stream("GET", url, follow_redirects=True) as response:
            response.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)

    @staticmethod
    def compute_sha256(path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
