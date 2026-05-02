# =============================================================================
# mi_m_t/services/requests.py — RequestService
# tags:    [μS-CAND][TRIG-REQ]
# date:    2026-04-29
# citation: ARCH-SPEC §7.5, OQ-028 (INSERT OR IGNORE → portable delete+insert)
# =============================================================================
from __future__ import annotations
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.models.request import Request
from mi_m_t.schemas.request_schema import RequestCreate, LinkCasesIn


class RequestService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: RequestCreate, user) -> Request:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        async with self.db.begin():
            req = Request(
                project_id=payload.project_id,
                item_code=payload.item_code,
                item_name=payload.item_name,
                item_type=payload.item_type,
                item_descr=payload.item_descr,
                submitter_id=payload.submitter_id,
                item_submit_date=payload.item_submit_date,
                severity_by_subm=payload.severity_by_subm,
                priority_by_subm=payload.priority_by_subm,
                used_prod_build=payload.used_prod_build,
                item_status="new",
                created_at=now,
                updated_at=now,
            )
            self.db.add(req)
        await self.db.refresh(req)
        return req

    async def get(self, req_id: int) -> Request | None:
        result = await self.db.execute(
            select(Request).where(Request.id == req_id)
        )
        return result.scalar_one_or_none()

    async def list_page(
        self,
        project_id: int | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[Request], int]:
        count_result = await self.db.execute(
            text(
                "SELECT COUNT(*) FROM requests"
                + (" WHERE project_id = :pid" if project_id else "")
            ),
            {"pid": project_id} if project_id else {},
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        q = select(Request)
        if project_id is not None:
            q = q.where(Request.project_id == project_id)
        rows = (await self.db.execute(
            q.order_by(Request.id).limit(page_size).offset(offset)
        )).scalars().all()
        return rows, total

    async def link_test_cases(self, req_id: int, payload: LinkCasesIn) -> list[int]:
        """
        Insert request_test_cases rows, skipping duplicates.
        OQ-028 workaround: DELETE existing + re-INSERT for portability
        across SQLite (INSERT OR IGNORE), MySQL (INSERT IGNORE),
        and PostgreSQL (ON CONFLICT DO NOTHING). A delete+insert is
        portable and idempotent for this low-cardinality join.
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        async with self.db.begin():
            for tc_id in payload.test_case_ids:
                await self.db.execute(
                    text(
                        "DELETE FROM request_test_cases"
                        " WHERE request_id = :rid AND test_case_id = :cid"
                    ),
                    {"rid": req_id, "cid": tc_id},
                )
                await self.db.execute(
                    text(
                        "INSERT INTO request_test_cases"
                        " (request_id, test_case_id, link_kind, created_at)"
                        " VALUES (:rid, :cid, :lk, :now)"
                    ),
                    {"rid": req_id, "cid": tc_id, "lk": payload.link_kind, "now": now},
                )
        return payload.test_case_ids
