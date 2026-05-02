# =============================================================================
# tests/test_smk9.py — SMK9 pytest suite (20 test functions)
# tags:    [μS-CAND][TRIG-REQ]
# date:    2026-05-02
# citation: ARCH-SPEC §7.5 (router inventory), smoke_test.py (reference impl)
#
# Design note — sequential state:
#   These tests are a smoke suite, not isolated unit tests.
#   S03/S05/S07/S09/S12 create entities and store their IDs in `_state`.
#   Later tests consume those IDs.  Tests MUST run in definition order
#   (pytest default, guaranteed by no randomisation plugin in this suite).
#   If an early create-test fails, downstream tests will fail with a
#   KeyError / 404 — that is intentional cascade behaviour.
#
# asyncio_mode = "auto" is set in pyproject.toml — no @pytest.mark.asyncio needed.
# =============================================================================
from __future__ import annotations

from datetime import datetime

import httpx
import pytest

# ── Module-level mutable state (entity IDs shared across sequential tests) ────
_state: dict[str, int] = {}

NOW = datetime.utcnow().isoformat()


# ═══════════════════════════════════════════════════════════════════════════════
# S01-S04  — Health + Projects
# ═══════════════════════════════════════════════════════════════════════════════

async def test_s01_health(client: httpx.AsyncClient) -> None:
    """S01  GET /health → 200 with status key."""
    r = await client.get("/health")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "ok"


