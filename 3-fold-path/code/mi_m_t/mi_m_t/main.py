# =============================================================================
# mi_m_t/main.py — FastAPI application factory
# tags:    [μS-CAND]
# date:    2026-04-29
# citation: ARCH-SPEC §7.1 (API versioning), §7.5 (router inventory)
# =============================================================================
from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import mi_m_t.models  # noqa: F401 — registers all ORM models in mapper registry
from mi_m_t.db import engine
from mi_m_t.config import settings
from mi_m_t.domain.statuses import TransitionError, RoleError

# ── Routers ──────────────────────────────────────────────────────────────────
from mi_m_t.routers.projects      import router as projects_router
from mi_m_t.routers.test_targets  import router as test_targets_router
from mi_m_t.routers.test_cases    import router as test_cases_router
from mi_m_t.routers.requests      import router as requests_router
from mi_m_t.routers.test_runs     import router as test_runs_router
from mi_m_t.routers.state_machine import router as state_machine_router
from mi_m_t.routers.value_lists   import router as value_lists_router
from mi_m_t.routers.sync          import router as sync_router
from mi_m_t.routers.trace         import router as trace_router


# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: nothing to do — migrations applied via runner.py
    yield
    # shutdown: dispose engine connection pool
    await engine.dispose()


# ── App factory ──────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="MI-M-T API",
        version="0.1.0",
        description=(
            "Methodology for Integrated Manual Testing — "
            "REST API (ARCH-SPEC §7.1). "
            "Supports MySQL 8.0 / PostgreSQL 14 / SQLite 3.38."
        ),
        lifespan=lifespan,
    )

    # ── Domain exception handlers ─────────────────────────────────────────
    @app.exception_handler(TransitionError)
    async def _transition_error(request: Request, exc: TransitionError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(RoleError)
    async def _role_error(request: Request, exc: RoleError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    # ── Router registration  (all under /api/v1) ──────────────────────────
    prefix = "/api/v1"
    app.include_router(projects_router,      prefix=prefix)
    app.include_router(test_targets_router,  prefix=prefix)
    app.include_router(test_cases_router,    prefix=prefix)
    app.include_router(requests_router,      prefix=prefix)
    app.include_router(test_runs_router,     prefix=prefix)
    app.include_router(state_machine_router, prefix=prefix)
    app.include_router(value_lists_router,   prefix=prefix)
    app.include_router(sync_router,          prefix=prefix)
    app.include_router(trace_router,         prefix=prefix)

    # ── Health check (ARCH-SPEC §7.1 — DB connectivity probe) ────────────
    @app.get("/health", tags=["meta"])
    async def health():
        from sqlalchemy import text as _text
        from fastapi.responses import JSONResponse as _JSONResponse
        db_status = "ok"
        db_error: str | None = None
        try:
            async with engine.connect() as conn:
                await conn.execute(_text("SELECT 1"))
        except Exception as exc:
            db_status = "error"
            db_error = str(exc)
        payload: dict = {
            "status": "ok" if db_status == "ok" else "degraded",
            "version": app.version,
            "db_driver": settings.db_driver,
            "db_status": db_status,
        }
        if db_error:
            payload["db_error"] = db_error
        return _JSONResponse(
            content=payload,
            status_code=200 if db_status == "ok" else 503,
        )

    return app


app = create_app()
