import pytest_asyncio


@pytest_asyncio.fixture
async def contesto(client):
    """Organizzazione + membro autore, pronti per creare comunicazioni."""
    org = (
        await client.post("/organizzazioni", json={"nome": "Assoc", "slug": "assoc"})
    ).json()
    membro = (
        await client.post(
            f"/organizzazioni/{org['id']}/membri",
            json={"nome": "Autore", "cognome": "Re", "email": "autore@example.com"},
        )
    ).json()
    return org, membro


async def test_ciclo_di_vita_comunicazione(client, contesto):
    org, membro = contesto
    oid = org["id"]

    resp = await client.post(
        f"/organizzazioni/{oid}/comunicazioni",
        json={
            "titolo": "Assemblea",
            "corpo": "Convocazione assemblea ordinaria.",
            "autore_id": membro["id"],
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

    # non raggiungibile da un altro tenant
    resp = await client.get(
        f"/organizzazioni/{altra['id']}/comunicazioni/{com['id']}"
    )
    assert resp.status_code == 404
