from fastapi import HTTPException, status

from app.models.membro import Membro
from app.repositories.membro import MembroRepository
from app.schemas.membro import MembroCreate, MembroUpdate


class MembroService:
    def __init__(self, repository: MembroRepository) -> None:
        self.repository = repository

    async def crea(self, dati: MembroCreate) -> Membro:
        if await self.repository.get_by_email(dati.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{dati.email}' già registrata in questa organizzazione.",
            )
        membro = Membro(**dati.model_dump())
        return await self.repository.add(membro)

    async def get(self, id_: int) -> Membro:
        membro = await self.repository.get(id_)
        if membro is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membro non trovato.",
            )
        return membro

    async def lista(self, *, limit: int = 100, offset: int = 0) -> list[Membro]:
        return await self.repository.list(limit=limit, offset=offset)

    async def aggiorna(self, id_: int, dati: MembroUpdate) -> Membro:
        membro = await self.get(id_)
        for campo, valore in dati.model_dump(exclude_unset=True).items():
            setattr(membro, campo, valore)
        return await self.repository.add(membro)

    async def elimina(self, id_: int) -> None:
        membro = await self.get(id_)
        await self.repository.delete(membro)
