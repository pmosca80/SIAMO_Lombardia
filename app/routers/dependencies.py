from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.email import get_email_sender
from app.core.security import CurrentUser
from app.models.utente import RuoloUtente
from app.repositories.campagna import CampagnaRepository
from app.repositories.comunicazione import ComunicazioneRepository
from app.repositories.organizzazione import OrganizzazioneRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.token_azione import TokenAzioneRepository
from app.repositories.utente import UtenteRepository
from app.services.auth import AuthService
from app.services.comunicazione import ComunicazioneService
from app.services.organizzazione import OrganizzazioneService
from app.services.utente import UtenteService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# --- Autenticazione ---------------------------------------------------------

def get_current_user(request: Request) -> CurrentUser:
    """Legge l'utente autenticato dal context di request (vedi
    `AuthContextMiddleware`). Solleva 401 se non è stato presentato un JWT
    valido: è il punto di ingresso di ogni route protetta.
    """
    current_user = getattr(request.state, "current_user", None)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticazione richiesta.",
        )
    return current_user


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


def require_ruoli(*ruoli: RuoloUtente):
    """Dependency factory: consente l'accesso solo ai ruoli indicati.

        @router.post("", dependencies=[Depends(require_ruoli(RuoloUtente.AMMINISTRATORE))])
    """

    def _verifica(current_user: CurrentUserDep) -> CurrentUser:
        if current_user.ruolo not in ruoli:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permessi insufficienti per questa operazione.",
            )
        return current_user

    return _verifica


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(
        session,
        TokenAzioneRepository(session),
        RefreshTokenRepository(session),
        get_email_sender(),
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


# --- Organizzazione (tenant radice) ---------------------------------------

def get_organizzazione_service(session: SessionDep) -> OrganizzazioneService:
    return OrganizzazioneService(OrganizzazioneRepository(session))


OrganizzazioneServiceDep = Annotated[
    OrganizzazioneService, Depends(get_organizzazione_service)
]


async def get_tenant_id(
    organizzazione_id: int,
    current_user: CurrentUserDep,
    service: OrganizzazioneServiceDep,
) -> int:
    """Estrae l'`organizzazione_id` dal path, lo confronta con quello del JWT
    e ne verifica l'esistenza (404).

    L'`organizzazione_id` del token (iniettato nel context dal middleware)
    è la fonte di verità del tenant: il path serve solo a rendere l'URL
    leggibile/RESTful. Se non coincidono l'utente sta tentando di accedere
    ai dati di un altro tenant -> 403, indipendentemente dal fatto che
    l'organizzazione nel path esista davvero.
    """
    if organizzazione_id != current_user.organizzazione_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato: organizzazione non corrispondente al token.",
        )
    await service.get(organizzazione_id)
    return organizzazione_id


TenantId = Annotated[int, Depends(get_tenant_id)]


# --- Entità tenant-scoped -------------------------------------------------

def get_utente_service(session: SessionDep, tenant_id: TenantId) -> UtenteService:
    return UtenteService(UtenteRepository(session, tenant_id))


UtenteServiceDep = Annotated[UtenteService, Depends(get_utente_service)]


def get_comunicazione_service(
    session: SessionDep,
    tenant_id: TenantId,
) -> ComunicazioneService:
    return ComunicazioneService(
        ComunicazioneRepository(session, tenant_id),
        UtenteRepository(session, tenant_id),
        CampagnaRepository(session, tenant_id),
    )


ComunicazioneServiceDep = Annotated[
    ComunicazioneService, Depends(get_comunicazione_service)
]
