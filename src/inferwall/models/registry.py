"""Model registry — defines which models are needed for each profile."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelSpec:
    """Specification for a downloadable model."""

    name: str
    repo_id: str  # HuggingFace repo ID
    filename: str  # File to download (or "" for full repo)
    size_mb: int  # Approximate size in MB
    engine: str  # Which engine uses this model
    profile: str  # Minimum profile: "standard" or "full"
    description: str


# Model registry — all models InferenceWall can use
MODELS: dict[str, ModelSpec] = {
    "deberta-injection": ModelSpec(
        name="deberta-injection",
        repo_id="protectai/deberta-v3-base-prompt-injection-v2",
        filename="",
        size_mb=400,
        engine="classifier",
        profile="standard",
        description="DeBERTa v3 fine-tuned for prompt injection detection",
    ),
    "distilbert-toxicity": ModelSpec(
        name="distilbert-toxicity",
        repo_id="Uzyau/distilbert-toxicity-onnx",
        filename="",
        size_mb=520,
        engine="classifier",
        profile="standard",
        description="DistilBERT multilingual toxicity classifier (ONNX)",
    ),
    "minilm-embeddings": ModelSpec(
        name="minilm-embeddings",
        repo_id="sentence-transformers/all-MiniLM-L6-v2",
        filename="",
        size_mb=80,
        engine="semantic",
        profile="standard",
        description="MiniLM-L6 for semantic similarity embeddings",
    ),
    "phi4-mini-judge": ModelSpec(
        name="phi4-mini-judge",
        repo_id="microsoft/Phi-4-mini-instruct-gguf",
        filename="Phi-4-mini-instruct-q4.gguf",
        size_mb=2400,
        engine="llm-judge",
        profile="full",
        description="Phi-4 Mini Q4 for borderline case adjudication",
    ),
}


def get_models_for_profile(profile: str) -> list[ModelSpec]:
    """Get models required for a deployment profile."""
    if profile == "lite":
        return []
    if profile == "standard":
        return [m for m in MODELS.values() if m.profile == "standard"]
    if profile == "full":
        return list(MODELS.values())
    return []


def get_model(name: str) -> ModelSpec | None:
    """Get a model spec by name."""
    return MODELS.get(name)
