# Contributing to InferenceWall

Thank you for your interest in contributing to InferenceWall!

## Ways to Contribute

### Signature Contributions (CC BY-SA 4.0)

The most impactful way to contribute is by adding or improving detection signatures. Community signatures are licensed under CC BY-SA 4.0 — any modifications must be shared back under the same license.

**To contribute a signature:**

1. Fork this repo
2. Create a YAML file in `src/inferwall/catalog/<category>/`
3. Follow the format in [Signature Authoring Guide](docs/signature-authoring.md)
4. Include the license header: `# License: CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/`
5. Add at least 3 true positive and 3 true negative test cases
6. Open a PR with a description of what the signature detects

**Signature ID format:** `{CATEGORY}-{SUBCATEGORY}-{NUMBER}`
- Injection: `INJ-D-xxx`, `INJ-I-xxx`, `INJ-O-xxx`
- Content Safety: `CS-T-xxx`, `CS-B-xxx`
- Data Leakage: `DL-P-xxx`, `DL-S-xxx`
- System Prompt: `SP-xxx`
- Agentic: `AG-xxx`

### Code Contributions (Apache-2.0)

Engine code, API, CLI, and infrastructure improvements are welcome under Apache-2.0.

1. Fork and create a feature branch
2. Write tests first (TDD is mandatory)
3. Run `just lint` and `just test-all` before submitting
4. Open a PR with a clear description

### Bug Reports

Open an issue with:
- Steps to reproduce
- Expected vs actual behavior
- InferenceWall version and environment

## Development Setup

```bash
git clone https://github.com/inferwall/inferwall.git
cd inferwall
bash scripts/bootstrap.sh
```

## Code Quality

- Python: `ruff check`, `ruff format`, `mypy --strict`
- Rust: `cargo clippy -- -D warnings`, `cargo fmt`
- Tests: `just test-all`

All PRs must pass CI (lint + test) before merge.
