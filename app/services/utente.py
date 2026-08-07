import asyncio

from fastapi import HTTPException, status

from app.core.security import hash_password
from app.models.utente import Utente
from app.repositories.utente import UtenteRepository
from app.schemas.utente import UtenteCreate, UtenteUpdate


class UtenteService:
    def __init__(self, repository: UtenteRepository) -> None:
        self.repository = repository

    async def crea(self, dati: UtenteCreate) -> Utente:
        if await self.repository.get_by_email(dati.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{dati.email}' già registrata in questa organizzazione.",
            )
        dati_utente = dati.model_dump(exclude={"password"})
        if dati.password is not None:
            dati_utente["password_hash"] = await asyncio.to_thread(hash_password, dati.password)
        utente = Utente(**dati_utente)
        return await self.repository.add(utente)

    async def get(self, id_: int) -> Utente:
        utente = await self.repository.get(id_)
        if utente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utente non trovato.",
            )
        return utente

    async def lista(self, *, limit: int = 100, offset: int = 0) -> list[Utente]:
        return await self.repository.list(limit=limit, offset=offset)

    async def aggiorna(self, id_: int, dati: UtenteUpdate) -> Utente:
        utente = await self.get(id_)
        for campo, valore in dati.model_dump(exclude_unset=True).items():
            setattr(utente, campo, valore)
        return await self.repository.add(utente)

    async def elimina(self, id_: int) -> None:
        utente = await self.get(id_)
        await self.repository.delete(utente)
