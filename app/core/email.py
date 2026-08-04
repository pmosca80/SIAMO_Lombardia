"""Invio email, con backend astratto per poter collegare un provider reale.

Il backend di default logga il link invece di inviarlo davvero: comodo in
sviluppo/test e senza dipendenze SMTP. Se configurata una `resend_api_key`
si usa `ResendEmailSender` (nessun dominio proprio richiesto: il mittente di
default `onboarding@resend.dev` è già autenticato da Resend). In alternativa,
se è presente una password SMTP (Brevo), si usa `BrevoEmailSender` — richiede
però un dominio proprio autenticato per una consegna affidabile su Gmail
(vedi allineamento SPF/DKIM/DMARC).
"""
import asyncio
import logging
import smtplib
from email.message import EmailMessage
from typing import Protocol

import resend

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


class ResendEmailSender:
    """Invia il magic link via Resend (https://resend.com)."""

    def __init__(self, *, api_key: str, mittente: str) -> None:
        self.api_key = api_key
        self.mittente = mittente

    async def invia_magic_link(self, *, email: str, link: str) -> None:
        await asyncio.to_thread(self._invia_sync, email, link)

    def _invia_sync(self, email: str, link: str) -> None:
        resend.api_key = self.api_key
        resend.Emails.send(
            {
                "from": self.mittente,
                "to": [email],
                "subject": "Il tuo link di accesso a SIAMO Lombardia",
                "html": (
                    "<p>Clicca sul link per accedere (valido per un tempo limitato):</p>"
                    f'<p><a href="{link}">{link}</a></p>'
                    "<p>Se non hai richiesto tu l'accesso, ignora questa email.</p>"
                ),
            }
        )
        logger.info("Magic link inviato via Resend a %s", email)


def get_email_sender() -> EmailSender:
    if settings.resend_api_key:
        return ResendEmailSender(
            api_key=settings.resend_api_key,
            mittente=settings.resend_from,
        )
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
