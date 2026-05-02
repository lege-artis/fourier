# =============================================================================
# mi_m_t/routers/sync.py — stub 501 routes for JIRA/Zephyr/Postman sync
# date:    2026-04-29
# citation: ARCH-SPEC §7.5 (non-MVP sync stubs), MI-M-T-D03, MI-M-T-D04
# =============================================================================
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.deps import get_db, current_user
from mi_m_t.domain.statuses import ENTITY_TABLES

router = APIRouter(prefix="/sync", tags=["sync"])

_SYSTEMS = {"jira", "zephyr", "postman"}

NOT_IMPL = {"detail": "sync adapter not yet implemented — see D-10 milestone"}


@router.post("/jira/pull/{entity_table}/{entity_id}", status_code=501)
async def jira_pull(entity_table: str, entity_id: int, user=Depends(current_user)):
    raise HTTPException(501, NOT_IMPL["detail"])


@router.post("/jira/push/{entity_table}/{entity_id}", status_code=501)
async def jira_push(entity_table: str, entity_id: int, user=Depends(current_user)):
    raise HTTPException(501, NOT_IMPL["detail"])


@router.post("/zephyr/pull/{entity_table}/{entity_id}", status_code=501)
async def zephyr_pull(entity_table: str, entity_id: int, user=Depends(current_user)):
    raise HTTPException(501, NOT_IMPL["detail"])


@router.post("/postman/pull/{entity_table}/{entity_id}", status_code=501)
async def postman_pull(entity_table: str, entity_id: int, user=Depends(current_user)):
    raise HTTPException(501, NOT_IMPL["detail"])
