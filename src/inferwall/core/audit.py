"""Audit logger — append-only JSON lines for security events."""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):  # noqa: UP042
        pass


def _iso_timestamp(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _create_obs_shipper() -> Any | None:
    """Lazy initialization of observability shipper - only imports when needed."""
    if not os.environ.get("IW_ELK_URL"):
        return None
    from inferwall.plugins.observability import create_shipper

    return create_shipper()


class AuditCategory(StrEnum):
    AUTH = "auth"
    POLICY = "policy"
    CONFIG = "config"
    SIGNATURES = "signatures"
    ENGINES = "engines"
    TLS = "tls"
    ADMIN = "admin"
    RATE_LIMIT = "rate_limit"
    LIFECYCLE = "lifecycle"
    SCAN = "scan"


@dataclass
class AuditEvent:
    """A single audit log entry."""

    category: str
    action: str
    timestamp: float = field(default_factory=time.time)
    details: dict[str, object] = field(default_factory=dict)
    ip: str = ""
    key_prefix: str = ""


class AuditLogger:
    """Append-only audit logger writing JSON lines."""

    def __init__(self, log_path: Path | None = None) -> None:
        self._log_path = log_path
        self._events: list[AuditEvent] = []
        self._obs_shipper = _create_obs_shipper()

    def log(self, event: AuditEvent) -> None:
        """Log an audit event."""
        self._events.append(event)
        if self._log_path:
            with open(self._log_path, "a") as f:
                f.write(json.dumps(asdict(event)) + "\n")
        if self._obs_shipper is not None and self._obs_shipper.enabled:
            payload = {
                "log_type": "audit",
                "timestamp": _iso_timestamp(event.timestamp),
                "category": event.category,
                "action": event.action,
                "details": event.details,
                "source_ip": event.ip,
                "key_prefix": event.key_prefix,
            }
            self._obs_shipper.ship_sync(payload)

    def get_events(
        self,
        category: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query recent audit events."""
        events = self._events
        if category:
            events = [e for e in events if e.category == category]
        return events[-limit:]

    @property
    def event_count(self) -> int:
        return len(self._events)
