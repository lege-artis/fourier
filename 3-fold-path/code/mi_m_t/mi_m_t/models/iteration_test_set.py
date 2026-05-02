# mi_m_t/models/iteration_test_set.py
# Minimal ORM model — needed only for FK resolution by SQLAlchemy mapper.
# iteration_test_sets is a BB-1 item table (ARCH-SPEC §3.x).
from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, String, Date
from mi_m_t.models.base import Base, ItemBase


class IterationTestSet(ItemBase, Base):
    __tablename__ = "iteration_test_sets"
    __table_args__ = ItemBase.standard_table_args.__func__(
        type("_T", (), {"__tablename__": "iteration_test_sets"})
    )

    iteration_label:      Mapped[Optional[str]]      = mapped_column(String(100))
    iteration_start_date: Mapped[Optional[datetime]] = mapped_column(Date)
    iteration_end_date:   Mapped[Optional[datetime]] = mapped_column(Date)
    target_environment_id: Mapped[Optional[int]]     = mapped_column(BigInteger)
