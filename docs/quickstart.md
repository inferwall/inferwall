# InferenceWall Quickstart

## Installation

### Option 1: From PyPI

```bash
pip install inferwall                  # Lite — heuristic only
pip install inferwall[standard]        # + ML classifier + semantic
pip install inferwall[full]            # + LLM-judge
```

Pre-built wheels are available for Linux x86_64, Linux aarch64, macOS arm64, and Windows x86_64.
Requires Python >= 3.10.

### Option 2: From source (development)

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
- `IW_SIGNATURES_DIR` — Path to custom signatures directory
- `IW_POLICY_PATH` — Path to custom policy file

## Customization

InferenceWall uses a **three-layer catalog merge** system that lets you customize signatures and policies without modifying the shipped package.

### Custom Signatures

Place custom signature YAML files in `~/.inferwall/signatures/`. These are merged with the shipped catalog at startup:

1. **Shipped catalog** (read-only, inside the pip package) — the built-in 83 signatures
2. **Custom signatures** (`~/.inferwall/signatures/`) — your additions and overrides
3. **Override by ID** — a custom signature with the same ID as a shipped one replaces it entirely

To override the environment default, set `IW_SIGNATURES_DIR` to point at any directory:

```bash
export IW_SIGNATURES_DIR=/opt/inferwall/my-signatures
```

#### Example: Creating a Custom Signature

```bash
mkdir -p ~/.inferwall/signatures
cat > ~/.inferwall/signatures/custom-block-internal.yaml << 'EOF'
# Custom signature — block references to internal project names
signature:
  id: INJ-D-100
  name: Internal Project Name Leak
  version: "1.0.0"

meta:
  category: data-leakage
  subcategory: S
  technique: keyword-match
  severity: high
  confidence: high
  performance_cost: low
  tags: [internal, custom]

detection:
  engine: heuristic
  direction: output
  patterns:
    - type: substring
      value: "Project Nightingale"
    - type: substring
      value: "Project Falcon"
  condition: any

scoring:
  anomaly_points: 10

tuning:
  enabled: true
  default_enabled: true
  default_action: enforce
EOF
```

After adding the file, restart the server or SDK — the new signature is picked up automatically.

### Custom Policies

Copy and modify a policy to tune thresholds and per-signature overrides:

```bash
mkdir -p ~/.inferwall/policies
cp $(python -c "import inferwall; print(inferwall.__path__[0])")/policies/default.yaml \
   ~/.inferwall/policies/my-policy.yaml
```

Edit `~/.inferwall/policies/my-policy.yaml` to change thresholds, mode, or per-signature overrides. The pipeline auto-discovers policies from `~/.inferwall/policies/`.

To point at a specific policy file, set `IW_POLICY_PATH`:

```bash
export IW_POLICY_PATH=~/.inferwall/policies/my-policy.yaml
```
