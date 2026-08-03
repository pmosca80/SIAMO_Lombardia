from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.organizzazione import OrganizzazioneRepository
from app.services.organizzazione import OrganizzazioneService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_organizzazione_service(session: SessionDep) -> OrganizzazioneService:
    return OrganizzazioneService(OrganizzazioneRepository(session))


OrganizzazioneServiceDep = Annotated[
    OrganizzazioneService, Depends(get_organizzazione_service)
]
