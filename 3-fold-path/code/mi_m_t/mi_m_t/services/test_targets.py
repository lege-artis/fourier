# =============================================================================
# mi_m_t/services/test_targets.py — TestTargetService
# tags:    [μS-CAND]
# date:    2026-04-29
# citation: ARCH-SPEC §7.5
# =============================================================================
from __future__ import annotations
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.models.test_target import TestTarget
from mi_m_t.schemas.test_target import TestTargetCreate, TestTargetUpdate


class TestTargetService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: TestTargetCreate, user) -> TestTarget:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        async with self.db.begin():
            tt = TestTarget(
                project_id=payload.project_id,
                item_code=payload.item_code,
                item_name=payload.item_name,
                item_type=payload.item_type,
                item_descr=payload.item_descr,
                submitter_id=payload.submitter_id,
                item_submit_date=payload.item_submit_date,
                severity_by_subm=payload.severity_by_subm,
                priority_by_subm=payload.priority_by_subm,
                tst_strat_ideas=payload.tst_strat_ideas,
                parent_id=payload.parent_id,
                item_status="new",
                created_at=now,
                updated_at=now,
            )
            self.db.add(tt)
        await self.db.refresh(tt)
        return tt

    async def get(self, tt_id: int) -> TestTarget | None:
        result = await self.db.execute(
            select(TestTarget).where(TestTarget.id == tt_id)
        )
        return result.scalar_one_or_none()

    async def list_page(
        self,
        project_id: int | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[TestTarget], int]:
        count_result = await self.db.execute(
            text(
                "SELECT COUNT(*) FROM test_targets"
                + (" WHERE project_id = :pid" if project_id else "")
            ),
            {"pid": project_id} if project_id else {},
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        q = select(TestTarget)
        if project_id is not None:
            q = q.where(TestTarget.project_id == project_id)
        rows = (await self.db.execute(
            q.order_by(TestTarget.id).limit(page_size).offset(offset)
        )).scalars().all()
        return rows, total

    async def update(self, tt_id: int, payload: TestTargetUpdate) -> TestTarget | None:
        tt = await self.get(tt_id)
        if tt is None:
            return None
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        async with self.db.begin():
            data = payload.model_dump(exclude_none=True)
            data["updated_at"] = now
            for k, v in data.items():
                setattr(tt, k, v)
        await self.db.refresh(tt)
        return tt
