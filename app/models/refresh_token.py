from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.utente import Utente


class RefreshToken(Base, TenantMixin, TimestampMixin):
    """Refresh token opaco, con rotazione: ogni uso ne genera uno nuovo e
    revoca quello precedente (`revocato_at`).

    Viene salvato solo l'hash SHA-256 del token, come per `MagicLinkToken`.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    utente_id: Mapped[int] = mapped_column(
        ForeignKey("utenti.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    scade_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revocato_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    utente: Mapped["Utente"] = relationship()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RefreshToken id={self.id} utente_id={self.utente_id}>"
