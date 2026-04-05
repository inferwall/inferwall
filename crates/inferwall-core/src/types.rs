use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

/// Represents a single signature match from detection.
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Match {
    #[pyo3(get, set)]
    pub signature_id: String,
    #[pyo3(get, set)]
    pub engine: String,
    #[pyo3(get, set)]
    pub matched_text: String,
    #[pyo3(get, set)]
    pub score: f64,
    #[pyo3(get, set)]
    pub offset: usize,
    #[pyo3(get, set)]
    pub length: usize,
    #[pyo3(get, set)]
    pub confidence: f64,
    #[pyo3(get, set)]
    pub severity: f64,
}

#[pymethods]
impl Match {
    #[new]
    #[pyo3(signature = (signature_id, engine, matched_text, score, offset, length, confidence=0.0, severity=0.0))]
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        signature_id: String,
        engine: String,
        matched_text: String,
        score: f64,
        offset: usize,
        length: usize,
        confidence: f64,
        severity: f64,
    ) -> Self {
        Self {
            signature_id,
            engine,
            matched_text,
            score,
            offset,
            length,
            confidence,
            severity,
        }
    }

    /// Construct a Match from confidence and severity, computing score = confidence * severity.
    #[staticmethod]
    pub fn with_confidence(
        signature_id: String,
        engine: String,
        matched_text: String,
        confidence: f64,
        severity: f64,
        offset: usize,
        length: usize,
    ) -> Self {
        Self {
            signature_id,
            engine,
            matched_text,
            score: confidence * severity,
            offset,
            length,
            confidence,
            severity,
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "Match(sig={}, engine={}, score={}, confidence={}, severity={})",
            self.signature_id, self.engine, self.score, self.confidence, self.severity
        )
    }
}

/// Final scan decision.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum Decision {
    Allow,
    Flag,
    Block,
}

#[pymethods]
impl Decision {
    fn __repr__(&self) -> String {
        match self {
            Decision::Allow => "Decision.Allow".to_string(),
            Decision::Flag => "Decision.Flag".to_string(),
            Decision::Block => "Decision.Block".to_string(),
        }
    }
}

/// Scoring policy configuration passed from Python.
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ScoringPolicy {
    #[pyo3(get, set)]
    pub inbound_threshold_flag: f64,
    #[pyo3(get, set)]
    pub inbound_threshold_block: f64,
    #[pyo3(get, set)]
    pub outbound_threshold_flag: f64,
    #[pyo3(get, set)]
    pub outbound_threshold_block: f64,
}

#[pymethods]
impl ScoringPolicy {
    #[new]
    pub fn new(
        inbound_threshold_flag: f64,
        inbound_threshold_block: f64,
        outbound_threshold_flag: f64,
        outbound_threshold_block: f64,
    ) -> Self {
        Self {
            inbound_threshold_flag,
            inbound_threshold_block,
            outbound_threshold_flag,
            outbound_threshold_block,
        }
    }
}

/// Result of score evaluation.
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ScoreResult {
    #[pyo3(get, set)]
    pub total_score: f64,
    #[pyo3(get, set)]
    pub decision: Decision,
    #[pyo3(get, set)]
    pub match_count: usize,
}

#[pymethods]
impl ScoreResult {
    #[new]
    pub fn new(total_score: f64, decision: Decision, match_count: usize) -> Self {
        Self {
            total_score,
            decision,
            match_count,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_match_creation() {
        let m = Match::new(
            "INJ-D-001".to_string(),
            "heuristic".to_string(),
            "ignore previous".to_string(),
            5.0,
            0,
            15,
            0.0,
            0.0,
        );
        assert_eq!(m.signature_id, "INJ-D-001");
        assert_eq!(m.engine, "heuristic");
        assert_eq!(m.score, 5.0);
        assert_eq!(m.confidence, 0.0);
        assert_eq!(m.severity, 0.0);
    }

    #[test]
    fn test_match_with_confidence_constructor() {
        let m = Match::with_confidence(
            "TEST-001".to_string(),
            "classifier".to_string(),
            "injection attempt".to_string(),
            0.85,
            10.0,
            0,
            17,
        );
        assert_eq!(m.confidence, 0.85);
        assert_eq!(m.severity, 10.0);
        assert!((m.score - 8.5).abs() < 0.001);
    }

    #[test]
    fn test_decision_equality() {
        assert_eq!(Decision::Allow, Decision::Allow);
        assert_eq!(Decision::Flag, Decision::Flag);
        assert_eq!(Decision::Block, Decision::Block);
        assert_ne!(Decision::Allow, Decision::Block);
    }

    #[test]
    fn test_scoring_policy_creation() {
        let policy = ScoringPolicy::new(5.0, 15.0, 5.0, 15.0);
        assert_eq!(policy.inbound_threshold_flag, 5.0);
        assert_eq!(policy.inbound_threshold_block, 15.0);
    }

    #[test]
    fn test_score_result_creation() {
        let result = ScoreResult::new(10.0, Decision::Flag, 3);
        assert_eq!(result.total_score, 10.0);
        assert_eq!(result.decision, Decision::Flag);
        assert_eq!(result.match_count, 3);
    }

    #[test]
    fn test_match_serialization_roundtrip() {
        let m = Match::new(
            "INJ-D-001".to_string(),
            "heuristic".to_string(),
            "test".to_string(),
            5.0,
            0,
            4,
            0.0,
            0.0,
        );
        let json = serde_json::to_string(&m).unwrap();
        let deserialized: Match = serde_json::from_str(&json).unwrap();
        assert_eq!(deserialized.signature_id, m.signature_id);
        assert_eq!(deserialized.score, m.score);
    }

    #[test]
    fn test_decision_serialization_roundtrip() {
        for decision in [Decision::Allow, Decision::Flag, Decision::Block] {
            let json = serde_json::to_string(&decision).unwrap();
            let deserialized: Decision = serde_json::from_str(&json).unwrap();
            assert_eq!(deserialized, decision);
        }
    }

    #[test]
    fn test_scoring_policy_serialization_roundtrip() {
        let policy = ScoringPolicy::new(5.0, 15.0, 3.0, 10.0);
        let json = serde_json::to_string(&policy).unwrap();
        let deserialized: ScoringPolicy = serde_json::from_str(&json).unwrap();
        assert_eq!(
            deserialized.inbound_threshold_flag,
            policy.inbound_threshold_flag
        );
        assert_eq!(
            deserialized.outbound_threshold_block,
            policy.outbound_threshold_block
        );
    }
}
