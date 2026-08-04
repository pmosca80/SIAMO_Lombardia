from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings


class RegistrazioneRequest(BaseModel):
    organizzazione_id: int
    nome: str = Field(..., max_length=120)
    cognome: str = Field(..., max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class MessaggioGenerico(BaseModel):
    message: str


class LoginRequest(BaseModel):
    organizzazione_id: int
    email: EmailStr
    password: str


class PasswordDimenticataRequest(BaseModel):
    organizzazione_id: int
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    nuova_password: str = Field(..., min_length=8, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = settings.access_token_expire_minutes * 60
