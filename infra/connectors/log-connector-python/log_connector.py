"""
log_connector.py  --  VibeCodeProjects structured log connector (Python)
Project: KH-Sim / infra  |  Task: LOG-003

Dual-sink logging.Handler setup:
  MongoDB  vibedev.logs       -- app runtime events (flexible schema, 30-day TTL)
  Elasticsearch {prefix}-YYYY.MM.DD  -- CI/test/structured diagnostics

Both sinks are optional; omit the corresponding argument to disable.

Schema: infra/connectors/LOG-CONNECTOR-SPEC.md
Architecture: infra/LOG-ARCHITECTURE.md

Usage::

    from log_connector import get_logger

    logger = get_logger(
        app="kh-rust-runner",
        session_id=os.environ.get("LOG_SESSION_ID", str(uuid.uuid4())),
        mongo_uri="mongodb://127.0.0.1:27017",
        es_node="http://localhost:9200",
        index_prefix="kh-sim",
    )

    logger.info("Simulation started", extra={"kx": 1.0, "ky": 0.5})
    logger.error("Divergence detected", extra={"iteration": 42, "residual": 9.9e6})
"""

from __future__ import annotations

import logging
import os
import platform
import socket
import threading
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Optional dependencies -- both sinks degrade gracefully if libraries absent
# ---------------------------------------------------------------------------
try:
    from pymongo import MongoClient  # type: ignore
    from pymongo.errors import PyMongoError  # type: ignore
    _MONGO_AVAILABLE = True
except ImportError:
    _MONGO_AVAILABLE = False

try:
    from elasticsearch import Elasticsearch  # type: ignore
    # elasticsearch-py 8.19+ removed ElasticsearchException; ApiError is the base now.
    # Fall back gracefully so the guard works across 8.13–8.x releases.
    try:
        from elasticsearch.exceptions import ElasticsearchException  # type: ignore
    except ImportError:
        from elasticsearch import ApiError as ElasticsearchException  # type: ignore
    _ES_AVAILABLE = True
except ImportError:
    _ES_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _build_doc(record: logging.LogRecord, default_meta: dict) -> dict:
    """Convert a LogRecord into the shared VibeCode log schema document."""
    # Extract user-supplied extra fields (exclude stdlib LogRecord internals)
    _stdlib_keys = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message", "taskName",
    }
    context = {
        k: v for k, v in record.__dict__.items()
        if k not in _stdlib_keys and not k.startswith("_")
    }
    # Remove keys injected by LoggerAdapter / get_logger
    for key in ("app", "session_id", "version", "source"):
        context.pop(key, None)

    ts = _utc_now()
    return {
        "@timestamp": ts.isoformat(),
        "timestamp":  ts,           # native datetime for MongoDB TTL index
        "level":      record.levelname.lower(),
        "source":     default_meta.get("source") or default_meta.get("app", "unknown"),
        "app":        default_meta.get("app", "unknown"),
        "session_id": default_meta.get("session_id", "none"),
        "message":    record.getMessage(),
        "metadata": {
            "host":    socket.gethostname(),
            "pid":     os.getpid(),
            "env":     os.environ.get("LOG_ENV", "development"),
            "version": default_meta.get("version", "0.0.0"),
        },
        "context": context,
    }


# ---------------------------------------------------------------------------
# MongoDB handler
# ---------------------------------------------------------------------------

class MongoHandler(logging.Handler):
    """
    Logging handler that writes structured documents to MongoDB.

    Connection is established asynchronously on first use so that import /
    logger construction never blocks. If the connection fails the handler
    emits a stderr warning and discards subsequent log records silently --
    logging must never crash the host process.
    """

    def __init__(
        self,
        uri: str,
        db: str = "vibedev",
        collection: str = "logs",
        default_meta: Optional[dict] = None,
        server_selection_timeout_ms: int = 5_000,
    ) -> None:
        super().__init__()
        if not _MONGO_AVAILABLE:
            raise ImportError(
                "pymongo is required for MongoHandler. "
                "Install with: pip install pymongo"
            )
        self._default_meta = default_meta or {}
        self._db_name      = db
        self._col_name     = collection
        self._col          = None      # set after connect
        self._ready        = False
        self._failed       = False
        self._lock         = threading.Lock()

        try:
            client = MongoClient(
                uri,
                serverSelectionTimeoutMS=server_selection_timeout_ms,
            )
            # Trigger DNS + TCP before any log is emitted (still fast)
            client.admin.command("ping")
            self._col   = client[db][collection]
            self._ready = True
        except PyMongoError as exc:
            import sys
            print(
                f"[MongoHandler] connect failed: {exc} -- MongoDB sink disabled",
                file=sys.stderr,
            )
            self._failed = True

    def emit(self, record: logging.LogRecord) -> None:
        if self._failed or not self._ready:
            return
        try:
            doc = _build_doc(record, self._default_meta)
            self._col.insert_one(doc)
        except PyMongoError as exc:
            import sys
            print(f"[MongoHandler] insert error: {exc}", file=sys.stderr)
        except Exception:  # noqa: BLE001
            self.handleError(record)


# ---------------------------------------------------------------------------
# Elasticsearch handler
# ---------------------------------------------------------------------------

