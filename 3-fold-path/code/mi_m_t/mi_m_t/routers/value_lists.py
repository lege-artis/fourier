# =============================================================================
# mi_m_t/routers/value_lists.py — GET /api/v1/value-lists/* (static tables)
# date:    2026-04-29
# citation: ARCH-SPEC §7.5 (value list endpoints)
# =============================================================================
from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.deps import get_db, current_user
from mi_m_t.domain.statuses import STATUSES, ENTITY_TABLES
from mi_m_t.domain.decomposition import PHASE_RESOURCE_MATRIX

router = APIRouter(prefix="/value-lists", tags=["value-lists"])


@router.get("/statuses")
async def get_statuses(user=Depends(current_user)):
    return {"statuses": sorted(STATUSES)}


@router.get("/entity-tables")
async def get_entity_tables(user=Depends(current_user)):
    return {"entity_tables": sorted(ENTITY_TABLES)}


@router.get("/phase-resource-matrix")
async def get_phase_resource_matrix(user=Depends(current_user)):
    return {
        "matrix": {
            phase: sorted(allowed)
            for phase, allowed in PHASE_RESOURCE_MATRIX.items()
        }
    }


@router.get("/item-types")
async def get_item_types(db: AsyncSession = Depends(get_db), user=Depends(current_user)):
    rows = (await db.execute(
        text("SELECT code, label, scope FROM item_type_lkp ORDER BY scope, code")
    )).mappings().all()
    return {"item_types": [dict(r) for r in rows]}


@router.get("/resource-types")
async def get_resource_types(db: AsyncSession = Depends(get_db), user=Depends(current_user)):
    rows = (await db.execute(
        text("SELECT code, label FROM resource_type_lkp ORDER BY code")
    )).mappings().all()
    return {"resource_types": [dict(r) for r in rows]}
