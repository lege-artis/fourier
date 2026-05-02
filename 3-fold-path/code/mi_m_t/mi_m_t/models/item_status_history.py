from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey, CheckConstraint, Index
from mi_m_t.models.base import Base

_ENTITY_TABLES = (
    "entity_table IN ('test_targets','test_cases','test_scripts','test_data',"
    "'test_environments','iteration_test_sets','test_runs','requests')"
)

class ItemStatusHistory(Base):
    __tablename__ = "item_status_history"
    __table_args__ = (
        CheckConstraint(_ENTITY_TABLES, name="ck_ish_entity_table"),
        Index("ix_ish_entity", "entity_table", "entity_id", "changed_at"),
    )

    id:            Mapped[int]           = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity_table:  Mapped[str]           = mapped_column(String(50), nullable=False)
    entity_id:     Mapped[int]           = mapped_column(BigInteger, nullable=False)
    from_status:   Mapped[Optional[str]] = mapped_column(String(30))
    to_status:     Mapped[str]           = mapped_column(String(30), nullable=False)
    changed_by_id: Mapped[int]           = mapped_column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    changed_at:    Mapped[datetime]      = mapped_column(DateTime, nullable=False)
    note:          Mapped[Optional[str]] = mapped_column(Text)
