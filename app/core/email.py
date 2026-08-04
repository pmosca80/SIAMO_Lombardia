"""Invio email, con backend astratto per poter collegare un provider reale.

Il backend di default logga il link invece di inviarlo davvero: comodo in
sviluppo/test e senza dipendenze SMTP. Se in configurazione è presente una
password SMTP (Brevo), si usa invece `BrevoEmailSender`.
"""
import asyncio
import logging
import smtplib
from email.message import EmailMessage
from typing import Protocol

from app.core.config import settings

logger = logging.getLogger("app.email")


class EmailSender(Protocol):
    async def invia_magic_link(self, *, email: str, link: str) -> None: ...


class LogEmailSender:
    """Backend di sviluppo: logga il magic link invece di inviarlo via email."""

    async def invia_magic_link(self, *, email: str, link: str) -> None:
        logger.info("Magic link per %s: %s", email, link)


class BrevoEmailSender:
    """Invia il magic link via SMTP relay di Brevo (ex Sendinblue)."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        login: str,
        password: str,
        mittente: str,
        mittente_nome: str,
    ) -> None:
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.mittente = mittente
        self.mittente_nome = mittente_nome

    async def invia_magic_link(self, *, email: str, link: str) -> None:
        await asyncio.to_thread(self._invia_sync, email, link)

    def _invia_sync(self, email: str, link: str) -> None:
        messaggio = EmailMessage()
        messaggio["Subject"] = "Il tuo link di accesso a SIAMO Lombardia"
        messaggio["From"] = f"{self.mittente_nome} <{self.mittente}>"
        messaggio["To"] = email
        messaggio.set_content(
            "Clicca sul link per accedere (valido per un tempo limitato):\n\n"
            f"{link}\n\n"
            "Se non hai richiesto tu l'accesso, ignora questa email."
        )

        with smtplib.SMTP(self.host, self.port) as smtp:
            smtp.starttls()
            smtp.login(self.login, self.password)
            smtp.send_message(messaggio)
        logger.info("Magic link inviato via Brevo a %s", email)


def get_email_sender() -> EmailSender:
    if settings.smtp_password and settings.email_from:
        return BrevoEmailSender(
            host=settings.smtp_host,
            port=settings.smtp_port,
            login=settings.smtp_login or settings.email_from,
            password=settings.smtp_password,
            mittente=settings.email_from,
            mittente_nome=settings.email_from_name,
        )
    return LogEmailSender()
