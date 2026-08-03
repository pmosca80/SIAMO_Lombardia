async def test_crea_e_lista_utenti(client, organizzazione):
    oid = organizzazione["id"]
    resp = await client.post(
        f"/organizzazioni/{oid}/utenti",
        json={"nome": "Mario", "cognome": "Rossi", "email": "mario@example.com"},
    )
    assert resp.status_code == 201, resp.text
    utente = resp.json()
    assert utente["ruolo"] == "socio"  # default
    assert utente["organizzazione_id"] == oid

    resp = await client.get(f"/organizzazioni/{oid}/utenti")
    assert resp.status_code == 200
    # l'admin bootstrap dalla fixture `organizzazione` + il socio appena creato
    assert len(resp.json()) == 2


async def test_email_duplicata_stessa_org_va_in_conflitto(client, organizzazione):
    oid = organizzazione["id"]
    payload = {"nome": "A", "cognome": "B", "email": "dup@example.com"}
    await client.post(f"/organizzazioni/{oid}/utenti", json=payload)
    resp = await client.post(f"/organizzazioni/{oid}/utenti", json=payload)
    assert resp.status_code == 409


async def test_richiesta_senza_token_rifiutata(client):
    resp = await client.post(
        "/organizzazioni/999/utenti",
        json={"nome": "A", "cognome": "B", "email": "x@example.com"},
    )
    assert resp.status_code == 401


async def test_organizzazione_nel_path_diversa_dal_token(client, organizzazione):
    # `organizzazione` autentica il client come admin di quel tenant: un
    # path con un altro organizzazione_id viene respinto prima ancora di
    # verificare se quell'organizzazione esiste davvero.
    resp = await client.post(
        "/organizzazioni/999/utenti",
        json={"nome": "A", "cognome": "B", "email": "x@example.com"},
    )
    assert resp.status_code == 403


async def test_isolamento_tenant(client, autentica):
    org_a = (
        await client.post(
            "/organizzazioni",
            json={
                "nome": "A",
                "slug": "org-a",
                "admin_nome": "Admin",
                "admin_cognome": "A",
                "admin_email": "admin@org-a.example.com",
            },
        )
    ).json()
    org_b = (
        await client.post(
            "/organizzazioni",
            json={
                "nome": "B",
                "slug": "org-b",
                "admin_nome": "Admin",
                "admin_cognome": "B",
                "admin_email": "admin@org-b.example.com",
            },
        )
    ).json()

    token_a = await autentica(organizzazione_id=org_a["id"], email="admin@org-a.example.com")
    token_b = await autentica(organizzazione_id=org_b["id"], email="admin@org-b.example.com")

    client.headers["Authorization"] = f"Bearer {token_a}"
    utente = (
        await client.post(
            f"/organizzazioni/{org_a['id']}/utenti",
            json={"nome": "M", "cognome": "R", "email": "m@example.com"},
        )
    ).json()

    # visibile nel proprio tenant
    resp = await client.get(f"/organizzazioni/{org_a['id']}/utenti/{utente['id']}")
    assert resp.status_code == 200

    # il token di A non autorizza l'accesso al path di B
    resp = await client.get(f"/organizzazioni/{org_b['id']}/utenti/{utente['id']}")
    assert resp.status_code == 403

    # con un token valido per B, ma un utente che esiste solo in A: invisibile
    client.headers["Authorization"] = f"Bearer {token_b}"
    resp = await client.get(f"/organizzazioni/{org_b['id']}/utenti/{utente['id']}")
    assert resp.status_code == 404

    # la stessa email è riutilizzabile in un altro tenant (unicità per-org)
    resp = await client.post(
        f"/organizzazioni/{org_b['id']}/utenti",
        json={"nome": "M", "cognome": "R", "email": "m@example.com"},
    )
    assert resp.status_code == 201
