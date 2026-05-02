#!/usr/bin/env python3
"""
SMK9 — MI-M-T FastAPI smoke test, 20 cases
Supports sqlite / mysql / postgres via CLI args for D-09 portability pass.

Usage:
  # SQLite (default)
  SQLITE_PATH=d06.sqlite python3 smoke_test.py

  # Explicit sqlite
  python3 smoke_test.py --db-driver sqlite --db-url sqlite+aiosqlite:///d09-test.sqlite

  # MySQL 8
  python3 smoke_test.py --db-driver mysql \
    --db-url "mysql+asyncmy://root:@127.0.0.1:3306/mimt_dev"

  # PostgreSQL 14
  python3 smoke_test.py --db-driver postgres \
    --db-url "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/mimt_dev"
"""
import argparse, asyncio, json, sys, os
from datetime import datetime

# ── CLI args ──────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="MI-M-T SMK9 smoke test")
parser.add_argument("--db-driver", default=None,
                    choices=["sqlite", "mysql", "postgres"],
                    help="Override DB_DRIVER env var")
parser.add_argument("--db-url", default=None,
                    help="Override DATABASE_URL (full SQLAlchemy async URL)")
args = parser.parse_args()

# ── Environment setup (before app import) ─────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if args.db_driver:
    os.environ["DB_DRIVER"] = args.db_driver
if args.db_url:
    # pydantic-settings reads individual fields; inject via monkeypatch after import
    pass
if "SQLITE_PATH" not in os.environ and not args.db_url and not args.db_driver:
    os.environ["SQLITE_PATH"] = "d06.sqlite"

# Switch to project dir so relative SQLITE_PATH works
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from mi_m_t.main import create_app
from mi_m_t.config import settings

# Apply --db-url override via settings monkeypatch (post-import)
if args.db_url:
    settings.__dict__["_database_url_override"] = args.db_url
    # Patch database_url property
    type(settings).database_url = property(
        lambda self: args.db_url
    )

import httpx

app = create_app()
BASE  = "http://test"
HDRS  = {"x-user-id": "1", "x-user-role": "TM", "content-type": "application/json"}
NOW   = datetime.utcnow().isoformat()
RUN_TAG = datetime.utcnow().strftime("%H%M%S")

passed = []
failed = []


def _chk(name, ok, resp=None):
    if ok:
        passed.append(name)
    else:
        detail = ""
        if resp is not None:
            try:   detail = json.dumps(resp.json(), indent=None)[:300]
            except: detail = resp.text[:300]
        failed.append((name, detail))


