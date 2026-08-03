"""Test a livello ORM: relazioni e vincoli delle entità del modello dati.

Non passano dagli endpoint HTTP (campagne/documenti/letture non hanno ancora
API dedicate); esercitano direttamente i modelli e le loro relazioni.
"""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models import (
    Campagna,
    Comunicazione,
    Documento,
    Lettura,
    Organizzazione,
    Utente,
)


async def _crea_grafo(session):
    org = Organizzazione(nome="Assoc", slug="assoc")
    session.add(org)
    await session.flush()

    utente = Utente(
        organizzazione_id=org.id, nome="Anna", cognome="Bianchi", email="anna@example.com"
    )
    campagna = Campagna(organizzazione_id=org.id, nome="Tesseramento 2026")
    session.add_all([utente, campagna])
    await session.flush()

    com = Comunicazione(
        organizzazione_id=org.id,
        titolo="Rinnovo",
        corpo="Rinnova la tessera.",
        campagna_id=campagna.id,
        autore_id=utente.id,
    )
    session.add(com)
    await session.flush()

    doc = Documento(
        organizzazione_id=org.id,
        nome_file="modulo.pdf",
        url="https://storage/modulo.pdf",
        comunicazione_id=com.id,
        caricato_da_id=utente.id,
    )
    lettura = Lettura(
        organizzazione_id=org.id, comunicazione_id=com.id, utente_id=utente.id
    )
    session.add_all([doc, lettura])
    await session.flush()
    return org, utente, campagna, com, doc, lettura


async def test_relazioni_navigabili(db_session):
    org, utente, campagna, com, doc, lettura = await _crea_grafo(db_session)

    # comunicazione -> campagna / autore / documenti / letture
    com2 = (
        await db_session.execute(
            select(Comunicazione)
            .where(Comunicazione.id == com.id)
            .options(
                selectinload(Comunicazione.campagna),
                selectinload(Comunicazione.autore),
                selectinload(Comunicazione.documenti),
                selectinload(Comunicazione.letture),
            )
        )
    ).scalar_one()
    assert com2.campagna.id == campagna.id
    assert com2.autore.id == utente.id
    assert [d.id for d in com2.documenti] == [doc.id]
    assert [lt.id for lt in com2.letture] == [lettura.id]

    # campagna -> comunicazioni
    campagna2 = (
        await db_session.execute(
            select(Campagna)
            .where(Campagna.id == campagna.id)
            .options(selectinload(Campagna.comunicazioni))
        )
    ).scalar_one()
    assert [c.id for c in campagna2.comunicazioni] == [com.id]

    # documento -> uploader / comunicazione
    doc2 = (
        await db_session.execute(
            select(Documento)
            .where(Documento.id == doc.id)
            .options(
                selectinload(Documento.caricato_da),
                selectinload(Documento.comunicazione),
            )
        )
    ).scalar_one()
    assert doc2.caricato_da.id == utente.id
    assert doc2.comunicazione.id == com.id

    # letto_at valorizzato dal default lato DB
    assert lettura.letto_at is not None


async def test_lettura_unica_per_utente_e_comunicazione(db_session):
    org, utente, campagna, com, doc, lettura = await _crea_grafo(db_session)

    # seconda lettura dello stesso utente sulla stessa comunicazione -> viola il vincolo
    db_session.add(
        Lettura(
            organizzazione_id=org.id, comunicazione_id=com.id, utente_id=utente.id
        )
    )
    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_campagna_nome_unico_per_org(db_session):
    org = Organizzazione(nome="Assoc", slug="assoc")
    db_session.add(org)
    await db_session.flush()

    db_session.add(Campagna(organizzazione_id=org.id, nome="Natale"))
    await db_session.flush()

    db_session.add(Campagna(organizzazione_id=org.id, nome="Natale"))
    with pytest.raises(IntegrityError):
        await db_session.flush()
