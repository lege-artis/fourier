# Log Infrastructure Architecture
**Project:** VibeCodeProjects — Hybrid Log Stack
**Version:** 1.0.0 | **Date:** 2026-03-22
**Status:** Design complete — implementation pending

---

## Architecture Decision

**Pattern: Hybrid log stack** — two complementary stores with distinct roles:

| Store | Role | Sources |
|-------|------|---------|
| MongoDB `vibedev.logs` | App runtime events (lightweight, flexible schema) | Node.js, React, Python app instances |
| Elasticsearch `ci-logs-*`, `test-results-*`, `db-slow-*` | Structured CI/test results + DB diagnostics (searchable, dashboarded) | GitHub Actions, Playwright, cargo/sbt/fpc/gfortran, PG slow queries, MongoDB slow ops |

**Shipper:** Fluent Bit (replaces Logstash — 10× lighter, Docker-native)
**Dashboard:** Kibana (ES only)

---

## Component Topology

```
┌─────────────────────────────────────────────────────────────────┐
│  LOG SOURCES                                                    │
│                                                                 │
│  Node.js/React ──────────────────────────────► MongoDB          │
│  Python scripts ─────────────────────────────► vibedev.logs     │
│                                                                 │
│  GitHub Actions ──► Fluent Bit ──────────────► Elasticsearch    │
│  Playwright ──────► (port 24224) ────────────► ci-logs-*        │
│  cargo/sbt/fpc ───►                          ► test-results-*   │
│  PG slow queries ─►                          ► db-slow-*        │
│  MongoDB slow ops ►                                             │
│                                               Kibana (5601)     │
│                                               └── dashboards    │
└─────────────────────────────────────────────────────────────────┘
```

---

## MongoDB Log Schema

**Database:** `vibedev`
**Collection:** `logs`

```json
{
  "_id": "ObjectId",
  "timestamp": "ISODate",
  "level": "info|warn|error|debug",
  "source": "node-app|react-frontend|python-script",
  "app": "string (application/service name)",
  "session_id": "string (development session UUID)",
  "message": "string",
  "metadata": {
    "host": "string",
    "pid": "number",
    "env": "development|test|staging",
    "version": "string"
  },
  "context": {}
}
```

**Indexes:**
```js
db.logs.createIndex({ timestamp: -1 })
db.logs.createIndex({ level: 1, timestamp: -1 })
db.logs.createIndex({ app: 1, timestamp: -1 })
db.logs.createIndex({ session_id: 1 })
```

**Retention:** 30 days rolling (TTL index on timestamp)
```js
db.logs.createIndex({ timestamp: 1 }, { expireAfterSeconds: 2592000 })
```

---

## Elasticsearch Index Patterns

### ci-logs-{YYYY.MM.DD}
GitHub Actions job-level log lines.
```json
{
  "@timestamp": "ISO8601",
  "workflow": "ci-heartbeat",
  "job": "cpp-build-test|rust-build-test|...",
  "step": "string",
  "level": "info|error|warning",
  "message": "string",
  "run_id": "number",
  "run_number": "number",
  "conclusion": "success|failure|skipped",
  "duration_ms": "number",
  "runner_os": "ubuntu-latest|windows-latest"
}
```

### test-results-{YYYY.MM.DD}
Structured pass/fail per test suite.
```json
{
  "@timestamp": "ISO8601",
  "suite": "playwright|cargo|sbt|fpc|gfortran",
  "platform": "C++|Rust|Scala|Pascal|Fortran|React",
  "test_name": "string",
  "status": "pass|fail|skip",
  "duration_ms": "number",
  "error_message": "string|null",
  "file": "string",
  "device": "ThinkPad|MacBook",
  "browser": "chromium|firefox|mobile-chrome|null"
}
```

### db-slow-{YYYY.MM.DD}
Slow query diagnostics from both databases.
```json
{
  "@timestamp": "ISO8601",
  "db_type": "postgresql|mongodb",
  "duration_ms": "number",
  "query": "string",
  "database": "vibedev",
  "client": "string",
  "rows_examined": "number|null",
  "plan": "object|null"
}
```

---

## Fluent Bit Configuration

**File:** `infra/docker/elasticsearch/fluent-bit.conf`

