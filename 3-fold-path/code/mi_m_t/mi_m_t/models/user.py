from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from mi_m_t.models.base import Base

_ROLES = "role_in_process IN ('PM','DM','TM','TA','TD','TI','TE','PAn')"

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="ux_users_username"),
        UniqueConstraint("email",    name="ux_users_email"),
        CheckConstraint(_ROLES,      name="ck_users_role"),
    )

    id:              Mapped[int]           = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username:        Mapped[str]           = mapped_column(String(100), nullable=False)
    email:           Mapped[str]           = mapped_column(String(255), nullable=False)
    display_name:    Mapped[str]           = mapped_column(String(255), nullable=False)
    role_in_process: Mapped[str]           = mapped_column(String(10),  nullable=False)
    is_active:       Mapped[int]           = mapped_column(nullable=False, default=1)
    created_at:      Mapped[datetime]      = mapped_column(DateTime, nullable=False)
    updated_at:      Mapped[datetime]      = mapped_column(DateTime, nullable=False)
