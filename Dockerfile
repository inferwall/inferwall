# Multi-stage Docker build for InferenceWall
# Stage 1: Build Rust extension
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /build

# Copy Rust sources first (cache layer)
COPY Cargo.toml Cargo.lock rust-toolchain.toml ./
COPY crates/ crates/

# Build Rust extension
RUN pip install maturin && \
    maturin build --release --manifest-path crates/inferwall-core/Cargo.toml

# Copy Python sources
COPY pyproject.toml ./
COPY src/ src/

# Stage 2: Runtime image
FROM python:3.12-slim AS runtime

RUN groupadd -r inferwall && useradd -r -g inferwall inferwall

WORKDIR /app

# Install Python package
COPY --from=builder /build/target/wheels/*.whl /tmp/
COPY --from=builder /build/pyproject.toml /build/src/ ./src/
COPY pyproject.toml ./

RUN pip install --no-cache-dir /tmp/*.whl && \
    pip install --no-cache-dir . && \
    rm -rf /tmp/*.whl

# Copy catalog and policies
COPY src/inferwall/catalog/ /app/src/inferwall/catalog/
COPY src/inferwall/policies/ /app/src/inferwall/policies/

USER inferwall

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8000/v1/health/live'); r.raise_for_status()" || exit 1

ENTRYPOINT ["python", "-m", "uvicorn", "inferwall.api.app:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
