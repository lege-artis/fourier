from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, String, CheckConstraint
from mi_m_t.models.base import Base, ItemBase


class Request(ItemBase, Base):
    __tablename__ = "requests"
    __table_args__ = (
        *ItemBase.standard_table_args.__func__(
            type("_T", (), {"__tablename__": "requests"})
        ),
        CheckConstraint("item_type IN ('bug','change_request')", name="ck_requests_item_type"),
    )

    used_prod_build: Mapped[Optional[str]] = mapped_column(String(100))
