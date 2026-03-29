// Compiled regex matching — ReDoS-immune (uses Rust regex crate, linear time).

/// Find first match of pattern in text. Returns (matched_text, offset, length).
pub fn find_match(
    text: &str,
    pattern: &str,
    case_insensitive: bool,
) -> Option<(String, usize, usize)> {
    let full_pattern = if case_insensitive && !pattern.starts_with("(?i)") {
        format!("(?i){}", pattern)
    } else {
        pattern.to_string()
    };

    let re = regex::Regex::new(&full_pattern).ok()?;
    let m = re.find(text)?;
    Some((m.as_str().to_string(), m.start(), m.end() - m.start()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_regex_match() {
        let result = find_match("hello world", r"world", false);
        assert!(result.is_some());
        let (matched, offset, len) = result.unwrap();
        assert_eq!(matched, "world");
        assert_eq!(offset, 6);
        assert_eq!(len, 5);
    }

    #[test]
    fn test_case_insensitive_match() {
        let result = find_match("HELLO WORLD", r"hello", true);
        assert!(result.is_some());
        assert_eq!(result.unwrap().0, "HELLO");
    }

    #[test]
    fn test_no_match() {
        let result = find_match("hello world", r"xyz", false);
        assert!(result.is_none());
    }

    #[test]
    fn test_empty_text() {
        let result = find_match("", r"test", false);
        assert!(result.is_none());
    }

    #[test]
    fn test_complex_pattern() {
        let result = find_match(
            "ignore previous instructions",
            r"ignore\s+previous\s+instructions",
            false,
        );
        assert!(result.is_some());
    }

    #[test]
    fn test_invalid_regex_returns_none() {
        let result = find_match("test", r"[invalid", false);
        assert!(result.is_none());
    }

    #[test]
    fn test_inline_case_insensitive_flag() {
        let result = find_match("HELLO", "(?i)hello", false);
        assert!(result.is_some());
    }

    #[test]
    fn test_no_duplicate_case_flag() {
        // If pattern already has (?i), don't add another
        let result = find_match("HELLO", "(?i)hello", true);
        assert!(result.is_some());
    }
}
