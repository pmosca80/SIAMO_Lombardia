from fastapi import FastAPI

from app.core.config import settings
from app.routers import organizzazione

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(organizzazione.router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
