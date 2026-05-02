# =============================================================================
# mi_m_t/models/test_run.py
# date:    2026-04-30
# citation: ARCH-SPEC §7.3, DDL 011
# note:     run_date + executor_id are NOT NULL per DDL (corrected from Optional)
# =============================================================================
from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, String, DateTime, CheckConstraint, Index
from mi_m_t.models.base import Base, ItemBase

_VERDICT_CHECK = "overall_verdict IN ('pass','fail','partial','aborted','in-progress')"

class TestRun(ItemBase, Base):
    __tablename__ = "test_runs"
    __table_args__ = (
        *ItemBase.standard_table_args.__func__(
            type("_T", (), {"__tablename__": "test_runs"})
        ),
        CheckConstraint(_VERDICT_CHECK, name="ck_test_runs_overall"),
        Index("ix_test_runs_executor", "executor_id"),
        Index("ix_test_runs_its",      "iteration_test_set_id"),
    )

    iteration_test_set_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("iteration_test_sets.id", ondelete="SET NULL"))
    executor_id:           Mapped[int]           = mapped_column(BigInteger, ForeignKey("users.id",               ondelete="RESTRICT"), nullable=False)
    overall_verdict:       Mapped[Optional[str]] = mapped_column(String(20))
    run_date:              Mapped[datetime]      = mapped_column(DateTime, nullable=False)
    run_finished_at:       Mapped[Optional[datetime]] = mapped_column(DateTime)
