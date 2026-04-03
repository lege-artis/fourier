#!/usr/bin/env python3
"""
smoke_test.py  --  LOG-003 integration smoke test

Verifies end-to-end log delivery from log_connector (Python) to:
  MongoDB  mongodb://127.0.0.1:27017/vibedev   collection: logs
  Elasticsearch  http://localhost:9200          index: kh-sim-YYYY.MM.DD

Exit codes:
  0  all checks passed
  1  one or more checks failed

Prerequisites:
  MongoDB 8.2.6 running on 27017 (DB-002 done)
  ELK stack up:  .\\_config\\Start-LocalEnv.ps1 -Action up -Stack elk
  pip install -r requirements.txt  (in this directory)

Run:
  python smoke_test.py
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from datetime import datetime, timezone

# ── Configuration ─────────────────────────────────────────────────────────────

MONGO_URI    = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017")
ES_NODE      = os.environ.get("ES_NODE",     "http://localhost:9200")
SESSION      = f"smoke-{int(time.time())}"
APP          = "log-connector-smoke-test-py"
INDEX_PREFIX = "kh-sim"

# ── Utilities ─────────────────────────────────────────────────────────────────

passed = 0
failed = 0


def ok(label: str) -> None:
    global passed
    print(f"  [PASS] {label}")
    passed += 1


def fail(label: str, detail: str = "") -> None:
    global failed
    suffix = f": {detail}" if detail else ""
    print(f"  [FAIL] {label}{suffix}", file=sys.stderr)
    failed += 1


def header(text: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {text}")
    print("─" * 60)


# ── Main ─────────────────────────────────────────────────────────────────────

def run() -> None:
    header("LOG-003 smoke test — log-connector-python")

    # ── 1. Emit test events ───────────────────────────────────────────────────
    header("Step 1: emit structured log events")

    try:
        from log_connector import get_logger
    except ImportError as exc:
        fail("Import log_connector", str(exc))
        _summary()
        return

    logger = get_logger(
        app=APP,
        session_id=SESSION,
        version="1.0.0",
        level="debug",
        mongo_uri=MONGO_URI,
        mongo_db="vibedev",
        mongo_collection="logs",
        es_node=ES_NODE,
        index_prefix=INDEX_PREFIX,
    )

    logger.info("Smoke test started", extra={"step": "init", "session": SESSION})
    logger.debug("Debug event", extra={"detail": "low-level trace"})
    logger.warning("Intentional warning", extra={"code": "W001", "threshold": 0.95})
    logger.error("Intentional error (non-fatal)", extra={"code": "E001", "recoverable": True})

    print("  Waiting 2s for handler flush...")
    time.sleep(2)

    ok("log events emitted (4 events: info, debug, warning, error)")

    # ── 2. Verify MongoDB ─────────────────────────────────────────────────────
    header("Step 2: verify MongoDB vibedev.logs")

    try:
        from pymongo import MongoClient
        from pymongo.errors import PyMongoError

        mc = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5_000)
        mc.admin.command("ping")
        col   = mc["vibedev"]["logs"]
        count = col.count_documents({"session_id": SESSION, "app": APP})

        if count >= 4:
            ok(f"MongoDB: {count} documents found for session {SESSION}")
        elif count > 0:
            fail(f"MongoDB: expected >= 4 docs, found {count}")
        else:
            fail(f"MongoDB: 0 documents found for session {SESSION}")

        # Schema spot-check
        doc = col.find_one({"session_id": SESSION, "app": APP})
        if doc:
            required = all([
                doc.get("level"),
                doc.get("message"),
                doc.get("app"),
                doc.get("session_id"),
                isinstance(doc.get("metadata"), dict),
                doc["metadata"].get("host"),
                doc["metadata"].get("pid") is not None,
            ])
            if required:
                ok("MongoDB: document schema valid (level, message, app, session_id, metadata)")
            else:
                fail("MongoDB: document missing required schema fields", str(doc))

        mc.close()

    except ImportError:
        fail("MongoDB: pymongo not installed")
    except PyMongoError as exc:
        fail("MongoDB: connection or query failed", str(exc))

    # ── 3. Verify Elasticsearch ───────────────────────────────────────────────
    header("Step 3: verify Elasticsearch kh-sim-* index")

    try:
        from elasticsearch import Elasticsearch
        try:
            from elasticsearch.exceptions import ElasticsearchException
        except ImportError:
            from elasticsearch import ApiError as ElasticsearchException  # type: ignore

        es    = Elasticsearch([ES_NODE], request_timeout=10)
        today = datetime.now(timezone.utc).strftime("%Y.%m.%d")
        index = f"{INDEX_PREFIX}-{today}"

        # Force refresh so newly indexed docs are visible
        try:
            es.indices.refresh(index=f"{INDEX_PREFIX}-*")
        except ElasticsearchException:
            pass  # index may not exist yet if ES sink failed -- handled below

        # Diagnostic: total doc count (mapping-agnostic)
        total = es.count(index=f"{INDEX_PREFIX}-*")
        print(f"  [INFO] Total docs in {INDEX_PREFIX}-*: {total['count']}")

        # ES 8 dynamic mapping: string fields → text + .keyword sub-field.
        # Use session_id.keyword for exact term match.
        try:
            result = es.count(
                index=f"{INDEX_PREFIX}-*",
                query={"term": {"session_id.keyword": SESSION}},
            )
        except ElasticsearchException:
            result = es.count(
                index=f"{INDEX_PREFIX}-*",
                query={"match_phrase": {"session_id": SESSION}},
            )
        count = result["count"]

        if count >= 4:
            ok(f"Elasticsearch: {count} documents in {index} for session {SESSION}")
        elif count > 0:
            fail(f"Elasticsearch: expected >= 4 docs, found {count}")
        else:
            fail(f"Elasticsearch: 0 documents found in {index} for session {SESSION}")

        # Schema spot-check
        try:
            hit = es.search(
                index=f"{INDEX_PREFIX}-*",
                size=1,
                query={"term": {"session_id.keyword": SESSION}},
            )
        except ElasticsearchException:
            hit = {}
        hits = hit.get("hits", {}).get("hits", [])
        if hits:
            src = hits[0]["_source"]
            if src.get("@timestamp") and src.get("level"):
                ok("Elasticsearch: document has @timestamp and level fields")
            else:
                fail("Elasticsearch: document missing @timestamp or level", str(src))

    except ImportError:
        fail("Elasticsearch: elasticsearch-py not installed")
    except ElasticsearchException as exc:
        fail("Elasticsearch: connection or query failed", str(exc))

    # ── 4. Cluster health sanity ──────────────────────────────────────────────
    header("Step 4: ES cluster health")

    try:
        from elasticsearch import Elasticsearch
        es     = Elasticsearch([ES_NODE], request_timeout=5)
        health = es.cluster.health()
        status = health.get("status", "unknown")
        nodes  = health.get("number_of_nodes", "?")
        if status in ("green", "yellow"):
            ok(f"Elasticsearch cluster: status={status}, nodes={nodes}")
        else:
            fail(f"Elasticsearch cluster: unexpected status={status}")
    except Exception as exc:  # noqa: BLE001
        fail("Elasticsearch cluster health check failed", str(exc))

    # ── Summary ───────────────────────────────────────────────────────────────
    _summary()


def _summary() -> None:
    global passed, failed
    header("Summary")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    if failed == 0:
        print("\n  LOG-003 smoke test PASSED -- log-connector-python operational\n")
        sys.exit(0)
    else:
        print("\n  LOG-003 smoke test FAILED -- see [FAIL] lines above\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run()
