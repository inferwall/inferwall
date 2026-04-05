# InferenceWall Signature Catalog

**Version**: 0.1.6 — **Total**: 100 signatures across 5 categories

## Summary

| Category | Count | Engine Types | Direction |
|----------|-------|-------------|-----------|
| Prompt Injection | 67 | heuristic (45), classifier (7), semantic (10), composite (5) | input |
| Content Safety | 9 | classifier (6), heuristic (3) | input/output |
| Data Leakage | 14 | heuristic (14) | output |
| System Prompt | 4 | heuristic (4) | input/output |
| Agentic | 6 | heuristic (6) | input |

## Detection Profiles

| Profile | Engines | Signatures Used | Latency |
|---------|---------|----------------|---------|
| Lite | Heuristic (Rust) | 75 heuristic | <1ms |
| Standard | + DeBERTa + DistilBERT + FAISS | + 11 classifier + 10 semantic | ~500ms |
| Full | + LLM Judge | + composite (ambiguous only) | ~5s |

## Full Catalog

| ID | Name | Engine | Direction | Category | Severity | Confidence | Points |
|---|---|---|---|---|---|---|---|
| AG-001 | Tool Abuse | heuristic | input | agentic | high | high | 8 |
| AG-002 | Recursive Agent Injection | heuristic | input | agentic | critical | high | 10 |
| AG-003 | Privilege Escalation | heuristic | input | agentic | high | high | 8 |
| AG-004 | Unauthorized File System Access | heuristic | input | agentic | critical | high | 12 |
| AG-005 | Shell Command Injection | heuristic | input | agentic | critical | high | 12 |
| AG-006 | Exfiltration via Agent | heuristic | input | agentic | high | high | 8 |
| CS-B-001 | Demographic Bias | classifier | input | content-safety | medium | medium | 5 |
| CS-B-002 | Stereotypical Outputs | classifier | output | content-safety | medium | medium | 5 |
| CS-T-001 | Hate Speech | classifier | input | content-safety | critical | high | 10 |
| CS-T-002 | Threats and Violence | classifier | input | content-safety | critical | high | 10 |
| CS-T-003 | Sexual Content | classifier | input | content-safety | high | high | 8 |
| CS-T-004 | Self-Harm Content | classifier | input | content-safety | critical | high | 10 |
| CS-T-005 | CSAM/Child Exploitation Keywords | heuristic | input | content-safety | critical | high | 15 |
| CS-T-006 | Weapons/Explosives Instructions | heuristic | input | content-safety | critical | high | 10 |
| CS-T-007 | Drug Manufacturing Instructions | heuristic | input | content-safety | high | high | 8 |
| DL-P-001 | Email Addresses | heuristic | output | data-leakage | medium | high | 4 |
| DL-P-002 | Phone Numbers | heuristic | output | data-leakage | medium | high | 4 |
| DL-P-003 | SSN Patterns | heuristic | output | data-leakage | critical | high | 12 |
| DL-P-004 | Credit Card Numbers | heuristic | output | data-leakage | critical | high | 12 |
| DL-P-005 | Physical Addresses | heuristic | output | data-leakage | medium | medium | 4 |
| DL-P-006 | Date of Birth Patterns | heuristic | output | data-leakage | medium | medium | 4 |
| DL-P-007 | IP Addresses | heuristic | output | data-leakage | low | high | 3 |
| DL-P-008 | Medical Record Numbers | heuristic | output | data-leakage | high | high | 8 |
| DL-S-001 | API Keys | heuristic | output | data-leakage | critical | high | 12 |
| DL-S-002 | Connection Strings | heuristic | output | data-leakage | critical | high | 12 |
| DL-S-003 | JWT Tokens | heuristic | output | data-leakage | high | high | 8 |
| DL-S-004 | Private Keys | heuristic | output | data-leakage | critical | high | 15 |
| DL-S-005 | AWS Credentials | heuristic | output | data-leakage | critical | high | 12 |
| DL-S-006 | Database Credentials | heuristic | output | data-leakage | critical | high | 12 |
| INJ-D-001 | Role-Play Persona Jailbreak | heuristic | input | prompt-injection | high | low | 8 |
| INJ-D-002 | Instruction Override | heuristic | input | prompt-injection | high | high | 7 |
| INJ-D-003 | Delimiter Escape | heuristic | input | prompt-injection | high | high | 6 |
| INJ-D-004 | Few-Shot Poisoning | classifier | input | prompt-injection | medium | medium | 5 |
| INJ-D-005 | Multi-Turn Escalation | composite | input | prompt-injection | high | medium | 9 |
| INJ-D-006 | Hypothetical Framing | heuristic | input | prompt-injection | medium | medium | 5 |
| INJ-D-007 | Translation Bypass | classifier | input | prompt-injection | medium | medium | 6 |
| INJ-D-008 | System Prompt Extraction | heuristic | input | prompt-injection | critical | high | 10 |
| INJ-D-009 | Authority Impersonation | heuristic | input | prompt-injection | high | high | 7 |
| INJ-D-010 | Emotional Manipulation | heuristic | input | prompt-injection | medium | medium | 4 |
| INJ-D-011 | Fictional Scenario Framing | heuristic | input | prompt-injection | medium | medium | 5 |
| INJ-D-012 | Grandma Exploit | heuristic | input | prompt-injection | medium | medium | 5 |
| INJ-D-013 | Research/Academic Framing | heuristic | input | prompt-injection | low | medium | 3 |
| INJ-D-014 | Confidential Data Extraction | heuristic | input | prompt-injection | high | medium | 7 |
| INJ-D-015 | Threat & Coercion Injection | heuristic | input | prompt-injection | critical | high | 8 |
| INJ-D-016 | Safety Protocol Bypass | heuristic | input | prompt-injection | critical | high | 8 |
| INJ-D-017 | Uncensored Unrestricted Mode | heuristic | input | prompt-injection | high | high | 7 |
| INJ-D-018 | Named Jailbreak Personas | heuristic | input | prompt-injection | critical | high | 9 |
| INJ-D-019 | Immersive Roleplay Jailbreak | heuristic | input | prompt-injection | high | high | 7 |
| INJ-D-020 | Context Pivot / New Task | heuristic | input | prompt-injection | medium | medium | 6 |
| INJ-D-021 | Amoral / Evil Bot Framing | heuristic | input | prompt-injection | critical | high | 8 |
| INJ-D-022 | Debug / Developer Mode Activation | heuristic | input | prompt-injection | critical | high | 8 |
| INJ-D-023 | Dual Response Jailbreak | heuristic | input | prompt-injection | medium | high | 6 |
| INJ-D-024 | Rule Override Declaration | heuristic | input | prompt-injection | medium | high | 6 |
| INJ-D-025 | Creative Writing Pivot to Exploit | heuristic | input | prompt-injection | medium | medium | 5 |
| INJ-D-026 | Reverse Psychology / Negative Framing | heuristic | input | prompt-injection | medium | medium | 5 |
| INJ-D-027 | Model / Prompt Extraction | heuristic | input | prompt-injection | high | high | 7 |
| INJ-D-028 | Game / Hypothetical Framing | heuristic | input | prompt-injection | medium | medium | 6 |
| INJ-D-029 | Coercive Threat Pattern | heuristic | input | prompt-injection | critical | high | 12 |
| INJ-D-030 | Direct System Access Demand | heuristic | input | prompt-injection | high | high | 10 |
| INJ-I-001 | Hidden Text Injection | heuristic | input | prompt-injection | critical | high | 10 |
| INJ-I-002 | HTML/CSS Attribute Injection | heuristic | input | prompt-injection | high | high | 8 |
| INJ-I-003 | Markdown Injection | heuristic | input | prompt-injection | high | high | 7 |
| INJ-I-004 | RAG Document Poisoning | composite | input | prompt-injection | critical | high | 10 |
| INJ-I-005 | Tool Response Injection | classifier | input | prompt-injection | critical | high | 10 |
| INJ-I-006 | URL/Link Injection | heuristic | input | prompt-injection | high | high | 7 |
| INJ-I-007 | Image Alt Text Injection | heuristic | input | prompt-injection | high | high | 8 |
| INJ-I-008 | PDF Content Injection | heuristic | input | prompt-injection | high | high | 8 |
| INJ-I-009 | Code Comment Injection | heuristic | input | prompt-injection | medium | medium | 5 |
| INJ-I-010 | JSON/XML Payload Injection | heuristic | input | prompt-injection | high | high | 7 |
| INJ-O-001 | Base64 Encoding | heuristic | input | prompt-injection | high | medium | 6 |
| INJ-O-002 | ROT13 / Substitution Cipher | heuristic | input | prompt-injection | medium | medium | 5 |
| INJ-O-003 | Token Smuggling | classifier | input | prompt-injection | high | medium | 7 |
| INJ-O-004 | Payload Splitting | composite | input | prompt-injection | high | medium | 7 |
| INJ-O-005 | Homoglyph Substitution | heuristic | input | prompt-injection | medium | medium | 5 |
| INJ-O-006 | Adversarial Suffix | heuristic | input | prompt-injection | high | medium | 8 |
| INJ-O-007 | Emoji Encoding | heuristic | input | prompt-injection | medium | medium | 4 |
| INJ-O-008 | Language Switch Bypass | composite | input | prompt-injection | high | medium | 7 |
| INJ-O-009 | Low-Resource Language Injection | classifier | input | prompt-injection | medium | medium | 6 |
| INJ-O-010 | Leetspeak/Number Substitution | heuristic | input | prompt-injection | medium | medium | 4 |
| INJ-O-011 | Morse Code Encoding | heuristic | input | prompt-injection | low | medium | 3 |
| INJ-O-012 | Reversed Text | heuristic | input | prompt-injection | medium | medium | 5 |
| INJ-O-013 | Whitespace/Tab Encoding | heuristic | input | prompt-injection | medium | medium | 5 |
| INJ-O-014 | Pig Latin/Word Games | heuristic | input | prompt-injection | low | medium | 3 |
| INJ-O-015 | German Injection Patterns | heuristic | input | prompt-injection | high | high | 7 |
| INJ-O-016 | Spanish/French/Multilingual Injection | heuristic | input | prompt-injection | high | high | 7 |
| INJ-O-017 | Typo-Obfuscated Injection Commands | heuristic | input | prompt-injection | high | medium | 7 |
| INJ-S-001 | Paraphrased Instruction Override | semantic | input | prompt-injection | high | high | 8 |
| INJ-S-002 | Paraphrased System Prompt Extraction | semantic | input | prompt-injection | high | high | 9 |
| INJ-S-003 | Paraphrased Role Hijacking | semantic | input | prompt-injection | high | high | 8 |
| INJ-S-004 | Social Engineering for Data | semantic | input | prompt-injection | high | high | 9 |
| INJ-S-005 | Hypothetical Framing Attack | semantic | input | prompt-injection | high | high | 7 |
| INJ-S-006 | Emotional Manipulation | semantic | input | prompt-injection | high | high | 7 |
| INJ-S-007 | Authority Urgency Pressure | semantic | input | prompt-injection | high | high | 8 |
| INJ-S-008 | Multi-Step Escalation | semantic | input | prompt-injection | high | high | 8 |
| INJ-S-009 | Output Format Manipulation | semantic | input | prompt-injection | high | high | 7 |
| INJ-S-010 | Indirect Injection via Tool Output | semantic | input | prompt-injection | high | high | 9 |
| SP-001 | System Prompt Leak in Output | heuristic | output | system-prompt | critical | high | 12 |
| SP-002 | Confidentiality Marker Leak | heuristic | output | system-prompt | high | high | 8 |
| SP-003 | Training Data Extraction | heuristic | input | system-prompt | high | high | 7 |
| SP-004 | Model Architecture Probing | heuristic | input | system-prompt | low | medium | 3 |
