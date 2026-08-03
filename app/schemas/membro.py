from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.membro import RuoloMembro


class MembroBase(BaseModel):
    nome: str = Field(..., max_length=120)
    cognome: str = Field(..., max_length=120)
    email: EmailStr
    ruolo: RuoloMembro = RuoloMembro.SOCIO
    attivo: bool = True


class MembroCreate(MembroBase):
    pass


class MembroUpdate(BaseModel):
    nome: str | None = Field(default=None, max_length=120)
    cognome: str | None = Field(default=None, max_length=120)
    ruolo: RuoloMembro | None = None
    attivo: bool | None = None


class MembroRead(MembroBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organizzazione_id: int
    created_at: datetime
    updated_at: datetime
