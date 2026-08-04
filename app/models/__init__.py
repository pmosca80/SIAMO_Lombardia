"""Registro dei modelli ORM.

Importare qui ogni nuovo modello così che Alembic (autogenerate) e la
configurazione dei mapper lo vedano tramite `Base.metadata`.
"""

from app.models.base import Base, TenantMixin, TimestampMixin
from app.models.campagna import Campagna, StatoCampagna
from app.models.comunicazione import (
    CanaleComunicazione,
    Comunicazione,
    StatoComunicazione,
)
from app.models.documento import Documento
from app.models.lettura import Lettura
from app.models.organizzazione import Organizzazione
from app.models.refresh_token import RefreshToken
from app.models.token_azione import TipoTokenAzione, TokenAzione
from app.models.utente import RuoloUtente, Utente

__all__ = [
    "Base",
    "TenantMixin",
    "TimestampMixin",
    "Organizzazione",
    "Utente",
    "RuoloUtente",
    "Campagna",
    "StatoCampagna",
    "Comunicazione",
    "CanaleComunicazione",
    "StatoComunicazione",
    "Documento",
    "Lettura",
    "TokenAzione",
    "TipoTokenAzione",
    "RefreshToken",
]
