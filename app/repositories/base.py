from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repository generico con le operazioni CRUD comuni.

    I repository concreti ereditano da questa classe e aggiungono le query
    specifiche del dominio. Per le entità multi-tenant, filtrare sempre per
    `organizzazione_id` nelle query dedicate.
    """

    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id_: int) -> ModelType | None:
        return await self.session.get(self.model, id_)

    async def list(self, *, limit: int = 100, offset: int = 0) -> list[ModelType]:
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def add(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.flush()


class TenantRepository(BaseRepository[ModelType]):
    """Repository per entità multi-tenant.

    Ogni operazione è vincolata a `organizzazione_id`: le letture filtrano per
    tenant e le scritture impostano il tenant sull'istanza. In questo modo
    l'isolamento è garantito a livello di data-access, non demandato ai layer
    superiori.
    """

    def __init__(self, session: AsyncSession, organizzazione_id: int) -> None:
        super().__init__(session)
        self.organizzazione_id = organizzazione_id

    async def get(self, id_: int) -> ModelType | None:
        result = await self.session.execute(
            select(self.model).where(
                self.model.id == id_,
                self.model.organizzazione_id == self.organizzazione_id,
            )
        )
        return result.scalar_one_or_none()

    async def list(self, *, limit: int = 100, offset: int = 0) -> list[ModelType]:
        result = await self.session.execute(
            select(self.model)
            .where(self.model.organizzazione_id == self.organizzazione_id)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def add(self, instance: ModelType) -> ModelType:
        instance.organizzazione_id = self.organizzazione_id
        return await super().add(instance)
