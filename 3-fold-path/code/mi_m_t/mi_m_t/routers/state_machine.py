# =============================================================================
# mi_m_t/routers/state_machine.py
# date:    2026-04-29
# citation: ARCH-SPEC §7.5, §4.2
# =============================================================================
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.deps import get_db, current_user
from mi_m_t.domain.statuses import ENTITY_TABLES

router = APIRouter(prefix="/state-machine", tags=["state-machine"])


@router.get("/{entity_table}")
async def get_state_machine(
    entity_table: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    """Return all active transitions for an entity table."""
    if entity_table not in ENTITY_TABLES:
        raise HTTPException(400, f"Unknown entity_table: '{entity_table}'")
    rows = (await db.execute(
        text(
            "SELECT id, entity_table, from_status, to_status,"
            " requires_role, is_active"
            " FROM item_status_transitions"
            " WHERE entity_table = :et AND is_active = true"  # OQ-034 (D-09)
            " ORDER BY from_status, to_status"
        ),
        {"et": entity_table},
    )).mappings().all()
    return {"entity_table": entity_table, "transitions": [dict(r) for r in rows]}


@router.get("/{entity_table}/{from_status}")
async def get_transitions_from(
    entity_table: str,
    from_status: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    """Return allowed to_status values from a given from_status (fans 'any')."""
    if entity_table not in ENTITY_TABLES:
        raise HTTPException(400, f"Unknown entity_table: '{entity_table}'")
    rows = (await db.execute(
        text(
            "SELECT to_status, requires_role"
            " FROM item_status_transitions"
            " WHERE entity_table = :et"
            "   AND (from_status = :from OR from_status = 'any')"
            "   AND is_active = true"  # OQ-034 (D-09)
            " ORDER BY to_status"
        ),
        {"et": entity_table, "from": from_status},
    )).mappings().all()
    return {
        "entity_table": entity_table,
        "from_status": from_status,
        "allowed_transitions": [dict(r) for r in rows],
    }
