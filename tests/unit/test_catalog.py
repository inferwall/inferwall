"""Tests for the shipped signature catalog — validates loader + schema end-to-end."""

from pathlib import Path

from inferwall.signatures.loader import SignatureLoader

CATALOG_DIR = Path(__file__).parent.parent.parent / "src" / "inferwall" / "catalog"

EXPECTED_SIGS = {
    # Injection — direct (existing)
    "INJ-D-001",
    "INJ-D-002",
    "INJ-D-003",
    "INJ-D-008",
    # Injection — indirect (existing)
    "INJ-I-001",
    "INJ-I-002",
    "INJ-I-003",
    # Injection — obfuscation (existing)
    "INJ-O-001",
    "INJ-O-002",
    "INJ-O-005",
    "INJ-O-006",
    "INJ-O-007",
    # Data leakage (existing)
    "DL-P-001",
    "DL-P-002",
    "DL-S-001",
    # Content safety (M2)
    "CS-T-001",
    "CS-T-002",
    "CS-T-003",
    "CS-T-004",
    "CS-B-001",
    "CS-B-002",
    # Data leakage (M2)
    "DL-P-003",
    "DL-P-004",
    "DL-S-002",
    "DL-S-003",
    # Injection extras (M2)
    "INJ-D-004",
    "INJ-D-005",
    "INJ-D-006",
    "INJ-D-007",
    "INJ-I-004",
    "INJ-I-005",
    "INJ-O-003",
    "INJ-O-004",
    "INJ-O-008",
    "INJ-O-009",
    # System prompt (M2)
    "SP-001",
    "SP-002",
    # Agentic (M2)
    "AG-001",
    "AG-002",
    "AG-003",
}


class TestCatalogLoads:
    """Test that all shipped signatures load and validate."""

    def test_catalog_directory_exists(self) -> None:
        assert CATALOG_DIR.exists()

    def test_all_40_signatures_load(self) -> None:
        loader = SignatureLoader(CATALOG_DIR)
        sigs = loader.load()
        assert len(sigs) == 40, f"Expected 40, got {len(sigs)}. Errors: {loader.errors}"
        assert len(loader.errors) == 0

    def test_all_expected_ids_present(self) -> None:
        loader = SignatureLoader(CATALOG_DIR)
        loader.load()
        loaded_ids = set(loader.get_all_ids())
        assert loaded_ids == EXPECTED_SIGS

    def test_signatures_grouped_by_engine(self) -> None:
        loader = SignatureLoader(CATALOG_DIR)
        loader.load()
        groups = loader.group_by_engine()
        assert "heuristic" in groups
        assert len(groups["heuristic"]) == 24
        assert "classifier" in groups
        assert len(groups["classifier"]) == 11
        assert "semantic" in groups
        assert len(groups["semantic"]) == 1
        assert "composite" in groups
        assert len(groups["composite"]) == 4

    def test_input_signatures(self) -> None:
        loader = SignatureLoader(CATALOG_DIR)
        loader.load()
        input_sigs = [
            s for s in loader.load() if s.detection.direction.value == "input"
        ]
        assert len(input_sigs) == 30

    def test_output_signatures(self) -> None:
        loader = SignatureLoader(CATALOG_DIR)
        loader.load()
        output_sigs = [
            s for s in loader.load() if s.detection.direction.value == "output"
        ]
        assert len(output_sigs) == 10

    def test_anomaly_points_in_valid_range(self) -> None:
        loader = SignatureLoader(CATALOG_DIR)
        sigs = loader.load()
        for sig in sigs:
            assert 1 <= sig.scoring.anomaly_points <= 15, (
                f"{sig.signature.id}: points {sig.scoring.anomaly_points} out of range"
            )

    def test_critical_sigs_have_high_points(self) -> None:
        loader = SignatureLoader(CATALOG_DIR)
        sigs = loader.load()
        for sig in sigs:
            if sig.meta.severity.value == "critical":
                assert sig.scoring.anomaly_points >= 10, (
                    f"{sig.signature.id}: critical severity "
                    f"but only {sig.scoring.anomaly_points} points"
                )
