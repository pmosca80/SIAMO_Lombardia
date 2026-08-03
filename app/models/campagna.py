import enum
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.comunicazione import Comunicazione
    from app.models.organizzazione import Organizzazione


class StatoCampagna(str, enum.Enum):
    PIANIFICATA = "pianificata"
    ATTIVA = "attiva"
    CONCLUSA = "conclusa"


class Campagna(Base, TenantMixin, TimestampMixin):
    """Raggruppa più comunicazioni con un obiettivo e un arco temporale comuni."""

    __tablename__ = "campagne"
    __table_args__ = (
        UniqueConstraint("organizzazione_id", "nome", name="uq_campagna_org_nome"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descrizione: Mapped[str | None] = mapped_column(Text, nullable=True)
    stato: Mapped[StatoCampagna] = mapped_column(
        Enum(StatoCampagna, name="stato_campagna"),
        default=StatoCampagna.PIANIFICATA,
        nullable=False,
    )
    data_inizio: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_fine: Mapped[date | None] = mapped_column(Date, nullable=True)

    organizzazione: Mapped["Organizzazione"] = relationship(back_populates="campagne")
    comunicazioni: Mapped[list["Comunicazione"]] = relationship(
        back_populates="campagna",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Campagna id={self.id} nome={self.nome!r} stato={self.stato}>"
