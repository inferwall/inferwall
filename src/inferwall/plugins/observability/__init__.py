"""Observability plugin for log shipping."""

from __future__ import annotations

import os
from typing import Any


def _get_shipper_class() -> type[Any] | None:
    """Lazy import - only load when needed."""
    try:
        from inferwall.plugins.observability.elk_shipper import ElkShipper

        return ElkShipper
    except ImportError:
        return None


def create_shipper(endpoint: str | None = None) -> Any | None:
    """Create an observability shipper if enabled via environment.

    Set IW_ELK_URL to enable (e.g., http://localhost:8080).
    Returns None if not configured or dependencies missing.
    """
    url = endpoint or os.environ.get("IW_ELK_URL")
    if not url:
        return None

    shipper_class = _get_shipper_class()
    if shipper_class is None:
        import logging

        logging.getLogger(__name__).warning(
            "Observability plugin requested but httpx not installed. "
            "Install with: pip install inferwall[observability]"
        )
        return None

    return shipper_class(url)
