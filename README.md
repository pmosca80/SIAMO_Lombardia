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

## Modello dati

Sei entità, tutte tenant-scoped tranne l'organizzazione (radice):

- **organizzazioni** — il tenant. Eliminandola, cascata su tutto (`ON DELETE CASCADE`).
- **utenti** — persone dell'associazione (ruolo: amministratore/operatore/socio);
  email unica per organizzazione.
- **campagne** — raggruppano comunicazioni; nome unico per organizzazione.
- **comunicazioni** — messaggi; opzionalmente legate a una campagna e a un
  utente autore (`ON DELETE SET NULL`); stato bozza → inviata.
- **documenti** — allegati o libreria documentale; legame opzionale alla
  comunicazione (`SET NULL`).
- **letture** — ricevute di lettura: coppia (comunicazione, utente) unica.

## Multi-tenancy

Il tenant è l'**Organizzazione**. La colonna `organizzazione_id` da propagare
su tutte le tabelle future vive in un unico punto: `TenantMixin`
([app/models/base.py](app/models/base.py)). Ogni nuovo modello la eredita:

```python
class Utente(Base, TenantMixin, TimestampMixin):
    __tablename__ = "utenti"
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
