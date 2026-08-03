"""Configurazione dei test end-to-end.

I test girano contro un database SQLite in-memory creato da
`Base.metadata.create_all`: nessun Postgres né credenziali necessarie.
La dependency `get_session` dell'app viene sostituita con una sessione
legata all'engine di test.
"""
import os

# Deve avvenire prima di importare qualsiasi modulo dell'app: `Settings`
# richiede DATABASE_URL già al momento dell'import.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import get_session
from app.main import app
from app.models import Base


@pytest_asyncio.fixture
async def engine():
    """Engine SQLite in-memory con schema ricreato per ogni test."""
    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def client(engine):
    """AsyncClient httpx collegato all'app via ASGI, con sessione di test."""
    TestSession = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_session():
        async with TestSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def organizzazione(client):
    """Crea un'organizzazione di supporto e ne restituisce la rappresentazione."""
    resp = await client.post(
        "/organizzazioni", json={"nome": "Associazione Test", "slug": "assoc-test"}
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
