from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class NormativaDocumento(Base, TimestampMixin):
    """Documento normativo importato dall'archivio pubblico siamoesercito.org.

    Contenuto nazionale, non legato a un'organizzazione (niente
    TenantMixin): a differenza di `Documento`, che rappresenta un allegato
    caricato da un'organizzazione, qui il tenant non esiste.
    """

    __tablename__ = "normative_documenti"

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria_macro_slug: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria_macro_nome: Mapped[str] = mapped_column(String(150), nullable=False)
    categoria_sub_slug: Mapped[str] = mapped_column(String(150), nullable=False)
    categoria_sub_nome: Mapped[str] = mapped_column(String(150), nullable=False)
    titolo: Mapped[str] = mapped_column(String(500), nullable=False)
    data_pubblicazione: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    file_size_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<NormativaDocumento id={self.id} titolo={self.titolo!r}>"
