# =============================================================================
# mimt-app/Dockerfile — Topology A multi-stage image
# tags:    [PoC-02][TOPO-A]
# date:    2026-05-03
# citation: OPUS-CYCLE-v0.2-MASTER.md §6.1 G-01; HANDOVER-V0.2-THINKPAD.md PoC-02
#
# Build context: 3-fold-path/code/  (parent of mimt-app/ and mi_m_t/)
# Referenced from docker-compose.yml as:
#   build:
#     context: ..
#     dockerfile: mimt-app/Dockerfile
#
# Two stages:
#   deps    — Python 3.11-slim + gcc/libpq-dev + pip install (all runtime deps)
#   runtime — Python 3.11-slim + libpq5 + non-root user mimt (uid 1001)
#             includes mi_m_t/ package AND migrations/ runner
#
# ENV defaults (override via .env or -e flags):
#   DB_DRIVER=postgres   DB_HOST=mimt-pg14   DB_PORT=5432
#   DB_NAME=mimt_dev     DB_USER=postgres    DB_PASS=postgres
#   APP_ENV=production   DEBUG=false
#   SECRET_KEY=change-me-in-production
# =============================================================================

# ── Stage 1: dependency resolver ──────────────────────────────────────────────
FROM python:3.11-slim AS deps

WORKDIR /build

# C-extension build tools: asyncpg (libpq-dev) + asyncmy (gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the pyproject.toml so pip layer is cache-friendly
COPY mi_m_t/pyproject.toml .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir \
        "fastapi>=0.104" \
        "pydantic>=2.0" \
        "pydantic-settings>=2.0" \
        "sqlalchemy[asyncio]>=2.0" \
        "aiosqlite>=0.19" \
        "asyncmy>=0.2" \
        "asyncpg>=0.29" \
        "uvicorn[standard]>=0.24" \
        "httpx>=0.26" \
        "alembic>=1.13" \
        "pyyaml>=6.0"

# ── Stage 2: lean runtime image ───────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Runtime shared lib for asyncpg (libpq5 is the postgres client library)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user — security hardening (matches Topology B uid convention)
RUN groupadd --gid 1001 mimt \
 && useradd --uid 1001 --gid mimt --shell /bin/bash --create-home mimt

WORKDIR /app

# Transplant installed packages from deps stage (avoids rebuilding)
COPY --from=deps /usr/local/lib/python3.11/site-packages \
                 /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Application source — build context is 3-fold-path/code/
COPY mi_m_t/mi_m_t/ ./mi_m_t/
COPY migrations/     ./migrations/

# Ownership — everything under /app belongs to mimt
RUN chown -R mimt:mimt /app

USER mimt

# Environment defaults — all overridable via docker-compose env_file or -e
ENV DB_DRIVER=postgres \
    DB_HOST=mimt-pg14 \
    DB_PORT=5432 \
    DB_NAME=mimt_dev \
    DB_USER=postgres \
    DB_PASS=postgres \
    APP_ENV=production \
    DEBUG=false \
    SECRET_KEY=change-me-in-production

EXPOSE 8000

# Graceful shutdown: uvicorn handles SIGTERM correctly with --workers 1
CMD ["uvicorn", "mi_m_t.main:create_app", "--factory", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", "--timeout-keep-alive", "30"]
