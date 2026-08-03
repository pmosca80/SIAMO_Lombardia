from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import aware_utc
from app.models.refresh_token import RefreshToken
from app.models.utente import Utente


class RefreshTokenRepository:
    """Repository per i refresh token.

    Come `MagicLinkRepository`, la ricerca avviene per hash del token: al
    momento del refresh il tenant non è ancora noto lato server.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def crea(self, *, utente: Utente, token_hash: str, scade_at: datetime) -> RefreshToken:
        token = RefreshToken(
            utente_id=utente.id,
            organizzazione_id=utente.organizzazione_id,
            token_hash=token_hash,
            scade_at=scade_at,
        )
        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return token

    async def get_valido(self, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        token = result.scalar_one_or_none()
        if token is None or token.revocato_at is not None:
            return None
        if aware_utc(token.scade_at) < datetime.now(timezone.utc):
            return None
        return token

    async def revoca(self, token: RefreshToken) -> None:
        token.revocato_at = datetime.now(timezone.utc)
        self.session.add(token)
        await self.session.flush()
