# =============================================================================
# mi_m_t/routers/test_cases.py
# date:    2026-04-29
# citation: ARCH-SPEC §7.5
# =============================================================================
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.deps import get_db, current_user
from mi_m_t.schemas.test_case import TestCaseCreate, TestCaseRead, TransitionIn
from mi_m_t.schemas.common import Page
from mi_m_t.services.test_cases import TestCaseService
from mi_m_t.services.transitions import TransitionService
from mi_m_t.domain.statuses import TransitionError, RoleError

router = APIRouter(prefix="/test-cases", tags=["test-cases"])


@router.post("", status_code=201)
async def create_test_case(
    payload: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestCaseService(db)
    tc = await svc.create(payload, user)
    # get full form with phases
    return await svc.get(tc.id)


@router.get("", response_model=Page[TestCaseRead])
async def list_test_cases(
    project_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestCaseService(db)
    rows, total = await svc.list_page(project_id, page, page_size)
    import math
    total_pages = max(1, math.ceil(total / page_size)) if page_size else 1
    return Page(data=list(rows), total=total, total_pages=total_pages, page=page, page_size=page_size)


@router.get("/{tc_id}")
async def get_test_case(
    tc_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestCaseService(db)
    tc = await svc.get(tc_id)
    if tc is None:
        raise HTTPException(404, f"TestCase {tc_id} not found")
    return tc


@router.post("/{tc_id}/transition", status_code=200)
async def transition_test_case(
    tc_id: int,
    payload: TransitionIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TransitionService(db)
    try:
        result = await svc.transition("test_cases", tc_id, payload.to_status, user, payload.note)
    except TransitionError as exc:
        msg = str(exc)
        if "ENTITY_NOT_FOUND" in msg:
            raise HTTPException(404, msg)
        raise HTTPException(409, msg)
    except RoleError as exc:
        raise HTTPException(403, str(exc))
    return result
