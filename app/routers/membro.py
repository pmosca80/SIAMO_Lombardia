from fastapi import APIRouter, status

from app.routers.dependencies import MembroServiceDep
from app.schemas.membro import MembroCreate, MembroRead, MembroUpdate

router = APIRouter(
    prefix="/organizzazioni/{organizzazione_id}/membri",
    tags=["membri"],
)


@router.post("", response_model=MembroRead, status_code=status.HTTP_201_CREATED)
async def crea_membro(dati: MembroCreate, service: MembroServiceDep) -> MembroRead:
    return await service.crea(dati)


@router.get("", response_model=list[MembroRead])
async def lista_membri(
    service: MembroServiceDep,
    limit: int = 100,
    offset: int = 0,
) -> list[MembroRead]:
    return await service.lista(limit=limit, offset=offset)


@router.get("/{membro_id}", response_model=MembroRead)
async def get_membro(membro_id: int, service: MembroServiceDep) -> MembroRead:
    return await service.get(membro_id)


@router.patch("/{membro_id}", response_model=MembroRead)
async def aggiorna_membro(
    membro_id: int,
    dati: MembroUpdate,
    service: MembroServiceDep,
) -> MembroRead:
    return await service.aggiorna(membro_id, dati)


@router.delete("/{membro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def elimina_membro(membro_id: int, service: MembroServiceDep) -> None:
    await service.elimina(membro_id)
