# Third-Party Notices

InferenceWall uses the following third-party ML models and libraries.
Models are not shipped with InferenceWall — they are downloaded on demand
by the user via `inferwall models download`.

## ML Models

### DeBERTa v3 — Prompt Injection Detection
- **Model**: protectai/deberta-v3-base-prompt-injection-v2
- **Author**: Protect AI
- **License**: Apache-2.0
- **URL**: https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2
- **Used by**: Classifier engine (Standard profile)

### DistilBERT — Multilingual Toxicity Classification
- **Model**: citizenlab/distilbert-base-multilingual-cased-toxicity
- **Author**: Citizen Lab
- **License**: Apache-2.0
- **URL**: https://huggingface.co/citizenlab/distilbert-base-multilingual-cased-toxicity
- **Used by**: Classifier engine (Standard profile)

### MiniLM-L6 — Sentence Embeddings
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Author**: Sentence-Transformers (UKP Lab, TU Darmstadt)
- **License**: Apache-2.0
- **URL**: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **Used by**: Semantic engine (Standard profile)

### Phi-4 Mini — LLM Judge
- **Model**: microsoft/Phi-4-mini-instruct
- **Author**: Microsoft
- **License**: MIT
- **URL**: https://huggingface.co/microsoft/Phi-4-mini-instruct
- **Used by**: LLM-Judge engine (Full profile)

## Rust Dependencies

InferenceWall's Rust extension (inferwall-core) uses:

| Crate | License | Purpose |
|-------|---------|---------|
| pyo3 | Apache-2.0 OR MIT | Python ↔ Rust bindings |
| regex | Apache-2.0 OR MIT | Pattern matching (ReDoS-immune) |
| aho-corasick | Apache-2.0 OR MIT | Multi-pattern substring search |
| unicode-normalization | Apache-2.0 OR MIT | Unicode NFKC normalization |
| base64 | Apache-2.0 OR MIT | Encoding detection/decode |
| serde | Apache-2.0 OR MIT | Serialization |
| arc-swap | Apache-2.0 OR MIT | Atomic reference swap |

## Python Dependencies

Key Python dependencies (installed via pip):

| Package | License | Purpose |
|---------|---------|---------|
| pydantic | MIT | Data validation and schema |
| fastapi | MIT | HTTP API framework |
| uvicorn | BSD-3-Clause | ASGI server |
| pyyaml | MIT | YAML parsing |
| httpx | BSD-3-Clause | HTTP client |
| onnxruntime | MIT | ML model inference (optional) |
| faiss-cpu | MIT | Similarity search (optional) |
| tokenizers | Apache-2.0 | Text tokenization (optional) |
| llama-cpp-python | MIT | LLM inference (optional) |

## Note on Model Licensing

The models listed above are downloaded directly from HuggingFace by the user.
InferenceWall does not redistribute these models. Users are responsible for
complying with each model's license terms. All models currently referenced
use permissive licenses (Apache-2.0 or MIT).
