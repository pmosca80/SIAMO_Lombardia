from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.comunicazione import CanaleComunicazione, StatoComunicazione


class ComunicazioneBase(BaseModel):
    titolo: str = Field(..., max_length=255)
    corpo: str = Field(..., min_length=1)
    canale: CanaleComunicazione = CanaleComunicazione.EMAIL
    autore_id: int | None = None


class ComunicazioneCreate(ComunicazioneBase):
    pass


class ComunicazioneUpdate(BaseModel):
    titolo: str | None = Field(default=None, max_length=255)
    corpo: str | None = Field(default=None, min_length=1)
    canale: CanaleComunicazione | None = None
    autore_id: int | None = None


class ComunicazioneRead(ComunicazioneBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organizzazione_id: int
    stato: StatoComunicazione
    inviata_at: datetime | None
    created_at: datetime
    updated_at: datetime