async def test_s02_projects_list_empty(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S02  GET /api/v1/projects → 200 (may be empty list)."""
    r = await client.get("/api/v1/projects", headers=hdrs)
    assert r.status_code == 200, r.text


async def test_s03_create_project(
    client: httpx.AsyncClient, hdrs: dict, run_tag: str
) -> None:
    """S03  POST /api/v1/projects → 201, stores proj_id."""
    r = await client.post(
        "/api/v1/projects",
        headers=hdrs,
        json={"project_code": f"SMK9-{run_tag}", "name": f"Smoke run {run_tag}"},
    )
    assert r.status_code == 201, r.text
    _state["proj_id"] = r.json()["id"]


async def test_s04_get_project(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S04  GET /api/v1/projects/{id} → 200."""
    proj_id = _state["proj_id"]
    r = await client.get(f"/api/v1/projects/{proj_id}", headers=hdrs)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == proj_id


# ═══════════════════════════════════════════════════════════════════════════════
# S05-S06  — Test Targets
# ═══════════════════════════════════════════════════════════════════════════════

async def test_s05_create_test_target(
    client: httpx.AsyncClient, hdrs: dict, run_tag: str
) -> None:
    """S05  POST /api/v1/test-targets → 201, stores tt_id."""
    r = await client.post(
        "/api/v1/test-targets",
        headers=hdrs,
        json={
            "project_id":       _state["proj_id"],
            "item_code":        f"TT-{run_tag}",
            "item_name":        "Login module",
            "submitter_id":     1,
            "item_submit_date": NOW,
        },
    )
    assert r.status_code == 201, r.text
    _state["tt_id"] = r.json()["id"]


async def test_s06_list_test_targets(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S06  GET /api/v1/test-targets?project_id=… → 200, contains created target."""
    proj_id = _state["proj_id"]
    r = await client.get(
        f"/api/v1/test-targets?project_id={proj_id}", headers=hdrs
    )
    assert r.status_code == 200, r.text
    ids = [item["id"] for item in r.json()["data"]]
    assert _state["tt_id"] in ids


# ═══════════════════════════════════════════════════════════════════════════════
# S07-S08  — Test Cases
# ═══════════════════════════════════════════════════════════════════════════════

async def test_s07_create_test_case(
    client: httpx.AsyncClient, hdrs: dict, run_tag: str
) -> None:
    """S07  POST /api/v1/test-cases → 201, stores tc_id."""
    r = await client.post(
        "/api/v1/test-cases",
        headers=hdrs,
        json={
            "project_id":       _state["proj_id"],
            "item_code":        f"TC-{run_tag}",
            "item_name":        "Login happy path",
            "submitter_id":     1,
            "item_submit_date": NOW,
            "test_target_id":   _state["tt_id"],
            "phases": [
                {"phase_type": "pre",  "phase_name": "Setup",    "resources": []},
                {"phase_type": "exec", "phase_name": "Execute",  "resources": []},
                {"phase_type": "post", "phase_name": "Teardown", "resources": []},
            ],
        },
    )
    assert r.status_code == 201, r.text
    _state["tc_id"] = r.json()["id"]


async def test_s08_get_test_case(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S08  GET /api/v1/test-cases/{id} → 200, phases present."""
    tc_id = _state["tc_id"]
    r = await client.get(f"/api/v1/test-cases/{tc_id}", headers=hdrs)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] == tc_id
    assert len(body.get("phases", [])) == 3


# ═══════════════════════════════════════════════════════════════════════════════
# S09-S11  — Requests
# ═══════════════════════════════════════════════════════════════════════════════

async def test_s09_create_request(
    client: httpx.AsyncClient, hdrs: dict, run_tag: str
) -> None:
    """S09  POST /api/v1/requests → 201, stores req_id."""
    r = await client.post(
        "/api/v1/requests",
        headers=hdrs,
        json={
            "project_id":       _state["proj_id"],
            "item_code":        f"REQ-{run_tag}",
            "item_name":        "Login regression",
            "item_type":        "bug",
            "submitter_id":     1,
            "item_submit_date": NOW,
        },
    )
    assert r.status_code == 201, r.text
    _state["req_id"] = r.json()["id"]


async def test_s10_link_cases_to_request(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S10  POST /api/v1/requests/{id}/link-cases → 200."""
    req_id = _state["req_id"]
    tc_id  = _state["tc_id"]
    r = await client.post(
        f"/api/v1/requests/{req_id}/link-cases",
        headers=hdrs,
        json={"test_case_ids": [tc_id]},
    )
    assert r.status_code == 200, r.text


async def test_s11_list_requests(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S11  GET /api/v1/requests?project_id=… → 200, contains created request."""
    proj_id = _state["proj_id"]
    r = await client.get(
        f"/api/v1/requests?project_id={proj_id}", headers=hdrs
    )
    assert r.status_code == 200, r.text
    ids = [item["id"] for item in r.json()["data"]]
    assert _state["req_id"] in ids


# ═══════════════════════════════════════════════════════════════════════════════
# S12-S16  — Test Runs
# ═══════════════════════════════════════════════════════════════════════════════

async def test_s12_create_test_run(
    client: httpx.AsyncClient, hdrs: dict, run_tag: str
) -> None:
    """S12  POST /api/v1/test-runs → 201, stores run_id."""
    r = await client.post(
        "/api/v1/test-runs",
        headers=hdrs,
        json={
            "project_id":       _state["proj_id"],
            "item_code":        f"RUN-{run_tag}",
            "item_name":        "Smoke run 9",
            "submitter_id":     1,
            "item_submit_date": NOW,
            "executor_id":      1,
            "run_date":         NOW,
        },
    )
    assert r.status_code == 201, r.text
    _state["run_id"] = r.json()["id"]


async def test_s13_get_test_run(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S13  GET /api/v1/test-runs/{id} → 200."""
    run_id = _state["run_id"]
    r = await client.get(f"/api/v1/test-runs/{run_id}", headers=hdrs)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == run_id


async def test_s14_append_run_result(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S14  POST /api/v1/test-runs/{id}/results → 200/201."""
    run_id = _state["run_id"]
    tc_id  = _state["tc_id"]
    r = await client.post(
        f"/api/v1/test-runs/{run_id}/results",
        headers=hdrs,
        json={
            "test_case_id":  tc_id,
            "verdict":       "pass",
            "actual_result": "Login succeeded",
        },
    )
    assert r.status_code in (200, 201), r.text


async def test_s15_finalize_test_run(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S15  POST /api/v1/test-runs/{id}/finalize → 200."""
    run_id = _state["run_id"]
    r = await client.post(
        f"/api/v1/test-runs/{run_id}/finalize", headers=hdrs
    )
    assert r.status_code == 200, r.text
    # Verdict must be set after finalize
    assert r.json().get("overall_verdict") is not None


async def test_s16_list_test_runs(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S16  GET /api/v1/test-runs?project_id=… → 200."""
    proj_id = _state["proj_id"]
    r = await client.get(
        f"/api/v1/test-runs?project_id={proj_id}", headers=hdrs
    )
    assert r.status_code == 200, r.text


# ═══════════════════════════════════════════════════════════════════════════════
# S17  — Transition
# ═══════════════════════════════════════════════════════════════════════════════

async def test_s17_transition_test_target(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S17  POST /api/v1/test-targets/{id}/transition → 200, status updated."""
    tt_id = _state["tt_id"]
    r = await client.post(
        f"/api/v1/test-targets/{tt_id}/transition",
        headers=hdrs,
        json={"to_status": "in-analysis", "note": "smoke"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["item_status"] == "in-analysis"


# ═══════════════════════════════════════════════════════════════════════════════
# S18-S20  — State machine / Value lists / Trace
# ═══════════════════════════════════════════════════════════════════════════════

async def test_s18_state_machine(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S18  GET /api/v1/state-machine/test_targets → 200, transitions present."""
    r = await client.get("/api/v1/state-machine/test_targets", headers=hdrs)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "transitions" in body
    assert len(body["transitions"]) > 0


async def test_s19_value_lists(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S19  GET /api/v1/value-lists/statuses → 200."""
    r = await client.get("/api/v1/value-lists/statuses", headers=hdrs)
    assert r.status_code == 200, r.text


async def test_s20_trace(
    client: httpx.AsyncClient, hdrs: dict
) -> None:
    """S20  GET /api/v1/trace/test_targets/{id} → 200."""
    tt_id = _state["tt_id"]
    r = await client.get(
        f"/api/v1/trace/test_targets/{tt_id}", headers=hdrs
    )
    assert r.status_code == 200, r.text
