from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.utente import RuoloUtente


class UtenteBase(BaseModel):
    nome: str = Field(..., max_length=120)
    cognome: str = Field(..., max_length=120)
    email: EmailStr
    ruolo: RuoloUtente = RuoloUtente.SOCIO
    attivo: bool = True


class UtenteCreate(UtenteBase):
    # Opzionale: senza password l'utente dovrà impostarne una tramite il
    # flusso "password dimenticata" prima di poter accedere.
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UtenteUpdate(BaseModel):
    nome: str | None = Field(default=None, max_length=120)
    cognome: str | None = Field(default=None, max_length=120)
    ruolo: RuoloUtente | None = None
    attivo: bool | None = None


class UtenteRead(UtenteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organizzazione_id: int
    created_at: datetime
    updated_at: datetime
