from fastapi import APIRouter, status

from app.routers.dependencies import AuthServiceDep
from app.schemas.auth import (
    LogoutRequest,
    MagicLinkRequest,
    MagicLinkRequestRead,
    MagicLinkVerify,
    RefreshRequest,
    TokenPair,
)

router = APIRouter(prefix="/auth", tags=["autenticazione"])


@router.post("/magic-link", response_model=MagicLinkRequestRead)
async def richiedi_magic_link(
    dati: MagicLinkRequest, service: AuthServiceDep
) -> MagicLinkRequestRead:
    link = await service.richiedi_magic_link(
        organizzazione_id=dati.organizzazione_id, email=dati.email
    )
    return MagicLinkRequestRead(debug_link=link)


@router.post("/verify", response_model=TokenPair)
async def verifica_magic_link(dati: MagicLinkVerify, service: AuthServiceDep) -> TokenPair:
    access_token, refresh_token, _utente = await service.verifica_magic_link(dati.token)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(dati: RefreshRequest, service: AuthServiceDep) -> TokenPair:
    access_token, refresh_token_ = await service.refresh(dati.refresh_token)
    return TokenPair(access_token=access_token, refresh_token=refresh_token_)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(dati: LogoutRequest, service: AuthServiceDep) -> None:
    await service.logout(dati.refresh_token)
