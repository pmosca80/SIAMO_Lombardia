from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrganizzazioneBase(BaseModel):
    nome: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    attiva: bool = True


class OrganizzazioneCreate(OrganizzazioneBase):
    pass


class OrganizzazioneUpdate(BaseModel):
    nome: str | None = Field(default=None, max_length=255)
    attiva: bool | None = None


class OrganizzazioneRead(OrganizzazioneBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
