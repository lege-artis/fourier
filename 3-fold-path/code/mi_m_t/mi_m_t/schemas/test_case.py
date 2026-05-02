# =============================================================================
# mi_m_t/schemas/test_case.py — Pydantic v2 schemas for test_cases
# citation: ARCH-SPEC §7.4 (canonical Pydantic schema), §R-TC-3, §R-TC-5
# =============================================================================
from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator

PHASE_TYPE    = Literal["pre", "exec", "post"]
RESOURCE_TYPE = Literal[
    "test_script", "test_data", "test_environment",
    "test_procedure", "test_component", "test_user",
]
ADMISSIBILITY: dict[str, set[str]] = {
    "pre":  {"test_data", "test_procedure"},
    "exec": {"test_script", "test_data", "test_environment", "test_component", "test_user"},
    "post": {"test_data", "test_procedure"},
}
ITEM_TYPE = Literal[
    "functional","regression","smoke","negative","boundary",
    "performance","security","exploratory","other",
]
ITEM_STATUS = Literal[
    "new","in-analysis","confirmed","in-progress","implemented",
    "verifying","passed","failed","closed","cancelled","duplicate","deferred",
]
SEV = Literal["A","B","C","X"]
PRI = Literal["H","M","L","X"]
ATT = Literal["P","S","I","X"]


class PhaseResourceIn(BaseModel):
    resource_type: RESOURCE_TYPE
    resource_id:   int
    sort_order:    int = 0
    usage_notes:   Optional[str] = None


class TestCasePhaseIn(BaseModel):
    phase_type:  PHASE_TYPE
    phase_descr: Optional[str] = None
    sort_order:  int = 0
    resources:   List[PhaseResourceIn] = []

    @field_validator("resources")
    @classmethod
    def admissible(cls, resources, info):
        """R-TC-5: resource_type must be admissible for phase_type."""
        phase_type = info.data.get("phase_type")
        if phase_type is None:
            return resources
        allowed = ADMISSIBILITY.get(phase_type, set())
        for r in resources:
            if r.resource_type not in allowed:
                raise ValueError(
                    f"R-TC-5: {r.resource_type} not admissible in phase {phase_type}. "
                    f"Allowed: {sorted(allowed)}"
                )
        return resources


class TestCaseCreate(BaseModel):
    project_id:        int
    test_target_id:    int
    item_code:         str = Field(min_length=1, max_length=100)
    item_name:         str = Field(min_length=3, max_length=255)
    item_type:         Optional[ITEM_TYPE]  = None
    item_descr:        Optional[str]        = None
    submitter_id:      int
    item_submit_date:  datetime
    item_manager_id:   Optional[int]        = None
    item_status:       ITEM_STATUS          = "new"
    severity_by_subm:  Optional[SEV]        = None
    priority_by_subm:  Optional[PRI]        = None
    attention_by_subm: Optional[ATT]        = None
    ext_attrs:         Optional[dict]       = None
    phases:            List[TestCasePhaseIn]

    @field_validator("phases")
    @classmethod
    def must_have_all_phase_types(cls, phases):
        """R-TC-3: pre, exec, post phases all required."""
        present = {p.phase_type for p in phases}
        missing = {"pre", "exec", "post"} - present
        if missing:
            raise ValueError(f"R-TC-3: missing phase_type(s): {', '.join(sorted(missing))}")
        seen: set[str] = set()
        for p in phases:
            if p.phase_type in seen:
                raise ValueError(f"duplicate phase_type: {p.phase_type}")
            seen.add(p.phase_type)
        return phases


class PhaseResourceRead(BaseModel):
    model_config = {"from_attributes": True}
    id:            int
    phase_id:      int
    resource_type: str
    resource_id:   int
    usage_notes:   Optional[str] = None


class TestCasePhaseRead(BaseModel):
    model_config = {"from_attributes": True}
    id:          int
    test_case_id: int
    phase_type:  str
    phase_descr: Optional[str] = None
    sort_order:  int
    resources:   List[PhaseResourceRead] = []


class TestCaseRead(BaseModel):
    model_config = {"from_attributes": True}
    id:               int
    project_id:       int
    item_code:        str
    item_name:        str
    item_status:      str
    item_type:        Optional[str]      = None
    test_target_id:   Optional[int]      = None
    submitter_id:     int
    item_submit_date: datetime
    last_run_verdict: Optional[str]      = None
    created_at:       datetime
    updated_at:       datetime
    phases:           List[TestCasePhaseRead] = []


class TransitionIn(BaseModel):
    to_status: ITEM_STATUS
    note:      Optional[str] = None
