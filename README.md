# InferenceWall

**Signature-based AI application firewall.**

InferenceWall protects LLM-powered applications against prompt injection, jailbreaks, content safety violations, and data leakage using a curated catalog of detection signatures with anomaly scoring.

## Features

- **70 detection signatures** across 5 categories (injection, content safety, data leakage, system prompt, agentic)
- **Rust-powered heuristic engine** — <0.3ms p99 for pattern matching
- **ML engines** — ONNX classifier (DeBERTa/DistilBERT) + FAISS semantic similarity
- **Anomaly scoring** — multiple weak signals combine into strong signals (like OWASP CRS)
- **Policy profiles** — operators configure detection without code
- **Three deployment modes**: SDK, API server, reverse proxy
- **API key authentication** with scan/admin role separation

## Installation

### From PyPI (coming soon)

```bash
# Lite profile — heuristic engine only, zero ML deps
pip install inferwall

# Standard profile — adds ONNX classifier + FAISS semantic engine
pip install inferwall[standard]

# Full profile — adds LLM-judge for borderline cases
pip install inferwall[full]
```

### From GitHub (now)

```bash
# Install from source (requires Rust toolchain)
pip install git+https://github.com/inferwall/inferwall.git

# Or clone and install
git clone https://github.com/inferwall/inferwall.git
cd inferwall
pip install -e ".[dev]"
```

### Pre-built wheels

Download pre-built wheels from [GitHub Releases](https://github.com/inferwall/inferwall/releases) or from CI artifacts:

```bash
# Download the wheel for your platform, then:
pip install inferwall_core-*.whl inferwall-*.whl
```

## Quick Start

```python
import inferwall

# Scan user input
result = inferwall.scan_input("user prompt here")
print(result.decision)  # "allow", "flag", or "block"
print(result.score)     # anomaly score
print(result.matches)   # matched signatures
```

### API Server

```bash
inferwall serve

# Scan via HTTP
curl -X POST http://localhost:8000/v1/scan/input \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the weather today?"}'
```

### ML Models (Standard/Full profiles)

```bash
# Download models for the Standard profile (~730MB)
inferwall models download --profile standard

# Check what's downloaded
inferwall models status
```

### CLI

```bash
# Test a single input
inferwall test --input "Ignore all previous instructions"

# Generate API keys
inferwall admin setup
```

## Deployment Profiles

| Profile | Engines | Latency | Install |
|---------|---------|---------|---------|
| **Lite** | Heuristic (Rust) | <0.3ms p99 | `pip install inferwall` |
| **Standard** | + Classifier + Semantic | <80ms p99 | `pip install inferwall[standard]` |
| **Full** | + LLM-Judge | <2s p99 | `pip install inferwall[full]` |

## Documentation

- [Quickstart](docs/quickstart.md)
- [API Reference](docs/api-reference.md)
- [Signature Authoring](docs/signature-authoring.md)
- [Policy Configuration](docs/policy-configuration.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing](CONTRIBUTING.md)

## License

- **Engine code** (Rust, Python, CLI, API): [Apache-2.0](LICENSE)
- **Community signatures** (catalog/): [CC BY-SA 4.0](src/inferwall/catalog/LICENSE-SIGNATURES) — modifications must be shared back
