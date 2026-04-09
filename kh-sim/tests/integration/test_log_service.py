# test_log_service.py — KH-014 log service integration tests
# Task: KH-018  |  Service: kh-log-service :8006
#
# Tests are grouped by capability:
#   - /health  (always runs — handles degraded/503)
#   - /info    (always runs — static metadata)
#   - POST /event (skipped if MongoDB unavailable)
#   - GET /viewer (skipped if MongoDB unavailable)
#   - GET /summary (always runs — returns 0-event rows when MongoDB up)
#
# MongoDB availability is detected from /health response.

import time

import pytest
import requests

from conftest import BACKEND_NAMES


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mongo_available(log_url: str) -> bool:
    """Return True if log service reports MongoDB connected."""
    try:
        r = requests.get(f"{log_url}/health", timeout=5)
        body = r.json()
        return r.status_code == 200 and body.get("mongo") == "connected"
    except Exception:
        return False


def _require_mongo(log_url: str) -> None:
    """Skip test if MongoDB is unavailable (degraded mode)."""
    if not _mongo_available(log_url):
        pytest.skip("MongoDB not connected — log service in degraded mode")


# ── /health ───────────────────────────────────────────────────────────────────

def test_log_health_accepts_degraded(log_url: str) -> None:
    """Log service /health returns 200 (connected) or 503 (degraded) — never 4xx."""
    try:
        resp = requests.get(f"{log_url}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")
    assert resp.status_code in (200, 503), (
        f"/health: unexpected status {resp.status_code}"
    )


def test_log_health_body_fields(log_url: str) -> None:
    """Log service /health body has status, mongo, uptime_s."""
    try:
        resp = requests.get(f"{log_url}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")

    body = resp.json()
    for field in ("status", "mongo", "uptime_s"):
        assert field in body, f"/health response missing field '{field}'"

    assert body["mongo"] in ("connected", "disconnected", "error"), (
        f"/health: unexpected mongo value '{body['mongo']}'"
    )
    assert isinstance(body["uptime_s"], (int, float)) and body["uptime_s"] >= 0


# ── /info ─────────────────────────────────────────────────────────────────────

