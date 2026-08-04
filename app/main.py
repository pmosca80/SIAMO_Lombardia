from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.auth_middleware import AuthContextMiddleware
from app.core.config import settings
from app.routers import auth, comunicazione, organizzazione, utente

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# Il frontend (SPA separata) chiama l'API da un'origine diversa: senza CORS
# il browser blocca la risposta prima che arrivi al codice JS del client.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_base_url],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthContextMiddleware)

app.include_router(auth.router)
app.include_router(organizzazione.router)
app.include_router(utente.router)
app.include_router(comunicazione.router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
