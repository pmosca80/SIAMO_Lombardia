from fastapi import HTTPException, status

from app.models.organizzazione import Organizzazione
from app.models.utente import RuoloUtente, Utente
from app.repositories.organizzazione import OrganizzazioneRepository
from app.repositories.utente import UtenteRepository
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
        dati_org = dati.model_dump(
            exclude={"admin_nome", "admin_cognome", "admin_email"}
        )
        organizzazione = await self.repository.add(Organizzazione(**dati_org))

        # Senza un utente non c'è modo di autenticarsi (login via magic
        # link) per gestire il tenant appena creato: se richiesto, il primo
        # amministratore viene creato contestualmente.
        if dati.admin_email is not None:
            utenti = UtenteRepository(self.repository.session, organizzazione.id)
            await utenti.add(
                Utente(
                    nome=dati.admin_nome,
                    cognome=dati.admin_cognome,
                    email=dati.admin_email,
                    ruolo=RuoloUtente.AMMINISTRATORE,
                )
            )
        return organizzazione

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
