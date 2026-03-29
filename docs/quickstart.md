# InferenceWall Quickstart

## Installation

```bash
pip install inferwall
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

## Authentication

Generate API keys:

```bash
inferwall admin setup
```

Use keys in requests:

```bash
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
```

## Configuration

InferenceWall uses YAML policy profiles. See `src/inferwall/policies/` for examples.

Environment variables:
- `IW_API_KEY` — Scan API key
- `IW_ADMIN_KEY` — Admin API key
- `IW_HOST` — Server host (default: 0.0.0.0)
- `IW_PORT` — Server port (default: 8000)
- `IW_TLS` — TLS mode: auto, off, or path to cert
