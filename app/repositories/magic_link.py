from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import aware_utc
from app.models.magic_link_token import MagicLinkToken
from app.models.utente import Utente


class MagicLinkRepository:
    """Repository per i token di magic link.

    A differenza dei repository tenant-scoped, la ricerca avviene per hash
    del token: al momento della verifica l'organizzazione non è ancora
    nota (il client conosce solo il token ricevuto via email).
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def crea(self, *, utente: Utente, token_hash: str, scade_at: datetime) -> MagicLinkToken:
        token = MagicLinkToken(
            utente_id=utente.id,
            organizzazione_id=utente.organizzazione_id,
            token_hash=token_hash,
            scade_at=scade_at,
        )
        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return token

    async def get_valido(self, token_hash: str) -> MagicLinkToken | None:
        result = await self.session.execute(
            select(MagicLinkToken).where(MagicLinkToken.token_hash == token_hash)
        )
        token = result.scalar_one_or_none()
        if token is None or token.usato_at is not None:
            return None
        if aware_utc(token.scade_at) < datetime.now(timezone.utc):
            return None
        return token

    async def segna_usato(self, token: MagicLinkToken) -> None:
        token.usato_at = datetime.now(timezone.utc)
        self.session.add(token)
        await self.session.flush()
