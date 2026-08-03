from fastapi import APIRouter, status

from app.routers.dependencies import OrganizzazioneServiceDep
from app.schemas.organizzazione import (
    OrganizzazioneCreate,
    OrganizzazioneRead,
    OrganizzazioneUpdate,
)

router = APIRouter(prefix="/organizzazioni", tags=["organizzazioni"])


@router.post("", response_model=OrganizzazioneRead, status_code=status.HTTP_201_CREATED)
async def crea_organizzazione(
    dati: OrganizzazioneCreate,
    service: OrganizzazioneServiceDep,
) -> OrganizzazioneRead:
    return await service.crea(dati)


@router.get("", response_model=list[OrganizzazioneRead])
async def lista_organizzazioni(
    service: OrganizzazioneServiceDep,
    limit: int = 100,
    offset: int = 0,
) -> list[OrganizzazioneRead]:
    return await service.lista(limit=limit, offset=offset)


@router.get("/{organizzazione_id}", response_model=OrganizzazioneRead)
async def get_organizzazione(
    organizzazione_id: int,
    service: OrganizzazioneServiceDep,
) -> OrganizzazioneRead:
    return await service.get(organizzazione_id)


@router.patch("/{organizzazione_id}", response_model=OrganizzazioneRead)
async def aggiorna_organizzazione(
    organizzazione_id: int,
    dati: OrganizzazioneUpdate,
    service: OrganizzazioneServiceDep,
) -> OrganizzazioneRead:
    return await service.aggiorna(organizzazione_id, dati)


@router.delete("/{organizzazione_id}", status_code=status.HTTP_204_NO_CONTENT)
async def elimina_organizzazione(
    organizzazione_id: int,
    service: OrganizzazioneServiceDep,
) -> None:
    await service.elimina(organizzazione_id)
