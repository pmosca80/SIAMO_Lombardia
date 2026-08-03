async def test_crea_e_lista_membri(client, organizzazione):
    oid = organizzazione["id"]
    resp = await client.post(
        f"/organizzazioni/{oid}/membri",
        json={"nome": "Mario", "cognome": "Rossi", "email": "mario@example.com"},
    )
    assert resp.status_code == 201, resp.text
    membro = resp.json()
    assert membro["ruolo"] == "socio"  # default
    assert membro["organizzazione_id"] == oid

    resp = await client.get(f"/organizzazioni/{oid}/membri")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_email_duplicata_stessa_org_va_in_conflitto(client, organizzazione):
    oid = organizzazione["id"]
    payload = {"nome": "A", "cognome": "B", "email": "dup@example.com"}
    await client.post(f"/organizzazioni/{oid}/membri", json=payload)
    resp = await client.post(f"/organizzazioni/{oid}/membri", json=payload)
    assert resp.status_code == 409


async def test_membro_su_org_inesistente(client):
    resp = await client.post(
        "/organizzazioni/999/membri",
        json={"nome": "A", "cognome": "B", "email": "x@example.com"},
    )
    assert resp.status_code == 404


async def test_isolamento_tenant(client):
    org_a = (
        await client.post("/organizzazioni", json={"nome": "A", "slug": "org-a"})
    ).json()
    org_b = (
        await client.post("/organizzazioni", json={"nome": "B", "slug": "org-b"})
    ).json()

    membro = (
        await client.post(
            f"/organizzazioni/{org_a['id']}/membri",
            json={"nome": "M", "cognome": "R", "email": "m@example.com"},
        )
    ).json()

    # visibile nel proprio tenant
    resp = await client.get(f"/organizzazioni/{org_a['id']}/membri/{membro['id']}")
    assert resp.status_code == 200

    # invisibile da un altro tenant
    resp = await client.get(f"/organizzazioni/{org_b['id']}/membri/{membro['id']}")
    assert resp.status_code == 404

    # la stessa email è riutilizzabile in un altro tenant (unicità per-org)
    resp = await client.post(
        f"/organizzazioni/{org_b['id']}/membri",
        json={"nome": "M", "cognome": "R", "email": "m@example.com"},
    )
    assert resp.status_code == 201
