from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, Text
from mi_m_t.models.base import Base, ItemBase


class TestTarget(ItemBase, Base):
    __tablename__ = "test_targets"

    @classmethod
    def __table_args_extra__(cls):
        return ()

    __table_args__ = ItemBase.standard_table_args.__func__(
        type("_T", (), {"__tablename__": "test_targets"})
    )

    # Entity-specific delta column (ARCH-SPEC §2.1)
    tst_strat_ideas: Mapped[Optional[str]] = mapped_column(Text)
