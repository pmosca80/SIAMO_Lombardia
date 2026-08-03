from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.utente import Utente


class MagicLinkToken(Base, TenantMixin, TimestampMixin):
    """Token monouso per il login via magic link.

    Viene salvato solo l'hash SHA-256 del token (mai il valore in chiaro,
    che esiste soltanto nel link inviato via email). Un token e' valido se
    non e' scaduto e non e' gia' stato usato.
    """

    __tablename__ = "magic_link_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    utente_id: Mapped[int] = mapped_column(
        ForeignKey("utenti.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    scade_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usato_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    utente: Mapped["Utente"] = relationship()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MagicLinkToken id={self.id} utente_id={self.utente_id}>"
