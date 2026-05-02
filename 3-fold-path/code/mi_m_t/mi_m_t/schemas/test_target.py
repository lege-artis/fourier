from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TestTargetCreate(BaseModel):
    project_id:        int
    item_code:         str = Field(min_length=1, max_length=100)
    item_name:         str = Field(min_length=3, max_length=255)
    item_type:         Optional[str]  = None
    item_descr:        Optional[str]  = None
    submitter_id:      int
    item_submit_date:  datetime
    severity_by_subm:  Optional[str]  = None
    priority_by_subm:  Optional[str]  = None
    tst_strat_ideas:   Optional[str]  = None
    parent_id:         Optional[int]  = None


class TestTargetRead(BaseModel):
    model_config = {"from_attributes": True}
    id:              int
    project_id:      int
    item_code:       str
    item_name:       str
    item_status:     str
    item_type:       Optional[str]  = None
    tst_strat_ideas: Optional[str]  = None
    parent_id:       Optional[int]  = None
    created_at:      datetime
    updated_at:      datetime


class TestTargetUpdate(BaseModel):
    item_name:        Optional[str] = None
    item_descr:       Optional[str] = None
    item_type:        Optional[str] = None
    severity_by_subm: Optional[str] = None
    priority_by_subm: Optional[str] = None
    tst_strat_ideas:  Optional[str] = None
    attention:        Optional[str] = None
    parent_id:        Optional[int] = None
