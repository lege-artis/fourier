# =============================================================================
# mi_m_t/routers/trace.py — GET /api/v1/trace/{entity_table}/{entity_id}
# date:    2026-04-29
# citation: ARCH-SPEC §7.5, §1.5 (append-only audit trail)
# =============================================================================
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.deps import get_db, current_user
from mi_m_t.domain.statuses import ENTITY_TABLES

router = APIRouter(prefix="/trace", tags=["trace"])


@router.get("/{entity_table}/{entity_id}")
async def get_trace(
    entity_table: str,
    entity_id: int,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    if entity_table not in ENTITY_TABLES:
        raise HTTPException(400, f"Unknown entity_table: '{entity_table}'")

    rows = (await db.execute(
        text(
            "SELECT id, entity_table, entity_id, from_status, to_status,"
            "       changed_by_id, changed_at, note"
            " FROM item_status_history"
            " WHERE entity_table = :et AND entity_id = :eid"
            " ORDER BY changed_at DESC"
            " LIMIT :lim"
        ),
        {"et": entity_table, "eid": entity_id, "lim": limit},
    )).mappings().all()

    return {
        "entity_table": entity_table,
        "entity_id": entity_id,
        "history": [dict(r) for r in rows],
    }
