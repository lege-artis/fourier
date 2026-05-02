# =============================================================================
# mi_m_t/schemas/common.py — shared Pydantic v2 types + envelope
# citation: ARCH-SPEC §5.2 (pagination envelope, status codes)
# =============================================================================
from __future__ import annotations
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    data:        List[T]
    page:        int
    page_size:   int
    total:       int
    total_pages: int


class Problem(BaseModel):
    """RFC 7807 problem-details response body (ARCH-SPEC §5.2)."""
    type:       str
    title:      str
    status:     int
    detail:     str
    instance:   Optional[str]  = None
    violations: Optional[list] = None


# Literal type aliases shared across schemas
ITEM_STATUS   = str   # validated at Pydantic field level in each schema
SEV           = str
PRI           = str
ATT           = str
