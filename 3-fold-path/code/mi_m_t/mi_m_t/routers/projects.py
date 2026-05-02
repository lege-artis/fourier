# =============================================================================
# mi_m_t/routers/projects.py
# date:    2026-04-29
# citation: ARCH-SPEC §7.5
# note:     Project ORM cols are `name` / `description` (not project_name/descr)
# =============================================================================
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mi_m_t.deps import get_db, current_user
from mi_m_t.models.project import Project

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    project_code: str = Field(min_length=1, max_length=50)
    name:         str = Field(min_length=3, max_length=255)
    description:  str | None = None


class ProjectRead(BaseModel):
    model_config = {"from_attributes": True}
    id:           int
    project_code: str
    name:         str
    description:  str | None = None
    status:       str = "active"
    created_at:   datetime
    updated_at:   datetime


@router.post("", response_model=ProjectRead, status_code=201)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    async with db.begin():
        proj = Project(
            project_code=payload.project_code,
            name=payload.name,
            description=payload.description,
            created_at=now,
            updated_at=now,
        )
        db.add(proj)
    await db.refresh(proj)
    return proj


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    rows = (await db.execute(select(Project).order_by(Project.id))).scalars().all()
    return rows


@router.get("/{proj_id}", response_model=ProjectRead)
async def get_project(
    proj_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    result = await db.execute(select(Project).where(Project.id == proj_id))
    proj = result.scalar_one_or_none()
    if proj is None:
        raise HTTPException(404, f"Project {proj_id} not found")
    return proj
