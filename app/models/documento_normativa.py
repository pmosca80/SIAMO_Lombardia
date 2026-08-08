from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.categoria_normativa import CategoriaNormativa


class DocumentoNormativa(Base, TimestampMixin):
    """Documento normativo importato dall'archivio pubblico siamoesercito.org.

    Contenuto nazionale, non legato a un'organizzazione (niente
    TenantMixin): a differenza di `Documento`, che rappresenta un allegato
    caricato da un'organizzazione, qui il tenant non esiste.
    """

    __tablename__ = "documento_normativa"

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categoria_normativa.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    titolo: Mapped[str] = mapped_column(String(500), nullable=False)
    data_pubblicazione: Mapped[date | None] = mapped_column(Date, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    file_size_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Solo per audit/idempotenza import: chiave naturale usata dallo script
    # per capire se un documento è già stato importato. Mai esposto al
    # frontend (i documenti sono di proprietà della piattaforma terza).
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    categoria: Mapped["CategoriaNormativa"] = relationship(back_populates="documenti")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DocumentoNormativa id={self.id} titolo={self.titolo!r}>"
