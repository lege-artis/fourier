# =============================================================================
# mi_m_t/services/test_runs.py — TestRunService
# tags:    [μS-CAND]
# date:    2026-04-30  (fix: removed nested begin() after autobegun SELECT)
# citation: ARCH-SPEC §7.5, §5.3 (finalize logic)
# note:     SQLAlchemy 2.x: session.begin() raises InvalidRequestError if
#           autobegin already triggered by a prior SELECT on the same session.
#           Pattern: use db.add()+flush() for ORM inserts; direct execute()
#           for raw DML within existing autobegin; get_db manages commit.
#           Explicit async with db.begin() is only safe as the FIRST op on
#           a fresh session (create() methods). Never call begin() after any
#           SELECT on the same session instance.
# =============================================================================
from __future__ import annotations
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.models.test_run import TestRun
from mi_m_t.schemas.test_run import TestRunCreate, ResultAppend


# Priority order (worst-first) for per-case verdicts (DDL CHECK: pass|fail|skip|blocked|partial)
_VERDICT_PRIORITY = ["fail", "blocked", "partial", "skip", "pass"]


def _aggregate_verdict(verdicts: list[str]) -> str:
    """
    Collapse per-case verdicts → overall_verdict (DDL CHECK: pass|fail|partial|...).
    fail     → 'fail'
    blocked  → 'partial'
    partial  → 'partial'
    skip     → 'partial'
    pass     → 'pass'
    """
    for v in _VERDICT_PRIORITY:
        if v in verdicts:
            if v == "fail":
                return "fail"
            if v in ("blocked", "partial", "skip"):
                return "partial"
            return "pass"
    return "partial"


class TestRunService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: TestRunCreate, user) -> TestRun:
        """
        create() is called as the FIRST operation on a fresh session (no prior
        SELECT), so async with db.begin() is safe here.
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        async with self.db.begin():
            tr = TestRun(
                project_id=payload.project_id,
                item_code=payload.item_code,
                item_name=payload.item_name,
                item_descr=payload.item_descr,
                submitter_id=payload.submitter_id,
                item_submit_date=payload.item_submit_date,
                iteration_test_set_id=payload.iteration_test_set_id,
                executor_id=payload.executor_id,
                run_date=payload.run_date or now,
                item_status="new",
                created_at=now,
                updated_at=now,
            )
            self.db.add(tr)
        await self.db.refresh(tr)
        return tr

    async def get(self, run_id: int) -> TestRun | None:
        result = await self.db.execute(
            select(TestRun).where(TestRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def list_page(
        self,
        project_id: int | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[TestRun], int]:
        count_result = await self.db.execute(
            text(
                "SELECT COUNT(*) FROM test_runs"
                + (" WHERE project_id = :pid" if project_id else "")
            ),
            {"pid": project_id} if project_id else {},
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        q = select(TestRun)
        if project_id is not None:
            q = q.where(TestRun.project_id == project_id)
        rows = (await self.db.execute(
            q.order_by(TestRun.id).limit(page_size).offset(offset)
        )).scalars().all()
        return rows, total

    async def append_result(self, run_id: int, payload: ResultAppend) -> dict:
        """
        Upsert a test_run_results row.
        NOTE: Called after svc.get() in the router, so autobegin is already
        active — must NOT wrap in async with db.begin() (raises InvalidRequestError).
        DML executes within the existing autobegin; get_db commits on response.
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        # Portable upsert: DELETE + INSERT
        await self.db.execute(
            text(
                "DELETE FROM test_run_results"
                " WHERE test_run_id = :rid AND test_case_id = :cid"
            ),
            {"rid": run_id, "cid": payload.test_case_id},
        )
        await self.db.execute(
            text(
                "INSERT INTO test_run_results"
                " (test_run_id, test_case_id, verdict, actual_result,"
                "  evidence_ref, started_at, finished_at, created_at)"
                " VALUES (:rid, :cid, :v, :ar, :er, :sa, :fa, :now)"
            ),
            {
                "rid": run_id,
                "cid": payload.test_case_id,
                "v":   payload.verdict,
                "ar":  payload.actual_result,
                "er":  payload.evidence_ref,
                "sa":  payload.started_at,
                "fa":  payload.finished_at,
                "now": now,
            },
        )
        # Flush so SELECT below sees the inserted row within the same transaction
        await self.db.flush()
        row = (await self.db.execute(
            text(
                "SELECT * FROM test_run_results"
                " WHERE test_run_id = :rid AND test_case_id = :cid"
            ),
            {"rid": run_id, "cid": payload.test_case_id},
        )).mappings().first()
        return dict(row) if row else {}

    async def finalize(self, run_id: int) -> TestRun | None:
        """
        Compute overall_verdict; stamp run_finished_at; set item_status.
        NOTE: self.get() triggers autobegin — must NOT call async with db.begin()
        afterwards. Executes UPDATE in existing autobegin; get_db commits.
        """
        tr = await self.get(run_id)
        if tr is None:
            return None
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        verdict_rows = (await self.db.execute(
            text("SELECT verdict FROM test_run_results WHERE test_run_id = :rid"),
            {"rid": run_id},
        )).scalars().all()

        verdicts = list(verdict_rows)
        overall = _aggregate_verdict(verdicts) if verdicts else "partial"
        new_status = "passed" if overall == "pass" else "failed"

        await self.db.execute(
            text(
                "UPDATE test_runs"
                " SET overall_verdict = :ov, run_finished_at = :now,"
                "     item_status = :st, updated_at = :now"
                " WHERE id = :id"
            ),
            {"ov": overall, "now": now, "st": new_status, "id": run_id},
        )
        await self.db.flush()
        # Re-fetch to return updated state
        await self.db.refresh(tr)
        return tr
