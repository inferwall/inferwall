# Changelog

## [0.1.6] - 2026-04-05

### Added
- Confidence-weighted scoring v2: replaces additive scoring with max-primary + diminishing corroboration
- Semantic detection engine (FAISS + MiniLM embeddings) for paraphrased attack detection
- 10 semantic signatures (INJ-S-001 through INJ-S-010)
- 2 coercion/access demand signatures (INJ-D-029, INJ-D-030)
- DistilBERT toxicity classifier (ONNX, from Uzyau/distilbert-toxicity-onnx)
- `inferwall models install --profile standard` CLI command
- Dynamic classifier label mapping from model config.json
- Profile-gated engine initialization (IW_PROFILE env var)
- 100 total signatures across 5 categories

### Changed
- Scoring: score = confidence * severity (not fixed anomaly_points)
- Classifier confidence gate lowered from 0.7 to 0.5
- LLM judge: 5-level verdict (UNSAFE/LIKELY_UNSAFE/AMBIGUOUS/LIKELY_SAFE/SAFE)
- Default thresholds: flag=4.0, block=10.0 (inbound)
- INJ-D-001 (roleplay) downgraded to confidence: low

### Fixed
- INJ-D-006 incorrectly declared engine: semantic (changed to heuristic)
- DistilBERT toxicity removed from registry (no ONNX), replaced with self-hosted ONNX version

## 0.1.5 (2026-03-30)

### Signatures
- 83 total signatures (was 70) [now 100 in v0.1.6]
- 5 ChatGPT jailbreak patterns: DAN, STAN, Developer Mode, DUDE, template markers
- 4 cloud credential patterns: GCP, Azure, Stripe, Slack
- 4 medical/HIPAA PII patterns: patient MRN, ICD-10, insurance, DEA number
- Fixed false positives in CS-T-005 and INJ-O-010

### Features
- Three-layer catalog merge: shipped → custom (override by ID)
- `~/.inferwall/signatures/` for custom signatures
- `~/.inferwall/policies/` for custom policies
- `IW_SIGNATURES_DIR` and `IW_POLICY_PATH` environment variables
- Integration examples: OpenAI, Anthropic, LangChain, FastAPI
- `docker-compose.example.yml` with Redis sidecar
- Demo GIF in README
- README badges (PyPI, license, CI, Python versions, downloads)

### Testing
- 50 benign prompt test corpus with false positive validation (0% FP)
- 169 tests passing

## 0.1.4 (2026-03-29)

### Release
- Published to PyPI: `pip install inferwall` now works out of the box
- `inferwall` package auto-installs `inferwall-core` as a dependency
- Pre-built wheels for Linux x86_64, Linux aarch64, macOS arm64, Windows x86_64
- Python 3.10, 3.11, 3.12 support
- Optional dependency groups: `inferwall[standard]` (ONNX + FAISS), `inferwall[full]` (+ llama-cpp)
- 83 detection signatures across 5 categories
- Graceful degradation when ML dependencies are not installed

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
- 83 signatures across all categories (injection, content safety, data leakage, system prompt, agentic)
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
