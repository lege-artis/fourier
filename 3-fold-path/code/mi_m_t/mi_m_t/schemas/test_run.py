# =============================================================================
# mi_m_t/schemas/test_run.py
# date:    2026-04-30
# citation: ARCH-SPEC §7.5, DDL 011/017
# note:     run_date / executor_id / submitter_id / item_submit_date all NOT NULL
#           test_run_results verdict CHECK: pass|fail|skip|blocked|partial
#           overall_verdict  CHECK:         pass|fail|partial|aborted|in-progress
# =============================================================================
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TestRunCreate(BaseModel):
    project_id:            int
    item_code:             str      = Field(min_length=1, max_length=100)
    item_name:             str      = Field(min_length=3, max_length=255)
    item_descr:            Optional[str]      = None
    submitter_id:          int                # BB-1 NOT NULL
    item_submit_date:      datetime           # BB-1 NOT NULL
    iteration_test_set_id: Optional[int]      = None
    executor_id:           int                # DDL NOT NULL
    run_date:              Optional[datetime] = None  # defaults to now() in service


class ResultAppend(BaseModel):
    """One test-case result row within a run."""
    test_case_id:  int
    verdict:       str            # CHECK: pass|fail|skip|blocked|partial
    actual_result: Optional[str]      = None
    evidence_ref:  Optional[str]      = None
    started_at:    Optional[datetime] = None  # test_run_results.started_at
    finished_at:   Optional[datetime] = None  # test_run_results.finished_at


class TestRunRead(BaseModel):
    model_config = {"from_attributes": True}
    id:                    int
    project_id:            int
    item_code:             str
    item_name:             str
    item_status:           str
    submitter_id:          int
    executor_id:           int
    overall_verdict:       Optional[str]      = None
    iteration_test_set_id: Optional[int]      = None
    run_date:              Optional[datetime] = None
    run_finished_at:       Optional[datetime] = None
    created_at:            datetime
    updated_at:            datetime
