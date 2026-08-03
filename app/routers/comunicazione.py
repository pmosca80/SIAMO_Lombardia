from fastapi import APIRouter, Depends, status

from app.models.utente import RuoloUtente
from app.routers.dependencies import ComunicazioneServiceDep, require_ruoli
from app.schemas.comunicazione import (
    ComunicazioneCreate,
    ComunicazioneRead,
    ComunicazioneUpdate,
)

router = APIRouter(
    prefix="/organizzazioni/{organizzazione_id}/comunicazioni",
    tags=["comunicazioni"],
)

# Creare/modificare/inviare comunicazioni è compito di dirigenti/amministratori;
# i soci possono solo leggerle (route GET, prive di questa dependency).
_gestione_comunicazioni = require_ruoli(RuoloUtente.AMMINISTRATORE, RuoloUtente.OPERATORE)


@router.post(
    "",
    response_model=ComunicazioneRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_gestione_comunicazioni)],
)
async def crea_comunicazione(
    dati: ComunicazioneCreate,
    service: ComunicazioneServiceDep,
) -> ComunicazioneRead:
    return await service.crea(dati)


@router.get("", response_model=list[ComunicazioneRead])
async def lista_comunicazioni(
    service: ComunicazioneServiceDep,
    limit: int = 100,
    offset: int = 0,
) -> list[ComunicazioneRead]:
    return await service.lista(limit=limit, offset=offset)


@router.get("/{comunicazione_id}", response_model=ComunicazioneRead)
async def get_comunicazione(
    comunicazione_id: int,
    service: ComunicazioneServiceDep,
) -> ComunicazioneRead:
    return await service.get(comunicazione_id)


@router.patch(
    "/{comunicazione_id}",
    response_model=ComunicazioneRead,
    dependencies=[Depends(_gestione_comunicazioni)],
)
async def aggiorna_comunicazione(
    comunicazione_id: int,
    dati: ComunicazioneUpdate,
    service: ComunicazioneServiceDep,
) -> ComunicazioneRead:
    return await service.aggiorna(comunicazione_id, dati)


@router.post(
    "/{comunicazione_id}/invia",
    response_model=ComunicazioneRead,
    dependencies=[Depends(_gestione_comunicazioni)],
)
async def invia_comunicazione(
    comunicazione_id: int,
    service: ComunicazioneServiceDep,
) -> ComunicazioneRead:
    return await service.invia(comunicazione_id)


@router.delete(
    "/{comunicazione_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(_gestione_comunicazioni)],
)
async def elimina_comunicazione(
    comunicazione_id: int,
    service: ComunicazioneServiceDep,
) -> None:
    await service.elimina(comunicazione_id)
