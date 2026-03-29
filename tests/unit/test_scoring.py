"""Tests for Python-level scoring integration."""

import inferwall_core


class TestScoringIntegration:
    """Test scoring via PyO3 interface."""

    def test_evaluate_empty_matches(self) -> None:
        policy = inferwall_core.ScoringPolicy(5.0, 15.0, 5.0, 10.0)
        result = inferwall_core.evaluate_score([], policy, True)
        assert result.total_score == 0.0
        assert result.decision == inferwall_core.Decision.Allow

    def test_evaluate_flag(self) -> None:
        m = inferwall_core.Match("TEST", "heuristic", "text", 7.0, 0, 4)
        policy = inferwall_core.ScoringPolicy(5.0, 15.0, 5.0, 10.0)
        result = inferwall_core.evaluate_score([m], policy, True)
        assert result.decision == inferwall_core.Decision.Flag

    def test_evaluate_block(self) -> None:
        m1 = inferwall_core.Match("A", "heuristic", "t", 8.0, 0, 1)
        m2 = inferwall_core.Match("B", "heuristic", "t", 8.0, 0, 1)
        policy = inferwall_core.ScoringPolicy(5.0, 15.0, 5.0, 10.0)
        result = inferwall_core.evaluate_score([m1, m2], policy, True)
        assert result.decision == inferwall_core.Decision.Block

    def test_early_exit(self) -> None:
        m = inferwall_core.Match("A", "heuristic", "t", 30.0, 0, 1)
        assert inferwall_core.should_early_exit([m], 25.0) is True

    def test_no_early_exit(self) -> None:
        m = inferwall_core.Match("A", "heuristic", "t", 5.0, 0, 1)
        assert inferwall_core.should_early_exit([m], 25.0) is False


class TestSessionStoreIntegration:
    """Test session store via PyO3 interface."""

    def test_create_and_get(self) -> None:
        store = inferwall_core.SessionStore()
        assert store.create("s1") is True
        state = store.get("s1")
        assert state is not None
        score, turns, sigs = state
        assert score == 0.0
        assert turns == 0

    def test_update_accumulates(self) -> None:
        store = inferwall_core.SessionStore()
        store.create("s1")
        store.update("s1", 5.0, ["SIG-A"])
        store.update("s1", 3.0, ["SIG-B"])
        score, turns, sigs = store.get("s1")
        assert score == 8.0
        assert turns == 2
        assert len(sigs) == 2

    def test_delete(self) -> None:
        store = inferwall_core.SessionStore()
        store.create("s1")
        assert store.delete("s1") is True
        assert store.get("s1") is None

    def test_cleanup(self) -> None:
        store = inferwall_core.SessionStore()
        store.create("s1", 0)  # TTL = 0 seconds
        import time

        time.sleep(0.01)
        removed = store.cleanup_expired()
        assert removed == 1
