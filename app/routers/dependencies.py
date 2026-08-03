from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.campagna import CampagnaRepository
from app.repositories.comunicazione import ComunicazioneRepository
from app.repositories.organizzazione import OrganizzazioneRepository
from app.repositories.utente import UtenteRepository
from app.services.comunicazione import ComunicazioneService
from app.services.organizzazione import OrganizzazioneService
from app.services.utente import UtenteService

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

def get_utente_service(session: SessionDep, tenant_id: TenantId) -> UtenteService:
    return UtenteService(UtenteRepository(session, tenant_id))


UtenteServiceDep = Annotated[UtenteService, Depends(get_utente_service)]


def get_comunicazione_service(
    session: SessionDep,
    tenant_id: TenantId,
) -> ComunicazioneService:
    return ComunicazioneService(
        ComunicazioneRepository(session, tenant_id),
        UtenteRepository(session, tenant_id),
        CampagnaRepository(session, tenant_id),
    )


ComunicazioneServiceDep = Annotated[
    ComunicazioneService, Depends(get_comunicazione_service)
]
