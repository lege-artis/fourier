from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Text, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from mi_m_t.models.base import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("project_code", name="ux_projects_code"),
        CheckConstraint("status IN ('active','archived','deleted')", name="ck_projects_status"),
    )

    id:           Mapped[int]            = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_code: Mapped[str]            = mapped_column(String(20), nullable=False)
    name:         Mapped[str]            = mapped_column(String(255), nullable=False)
    description:  Mapped[Optional[str]]  = mapped_column(Text)
    status:       Mapped[str]            = mapped_column(String(20), nullable=False, default="active")
    created_at:   Mapped[datetime]       = mapped_column(DateTime, nullable=False)
    updated_at:   Mapped[datetime]       = mapped_column(DateTime, nullable=False)
