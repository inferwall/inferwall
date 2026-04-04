# SIEM Integration — ELK Testing Facility

InferenceWall can ship scan results and audit events to an external ELK (Elasticsearch, Logstash, Kibana) stack for SIEM-style analysis and testing.

## Quick Start

1. **Start the ELK testing facility** (located at `~/workspace/cybermancer/elk-siem`):
   ```bash
   cd ~/workspace/cybermancer/elk-siem
   docker compose up -d
   ```

2. **Point inferwall to Logstash**:
   ```bash
   export IW_ELK_URL=http://localhost:8080
   ```

3. **Run inferwall and generate traffic**:
   ```bash
   cd ~/workspace/cybermancer/aiaf/inferwall
   ./start.sh dev
   ./start.sh e2e
   ```

4. **Open Kibana** at http://localhost:5601 and import the dashboard from `elk-siem/kibana/dashboards/inferwall-dashboard.ndjson`.

## Configuration

| Environment Variable | Description | Example |
|----------------------|-------------|---------|
| `IW_ELK_URL` | Logstash HTTP input endpoint | `http://localhost:8080` |

When `IW_ELK_URL` is set, inferwall automatically ships:
- **Scan logs** — decision, score, matched signatures, request metadata
- **Audit events** — auth, policy changes, config changes, etc.

Shipping is fire-and-forget: failures are silently ignored so the scan path is never blocked.

## Architecture

```
inferwall ──HTTP/JSON──> Logstash (8080) ──> Elasticsearch ──> Kibana
       │
       └── Filebeat (optional, file-based logs)
```

## Indices

Events land in daily indices: `inferwall-logs-YYYY.MM.dd`

## Dashboards

The provided Kibana dashboard includes:
- **Scans by Decision** — pie chart of allow / flag / block
- **Top Signatures** — most frequently matched signatures
- **Anomaly Score Over Time** — trend line of average scores

## Docker Compose (inferwall + ELK)

To run inferwall inside Docker on the same network:

```bash
cd ~/workspace/cybermancer/aiaf/inferwall
docker build -t inferwall:latest .

cd ~/workspace/cybermancer/elk-siem
docker compose up -d
docker compose -f compose-inferwall.yml up -d
```
