from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import aware_utc
from app.models.token_azione import TipoTokenAzione, TokenAzione
from app.models.utente import Utente


class TokenAzioneRepository:
    """Repository per i token di verifica email e reset password.

    Come `RefreshTokenRepository`, la ricerca avviene per hash del token: al
    momento della verifica il tenant non è ancora noto lato server (il
    client conosce solo il token ricevuto via email).
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def crea(
        self, *, tipo: TipoTokenAzione, utente: Utente, token_hash: str, scade_at: datetime
    ) -> TokenAzione:
        token = TokenAzione(
            utente_id=utente.id,
            organizzazione_id=utente.organizzazione_id,
            tipo=tipo,
            token_hash=token_hash,
            scade_at=scade_at,
        )
        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return token

    async def get_valido(self, *, tipo: TipoTokenAzione, token_hash: str) -> TokenAzione | None:
        result = await self.session.execute(
            select(TokenAzione).where(
                TokenAzione.tipo == tipo, TokenAzione.token_hash == token_hash
            )
        )
        token = result.scalar_one_or_none()
        if token is None or token.usato_at is not None:
            return None
        if aware_utc(token.scade_at) < datetime.now(timezone.utc):
            return None
        return token

    async def segna_usato(self, token: TokenAzione) -> None:
        token.usato_at = datetime.now(timezone.utc)
        self.session.add(token)
        await self.session.flush()
