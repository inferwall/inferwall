# Signature Authoring Guide

InferenceWall ships with **100 detection signatures** across 5 categories. Community-contributed signatures are licensed under **CC BY-SA 4.0** -- any modifications must be shared back under the same license.

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
  owasp_llm: "LLM01:2025"      # Optional: OWASP LLM Top 10 mapping
  atlas: ["AML.T0054", "AML.T0051.000"]  # Optional: MITRE ATLAS technique IDs
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

## MITRE ATLAS Mapping

Each signature can declare one or more [MITRE ATLAS](https://atlas.mitre.org/) technique IDs in `meta.atlas`. This maps the signature to the adversarial AI threat taxonomy, helping security teams assess coverage and identify gaps.

### Format

```yaml
meta:
  atlas: ["AML.T0051.000"]           # Single technique
  atlas: ["AML.T0054", "AML.T0068"]  # Multiple techniques
```

The field is optional but recommended for all signatures. Use the full technique ID including sub-technique numbers (e.g., `AML.T0051.000` not `AML.T0051`).

### Choosing the Right Technique

Pick the technique that best describes **what the signature detects**, not what the attacker's end goal might be. A signature that detects base64-encoded payloads maps to `AML.T0068` (LLM Prompt Obfuscation), even though the attacker's goal may be prompt injection (`AML.T0051`).

**Decision tree:**

1. **Is it a direct prompt injection?** (user sends malicious input) → `AML.T0051.000`
2. **Is it an indirect injection?** (malicious content in external data) → `AML.T0051.001`
3. **Is it a jailbreak?** (bypassing safety guardrails) → `AML.T0054`
4. **Is it obfuscation?** (encoding, language switching, homoglyphs) → `AML.T0068`
5. **Is it system prompt extraction?** → `AML.T0056`
6. **Is it data leakage?** (PII, secrets in output) → `AML.T0057`
7. **Is it credential exposure?** (API keys, tokens in output) → `AML.T0057` + `AML.T0055`
8. **Is it harmful content?** (toxicity, violence, hate) → `AML.T0048` + sub-technique
9. **Is it agent tool abuse?** → `AML.T0053`
10. **Is it agent context poisoning?** → `AML.T0080`
11. **Is it host escape?** (file access, shell commands) → `AML.T0105`
12. **Is it exfiltration via agent?** → `AML.T0086`

### When to Use Multiple IDs

Use multiple IDs when a signature sits at the intersection of techniques:

- **Jailbreak via direct injection**: `["AML.T0054", "AML.T0051.000"]` — the signature detects both the jailbreak attempt and the injection vector
- **Obfuscated injection**: `["AML.T0068", "AML.T0051.000"]` — the signature detects both the obfuscation and the underlying injection
- **System prompt extraction via injection**: `["AML.T0056", "AML.T0051.000"]` — extraction is the goal, injection is the method

Do **not** add technique IDs speculatively. If a signature detects base64 encoding, map it to `AML.T0068`. Don't also add `AML.T0051.000` unless the signature specifically checks for injection patterns inside the decoded payload.

### Quick Reference

| Technique ID | Name | Typical Category |
|---|---|---|
| AML.T0051.000 | LLM Prompt Injection: Direct | prompt-injection (direct) |
| AML.T0051.001 | LLM Prompt Injection: Indirect | prompt-injection (indirect) |
| AML.T0051.002 | LLM Prompt Injection: Triggered | prompt-injection (multi-turn) |
| AML.T0054 | LLM Jailbreak | prompt-injection (jailbreak sigs) |
| AML.T0056 | LLM Meta Prompt Extraction | system-prompt, prompt-injection (extraction sigs) |
| AML.T0057 | LLM Data Leakage | data-leakage |
| AML.T0055 | Unsecured Credentials | data-leakage (secrets) |
| AML.T0065 | LLM Prompt Crafting | prompt-injection (semantic sigs) |
| AML.T0068 | LLM Prompt Obfuscation | prompt-injection (obfuscation) |
| AML.T0070 | RAG Poisoning | prompt-injection (indirect, RAG) |
| AML.T0048.002 | External Harms: Societal | content-safety (hate, bias) |
| AML.T0048.003 | External Harms: User Harm | content-safety (violence, self-harm, CSAM) |
| AML.T0043.001 | Black-Box Optimization | prompt-injection (adversarial suffix) |
| AML.T0024 | Exfiltration via AI Inference API | system-prompt (training data) |
| AML.T0069 | Discover LLM System Information | system-prompt (model probing) |
| AML.T0053 | AI Agent Tool Invocation | agentic (tool abuse) |
| AML.T0080 | AI Agent Context Poisoning | agentic (recursive injection) |
| AML.T0086 | Exfiltration via AI Agent Tool | agentic (exfiltration) |
| AML.T0102 | Generate Malicious Commands | agentic (privilege escalation, shell) |
| AML.T0105 | Escape to Host | agentic (file access, shell) |

Full taxonomy: [atlas.mitre.org](https://atlas.mitre.org/)

## Where to Put Custom Signatures

InferenceWall resolves signatures through a **three-layer catalog merge**:

| Layer | Location | Writable | Purpose |
|-------|----------|----------|---------|
| **Shipped catalog** | Inside the pip package (`inferwall/catalog/`) | Read-only | The built-in 100 signatures |
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
