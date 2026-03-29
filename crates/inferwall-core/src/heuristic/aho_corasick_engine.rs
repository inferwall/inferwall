// Aho-Corasick multi-pattern substring matching — fastest pattern type.

/// Find first occurrence of a substring in text. Returns (matched_text, offset, length).
pub fn find_match(
    text: &str,
    pattern: &str,
    case_insensitive: bool,
) -> Option<(String, usize, usize)> {
    let ac = aho_corasick::AhoCorasickBuilder::new()
        .ascii_case_insensitive(case_insensitive)
        .build([pattern])
        .ok()?;

    let m = ac.find(text)?;
    let matched = &text[m.start()..m.end()];
    Some((matched.to_string(), m.start(), m.end() - m.start()))
}

/// Find all occurrences of multiple patterns in text.
pub fn find_all_matches(
    text: &str,
    patterns: &[&str],
    case_insensitive: bool,
) -> Vec<(usize, String, usize, usize)> {
    let Ok(ac) = aho_corasick::AhoCorasickBuilder::new()
        .ascii_case_insensitive(case_insensitive)
        .build(patterns)
    else {
        return Vec::new();
    };

    ac.find_iter(text)
        .map(|m| {
            let matched = &text[m.start()..m.end()];
            (
                m.pattern().as_usize(),
                matched.to_string(),
                m.start(),
                m.end() - m.start(),
            )
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_exact_substring_match() {
        let result = find_match("hello world", "world", false);
        assert!(result.is_some());
        let (matched, offset, len) = result.unwrap();
        assert_eq!(matched, "world");
        assert_eq!(offset, 6);
        assert_eq!(len, 5);
    }

    #[test]
    fn test_case_insensitive_substring() {
        let result = find_match("IGNORE PREVIOUS", "ignore previous", true);
        assert!(result.is_some());
        assert_eq!(result.unwrap().0, "IGNORE PREVIOUS");
    }

    #[test]
    fn test_case_sensitive_no_match() {
        let result = find_match("HELLO", "hello", false);
        assert!(result.is_none());
    }

    #[test]
    fn test_empty_text() {
        let result = find_match("", "test", false);
        assert!(result.is_none());
    }

    #[test]
    fn test_multi_pattern_match() {
        let patterns = vec!["ignore", "previous", "instructions"];
        let results = find_all_matches("ignore previous instructions", &patterns, false);
        assert_eq!(results.len(), 3);
    }

    #[test]
    fn test_multi_pattern_partial_match() {
        let patterns = vec!["hello", "world", "missing"];
        let results = find_all_matches("hello world", &patterns, false);
        assert_eq!(results.len(), 2);
    }

    #[test]
    fn test_multi_pattern_no_match() {
        let patterns = vec!["abc", "xyz"];
        let results = find_all_matches("hello world", &patterns, false);
        assert!(results.is_empty());
    }
}
