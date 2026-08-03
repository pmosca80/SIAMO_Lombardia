from app.models.comunicazione import Comunicazione
from app.repositories.base import TenantRepository


class ComunicazioneRepository(TenantRepository[Comunicazione]):
    model = Comunicazione