class ESHandler(logging.Handler):
    """
    Logging handler that indexes structured documents into Elasticsearch.

    Index pattern: {index_prefix}-YYYY.MM.DD  (Logstash-style date suffix).
    Connection errors are logged to stderr and the handler carries on -- the
    host process is never interrupted.
    """

    def __init__(
        self,
        node: str = "http://localhost:9200",
        index_prefix: str = "app-logs",
        default_meta: Optional[dict] = None,
        request_timeout: int = 5,
    ) -> None:
        super().__init__()
        if not _ES_AVAILABLE:
            raise ImportError(
                "elasticsearch-py is required for ESHandler. "
                "Install with: pip install elasticsearch"
            )
        self._index_prefix  = index_prefix
        self._default_meta  = default_meta or {}
        self._request_timeout = request_timeout
        self._es = Elasticsearch(
            [node],
            request_timeout=request_timeout,
        )

    def emit(self, record: logging.LogRecord) -> None:
        try:
            doc   = _build_doc(record, self._default_meta)
            today = _utc_now().strftime("%Y.%m.%d")
            index = f"{self._index_prefix}-{today}"
            self._es.index(index=index, document=doc)
        except ElasticsearchException as exc:
            import sys
            print(f"[ESHandler] index error: {exc}", file=sys.stderr)
        except Exception:  # noqa: BLE001
            self.handleError(record)


# ---------------------------------------------------------------------------
# Console handler (JSON-structured, CI-friendly)
# ---------------------------------------------------------------------------

class _StructuredConsoleFormatter(logging.Formatter):
    """Single-line structured log format: timestamp [app] LEVEL: message {context}"""

    def format(self, record: logging.LogRecord) -> str:
        ts  = _utc_now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        app = getattr(record, "app", record.name)
        lvl = record.levelname
        msg = record.getMessage()
        # Include any extra context fields
        _stdlib_keys = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message", "taskName",
        }
        ctx = {
            k: v for k, v in record.__dict__.items()
            if k not in _stdlib_keys and not k.startswith("_")
            and k not in ("app", "session_id", "version", "source")
        }
        suffix = f" {ctx}" if ctx else ""
        return f"{ts} [{app}] {lvl}: {msg}{suffix}"


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------

def get_logger(
    app: str,
    session_id: Optional[str] = None,
    version: str = "0.0.0",
    level: str = "info",
    mongo_uri: Optional[str] = None,
    mongo_db: str = "vibedev",
    mongo_collection: str = "logs",
    es_node: Optional[str] = None,
    index_prefix: str = "app-logs",
    console: bool = True,
) -> logging.Logger:
    """
    Build and return a stdlib Logger wired to the requested sinks.

    Parameters
    ----------
    app:              Application / service identifier (required)
    session_id:       Dev/test session UUID; auto-generated if omitted
    version:          Application version string
    level:            Minimum log level string (default: LOG_LEVEL env or 'info')
    mongo_uri:        MongoDB connection string; omit to disable Mongo sink
    mongo_db:         MongoDB database name (default: 'vibedev')
    mongo_collection: MongoDB collection name (default: 'logs')
    es_node:          Elasticsearch base URL; omit to disable ES sink
    index_prefix:     Elasticsearch index prefix (default: 'app-logs')
    console:          Include structured console handler (default: True)

    Returns
    -------
    logging.Logger instance with the configured sinks attached.
    """
    if not app:
        raise ValueError("log_connector.get_logger: 'app' parameter is required")

    import uuid
    resolved_session = (
        session_id
        or os.environ.get("LOG_SESSION_ID")
        or str(uuid.uuid4())
    )
    resolved_level = (
        level
        or os.environ.get("LOG_LEVEL", "info")
    ).upper()

    default_meta = {
        "app":        app,
        "source":     app,
        "session_id": resolved_session,
        "version":    version,
    }

    logger = logging.getLogger(app)
    # Avoid adding duplicate handlers on repeated calls in the same process
    if logger.handlers:
        logger.handlers.clear()

    logger.setLevel(resolved_level)
    logger.propagate = False

    # Console sink
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(resolved_level)
        ch.setFormatter(_StructuredConsoleFormatter())
        logger.addHandler(ch)

    # MongoDB sink
    if mongo_uri or os.environ.get("MONGODB_URI"):
        uri = mongo_uri or os.environ["MONGODB_URI"]
        try:
            mh = MongoHandler(
                uri=uri,
                db=mongo_db,
                collection=mongo_collection,
                default_meta=default_meta,
            )
            mh.setLevel(resolved_level)
            logger.addHandler(mh)
        except ImportError as exc:
            import sys
            print(f"[log_connector] MongoDB sink skipped: {exc}", file=sys.stderr)

    # Elasticsearch sink
    if es_node or os.environ.get("ES_NODE"):
        node = es_node or os.environ["ES_NODE"]
        try:
            eh = ESHandler(
                node=node,
                index_prefix=index_prefix,
                default_meta=default_meta,
            )
            eh.setLevel(resolved_level)
            logger.addHandler(eh)
        except ImportError as exc:
            import sys
            print(f"[log_connector] Elasticsearch sink skipped: {exc}", file=sys.stderr)

    # Inject default_meta into every LogRecord via a Filter
    class _MetaFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            for k, v in default_meta.items():
                if not hasattr(record, k):
                    setattr(record, k, v)
            return True

    logger.addFilter(_MetaFilter())

    return logger
