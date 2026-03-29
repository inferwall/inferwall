"""Signature schema — Pydantic models for YAML signature definitions."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):  # type: ignore[no-redef]
        pass


from pydantic import BaseModel, Field


class Category(StrEnum):
    PROMPT_INJECTION = "prompt-injection"
    CONTENT_SAFETY = "content-safety"
    DATA_LEAKAGE = "data-leakage"
    AGENTIC = "agentic"
    SYSTEM_PROMPT = "system-prompt"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PerformanceCost(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EngineType(StrEnum):
    HEURISTIC = "heuristic"
    CLASSIFIER = "classifier"
    SEMANTIC = "semantic"
    LLM_JUDGE = "llm-judge"
    COMPOSITE = "composite"


class Direction(StrEnum):
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"


class Condition(StrEnum):
    ANY = "any"
    ALL = "all"
    WEIGHTED = "weighted"


class DefaultAction(StrEnum):
    ENFORCE = "enforce"
    MONITOR = "monitor"


class PatternType(StrEnum):
    REGEX = "regex"
    SUBSTRING = "substring"
    SEMANTIC = "semantic"
    PERPLEXITY = "perplexity"
    ENCODING = "encoding"
    UNICODE = "unicode"


class Signature(BaseModel):
    id: str
    name: str
    version: str


class Meta(BaseModel):
    category: Category
    subcategory: str
    technique: str
    owasp_llm: str | None = None
    severity: Severity
    confidence: Confidence
    performance_cost: PerformanceCost
    tags: list[str] | None = None


class Pattern(BaseModel):
    type: PatternType
    value: str | None = None
    flags: str | None = None
    case_insensitive: bool | None = None
    reference_phrases: list[str] | None = None
    similarity_threshold: float | None = None
    min_threshold: float | None = None
    max_threshold: float | None = None
    encodings: list[str] | None = None
    checks: list[str] | None = None


class Detection(BaseModel):
    engine: EngineType
    direction: Direction
    patterns: list[Pattern] | None = None
    model: str | None = None
    condition: Condition


class Scoring(BaseModel):
    anomaly_points: int = Field(ge=1, le=15)


class Tuning(BaseModel):
    enabled: bool
    default_enabled: bool
    default_action: DefaultAction


class SignatureDefinition(BaseModel):
    signature: Signature
    meta: Meta
    detection: Detection
    scoring: Scoring
    tuning: Tuning
