# API Reference

## Scan Endpoints

### POST /v1/scan/input
Scan user input for threats.

**Request:**
```json
{"text": "user prompt here", "session_id": "optional-session-id"}
```

**Response:**
```json
{
  "decision": "allow|flag|block",
  "score": 7.2,
  "matches": [
    {
      "signature_id": "INJ-D-002",
      "matched_text": "ignore all previous instructions",
      "score": 6.3,
      "confidence": 0.9,
      "severity": 7.0
    }
  ],
  "request_id": "req-1712345678000"
}
```

> Score = confidence (0.0-1.0) x severity (1-15). Decision thresholds: flag >= 4.0, block >= 10.0 (inbound).

### POST /v1/scan/output
Scan LLM output for data leakage.

### POST /v1/analyze/input
Analyze input with PII detection.

### POST /v1/analyze/output
Analyze output with PII detection.

## Health Endpoints

### GET /v1/health
Full health status with signature count.

### GET /v1/health/live
Liveness probe (K8s).

### GET /v1/health/ready
Readiness probe (K8s).

## Signature Endpoints

### GET /v1/signatures
List all loaded signatures.

### GET /v1/signatures/{id}
Get signature details by ID.

## Session Endpoints

### POST /v1/sessions
Create a session. Body: `{"session_id": "...", "ttl_secs": 1800}`

### GET /v1/sessions/{id}
Get session state.

### DELETE /v1/sessions/{id}
Delete a session.

## Policy Endpoints

### GET /v1/policies
List loaded policy profiles.

## Auth Endpoints

### POST /v1/auth/login
Login with admin key, sets httpOnly cookie. Body: `{"key": "..."}`

### POST /v1/auth/logout
Clear session cookie.

### GET /v1/auth/check
Check current session validity.

## Admin Endpoints

### POST /v1/admin/reload
Hot-reload signatures and policies.

### GET /v1/admin/stats
System statistics.

### GET /v1/config
Runtime configuration.

## Model Management CLI

These commands manage ML model downloads for the Standard and Full profiles.

| Command | Description |
|---------|-------------|
| `inferwall models install --profile standard` | Install deps + download models (recommended) |
| `inferwall models download --profile standard` | Download models only (~1GB for standard) |
| `inferwall models list` | List downloaded models |
| `inferwall models status` | Show download status of all models |
