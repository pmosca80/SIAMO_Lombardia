from app.models.campagna import Campagna
from app.repositories.base import TenantRepository


class CampagnaRepository(TenantRepository[Campagna]):
    model = Campagna
