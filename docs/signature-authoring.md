# Signature Authoring Guide

## Signature Format

Each signature is a single YAML file in the catalog directory.

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

## Testing

Every signature must have 3+ true positive and 3+ true negative test cases.
