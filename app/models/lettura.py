from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.comunicazione import Comunicazione
    from app.models.organizzazione import Organizzazione
    from app.models.utente import Utente


class Lettura(Base, TenantMixin, TimestampMixin):
    """Ricevuta di lettura: registra che un utente ha letto una comunicazione.

    La coppia (comunicazione, utente) è unica: una sola ricevuta per lettore.
    Se la comunicazione o l'utente vengono eliminati, la ricevuta decade
    (ON DELETE CASCADE).
    """

    __tablename__ = "letture"
    __table_args__ = (
        UniqueConstraint(
            "comunicazione_id", "utente_id", name="uq_lettura_comunicazione_utente"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    comunicazione_id: Mapped[int] = mapped_column(
        ForeignKey("comunicazioni.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    utente_id: Mapped[int] = mapped_column(
        ForeignKey("utenti.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    letto_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    organizzazione: Mapped["Organizzazione"] = relationship(back_populates="letture")
    comunicazione: Mapped["Comunicazione"] = relationship(back_populates="letture")
    utente: Mapped["Utente"] = relationship(back_populates="letture")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Lettura id={self.id} comunicazione={self.comunicazione_id} "
            f"utente={self.utente_id}>"
        )
