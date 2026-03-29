"""FastAPI application for InferenceWall."""

from __future__ import annotations

import time

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from inferwall.api.deps import get_pipeline, verify_scan_auth

app = FastAPI(
    title="InferenceWall",
    description="Signature-based AI application firewall",
    version="0.1.4",
)

# Register routers
from inferwall.api.routes.signatures import router as signatures_router  # noqa: E402

app.include_router(signatures_router)


# --- Request/Response Models ---


class ScanRequest(BaseModel):
    text: str
    session_id: str | None = None


class MatchResponse(BaseModel):
    signature_id: str
    matched_text: str
    score: float


class ScanResponseModel(BaseModel):
    decision: str
    score: float
    matches: list[MatchResponse]
    request_id: str


class HealthResponse(BaseModel):
    status: str
    version: str
    signature_count: int


# --- Health Endpoints (unauthenticated for K8s/LB) ---


@app.get("/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    pipeline = get_pipeline()
    return HealthResponse(
        status="healthy",
        version="0.1.4",
        signature_count=pipeline.signature_count,
    )


@app.get("/v1/health/live")
def health_live() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/v1/health/ready")
def health_ready() -> dict[str, str]:
    pipeline = get_pipeline()
    if pipeline.signature_count > 0:
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Not ready: no signatures loaded")


# --- Scan Endpoints ---


@app.post("/v1/scan/input", response_model=ScanResponseModel)
def scan_input(
    request: ScanRequest,
    _role: str | None = Depends(verify_scan_auth),
) -> ScanResponseModel:
    pipeline = get_pipeline()
    request_id = f"req-{int(time.time() * 1000)}"
    result = pipeline.scan_input(request.text, request_id=request_id)
    return ScanResponseModel(
        decision=result.decision,
        score=result.score,
        matches=[
            MatchResponse(
                signature_id=m["signature_id"],  # type: ignore[arg-type]
                matched_text=m["matched_text"],  # type: ignore[arg-type]
                score=m["score"],  # type: ignore[arg-type]
            )
            for m in result.matches
        ],
        request_id=request_id,
    )


@app.post("/v1/scan/output", response_model=ScanResponseModel)
def scan_output(
    request: ScanRequest,
    _role: str | None = Depends(verify_scan_auth),
) -> ScanResponseModel:
    pipeline = get_pipeline()
    request_id = f"req-{int(time.time() * 1000)}"
    result = pipeline.scan_output(request.text, request_id=request_id)
    return ScanResponseModel(
        decision=result.decision,
        score=result.score,
        matches=[
            MatchResponse(
                signature_id=m["signature_id"],  # type: ignore[arg-type]
                matched_text=m["matched_text"],  # type: ignore[arg-type]
                score=m["score"],  # type: ignore[arg-type]
            )
            for m in result.matches
        ],
        request_id=request_id,
    )