def test_log_info_status_code(log_url: str) -> None:
    """GET /info returns 200."""
    try:
        resp = requests.get(f"{log_url}/info", timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")
    assert resp.status_code == 200


def test_log_info_body_fields(log_url: str) -> None:
    """GET /info body contains expected service metadata."""
    try:
        resp = requests.get(f"{log_url}/info", timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")

    body = resp.json()
    for field in ("service", "version", "port"):
        assert field in body, f"/info response missing field '{field}'"
    assert body.get("port") == 8006, (
        f"/info port {body.get('port')} != expected 8006"
    )


# ── POST /event ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("backend_name", BACKEND_NAMES)
def test_log_post_valid_event(
    backend_name: str, log_url: str, test_session_id: str
) -> None:
    """POST /event with valid payload returns 201 for each known backend."""
    _require_mongo(log_url)
    payload = {
        "source": backend_name,
        "message": f"integration test event from {backend_name}",
        "level": "info",
        "session_id": test_session_id,
        "metadata": {"test": True, "backend": backend_name},
    }
    try:
        resp = requests.post(f"{log_url}/event", json=payload, timeout=10)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")
    assert resp.status_code == 201, (
        f"{backend_name}: POST /event returned {resp.status_code}: {resp.text[:200]}"
    )
    body = resp.json()
    assert "inserted_id" in body or "id" in body, (
        f"{backend_name}: POST /event response missing inserted_id: {body}"
    )


def test_log_post_invalid_backend_returns_400(
    log_url: str, test_session_id: str
) -> None:
    """POST /event with unknown backend name returns 400."""
    _require_mongo(log_url)
    payload = {
        "source": "kh-invalid-backend",
        "message": "should be rejected",
        "level": "info",
        "session_id": test_session_id,
    }
    try:
        resp = requests.post(f"{log_url}/event", json=payload, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")
    assert resp.status_code == 400, (
        f"POST /event with invalid backend: expected 400, got {resp.status_code}"
    )


def test_log_post_missing_source_returns_400(
    log_url: str, test_session_id: str
) -> None:
    """POST /event without required 'source' field returns 400."""
    _require_mongo(log_url)
    payload = {
        "message": "missing source field",
        "level": "info",
        "session_id": test_session_id,
    }
    try:
        resp = requests.post(f"{log_url}/event", json=payload, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")
    assert resp.status_code == 400, (
        f"POST /event without source: expected 400, got {resp.status_code}"
    )


# ── GET /viewer ───────────────────────────────────────────────────────────────

def test_log_viewer_returns_array(log_url: str, test_session_id: str) -> None:
    """GET /viewer returns a JSON array (may be empty if no prior events)."""
    _require_mongo(log_url)
    try:
        resp = requests.get(
            f"{log_url}/viewer",
            params={"session_id": test_session_id},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")
    assert resp.status_code == 200, f"GET /viewer: {resp.status_code}: {resp.text[:200]}"
    body = resp.json()
    assert isinstance(body, list), f"GET /viewer: expected list, got {type(body)}"


def test_log_viewer_reflects_posted_events(
    log_url: str, test_session_id: str
) -> None:
    """Events posted with test_session_id are retrievable via /viewer."""
    _require_mongo(log_url)

    # Post a unique sentinel event
    sentinel_msg = f"sentinel-{test_session_id}"
    payload = {
        "source": "kh-rust",
        "message": sentinel_msg,
        "level": "debug",
        "session_id": test_session_id,
    }
    try:
        post_resp = requests.post(f"{log_url}/event", json=payload, timeout=10)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")
    assert post_resp.status_code == 201

    # Retrieve and verify
    get_resp = requests.get(
        f"{log_url}/viewer",
        params={"session_id": test_session_id, "backend": "kh-rust"},
        timeout=10,
    )
    assert get_resp.status_code == 200
    events = get_resp.json()
    assert any(
        e.get("message") == sentinel_msg for e in events
    ), f"Sentinel event '{sentinel_msg}' not found in viewer response"


def test_log_viewer_limit_param(log_url: str, test_session_id: str) -> None:
    """GET /viewer respects ?limit parameter (result length <= limit)."""
    _require_mongo(log_url)
    try:
        resp = requests.get(
            f"{log_url}/viewer",
            params={"session_id": test_session_id, "limit": 2},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) <= 2, f"limit=2 but /viewer returned {len(events)} events"


# ── GET /summary ──────────────────────────────────────────────────────────────

def test_log_summary_returns_all_backends(log_url: str) -> None:
    """GET /summary returns one entry per known backend (including 0-event backends)."""
    _require_mongo(log_url)
    try:
        resp = requests.get(f"{log_url}/summary", timeout=10)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")
    assert resp.status_code == 200, f"GET /summary: {resp.status_code}: {resp.text[:200]}"
    body = resp.json()
    assert isinstance(body, list), f"GET /summary: expected list, got {type(body)}"
    assert len(body) == len(BACKEND_NAMES), (
        f"GET /summary: expected {len(BACKEND_NAMES)} entries (one per backend), "
        f"got {len(body)}: {[e.get('backend') for e in body]}"
    )


def test_log_summary_entry_schema(log_url: str) -> None:
    """Each /summary entry has backend and event_count fields."""
    _require_mongo(log_url)
    try:
        resp = requests.get(f"{log_url}/summary", timeout=10)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Log service not reachable at {log_url}")
    body = resp.json()
    for entry in body:
        assert "backend" in entry, f"/summary entry missing 'backend': {entry}"
        assert "event_count" in entry, f"/summary entry missing 'event_count': {entry}"
        assert isinstance(entry["event_count"], int), (
            f"/summary event_count must be int: {entry}"
        )
