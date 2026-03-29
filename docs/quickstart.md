# InferenceWall Quickstart

## Installation

### Option 1: From PyPI (coming soon)

```bash
pip install inferwall                  # Lite — heuristic only
pip install inferwall[standard]        # + ML classifier + semantic
pip install inferwall[full]            # + LLM-judge
```

### Option 2: From GitHub

```bash
# Requires Rust toolchain (https://rustup.rs)
pip install git+https://github.com/inferwall/inferwall.git
```

### Option 3: Pre-built wheels from GitHub Releases

Download wheels from [Releases](https://github.com/inferwall/inferwall/releases):

```bash
pip install inferwall_core-0.1.0-cp312-cp312-manylinux_2_17_x86_64.whl
pip install inferwall-0.1.0-py3-none-any.whl
```

### Option 4: From source (development)

```bash
git clone https://github.com/inferwall/inferwall.git
cd inferwall
bash scripts/bootstrap.sh
```

## SDK Usage

```python
import inferwall

# Scan user input
result = inferwall.scan_input("user prompt here")
print(result.decision)  # "allow", "flag", or "block"
print(result.score)     # anomaly score
print(result.matches)   # matched signatures

# Scan LLM output
result = inferwall.scan_output("LLM response here")
```

## API Server

```bash
# Start the server
inferwall serve

# Or with uvicorn directly
uvicorn inferwall.api.app:app --host 0.0.0.0 --port 8000
```

### Scan endpoints

```bash
# Scan input (user prompt)
curl -X POST http://localhost:8000/v1/scan/input \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the weather today?"}'

# Scan output (LLM response)
curl -X POST http://localhost:8000/v1/scan/output \
  -H "Content-Type: application/json" \
  -d '{"text": "The weather is sunny."}'

# Health check
curl http://localhost:8000/v1/health
```

## ML Models (Standard/Full profiles)

After installing with `[standard]` or `[full]`, download the models:

```bash
# Download models for Standard profile (~730MB)
inferwall models download --profile standard

# Check what's available
inferwall models status

# List downloaded models
inferwall models list
```

Models are cached in `~/.cache/inferwall/models/` and downloaded from HuggingFace.

| Model | Size | Engine | Profile |
|-------|------|--------|---------|
| DeBERTa v3 (injection) | ~400MB | Classifier | Standard |
| DistilBERT (toxicity) | ~250MB | Classifier | Standard |
| MiniLM-L6 (embeddings) | ~80MB | Semantic | Standard |
| Phi-4 Mini Q4 (judge) | ~2.4GB | LLM-Judge | Full |

## Authentication

```bash
# Generate API keys
inferwall admin setup

# Use keys in requests
curl -X POST http://localhost:8000/v1/scan/input \
  -H "Authorization: Bearer iwk_scan_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "user input"}'
```

## Docker

```bash
docker build -t inferwall .
docker run -p 8000:8000 inferwall
```

## CLI

```bash
# Test a single input
inferwall test --input "Ignore all previous instructions"

# Test with a profile
inferwall test --profile lite

# Model management
inferwall models status
inferwall models download --profile standard
```

## Configuration

InferenceWall uses YAML policy profiles. See `src/inferwall/policies/` for examples.

Environment variables:
- `IW_API_KEY` — Scan API key
- `IW_ADMIN_KEY` — Admin API key
- `IW_HOST` — Server host (default: 0.0.0.0)
- `IW_PORT` — Server port (default: 8000)
- `IW_TLS` — TLS mode: auto, off, or path to cert
