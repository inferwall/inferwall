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

## GPU Support for ONNX Runtime

For significantly faster inference with the Standard and Full profiles, you can enable GPU support for ONNX Runtime.  By default, Inferwall uses the CPUExecutionProvider, resulting in ~500ms per request.  With GPU acceleration, latency can be reduced to ~20-50ms.

### CUDA Requirements

- A compatible NVIDIA GPU.
- NVIDIA CUDA Toolkit installed.  Refer to the ONNX Runtime documentation for supported CUDA versions: [https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)
- `nvidia-driver` installed and configured.

### Installation

Instead of installing `onnxruntime`, install `onnxruntime-gpu`:

```bash
pip install onnxruntime-gpu
```

### Docker GPU Setup (nvidia-docker)

To use the GPU within a Docker container, you need to use `nvidia-docker`.

1.  Ensure you have the NVIDIA Container Toolkit installed.  Follow the instructions here: [https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2.  Build and run your Docker container using `nvidia-docker`:

```bash
docker build -t inferwall .
docker run --gpus all -p 8000:8000 \
  -e IW_API_KEY=iwk_scan_yourkey \
  -e IW_ADMIN_KEY=iwk_admin_yourkey \
  inferwall
```

The `--gpus all` flag makes all available GPUs accessible to the container.

### Verifying GPU Usage

1.  **Check ONNX Runtime logs:**  When the application starts, ONNX Runtime will log which execution providers are available.  Look for output indicating that the CUDA Execution Provider is being used.

2.  **Monitor GPU utilization:** Use tools like `nvidia-smi` to monitor GPU utilization while the application is processing requests.  You should see increased GPU usage when requests are being handled.

3.  **In-code verification (advanced):**  You can add logging to `src/inferwall/engines/classifier.py` to explicitly check the session options and available providers.  For example, you can log the `providers` list in the `__init__` method of the `Classifier` class.