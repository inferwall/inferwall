# InferenceWall

**Signature-based AI application firewall.**

InferenceWall protects LLM-powered applications against prompt injection, jailbreaks, content safety violations, and data leakage using a curated catalog of detection signatures with anomaly scoring.

## Features

- **40+ detection signatures** across 5 categories (injection, content safety, data leakage, system prompt, agentic)
- **Rust-powered heuristic engine** — <0.3ms p99 for pattern matching
- **Anomaly scoring** — multiple weak signals combine into strong signals (like OWASP CRS)
- **Policy profiles** — operators configure detection without code
- **Three deployment modes**: SDK, API server, reverse proxy
- **API key authentication** with scan/admin role separation

## Quick Start

```bash
pip install inferwall

# SDK usage
python -c "import inferwall; print(inferwall.scan_input('hello').decision)"

# API server
inferwall serve
```

## Documentation

- [Quickstart](docs/quickstart.md)
- [Signature Authoring](docs/signature-authoring.md)

## License

- **Engine code** (Rust, Python, CLI, API): [Apache-2.0](LICENSE)
- **Community signatures** (catalog/): [CC BY-SA 4.0](src/inferwall/catalog/LICENSE-SIGNATURES) — modifications must be shared back
