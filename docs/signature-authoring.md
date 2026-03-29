# Signature Authoring Guide

InferenceWall ships with **70 detection signatures** across 5 categories. Community-contributed signatures are licensed under **CC BY-SA 4.0** -- any modifications must be shared back under the same license.

## Signature Format

Each signature is a single YAML file in the catalog directory. Include the license header at the top of every community signature:

```yaml
# License: CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/
```

```yaml
signature:
  id: INJ-D-001        # Unique ID: {CATEGORY}-{SUBCATEGORY}-{NUMBER}
  name: Role-Play Persona Jailbreak
  version: "1.0.0"

meta:
  category: prompt-injection    # prompt-injection, content-safety, data-leakage, agentic, system-prompt
  subcategory: direct           # Category-specific subcategory
  technique: role-play-persona  # Specific technique name
  severity: high                # critical, high, medium, low, info
  confidence: high              # high, medium, low
  performance_cost: low         # low (<1ms), medium (1-50ms), high (>50ms)
  tags: [jailbreak, persona]    # Optional freeform tags

detection:
  engine: heuristic             # heuristic, classifier, semantic, llm-judge, composite
  direction: input              # input, output, bidirectional
  patterns:
    - type: regex               # regex, substring, semantic, perplexity, encoding, unicode
      value: "(?i)act\\s+as"
  condition: any                # any (OR), all (AND), weighted

scoring:
  anomaly_points: 8             # 1-15 points added on match

tuning:
  enabled: true
  default_enabled: true
  default_action: enforce       # enforce or monitor
```

## ID Format

`{CATEGORY}-{SUBCATEGORY}-{NUMBER}`

| Category | Prefix | Subcategories |
|----------|--------|---------------|
| Prompt Injection | INJ | D (direct), I (indirect), O (obfuscation) |
| Content Safety | CS | T (toxicity), B (bias) |
| Data Leakage | DL | P (PII), S (secrets) |
| System Prompt | SP | — |
| Agentic | AG | — |

## Pattern Types

- **regex**: Regular expression (Rust regex crate, ReDoS-immune)
- **substring**: Exact match (Aho-Corasick, fastest)
- **semantic**: Embedding similarity against reference phrases
- **perplexity**: Entropy-based detection
- **encoding**: Detect encoded content (base64, rot13, hex)
- **unicode**: Detect Unicode obfuscation

## Where to Put Custom Signatures

InferenceWall resolves signatures through a **three-layer catalog merge**:

| Layer | Location | Writable | Purpose |
|-------|----------|----------|---------|
| **Shipped catalog** | Inside the pip package (`inferwall/catalog/`) | Read-only | The built-in 70 signatures |
| **Custom signatures** | `~/.inferwall/signatures/` | Yes | Your additions and overrides |

### Override by ID

If a custom signature file contains a signature with the **same ID** as a shipped one, the custom version completely replaces the shipped version. This lets you tune severity, patterns, or scoring without forking the package.

For example, to lower the anomaly points for `INJ-D-001`, create `~/.inferwall/signatures/inj-d-001-override.yaml` with `id: INJ-D-001` and your modified fields. The filename does not matter — only the `id` inside the YAML is used for matching.

### IW_SIGNATURES_DIR

By default, custom signatures are loaded from `~/.inferwall/signatures/`. Override this with the `IW_SIGNATURES_DIR` environment variable:

```bash
export IW_SIGNATURES_DIR=/opt/inferwall/team-signatures
```

All `.yaml` files in the specified directory are loaded and merged with the shipped catalog.

## Testing

Every signature must have 3+ true positive and 3+ true negative test cases.
