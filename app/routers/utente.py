from fastapi import APIRouter, Depends, status

from app.models.utente import RuoloUtente
from app.routers.dependencies import UtenteServiceDep, require_ruoli
from app.schemas.utente import UtenteCreate, UtenteRead, UtenteUpdate

router = APIRouter(
    prefix="/organizzazioni/{organizzazione_id}/utenti",
    tags=["utenti"],
)

# Gestire l'anagrafica soci è compito di dirigenti/amministratori; i soci
# possono solo consultarla (route GET, prive di questa dependency).
_gestione_utenti = require_ruoli(RuoloUtente.AMMINISTRATORE, RuoloUtente.OPERATORE)


@router.post(
    "",
    response_model=UtenteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_gestione_utenti)],
)
async def crea_utente(dati: UtenteCreate, service: UtenteServiceDep) -> UtenteRead:
    return await service.crea(dati)


@router.get("", response_model=list[UtenteRead])
async def lista_utenti(
    service: UtenteServiceDep,
    limit: int = 100,
    offset: int = 0,
) -> list[UtenteRead]:
    return await service.lista(limit=limit, offset=offset)


@router.get("/{utente_id}", response_model=UtenteRead)
async def get_utente(utente_id: int, service: UtenteServiceDep) -> UtenteRead:
    return await service.get(utente_id)


@router.patch(
    "/{utente_id}",
    response_model=UtenteRead,
    dependencies=[Depends(_gestione_utenti)],
)
async def aggiorna_utente(
    utente_id: int,
    dati: UtenteUpdate,
    service: UtenteServiceDep,
) -> UtenteRead:
    return await service.aggiorna(utente_id, dati)


@router.delete(
    "/{utente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_ruoli(RuoloUtente.AMMINISTRATORE))],
)
async def elimina_utente(utente_id: int, service: UtenteServiceDep) -> None:
    await service.elimina(utente_id)
