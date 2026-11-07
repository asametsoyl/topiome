from __future__ import annotations

from conftest import create_demo_run, login, register
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Membership, Result, Run, User
from app.security import hash_password
from app.services import pipeline as pipeline_service


def test_demo_run_succeeds_with_full_provenance(client):
    register(client)
    run = create_demo_run(client)

    assert run["status"] == "succeeded", run.get("error_message")
    provenance = run["provenance"]
    assert provenance["disease_pack"]["id"] == "glioblastoma"
    assert len(provenance["disease_pack"]["sha256"]) == 64
    assert provenance["reference"]["version"]
    assert provenance["software"]["commit"] == "test-commit-0123456789"
    assert provenance["params"]["n_spots"] == 300
    assert provenance["input"]["kind"] == "synthetic"
    assert provenance["input"]["synthetic_seed"] == 42


def test_results_carry_ported_analyses(client):
    register(client)
    run = create_demo_run(client)
    payload = client.get(f"/api/v1/runs/{run['id']}/results").json()["payload"]

    assert payload["provenance"]["software"]["commit"] == "test-commit-0123456789"
    assert payload["validation"]["method_concordance"]["mean_spot_agreement"] > 0
    assert payload["validation"]["atlas_check"]["status"] == "skipped_synthetic"
    assert len(payload["communication"]) == 10
    assert any("MGMT" in item for item in payload["summary"]["not_assessed"])


