from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.campagna import Campagna
    from app.models.comunicazione import Comunicazione
    from app.models.documento import Documento
    from app.models.lettura import Lettura
    from app.models.utente import Utente


class Organizzazione(Base, TimestampMixin):
    """Tenant radice dell'applicazione.

    Ogni associazione è un'organizzazione; tutte le altre entità sono
    isolate per `organizzazione_id` (vedi `TenantMixin`). L'eliminazione di
    un'organizzazione propaga a cascata su tutte le entità figlie (ON DELETE
    CASCADE lato DB; `passive_deletes` demanda la cascata al database).
    """

    __tablename__ = "organizzazioni"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    attiva: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    utenti: Mapped[list["Utente"]] = relationship(
        back_populates="organizzazione",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    campagne: Mapped[list["Campagna"]] = relationship(
        back_populates="organizzazione",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comunicazioni: Mapped[list["Comunicazione"]] = relationship(
        back_populates="organizzazione",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    documenti: Mapped[list["Documento"]] = relationship(
        back_populates="organizzazione",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    letture: Mapped[list["Lettura"]] = relationship(
        back_populates="organizzazione",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Organizzazione id={self.id} slug={self.slug!r}>"
