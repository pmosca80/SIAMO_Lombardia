from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.documento_normativa import DocumentoNormativa


class CategoriaNormativa(Base, TimestampMixin):
    """Categoria dell'archivio Normative (siamoesercito.org), self-referencing:

    macro-categorie (es. "Amministrazione") hanno `parent_id` nullo;
    sotto-categorie (es. "Bilinguismo") hanno `parent_id` verso la macro.
    """

    __tablename__ = "categoria_normativa"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categoria_normativa.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )

    parent: Mapped["CategoriaNormativa | None"] = relationship(
        remote_side=[id], back_populates="figlie"
    )
    figlie: Mapped[list["CategoriaNormativa"]] = relationship(back_populates="parent")
    documenti: Mapped[list["DocumentoNormativa"]] = relationship(
        back_populates="categoria"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CategoriaNormativa id={self.id} slug={self.slug!r}>"
