"""Invio email, con backend astratto per poter collegare un provider reale.

Il backend di default logga il link invece di inviarlo davvero: comodo in
sviluppo/test e senza dipendenze SMTP. Per un provider reale (es. Resend,
SES, SMTP), implementare `EmailSender` e sostituire `get_email_sender`.
"""
import logging
from typing import Protocol

logger = logging.getLogger("app.email")


class EmailSender(Protocol):
    async def invia_magic_link(self, *, email: str, link: str) -> None: ...


class LogEmailSender:
    """Backend di sviluppo: logga il magic link invece di inviarlo via email."""

    async def invia_magic_link(self, *, email: str, link: str) -> None:
        logger.info("Magic link per %s: %s", email, link)


def get_email_sender() -> EmailSender:
    return LogEmailSender()
