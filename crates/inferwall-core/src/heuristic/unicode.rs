/// Unicode checks: invisible characters, homoglyphs, bidi overrides, zero-width.
use unicode_normalization::UnicodeNormalization;

/// Result of Unicode analysis.
#[derive(Debug, Clone)]
pub struct UnicodeAnalysis {
    pub invisible_chars: usize,
    pub homoglyphs_detected: bool,
    pub bidi_overrides: usize,
    pub zero_width_chars: usize,
    pub normalized_text: String,
}

/// Analyze text for Unicode-based obfuscation techniques.
pub fn analyze(text: &str) -> UnicodeAnalysis {
    let mut invisible_chars = 0;
    let mut bidi_overrides = 0;
    let mut zero_width_chars = 0;

    for ch in text.chars() {
        if is_invisible(ch) {
            invisible_chars += 1;
        }
        if is_bidi_override(ch) {
            bidi_overrides += 1;
        }
        if is_zero_width(ch) {
            zero_width_chars += 1;
        }
    }

    let normalized = normalize_text(text);
    let homoglyphs_detected = normalized != text && !text.is_ascii();

    UnicodeAnalysis {
        invisible_chars,
        homoglyphs_detected,
        bidi_overrides,
        zero_width_chars,
        normalized_text: normalized,
    }
}

/// Normalize text: NFKC normalization + strip invisible characters.
pub fn normalize_text(text: &str) -> String {
    text.nfkc()
        .filter(|c| !is_invisible(*c) || c.is_whitespace())
        .collect()
}

/// Strip invisible/zero-width characters from text.
pub fn strip_invisible(text: &str) -> String {
    text.chars()
        .filter(|c| !is_invisible(*c) || c.is_whitespace())
        .collect()
}

fn is_invisible(ch: char) -> bool {
    matches!(ch,
        '\u{200B}' | // zero-width space
        '\u{200C}' | // zero-width non-joiner
        '\u{200D}' | // zero-width joiner
        '\u{FEFF}' | // BOM / zero-width no-break space
        '\u{00AD}' | // soft hyphen
        '\u{034F}' | // combining grapheme joiner
        '\u{061C}' | // arabic letter mark
        '\u{180E}' | // mongolian vowel separator
        '\u{2060}' | // word joiner
        '\u{2061}'..='\u{2064}' | // invisible math operators
        '\u{FE00}'..='\u{FE0F}'   // variation selectors
    )
}

fn is_bidi_override(ch: char) -> bool {
    matches!(
        ch,
        '\u{202A}'..='\u{202E}' | // LRE, RLE, PDF, LRO, RLO
        '\u{2066}'..='\u{2069}'   // LRI, RLI, FSI, PDI
    )
}

fn is_zero_width(ch: char) -> bool {
    matches!(
        ch,
        '\u{200B}' | '\u{200C}' | '\u{200D}' | '\u{FEFF}' | '\u{2060}'
    )
}

/// Map common homoglyphs to their ASCII equivalents.
pub fn map_homoglyphs(text: &str) -> String {
    text.chars()
        .map(|c| match c {
            '\u{0430}' => 'a', // Cyrillic а
            '\u{0435}' => 'e', // Cyrillic е
            '\u{043E}' => 'o', // Cyrillic о
            '\u{0440}' => 'p', // Cyrillic р
            '\u{0441}' => 'c', // Cyrillic с
            '\u{0443}' => 'y', // Cyrillic у
            '\u{0445}' => 'x', // Cyrillic х
            '\u{0456}' => 'i', // Cyrillic і
            '\u{0455}' => 's', // Cyrillic ѕ
            '\u{04BB}' => 'h', // Cyrillic һ
            '\u{FF41}'..='\u{FF5A}' => (c as u32 - 0xFF41 + b'a' as u32) as u8 as char, // fullwidth
            '\u{FF21}'..='\u{FF3A}' => (c as u32 - 0xFF21 + b'A' as u32) as u8 as char, // fullwidth caps
            _ => c,
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_zero_width_chars() {
        let text = "he\u{200B}llo"; // zero-width space
        let analysis = analyze(text);
        assert_eq!(analysis.zero_width_chars, 1);
        assert_eq!(analysis.invisible_chars, 1);
    }

    #[test]
    fn test_detect_bidi_override() {
        let text = "hello\u{202E}dlrow"; // RLO
        let analysis = analyze(text);
        assert_eq!(analysis.bidi_overrides, 1);
    }

    #[test]
    fn test_clean_text_no_issues() {
        let analysis = analyze("hello world");
        assert_eq!(analysis.invisible_chars, 0);
        assert_eq!(analysis.bidi_overrides, 0);
        assert_eq!(analysis.zero_width_chars, 0);
    }

    #[test]
    fn test_normalize_strips_invisible() {
        let text = "he\u{200B}llo\u{FEFF}";
        let normalized = normalize_text(text);
        assert_eq!(normalized, "hello");
    }

    #[test]
    fn test_homoglyph_mapping() {
        let text = "\u{0430}\u{0435}"; // Cyrillic а + е
        let mapped = map_homoglyphs(text);
        assert_eq!(mapped, "ae");
    }

    #[test]
    fn test_fullwidth_mapping() {
        let text = "\u{FF48}\u{FF45}\u{FF4C}\u{FF4C}\u{FF4F}"; // fullwidth "hello"
        let mapped = map_homoglyphs(text);
        assert_eq!(mapped, "hello");
    }

    #[test]
    fn test_strip_invisible() {
        let text = "ig\u{200B}no\u{200C}re";
        let stripped = strip_invisible(text);
        assert_eq!(stripped, "ignore");
    }

    #[test]
    fn test_empty_input() {
        let analysis = analyze("");
        assert_eq!(analysis.invisible_chars, 0);
        assert_eq!(analysis.normalized_text, "");
    }
}
