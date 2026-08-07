from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

_is_sqlite = settings.database_url.startswith("sqlite")

if _is_sqlite:
    # SQLite (test/dev) usa StaticPool: non accetta pool_size/max_overflow.
    engine = create_async_engine(settings.database_url, echo=settings.debug)
else:
    # pool_size/max_overflow espliciti (invece dei default SQLAlchemy 5+10).
    # pool_recycle: evita errori di connessione chiusa da Railway su
    # connessioni Postgres idle.
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=5,
        max_overflow=5,
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency FastAPI: fornisce una sessione async con gestione commit/rollback."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
