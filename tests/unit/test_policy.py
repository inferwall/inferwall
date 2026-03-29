"""Tests for policy engine — written BEFORE implementation (TDD)."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from inferwall.core.policy import PolicyEngine, PolicyProfile

# --- Test policy data ---

DEFAULT_POLICY = {
    "name": "default",
    "version": "1.0.0",
    "mode": "enforce",
    "thresholds": {
        "inbound_flag": 5,
        "inbound_block": 15,
        "outbound_flag": 5,
        "outbound_block": 10,
        "early_exit": 25,
    },
    "signatures": {},
}

MONITOR_POLICY = {
    "name": "monitor-only",
    "version": "1.0.0",
    "mode": "monitor",
    "thresholds": {
        "inbound_flag": 5,
        "inbound_block": 15,
        "outbound_flag": 5,
        "outbound_block": 10,
        "early_exit": 25,
    },
    "signatures": {},
}

POLICY_WITH_OVERRIDES = {
    "name": "custom",
    "version": "1.0.0",
    "mode": "enforce",
    "thresholds": {
        "inbound_flag": 5,
        "inbound_block": 15,
        "outbound_flag": 5,
        "outbound_block": 10,
        "early_exit": 25,
    },
    "signatures": {
        "INJ-D-001": {"action": "monitor", "anomaly_points": 3},
        "INJ-D-008": {"action": "enforce"},
    },
}


class TestPolicyProfileParsing:
    """Test policy profile loading and validation."""

    def test_parse_default_policy(self) -> None:
        profile = PolicyProfile.model_validate(DEFAULT_POLICY)
        assert profile.name == "default"
        assert profile.mode == "enforce"

    def test_parse_monitor_policy(self) -> None:
        profile = PolicyProfile.model_validate(MONITOR_POLICY)
        assert profile.mode == "monitor"

    def test_parse_policy_with_overrides(self) -> None:
        profile = PolicyProfile.model_validate(POLICY_WITH_OVERRIDES)
        assert "INJ-D-001" in profile.signatures
        assert profile.signatures["INJ-D-001"].action == "monitor"

    def test_invalid_mode_rejected(self) -> None:
        data = {**DEFAULT_POLICY, "mode": "passive"}
        with pytest.raises(ValidationError):
            PolicyProfile.model_validate(data)

    def test_missing_name_rejected(self) -> None:
        data = {**DEFAULT_POLICY}
        del data["name"]
        with pytest.raises(ValidationError):
            PolicyProfile.model_validate(data)


class TestPolicyEngineOverrideResolution:
    """Test override precedence: per-sig override > global mode > default."""

    def test_global_enforce_no_override_uses_signature_default(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(DEFAULT_POLICY))
        # No per-sig override, global is enforce → use signature default_action
        action = engine.resolve_action("INJ-D-001", sig_default_action="enforce")
        assert action == "enforce"

    def test_global_monitor_overrides_signature_default(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(MONITOR_POLICY))
        # Global is monitor → even if sig default is enforce, result is monitor
        action = engine.resolve_action("INJ-D-001", sig_default_action="enforce")
        assert action == "monitor"

    def test_per_sig_override_takes_precedence_over_global(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(POLICY_WITH_OVERRIDES))
        # INJ-D-001 is overridden to monitor even though global is enforce
        action = engine.resolve_action("INJ-D-001", sig_default_action="enforce")
        assert action == "monitor"

    def test_per_sig_enforce_overrides_global_monitor(self) -> None:
        data = {**MONITOR_POLICY, "signatures": {"INJ-D-008": {"action": "enforce"}}}
        engine = PolicyEngine(PolicyProfile.model_validate(data))
        # INJ-D-008 is overridden to enforce even though global is monitor
        action = engine.resolve_action("INJ-D-008", sig_default_action="monitor")
        assert action == "enforce"

    def test_default_override_uses_signature_default(self) -> None:
        data = {**DEFAULT_POLICY, "signatures": {"INJ-D-001": {"action": "default"}}}
        engine = PolicyEngine(PolicyProfile.model_validate(data))
        action = engine.resolve_action("INJ-D-001", sig_default_action="enforce")
        assert action == "enforce"


class TestPolicyEngineAnomalyPointsOverride:
    """Test per-signature anomaly point adjustments."""

    def test_override_anomaly_points(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(POLICY_WITH_OVERRIDES))
        points = engine.resolve_anomaly_points("INJ-D-001", sig_default_points=8)
        assert points == 3

    def test_no_override_uses_signature_default(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(DEFAULT_POLICY))
        points = engine.resolve_anomaly_points("INJ-D-001", sig_default_points=8)
        assert points == 8

    def test_override_without_points_uses_default(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(POLICY_WITH_OVERRIDES))
        # INJ-D-008 has action override but no points override
        points = engine.resolve_anomaly_points("INJ-D-008", sig_default_points=10)
        assert points == 10


class TestPolicyEngineThresholds:
    """Test threshold resolution."""

    def test_inbound_thresholds(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(DEFAULT_POLICY))
        assert engine.inbound_flag_threshold == 5
        assert engine.inbound_block_threshold == 15

    def test_outbound_thresholds(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(DEFAULT_POLICY))
        assert engine.outbound_flag_threshold == 5
        assert engine.outbound_block_threshold == 10

    def test_early_exit_threshold(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(DEFAULT_POLICY))
        assert engine.early_exit_threshold == 25


class TestPolicyEngineEnforcementModes:
    """Test enforcement mode resolution."""

    def test_monitor_mode_never_blocks(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(MONITOR_POLICY))
        assert engine.is_monitor_mode is True

    def test_enforce_mode_allows_blocking(self) -> None:
        engine = PolicyEngine(PolicyProfile.model_validate(DEFAULT_POLICY))
        assert engine.is_monitor_mode is False


class TestPolicyEngineLoadFromYAML:
    """Test loading policy from YAML file."""

    def test_load_from_yaml(self, tmp_path: Path) -> None:
        policy_path = tmp_path / "default.yaml"
        policy_path.write_text(yaml.dump(DEFAULT_POLICY))
        profile = PolicyProfile.from_yaml(policy_path)
        assert profile.name == "default"

    def test_load_invalid_yaml_raises(self, tmp_path: Path) -> None:
        policy_path = tmp_path / "bad.yaml"
        policy_path.write_text("{{invalid yaml::")
        with pytest.raises((yaml.YAMLError, ValidationError)):
            PolicyProfile.from_yaml(policy_path)
