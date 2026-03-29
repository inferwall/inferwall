#!/usr/bin/env bash
set -euo pipefail

echo "==> Checking prerequisites..."
command -v rustup >/dev/null || { echo "Install Rust: https://rustup.rs"; exit 1; }
command -v uv >/dev/null || { echo "Install uv: https://docs.astral.sh/uv/"; exit 1; }

echo "==> Setting up Python (via uv)..."
uv python install 3.12

echo "==> Setting Rust toolchain..."
rustup show

echo "==> Installing just (command runner)..."
command -v just >/dev/null || cargo install just

echo "==> Creating Python venv and installing deps..."
uv venv
uv sync --extra dev

echo "==> Building Rust extension (dev mode)..."
uv run maturin develop --manifest-path crates/inferwall-core/Cargo.toml

echo "==> Installing pre-commit hooks..."
uv run pre-commit install

echo "==> Verifying..."
uv run python -c "import inferwall_core; print(f'Rust extension OK: {inferwall_core.__version__}')"
uv run pytest tests/unit -x -q

echo "==> Done. Run 'source .venv/bin/activate' or use 'uv run <cmd>'"
