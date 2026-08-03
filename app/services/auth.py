from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.email import EmailSender
from app.core.security import (
    create_access_token,
    genera_token_opaco,
    hash_token,
    scadenza_da_giorni,
    scadenza_da_minuti,
)
from app.models.utente import Utente
from app.repositories.magic_link import MagicLinkRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.utente import UtenteRepository


class AuthService:
    """Login passwordless via magic link + coppia di token JWT/refresh."""

    def __init__(
        self,
        session: AsyncSession,
        magic_link_repo: MagicLinkRepository,
        refresh_repo: RefreshTokenRepository,
        email_sender: EmailSender,
    ) -> None:
        self.session = session
        self.magic_link_repo = magic_link_repo
        self.refresh_repo = refresh_repo
        self.email_sender = email_sender

    async def richiedi_magic_link(
        self, *, organizzazione_id: int, email: str
    ) -> str | None:
        """Genera un magic link e lo invia via email.

        Non rivela se l'indirizzo esiste nel tenant (evita enumerazione
        utenti): la risposta è sempre generica lato router. Ritorna il link
        generato solo in debug (nessun invio email reale configurato), utile
        per sviluppo/test.
        """
        utenti = UtenteRepository(self.session, organizzazione_id)
        utente = await utenti.get_by_email(email)
        if utente is None or not utente.attivo:
            return None

        token = genera_token_opaco()
        await self.magic_link_repo.crea(
            utente=utente,
            token_hash=hash_token(token),
            scade_at=scadenza_da_minuti(settings.magic_link_expire_minutes),
        )
        link = f"{settings.frontend_base_url}/auth/verifica?token={token}"
        await self.email_sender.invia_magic_link(email=email, link=link)
        return link if settings.debug else None

    async def verifica_magic_link(self, token: str) -> tuple[str, str, Utente]:
        """Consuma il magic link e restituisce (access_token, refresh_token, utente)."""
        record = await self.magic_link_repo.get_valido(hash_token(token))
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Magic link non valido o scaduto.",
            )
        await self.magic_link_repo.segna_usato(record)

        utente = await self.session.get(Utente, record.utente_id)
        if utente is None or not utente.attivo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utente non valido.",
            )

        access_token = self._crea_access_token(utente)
        refresh_token = await self._crea_refresh_token(utente)
        return access_token, refresh_token, utente

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        """Ruota il refresh token e restituisce una nuova coppia (access, refresh)."""
        record = await self.refresh_repo.get_valido(hash_token(refresh_token))
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token non valido o scaduto.",
            )
        # Rotazione: il token presentato è consumato ad ogni uso, così un
        # refresh token rubato e già usato dal legittimo proprietario non è
        # più riutilizzabile.
        await self.refresh_repo.revoca(record)

        utente = await self.session.get(Utente, record.utente_id)
        if utente is None or not utente.attivo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utente non valido.",
            )

        access_token = self._crea_access_token(utente)
        nuovo_refresh_token = await self._crea_refresh_token(utente)
        return access_token, nuovo_refresh_token

    async def logout(self, refresh_token: str) -> None:
        record = await self.refresh_repo.get_valido(hash_token(refresh_token))
        if record is not None:
            await self.refresh_repo.revoca(record)

    def _crea_access_token(self, utente: Utente) -> str:
        return create_access_token(
            utente_id=utente.id,
            organizzazione_id=utente.organizzazione_id,
            ruolo=utente.ruolo,
        )

    async def _crea_refresh_token(self, utente: Utente) -> str:
        refresh_token = genera_token_opaco()
        await self.refresh_repo.crea(
            utente=utente,
            token_hash=hash_token(refresh_token),
            scade_at=scadenza_da_giorni(settings.refresh_token_expire_days),
        )
        return refresh_token
