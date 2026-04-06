# SIEM Integration — ELK Testing Facility

InferenceWall can ship scan results and audit events to an external ELK (Elasticsearch, Logstash, Kibana) stack for SIEM-style analysis and testing.

## Quick Start

1. **Start an ELK stack** (using Docker Compose):
   ```bash
   # Example docker-compose.yml for ELK
   wget https://raw.githubusercontent.com/inferwall/inferwall/main/docs/examples/elk-docker-compose.yml
   docker compose up -d
   ```

2. **Point inferwall to Logstash**:
   ```bash
   export IW_ELK_URL=http://localhost:8080
   ```

3. **Run inferwall**:
   ```bash
   inferwall serve
   # or with Docker
   docker run -e IW_ELK_URL=http://host.docker.internal:8080 -p 8000:8000 inferwall
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
# Build inferwall image
docker build -t inferwall:latest .

# Start ELK stack
docker compose up -d

# Start inferwall with ELK integration
docker run -d \
  -e IW_ELK_URL=http://logstash:8080 \
  --network elk-network \
  -p 8000:8000 \
  inferwall:latest
```
