"""Importer standalone: archivio Normative di siamoesercito.org -> R2 + Postgres.

Uso:
    python scripts/import_normative.py [--categoria SLUG] [--limit N]
        [--delay SECONDI] [--dry-run] [--recheck-pdf]
    python scripts/import_normative.py --verify

Le pagine HTML del sito sono pubbliche; i PDF allegati richiedono invece un
account autenticato (Drupal serve /system/files/... solo agli utenti
loggati). Se SIAMOESERCITO_USERNAME/PASSWORD non sono configurati in .env,
lo script importa comunque tutti i metadati ma salta il download dei PDF.

Non è collegato all'app FastAPI: usa AsyncSessionLocal direttamente, fuori
dal ciclo di vita delle request.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import logging
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.storage_r2 import (
    R2NonConfigurato,
    get_bucket_normative,
    get_r2_client,
    list_keys,
    upload_file,
)
from app.models.categoria_normativa import CategoriaNormativa
from app.models.documento_normativa import DocumentoNormativa

BASE_URL = "https://www.siamoesercito.org"
INDEX_URL = f"{BASE_URL}/index.php/normative"
LOGIN_URL = f"{BASE_URL}/index.php/user/login"
USER_AGENT = "SIAMO-Lombardia-ImportBot/1.0 (+contatto: pmosca80@gmail.com)"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("import_normative")


def slugify(testo: str) -> str:
    testo = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode()
    testo = testo.lower().strip()
    testo = re.sub(r"[^a-z0-9]+", "-", testo)
    return testo.strip("-")


def normalizza_href_categoria(href: str) -> str:
    """Corregge il bug del menu sorgente: alcuni link mancano dello slash
    tra "/index.php/normative" e lo slug (es. "normativecfi-cfg")."""
    match = re.match(r"^(/index\.php/normative)(?!/)(.+)$", href)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return href


def normalizza_url_pdf(href: str) -> str:
    """Il link del PDF nell'HTML ha un prefisso /index.php/ duplicato (bug
    del sito sorgente) che restituisce 403. Il file vero è servito senza
    alcun prefisso /index.php/."""
    assoluto = urljoin(BASE_URL, href)
    return re.sub(r"^(https?://[^/]+)(/index\.php)+/", r"\1/", assoluto)


@dataclass
class CategoriaSub:
    macro_slug: str
    macro_nome: str
    sub_slug: str
    sub_nome: str
    href: str


@dataclass
class DocumentoTrovato:
    titolo: str
    data_pubblicazione: date | None
    url: str


@dataclass
class Report:
    categorie_processate: int = 0
    documenti_trovati: int = 0
    documenti_creati: int = 0
    documenti_aggiornati: int = 0
    pdf_scaricati: int = 0
    pdf_saltati_no_auth: int = 0
    errori: list[tuple[str, str, str]] = field(default_factory=list)

    def stampa(self) -> None:
        logger.info("=" * 60)
        logger.info("REPORT FINALE")
        logger.info("Categorie processate: %d", self.categorie_processate)
        logger.info("Documenti trovati:    %d", self.documenti_trovati)
        logger.info("  creati:             %d", self.documenti_creati)
        logger.info("  aggiornati:         %d", self.documenti_aggiornati)
        logger.info("PDF scaricati:        %d", self.pdf_scaricati)
        logger.info("PDF saltati (no auth):%d", self.pdf_saltati_no_auth)
        logger.info("Errori:               %d", len(self.errori))
        for url, fase, dettaglio in self.errori:
            logger.error("  [%s] %s -> %s", fase, url, dettaglio)
        logger.info("=" * 60)


class ImporterNormative:
    def __init__(self, *, delay: float, dry_run: bool) -> None:
        self.delay = delay
        self.dry_run = dry_run
        self.report = Report()
        self.autenticato = False
        self.client = httpx.Client(
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            timeout=30.0,
        )

    def close(self) -> None:
        self.client.close()

    def _throttle(self) -> None:
        import time

        time.sleep(self.delay)

    def _get(self, url: str) -> BeautifulSoup | None:
        self._throttle()
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")
        except httpx.HTTPError as exc:
            self.report.errori.append((url, "GET", str(exc)))
            logger.warning("GET fallita per %s: %s", url, exc)
            return None

    def login(self) -> None:
        if not (settings.siamoesercito_username and settings.siamoesercito_password):
            logger.warning(
                "Credenziali siamoesercito.org non configurate: i PDF verranno saltati."
            )
            return

        self._throttle()
        try:
            resp = self.client.get(LOGIN_URL)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            self.report.errori.append((LOGIN_URL, "LOGIN-GET", str(exc)))
            logger.error("Impossibile aprire la pagina di login: %s", exc)
            return

        soup = BeautifulSoup(resp.text, "lxml")
        form_build_id_el = soup.select_one('input[name="form_build_id"]')
        op_el = soup.select_one('input[name="op"]')
        if form_build_id_el is None:
            self.report.errori.append((LOGIN_URL, "LOGIN-PARSE", "form_build_id non trovato"))
            logger.error("Form di login non riconosciuta (form_build_id assente).")
            return

        payload = {
            "name": settings.siamoesercito_username,
            "pass": settings.siamoesercito_password,
            "form_build_id": form_build_id_el["value"],
            "form_id": "user_login_form",
            "op": op_el["value"] if op_el else "Accedi",
        }

        self._throttle()
        try:
            resp = self.client.post(LOGIN_URL, data=payload)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            self.report.errori.append((LOGIN_URL, "LOGIN-POST", str(exc)))
            logger.error("Login fallito: %s", exc)
            return

        if "user/logout" in resp.text:
            self.autenticato = True
            logger.info("Login su siamoesercito.org riuscito.")
        else:
            self.report.errori.append((LOGIN_URL, "LOGIN", "credenziali non accettate"))
            logger.error("Login fallito: credenziali non accettate o form cambiata.")

    def estrai_albero_categorie(self) -> list[CategoriaSub]:
        soup = self._get(INDEX_URL)
        if soup is None:
            return []

        risultato: list[CategoriaSub] = []
        for card in soup.select("div.col-3.card.shadow"):
            macro_a = card.select_one("h3 a")
            if macro_a is None:
                continue
            macro_nome = macro_a.get_text(strip=True)
            macro_href = normalizza_href_categoria(macro_a["href"])
            macro_slug = macro_href.rstrip("/").split("/")[-1]

            for sub_a in card.select(".list-item-title a"):
                sub_nome = sub_a.get_text(strip=True)
                sub_href = normalizza_href_categoria(sub_a["href"])
                if "taxonomy/term/" in sub_href:
                    sub_slug = slugify(sub_nome)
                else:
                    sub_slug = sub_href.rstrip("/").split("/")[-1]
                risultato.append(
                    CategoriaSub(
                        macro_slug=macro_slug,
                        macro_nome=macro_nome,
                        sub_slug=sub_slug,
                        sub_nome=sub_nome,
                        href=urljoin(BASE_URL, sub_href),
                    )
                )
        return risultato

    def estrai_documenti_categoria(self, categoria: CategoriaSub) -> list[DocumentoTrovato]:
        documenti: list[DocumentoTrovato] = []
        visti: set[str] = set()
        pagina = 0
        max_pagine = 100  # guardia di sicurezza contro loop infiniti

        while pagina < max_pagine:
            separatore = "&" if "?" in categoria.href else "?"
            url_pagina = categoria.href if pagina == 0 else f"{categoria.href}{separatore}page={pagina}"
            soup = self._get(url_pagina)
            if soup is None:
                break

            trovati_in_pagina = 0
            for container in soup.select("div.it-right-zone"):
                link_el = container.select_one("h4 a")
                if link_el is None:
                    continue
                node_url = urljoin(BASE_URL, link_el["href"])
                if node_url in visti:
                    continue
                visti.add(node_url)
                trovati_in_pagina += 1

                time_el = container.select_one("time[datetime]")
                data_pub = None
                if time_el is not None:
                    try:
                        data_pub = datetime.fromisoformat(
                            time_el["datetime"].replace("Z", "+00:00")
                        ).date()
                    except ValueError:
                        pass

                documenti.append(
                    DocumentoTrovato(
                        titolo=link_el.get_text(strip=True),
                        data_pubblicazione=data_pub,
                        url=node_url,
                    )
                )

            if trovati_in_pagina == 0:
                break
            pagina += 1

        return documenti

    def estrai_allegato_nodo(self, url_nodo: str) -> tuple[str, str] | None:
        """Ritorna (href, nome_file_leggibile) del PDF allegato al nodo."""
        soup = self._get(url_nodo)
        if soup is None:
            return None
        allegati = soup.select_one("div.field--name-field-allegati")
        if allegati is None:
            return None
        pdf_a = allegati.select_one('a[href*="system/files"]')
        if pdf_a is None:
            return None
        nome_file = pdf_a.get_text(strip=True) or pdf_a["href"].split("/")[-1]
        return pdf_a["href"], nome_file

    def scarica_pdf(self, pdf_href: str) -> bytes | None:
        if not self.autenticato:
            self.report.pdf_saltati_no_auth += 1
            return None
        url_pdf = normalizza_url_pdf(pdf_href)
        self._throttle()
        try:
            resp = self.client.get(url_pdf)
            resp.raise_for_status()
            if "text/html" in resp.headers.get("content-type", ""):
                # Redirect finito su una pagina HTML (es. login): non è un PDF.
                raise httpx.HTTPError("risposta HTML invece del PDF (sessione scaduta?)")
            return resp.content
        except httpx.HTTPError as exc:
            self.report.errori.append((url_pdf, "DOWNLOAD-PDF", str(exc)))
            logger.warning("Download PDF fallito per %s: %s", url_pdf, exc)
            return None


async def get_or_create_categoria(
    session, *, slug: str, nome: str, parent_id: int | None
) -> int:
    esistente = (
        await session.execute(
            select(CategoriaNormativa).where(CategoriaNormativa.slug == slug)
        )
    ).scalar_one_or_none()
    if esistente is not None:
        if esistente.nome != nome or esistente.parent_id != parent_id:
            esistente.nome = nome
            esistente.parent_id = parent_id
            await session.flush()
        return esistente.id

    riga = CategoriaNormativa(slug=slug, nome=nome, parent_id=parent_id)
    session.add(riga)
    await session.flush()
    return riga.id


async def assicura_categorie(session, categorie: list[CategoriaSub]) -> dict[str, int]:
    """Crea/aggiorna macro e sotto-categorie in DB, ritorna sub_slug -> id."""
    macro_id_by_slug: dict[str, int] = {}
    for macro_slug, macro_nome in {(c.macro_slug, c.macro_nome) for c in categorie}:
        macro_id_by_slug[macro_slug] = await get_or_create_categoria(
            session, slug=macro_slug, nome=macro_nome, parent_id=None
        )

    sub_id_by_slug: dict[str, int] = {}
    for categoria in categorie:
        sub_id_by_slug[categoria.sub_slug] = await get_or_create_categoria(
            session,
            slug=categoria.sub_slug,
            nome=categoria.sub_nome,
            parent_id=macro_id_by_slug[categoria.macro_slug],
        )
    return sub_id_by_slug


async def upsert_documento(
    session,
    *,
    categoria: CategoriaSub,
    categoria_id: int | None,
    documento: DocumentoTrovato,
    importer: ImporterNormative,
    recheck_pdf: bool,
) -> None:
    esistente = (
        await session.execute(
            select(DocumentoNormativa).where(
                DocumentoNormativa.source_url == documento.url
            )
        )
    ).scalar_one_or_none()

    e_nuovo = esistente is None
    riga = esistente or DocumentoNormativa(source_url=documento.url)

    riga.titolo = documento.titolo
    riga.data_pubblicazione = documento.data_pubblicazione

    scarica = e_nuovo or riga.file_path is None or recheck_pdf
    if scarica and importer.autenticato:
        allegato = importer.estrai_allegato_nodo(documento.url)
        if allegato:
            pdf_href, nome_file_originale = allegato
            contenuto = importer.scarica_pdf(pdf_href)
            if contenuto is not None:
                checksum = hashlib.sha256(contenuto).hexdigest()
                if checksum != riga.checksum:
                    nome_file = slugify(nome_file_originale) or "documento"
                    file_path = (
                        f"{categoria.macro_slug}/{categoria.sub_slug}/{nome_file}.pdf"
                    )
                    if not importer.dry_run:
                        client = get_r2_client()
                        upload_file(
                            client,
                            bucket=get_bucket_normative(),
                            key=file_path,
                            data=contenuto,
                            content_type="application/pdf",
                        )
                    riga.file_path = file_path
                    riga.checksum = checksum
                    riga.file_size_kb = len(contenuto) // 1024
                    riga.imported_at = datetime.now(timezone.utc)
                    importer.report.pdf_scaricati += 1
    elif scarica and not importer.autenticato:
        importer.report.pdf_saltati_no_auth += 1

    if importer.dry_run:
        azione = "creerebbe" if e_nuovo else "aggiornerebbe"
        logger.info("[dry-run] %s: %s", azione, documento.titolo)
        return

    riga.categoria_id = categoria_id
    if e_nuovo:
        session.add(riga)
        importer.report.documenti_creati += 1
    else:
        importer.report.documenti_aggiornati += 1
    await session.flush()


async def esegui_import(args: argparse.Namespace) -> None:
    importer = ImporterNormative(delay=args.delay, dry_run=args.dry_run)
    try:
        importer.login()
        categorie = importer.estrai_albero_categorie()
        if args.categoria:
            categorie = [c for c in categorie if c.sub_slug == args.categoria]
            if not categorie:
                logger.error("Nessuna categoria trovata con slug '%s'.", args.categoria)
                return

        logger.info("Categorie da processare: %d", len(categorie))

        totale_processati = 0
        async with AsyncSessionLocal() as session:
            categoria_id_by_sub_slug: dict[str, int] = {}
            if not args.dry_run:
                categoria_id_by_sub_slug = await assicura_categorie(session, categorie)
                await session.commit()

            for categoria in categorie:
                logger.info(
                    "Categoria: %s / %s", categoria.macro_nome, categoria.sub_nome
                )
                documenti = importer.estrai_documenti_categoria(categoria)
                importer.report.categorie_processate += 1
                importer.report.documenti_trovati += len(documenti)

                for documento in documenti:
                    if args.limit and totale_processati >= args.limit:
                        break
                    try:
                        await upsert_documento(
                            session,
                            categoria=categoria,
                            categoria_id=categoria_id_by_sub_slug.get(categoria.sub_slug),
                            documento=documento,
                            importer=importer,
                            recheck_pdf=args.recheck_pdf,
                        )
                        if not args.dry_run:
                            await session.commit()
                    except Exception as exc:  # noqa: BLE001 - accumula e continua
                        await session.rollback()
                        importer.report.errori.append((documento.url, "UPSERT", str(exc)))
                        logger.exception("Errore importando %s", documento.url)
                    totale_processati += 1

                if args.limit and totale_processati >= args.limit:
                    break
    finally:
        importer.close()

    importer.report.stampa()


async def esegui_verify() -> None:
    async with AsyncSessionLocal() as session:
        righe = (
            (
                await session.execute(
                    select(DocumentoNormativa).where(
                        DocumentoNormativa.file_path.is_not(None)
                    )
                )
            )
            .scalars()
            .all()
        )
    chiavi_db = {r.file_path for r in righe}
    logger.info("Record con file su R2 (da DB): %d", len(chiavi_db))

    try:
        client = get_r2_client()
        bucket = get_bucket_normative()
    except R2NonConfigurato as exc:
        logger.error("Impossibile verificare R2: %s", exc)
        return

    chiavi_r2 = list_keys(client, bucket=bucket, prefix="")
    logger.info("Oggetti trovati su R2 nel bucket: %d", len(chiavi_r2))

    mancanti_su_r2 = chiavi_db - chiavi_r2
    orfani_su_r2 = chiavi_r2 - chiavi_db

    if mancanti_su_r2:
        logger.warning("Record DB senza file su R2 (%d):", len(mancanti_su_r2))
        for chiave in sorted(mancanti_su_r2):
            logger.warning("  %s", chiave)
    if orfani_su_r2:
        logger.warning("File su R2 senza record DB (%d):", len(orfani_su_r2))
        for chiave in sorted(orfani_su_r2):
            logger.warning("  %s", chiave)
    if not mancanti_su_r2 and not orfani_su_r2:
        logger.info("Integrità OK: DB e R2 allineati.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--categoria", help="Limita a una sotto-categoria (slug)")
    parser.add_argument("--limit", type=int, help="Numero massimo di documenti da processare")
    parser.add_argument("--delay", type=float, default=1.5, help="Secondi di attesa tra le richieste HTTP")
    parser.add_argument("--dry-run", action="store_true", help="Non scrive su DB/R2, solo log")
    parser.add_argument(
        "--recheck-pdf",
        action="store_true",
        help="Ri-scarica e ricalcola il checksum anche per documenti già importati",
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verifica integrità DB vs R2 e termina"
    )
    args = parser.parse_args()

    if args.verify:
        asyncio.run(esegui_verify())
    else:
        asyncio.run(esegui_import(args))


if __name__ == "__main__":
    main()