```ini
[SERVICE]
    Flush         5
    Daemon        Off
    Log_Level     info
    HTTP_Server   On
    HTTP_Listen   0.0.0.0
    HTTP_Port     2020

# ── GitHub Actions log input (TCP JSON) ──────────────────────────
[INPUT]
    Name    tcp
    Listen  0.0.0.0
    Port    24224
    Format  json
    Tag     ci.actions

# ── PostgreSQL slow query log ─────────────────────────────────────
[INPUT]
    Name    tail
    Path    C:\Users\vitez\pgdata\pg.log
    Tag     db.postgres
    Parser  postgresql_slow

# ── MongoDB log ───────────────────────────────────────────────────
[INPUT]
    Name    tail
    Path    C:\Users\vitez\mongodata\mongod.log
    Tag     db.mongo
    Parser  json

# ── Output to Elasticsearch ───────────────────────────────────────
[OUTPUT]
    Name            es
    Match           ci.*
    Host            127.0.0.1
    Port            9200
    Index           ci-logs
    Type            _doc
    Logstash_Format On
    Logstash_Prefix ci-logs

[OUTPUT]
    Name            es
    Match           test.*
    Host            127.0.0.1
    Port            9200
    Logstash_Format On
    Logstash_Prefix test-results

[OUTPUT]
    Name            es
    Match           db.*
    Host            127.0.0.1
    Port            9200
    Logstash_Format On
    Logstash_Prefix db-slow
```

---

## Docker Compose

**File:** `infra/docker/elasticsearch/docker-compose.yml`

```yaml
version: "3.8"

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.0
    container_name: vibe-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - ES_JAVA_OPTS=-Xms512m -Xmx1g
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - esdata:/usr/share/elasticsearch/data
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  kibana:
    image: docker.elastic.co/kibana/kibana:8.13.0
    container_name: vibe-kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      elasticsearch:
        condition: service_healthy

  fluent-bit:
    image: fluent/fluent-bit:3.0
    container_name: vibe-fluent-bit
    ports:
      - "24224:24224"
      - "2020:2020"
    volumes:
      - ./fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf:ro
    depends_on:
      - elasticsearch

volumes:
  esdata:
    driver: local
```

---

## Connector Specifications

See `infra/connectors/LOG-CONNECTOR-SPEC.md` for full API contracts.

### Quick Reference

| Connector | Language | Target | File |
|-----------|----------|--------|------|
| log-connector-node | Node.js / Winston | MongoDB + ES | `connectors/log-connector-node/` |
| log-connector-python | Python / logging | MongoDB + ES | `connectors/log-connector-python/` |
| log-connector-github-actions | YAML / curl | ES via Fluent Bit | `connectors/log-connector-github-actions/` |

---

## CI/CD Integration

New job added to `ci-heartbeat.yml`: **`log-infra-test`**

```yaml
log-infra-test:
  name: Log Infrastructure Health
  runs-on: ubuntu-latest
  steps:
    - name: Start ES stack
      run: docker compose -f infra/docker/elasticsearch/docker-compose.yml up -d
    - name: Wait for ES health
      run: |
        timeout 60 bash -c 'until curl -sf http://localhost:9200/_cluster/health; do sleep 2; done'
    - name: Ship test event
      run: |
        curl -X POST http://localhost:9200/test-results-$(date +%Y.%m.%d)/_doc \
          -H "Content-Type: application/json" \
          -d '{"@timestamp":"'$(date -u +%FT%TZ)'","suite":"ci-health-check","status":"pass"}'
    - name: Verify ingestion
      run: |
        sleep 2
        COUNT=$(curl -sf http://localhost:9200/test-results-*/_count | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])")
        [ "$COUNT" -gt 0 ] && echo "ES ingestion OK: $COUNT docs" || exit 1
```

---

## Production Docker Image Template

The ES stack Docker Compose is designed as a drop-in production template:
- Replace `discovery.type=single-node` with cluster config for multi-node
- Enable `xpack.security.enabled=true` + TLS for production
- Mount external volume for `esdata`
- Replace Fluent Bit file tail inputs with Kubernetes/Docker log drivers

---

## Resource Requirements (Local Dev)

| Component | RAM | CPU | Disk |
|-----------|-----|-----|------|
| Elasticsearch | 1 GB | 0.5 vCPU | ~2 GB / month |
| Kibana | 256 MB | 0.2 vCPU | minimal |
| Fluent Bit | 32 MB | 0.05 vCPU | minimal |
| **Total** | **~1.3 GB** | **~0.75 vCPU** | **~2 GB / month** |

> Requires Docker Desktop running (Gate 6).
