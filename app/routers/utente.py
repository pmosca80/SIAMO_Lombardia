from fastapi import APIRouter, status

from app.routers.dependencies import UtenteServiceDep
from app.schemas.utente import UtenteCreate, UtenteRead, UtenteUpdate

router = APIRouter(
    prefix="/organizzazioni/{organizzazione_id}/utenti",
    tags=["utenti"],
)


@router.post("", response_model=UtenteRead, status_code=status.HTTP_201_CREATED)
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


@router.patch("/{utente_id}", response_model=UtenteRead)
async def aggiorna_utente(
    utente_id: int,
    dati: UtenteUpdate,
    service: UtenteServiceDep,
) -> UtenteRead:
    return await service.aggiorna(utente_id, dati)


@router.delete("/{utente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def elimina_utente(utente_id: int, service: UtenteServiceDep) -> None:
    await service.elimina(utente_id)
