# =============================================================================
# mi_m_t/routers/requests.py
# date:    2026-04-29
# citation: ARCH-SPEC §7.5
# =============================================================================
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.deps import get_db, current_user
from mi_m_t.schemas.request_schema import RequestCreate, RequestRead, LinkCasesIn
from mi_m_t.schemas.test_case import TransitionIn
from mi_m_t.schemas.common import Page
from mi_m_t.services.requests import RequestService
from mi_m_t.services.transitions import TransitionService
from mi_m_t.domain.statuses import TransitionError, RoleError

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestRead, status_code=201)
async def create_request(
    payload: RequestCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = RequestService(db)
    return await svc.create(payload, user)


@router.get("", response_model=Page[RequestRead])
async def list_requests(
    project_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = RequestService(db)
    rows, total = await svc.list_page(project_id, page, page_size)
    import math
    total_pages = max(1, math.ceil(total / page_size)) if page_size else 1
    return Page(data=list(rows), total=total, total_pages=total_pages, page=page, page_size=page_size)


@router.get("/{req_id}", response_model=RequestRead)
async def get_request(
    req_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = RequestService(db)
    req = await svc.get(req_id)
    if req is None:
        raise HTTPException(404, f"Request {req_id} not found")
    return req


@router.post("/{req_id}/link-cases", status_code=200)
async def link_cases(
    req_id: int,
    payload: LinkCasesIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = RequestService(db)
    linked = await svc.link_test_cases(req_id, payload)
    return {"request_id": req_id, "linked_test_case_ids": linked}


@router.post("/{req_id}/transition", status_code=200)
async def transition_request(
    req_id: int,
    payload: TransitionIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    svc = TransitionService(db)
    try:
        result = await svc.transition("requests", req_id, payload.to_status, user, payload.note)
    except TransitionError as exc:
        msg = str(exc)
        if "ENTITY_NOT_FOUND" in msg:
            raise HTTPException(404, msg)
        raise HTTPException(409, msg)
    except RoleError as exc:
        raise HTTPException(403, str(exc))
    return result
