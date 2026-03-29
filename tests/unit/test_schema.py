"""Tests for signature schema validation — written BEFORE implementation (TDD)."""

import pytest
import yaml
from pydantic import ValidationError

from inferwall.signatures.schema import (
    SignatureDefinition,
)

# --- Valid signature YAML ---

VALID_HEURISTIC_SIG = {
    "signature": {
        "id": "INJ-D-001",
        "name": "Role-Play Persona Jailbreak",
        "version": "1.0.0",
    },
    "meta": {
        "category": "prompt-injection",
        "subcategory": "direct",
        "technique": "role-play-persona",
        "severity": "high",
        "confidence": "high",
        "performance_cost": "low",
    },
    "detection": {
        "engine": "heuristic",
        "direction": "input",
        "patterns": [
            {
                "type": "regex",
                "value": r"(?i)(you\s+are|act\s+as|pretend\s+to\s+be)\s+(a|an)\s+\w+",
            },
        ],
        "condition": "any",
    },
    "scoring": {"anomaly_points": 8},
    "tuning": {"enabled": True, "default_enabled": True, "default_action": "enforce"},
}


VALID_OUTPUT_SIG = {
    "signature": {"id": "DL-P-001", "name": "Email Addresses", "version": "1.0.0"},
    "meta": {
        "category": "data-leakage",
        "subcategory": "pii",
        "technique": "email-detection",
        "severity": "medium",
        "confidence": "high",
        "performance_cost": "low",
    },
    "detection": {
        "engine": "heuristic",
        "direction": "output",
        "patterns": [
            {
                "type": "regex",
                "value": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            },
        ],
        "condition": "any",
    },
    "scoring": {"anomaly_points": 4},
    "tuning": {"enabled": True, "default_enabled": True, "default_action": "enforce"},
}


class TestSignatureSchema:
    """Test that valid YAML passes schema validation."""

    def test_valid_heuristic_signature_parses(self) -> None:
        sig = SignatureDefinition.model_validate(VALID_HEURISTIC_SIG)
        assert sig.signature.id == "INJ-D-001"
        assert sig.meta.category == "prompt-injection"
        assert sig.detection.engine == "heuristic"
        assert sig.scoring.anomaly_points == 8

    def test_valid_output_signature_parses(self) -> None:
        sig = SignatureDefinition.model_validate(VALID_OUTPUT_SIG)
        assert sig.signature.id == "DL-P-001"
        assert sig.detection.direction == "output"

    def test_signature_from_yaml_string(self) -> None:
        yaml_str = yaml.dump(VALID_HEURISTIC_SIG)
        data = yaml.safe_load(yaml_str)
        sig = SignatureDefinition.model_validate(data)
        assert sig.signature.id == "INJ-D-001"

    def test_bidirectional_direction(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["detection"] = {**data["detection"], "direction": "bidirectional"}
        sig = SignatureDefinition.model_validate(data)
        assert sig.detection.direction == "bidirectional"


class TestSignatureSchemaRequiredFields:
    """Test that missing required fields are rejected."""

    def test_missing_signature_id_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["signature"] = {"name": "Test", "version": "1.0.0"}  # missing id
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_missing_meta_category_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["meta"] = {**data["meta"]}
        del data["meta"]["category"]
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_missing_detection_engine_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["detection"] = {**data["detection"]}
        del data["detection"]["engine"]
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_missing_scoring_anomaly_points_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["scoring"] = {}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_missing_tuning_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        del data["tuning"]
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)


class TestSignatureSchemaEnumValidation:
    """Test that invalid enum values are rejected with clear errors."""

    def test_invalid_category_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["meta"] = {**data["meta"], "category": "not-a-category"}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_invalid_severity_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["meta"] = {**data["meta"], "severity": "extreme"}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_invalid_engine_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["detection"] = {**data["detection"], "engine": "neural-net"}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_invalid_direction_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["detection"] = {**data["detection"], "direction": "both"}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_invalid_condition_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["detection"] = {**data["detection"], "condition": "xor"}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_invalid_confidence_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["meta"] = {**data["meta"], "confidence": "very-high"}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_invalid_performance_cost_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["meta"] = {**data["meta"], "performance_cost": "extreme"}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_invalid_default_action_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["tuning"] = {**data["tuning"], "default_action": "delete"}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)


class TestSignatureSchemaAnomalyPointsRange:
    """Test anomaly_points range validation (1-15)."""

    def test_anomaly_points_min(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["scoring"] = {"anomaly_points": 1}
        sig = SignatureDefinition.model_validate(data)
        assert sig.scoring.anomaly_points == 1

    def test_anomaly_points_max(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["scoring"] = {"anomaly_points": 15}
        sig = SignatureDefinition.model_validate(data)
        assert sig.scoring.anomaly_points == 15

    def test_anomaly_points_zero_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["scoring"] = {"anomaly_points": 0}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)

    def test_anomaly_points_over_max_rejected(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["scoring"] = {"anomaly_points": 16}
        with pytest.raises(ValidationError):
            SignatureDefinition.model_validate(data)


class TestPatternTypes:
    """Test pattern type validation."""

    def test_regex_pattern(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["detection"] = {
            **data["detection"],
            "patterns": [{"type": "regex", "value": r"test.*pattern"}],
        }
        sig = SignatureDefinition.model_validate(data)
        assert sig.detection.patterns[0].type == "regex"

    def test_substring_pattern(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["detection"] = {
            **data["detection"],
            "patterns": [
                {"type": "substring", "value": "ignore previous instructions"},
            ],
        }
        sig = SignatureDefinition.model_validate(data)
        assert sig.detection.patterns[0].type == "substring"

    def test_multiple_patterns(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["detection"] = {
            **data["detection"],
            "patterns": [
                {"type": "regex", "value": r"pattern1"},
                {"type": "substring", "value": "pattern2"},
            ],
        }
        sig = SignatureDefinition.model_validate(data)
        assert len(sig.detection.patterns) == 2


class TestOptionalFields:
    """Test optional fields."""

    def test_owasp_llm_optional(self) -> None:
        sig = SignatureDefinition.model_validate(VALID_HEURISTIC_SIG)
        assert sig.meta.owasp_llm is None

    def test_owasp_llm_present(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["meta"] = {**data["meta"], "owasp_llm": "LLM01:2025"}
        sig = SignatureDefinition.model_validate(data)
        assert sig.meta.owasp_llm == "LLM01:2025"

    def test_tags_optional(self) -> None:
        sig = SignatureDefinition.model_validate(VALID_HEURISTIC_SIG)
        assert sig.meta.tags is None or sig.meta.tags == []

    def test_tags_present(self) -> None:
        data = {**VALID_HEURISTIC_SIG}
        data["meta"] = {**data["meta"], "tags": ["jailbreak", "persona"]}
        sig = SignatureDefinition.model_validate(data)
        assert sig.meta.tags == ["jailbreak", "persona"]
