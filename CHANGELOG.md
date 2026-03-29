# Changelog

## 0.1.0-dev (2026-03-29)

### M0: Foundation
- Repo skeleton with pyproject.toml, Cargo.toml, rust-toolchain.toml, justfile
- Rust crate: PyO3 module with types.rs (Match, Decision, ScoringPolicy, ScoreResult)
- Signature schema: full Pydantic models for YAML spec
- Signature loader: read YAML, validate, index by ID, group by engine
- Policy engine: load profiles, resolve overrides, enforcement modes
- Engine abstraction: BaseEngine with scan() interface
- CI pipeline: .github/workflows/ci.yml
- 5 initial heuristic signatures

### M1: Heuristic + API + Security
- Rust heuristic engine: regex (ReDoS-immune), Aho-Corasick, encoding, Unicode, entropy
- Text preprocessor: normalize, decode, homoglyph map
- Scoring pipeline: accumulate, threshold eval, early exit, decision
- scan_heuristic_with_preprocess() — single Rust call
- 15 heuristic signatures
- FastAPI: /v1/scan/input, /v1/scan/output, /v1/health endpoints
- API key auth with scan/admin role separation
- SDK: import inferwall; inferwall.scan_input("text")
- CLI: inferwall test --input, inferwall admin setup, inferwall serve
- Rate limiter, audit logger

### M2: ML Engines + Signatures
- 70 signatures across all categories (injection, content safety, data leakage, system prompt, agentic)
- ML classifier engine: ONNX runtime (DeBERTa/DistilBERT models)
- ML semantic engine: FAISS similarity search against reference embeddings
- Model download manager: `inferwall models download`, `inferwall models list`, `inferwall models status`
- Composite engine combining heuristic + ML signals
- Signature catalog API: GET /v1/signatures, /v1/signatures/{id}
- Dual licensing: Apache-2.0 for code, CC BY-SA 4.0 for community signatures

### M3: Advanced Engines + Operations
- Rust session store: TTL, memory bounds, FIFO eviction
- Session API: POST/GET/DELETE /v1/sessions
- Admin reload: POST /v1/admin/reload
- Policy API: GET /v1/policies
- Auth API: login, logout, check (httpOnly cookies)
- Config API: GET /v1/config
- LLM-judge engine (Full profile)

### M4: UI + Release
- inferwall-ui: 10-page Next.js management console
- Dockerfile: multi-stage, non-root, health check
- Helm chart: K8s deployment with health probes
- Documentation: quickstart, signature authoring, policy config, deployment, API reference
- README, LICENSE (Apache-2.0), CHANGELOG
