"""Middleware che decodifica il JWT (se presente) e lo mette nel context
della request, cosi' l'`organizzazione_id` del tenant autenticato e' sempre
disponibile senza doverlo ricavare dal path o ridecodificare l'header in
ogni dependency.

Nessun token -> richiesta anonima (`request.state.current_user = None`): le
route pubbliche (es. `/auth/*`, `/health`) restano accessibili, quelle
protette rifiutano l'accesso a livello di dependency (`get_current_user`).
Token presente ma invalido/scaduto -> 401 immediato, prima di raggiungere
la route.
"""
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.core.security import CurrentUser, decode_access_token


class AuthContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request.state.current_user = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[len("Bearer "):].strip()
            try:
                payload = decode_access_token(token)
            except HTTPException as exc:
                return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
            request.state.current_user = CurrentUser(
                utente_id=payload.sub,
                organizzazione_id=payload.org,
                ruolo=payload.ruolo,
            )
        return await call_next(request)
