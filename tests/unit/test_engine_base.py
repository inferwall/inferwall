"""Tests for engine abstraction — written BEFORE implementation (TDD)."""

from typing import Any

import pytest

from inferwall.engines.base import BaseEngine, ScanResult


class TestBaseEngineContract:
    """Test BaseEngine abstract interface contract."""

    def test_base_engine_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            BaseEngine()  # type: ignore[abstract]

    def test_concrete_engine_must_implement_scan(self) -> None:
        class IncompleteEngine(BaseEngine):
            @property
            def engine_type(self) -> str:
                return "test"

        with pytest.raises(TypeError):
            IncompleteEngine()  # type: ignore[abstract]

    def test_concrete_engine_with_scan_can_be_instantiated(self) -> None:
        class TestEngine(BaseEngine):
            @property
            def engine_type(self) -> str:
                return "test"

            def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
                return []

        engine = TestEngine()
        assert engine.engine_type == "test"


class TestScanResult:
    """Test ScanResult data class."""

    def test_scan_result_creation(self) -> None:
        result = ScanResult(
            signature_id="INJ-D-001",
            matched_text="ignore previous",
            score=8.0,
            offset=0,
            length=15,
        )
        assert result.signature_id == "INJ-D-001"
        assert result.score == 8.0

    def test_scan_result_equality(self) -> None:
        r1 = ScanResult("INJ-D-001", "test", 5.0, 0, 4)
        r2 = ScanResult("INJ-D-001", "test", 5.0, 0, 4)
        assert r1 == r2


class TestEngineWithEmptyInput:
    """Test engine behavior with empty inputs."""

    def test_scan_empty_text_returns_empty(self) -> None:
        class TestEngine(BaseEngine):
            @property
            def engine_type(self) -> str:
                return "test"

            def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
                if not text:
                    return []
                return [ScanResult("TEST-001", text, 5.0, 0, len(text))]

        engine = TestEngine()
        results = engine.scan("", [])
        assert results == []

    def test_scan_empty_signatures_returns_empty(self) -> None:
        class TestEngine(BaseEngine):
            @property
            def engine_type(self) -> str:
                return "test"

            def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
                if not signatures:
                    return []
                return [ScanResult("TEST-001", text, 5.0, 0, len(text))]

        engine = TestEngine()
        results = engine.scan("some text", [])
        assert results == []

    def test_scan_returns_list_of_scan_results(self) -> None:
        class TestEngine(BaseEngine):
            @property
            def engine_type(self) -> str:
                return "test"

            def scan(self, text: str, signatures: list[Any]) -> list[ScanResult]:
                return [ScanResult("TEST-001", "match", 5.0, 0, 5)]

        engine = TestEngine()
        results = engine.scan("test text", ["sig1"])
        assert len(results) == 1
        assert isinstance(results[0], ScanResult)
