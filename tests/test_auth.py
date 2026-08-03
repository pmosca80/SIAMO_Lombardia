"""Test end-to-end del flusso di autenticazione: magic link, refresh
(con rotazione), logout e autorizzazione basata sul ruolo.
"""


async def test_richiesta_magic_link_email_inesistente_non_rivela_nulla(client, organizzazione):
    resp = await client.post(
        "/auth/magic-link",
        json={"organizzazione_id": organizzazione["id"], "email": "sconosciuto@example.com"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["debug_link"] is None


async def test_verifica_magic_link_emette_coppia_di_token(client, organizzazione, autentica):
    resp = await client.post(
        "/auth/magic-link",
        json={
            "organizzazione_id": organizzazione["id"],
            "email": "admin@assoc-test.example.com",
        },
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["debug_link"].split("token=", 1)[1]

    resp = await client.post("/auth/verify", json={"token": token})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


async def test_magic_link_e_monouso(client, organizzazione):
    resp = await client.post(
        "/auth/magic-link",
        json={
            "organizzazione_id": organizzazione["id"],
            "email": "admin@assoc-test.example.com",
        },
    )
    token = resp.json()["debug_link"].split("token=", 1)[1]

    resp = await client.post("/auth/verify", json={"token": token})
    assert resp.status_code == 200

    # riutilizzo dello stesso token -> rifiutato
    resp = await client.post("/auth/verify", json={"token": token})
    assert resp.status_code == 401


async def test_verifica_token_invalido_rifiutata(client):
    resp = await client.post("/auth/verify", json={"token": "non-esiste"})
    assert resp.status_code == 401


async def test_refresh_ruota_il_token_e_revoca_il_precedente(client, organizzazione):
    resp = await client.post(
        "/auth/magic-link",
        json={
            "organizzazione_id": organizzazione["id"],
            "email": "admin@assoc-test.example.com",
        },
    )
    token = resp.json()["debug_link"].split("token=", 1)[1]
    coppia = (await client.post("/auth/verify", json={"token": token})).json()

    resp = await client.post(
        "/auth/refresh", json={"refresh_token": coppia["refresh_token"]}
    )
    assert resp.status_code == 200, resp.text
    nuova_coppia = resp.json()
    assert nuova_coppia["refresh_token"] != coppia["refresh_token"]

    # il refresh token precedente non è più utilizzabile (rotazione)
    resp = await client.post(
        "/auth/refresh", json={"refresh_token": coppia["refresh_token"]}
    )
    assert resp.status_code == 401


async def test_refresh_token_invalido_rifiutato(client):
    resp = await client.post("/auth/refresh", json={"refresh_token": "non-esiste"})
    assert resp.status_code == 401


async def test_logout_revoca_il_refresh_token(client, organizzazione):
    resp = await client.post(
        "/auth/magic-link",
        json={
            "organizzazione_id": organizzazione["id"],
            "email": "admin@assoc-test.example.com",
        },
    )
    token = resp.json()["debug_link"].split("token=", 1)[1]
    coppia = (await client.post("/auth/verify", json={"token": token})).json()

    resp = await client.post(
        "/auth/logout", json={"refresh_token": coppia["refresh_token"]}
    )
    assert resp.status_code == 204

    resp = await client.post(
        "/auth/refresh", json={"refresh_token": coppia["refresh_token"]}
    )
    assert resp.status_code == 401


async def test_token_scaduto_o_malformato_rifiutato_dal_middleware(client, organizzazione):
    client.headers["Authorization"] = "Bearer token-non-valido"
    resp = await client.get(f"/organizzazioni/{organizzazione['id']}/utenti")
    assert resp.status_code == 401


async def test_socio_non_puo_creare_utenti(client, organizzazione, autentica):
    # l'admin (fixture `organizzazione`) crea un socio
    resp = await client.post(
        f"/organizzazioni/{organizzazione['id']}/utenti",
        json={"nome": "Socio", "cognome": "Semplice", "email": "socio@example.com"},
    )
    assert resp.status_code == 201, resp.text

    # il socio effettua il login: ha un token valido, ma ruolo "socio"
    token_socio = await autentica(
        organizzazione_id=organizzazione["id"], email="socio@example.com"
    )
    client.headers["Authorization"] = f"Bearer {token_socio}"

    resp = await client.post(
        f"/organizzazioni/{organizzazione['id']}/utenti",
        json={"nome": "Altro", "cognome": "Utente", "email": "altro@example.com"},
    )
    assert resp.status_code == 403

    # ma può comunque consultare l'elenco soci
    resp = await client.get(f"/organizzazioni/{organizzazione['id']}/utenti")
    assert resp.status_code == 200


async def test_socio_non_puo_creare_comunicazioni(client, organizzazione, autentica):
    resp = await client.post(
        f"/organizzazioni/{organizzazione['id']}/utenti",
        json={"nome": "Socio", "cognome": "Semplice", "email": "socio2@example.com"},
    )
    assert resp.status_code == 201, resp.text

    token_socio = await autentica(
        organizzazione_id=organizzazione["id"], email="socio2@example.com"
    )
    client.headers["Authorization"] = f"Bearer {token_socio}"

    resp = await client.post(
        f"/organizzazioni/{organizzazione['id']}/comunicazioni",
        json={"titolo": "T", "corpo": "C"},
    )
    assert resp.status_code == 403
