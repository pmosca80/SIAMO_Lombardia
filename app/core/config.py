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

    # --- Autenticazione JWT ---
    # In produzione DEVE essere impostata via variabile d'ambiente `JWT_SECRET_KEY`.
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    magic_link_expire_minutes: int = 15

    # Base URL del frontend che completa il login (pagina che legge `?token=`
    # e chiama `POST /auth/verify`).
    frontend_base_url: str = "http://localhost:5173"

    # --- Invio email (Brevo SMTP relay) ---
    # Se `smtp_password` non è impostata, si usa il backend di sviluppo che
    # logga il link invece di inviarlo (vedi `app/core/email.py`).
    smtp_host: str = "smtp-relay.brevo.com"
    smtp_port: int = 587
    smtp_login: str | None = None
    smtp_password: str | None = None
    email_from: str | None = None
    email_from_name: str = "SIAMO Lombardia"

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
