"""Async HTTP shipper for ELK / Logstash testing facility."""

from __future__ import annotations

import os
from typing import Any

import httpx


class ElkShipper:
    """Ship structured events to a Logstash HTTP input for SIEM testing.

    Set ``IW_ELK_URL`` (e.g. ``http://localhost:8080``) to enable shipping.
    Events are fire-and-forget; failures are silently dropped so the scan
    path is never blocked.
    """

    def __init__(self, endpoint: str | None = None) -> None:
        self._endpoint = endpoint or os.environ.get("IW_ELK_URL")
        self._client: httpx.AsyncClient | None = None
        if self._endpoint:
            self._client = httpx.AsyncClient(timeout=5.0)

    @property
    def enabled(self) -> bool:
        return self._endpoint is not None and self._client is not None

    async def ship(self, payload: dict[str, Any]) -> None:
        if not self.enabled or self._client is None:
            return
        try:
            await self._client.post(self._endpoint, json=payload)
        except Exception:
            # Fire-and-forget: never block scan path for SIEM testing
            pass

    def ship_sync(self, payload: dict[str, Any]) -> None:
        """Synchronous fallback for code paths that are not async."""
        if not self.enabled:
            return
        try:
            httpx.post(self._endpoint, json=payload, timeout=5.0)
        except Exception:
            pass

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
