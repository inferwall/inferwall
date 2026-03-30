"""Pipeline orchestrator — runs signatures through engines, scores, decides."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import inferwall_core

from inferwall.core.policy import PolicyEngine, PolicyProfile
from inferwall.engines.heuristic import HeuristicEngine
from inferwall.signatures.loader import (
    USER_DIR,
    SignatureLoader,
)
from inferwall.signatures.schema import SignatureDefinition

# Default shipped policy
SHIPPED_POLICIES = Path(__file__).parent.parent / "policies"


@dataclass
class ScanResponse:
    """Result of a scan operation."""

    decision: str  # "allow", "flag", "block"
    score: float
    matches: list[dict[str, object]] = field(default_factory=list)
    request_id: str = ""


class Pipeline:
    """Orchestrates signature loading, engine dispatch, scoring.

    Supports three-layer catalog merge and user-configurable policies.
    """

    def __init__(
        self,
        catalog_dir: Path | None = None,
        policy_path: Path | None = None,
    ) -> None:
        # Load signatures
        if catalog_dir is not None:
            # Explicit directory — single-directory mode
            self._loader = SignatureLoader(catalog_dir)
            self._signatures = self._loader.load()
        else:
            # Default — three-layer merge
            self._loader = SignatureLoader()
            self._signatures = self._loader.load_merged()

        # Load policy
        if policy_path is None:
            policy_path = _resolve_policy_path()
        profile = PolicyProfile.from_yaml(policy_path)
        self._policy = PolicyEngine(profile)

        # Initialize engines
        self._heuristic = HeuristicEngine()
        self._classifier = self._init_classifier()
        self._llm_judge = self._init_llm_judge()

    def _init_classifier(self) -> object | None:
        """Try to initialize classifier engine with downloaded models."""
        try:
            from inferwall.engines.classifier import ClassifierEngine
            from inferwall.models.downloader import ModelDownloader
            from inferwall.models.registry import get_model

            engine = ClassifierEngine()
            if not engine.is_available:
                return None

            downloader = ModelDownloader()
            for model_name in ("deberta-injection", "distilbert-toxicity"):
                spec = get_model(model_name)
                if spec and downloader.is_downloaded(spec):
                    engine.load_model(model_name, downloader.model_path(spec))

            return engine if engine.loaded_models else None
        except Exception:
            return None

    def _init_llm_judge(self) -> object | None:
        """Try to initialize LLM judge engine with downloaded model."""
        try:
            from inferwall.engines.llm_judge import LLMJudgeEngine
            from pathlib import Path

            judge_dir = Path.home() / ".cache" / "inferwall" / "models" / "llm-judge"
            if not judge_dir.exists():
                return None

            engine = LLMJudgeEngine()
            if engine.load_model(judge_dir):
                return engine
            return None
        except Exception:
            return None

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
        classifier_sigs = [
            s
            for s in active_sigs
            if s.detection.engine.value == "classifier"
        ]

        all_matches: list[inferwall_core.Match] = []

        # Heuristic scan
        if heuristic_sigs:
            results = self._heuristic.scan(text, heuristic_sigs)
            for r in results:
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

        # Classifier scan (Standard/Full profiles)
        if classifier_sigs and self._classifier is not None:
            results = self._classifier.scan(text, classifier_sigs)  # type: ignore[union-attr]
            for r in results:
                points = self._policy.resolve_anomaly_points(
                    r.signature_id,
                    sig_default_points=int(r.score),
                )
                action = self._policy.resolve_action(
                    r.signature_id,
                    sig_default_action=self._get_sig_default_action(
                        r.signature_id
                    ),
                )
                if action == "enforce":
                    all_matches.append(
                        inferwall_core.Match(
                            signature_id=r.signature_id,
                            engine="classifier",
                            matched_text=r.matched_text,
                            score=float(points),
                            offset=r.offset,
                            length=r.length,
                        )
                    )

        # LLM-Judge (Full profile) — only for ambiguous scores
        if self._llm_judge is not None:
            current_score = sum(m.score for m in all_matches)
            if self._llm_judge.should_invoke(current_score):  # type: ignore[union-attr]
                judge_results = self._llm_judge.scan(text, [])  # type: ignore[union-attr]
                for r in judge_results:
                    all_matches.append(
                        inferwall_core.Match(
                            signature_id=r.signature_id,
                            engine="llm-judge",
                            matched_text=r.matched_text,
                            score=r.score,
                            offset=0,
                            length=len(text),
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


def _resolve_policy_path() -> Path:
    """Resolve policy path: env var > user dir > shipped default."""
    env_path = os.environ.get("IW_POLICY_PATH")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p

    user_policies = USER_DIR / "policies"
    if user_policies.exists():
        # Use first .yaml file in user policies dir
        yamls = list(user_policies.glob("*.yaml")) + list(user_policies.glob("*.yml"))
        if yamls:
            return sorted(yamls)[0]

    return SHIPPED_POLICIES / "default.yaml"
