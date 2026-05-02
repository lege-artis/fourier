# =============================================================================
# mi_m_t/domain/statuses.py — 12-state lifecycle set + pure validation helpers
# tags:    [μS-CAND][TRIG-REQ]
# date:    2026-04-29
# citation: ARCH-SPEC §4 (state machine), §4.3 ('any' expansion rule)
# =============================================================================
from __future__ import annotations

STATUSES: frozenset[str] = frozenset({
    "new", "in-analysis", "confirmed", "in-progress", "implemented",
    "verifying", "passed", "failed", "closed", "cancelled", "duplicate", "deferred",
})

ENTITY_TABLES: frozenset[str] = frozenset({
    "test_targets", "test_cases", "test_scripts", "test_data",
    "test_environments", "iteration_test_sets", "test_runs", "requests",
})


def is_valid_status(s: str) -> bool:
    return s in STATUSES


def is_valid_entity_table(t: str) -> bool:
    return t in ENTITY_TABLES


class TransitionError(ValueError):
    """Raised when a status transition is not permitted by the state machine."""
    pass


class RoleError(PermissionError):
    """Raised when the user's role does not satisfy transition requires_role."""
    pass
