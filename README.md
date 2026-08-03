# SIAMO Lombardia

API FastAPI **multi-tenant** per la comunicazione associativa.
Stack: FastAPI · SQLAlchemy (async) · PostgreSQL · Alembic · Railway.

## Architettura

```
app/
├── core/           # config (env) e connessione DB async
├── models/         # modelli ORM  → base.py contiene i mixin multi-tenant
├── schemas/        # modelli Pydantic (I/O API)
├── repositories/   # accesso ai dati (query)  → base.py: CRUD generico
├── services/       # logica applicativa
├── routers/        # endpoint HTTP + dependency injection
└── main.py         # istanza FastAPI
alembic/            # migrazioni (env.py già configurato per engine async)
```

Flusso di una richiesta: **router → service → repository → DB**.

## Multi-tenancy

Il tenant è l'**Organizzazione**. La colonna `organizzazione_id` da propagare
su tutte le tabelle future vive in un unico punto: `TenantMixin`
([app/models/base.py](app/models/base.py)). Ogni nuovo modello la eredita:

```python
class Comunicazione(Base, TenantMixin, TimestampMixin):
    __tablename__ = "comunicazioni"
    id: Mapped[int] = mapped_column(primary_key=True)
    # organizzazione_id è già presente, indicizzata e con FK a organizzazioni
```

Ricordarsi di importare ogni nuovo modello in
[app/models/\_\_init\_\_.py](app/models/__init__.py) così che Alembic lo rilevi.

## Setup locale

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env         # e compilare DATABASE_URL
```

### Migrazioni

```bash
alembic revision --autogenerate -m "crea tabella organizzazioni"
alembic upgrade head
```

### Avvio

```bash
uvicorn app.main:app --reload
```

Docs interattive: <http://localhost:8000/docs> · Health check: `/health`

## Deploy su Railway

1. Aggiungere un servizio **PostgreSQL** → Railway inietta `DATABASE_URL`
   (l'app converte automaticamente lo schema in `postgresql+asyncpg://`).
2. Il [Procfile](Procfile) / [railway.json](railway.json) eseguono
   `alembic upgrade head` prima di avviare Uvicorn su `$PORT`.
