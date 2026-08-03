from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Organizzazione(Base, TimestampMixin):
    """Tenant radice dell'applicazione.

    Ogni associazione è un'organizzazione; tutte le altre entità sono
    isolate per `organizzazione_id` (vedi `TenantMixin`).
    """

    __tablename__ = "organizzazioni"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    attiva: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Organizzazione id={self.id} slug={self.slug!r}>"
