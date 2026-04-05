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

### From PyPI

```bash
# Lite profile — heuristic engine only, zero ML deps
pip install inferwall

# Standard profile — adds ONNX classifier + FAISS semantic engine
pip install inferwall[standard]

# Full profile — adds LLM-judge
pip install inferwall[full]
```

Pre-built wheels are available for Linux x86_64, Linux aarch64, macOS arm64, and Windows x86_64.
Requires Python >= 3.10.

### From Source (development)

```bash
git clone https://github.com/inferwall/inferwall.git
cd inferwall && pip install -e ".[dev]"
```

### Post-install Setup

```bash
inferwall admin setup
source .env.local && inferwall serve

# For Standard/Full profiles, install deps + download ML models:
inferwall models install --profile standard
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
