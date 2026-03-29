"""Policy engine — loads profiles, resolves overrides, enforcement modes."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):  # noqa: UP042
        pass


from pathlib import Path

import yaml
from pydantic import BaseModel


class PolicyMode(StrEnum):
    MONITOR = "monitor"
    ENFORCE = "enforce"


class ActionOverride(StrEnum):
    DEFAULT = "default"
    MONITOR = "monitor"
    ENFORCE = "enforce"


class Thresholds(BaseModel):
    inbound_flag: float
    inbound_block: float
    outbound_flag: float
    outbound_block: float
    early_exit: float


class SignatureOverride(BaseModel):
    action: ActionOverride = ActionOverride.DEFAULT
    anomaly_points: int | None = None


class PolicyProfile(BaseModel):
    name: str
    version: str
    mode: PolicyMode
    thresholds: Thresholds
    signatures: dict[str, SignatureOverride] = {}

    @classmethod
    def from_yaml(cls, path: Path) -> PolicyProfile:
        """Load a policy profile from a YAML file."""
        data = yaml.safe_load(path.read_text())
        return cls.model_validate(data)


class PolicyEngine:
    """Resolves policy overrides and enforcement modes for signatures."""

    def __init__(self, profile: PolicyProfile) -> None:
        self._profile = profile

    @property
    def is_monitor_mode(self) -> bool:
        return self._profile.mode == PolicyMode.MONITOR

    @property
    def inbound_flag_threshold(self) -> float:
        return self._profile.thresholds.inbound_flag

    @property
    def inbound_block_threshold(self) -> float:
        return self._profile.thresholds.inbound_block

    @property
    def outbound_flag_threshold(self) -> float:
        return self._profile.thresholds.outbound_flag

    @property
    def outbound_block_threshold(self) -> float:
        return self._profile.thresholds.outbound_block

    @property
    def early_exit_threshold(self) -> float:
        return self._profile.thresholds.early_exit

    def resolve_action(self, sig_id: str, sig_default_action: str) -> str:
        """Resolve the effective action for a signature.

        Precedence: per-signature override > global policy mode > signature default.
        """
        override = self._profile.signatures.get(sig_id)

        if override and override.action != ActionOverride.DEFAULT:
            result: str = override.action.value
            return result

        # Global mode takes precedence over signature default
        if self._profile.mode == PolicyMode.MONITOR:
            return "monitor"

        return sig_default_action

    def resolve_anomaly_points(self, sig_id: str, sig_default_points: int) -> int:
        """Resolve the effective anomaly points for a signature."""
        override = self._profile.signatures.get(sig_id)
        if override and override.anomaly_points is not None:
            return override.anomaly_points
        return sig_default_points
