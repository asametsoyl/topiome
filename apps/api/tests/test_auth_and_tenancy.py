from __future__ import annotations

from conftest import login, register


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_register_me_logout_cycle(client):
    user = register(client)
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["email"] == user["email"]
    assert me.json()["role"] == "owner"

    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


def test_session_cookie_is_http_only(client):
    client.cookies.clear()
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Cookie Check", "email": "cookie@example.com", "password": "long-enough-pass"},
    )
    assert response.status_code == 201
    assert "httponly" in response.headers["set-cookie"].lower()


def test_wrong_password_is_rejected(client):
    user = register(client)
    client.cookies.clear()
    response = client.post(
        "/api/v1/auth/login", json={"email": user["email"], "password": "not-the-password"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_duplicate_email_conflicts(client):
    user = register(client)
    client.cookies.clear()
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Again", "email": user["email"], "password": "another-long-pass"},
    )
    assert response.status_code == 409


def test_other_org_cannot_see_project(client):
    owner = register(client, name="Owner One")
    project = client.post(
        "/api/v1/projects", json={"name": "Secret", "description": "", "disease_pack": "breast"}
    ).json()

    register(client, name="Intruder Two")
    assert client.get(f"/api/v1/projects/{project['id']}").status_code == 404
    assert all(p["id"] != project["id"] for p in client.get("/api/v1/projects").json())

    login(client, owner["email"], owner["password"])
    assert client.get(f"/api/v1/projects/{project['id']}").status_code == 200


def test_foreign_origin_is_blocked_for_writes(client):
    register(client)
    response = client.post(
        "/api/v1/projects",
        json={"name": "CSRF", "description": "", "disease_pack": "breast"},
        headers={"Origin": "https://evil.example"},
    )
    assert response.status_code == 403


def test_timestamps_are_sent_as_utc(client):
    register(client)
    created_at = client.get("/api/v1/auth/me").json()["user"]["created_at"]
    # Without an offset browsers read the value as local time.
    assert created_at.endswith(("Z", "+00:00")), created_at


def test_repeated_wrong_passwords_are_throttled(client):
    user = register(client)
    client.cookies.clear()
    statuses = [
        client.post(
            "/api/v1/auth/login", json={"email": user["email"], "password": "wrong-password-x"}
        ).status_code
        for _ in range(11)
    ]
    assert statuses[:10] == [401] * 10
    assert statuses[10] == 429
    # Even the right password waits until the window passes.
    blocked = client.post(
        "/api/v1/auth/login", json={"email": user["email"], "password": user["password"]}
    )
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0
