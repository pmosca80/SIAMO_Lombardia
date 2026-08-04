from fastapi import APIRouter, status

from app.routers.dependencies import AuthServiceDep
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MessaggioGenerico,
    PasswordDimenticataRequest,
    RefreshRequest,
    RegistrazioneRequest,
    ResetPasswordRequest,
    TokenPair,
)

router = APIRouter(prefix="/auth", tags=["autenticazione"])

_MESSAGGIO_REGISTRAZIONE = MessaggioGenerico(
    message="Se l'indirizzo non è già registrato, riceverai a breve un'email per confermarlo."
)
_MESSAGGIO_RESET = MessaggioGenerico(
    message="Se l'indirizzo è registrato, riceverai a breve un'email per reimpostare la password."
)


@router.post("/registrati", response_model=MessaggioGenerico, status_code=status.HTTP_201_CREATED)
async def registrati(dati: RegistrazioneRequest, service: AuthServiceDep) -> MessaggioGenerico:
    await service.registra(
        organizzazione_id=dati.organizzazione_id,
        nome=dati.nome,
        cognome=dati.cognome,
        email=dati.email,
        password=dati.password,
    )
    return _MESSAGGIO_REGISTRAZIONE


@router.post("/verifica-email", response_model=TokenPair)
async def verifica_email(token: str, service: AuthServiceDep) -> TokenPair:
    access_token, refresh_token, _utente = await service.verifica_email(token)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenPair)
async def login(dati: LoginRequest, service: AuthServiceDep) -> TokenPair:
    access_token, refresh_token = await service.login(
        organizzazione_id=dati.organizzazione_id, email=dati.email, password=dati.password
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/password-dimenticata", response_model=MessaggioGenerico)
async def password_dimenticata(
    dati: PasswordDimenticataRequest, service: AuthServiceDep
) -> MessaggioGenerico:
    await service.richiedi_reset_password(
        organizzazione_id=dati.organizzazione_id, email=dati.email
    )
    return _MESSAGGIO_RESET


@router.post("/reset-password", response_model=MessaggioGenerico)
async def reset_password(dati: ResetPasswordRequest, service: AuthServiceDep) -> MessaggioGenerico:
    await service.reset_password(token=dati.token, nuova_password=dati.nuova_password)
    return MessaggioGenerico(message="Password aggiornata. Accedi con le nuove credenziali.")


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(dati: RefreshRequest, service: AuthServiceDep) -> TokenPair:
    access_token, refresh_token_ = await service.refresh(dati.refresh_token)
    return TokenPair(access_token=access_token, refresh_token=refresh_token_)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(dati: LogoutRequest, service: AuthServiceDep) -> None:
    await service.logout(dati.refresh_token)
