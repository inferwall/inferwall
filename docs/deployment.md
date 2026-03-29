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

### PyPI

```bash
pip install inferwall
inferwall admin setup
source .env.local && inferwall serve
```

## Deployment Profiles

| Profile | Engines | Latency | Dependencies |
|---------|---------|---------|-------------|
| **Lite** | Heuristic (Rust) | <0.3ms p99 | None |
| **Standard** | + Classifier + Semantic | <80ms p99 | ONNX, FAISS |
| **Full** | + LLM-Judge | <2s p99 | + llama-cpp |

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
