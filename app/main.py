from fastapi import FastAPI

from app.core.config import settings
from app.routers import comunicazione, organizzazione, utente

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(organizzazione.router)
app.include_router(utente.router)
app.include_router(comunicazione.router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
