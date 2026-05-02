# =============================================================================
# mi_m_t/db.py — async SQLAlchemy engine + session factory
# tags:    [μS-CAND][TRIG-REQ]
# date:    2026-04-29
# citation: ARCH-SPEC §7.1 (sqlalchemy 2.x async), §0.4 (SQLite FK pragma)
# =============================================================================
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import event, text
from mi_m_t.config import settings

_connect_args: dict = {}
_engine_kwargs: dict = {}

if settings.db_driver == "sqlite":
    # SQLite: single-file, check_same_thread=False required for async
    _connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=_connect_args,
    **_engine_kwargs,
)

# SQLite: enable FK enforcement per connection (ARCH-SPEC §0.4)
if settings.db_driver == "sqlite":
    from sqlalchemy import event as _event

    @_event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
