# Log Connector Specification
**Version:** 1.0.0 | **Date:** 2026-03-22

All connectors implement the same logical interface regardless of language.
MongoDB receives app runtime logs. Elasticsearch receives CI/test/DB diagnostics.

---

## Shared Log Event Schema

```typescript
interface LogEvent {
  timestamp:  string;        // ISO8601 UTC
  level:      "debug" | "info" | "warn" | "error";
  source:     string;        // originating service name
  app:        string;        // application identifier
  session_id: string;        // dev/test session UUID
  message:    string;
  metadata?: {
    host?:    string;
    pid?:     number;
    env?:     "development" | "test" | "staging" | "production";
    version?: string;
  };
  context?:   Record<string, unknown>;
}
```

---

## Connector A — log-connector-node

**Path:** `infra/connectors/log-connector-node/`
**Language:** Node.js (CommonJS + ESM)
**Dependencies:** `winston`, `mongodb`, `@elastic/elasticsearch`

### Installation
```bash
npm install winston mongodb @elastic/elasticsearch
```

### Usage
```javascript
const { createLogger } = require('./log-connector-node');

const logger = createLogger({
  app: 'my-app',
  sessionId: process.env.SESSION_ID || require('crypto').randomUUID(),
  mongo: { uri: process.env.MONGODB_URI, db: 'vibedev', collection: 'logs' },
  elastic: { node: 'http://localhost:9200', index: 'app-logs' },
});

logger.info('Server started', { port: 3000 });
logger.error('DB connection failed', { err: error.message });
```

### Implementation scaffold
```javascript
// infra/connectors/log-connector-node/index.js
const winston = require('winston');
const { MongoClient } = require('mongodb');
const { Client: ESClient } = require('@elastic/elasticsearch');

class MongoTransport extends winston.Transport {
  constructor(opts) {
    super(opts);
    this.client = new MongoClient(opts.uri);
    this.db = opts.db;
    this.collection = opts.collection;
    this.client.connect();
  }
  log(info, callback) {
    const col = this.client.db(this.db).collection(this.collection);
    col.insertOne({ timestamp: new Date(), ...info }).then(() => callback());
  }
}

class ESTransport extends winston.Transport {
  constructor(opts) {
    super(opts);
    this.es = new ESClient({ node: opts.node });
    this.index = opts.index;
  }
  log(info, callback) {
    this.es.index({
      index: `${this.index}-${new Date().toISOString().slice(0,10).replace(/-/g,'.')}`,
      document: { '@timestamp': new Date().toISOString(), ...info }
    }).then(() => callback());
  }
}

function createLogger(config) {
  return winston.createLogger({
    defaultMeta: { app: config.app, session_id: config.sessionId },
    transports: [
      new winston.transports.Console({ format: winston.format.simple() }),
      new MongoTransport(config.mongo),
      new ESTransport(config.elastic),
    ]
  });
}

module.exports = { createLogger };
```

---

## Connector B — log-connector-python

**Path:** `infra/connectors/log-connector-python/`
**Language:** Python 3.11+
**Dependencies:** `pymongo`, `elasticsearch`, `python-json-logger`

### Installation
```bash
pip install pymongo elasticsearch python-json-logger
```

### Usage
```python
from log_connector import get_logger

logger = get_logger(
    app="my-python-service",
    session_id="uuid-here",
    mongo_uri=os.environ["MONGODB_URI"],
    es_node="http://localhost:9200"
)

logger.info("Pipeline started", extra={"step": "preprocess"})
logger.error("Validation failed", extra={"metric": "accuracy", "value": 0.42})
```

### Implementation scaffold
```python
# infra/connectors/log-connector-python/log_connector.py
import logging
from datetime import datetime, timezone
from pymongo import MongoClient
from elasticsearch import Elasticsearch

class MongoHandler(logging.Handler):
    def __init__(self, uri, db="vibedev", collection="logs"):
        super().__init__()
        self.col = MongoClient(uri)[db][collection]

    def emit(self, record):
        doc = {
            "timestamp": datetime.now(timezone.utc),
            "level": record.levelname.lower(),
            "message": self.format(record),
            **getattr(record, "__dict__", {})
        }
        self.col.insert_one(doc)

class ESHandler(logging.Handler):
    def __init__(self, node="http://localhost:9200", index_prefix="app-logs"):
        super().__init__()
        self.es = Elasticsearch([node])
        self.index_prefix = index_prefix

    def emit(self, record):
        today = datetime.now(timezone.utc).strftime("%Y.%m.%d")
        doc = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "message": self.format(record),
        }
        self.es.index(index=f"{self.index_prefix}-{today}", document=doc)

def get_logger(app, session_id, mongo_uri, es_node="http://localhost:9200"):
    logger = logging.getLogger(app)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(MongoHandler(uri=mongo_uri))
    logger.addHandler(ESHandler(node=es_node, index_prefix="app-logs"))
    return logging.LoggerAdapter(logger, {"app": app, "session_id": session_id})
```

---

## Connector C — log-connector-github-actions

**Path:** `infra/connectors/log-connector-github-actions/`
**Type:** GitHub Actions composite action (YAML)

### Usage in workflow
```yaml
- name: Ship job result to Elasticsearch
  uses: ./infra/connectors/log-connector-github-actions
  with:
    es_host: http://localhost:9200
    suite: rust-build-test
    status: ${{ job.status }}
    duration_ms: ${{ steps.timer.outputs.duration }}
```

### action.yml
```yaml
name: Ship Test Result to Elasticsearch
description: Ships CI job result to Elasticsearch test-results index
inputs:
  es_host:     { required: true,  description: Elasticsearch base URL }
  suite:       { required: true,  description: Test suite name }
  status:      { required: true,  description: pass|fail|skip }
  duration_ms: { required: false, default: "0" }

runs:
  using: composite
  steps:
    - shell: bash
      run: |
        TODAY=$(date -u +%Y.%m.%d)
        curl -sf -X POST "${{ inputs.es_host }}/test-results-${TODAY}/_doc" \
          -H "Content-Type: application/json" \
          -d '{
            "@timestamp": "'$(date -u +%FT%TZ)'",
            "suite":       "${{ inputs.suite }}",
            "status":      "${{ inputs.status }}",
            "duration_ms": ${{ inputs.duration_ms }},
            "run_id":      "${{ github.run_id }}",
            "run_number":  ${{ github.run_number }},
            "workflow":    "${{ github.workflow }}",
            "branch":      "${{ github.ref_name }}"
          }' || echo "ES ship failed (non-fatal)"
```

---

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://127.0.0.1:27017/vibedev` |
| `ES_NODE` | Elasticsearch base URL | `http://localhost:9200` |
| `LOG_LEVEL` | Minimum log level | `info` |
| `LOG_SESSION_ID` | Session UUID for log correlation | auto-generated |
| `LOG_APP` | Application identifier | required |
| `LOG_ENV` | Environment tag | `development` |
