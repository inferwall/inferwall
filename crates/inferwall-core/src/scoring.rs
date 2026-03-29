/// Scoring pipeline: accumulate points, threshold evaluation, early exit, decision.
use crate::types::{Decision, Match, ScoreResult, ScoringPolicy};

/// Evaluate a set of matches against a scoring policy.
/// Returns the score result with decision.
pub fn evaluate_score(matches: &[Match], policy: &ScoringPolicy, is_inbound: bool) -> ScoreResult {
    let total_score: f64 = matches.iter().map(|m| m.score).sum();
    let match_count = matches.len();

    let (flag_threshold, block_threshold) = if is_inbound {
        (
            policy.inbound_threshold_flag,
            policy.inbound_threshold_block,
        )
    } else {
        (
            policy.outbound_threshold_flag,
            policy.outbound_threshold_block,
        )
    };

    let decision = if total_score >= block_threshold {
        Decision::Block
    } else if total_score >= flag_threshold {
        Decision::Flag
    } else {
        Decision::Allow
    };

    ScoreResult::new(total_score, decision, match_count)
}

/// Check if score exceeds early exit threshold (skip downstream engines).
pub fn should_early_exit(matches: &[Match], early_exit_threshold: f64) -> bool {
    let total: f64 = matches.iter().map(|m| m.score).sum();
    total >= early_exit_threshold
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_match(sig_id: &str, score: f64) -> Match {
        Match::new(
            sig_id.to_string(),
            "heuristic".to_string(),
            "test".to_string(),
            score,
            0,
            4,
        )
    }

    fn default_policy() -> ScoringPolicy {
        ScoringPolicy::new(5.0, 15.0, 5.0, 10.0)
    }

    #[test]
    fn test_no_matches_allow() {
        let result = evaluate_score(&[], &default_policy(), true);
        assert_eq!(result.total_score, 0.0);
        assert_eq!(result.decision, Decision::Allow);
        assert_eq!(result.match_count, 0);
    }

    #[test]
    fn test_below_flag_threshold_allow() {
        let matches = vec![make_match("TEST-001", 3.0)];
        let result = evaluate_score(&matches, &default_policy(), true);
        assert_eq!(result.decision, Decision::Allow);
    }

    #[test]
    fn test_at_flag_threshold_flag() {
        let matches = vec![make_match("TEST-001", 5.0)];
        let result = evaluate_score(&matches, &default_policy(), true);
        assert_eq!(result.decision, Decision::Flag);
    }

    #[test]
    fn test_above_flag_below_block_flag() {
        let matches = vec![make_match("TEST-001", 5.0), make_match("TEST-002", 5.0)];
        let result = evaluate_score(&matches, &default_policy(), true);
        assert_eq!(result.total_score, 10.0);
        assert_eq!(result.decision, Decision::Flag);
    }

    #[test]
    fn test_at_block_threshold_block() {
        let matches = vec![make_match("TEST-001", 8.0), make_match("TEST-002", 7.0)];
        let result = evaluate_score(&matches, &default_policy(), true);
        assert_eq!(result.total_score, 15.0);
        assert_eq!(result.decision, Decision::Block);
    }

    #[test]
    fn test_above_block_threshold_block() {
        let matches = vec![make_match("TEST-001", 10.0), make_match("TEST-002", 10.0)];
        let result = evaluate_score(&matches, &default_policy(), true);
        assert_eq!(result.decision, Decision::Block);
    }

    #[test]
    fn test_outbound_thresholds() {
        // Outbound block threshold is 10 (lower than inbound 15)
        let matches = vec![make_match("DL-001", 5.0), make_match("DL-002", 5.0)];
        let result = evaluate_score(&matches, &default_policy(), false);
        assert_eq!(result.decision, Decision::Block);
    }

    #[test]
    fn test_score_accumulation() {
        let matches = vec![
            make_match("A", 3.0),
            make_match("B", 4.0),
            make_match("C", 5.0),
        ];
        let result = evaluate_score(&matches, &default_policy(), true);
        assert_eq!(result.total_score, 12.0);
        assert_eq!(result.match_count, 3);
    }

    #[test]
    fn test_early_exit_below_threshold() {
        let matches = vec![make_match("TEST-001", 10.0)];
        assert!(!should_early_exit(&matches, 25.0));
    }

    #[test]
    fn test_early_exit_above_threshold() {
        let matches = vec![make_match("TEST-001", 15.0), make_match("TEST-002", 12.0)];
        assert!(should_early_exit(&matches, 25.0));
    }

    #[test]
    fn test_early_exit_at_threshold() {
        let matches = vec![make_match("TEST-001", 25.0)];
        assert!(should_early_exit(&matches, 25.0));
    }

    #[test]
    fn test_early_exit_empty() {
        assert!(!should_early_exit(&[], 25.0));
    }
}
