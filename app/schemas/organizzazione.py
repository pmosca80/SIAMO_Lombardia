from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class OrganizzazioneBase(BaseModel):
    nome: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    attiva: bool = True


class OrganizzazioneCreate(OrganizzazioneBase):
    # Se forniti, creano contestualmente il primo utente amministratore del
    # tenant: senza un utente non esiste modo di autenticarsi (login via
    # magic link) per gestire l'organizzazione appena creata.
    admin_nome: str | None = Field(default=None, max_length=120)
    admin_cognome: str | None = Field(default=None, max_length=120)
    admin_email: EmailStr | None = None

    @model_validator(mode="after")
    def _admin_completo_o_assente(self) -> "OrganizzazioneCreate":
        campi = (self.admin_nome, self.admin_cognome, self.admin_email)
        if any(campi) and not all(campi):
            raise ValueError(
                "admin_nome, admin_cognome e admin_email vanno forniti insieme."
            )
        return self


class OrganizzazioneUpdate(BaseModel):
    nome: str | None = Field(default=None, max_length=255)
    attiva: bool | None = None


class OrganizzazioneRead(OrganizzazioneBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
