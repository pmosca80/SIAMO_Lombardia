import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.campagna import Campagna
    from app.models.documento import Documento
    from app.models.lettura import Lettura
    from app.models.organizzazione import Organizzazione
    from app.models.utente import Utente


class CanaleComunicazione(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    AVVISO = "avviso"


class StatoComunicazione(str, enum.Enum):
    BOZZA = "bozza"
    INVIATA = "inviata"


class Comunicazione(Base, TenantMixin, TimestampMixin):
    """Messaggio che un'organizzazione invia ai propri utenti.

    Può appartenere a una campagna ed essere firmato da un utente autore;
    entrambi i legami sono opzionali (ON DELETE SET NULL).
    """

    __tablename__ = "comunicazioni"

    id: Mapped[int] = mapped_column(primary_key=True)
    titolo: Mapped[str] = mapped_column(String(255), nullable=False)
    corpo: Mapped[str] = mapped_column(Text, nullable=False)
    canale: Mapped[CanaleComunicazione] = mapped_column(
        Enum(CanaleComunicazione, name="canale_comunicazione"),
        default=CanaleComunicazione.EMAIL,
        nullable=False,
    )
    stato: Mapped[StatoComunicazione] = mapped_column(
        Enum(StatoComunicazione, name="stato_comunicazione"),
        default=StatoComunicazione.BOZZA,
        nullable=False,
    )
    campagna_id: Mapped[int | None] = mapped_column(
        ForeignKey("campagne.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    autore_id: Mapped[int | None] = mapped_column(
        ForeignKey("utenti.id", ondelete="SET NULL"),
        nullable=True,
    )
    inviata_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    organizzazione: Mapped["Organizzazione"] = relationship(
        back_populates="comunicazioni"
    )
    campagna: Mapped["Campagna | None"] = relationship(back_populates="comunicazioni")
    autore: Mapped["Utente | None"] = relationship(
        back_populates="comunicazioni_create",
        foreign_keys=[autore_id],
    )
    documenti: Mapped[list["Documento"]] = relationship(
        back_populates="comunicazione",
        passive_deletes=True,
    )
    letture: Mapped[list["Lettura"]] = relationship(
        back_populates="comunicazione",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Comunicazione id={self.id} titolo={self.titolo!r} stato={self.stato}>"
