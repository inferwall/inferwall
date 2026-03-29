// Character-level entropy estimation for detecting adversarial suffixes and gibberish.

/// Calculate Shannon entropy of a string (bits per character).
pub fn calculate_entropy(text: &str) -> f64 {
    if text.is_empty() {
        return 0.0;
    }

    let mut freq = [0u32; 256];
    let len = text.len() as f64;

    for byte in text.bytes() {
        freq[byte as usize] += 1;
    }

    freq.iter()
        .filter(|&&count| count > 0)
        .map(|&count| {
            let p = count as f64 / len;
            -p * p.log2()
        })
        .sum()
}

/// Check if text has abnormal entropy (indicating adversarial content).
/// Normal English text: ~3.5-4.5 bits/char
/// Adversarial suffixes: often >5.5 or <2.0 bits/char
pub fn is_abnormal_entropy(text: &str, min_threshold: f64, max_threshold: f64) -> bool {
    if text.len() < 20 {
        return false; // Too short for reliable entropy estimation
    }
    let entropy = calculate_entropy(text);
    entropy < min_threshold || entropy > max_threshold
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_string_entropy() {
        assert_eq!(calculate_entropy(""), 0.0);
    }

    #[test]
    fn test_single_char_repeated() {
        assert_eq!(calculate_entropy("aaaaaa"), 0.0);
    }

    #[test]
    fn test_two_chars_equal_frequency() {
        let entropy = calculate_entropy("abababab");
        assert!((entropy - 1.0).abs() < 0.01); // Should be ~1 bit
    }

    #[test]
    fn test_normal_english_entropy() {
        let entropy =
            calculate_entropy("The quick brown fox jumps over the lazy dog near the river bank");
        assert!(entropy > 3.0 && entropy < 5.0, "Got entropy: {}", entropy);
    }

    #[test]
    fn test_random_looking_high_entropy() {
        let entropy = calculate_entropy("x9$kL!m@p#2&qR*wZ^eT%fGhJnBvCy");
        assert!(entropy > 4.0, "Got entropy: {}", entropy);
    }

    #[test]
    fn test_abnormal_entropy_detection() {
        // Repeated chars = very low entropy
        assert!(!is_abnormal_entropy("aaaa", 2.0, 5.5)); // Too short
        assert!(is_abnormal_entropy("aaaaaaaaaaaaaaaaaaaaaa", 2.0, 5.5)); // Low entropy

        // Normal text should not be flagged
        assert!(!is_abnormal_entropy(
            "The quick brown fox jumps over the lazy dog near the river",
            2.0,
            5.5
        ));
    }

    #[test]
    fn test_short_text_not_flagged() {
        assert!(!is_abnormal_entropy("short", 2.0, 5.5));
    }
}
