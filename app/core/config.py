from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazione applicazione, letta da variabili d'ambiente / file .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SIAMO Lombardia"
    environment: str = "development"
    debug: bool = False

    # Su Railway viene iniettata come `DATABASE_URL` dal servizio Postgres.
    database_url: str

    @field_validator("database_url")
    @classmethod
    def _force_async_driver(cls, value: str) -> str:
        """Railway fornisce un URL `postgresql://`; SQLAlchemy async richiede asyncpg."""
        if value.startswith("postgres://"):
            value = value.replace("postgres://", "postgresql+asyncpg://", 1)
        elif value.startswith("postgresql://"):
            value = value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
