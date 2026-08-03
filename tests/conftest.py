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
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-non-per-produzione")
# In debug l'endpoint /auth/magic-link espone il link generato nella risposta
# (nessun invio email reale nei test): è così che i test recuperano il token.
os.environ.setdefault("DEBUG", "true")

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
async def db_session(engine):
    """Sessione ORM diretta sull'engine di test (per i test a livello di modello)."""
    TestSession = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with TestSession() as session:
        yield session


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
async def autentica(client):
    """Factory fixture: esegue il login via magic link e ritorna l'access token.

    Passa dal flusso HTTP reale (`/auth/magic-link` + `/auth/verify`) invece
    di generare il token direttamente, così i test esercitano lo stesso
    percorso usato in produzione.
    """

    async def _autentica(*, organizzazione_id: int, email: str) -> str:
        resp = await client.post(
            "/auth/magic-link",
            json={"organizzazione_id": organizzazione_id, "email": email},
        )
        assert resp.status_code == 200, resp.text
        debug_link = resp.json()["debug_link"]
        assert debug_link is not None, "debug_link assente: DEBUG non è true nei test?"
        token = debug_link.split("token=", 1)[1]

        resp = await client.post("/auth/verify", json={"token": token})
        assert resp.status_code == 200, resp.text
        return resp.json()["access_token"]

    return _autentica


@pytest_asyncio.fixture
async def organizzazione(client, autentica):
    """Crea un'organizzazione con il primo utente amministratore, effettua il
    login e imposta l'header `Authorization` di default sul client di test:
    le chiamate successive nel test sono così già autenticate come admin.
    """
    resp = await client.post(
        "/organizzazioni",
        json={
            "nome": "Associazione Test",
            "slug": "assoc-test",
            "admin_nome": "Admin",
            "admin_cognome": "Test",
            "admin_email": "admin@assoc-test.example.com",
        },
    )
    assert resp.status_code == 201, resp.text
    org = resp.json()

    token = await autentica(
        organizzazione_id=org["id"], email="admin@assoc-test.example.com"
    )
    client.headers["Authorization"] = f"Bearer {token}"
    return org
