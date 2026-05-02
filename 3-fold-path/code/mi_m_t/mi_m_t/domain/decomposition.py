# =============================================================================
# mi_m_t/domain/decomposition.py — R-RT / R-TC structural validators
# tags:    [μS-CAND][TRIG-REQ]
# date:    2026-04-29
# citation: ARCH-SPEC §R-TC-3 (phase presence), §R-TC-5 (resource admissibility)
# =============================================================================
from __future__ import annotations

# R-TC-5 admissibility matrix — phase_type → allowed resource_types
PHASE_RESOURCE_MATRIX: dict[str, frozenset[str]] = {
    "pre":  frozenset({"test_data", "test_procedure"}),
    "exec": frozenset({"test_script", "test_data", "test_environment",
                       "test_component", "test_user"}),
    "post": frozenset({"test_data", "test_procedure"}),
}

REQUIRED_PHASE_TYPES: frozenset[str] = frozenset({"pre", "exec", "post"})


class PhaseViolation(ValueError):
    """R-TC-3 or R-TC-5 violation."""
    pass


def assert_required_phases(phases: list[dict]) -> None:
    """R-TC-3: all three phase_types (pre, exec, post) must be present."""
    present = {p.get("phase_type") or getattr(p, "phase_type", None) for p in phases}
    missing = REQUIRED_PHASE_TYPES - present
    if missing:
        raise PhaseViolation(
            f"R-TC-3: missing required phase_type(s): {', '.join(sorted(missing))}"
        )


def assert_resource_admissible(phase_type: str, resource_type: str) -> None:
    """R-TC-5: resource_type must be admissible for phase_type."""
    allowed = PHASE_RESOURCE_MATRIX.get(phase_type)
    if allowed is None:
        raise PhaseViolation(f"R-TC-5: unknown phase_type '{phase_type}'")
    if resource_type not in allowed:
        raise PhaseViolation(
            f"R-TC-5: resource_type='{resource_type}' not admissible "
            f"in phase_type='{phase_type}'. Allowed: {sorted(allowed)}"
        )


def validate_phases(phases: list) -> None:
    """Combined R-TC-3 + R-TC-5 check for a full phase list (dicts or Pydantic objs)."""
    assert_required_phases(phases)
    for phase in phases:
        pt = phase.get("phase_type") if isinstance(phase, dict) else phase.phase_type
        resources = phase.get("resources", []) if isinstance(phase, dict) else phase.resources
        for res in resources:
            rt = res.get("resource_type") if isinstance(res, dict) else res.resource_type
            assert_resource_admissible(pt, rt)
