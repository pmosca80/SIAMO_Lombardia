from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.comunicazione import Comunicazione, StatoComunicazione
from app.repositories.comunicazione import ComunicazioneRepository
from app.repositories.membro import MembroRepository
from app.schemas.comunicazione import ComunicazioneCreate, ComunicazioneUpdate


class ComunicazioneService:
    def __init__(
        self,
        repository: ComunicazioneRepository,
        membri: MembroRepository,
    ) -> None:
        self.repository = repository
        self.membri = membri

    async def _valida_autore(self, autore_id: int | None) -> None:
        if autore_id is not None and await self.membri.get(autore_id) is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Autore non valido: nessun membro con questo id nell'organizzazione.",
            )

    async def crea(self, dati: ComunicazioneCreate) -> Comunicazione:
        await self._valida_autore(dati.autore_id)
        comunicazione = Comunicazione(**dati.model_dump())
        return await self.repository.add(comunicazione)

    async def get(self, id_: int) -> Comunicazione:
        comunicazione = await self.repository.get(id_)
        if comunicazione is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comunicazione non trovata.",
            )
        return comunicazione

    async def lista(self, *, limit: int = 100, offset: int = 0) -> list[Comunicazione]:
        return await self.repository.list(limit=limit, offset=offset)

    async def aggiorna(self, id_: int, dati: ComunicazioneUpdate) -> Comunicazione:
        comunicazione = await self.get(id_)
        if comunicazione.stato is StatoComunicazione.INVIATA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Una comunicazione già inviata non può essere modificata.",
            )
        payload = dati.model_dump(exclude_unset=True)
        if "autore_id" in payload:
            await self._valida_autore(payload["autore_id"])
        for campo, valore in payload.items():
            setattr(comunicazione, campo, valore)
        return await self.repository.add(comunicazione)

    async def invia(self, id_: int) -> Comunicazione:
        comunicazione = await self.get(id_)
        if comunicazione.stato is StatoComunicazione.INVIATA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Comunicazione già inviata.",
            )
        comunicazione.stato = StatoComunicazione.INVIATA
        comunicazione.inviata_at = datetime.now(timezone.utc)
        return await self.repository.add(comunicazione)

    async def elimina(self, id_: int) -> None:
        comunicazione = await self.get(id_)
        await self.repository.delete(comunicazione)
