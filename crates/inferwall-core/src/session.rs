// In-memory session store with TTL expiry.
// Concurrent access via std::sync for now (dashmap would be added for production).
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use pyo3::prelude::*;

const DEFAULT_TTL_SECS: u64 = 1800; // 30 minutes
const MAX_SESSIONS: usize = 100_000;
const MAX_HISTORY_PER_SESSION: usize = 500;
const MAX_TURNS_PER_SESSION: usize = 200;

#[derive(Clone, Debug)]
struct SessionData {
    cumulative_score: f64,
    turn_count: usize,
    matched_signatures: Vec<String>,
    _created_at: Instant,
    last_accessed: Instant,
    ttl: Duration,
}

/// Thread-safe in-memory session store.
#[pyclass]
#[derive(Clone)]
pub struct SessionStore {
    sessions: Arc<Mutex<HashMap<String, SessionData>>>,
    max_sessions: usize,
}

impl Default for SessionStore {
    fn default() -> Self {
        Self::new()
    }
}

#[pymethods]
impl SessionStore {
    #[new]
    pub fn new() -> Self {
        Self {
            sessions: Arc::new(Mutex::new(HashMap::new())),
            max_sessions: MAX_SESSIONS,
        }
    }

    /// Create a new session. Returns false if max sessions reached.
    #[pyo3(signature = (session_id, ttl_secs=None))]
    pub fn create(&self, session_id: String, ttl_secs: Option<u64>) -> bool {
        let mut sessions = self.sessions.lock().unwrap();
        if sessions.len() >= self.max_sessions {
            return false;
        }
        let ttl = Duration::from_secs(ttl_secs.unwrap_or(DEFAULT_TTL_SECS));
        let now = Instant::now();
        sessions.insert(
            session_id,
            SessionData {
                cumulative_score: 0.0,
                turn_count: 0,
                matched_signatures: Vec::new(),
                _created_at: now,
                last_accessed: now,
                ttl,
            },
        );
        true
    }

    /// Update session with new scan results. Returns false if session not found.
    pub fn update(&self, session_id: &str, score: f64, matched_sigs: Vec<String>) -> bool {
        let mut sessions = self.sessions.lock().unwrap();
        if let Some(session) = sessions.get_mut(session_id) {
            if session.turn_count >= MAX_TURNS_PER_SESSION {
                return false; // Max turns reached
            }
            session.cumulative_score += score;
            session.turn_count += 1;
            session.last_accessed = Instant::now();

            // Append signatures with FIFO eviction
            for sig in matched_sigs {
                if session.matched_signatures.len() >= MAX_HISTORY_PER_SESSION {
                    session.matched_signatures.remove(0);
                }
                session.matched_signatures.push(sig);
            }
            true
        } else {
            false
        }
    }

    /// Get session state. Returns (score, turn_count, sig_history) or None.
    pub fn get(&self, session_id: &str) -> Option<(f64, usize, Vec<String>)> {
        let sessions = self.sessions.lock().unwrap();
        sessions.get(session_id).map(|s| {
            (
                s.cumulative_score,
                s.turn_count,
                s.matched_signatures.clone(),
            )
        })
    }

    /// Delete a session.
    pub fn delete(&self, session_id: &str) -> bool {
        let mut sessions = self.sessions.lock().unwrap();
        sessions.remove(session_id).is_some()
    }

    /// Clean up expired sessions. Returns number removed.
    pub fn cleanup_expired(&self) -> usize {
        let mut sessions = self.sessions.lock().unwrap();
        let now = Instant::now();
        let before = sessions.len();
        sessions.retain(|_, s| now.duration_since(s.last_accessed) < s.ttl);
        before - sessions.len()
    }

    /// Get current session count.
    pub fn session_count(&self) -> usize {
        self.sessions.lock().unwrap().len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_session() {
        let store = SessionStore::new();
        assert!(store.create("sess-1".to_string(), None));
        assert_eq!(store.session_count(), 1);
    }

    #[test]
    fn test_get_session() {
        let store = SessionStore::new();
        store.create("sess-1".to_string(), None);
        let state = store.get("sess-1");
        assert!(state.is_some());
        let (score, turns, sigs) = state.unwrap();
        assert_eq!(score, 0.0);
        assert_eq!(turns, 0);
        assert!(sigs.is_empty());
    }

    #[test]
    fn test_get_nonexistent_session() {
        let store = SessionStore::new();
        assert!(store.get("nonexistent").is_none());
    }

    #[test]
    fn test_update_session() {
        let store = SessionStore::new();
        store.create("sess-1".to_string(), None);
        assert!(store.update("sess-1", 8.0, vec!["INJ-D-001".to_string()]));
        let (score, turns, sigs) = store.get("sess-1").unwrap();
        assert_eq!(score, 8.0);
        assert_eq!(turns, 1);
        assert_eq!(sigs, vec!["INJ-D-001"]);
    }

    #[test]
    fn test_cumulative_score() {
        let store = SessionStore::new();
        store.create("sess-1".to_string(), None);
        store.update("sess-1", 5.0, vec!["SIG-A".to_string()]);
        store.update("sess-1", 3.0, vec!["SIG-B".to_string()]);
        let (score, turns, sigs) = store.get("sess-1").unwrap();
        assert_eq!(score, 8.0);
        assert_eq!(turns, 2);
        assert_eq!(sigs.len(), 2);
    }

    #[test]
    fn test_delete_session() {
        let store = SessionStore::new();
        store.create("sess-1".to_string(), None);
        assert!(store.delete("sess-1"));
        assert!(store.get("sess-1").is_none());
        assert!(!store.delete("sess-1")); // Already deleted
    }

    #[test]
    fn test_max_turns_enforced() {
        let store = SessionStore::new();
        store.create("sess-1".to_string(), None);
        for i in 0..MAX_TURNS_PER_SESSION {
            assert!(store.update("sess-1", 1.0, vec![format!("SIG-{}", i)]));
        }
        // Should fail after max turns
        assert!(!store.update("sess-1", 1.0, vec!["SIG-EXTRA".to_string()]));
    }

    #[test]
    fn test_cleanup_expired() {
        let store = SessionStore::new();
        // Create with very short TTL
        store.create("sess-1".to_string(), Some(0));
        std::thread::sleep(std::time::Duration::from_millis(10));
        let removed = store.cleanup_expired();
        assert_eq!(removed, 1);
        assert_eq!(store.session_count(), 0);
    }

    #[test]
    fn test_session_history_fifo_eviction() {
        let store = SessionStore::new();
        store.create("sess-1".to_string(), None);
        // Add many sigs per turn to fill history before hitting turn limit
        let sigs_per_turn = 10;
        let turns_needed = (MAX_HISTORY_PER_SESSION + 10) / sigs_per_turn;
        for i in 0..turns_needed {
            let sigs: Vec<String> = (0..sigs_per_turn)
                .map(|j| format!("SIG-{}-{}", i, j))
                .collect();
            store.update("sess-1", 0.1, sigs);
        }
        let (_, _, sigs) = store.get("sess-1").unwrap();
        assert_eq!(sigs.len(), MAX_HISTORY_PER_SESSION);
        // First entries should have been evicted
        assert!(!sigs.contains(&"SIG-0-0".to_string()));
    }
}
