"""API test fixtures.

Settings are read once at import time, so the test database and storage
directory are configured through environment variables before ``app`` loads.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="topiome-api-tests-"))
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP / 'test.db'}"
os.environ["STORAGE_DIR"] = str(_TMP / "storage")
os.environ["AUTO_SEED"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters!"
os.environ["TOPIOME_GIT_COMMIT"] = "test-commit-0123456789"

import json  # noqa: E402
import secrets  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, *, name: str = "Ada Researcher") -> dict:
    """Register a fresh user + org; leaves the session cookie on ``client``."""
    client.cookies.clear()
    email = f"user-{secrets.token_hex(4)}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "password": "correct-horse-battery", "org_name": "Lab"},
    )
    assert response.status_code == 201, response.text
    return {**response.json(), "email": email, "password": "correct-horse-battery"}


def login(client: TestClient, email: str, password: str) -> None:
    client.cookies.clear()
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text


def create_demo_run(client: TestClient, pack: str = "glioblastoma") -> dict:
    """Project → demo sample (no files) → run. BackgroundTasks finish before return."""
    project = client.post(
        "/api/v1/projects", json={"name": "Pilot", "description": "", "disease_pack": pack}
    )
    assert project.status_code == 201, project.text
    sample = client.post(
        f"/api/v1/projects/{project.json()['id']}/samples",
        data={"metadata": json.dumps({"name": "Demo section", "disease_pack": pack})},
    )
    assert sample.status_code == 201, sample.text
    run = client.post(
        f"/api/v1/samples/{sample.json()['id']}/runs",
        json={"params": {"n_spots": 300, "lr_permutations": 19}},
    )
    assert run.status_code == 201, run.text
    detail = client.get(f"/api/v1/runs/{run.json()['id']}")
    assert detail.status_code == 200
    return detail.json()
