from sqlalchemy import select

from app.models.membro import Membro
from app.repositories.base import TenantRepository


class MembroRepository(TenantRepository[Membro]):
    model = Membro

    async def get_by_email(self, email: str) -> Membro | None:
        result = await self.session.execute(
            select(Membro).where(
                Membro.organizzazione_id == self.organizzazione_id,
                Membro.email == email,
            )
        )
        return result.scalar_one_or_none()
