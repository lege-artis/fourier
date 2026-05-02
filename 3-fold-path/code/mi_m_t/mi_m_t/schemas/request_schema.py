from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

ITEM_TYPE = Literal["bug", "change_request"]


class RequestCreate(BaseModel):
    project_id:        int
    item_code:         str = Field(min_length=1, max_length=100)
    item_name:         str = Field(min_length=3, max_length=255)
    item_type:         ITEM_TYPE
    item_descr:        Optional[str] = None
    submitter_id:      int
    item_submit_date:  datetime
    severity_by_subm:  Optional[str] = None
    priority_by_subm:  Optional[str] = None
    used_prod_build:   Optional[str] = None


class RequestRead(BaseModel):
    model_config = {"from_attributes": True}
    id:              int
    project_id:      int
    item_code:       str
    item_name:       str
    item_status:     str
    item_type:       str
    severity_by_subm: Optional[str] = None
    priority_by_subm: Optional[str] = None
    created_at:      datetime
    updated_at:      datetime


class LinkCasesIn(BaseModel):
    test_case_ids: list[int]
    link_kind:     str = "covers"
