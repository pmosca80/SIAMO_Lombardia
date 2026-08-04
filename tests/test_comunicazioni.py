import pytest_asyncio


@pytest_asyncio.fixture
async def contesto(client, autentica):
    """Organizzazione + utente autore, pronti per creare comunicazioni.

    Il client resta autenticato come amministratore dell'organizzazione
    creata: le chiamate successive nel test sono già autorizzate.
    """
    org = (
        await client.post(
            "/organizzazioni",
            json={
                "nome": "Assoc",
                "slug": "assoc",
                "admin_nome": "Admin",
                "admin_cognome": "Test",
                "admin_email": "admin@assoc.example.com",
                "admin_password": "Password123!",
            },
        )
    ).json()
    token = await autentica(organizzazione_id=org["id"], email="admin@assoc.example.com")
    client.headers["Authorization"] = f"Bearer {token}"

    utente = (
        await client.post(
            f"/organizzazioni/{org['id']}/utenti",
            json={"nome": "Autore", "cognome": "Re", "email": "autore@example.com"},
        )
    ).json()
    return org, utente


async def test_ciclo_di_vita_comunicazione(client, contesto):
    org, utente = contesto
    oid = org["id"]

    resp = await client.post(
        f"/organizzazioni/{oid}/comunicazioni",
        json={
            "titolo": "Assemblea",
            "corpo": "Convocazione assemblea ordinaria.",
            "autore_id": utente["id"],
        },
    )
    assert resp.status_code == 201, resp.text
    com = resp.json()
    assert com["stato"] == "bozza"
    assert com["inviata_at"] is None
    cid = com["id"]

    # invio
    resp = await client.post(f"/organizzazioni/{oid}/comunicazioni/{cid}/invia")
    assert resp.status_code == 200
    com = resp.json()
    assert com["stato"] == "inviata"
    assert com["inviata_at"] is not None

    # non più modificabile dopo l'invio
    resp = await client.patch(
        f"/organizzazioni/{oid}/comunicazioni/{cid}", json={"titolo": "Nuovo"}
    )
    assert resp.status_code == 409

    # doppio invio rifiutato
    resp = await client.post(f"/organizzazioni/{oid}/comunicazioni/{cid}/invia")
    assert resp.status_code == 409


async def test_autore_non_valido_rifiutato(client, contesto):
    org, _ = contesto
    resp = await client.post(
        f"/organizzazioni/{org['id']}/comunicazioni",
        json={"titolo": "T", "corpo": "C", "autore_id": 9999},
    )
    assert resp.status_code == 422


async def test_campagna_non_valida_rifiutata(client, contesto):
    org, _ = contesto
    resp = await client.post(
        f"/organizzazioni/{org['id']}/comunicazioni",
        json={"titolo": "T", "corpo": "C", "campagna_id": 9999},
    )
    assert resp.status_code == 422


async def test_comunicazione_isolata_per_tenant(client, contesto):
    org, _ = contesto
    altra = (
        await client.post("/organizzazioni", json={"nome": "Altra", "slug": "altra"})
    ).json()

    com = (
        await client.post(
            f"/organizzazioni/{org['id']}/comunicazioni",
            json={"titolo": "Privata", "corpo": "Solo per la mia org."},
        )
    ).json()

    # il token autentica per `org`: richiedere il path di un altro tenant è
    # respinto subito (403), senza nemmeno interrogare il repository.
    resp = await client.get(
        f"/organizzazioni/{altra['id']}/comunicazioni/{com['id']}"
    )
    assert resp.status_code == 403
