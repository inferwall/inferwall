"""Shared API dependencies — avoids circular imports between app and routes."""

from __future__ import annotations

import os
from typing import Annotated

from fastapi import Header, HTTPException

from inferwall.core.pipeline import Pipeline

_pipeline: Pipeline | None = None


def get_pipeline() -> Pipeline:
    """Get the global pipeline instance."""
    global _pipeline  # noqa: PLW0603
    if _pipeline is None:
        _pipeline = Pipeline()
    return _pipeline


def _get_api_key() -> str | None:
    return os.environ.get("IW_API_KEY")


def _get_admin_key() -> str | None:
    return os.environ.get("IW_ADMIN_KEY")


def verify_scan_auth(
    authorization: Annotated[str | None, Header()] = None,
) -> str | None:
    """Verify scan-level auth. Returns role or None if auth disabled."""
    api_key = _get_api_key()
    admin_key = _get_admin_key()

    if not api_key and not admin_key:
        return None

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    token = authorization.removeprefix("Bearer ").strip()

    if admin_key and token == admin_key:
        return "admin"
    if api_key and token == api_key:
        return "scan"

    raise HTTPException(status_code=401, detail="Invalid API key")


def verify_admin_auth(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """Verify admin-level auth."""
    admin_key = _get_admin_key()

    if not admin_key and not _get_api_key():
        return "admin"

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    token = authorization.removeprefix("Bearer ").strip()

    if admin_key and token == admin_key:
        return "admin"

    raise HTTPException(status_code=403, detail="Admin access required")
