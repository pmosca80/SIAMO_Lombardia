from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.comunicazione import Comunicazione
    from app.models.organizzazione import Organizzazione
    from app.models.utente import Utente


class Documento(Base, TenantMixin, TimestampMixin):
    """File caricato da un'organizzazione.

    Può essere autonomo (libreria documentale) oppure allegato a una
    comunicazione. Se la comunicazione viene eliminata il documento
    sopravvive come standalone (ON DELETE SET NULL).
    """

    __tablename__ = "documenti"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_file: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dimensione_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    comunicazione_id: Mapped[int | None] = mapped_column(
        ForeignKey("comunicazioni.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    caricato_da_id: Mapped[int | None] = mapped_column(
        ForeignKey("utenti.id", ondelete="SET NULL"),
        nullable=True,
    )

    organizzazione: Mapped["Organizzazione"] = relationship(back_populates="documenti")
    comunicazione: Mapped["Comunicazione | None"] = relationship(
        back_populates="documenti"
    )
    caricato_da: Mapped["Utente | None"] = relationship(
        back_populates="documenti_caricati",
        foreign_keys=[caricato_da_id],
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Documento id={self.id} nome_file={self.nome_file!r}>"
