"""Registro dei modelli ORM.

Importare qui ogni nuovo modello così che Alembic (autogenerate) lo veda
tramite `Base.metadata`.
"""

from app.models.base import Base, TenantMixin, TimestampMixin
from app.models.comunicazione import (
    CanaleComunicazione,
    Comunicazione,
    StatoComunicazione,
)
from app.models.membro import Membro, RuoloMembro
from app.models.organizzazione import Organizzazione

__all__ = [
    "Base",
    "TenantMixin",
    "TimestampMixin",
    "Organizzazione",
    "Membro",
    "RuoloMembro",
    "Comunicazione",
    "CanaleComunicazione",
    "StatoComunicazione",
]
