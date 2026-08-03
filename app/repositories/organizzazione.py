from sqlalchemy import select

from app.models.organizzazione import Organizzazione
from app.repositories.base import BaseRepository


class OrganizzazioneRepository(BaseRepository[Organizzazione]):
    model = Organizzazione

    async def get_by_slug(self, slug: str) -> Organizzazione | None:
        result = await self.session.execute(
            select(Organizzazione).where(Organizzazione.slug == slug)
        )
        return result.scalar_one_or_none()
