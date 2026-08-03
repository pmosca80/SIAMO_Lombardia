async def test_crud_organizzazione(client):
    # create
    resp = await client.post(
        "/organizzazioni", json={"nome": "ACME", "slug": "acme"}
    )
    assert resp.status_code == 201, resp.text
    org = resp.json()
    assert org["slug"] == "acme"
    assert org["attiva"] is True
    oid = org["id"]

    # read
    resp = await client.get(f"/organizzazioni/{oid}")
    assert resp.status_code == 200

    # list
    resp = await client.get("/organizzazioni")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # update
    resp = await client.patch(f"/organizzazioni/{oid}", json={"nome": "ACME 2"})
    assert resp.status_code == 200
    assert resp.json()["nome"] == "ACME 2"

    # delete
    resp = await client.delete(f"/organizzazioni/{oid}")
    assert resp.status_code == 204

    resp = await client.get(f"/organizzazioni/{oid}")
    assert resp.status_code == 404


async def test_slug_duplicato_va_in_conflitto(client):
    await client.post("/organizzazioni", json={"nome": "A", "slug": "dup"})
    resp = await client.post("/organizzazioni", json={"nome": "B", "slug": "dup"})
    assert resp.status_code == 409


async def test_get_organizzazione_inesistente(client):
    resp = await client.get("/organizzazioni/999")
    assert resp.status_code == 404


async def test_slug_non_valido_rifiutato(client):
    resp = await client.post(
        "/organizzazioni", json={"nome": "X", "slug": "Slug Non Valido!"}
    )
    assert resp.status_code == 422
