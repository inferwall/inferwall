use pyo3::prelude::*;

pub mod heuristic;
pub mod preprocess;
pub mod scoring;
pub mod session;
pub mod types;

use heuristic::{HeuristicPattern, HeuristicSignature};
use preprocess::PreprocessConfig;

/// Combined scan: preprocess text + run heuristic signatures.
/// Single Rust call to avoid redundant Python-Rust boundary crossings.
#[pyfunction]
#[pyo3(signature = (text, signatures, preprocess=true))]
fn scan_heuristic_with_preprocess(
    text: &str,
    signatures: Vec<PyHeuristicSignature>,
    preprocess: bool,
) -> (PyPreprocessResult, Vec<types::Match>) {
    let config = PreprocessConfig::default();

    // Step 1: Preprocess
    let preprocess_result = if preprocess {
        self::preprocess::preprocess(text, &config)
    } else {
        self::preprocess::PreprocessResult {
            original_text: text.to_string(),
            processed_text: text.to_string(),
            encodings_found: Vec::new(),
            invisible_chars_removed: 0,
            homoglyphs_mapped: false,
            was_truncated: false,
        }
    };

    // Step 2: Convert signatures and scan
    let rust_sigs: Vec<HeuristicSignature> = signatures.iter().map(|s| s.to_rust()).collect();
    let matches = heuristic::scan_heuristic(&preprocess_result.processed_text, &rust_sigs);

    let py_result = PyPreprocessResult {
        original_text: preprocess_result.original_text,
        processed_text: preprocess_result.processed_text,
        encodings_found: preprocess_result.encodings_found,
        invisible_chars_removed: preprocess_result.invisible_chars_removed,
        homoglyphs_mapped: preprocess_result.homoglyphs_mapped,
        was_truncated: preprocess_result.was_truncated,
    };

    (py_result, matches)
}

/// Evaluate anomaly score against policy thresholds.
#[pyfunction]
fn evaluate_score(
    matches: Vec<types::Match>,
    policy: types::ScoringPolicy,
    is_inbound: bool,
) -> types::ScoreResult {
    scoring::evaluate_score(&matches, &policy, is_inbound)
}

/// Check if early exit threshold is exceeded.
#[pyfunction]
fn should_early_exit(matches: Vec<types::Match>, threshold: f64) -> bool {
    scoring::should_early_exit(&matches, threshold)
}

// --- PyO3 wrapper types for crossing the boundary ---

#[pyclass]
#[derive(Clone)]
struct PyHeuristicSignature {
    #[pyo3(get)]
    id: String,
    #[pyo3(get)]
    patterns: Vec<PyHeuristicPattern>,
    #[pyo3(get)]
    condition: String,
    #[pyo3(get)]
    anomaly_points: f64,
}

#[pymethods]
impl PyHeuristicSignature {
    #[new]
    fn new(
        id: String,
        patterns: Vec<PyHeuristicPattern>,
        condition: String,
        anomaly_points: f64,
    ) -> Self {
        Self {
            id,
            patterns,
            condition,
            anomaly_points,
        }
    }
}

impl PyHeuristicSignature {
    fn to_rust(&self) -> HeuristicSignature {
        HeuristicSignature {
            id: self.id.clone(),
            patterns: self.patterns.iter().map(|p| p.to_rust()).collect(),
            condition: self.condition.clone(),
            anomaly_points: self.anomaly_points,
        }
    }
}

#[pyclass]
#[derive(Clone)]
struct PyHeuristicPattern {
    #[pyo3(get)]
    pattern_type: String,
    #[pyo3(get)]
    value: String,
    #[pyo3(get)]
    case_insensitive: bool,
}

#[pymethods]
impl PyHeuristicPattern {
    #[new]
    fn new(pattern_type: String, value: String, case_insensitive: bool) -> Self {
        Self {
            pattern_type,
            value,
            case_insensitive,
        }
    }
}

impl PyHeuristicPattern {
    fn to_rust(&self) -> HeuristicPattern {
        HeuristicPattern {
            pattern_type: self.pattern_type.clone(),
            value: self.value.clone(),
            case_insensitive: self.case_insensitive,
        }
    }
}

#[pyclass]
#[derive(Clone)]
struct PyPreprocessResult {
    #[pyo3(get)]
    original_text: String,
    #[pyo3(get)]
    processed_text: String,
    #[pyo3(get)]
    encodings_found: Vec<String>,
    #[pyo3(get)]
    invisible_chars_removed: usize,
    #[pyo3(get)]
    homoglyphs_mapped: bool,
    #[pyo3(get)]
    was_truncated: bool,
}

/// InferenceWall Rust core extension.
#[pymodule]
fn inferwall_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", "0.1.5")?;
    m.add_class::<types::Match>()?;
    m.add_class::<types::Decision>()?;
    m.add_class::<types::ScoringPolicy>()?;
    m.add_class::<types::ScoreResult>()?;
    m.add_class::<PyHeuristicSignature>()?;
    m.add_class::<PyHeuristicPattern>()?;
    m.add_class::<PyPreprocessResult>()?;
    m.add_class::<session::SessionStore>()?;
    m.add_function(wrap_pyfunction!(scan_heuristic_with_preprocess, m)?)?;
    m.add_function(wrap_pyfunction!(evaluate_score, m)?)?;
    m.add_function(wrap_pyfunction!(should_early_exit, m)?)?;
    Ok(())
}
