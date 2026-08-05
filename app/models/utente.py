import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.comunicazione import Comunicazione
    from app.models.documento import Documento
    from app.models.lettura import Lettura
    from app.models.organizzazione import Organizzazione


class RuoloUtente(str, enum.Enum):
    AMMINISTRATORE = "amministratore"
    OPERATORE = "operatore"
    SOCIO = "socio"


class Utente(Base, TenantMixin, TimestampMixin):
    """Persona associata a un'organizzazione (socio, operatore, amministratore).

    L'email è unica *all'interno* della stessa organizzazione: due tenant
    diversi possono avere lo stesso indirizzo.
    """

    __tablename__ = "utenti"
    __table_args__ = (
        UniqueConstraint("organizzazione_id", "email", name="uq_utente_org_email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    cognome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    # Obbligatorio nel form di autoregistrazione (vedi RegistrazioneRequest),
    # ma nullo a livello di colonna: gli utenti creati da un amministratore
    # (UtenteCreate) possono non averlo ancora assegnato.
    numero_tessera: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ruolo: Mapped[RuoloUtente] = mapped_column(
        Enum(RuoloUtente, name="ruolo_utente"),
        default=RuoloUtente.SOCIO,
        nullable=False,
    )
    attivo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Nullo finché l'utente non imposta una password (registrazione o "password
    # dimenticata"): un amministratore può creare un utente senza password,
    # che dovrà poi impostarne una tramite il flusso di reset.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # True per gli utenti creati da un amministratore (già vetted). False solo
    # per la registrazione libera, finché non si verifica l'indirizzo email.
    email_verificato: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    organizzazione: Mapped["Organizzazione"] = relationship(back_populates="utenti")
    comunicazioni_create: Mapped[list["Comunicazione"]] = relationship(
        back_populates="autore",
        foreign_keys="Comunicazione.autore_id",
    )
    documenti_caricati: Mapped[list["Documento"]] = relationship(
        back_populates="caricato_da",
        foreign_keys="Documento.caricato_da_id",
    )
    letture: Mapped[list["Lettura"]] = relationship(
        back_populates="utente",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Utente id={self.id} email={self.email!r} org={self.organizzazione_id}>"
