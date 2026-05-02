# =============================================================================
# mi_m_t/models/base.py — ItemBase BB-1 mixin + DeclarativeBase
# tags:    [μS-CAND][TRIG-REQ]
# date:    2026-04-29
# citation: ARCH-SPEC §7.3 (SQLAlchemy ItemBase mixin verbatim)
# =============================================================================
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, SmallInteger, String, Text, DateTime, CHAR, JSON,
    ForeignKey, CheckConstraint, UniqueConstraint, Index,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, declared_attr,
)


class Base(DeclarativeBase):
    pass


# 12-state CHECK expression — reused by standard_table_args()
_STATUS_CHECK = (
    "item_status IN ('new','in-analysis','confirmed','in-progress','implemented',"
    "'verifying','passed','failed','closed','cancelled','duplicate','deferred')"
)


class ItemBase:
    """BB-1 universal item base. Mixed into every item-table model (ARCH-SPEC §7.3)."""

    id:                   Mapped[int]            = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id:           Mapped[int]            = mapped_column(BigInteger, ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False)
    code_to_impulse:      Mapped[Optional[str]]  = mapped_column(String(100))
    impulse_tree_lvl:     Mapped[Optional[int]]  = mapped_column(SmallInteger)
    extern_tree_path:     Mapped[Optional[str]]  = mapped_column(Text)
    parent_id:            Mapped[Optional[int]]  = mapped_column(BigInteger)
    item_code:            Mapped[str]            = mapped_column(String(100), nullable=False)
    intern_tree_path:     Mapped[Optional[str]]  = mapped_column(Text)
    item_tree_lvl:        Mapped[Optional[int]]  = mapped_column(SmallInteger)
    intern_tree_info:     Mapped[Optional[str]]  = mapped_column(Text)
    ext_int_tree_code:    Mapped[Optional[str]]  = mapped_column(Text)
    item_name:            Mapped[str]            = mapped_column(String(255), nullable=False)
    item_type:            Mapped[Optional[str]]  = mapped_column(String(50))
    item_descr:           Mapped[Optional[str]]  = mapped_column(Text)
    ref:                  Mapped[Optional[str]]  = mapped_column(String(255))
    ref01:                Mapped[Optional[str]]  = mapped_column(String(500))
    ref02:                Mapped[Optional[str]]  = mapped_column(String(100))
    ref03:                Mapped[Optional[str]]  = mapped_column(String(500))
    ref04:                Mapped[Optional[str]]  = mapped_column(String(500))
    ref05:                Mapped[Optional[str]]  = mapped_column(String(500))
    note:                 Mapped[Optional[str]]  = mapped_column(Text)
    submitter_id:         Mapped[int]            = mapped_column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    item_submit_date:     Mapped[datetime]       = mapped_column(DateTime, nullable=False)
    item_manager_id:      Mapped[Optional[int]]  = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    note_to_item_manager: Mapped[Optional[str]]  = mapped_column(Text)
    duplicate_of_id:      Mapped[Optional[int]]  = mapped_column(BigInteger)
    similar_to_id:        Mapped[Optional[int]]  = mapped_column(BigInteger)
    item_status:          Mapped[str]            = mapped_column(String(30), nullable=False)
    date_of_adj_status:   Mapped[Optional[datetime]] = mapped_column(DateTime)
    stat_adj_by_id:       Mapped[Optional[int]]  = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    severity_confirmed:   Mapped[Optional[str]]  = mapped_column(CHAR(1))
    priority_confirmed:   Mapped[Optional[str]]  = mapped_column(CHAR(1))
    attention_confirmed:  Mapped[Optional[str]]  = mapped_column(CHAR(1))
    severity_by_subm:     Mapped[Optional[str]]  = mapped_column(CHAR(1))
    priority_by_subm:     Mapped[Optional[str]]  = mapped_column(CHAR(1))
    attention_by_subm:    Mapped[Optional[str]]  = mapped_column(CHAR(1))
    ext_attrs:            Mapped[Optional[dict]] = mapped_column(JSON)
    correlation_descr:    Mapped[Optional[str]]  = mapped_column(Text)
    created_at:           Mapped[datetime]       = mapped_column(DateTime, nullable=False)
    updated_at:           Mapped[datetime]       = mapped_column(DateTime, nullable=False)

    @classmethod
    def standard_table_args(cls) -> tuple:
        t = cls.__tablename__
        return (
            UniqueConstraint("project_id", "item_code", name=f"ux_{t}_project_code"),
            CheckConstraint("severity_confirmed  IS NULL OR severity_confirmed  IN ('A','B','C','X')", name=f"ck_{t}_sev_conf"),
            CheckConstraint("priority_confirmed  IS NULL OR priority_confirmed  IN ('H','M','L','X')", name=f"ck_{t}_pri_conf"),
            CheckConstraint("attention_confirmed IS NULL OR attention_confirmed IN ('P','S','I','X')", name=f"ck_{t}_att_conf"),
            CheckConstraint("severity_by_subm    IS NULL OR severity_by_subm    IN ('A','B','C','X')", name=f"ck_{t}_sev_subm"),
            CheckConstraint("priority_by_subm    IS NULL OR priority_by_subm    IN ('H','M','L','X')", name=f"ck_{t}_pri_subm"),
            CheckConstraint("attention_by_subm   IS NULL OR attention_by_subm   IN ('P','S','I','X')", name=f"ck_{t}_att_subm"),
            CheckConstraint(_STATUS_CHECK, name=f"ck_{t}_status"),
            Index(f"ix_{t}_status",         "item_status"),
            Index(f"ix_{t}_project_status", "project_id", "item_status"),
            Index(f"ix_{t}_submitter",      "submitter_id"),
            Index(f"ix_{t}_manager",        "item_manager_id"),
            Index(f"ix_{t}_parent",         "parent_id"),
            Index(f"ix_{t}_impulse",        "code_to_impulse"),
            Index(f"ix_{t}_submit_date",    "item_submit_date"),
        )
