"""Pipeline orchestrator — runs signatures through engines, scores, decides."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import inferwall_core

from inferwall.core.policy import PolicyEngine, PolicyProfile
from inferwall.engines.heuristic import HeuristicEngine
from inferwall.signatures.loader import SignatureLoader
from inferwall.signatures.schema import SignatureDefinition


@dataclass
class ScanResponse:
    """Result of a scan operation."""

    decision: str  # "allow", "flag", "block"
    score: float
    matches: list[dict[str, object]] = field(default_factory=list)
    request_id: str = ""


class Pipeline:
    """Orchestrates signature loading, engine dispatch, scoring."""

    def __init__(
        self,
        catalog_dir: Path | None = None,
        policy_path: Path | None = None,
    ) -> None:
        # Load signatures
        if catalog_dir is None:
            catalog_dir = Path(__file__).parent.parent / "catalog"
        self._loader = SignatureLoader(catalog_dir)
        self._signatures = self._loader.load()

        # Load policy
        if policy_path is None:
            policy_path = Path(__file__).parent.parent / "policies" / "default.yaml"
        profile = PolicyProfile.from_yaml(policy_path)
        self._policy = PolicyEngine(profile)

        # Initialize engines
        self._heuristic = HeuristicEngine()

    @property
    def signature_count(self) -> int:
        return len(self._signatures)

    @property
    def policy(self) -> PolicyEngine:
        return self._policy

    def scan_input(self, text: str, request_id: str = "") -> ScanResponse:
        """Scan input text (user prompt)."""
        return self._scan(text, is_inbound=True, request_id=request_id)

    def scan_output(self, text: str, request_id: str = "") -> ScanResponse:
        """Scan output text (LLM response)."""
        return self._scan(text, is_inbound=False, request_id=request_id)

    def _scan(self, text: str, *, is_inbound: bool, request_id: str) -> ScanResponse:
        # Filter signatures by direction
        direction = "input" if is_inbound else "output"
        active_sigs = [
            s
            for s in self._signatures
            if s.detection.direction.value in (direction, "bidirectional")
            and self._is_sig_active(s)
        ]

        # Group by engine and scan
        heuristic_sigs = [
            s for s in active_sigs if s.detection.engine.value == "heuristic"
        ]

        all_matches: list[inferwall_core.Match] = []

        # Heuristic scan
        if heuristic_sigs:
            results = self._heuristic.scan(text, heuristic_sigs)
            for r in results:
                # Resolve points from policy
                points = self._policy.resolve_anomaly_points(
                    r.signature_id,
                    sig_default_points=int(r.score),
                )
                action = self._policy.resolve_action(
                    r.signature_id,
                    sig_default_action=self._get_sig_default_action(r.signature_id),
                )
                if action == "enforce":
                    all_matches.append(
                        inferwall_core.Match(
                            signature_id=r.signature_id,
                            engine="heuristic",
                            matched_text=r.matched_text,
                            score=float(points),
                            offset=r.offset,
                            length=r.length,
                        )
                    )

        # Evaluate score
        scoring_policy = inferwall_core.ScoringPolicy(
            inbound_threshold_flag=self._policy.inbound_flag_threshold,
            inbound_threshold_block=self._policy.inbound_block_threshold,
            outbound_threshold_flag=self._policy.outbound_flag_threshold,
            outbound_threshold_block=self._policy.outbound_block_threshold,
        )
        score_result = inferwall_core.evaluate_score(
            all_matches, scoring_policy, is_inbound
        )

        # If in monitor mode, override to allow
        if self._policy.is_monitor_mode:
            decision = "allow"
        else:
            decision = score_result.decision.__repr__().split(".")[-1].lower()

        return ScanResponse(
            decision=decision,
            score=score_result.total_score,
            matches=[
                {
                    "signature_id": m.signature_id,
                    "matched_text": m.matched_text,
                    "score": m.score,
                }
                for m in all_matches
            ],
            request_id=request_id,
        )

    def _is_sig_active(self, sig: SignatureDefinition) -> bool:
        return sig.tuning.enabled and sig.tuning.default_enabled

    def _get_sig_default_action(self, sig_id: str) -> str:
        sig = self._loader.get_by_id(sig_id)
        if sig:
            return sig.tuning.default_action.value
        return "enforce"
