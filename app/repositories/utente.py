from sqlalchemy import select

from app.models.utente import Utente
from app.repositories.base import TenantRepository


class UtenteRepository(TenantRepository[Utente]):
    model = Utente

    async def get_by_email(self, email: str) -> Utente | None:
        result = await self.session.execute(
            select(Utente).where(
                Utente.organizzazione_id == self.organizzazione_id,
                Utente.email == email,
            )
        )
        return result.scalar_one_or_none()
