"""Primitive di sicurezza: JWT di accesso e token opachi (magic link, refresh).

I token opachi (magic link, refresh token) sono stringhe casuali ad alta
entropia; nel database viene salvato solo il loro hash SHA-256, mai il
valore in chiaro, cosi' un accesso al DB non permette di autenticarsi.
"""
import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.models.utente import RuoloUtente


class TokenPayload(BaseModel):
    """Claim decodificati di un access token JWT."""

    sub: int  # utente_id
    org: int  # organizzazione_id
    ruolo: RuoloUtente
    jti: str
    exp: int


@dataclass(frozen=True)
class CurrentUser:
    """Identita' autenticata, derivata dal JWT e disponibile ad ogni request."""

    utente_id: int
    organizzazione_id: int
    ruolo: RuoloUtente


def create_access_token(*, utente_id: int, organizzazione_id: int, ruolo: RuoloUtente) -> str:
    now = datetime.now(timezone.utc)
    scadenza = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(utente_id),
        "org": organizzazione_id,
        "ruolo": ruolo.value,
        "jti": uuid.uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int(scadenza.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token scaduto.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido.",
        )
    try:
        return TokenPayload(
            sub=int(payload["sub"]),
            org=int(payload["org"]),
            ruolo=RuoloUtente(payload["ruolo"]),
            jti=payload["jti"],
            exp=payload["exp"],
        )
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido.",
        )


def genera_token_opaco() -> str:
    """Genera un token casuale ad alta entropia (magic link / refresh token)."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def scadenza_da_minuti(minuti: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minuti)


def scadenza_da_giorni(giorni: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=giorni)


def aware_utc(dt: datetime) -> datetime:
    """Normalizza un datetime letto dal DB a UTC-aware.

    SQLite (usato nei test) non conserva il timezone: i valori tornano
    naive pur essendo stati salvati in UTC. Postgres/asyncpg restituisce
    invece datetime gia' aware. Questa funzione rende i due casi
    confrontabili con `datetime.now(timezone.utc)`.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
