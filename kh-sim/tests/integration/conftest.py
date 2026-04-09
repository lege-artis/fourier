# conftest.py — shared fixtures for KH-SIM integration test suite
# Task: KH-018 | Device: ThinkPad (LDE stack must be running)
#
# Environment overrides (all optional):
#   KH_RUST_URL     default http://localhost:8001
#   KH_SCALA_URL    default http://localhost:8002
#   KH_CPP_URL      default http://localhost:8003
#   KH_FORTRAN_URL  default http://localhost:8004
#   KH_PASCAL_URL   default http://localhost:8005
#   KH_LOG_URL      default http://localhost:8006
#
# Run: pytest kh-sim/tests/integration/ -v
#      pytest kh-sim/tests/integration/ -v -k "health"     # subset

import json
import os
import uuid
from pathlib import Path

import pytest
import requests

# ── Backend manifest ──────────────────────────────────────────────────────────

BACKEND_META = {
    "kh-rust":    {"port": 8001, "language": "Rust",    "framework": "axum"},
    "kh-scala":   {"port": 8002, "language": "Scala",   "framework": "http4s"},
    "kh-cpp":     {"port": 8003, "language": "C++",     "framework": "cpp-httplib"},
    "kh-fortran": {"port": 8004, "language": "Fortran", "framework": "C-interop"},
    "kh-pascal":  {"port": 8005, "language": "Pascal",  "framework": "fphttpapp"},
}

BACKEND_NAMES = list(BACKEND_META.keys())


def _backend_url(name: str) -> str:
    env_key = f"KH_{name.replace('kh-', '').upper()}_URL"
    return os.environ.get(env_key, f"http://localhost:{BACKEND_META[name]['port']}")


BACKEND_URLS: dict[str, str] = {name: _backend_url(name) for name in BACKEND_NAMES}
LOG_SERVICE_URL: str = os.environ.get("KH_LOG_URL", "http://localhost:8006")

# ── Reference data ────────────────────────────────────────────────────────────

_REF_PATH = (
    Path(__file__).parents[2] / "shared" / "physics" / "kh_reference_output.json"
)

with open(_REF_PATH) as _f:
    REFERENCE_OUTPUT: dict = json.load(_f)

REFERENCE_DIAGNOSTICS: dict[str, float] = REFERENCE_OUTPUT["diagnostics"]

# Canonical sim params that reproduce the reference output (64x32, 100 steps)
REFERENCE_PARAMS: dict = {
    "grid_nx":                 64,
    "grid_ny":                 32,
    "domain_lx":               1.0,
    "domain_ly":               0.5,
    "dt":                      0.001,
    "steps":                   100,
    "reynolds_number":         1000.0,
    "velocity_shear":          1.0,
    "perturbation_amplitude":  0.01,
    "perturbation_mode":       2,
}

EXPECTED_FIELD_LENGTH = REFERENCE_PARAMS["grid_nx"] * REFERENCE_PARAMS["grid_ny"]  # 2048

# Physics tolerances per KH-PHYSICS.md section 7
TOLERANCE_PCT: float = 5.0        # +-5% for KE, enstrophy
DIV_RMS_LIMIT: float = 1e-10      # incompressibility acceptance criterion

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def backend_urls() -> dict[str, str]:
    """Map of backend name -> base URL for all 5 backends."""
    return BACKEND_URLS


@pytest.fixture(scope="session")
def log_url() -> str:
    """Base URL for the kh-log-service."""
    return LOG_SERVICE_URL


@pytest.fixture(scope="session")
def test_session_id() -> str:
    """Unique session ID shared across all integration tests in this run."""
    return f"pytest-{uuid.uuid4().hex[:12]}"


@pytest.fixture(scope="session")
def simulate_responses(backend_urls: dict[str, str]) -> dict[str, requests.Response]:
    """
    Run POST /simulate on every backend once per pytest session.
    Cached so physics validation tests share the same HTTP calls.
    Tests that depend on this fixture will be skipped per-backend if the
    backend is unreachable.
    """
    results: dict[str, requests.Response] = {}
    for name, base_url in backend_urls.items():
        try:
            resp = requests.post(
                f"{base_url}/simulate",
                json=REFERENCE_PARAMS,
                timeout=30,
            )
            results[name] = resp
        except requests.exceptions.ConnectionError:
            results[name] = None  # type: ignore[assignment]
    return results


# ── Helpers (importable by test modules) ─────────────────────────────────────

def within_tolerance(actual: float, reference: float, pct: float) -> bool:
    """Return True if actual is within ±pct% of reference."""
    return abs(actual - reference) / abs(reference) <= pct / 100.0


def pct_error(actual: float, reference: float) -> float:
    return abs(actual - reference) / abs(reference) * 100.0
