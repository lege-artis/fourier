from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Text, UniqueConstraint, Index
from mi_m_t.models.base import Base


class ItemStatusTransition(Base):
    __tablename__ = "item_status_transitions"
    __table_args__ = (
        UniqueConstraint("entity_table", "from_status", "to_status", name="ux_ist_triple"),
        Index("ix_ist_lookup", "entity_table", "from_status", "is_active"),
    )

    id:             Mapped[int]           = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity_table:   Mapped[str]           = mapped_column(String(50), nullable=False)
    from_status:    Mapped[str]           = mapped_column(String(30), nullable=False)
    to_status:      Mapped[str]           = mapped_column(String(30), nullable=False)
    requires_role:  Mapped[Optional[str]] = mapped_column(String(10))
    description:    Mapped[Optional[str]] = mapped_column(Text)
    is_active:      Mapped[int]           = mapped_column(nullable=False, default=1)
