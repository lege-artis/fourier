# =============================================================================
# tests/conftest.py — MI-M-T pytest session fixtures
# tags:    [μS-CAND]
# date:    2026-05-02
# citation: ARCH-SPEC §7.6 (async service), pyproject.toml asyncio_mode=auto
#
# Environment precedence (highest first):
#   1. Environment variables already set (e.g. CI, PowerShell $env: chain)
#   2. Defaults below (SQLite LDE — safe for local dev with no containers)
#
# Override for other engines before running pytest:
#   PowerShell — MySQL 8:
#     $env:DB_DRIVER="mysql"; $env:DB_HOST="127.0.0.1"; $env:DB_PORT="3306"
#     $env:DB_NAME="mimt_dev"; $env:DB_USER="root"; $env:DB_PASS=""
#     pytest tests/
#
#   PowerShell — PostgreSQL 14 (Docker port 5433):
#     $env:DB_DRIVER="postgres"; $env:DB_HOST="127.0.0.1"; $env:DB_PORT="5433"
#     $env:DB_NAME="mimt_dev"; $env:DB_USER="postgres"; $env:DB_PASS="postgres"
#     pytest tests/
# =============================================================================
from __future__ import annotations

import os
import sys
from datetime import datetime

import httpx
import pytest
import pytest_asyncio

# ── Set env defaults BEFORE mi_m_t is imported ───────────────────────────────
# pydantic-settings reads env at Settings() instantiation (module-import time).
# Any override must be in os.environ before `from mi_m_t.main import create_app`.
os.environ.setdefault("DB_DRIVER", "sqlite")
# d06.sqlite lives at the mi_m_t package root (D-08 LDE database, gitignored).
# .test/d06.sqlite is the .env.example convention for fresh setups — not the
# existing D-08 file that was already seeded and verified.
os.environ.setdefault("SQLITE_PATH", "d06.sqlite")

# CWD must be the package root so relative SQLITE_PATH resolves correctly.
_PKG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_PKG_ROOT)
sys.path.insert(0, _PKG_ROOT)

from mi_m_t.main import create_app  # noqa: E402 — must follow env setup

# ── Constants ─────────────────────────────────────────────────────────────────
BASE_URL = "http://test"
HEADERS  = {
    "x-user-id":   "1",
    "x-user-role": "TM",
    "content-type": "application/json",
}


# ── Session-scoped fixtures ───────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="session")
async def client():
    """
    Session-scoped async HTTPX client wired to the FastAPI ASGI app.
    Single app instance + single DB connection pool for the entire test session.
    """
    _app = create_app()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=_app),
        base_url=BASE_URL,
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
def hdrs() -> dict[str, str]:
    """Shared request headers — X-User-Id / X-User-Role / Content-Type."""
    return HEADERS


@pytest.fixture(scope="session")
def run_tag() -> str:
    """
    HHMMSS tag unique to this test session.
    Used to avoid item_code collisions when running against a persistent DB.
    """
    return datetime.utcnow().strftime("%H%M%S")
