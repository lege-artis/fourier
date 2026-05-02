from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from mi_m_t.models.base import Base, ItemBase


class TestCase(ItemBase, Base):
    __tablename__ = "test_cases"
    __table_args__ = ItemBase.standard_table_args.__func__(
        type("_T", (), {"__tablename__": "test_cases"})
    )

    test_target_id:   Mapped[Optional[int]]      = mapped_column(BigInteger, ForeignKey("test_targets.id", ondelete="SET NULL"))
    last_run_date:    Mapped[Optional[datetime]]  = mapped_column(DateTime)   # OQ-032: was String(30), PG rejects VARCHAR→TIMESTAMP
    last_run_verdict: Mapped[Optional[str]]       = mapped_column(String(20))
