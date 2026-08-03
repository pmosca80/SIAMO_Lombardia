from fastapi import HTTPException, status

from app.models.organizzazione import Organizzazione
from app.repositories.organizzazione import OrganizzazioneRepository
from app.schemas.organizzazione import OrganizzazioneCreate, OrganizzazioneUpdate


class OrganizzazioneService:
    """Logica applicativa per le organizzazioni (tenant)."""

    def __init__(self, repository: OrganizzazioneRepository) -> None:
        self.repository = repository

    async def crea(self, dati: OrganizzazioneCreate) -> Organizzazione:
        if await self.repository.get_by_slug(dati.slug) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Slug '{dati.slug}' già in uso.",
            )
        organizzazione = Organizzazione(**dati.model_dump())
        return await self.repository.add(organizzazione)

    async def get(self, id_: int) -> Organizzazione:
        organizzazione = await self.repository.get(id_)
        if organizzazione is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organizzazione non trovata.",
            )
        return organizzazione

    async def lista(self, *, limit: int = 100, offset: int = 0) -> list[Organizzazione]:
        return await self.repository.list(limit=limit, offset=offset)

    async def aggiorna(self, id_: int, dati: OrganizzazioneUpdate) -> Organizzazione:
        organizzazione = await self.get(id_)
        for campo, valore in dati.model_dump(exclude_unset=True).items():
            setattr(organizzazione, campo, valore)
        return await self.repository.add(organizzazione)

    async def elimina(self, id_: int) -> None:
        organizzazione = await self.get(id_)
        await self.repository.delete(organizzazione)
