from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.comunicazione import ComunicazioneRepository
from app.repositories.membro import MembroRepository
from app.repositories.organizzazione import OrganizzazioneRepository
from app.services.comunicazione import ComunicazioneService
from app.services.membro import MembroService
from app.services.organizzazione import OrganizzazioneService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# --- Organizzazione (tenant radice) ---------------------------------------

def get_organizzazione_service(session: SessionDep) -> OrganizzazioneService:
    return OrganizzazioneService(OrganizzazioneRepository(session))


OrganizzazioneServiceDep = Annotated[
    OrganizzazioneService, Depends(get_organizzazione_service)
]


async def get_tenant_id(
    organizzazione_id: int,
    service: OrganizzazioneServiceDep,
) -> int:
    """Estrae l'`organizzazione_id` dal path e ne verifica l'esistenza (404).

    È il punto di ingresso del contesto multi-tenant: tutti i router annidati
    ricevono un tenant già validato.
    """
    await service.get(organizzazione_id)
    return organizzazione_id


TenantId = Annotated[int, Depends(get_tenant_id)]


# --- Entità tenant-scoped -------------------------------------------------

def get_membro_service(session: SessionDep, tenant_id: TenantId) -> MembroService:
    return MembroService(MembroRepository(session, tenant_id))


MembroServiceDep = Annotated[MembroService, Depends(get_membro_service)]


def get_comunicazione_service(
    session: SessionDep,
    tenant_id: TenantId,
) -> ComunicazioneService:
    return ComunicazioneService(
        ComunicazioneRepository(session, tenant_id),
        MembroRepository(session, tenant_id),
    )


ComunicazioneServiceDep = Annotated[
    ComunicazioneService, Depends(get_comunicazione_service)
]
