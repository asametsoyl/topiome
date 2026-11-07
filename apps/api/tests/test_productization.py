from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pyotp
from conftest import register

from app.db import SessionLocal
from app.models import Organization


def test_api_key_is_analyst_limited_and_revocable(client):
    register(client)
    created = client.post("/api/v1/api-keys", json={"name": "automation"})
    assert created.status_code == 201
    secret = created.json()["key"]

    assert client.get("/api/v1/org", headers={"X-API-Key": secret}).status_code == 200
    assert (
        client.get("/api/v1/org/audit-logs", headers={"X-API-Key": secret}).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/org/invitations",
            headers={"X-API-Key": secret},
            json={"email": "colleague@example.com", "role": "analyst"},
        ).status_code
        == 403
    )
    assert client.delete(f"/api/v1/api-keys/{created.json()['id']}").status_code == 200
    assert client.get("/api/v1/org", headers={"X-API-Key": secret}).status_code == 401


def test_invitation_acceptance_creates_membership(client):
    owner = register(client)
    with SessionLocal() as db:
        org = db.get(Organization, owner["org"]["id"])
        org.plan = "lab"
        db.commit()

    created = client.post(
        "/api/v1/org/invitations",
        json={"email": "colleague@example.com", "role": "analyst"},
    )
    assert created.status_code == 201
    token = parse_qs(urlparse(created.json()["accept_url"]).query)["token"][0]
    client.cookies.clear()
    accepted = client.post(
        "/api/v1/auth/invitations/accept",
        json={
            "token": token,
            "name": "New colleague",
            "password": "another-secure-password",
        },
    )
    assert accepted.status_code == 200
    assert accepted.json()["role"] == "analyst"
    assert accepted.json()["user"]["email"] == "colleague@example.com"


def test_only_owner_cannot_demote_themselves(client):
    register(client)
    member = client.get("/api/v1/org/members").json()[0]
    response = client.patch(
        f"/api/v1/org/members/{member['id']}", json={"role": "admin"}
    )
    assert response.status_code == 400


def test_mfa_setup_and_login_challenge(client):
    user = register(client)
    setup = client.post("/api/v1/auth/mfa/setup")
    assert setup.status_code == 200
    secret = setup.json()["secret"]
    enabled = client.post(
        "/api/v1/auth/mfa/enable", json={"code": pyotp.TOTP(secret).now()}
    )
    assert enabled.status_code == 200
    assert len(enabled.json()["recovery_codes"]) == 8

    client.post("/api/v1/auth/logout")
    client.cookies.clear()
    missing_code = client.post(
        "/api/v1/auth/login", json={"email": user["email"], "password": user["password"]}
    )
    assert missing_code.status_code == 401
    assert missing_code.headers.get("x-mfa-required") == "true"

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": user["password"],
            "totp_code": pyotp.TOTP(secret).now(),
        },
    )
    assert login.status_code == 200
    assert login.json()["user"]["mfa_enabled"] is True
