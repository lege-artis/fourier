# =============================================================================
# mi_m_t/services/test_cases.py — TestCaseService
# tags:    [μS-CAND][TRIG-REQ]
# date:    2026-04-29
# citation: ARCH-SPEC §7.5 (service layer), §R-TC-3, §R-TC-5
# =============================================================================
from __future__ import annotations
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mi_m_t.models.test_case import TestCase
from mi_m_t.schemas.test_case import TestCaseCreate, TestCasePhaseIn


class TestCaseService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # CREATE  (with phases + resources in a single transaction)
    # ------------------------------------------------------------------
    async def create(self, payload: TestCaseCreate, user) -> TestCase:
        """
        Persist TestCase + phases + resources atomically.
        Pydantic R-TC-3 / R-TC-5 validators have already run on `payload`.
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        async with self.db.begin():
            tc = TestCase(
                project_id=payload.project_id,
                test_target_id=payload.test_target_id,
                item_code=payload.item_code,
                item_name=payload.item_name,
                item_type=payload.item_type,
                item_descr=payload.item_descr,
                submitter_id=payload.submitter_id,
                item_submit_date=payload.item_submit_date,
                item_manager_id=payload.item_manager_id,
                item_status=payload.item_status,
                severity_by_subm=payload.severity_by_subm,
                priority_by_subm=payload.priority_by_subm,
                attention_by_subm=payload.attention_by_subm,
                ext_attrs=payload.ext_attrs,
                created_at=now,
                updated_at=now,
            )
            self.db.add(tc)
            await self.db.flush()  # get tc.id

            for phase_in in payload.phases:
                phase_id = await self._insert_phase(tc.id, phase_in, now)
                for res_in in phase_in.resources:
                    await self._insert_resource(phase_id, res_in)

        await self.db.refresh(tc)
        return tc

    async def _insert_phase(self, tc_id: int, ph: TestCasePhaseIn, now) -> int:
        await self.db.execute(
            text(
                "INSERT INTO test_case_phases"
                " (test_case_id, phase_type, phase_descr, sort_order, created_at, updated_at)"
                " VALUES (:tc_id, :pt, :pd, :so, :now, :now)"
            ),
            {"tc_id": tc_id, "pt": ph.phase_type, "pd": ph.phase_descr,
             "so": ph.sort_order, "now": now},
        )
        # OQ-033 (D-09): asyncpg cursor has no lastrowid. Use a follow-up SELECT
        # within the same transaction — portable across MySQL / PostgreSQL / SQLite.
        # (test_case_id, phase_type) is unique per test case, so the result is exact.
        row = (await self.db.execute(
            text(
                "SELECT id FROM test_case_phases"
                " WHERE test_case_id = :tc_id AND phase_type = :pt"
                " ORDER BY id DESC LIMIT 1"
            ),
            {"tc_id": tc_id, "pt": ph.phase_type},
        )).one()
        return row[0]

    async def _insert_resource(self, phase_id: int, res) -> None:
        await self.db.execute(
            text(
                "INSERT INTO test_case_phase_resources"
                " (test_case_phase_id, resource_type, resource_id, sort_order, usage_notes)"
                " VALUES (:ph, :rt, :rid, :so, :un)"
            ),
            {"ph": phase_id, "rt": res.resource_type, "rid": res.resource_id,
             "so": res.sort_order, "un": res.usage_notes},
        )

    # ------------------------------------------------------------------
    # GET  (loads phases + resources via raw SQL, returns ORM object)
    # ------------------------------------------------------------------
    async def get(self, tc_id: int) -> TestCase | None:
        result = await self.db.execute(
            select(TestCase).where(TestCase.id == tc_id)
        )
        tc = result.scalar_one_or_none()
        if tc is None:
            return None
        # Eagerly load phases + resources via raw SQL into transient attrs
        phases_rows = (await self.db.execute(
            text("SELECT * FROM test_case_phases WHERE test_case_id = :id ORDER BY sort_order"),
            {"id": tc_id},
        )).mappings().all()
        phases = []
        for ph_row in phases_rows:
            ph = dict(ph_row)
            res_rows = (await self.db.execute(
                text("SELECT * FROM test_case_phase_resources WHERE test_case_phase_id = :pid ORDER BY sort_order"),
                {"pid": ph_row["id"]},
            )).mappings().all()
            ph["resources"] = [dict(r) for r in res_rows]
            phases.append(ph)
        tc.__dict__["phases"] = phases  # transient attr for serialization
        return tc

    # ------------------------------------------------------------------
    # LIST  (paginated, no phases)
    # ------------------------------------------------------------------
    async def list_page(
        self,
        project_id: int | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[TestCase], int]:
        q = select(TestCase)
        if project_id is not None:
            q = q.where(TestCase.project_id == project_id)
        q_total = q
        total_row = (await self.db.execute(
            text(f"SELECT COUNT(*) FROM ({q_total.compile(compile_kwargs={'literal_binds': True})})")
        )).scalar() if False else None  # use simpler approach below

        # Simpler count
        count_result = await self.db.execute(
            text("SELECT COUNT(*) FROM test_cases" + (" WHERE project_id = :pid" if project_id else "")),
            {"pid": project_id} if project_id else {},
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        rows = (await self.db.execute(
            q.order_by(TestCase.id).limit(page_size).offset(offset)
        )).scalars().all()
        return rows, total

    # ------------------------------------------------------------------
    # UPDATE last_run_verdict (called by TestRunService after finalize)
    # ------------------------------------------------------------------
    async def update_last_run_verdict(self, tc_id: int, verdict: str) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.db.execute(
            text(
                "UPDATE test_cases SET last_run_verdict = :v,"
                " last_run_date = :now, updated_at = :now WHERE id = :id"
            ),
            {"v": verdict, "now": now, "id": tc_id},
        )
