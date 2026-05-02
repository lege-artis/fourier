# =============================================================================
# mi_m_t/deps.py — FastAPI dependency injectors
# tags:    [μS-CAND][TRIG-REQ]
# date:    2026-04-29
# citation: ARCH-SPEC §7.1 (deps pattern), §5.2 (auth placeholder)
# =============================================================================
from typing import AsyncGenerator
from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from mi_m_t.db import AsyncSessionFactory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, closed after request."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


class _User:
    """Minimal user stub for MVP. Replaced by real JWT/session auth post-MVP."""
    def __init__(self, user_id: int, role: str):
        self.id = user_id
        self.role_in_process = role


async def current_user(x_user_id: int = Header(default=1),
                       x_user_role: str = Header(default="TM")) -> _User:
    """
    Dev-mode auth: caller passes X-User-Id and X-User-Role headers.
    Post-MVP: replace with JWT bearer token validation.
    """
    return _User(user_id=x_user_id, role=x_user_role)
