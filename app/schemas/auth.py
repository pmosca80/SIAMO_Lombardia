from pydantic import BaseModel, EmailStr

from app.core.config import settings


class MagicLinkRequest(BaseModel):
    organizzazione_id: int
    email: EmailStr


class MagicLinkRequestRead(BaseModel):
    message: str = "Se l'indirizzo è registrato, riceverai a breve un'email con il link di accesso."
    # Popolato solo quando `debug=True`: nessun invio email reale è
    # configurato in sviluppo, quindi il link viene restituito qui.
    debug_link: str | None = None


class MagicLinkVerify(BaseModel):
    token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = settings.access_token_expire_minutes * 60