async def run():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url=BASE
    ) as c:

        # ── S01  GET /health ─────────────────────────────────────────────
        r = await c.get("/health")
        _chk("S01 GET /health → 200", r.status_code == 200)

        # ── S02  GET /api/v1/projects ────────────────────────────────────
        r = await c.get("/api/v1/projects", headers=HDRS)
        _chk("S02 GET /projects → 200", r.status_code == 200)

        # ── S03  POST /api/v1/projects ───────────────────────────────────
        r = await c.post("/api/v1/projects", headers=HDRS, json={
            "project_code": f"SMK9-{RUN_TAG}", "name": f"Smoke run {RUN_TAG}"})
        _chk("S03 POST /projects → 201", r.status_code == 201, r)
        proj_id = r.json()["id"]

        # ── S04  GET /api/v1/projects/{id} ──────────────────────────────
        r = await c.get(f"/api/v1/projects/{proj_id}", headers=HDRS)
        _chk("S04 GET /projects/{id} → 200", r.status_code == 200)

        # ── S05  POST /api/v1/test-targets ──────────────────────────────
        r = await c.post("/api/v1/test-targets", headers=HDRS, json={
            "project_id": proj_id, "item_code": f"TT-{RUN_TAG}",
            "item_name": "Login module", "submitter_id": 1,
            "item_submit_date": NOW})
        _chk("S05 POST /test-targets → 201", r.status_code == 201, r)
        tt_id = r.json()["id"]

        # ── S06  GET /api/v1/test-targets ───────────────────────────────
        r = await c.get(f"/api/v1/test-targets?project_id={proj_id}", headers=HDRS)
        _chk("S06 GET /test-targets → 200", r.status_code == 200)

        # ── S07  POST /api/v1/test-cases ────────────────────────────────
        r = await c.post("/api/v1/test-cases", headers=HDRS, json={
            "project_id": proj_id, "item_code": f"TC-{RUN_TAG}",
            "item_name": "Login happy path", "submitter_id": 1,
            "item_submit_date": NOW, "test_target_id": tt_id,
            "phases": [
                {"phase_type": "pre",  "phase_name": "Setup",    "resources": []},
                {"phase_type": "exec", "phase_name": "Execute",  "resources": []},
                {"phase_type": "post", "phase_name": "Teardown", "resources": []},
            ]})
        _chk("S07 POST /test-cases → 201", r.status_code == 201, r)
        tc_id = r.json()["id"]

        # ── S08  GET /api/v1/test-cases/{id} ────────────────────────────
        r = await c.get(f"/api/v1/test-cases/{tc_id}", headers=HDRS)
        _chk("S08 GET /test-cases/{id} → 200", r.status_code == 200)

        # ── S09  POST /api/v1/requests ──────────────────────────────────
        r = await c.post("/api/v1/requests", headers=HDRS, json={
            "project_id": proj_id, "item_code": f"REQ-{RUN_TAG}",
            "item_name": "Login regression", "item_type": "bug",
            "submitter_id": 1, "item_submit_date": NOW})
        _chk("S09 POST /requests → 201", r.status_code == 201, r)
        req_id = r.json()["id"]

        # ── S10  POST /requests/{id}/link-cases ─────────────────────────
        r = await c.post(f"/api/v1/requests/{req_id}/link-cases",
                         headers=HDRS, json={"test_case_ids": [tc_id]})
        _chk("S10 POST /requests/{id}/link-cases → 200", r.status_code == 200, r)

        # ── S11  GET /api/v1/requests ───────────────────────────────────
        r = await c.get(f"/api/v1/requests?project_id={proj_id}", headers=HDRS)
        _chk("S11 GET /requests → 200", r.status_code == 200)

        # ── S12  POST /api/v1/test-runs ─────────────────────────────────
        r = await c.post("/api/v1/test-runs", headers=HDRS, json={
            "project_id": proj_id, "item_code": f"RUN-{RUN_TAG}",
            "item_name": "Smoke run 9", "submitter_id": 1,
            "item_submit_date": NOW, "executor_id": 1,
            "run_date": NOW})
        _chk("S12 POST /test-runs → 201", r.status_code == 201, r)
        run_id = r.json()["id"]

        # ── S13  GET /api/v1/test-runs/{id} ─────────────────────────────
        r = await c.get(f"/api/v1/test-runs/{run_id}", headers=HDRS)
        _chk("S13 GET /test-runs/{id} → 200", r.status_code == 200)

        # ── S14  POST /test-runs/{id}/results ───────────────────────────
        r = await c.post(f"/api/v1/test-runs/{run_id}/results",
                         headers=HDRS, json={
                             "test_case_id": tc_id, "verdict": "pass",
                             "actual_result": "Login succeeded"})
        _chk("S14 POST /test-runs/{id}/results → 200", r.status_code == 200, r)

        # ── S15  POST /test-runs/{id}/finalize ──────────────────────────
        r = await c.post(f"/api/v1/test-runs/{run_id}/finalize", headers=HDRS)
        _chk("S15 POST /test-runs/{id}/finalize → 200", r.status_code == 200, r)

        # ── S16  GET /api/v1/test-runs ──────────────────────────────────
        r = await c.get(f"/api/v1/test-runs?project_id={proj_id}", headers=HDRS)
        _chk("S16 GET /test-runs → 200", r.status_code == 200)

        # ── S17  POST /test-targets/{id}/transition ──────────────────────
        r = await c.post(f"/api/v1/test-targets/{tt_id}/transition",
                         headers=HDRS, json={"to_status": "in-analysis", "note": "smoke"})
        _chk("S17 POST /test-targets/{id}/transition → 200", r.status_code == 200, r)

        # ── S18  GET /api/v1/state-machine/test_targets ─────────────────
        r = await c.get("/api/v1/state-machine/test_targets", headers=HDRS)
        _chk("S18 GET /state-machine/test_targets → 200", r.status_code == 200)

        # ── S19  GET /api/v1/value-lists/statuses ───────────────────────
        r = await c.get("/api/v1/value-lists/statuses", headers=HDRS)
        _chk("S19 GET /value-lists/statuses → 200", r.status_code == 200)

        # ── S20  GET /api/v1/trace/test_targets/{id} ────────────────────
        r = await c.get(f"/api/v1/trace/test_targets/{tt_id}", headers=HDRS)
        _chk("S20 GET /trace/test_targets/{id} → 200", r.status_code == 200)

    # ── Summary ──────────────────────────────────────────────────────────────
    db_info = args.db_url or os.environ.get("SQLITE_PATH", settings.sqlite_path)
    total = len(passed) + len(failed)
    print(f"\n{'='*60}")
    print(f"SMK9  {len(passed)}/{total} PASS  [{args.db_driver or settings.db_driver}  {db_info}]")
    print(f"{'='*60}")
    for name in passed:
        print(f"  ✓  {name}")
    for name, detail in failed:
        print(f"  ✗  {name}")
        if detail:
            print(f"       {detail}")
    return len(failed) == 0


if __name__ == "__main__":
    ok = asyncio.run(run())
    sys.exit(0 if ok else 1)
