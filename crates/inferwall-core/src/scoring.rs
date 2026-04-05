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

/// Confidence-weighted scoring: max-primary + diminishing corroboration.
///
/// Takes the highest-scoring match as primary signal and adds diminishing
/// contributions from corroborating matches. Two weak signals no longer
/// compound into a block decision.
pub fn evaluate_score_v2(
    matches: &[Match],
    policy: &ScoringPolicy,
    is_inbound: bool,
) -> ScoreResult {
    if matches.is_empty() {
        return ScoreResult::new(0.0, Decision::Allow, 0);
    }

    // Find primary signal (highest score = confidence * severity)
    let (primary_idx, primary) = matches
        .iter()
        .enumerate()
        .max_by(|(_, a), (_, b)| {
            a.score
                .partial_cmp(&b.score)
                .unwrap_or(std::cmp::Ordering::Equal)
        })
        .unwrap();

    // Corroboration: distinct signatures with diminishing returns
    let corroboration: f64 = matches
        .iter()
        .enumerate()
        .filter(|(i, m)| *i != primary_idx && m.signature_id != primary.signature_id)
        .enumerate()
        .map(|(rank, (_, m))| m.confidence * 0.3 * primary.severity / (1.0 + rank as f64))
        .sum();

    let effective_score = primary.score + corroboration;

    let (flag_t, block_t) = if is_inbound {
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

    let decision = if effective_score >= block_t {
        Decision::Block
    } else if effective_score >= flag_t {
        Decision::Flag
    } else {
        Decision::Allow
    };

    ScoreResult::new(effective_score, decision, matches.len())
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
            0.0,
            0.0,
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

    // --- v2 helpers and tests ---

    fn make_confident_match(sig_id: &str, confidence: f64, severity: f64) -> Match {
        Match::with_confidence(
            sig_id.to_string(),
            "heuristic".to_string(),
            "matched".to_string(),
            confidence,
            severity,
            0,
            7,
        )
    }

    fn default_policy_v2() -> ScoringPolicy {
        ScoringPolicy::new(4.0, 10.0, 3.0, 7.0)
    }

    #[test]
    fn test_v2_empty_matches_allows() {
        let matches: Vec<Match> = vec![];
        let policy = default_policy_v2();
        let result = evaluate_score_v2(&matches, &policy, true);
        assert_eq!(result.decision, Decision::Allow);
        assert_eq!(result.total_score, 0.0);
    }

    #[test]
    fn test_v2_single_high_confidence_blocks() {
        // 0.90 * 12 = 10.8 >= block(10.0)
        let matches = vec![make_confident_match("SIG-001", 0.90, 12.0)];
        let policy = default_policy_v2();
        let result = evaluate_score_v2(&matches, &policy, true);
        assert_eq!(result.decision, Decision::Block);
        assert!((result.total_score - 10.8).abs() < 0.01);
    }

    #[test]
    fn test_v2_single_low_confidence_allows() {
        // 0.45 * 8 = 3.6 < flag(4.0)
        let matches = vec![make_confident_match("SIG-001", 0.45, 8.0)];
        let policy = default_policy_v2();
        let result = evaluate_score_v2(&matches, &policy, true);
        assert_eq!(result.decision, Decision::Allow);
        assert!((result.total_score - 3.6).abs() < 0.01);
    }

    #[test]
    fn test_v2_two_weak_signals_dont_block() {
        // Primary: 0.45*8=3.6, Corr: 0.45*0.3*8=1.08
        // Total: 4.68 -> flag, NOT block
        let matches = vec![
            make_confident_match("SIG-001", 0.45, 8.0),
            make_confident_match("SIG-002", 0.45, 8.0),
        ];
        let policy = default_policy_v2();
        let result = evaluate_score_v2(&matches, &policy, true);
        assert_eq!(result.decision, Decision::Flag);
        assert!(result.total_score < 10.0, "Two weak signals must not block");
    }

    #[test]
    fn test_v2_critical_signature_blocks_alone() {
        // CSAM: 0.90 * 15 = 13.5 >= block(10.0)
        let matches = vec![make_confident_match("CS-T-005", 0.90, 15.0)];
        let policy = default_policy_v2();
        let result = evaluate_score_v2(&matches, &policy, true);
        assert_eq!(result.decision, Decision::Block);
    }

    #[test]
    fn test_v2_diminishing_corroboration() {
        // Primary: 0.70*8=5.6
        // Corr1: 0.70*0.3*8/1 = 1.68
        // Corr2: 0.60*0.3*8/2 = 0.72
        // Total: 8.0 -> flag
        let matches = vec![
            make_confident_match("SIG-001", 0.70, 8.0),
            make_confident_match("SIG-002", 0.70, 8.0),
            make_confident_match("SIG-003", 0.60, 8.0),
        ];
        let policy = default_policy_v2();
        let result = evaluate_score_v2(&matches, &policy, true);
        assert!(
            result.total_score < 10.0,
            "Diminishing returns must prevent block"
        );
        assert!(
            result.total_score >= 4.0,
            "Three medium signals should at least flag"
        );
    }

    #[test]
    fn test_v2_outbound_uses_outbound_thresholds() {
        // 0.90*8=7.2 >= outbound_block(7.0)
        let matches = vec![make_confident_match("SIG-001", 0.90, 8.0)];
        let policy = default_policy_v2();
        let result = evaluate_score_v2(&matches, &policy, false);
        assert_eq!(result.decision, Decision::Block);
    }
}
