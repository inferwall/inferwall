"""Signature catalog API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from inferwall.api.deps import get_pipeline

router = APIRouter(prefix="/v1/signatures", tags=["signatures"])


class SignatureSummary(BaseModel):
    id: str
    name: str
    version: str
    category: str
    engine: str
    severity: str
    direction: str
    anomaly_points: int
    enabled: bool


class SignatureDetail(SignatureSummary):
    subcategory: str
    technique: str
    confidence: str
    performance_cost: str
    tags: list[str]
    condition: str
    default_action: str


@router.get("", response_model=list[SignatureSummary])
def list_signatures() -> list[SignatureSummary]:
    """List all loaded signatures."""
    pipeline = get_pipeline()
    loader = pipeline._loader  # noqa: SLF001
    return [
        SignatureSummary(
            id=sig.signature.id,
            name=sig.signature.name,
            version=sig.signature.version,
            category=sig.meta.category.value,
            engine=sig.detection.engine.value,
            severity=sig.meta.severity.value,
            direction=sig.detection.direction.value,
            anomaly_points=sig.scoring.anomaly_points,
            enabled=sig.tuning.default_enabled,
        )
        for sig in loader.load()
    ]


@router.get("/{sig_id}", response_model=SignatureDetail)
def get_signature(sig_id: str) -> SignatureDetail:
    """Get details of a specific signature."""
    pipeline = get_pipeline()
    loader = pipeline._loader  # noqa: SLF001
    sig = loader.get_by_id(sig_id)
    if not sig:
        raise HTTPException(status_code=404, detail=f"Signature {sig_id} not found")
    return SignatureDetail(
        id=sig.signature.id,
        name=sig.signature.name,
        version=sig.signature.version,
        category=sig.meta.category.value,
        engine=sig.detection.engine.value,
        severity=sig.meta.severity.value,
        direction=sig.detection.direction.value,
        anomaly_points=sig.scoring.anomaly_points,
        enabled=sig.tuning.default_enabled,
        subcategory=sig.meta.subcategory,
        technique=sig.meta.technique,
        confidence=sig.meta.confidence.value,
        performance_cost=sig.meta.performance_cost.value,
        tags=sig.meta.tags or [],
        condition=sig.detection.condition.value,
        default_action=sig.tuning.default_action.value,
    )
