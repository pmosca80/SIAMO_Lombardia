from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.email import EmailSender
from app.core.security import (
    create_access_token,
    genera_token_opaco,
    hash_password,
    hash_token,
    scadenza_da_giorni,
    scadenza_da_minuti,
    verifica_password,
)
from app.models.token_azione import TipoTokenAzione
from app.models.utente import RuoloUtente, Utente
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.token_azione import TokenAzioneRepository
from app.repositories.utente import UtenteRepository

_CREDENZIALI_ERRATE = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenziali non valide."
)


class AuthService:
    """Login con email+password, registrazione con verifica email, reset
    password, coppia di token JWT/refresh."""

    def __init__(
        self,
        session: AsyncSession,
        token_repo: TokenAzioneRepository,
        refresh_repo: RefreshTokenRepository,
        email_sender: EmailSender,
    ) -> None:
        self.session = session
        self.token_repo = token_repo
        self.refresh_repo = refresh_repo
        self.email_sender = email_sender

    async def registra(
        self,
        *,
        organizzazione_id: int,
        nome: str,
        cognome: str,
        email: str,
        numero_tessera: str,
        password: str,
    ) -> None:
        """Crea l'utente (inattivo, email non verificata) e invia il link di
        verifica. Non rivela se l'email è già in uso in questo tenant: la
        risposta è sempre generica lato router (anti-enumerazione)."""
        utenti = UtenteRepository(self.session, organizzazione_id)
        if await utenti.get_by_email(email) is not None:
            return

        utente = await utenti.add(
            Utente(
                nome=nome,
                cognome=cognome,
                email=email,
                numero_tessera=numero_tessera,
                ruolo=RuoloUtente.SOCIO,
                attivo=False,
                email_verificato=False,
                password_hash=hash_password(password),
            )
        )
        await self._invia_token_azione(
            utente=utente,
            tipo=TipoTokenAzione.VERIFICA_EMAIL,
            scadenza_minuti=60 * 48,
            path="/auth/verifica-email",
            invia=self.email_sender.invia_verifica_email,
        )

    async def verifica_email(self, token: str) -> tuple[str, str, Utente]:
        """Consuma il token di verifica, attiva l'utente e lo autentica
        direttamente (stessa UX del vecchio magic link)."""
        utente = await self._consuma_token(token, TipoTokenAzione.VERIFICA_EMAIL)
        utente.email_verificato = True
        utente.attivo = True
        self.session.add(utente)
        await self.session.flush()

        access_token = self._crea_access_token(utente)
        refresh_token = await self._crea_refresh_token(utente)
        return access_token, refresh_token, utente

    async def login(self, *, organizzazione_id: int, email: str, password: str) -> tuple[str, str]:
        utenti = UtenteRepository(self.session, organizzazione_id)
        utente = await utenti.get_by_email(email)
        if utente is None or utente.password_hash is None:
            raise _CREDENZIALI_ERRATE
        if not verifica_password(password, utente.password_hash):
            raise _CREDENZIALI_ERRATE
        if not utente.email_verificato:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Devi verificare la tua email prima di accedere. Controlla la posta in arrivo.",
            )
        if not utente.attivo:
            raise _CREDENZIALI_ERRATE

        access_token = self._crea_access_token(utente)
        refresh_token = await self._crea_refresh_token(utente)
        return access_token, refresh_token

    async def richiedi_reset_password(self, *, organizzazione_id: int, email: str) -> None:
        """Non rivela se l'indirizzo esiste nel tenant: la risposta è sempre
        generica lato router (anti-enumerazione)."""
        utenti = UtenteRepository(self.session, organizzazione_id)
        utente = await utenti.get_by_email(email)
        if utente is None or not utente.attivo:
            return
        await self._invia_token_azione(
            utente=utente,
            tipo=TipoTokenAzione.RESET_PASSWORD,
            scadenza_minuti=120,
            path="/reset-password",
            invia=self.email_sender.invia_reset_password,
        )

    async def reset_password(self, *, token: str, nuova_password: str) -> None:
        utente = await self._consuma_token(token, TipoTokenAzione.RESET_PASSWORD)
        utente.password_hash = hash_password(nuova_password)
        self.session.add(utente)
        await self.session.flush()

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

    async def _invia_token_azione(self, *, utente, tipo, scadenza_minuti, path, invia) -> None:
        token = genera_token_opaco()
        await self.token_repo.crea(
            tipo=tipo,
            utente=utente,
            token_hash=hash_token(token),
            scade_at=scadenza_da_minuti(scadenza_minuti),
        )
        link = f"{settings.frontend_base_url}{path}?token={token}"
        await invia(email=utente.email, link=link)

    async def _consuma_token(self, token: str, tipo: TipoTokenAzione) -> Utente:
        record = await self.token_repo.get_valido(tipo=tipo, token_hash=hash_token(token))
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Link non valido o scaduto.",
            )
        await self.token_repo.segna_usato(record)

        utente = await self.session.get(Utente, record.utente_id)
        if utente is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utente non valido.",
            )
        return utente

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
