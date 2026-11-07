from __future__ import annotations

from conftest import create_demo_run, register

from app.db import SessionLocal
from app.models import Run, Sample


def _compare(client, a: str, b: str):
    return client.get("/api/v1/runs/compare", params={"a": a, "b": b})


def _set_run(run_id: str, **values) -> None:
    with SessionLocal() as db:
        run = db.get(Run, run_id)
        for key, value in values.items():
            setattr(run, key, value)
        db.commit()


def _set_sample(sample_id: str, **values) -> None:
    with SessionLocal() as db:
        sample = db.get(Sample, sample_id)
        for key, value in values.items():
            setattr(sample, key, value)
        db.commit()


def test_compare_same_pack_side_by_side(client):
    register(client)
    run_a = create_demo_run(client)
    run_b = create_demo_run(client)

    response = _compare(client, run_a["id"], run_b["id"])
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["a"]["run_id"] == run_a["id"]
    assert data["b"]["run_id"] == run_b["id"]
    assert data["same_pack"] is True
    assert data["same_pack_version"] is True
    assert data["a"]["method_agreement"] > 0
    assert data["a"]["tested_interactions"] == 10
    assert data["a"]["significant_interactions"] == run_a["summary"]["significant_interactions"]
    assert any("MGMT" in item for item in data["a"]["not_assessed"])
    assert not any("different" in warning for warning in data["warnings"])
    assert any("synthetic demo data" in warning for warning in data["warnings"])

    # Same synthetic seed and params → identical stored results → zero deltas.
    cell_types = {row["cell_type"] for row in data["composition"]}
    assert cell_types == set(run_a["summary"]["composition_mean"])
    assert all(row["delta"] == 0 for row in data["composition"])
    assert data["domains"]
    assert all(row["delta_pct"] == 0 for row in data["domains"])
    assert abs(sum(row["a_pct"] for row in data["domains"]) - 100) < 0.5

    pairs = data["communication"]
    assert len(pairs) == 10
    assert all(pair["a"] and pair["b"] for pair in pairs)
    assert pairs[0]["a"]["q_value"] == pairs[0]["b"]["q_value"]


def test_compare_other_org_run_is_404(client):
    register(client)
    mine = create_demo_run(client)
    register(client)  # second org; cookie now belongs to it
    theirs = create_demo_run(client)

    assert _compare(client, mine["id"], theirs["id"]).status_code == 404
    assert _compare(client, theirs["id"], mine["id"]).status_code == 404
    assert _compare(client, theirs["id"], "no-such-run").status_code == 404


def test_compare_requires_succeeded_runs(client):
    register(client)
    done = create_demo_run(client)
    pending = create_demo_run(client)
    _set_run(pending["id"], status="queued", stage="queued")

    response = _compare(client, done["id"], pending["id"])
    assert response.status_code == 409
    assert "only succeeded runs" in response.json()["detail"]

    _set_run(pending["id"], status="failed")
    assert _compare(client, pending["id"], done["id"]).status_code == 409


def test_compare_rejects_same_run_and_missing_ids(client):
    register(client)
    run = create_demo_run(client)
    assert _compare(client, run["id"], run["id"]).status_code == 400
    assert client.get("/api/v1/runs/compare", params={"a": run["id"]}).status_code == 422


def test_compare_needs_login(client):
    client.cookies.clear()
    assert _compare(client, "x", "y").status_code == 401


def test_compare_warns_on_pack_mismatch(client):
    register(client)
    gbm = create_demo_run(client, pack="glioblastoma")
    breast = create_demo_run(client, pack="breast")

    data = _compare(client, gbm["id"], breast["id"]).json()
    assert data["same_pack"] is False
    assert any("different disease packs" in warning for warning in data["warnings"])

    composition = {row["cell_type"]: row for row in data["composition"]}
    assert composition["fibroblast"]["a"] is not None  # defined in both packs
    assert composition["fibroblast"]["b"] is not None
    assert composition["tumor"]["b"] is None  # GBM only
    assert composition["tumor"]["delta"] is None
    assert composition["luminal"]["a"] is None  # breast only
    assert data["composition"][-1]["delta"] is None  # one-sided rows sort last

    domains = {row["id"]: row for row in data["domains"]}
    assert domains["leading_edge"]["b_pct"] is None
    assert domains["leading_edge"]["delta_pct"] is None

    pairs = data["communication"]
    assert any(pair["a"] is None for pair in pairs)
    assert any(pair["b"] is None for pair in pairs)


def test_compare_warns_on_pack_version_mismatch(client):
    register(client)
    run_a = create_demo_run(client)
    run_b = create_demo_run(client)
    _set_run(run_b["id"], pack_version="0.1.0")

    data = _compare(client, run_a["id"], run_b["id"]).json()
    assert data["same_pack"] is True
    assert data["same_pack_version"] is False
    assert any("different versions" in warning for warning in data["warnings"])


def test_compare_surfaces_assay_species_and_condition_mismatches(client):
    register(client)
    run_a = create_demo_run(client)
    run_b = create_demo_run(client)
    _set_sample(run_b["sample"]["id"], platform="xenium", species="mouse", condition="treated")

    data = _compare(client, run_a["id"], run_b["id"]).json()

    assert data["a"]["platform"] == "visium"
    assert data["b"]["platform"] == "xenium"
    assert data["b"]["species"] == "mouse"
    assert any("different assay platforms" in warning for warning in data["warnings"])
    assert any("different species" in warning for warning in data["warnings"])
    assert any("different recorded conditions" in warning for warning in data["warnings"])
