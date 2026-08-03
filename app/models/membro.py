import enum

from sqlalchemy import Boolean, Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin


class RuoloMembro(str, enum.Enum):
    AMMINISTRATORE = "amministratore"
    OPERATORE = "operatore"
    SOCIO = "socio"


class Membro(Base, TenantMixin, TimestampMixin):
    """Persona iscritta a un'organizzazione.

    L'email è unica *all'interno* della stessa organizzazione: due tenant
    diversi possono avere lo stesso indirizzo.
    """

    __tablename__ = "membri"
    __table_args__ = (
        UniqueConstraint("organizzazione_id", "email", name="uq_membro_org_email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    cognome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    ruolo: Mapped[RuoloMembro] = mapped_column(
        Enum(RuoloMembro, name="ruolo_membro"),
        default=RuoloMembro.SOCIO,
        nullable=False,
    )
    attivo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Membro id={self.id} email={self.email!r} org={self.organizzazione_id}>"