def test_report_needs_approval_before_export(client):
    register(client)
    run = create_demo_run(client)
    run_id = run["id"]
    assert run["report"]["status"] == "draft"

    preview = client.get(f"/api/v1/runs/{run_id}/report")
    assert preview.status_code == 200
    assert "Draft — not approved" in preview.text
    assert "Not assessed by this analysis" in preview.text

    assert client.get(f"/api/v1/runs/{run_id}/report/export").status_code == 409

    refused = client.post(f"/api/v1/runs/{run_id}/report/approve", json={"confirm_ruo": False})
    assert refused.status_code == 422

    approved = client.post(
        f"/api/v1/runs/{run_id}/report/approve",
        json={"confirm_ruo": True, "note": "Reviewed with PI"},
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"
    assert approved.json()["approved_by_name"] == "Ada Researcher"

    again = client.post(f"/api/v1/runs/{run_id}/report/approve", json={"confirm_ruo": True})
    assert again.status_code == 409

    exported = client.get(f"/api/v1/runs/{run_id}/report/export")
    assert exported.status_code == 200
    assert "attachment" in exported.headers["content-disposition"]
    assert "Approved for research use" in exported.text
    assert "Reviewed with PI" in exported.text

    actions = [entry["action"] for entry in client.get("/api/v1/org/audit-logs").json()]
    assert "report.approve" in actions
    assert "report.export" in actions


def test_gene_layer_is_not_fabricated_for_synthetic_data(client):
    register(client)
    run = create_demo_run(client)

    response = client.get(f"/api/v1/runs/{run['id']}/expression?gene=TP53")

    assert response.status_code == 422
    assert "uploaded Visium" in response.json()["detail"]


def test_roi_export_requires_approved_report_and_is_audited(client):
    register(client)
    run = create_demo_run(client)
    run_id = run["id"]
    payload = client.get(f"/api/v1/runs/{run_id}/results").json()["payload"]
    barcodes = [spot["barcode"] for spot in payload["spots"][:2]]

    denied = client.post(f"/api/v1/runs/{run_id}/roi-export", json={"barcodes": barcodes})
    assert denied.status_code == 409

    approved = client.post(f"/api/v1/runs/{run_id}/report/approve", json={"confirm_ruo": True})
    assert approved.status_code == 200
    exported = client.post(f"/api/v1/runs/{run_id}/roi-export", json={"barcodes": barcodes})
    assert exported.status_code == 200
    assert "text/csv" in exported.headers["content-type"]
    assert barcodes[0] in exported.text

    actions = [entry["action"] for entry in client.get("/api/v1/org/audit-logs").json()]
    assert "run.roi_export" in actions


def test_map_png_export_requires_approval_and_is_audited(client):
    register(client)
    run = create_demo_run(client)
    run_id = run["id"]
    metadata = {"width": 1200, "height": 800, "mode": "domain"}

    denied = client.post(f"/api/v1/runs/{run_id}/map-export", json=metadata)
    assert denied.status_code == 409
    client.post(f"/api/v1/runs/{run_id}/report/approve", json={"confirm_ruo": True})
    exported = client.post(f"/api/v1/runs/{run_id}/map-export", json=metadata)
    assert exported.status_code == 200
    assert exported.json() == {"ok": True}
    actions = [entry["action"] for entry in client.get("/api/v1/org/audit-logs").json()]
    assert "run.map_export" in actions


def _add_viewer(org_id: str) -> tuple[str, str]:
    email = f"viewer-{org_id[:8]}@example.com"
    with SessionLocal() as db:
        user = User(email=email, name="Read Only", password_hash=hash_password("viewer-password"))
        db.add(user)
        db.flush()
        db.add(Membership(user_id=user.id, org_id=org_id, role="viewer"))
        db.commit()
    return email, "viewer-password"


def test_viewer_is_read_only_but_can_export_approved(client):
    owner = register(client)
    run = create_demo_run(client)
    viewer_email, viewer_password = _add_viewer(owner["org"]["id"])

    login(client, viewer_email, viewer_password)
    assert client.get(f"/api/v1/runs/{run['id']}").status_code == 200
    denied = client.post(
        "/api/v1/projects", json={"name": "Nope", "description": "", "disease_pack": "breast"}
    )
    assert denied.status_code == 403
    assert client.post(f"/api/v1/runs/{run['id']}/retry").status_code == 403
    assert (
        client.post(f"/api/v1/runs/{run['id']}/report/approve", json={"confirm_ruo": True}).status_code
        == 403
    )

    login(client, owner["email"], owner["password"])
    client.post(f"/api/v1/runs/{run['id']}/report/approve", json={"confirm_ruo": True})

    login(client, viewer_email, viewer_password)
    assert client.get(f"/api/v1/runs/{run['id']}/report/export").status_code == 200


def _queued_copy(run_id: str) -> str:
    with SessionLocal() as db:
        original = db.get(Run, run_id)
        clone = Run(
            org_id=original.org_id,
            project_id=original.project_id,
            sample_id=original.sample_id,
            disease_pack=original.disease_pack,
            pack_version=original.pack_version,
            status="queued",
            stage="queued",
            params={"n_spots": 200, "lr_permutations": 9},
        )
        db.add(clone)
        db.commit()
        return clone.id


def test_cancelled_before_start_never_runs(client):
    register(client)
    run_id = _queued_copy(create_demo_run(client)["id"])
    assert client.post(f"/api/v1/runs/{run_id}/cancel").status_code == 200

    pipeline_service.execute_run(run_id)

    with SessionLocal() as db:
        run = db.get(Run, run_id)
        assert run.status == "cancelled"
        assert run.started_at is None
        assert db.scalar(select(Result).where(Result.run_id == run_id)) is None


def test_cancel_during_pipeline_is_not_overwritten(client, monkeypatch):
    register(client)
    run_id = _queued_copy(create_demo_run(client)["id"])
    real_pipeline = pipeline_service.run_pipeline

    def cancel_midway(*args, **kwargs):
        result = real_pipeline(*args, **kwargs)
        with SessionLocal() as db:  # the user presses Cancel while the worker is busy
            db.get(Run, run_id).status = "cancelled"
            db.commit()
        return result

    monkeypatch.setattr(pipeline_service, "run_pipeline", cancel_midway)
    pipeline_service.execute_run(run_id)

    with SessionLocal() as db:
        run = db.get(Run, run_id)
        assert run.status == "cancelled"
        assert run.stage == "cancelled"
        assert db.scalar(select(Result).where(Result.run_id == run_id)) is None
