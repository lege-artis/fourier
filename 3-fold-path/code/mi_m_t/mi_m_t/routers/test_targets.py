# =============================================================================
# mi_m_t/routers/test_targets.py
# date:    2026-04-29
# citation: ARCH-SPEC §7.5
# =============================================================================
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.deps import get_db, current_user
from mi_m_t.schemas.test_target import TestTargetCreate, TestTargetRead, TestTargetUpdate
from mi_m_t.schemas.test_case import TransitionIn
from mi_m_t.schemas.common import Page
from mi_m_t.services.test_targets import TestTargetService
from mi_m_t.services.transitions import TransitionService
from mi_m_t.domain.statuses import TransitionError, RoleError

router = APIRouter(prefix="/test-targets", tags=["test-targets"])


@router.post("", response_model=TestTargetRead, status_code=201)
async def create_target(
    payload: TestTargetCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestTargetService(db)
    return await svc.create(payload, user)


@router.get("", response_model=Page[TestTargetRead])
async def list_targets(
    project_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestTargetService(db)
    rows, total = await svc.list_page(project_id, page, page_size)
    import math
    total_pages = max(1, math.ceil(total / page_size)) if page_size else 1
    return Page(data=list(rows), total=total, total_pages=total_pages, page=page, page_size=page_size)


@router.get("/{tt_id}", response_model=TestTargetRead)
async def get_target(
    tt_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestTargetService(db)
    tt = await svc.get(tt_id)
    if tt is None:
        raise HTTPException(404, f"TestTarget {tt_id} not found")
    return tt


@router.patch("/{tt_id}", response_model=TestTargetRead)
async def update_target(
    tt_id: int,
    payload: TestTargetUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestTargetService(db)
    tt = await svc.update(tt_id, payload)
    if tt is None:
        raise HTTPException(404, f"TestTarget {tt_id} not found")
    return tt


@router.post("/{tt_id}/transition", status_code=200)
async def transition_target(
    tt_id: int,
    payload: TransitionIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TransitionService(db)
    try:
        result = await svc.transition("test_targets", tt_id, payload.to_status, user, payload.note)
    except TransitionError as exc:
        msg = str(exc)
        if "ENTITY_NOT_FOUND" in msg:
            raise HTTPException(404, msg)
        raise HTTPException(409, msg)
    except RoleError as exc:
        raise HTTPException(403, str(exc))
    return result
