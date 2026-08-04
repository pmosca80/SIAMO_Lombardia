import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.utente import Utente


class TipoTokenAzione(str, enum.Enum):
    VERIFICA_EMAIL = "verifica_email"
    RESET_PASSWORD = "reset_password"


class TokenAzione(Base, TenantMixin, TimestampMixin):
    """Token monouso per verifica email e reset password.

    Stesso schema per entrambi gli usi (distinti da `tipo`): viene salvato
    solo l'hash SHA-256 del token, mai il valore in chiaro, che esiste
    soltanto nel link inviato via email. Un token e' valido se non e'
    scaduto e non e' gia' stato usato.
    """

    __tablename__ = "token_azione"

    id: Mapped[int] = mapped_column(primary_key=True)
    utente_id: Mapped[int] = mapped_column(
        ForeignKey("utenti.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    tipo: Mapped[TipoTokenAzione] = mapped_column(
        Enum(TipoTokenAzione, name="tipo_token_azione"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    scade_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usato_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    utente: Mapped["Utente"] = relationship()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TokenAzione id={self.id} tipo={self.tipo} utente_id={self.utente_id}>"
