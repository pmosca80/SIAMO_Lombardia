from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base dichiarativa comune a tutti i modelli ORM."""


class TimestampMixin:
    """Colonne di audit temporale, gestite lato database."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TenantMixin:
    """Mixin multi-tenant.

    Ogni tabella "figlia" di un'organizzazione eredita da questo mixin per
    ottenere la colonna `organizzazione_id`. È il punto unico da propagare su
    tutte le tabelle future dell'applicazione:

        class Comunicazione(Base, TenantMixin, TimestampMixin):
            __tablename__ = "comunicazioni"
            id: Mapped[int] = mapped_column(primary_key=True)
            ...

    La colonna è indicizzata e non nullable per garantire isolamento e
    performance nelle query filtrate per tenant.
    """

    organizzazione_id: Mapped[int] = mapped_column(
        ForeignKey("organizzazioni.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
