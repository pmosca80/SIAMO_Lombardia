"""Test end-to-end del flusso di autenticazione: registrazione + verifica
email, login, reset password, refresh (con rotazione), logout e
autorizzazione basata sul ruolo.
"""
import logging


async def _ultimo_link(caplog, frammento_path: str) -> str:
    """Il backend di test (`LogEmailSender`) logga il link invece di
    inviarlo: lo si recupera dai log invece che da un'email reale."""
    for record in reversed(caplog.records):
        if frammento_path in record.getMessage():
            return record.getMessage().split(frammento_path, 1)[1].split(": ", 1)[-1].strip()
    raise AssertionError(f"Nessun link con '{frammento_path}' trovato nei log")


async def test_registrazione_e_verifica_email(client, organizzazione, caplog):
    oid = organizzazione["id"]
    with caplog.at_level(logging.INFO, logger="app.email"):
        resp = await client.post(
            "/auth/registrati",
            json={
                "organizzazione_id": oid,
                "nome": "Nuovo",
                "cognome": "Socio",
                "email": "nuovo@example.com",
                "numero_tessera": "LC-00042",
                "password": "Password123!",
            },
        )
        assert resp.status_code == 201, resp.text

        link = await _ultimo_link(caplog, "verifica email per")
    token = link.split("token=", 1)[1]

    # prima della verifica il login è rifiutato (email non verificata)
    resp = await client.post(
        "/auth/login",
        json={"organizzazione_id": oid, "email": "nuovo@example.com", "password": "Password123!"},
    )
    assert resp.status_code == 403

    resp = await client.post("/auth/verifica-email", params={"token": token})
    assert resp.status_code == 200, resp.text
    assert resp.json()["access_token"]

    # dopo la verifica il login funziona
    resp = await client.post(
        "/auth/login",
        json={"organizzazione_id": oid, "email": "nuovo@example.com", "password": "Password123!"},
    )
    assert resp.status_code == 200, resp.text


async def test_registrazione_email_duplicata_non_rivela_nulla(client, organizzazione):
    resp = await client.post(
        "/auth/registrati",
        json={
            "organizzazione_id": organizzazione["id"],
            "nome": "Admin",
            "cognome": "Test",
            "email": "admin@assoc-test.example.com",
            "numero_tessera": "LC-00099",
            "password": "AltraPassword123!",
        },
    )
    # stessa risposta generica sia in caso di successo che di email già in uso
    assert resp.status_code == 201
    assert "riceverai" in resp.json()["message"]


async def test_verifica_email_token_invalido_rifiutata(client):
    resp = await client.post("/auth/verifica-email", params={"token": "non-esiste"})
    assert resp.status_code == 401


async def test_login_password_errata_rifiutato(client, organizzazione):
    resp = await client.post(
        "/auth/login",
        json={
            "organizzazione_id": organizzazione["id"],
            "email": "admin@assoc-test.example.com",
            "password": "password-sbagliata",
        },
    )
    assert resp.status_code == 401


async def test_login_email_inesistente_rifiutato(client, organizzazione):
    resp = await client.post(
        "/auth/login",
        json={
            "organizzazione_id": organizzazione["id"],
            "email": "sconosciuto@example.com",
            "password": "Password123!",
        },
    )
    assert resp.status_code == 401


async def test_password_dimenticata_e_reset(client, organizzazione, caplog):
    oid = organizzazione["id"]
    with caplog.at_level(logging.INFO, logger="app.email"):
        resp = await client.post(
            "/auth/password-dimenticata",
            json={"organizzazione_id": oid, "email": "admin@assoc-test.example.com"},
        )
        assert resp.status_code == 200, resp.text

        link = await _ultimo_link(caplog, "reset password per")
    token = link.split("token=", 1)[1]

    resp = await client.post(
        "/auth/reset-password", json={"token": token, "nuova_password": "NuovaPassword456!"}
    )
    assert resp.status_code == 200, resp.text

    # il token è monouso
    resp = await client.post(
        "/auth/reset-password", json={"token": token, "nuova_password": "Altra789!"}
    )
    assert resp.status_code == 401

    # la vecchia password non funziona più, la nuova sì
    resp = await client.post(
        "/auth/login",
        json={
            "organizzazione_id": oid,
            "email": "admin@assoc-test.example.com",
            "password": "Password123!",
        },
    )
    assert resp.status_code == 401
    resp = await client.post(
        "/auth/login",
        json={
            "organizzazione_id": oid,
            "email": "admin@assoc-test.example.com",
            "password": "NuovaPassword456!",
        },
    )
    assert resp.status_code == 200


async def test_password_dimenticata_email_inesistente_non_rivela_nulla(client, organizzazione):
    resp = await client.post(
        "/auth/password-dimenticata",
        json={"organizzazione_id": organizzazione["id"], "email": "sconosciuto@example.com"},
    )
    assert resp.status_code == 200
    assert "riceverai" in resp.json()["message"]


async def test_reset_password_token_invalido_rifiutato(client):
    resp = await client.post(
        "/auth/reset-password", json={"token": "non-esiste", "nuova_password": "Password123!"}
    )
    assert resp.status_code == 401


async def test_refresh_ruota_il_token_e_revoca_il_precedente(client, organizzazione, autentica):
    resp = await client.post(
        "/auth/login",
        json={
            "organizzazione_id": organizzazione["id"],
            "email": "admin@assoc-test.example.com",
            "password": "Password123!",
        },
    )
    coppia = resp.json()

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
        "/auth/login",
        json={
            "organizzazione_id": organizzazione["id"],
            "email": "admin@assoc-test.example.com",
            "password": "Password123!",
        },
    )
    coppia = resp.json()

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
        json={
            "nome": "Socio",
            "cognome": "Semplice",
            "email": "socio@example.com",
            "password": "Password123!",
        },
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
        json={
            "nome": "Socio",
            "cognome": "Semplice",
            "email": "socio2@example.com",
            "password": "Password123!",
        },
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
