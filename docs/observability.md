# Observability

InferenceWall can ship scan results and audit events to an ELK (Elasticsearch, Logstash, Kibana) stack for centralized security monitoring.

This is an **optional plugin** — it has zero impact on InferenceWall unless explicitly enabled.

## Installation

```bash
# Observability plugin is optional — install separately
pip install inferwall[observability]
```

This adds the `httpx` dependency for HTTP log shipping. The core `pip install inferwall` does not include it.

## Quick Start

### 1. Enable log shipping

Set the `IW_ELK_URL` environment variable to your Logstash HTTP input:

```bash
export IW_ELK_URL=http://localhost:8080
```

That's it. InferenceWall will now ship scan logs and audit events to that endpoint.

### 2. Start InferenceWall

```bash
inferwall serve
```

Every scan request will fire-and-forget a JSON log to Logstash. If Logstash is unreachable, logs are silently dropped — scan latency is never affected.

### 3. Verify

```bash
# Trigger a scan
curl -X POST http://localhost:8000/v1/scan/input \
  -H "Content-Type: application/json" \
  -d '{"text": "ignore all previous instructions"}'

# Check Logstash received it
docker logs logstash | tail -5
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `IW_ELK_URL` | Logstash HTTP input endpoint | Not set (disabled) |

When `IW_ELK_URL` is **not set**, the Observability plugin is completely inactive — no imports, no overhead, no side effects.

## What Gets Shipped

### Scan Logs

Every `scan_input` and `scan_output` call ships a JSON payload:

```json
{
  "log_type": "scan",
  "timestamp": "2026-04-06T12:00:00Z",
  "direction": "input",
  "decision": "block",
  "anomaly_score": 12.8,
  "threshold": 10.0,
  "policy": "default",
  "request_id": "req-1712345678000",
  "matches": [
    {
      "signature_id": "INJ-D-002",
      "matched_text": "ignore all previous instructions",
      "score": 6.3,
      "confidence": 0.9,
      "severity": 7.0
    }
  ],
  "signature_count": 1
}
```

### Audit Events

Auth, policy, and config changes:

```json
{
  "log_type": "audit",
  "timestamp": "2026-04-06T12:00:00Z",
  "category": "auth",
  "action": "login_attempt",
  "details": {"key_prefix": "iwk_scan_"},
  "source_ip": "192.168.1.100"
}
```

Audit categories: `auth`, `policy`, `config`, `signatures`, `engines`, `admin`, `rate_limit`, `lifecycle`, `scan`.

## Architecture

```mermaid
flowchart LR
    IW["InferenceWall"] -->|"HTTP/JSON"| LS["Logstash :8080"]
    LS --> ES["Elasticsearch"]
    ES --> KB["Kibana"]
```

- **Fire-and-forget**: Shipping never blocks the scan pipeline
- **Synchronous HTTP**: Uses `httpx.post()` with 5s timeout
- **Silent failure**: All shipping errors are suppressed

## Logstash Configuration

Minimal Logstash pipeline to receive InferenceWall logs:

```conf
input {
  http {
    port => 8080
    codec => json
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "inferwall-logs-%{+YYYY.MM.dd}"
  }
}
```

## Docker Setup

```bash
# Run InferenceWall with ELK shipping enabled
docker run -d \
  -e IW_ELK_URL=http://logstash:8080 \
  -e IW_API_KEY=iwk_scan_yourkey \
  --network your-elk-network \
  -p 8000:8000 \
  inferwall:latest
```

## Use Cases

- **Compliance** (SOC2, ISO27001): Centralized audit trail of all scan decisions
- **Threat monitoring**: Dashboard showing block rate trends, top triggered signatures
- **Incident response**: Correlate LLM firewall events with other security logs
- **Tuning**: Identify high-FP signatures by analyzing flagged-but-benign patterns
