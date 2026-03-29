# Deployment Guide

## Quick Deploy

### Docker

```bash
docker build -t inferwall .
docker run -p 8000:8000 \
  -e IW_API_KEY=iwk_scan_yourkey \
  -e IW_ADMIN_KEY=iwk_admin_yourkey \
  inferwall
```

### Kubernetes (Helm)

```bash
helm install inferwall ./helm/inferwall \
  --set env.IW_API_KEY=iwk_scan_yourkey \
  --set env.IW_ADMIN_KEY=iwk_admin_yourkey
```

### From GitHub (now)

```bash
# Lite profile — heuristic engine only (requires Rust toolchain)
pip install git+https://github.com/inferwall/inferwall.git

# Standard profile — adds ONNX classifier + FAISS semantic engine
pip install "inferwall[standard] @ git+https://github.com/inferwall/inferwall.git"

# Full profile — adds LLM-judge
pip install "inferwall[full] @ git+https://github.com/inferwall/inferwall.git"

# Or clone and install
git clone https://github.com/inferwall/inferwall.git
cd inferwall && pip install -e ".[dev]"
```

### Pre-built Wheels

Download pre-built wheels from [GitHub Releases](https://github.com/inferwall/inferwall/releases):

```bash
pip install inferwall_core-*.whl inferwall-*.whl
```

### PyPI (coming soon)

```bash
# Lite profile — heuristic engine only, zero ML deps
pip install inferwall

# Standard profile
pip install inferwall[standard]

# Full profile
pip install inferwall[full]
```

### Post-install Setup

```bash
inferwall admin setup
source .env.local && inferwall serve

# For Standard/Full profiles, download ML models:
inferwall models download --profile standard
inferwall models status
```

## Deployment Profiles

| Profile | Install | Engines | Latency | Dependencies |
|---------|---------|---------|---------|-------------|
| **Lite** | `pip install inferwall` | Heuristic (Rust) | <0.3ms p99 | None |
| **Standard** | `pip install inferwall[standard]` | + Classifier (ONNX) + Semantic (FAISS) | <80ms p99 | onnxruntime, faiss-cpu |
| **Full** | `pip install inferwall[full]` | + LLM-Judge | <2s p99 | + llama-cpp-python |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `IW_API_KEY` | Scan API key | None (dev mode) |
| `IW_ADMIN_KEY` | Admin API key | None (dev mode) |
| `IW_HOST` | Server host | `0.0.0.0` |
| `IW_PORT` | Server port | `8000` |
| `IW_TLS` | TLS mode: auto, off, acme | `off` |
| `IW_PROFILE` | Deployment profile | `lite` |
| `IW_LOG_LEVEL` | Log level | `info` |
| `IW_REDIS_URL` | Redis URL for distributed sessions | None |

## Health Checks

```bash
# Liveness (is process alive?)
curl http://localhost:8000/v1/health/live

# Readiness (can process handle requests?)
curl http://localhost:8000/v1/health/ready

# Full health with signature count
curl http://localhost:8000/v1/health
```
