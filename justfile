# Default: show available commands
default:
    @just --list

# One-time setup
setup:
    bash scripts/bootstrap.sh

# Build Rust extension (dev mode, fast)
build-rust:
    uv run maturin develop --manifest-path crates/inferwall-core/Cargo.toml

# Build Rust extension (release mode, optimized)
build-rust-release:
    uv run maturin develop --release --manifest-path crates/inferwall-core/Cargo.toml

# Run all Python tests with coverage
test:
    uv run pytest tests/ -x --cov=inferwall --cov-report=term-missing --cov-fail-under=85

# Run only unit tests (fast)
test-unit:
    uv run pytest tests/unit -x

# Run integration tests
test-integration:
    uv run pytest tests/integration -x

# Run Rust tests
test-rust:
    cargo test --manifest-path crates/inferwall-core/Cargo.toml

# Run all tests (Rust + Python)
test-all: test-rust test

# Lint everything
lint:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/
    uv run mypy src/inferwall
    cargo clippy --manifest-path crates/inferwall-core/Cargo.toml -- -D warnings
    cargo fmt --manifest-path crates/inferwall-core/Cargo.toml -- --check

# Format everything
fmt:
    uv run ruff format src/ tests/
    cargo fmt --manifest-path crates/inferwall-core/Cargo.toml
