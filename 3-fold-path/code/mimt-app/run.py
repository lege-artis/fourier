#!/usr/bin/env python3
# =============================================================================
# mimt-app/run.py — Topology B entrypoint (Windows-portable, no admin rights)
# tags:    [PoC-01][TOPO-B]
# date:    2026-05-03
# citation: HANDOVER-V0.2-THINKPAD.md PoC-01 quick-note; OPUS-CYCLE-v0.2-MASTER.md §2
#
# Usage:
#   python run.py --env=dev     # boots on $MIMT_PORT_DEV (default 8080), dev.sqlite
#   python run.py --env=prod    # boots on $MIMT_PORT_PROD (default 8090), prod.sqlite
#
# Environment variables (all optional — defaults shown):
#   MIMT_PORT_DEV=8080          DEV listener port
#   MIMT_PORT_PROD=8090         PROD listener port
#   SQLITE_DEV_PATH=dev.sqlite  DEV SQLite file (relative to mi_m_t package root)
#   SQLITE_PROD_PATH=prod.sqlite PROD SQLite file
#   MIMT_HOST=0.0.0.0           Bind address (default 0.0.0.0)
#   MIMT_RELOAD=0               Set to 1 to enable uvicorn --reload (dev only)
#
# Topology B constraints:
#   - SQLite only (no Docker, no admin-managed DB)
#   - DEV and PROD run in separate OS processes with separate SQLite files
#   - Env vars set HERE, before mi_m_t import, so pydantic-settings picks them up
#   - PKG_ROOT added to sys.path so mi_m_t is importable without pip install -e
#
# Topology A (Docker) uses docker-compose.yml — see infra/docker/ for that path.
# =============================================================================
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# ── CLI args — parsed BEFORE any mi_m_t import ────────────────────────────────
_parser = argparse.ArgumentParser(
    description="MI-M-T Topology B runner",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=__doc__,
)
_parser.add_argument(
    "--env",
    choices=["dev", "prod"],
    default="dev",
    help="Target environment: dev (port 8080, dev.sqlite) or prod (port 8090, prod.sqlite)",
)
_parser.add_argument(
    "--host",
    default=None,
    help="Bind host (default: $MIMT_HOST or 0.0.0.0)",
)
_parser.add_argument(
    "--port",
    type=int,
    default=None,
    help="Override port (default: $MIMT_PORT_DEV / $MIMT_PORT_PROD)",
)
_parser.add_argument(
    "--reload",
    action="store_true",
    default=False,
    help="Enable uvicorn auto-reload (dev only; overrides $MIMT_RELOAD)",
)
args = _parser.parse_args()

# ── Environment setup — MUST happen before mi_m_t is imported ─────────────────
# pydantic-settings reads os.environ at Settings() instantiation (import time).
if args.env == "dev":
    _default_port       = 8080
    _default_sqlite     = "dev.sqlite"
    _port_env_key       = "MIMT_PORT_DEV"
    _sqlite_env_key     = "SQLITE_DEV_PATH"
    _app_env_value      = "development"
else:
    _default_port       = 8090
    _default_sqlite     = "prod.sqlite"
    _port_env_key       = "MIMT_PORT_PROD"
    _sqlite_env_key     = "SQLITE_PROD_PATH"
    _app_env_value      = "production"

_port       = args.port or int(os.environ.get(_port_env_key, _default_port))
_host       = args.host or os.environ.get("MIMT_HOST", "0.0.0.0")
_sqlite     = os.environ.get(_sqlite_env_key, _default_sqlite)
_reload     = args.reload or os.environ.get("MIMT_RELOAD", "0") == "1"

# Inject into environment — pydantic-settings reads these:
os.environ["DB_DRIVER"]    = "sqlite"
os.environ["SQLITE_PATH"]  = _sqlite
os.environ["APP_ENV"]      = _app_env_value
if args.env == "prod":
    os.environ["DEBUG"]    = "false"

# ── Path setup — add mi_m_t package root to sys.path ─────────────────────────
# Layout: 3-fold-path/code/mimt-app/run.py
#         3-fold-path/code/mi_m_t/          ← package root (contains mi_m_t/ sub-package)
_MIMT_APP_DIR = Path(__file__).resolve().parent
_PKG_ROOT     = (_MIMT_APP_DIR / ".." / "mi_m_t").resolve()

if not (_PKG_ROOT / "mi_m_t").is_dir():
    print(
        f"ERROR: mi_m_t package not found at {_PKG_ROOT / 'mi_m_t'}.\n"
        f"       Expected layout: <repo>/3-fold-path/code/mi_m_t/mi_m_t/__init__.py\n"
        f"       Check that run.py is inside 3-fold-path/code/mimt-app/",
        file=sys.stderr,
    )
    sys.exit(1)

sys.path.insert(0, str(_PKG_ROOT))

# SQLite path is relative to PKG_ROOT (where uvicorn process cwd will be set)
os.chdir(str(_PKG_ROOT))

# ── Late imports — safe after env + path setup ────────────────────────────────
try:
    import uvicorn
except ImportError:
    sys.exit("ERROR: uvicorn not installed. Run: pip install uvicorn --break-system-packages")

from mi_m_t.main import create_app  # noqa: E402

# ── Boot ──────────────────────────────────────────────────────────────────────
_app = create_app()

print(f"[mimt-app] env={args.env}  host={_host}  port={_port}  sqlite={_sqlite}  reload={_reload}")
print(f"[mimt-app] pkg_root={_PKG_ROOT}")
print(f"[mimt-app] health → http://{_host}:{_port}/health")

uvicorn.run(
    _app,
    host=_host,
    port=_port,
    reload=_reload,
    log_level="info" if args.env == "dev" else "warning",
)
