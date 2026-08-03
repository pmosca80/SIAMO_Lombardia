import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin


class CanaleComunicazione(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    AVVISO = "avviso"


class StatoComunicazione(str, enum.Enum):
    BOZZA = "bozza"
    INVIATA = "inviata"


class Comunicazione(Base, TenantMixin, TimestampMixin):
    """Messaggio che un'organizzazione invia ai propri membri."""

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
    # Autore della comunicazione: membro della stessa organizzazione.
    autore_id: Mapped[int | None] = mapped_column(
        ForeignKey("membri.id", ondelete="SET NULL"),
        nullable=True,
    )
    inviata_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Comunicazione id={self.id} titolo={self.titolo!r} stato={self.stato}>"
