from __future__ import annotations

from conftest import create_demo_run, register

from app import worker
from app.config import Settings
from app.db import SessionLocal
from app.models import Run
from app.services.queue import recover_interrupted_runs


def _queued_from(run_id: str) -> str:
    with SessionLocal() as db:
        original = db.get(Run, run_id)
        clone = Run(
            org_id=original.org_id,
            project_id=original.project_id,
            sample_id=original.sample_id,
            disease_pack=original.disease_pack,
            status="queued",
            stage="queued",
            params={"n_spots": 200, "lr_permutations": 9},
        )
        db.add(clone)
        db.commit()
        return clone.id


def test_worker_drains_the_queue(client):
    register(client)
    run_id = _queued_from(create_demo_run(client)["id"])
    assert worker.run_once() >= 1
    with SessionLocal() as db:
        assert db.get(Run, run_id).status == "succeeded"


def test_interrupted_runs_are_failed_with_a_clear_reason(client):
    register(client)
    run_id = _queued_from(create_demo_run(client)["id"])
    with SessionLocal() as db:
        db.get(Run, run_id).status = "running"
        db.commit()
    assert recover_interrupted_runs() >= 1
    detail = client.get(f"/api/v1/runs/{run_id}").json()
    assert detail["status"] == "failed"
    assert detail["error_code"] == "interrupted"


def test_production_settings_are_checked():
    unsafe = Settings(
        app_env="production",
        secret_key="dev-only-change-me-please-32-characters-minimum",
        database_url="sqlite:///./topiome.db",
        allow_demo_login=True,
        _env_file=None,
    )
    problems = unsafe.production_problems()
    assert any("SECRET_KEY" in p for p in problems)
    assert any("PostgreSQL" in p for p in problems)
    assert any("DEMO" in p for p in problems)
    safe = Settings(
        app_env="production",
        secret_key="x" * 48,
        database_url="postgresql+psycopg://u:p@db/topiome",
        allow_demo_login=False,
        _env_file=None,
    )
    assert safe.production_problems() == []
    assert Settings(app_env="development", _env_file=None).production_problems() == []
