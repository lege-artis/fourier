# =============================================================================
# mi_m_t/routers/test_runs.py
# date:    2026-04-29
# citation: ARCH-SPEC §7.5, §5.3 (finalize)
# =============================================================================
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.deps import get_db, current_user
from mi_m_t.schemas.test_run import TestRunCreate, TestRunRead, ResultAppend
from mi_m_t.schemas.test_case import TransitionIn
from mi_m_t.schemas.common import Page
from mi_m_t.services.test_runs import TestRunService
from mi_m_t.services.transitions import TransitionService
from mi_m_t.domain.statuses import TransitionError, RoleError

router = APIRouter(prefix="/test-runs", tags=["test-runs"])


@router.post("", response_model=TestRunRead, status_code=201)
async def create_run(
    payload: TestRunCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestRunService(db)
    return await svc.create(payload, user)


@router.get("", response_model=Page[TestRunRead])
async def list_runs(
    project_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestRunService(db)
    rows, total = await svc.list_page(project_id, page, page_size)
    import math
    total_pages = max(1, math.ceil(total / page_size)) if page_size else 1
    return Page(data=list(rows), total=total, total_pages=total_pages, page=page, page_size=page_size)


@router.get("/{run_id}", response_model=TestRunRead)
async def get_run(
    run_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestRunService(db)
    tr = await svc.get(run_id)
    if tr is None:
        raise HTTPException(404, f"TestRun {run_id} not found")
    return tr


@router.post("/{run_id}/results", status_code=200)
async def append_result(
    run_id: int,
    payload: ResultAppend,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestRunService(db)
    return await svc.append_result(run_id, payload)


@router.post("/{run_id}/finalize", response_model=TestRunRead)
async def finalize_run(
    run_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TestRunService(db)
    tr = await svc.finalize(run_id)
    if tr is None:
        raise HTTPException(404, f"TestRun {run_id} not found")
    return tr


@router.post("/{run_id}/transition", status_code=200)
async def transition_run(
    run_id: int,
    payload: TransitionIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TransitionService(db)
    try:
        result = await svc.transition("test_runs", run_id, payload.to_status, user, payload.note)
    except TransitionError as exc:
        msg = str(exc)
        if "ENTITY_NOT_FOUND" in msg:
            raise HTTPException(404, msg)
        raise HTTPException(409, msg)
    except RoleError as exc:
        raise HTTPException(403, str(exc))
    return result
