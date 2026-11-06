from __future__ import annotations

import zipfile

import pytest
from conftest import register
from sqlalchemy import create_engine, inspect, text

from app.db import upgrade_db
from app.disease_packs import _cross_check, get_pack, list_packs
from app.services.pipeline import _extract_zip


def test_incomplete_visium_upload_is_rejected(client):
    register(client)
    project = client.post(
        "/api/v1/projects", json={"name": "Upload", "description": "", "disease_pack": "breast"}
    ).json()
    response = client.post(
        f"/api/v1/projects/{project['id']}/samples",
        data={"metadata": '{"name": "Partial"}'},
        files=[("files", ("barcodes.tsv", b"AAAC-1\n", "text/plain"))],
    )
    assert response.status_code == 400
    assert "Missing Visium files" in response.json()["detail"]


def test_zip_slip_entries_are_refused(tmp_path):
    archive = tmp_path / "evil.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../../escape.txt", "nope")
    with pytest.raises(ValueError, match="Unsafe zip entry"):
        _extract_zip(archive, tmp_path / "out")
    assert not (tmp_path.parent / "escape.txt").exists()


def test_packs_expose_ported_fields(client):
    summaries = {pack["id"]: pack for pack in list_packs()}
    assert len(summaries) == 6
    gbm = summaries["glioblastoma"]
    assert gbm["ligand_receptor_count"] == 10
    assert gbm["atlas_reference"]["license_status"] == "review_pending"
    assert "data" not in gbm["atlas_reference"]
    assert get_pack("glioblastoma")["atlas_reference"]["data"]["genes"]["VEGFA"]["ctpan"] > 0


def test_pack_cross_check_catches_unknown_cell_type():
    pack = {
        "cell_types": [{"id": "tumor"}],
        "zones": [{"id": "core"}],
        "ligand_receptor_pairs": [
            {"ligand": "A", "receptor": "B", "sender": "tumor", "receiver": "ghost"}
        ],
        "atlas_reference": {"zone_map": {"rim": "le"}},
    }
    problems = _cross_check(pack)
    assert any("ghost" in p for p in problems)
    assert any("rim" in p for p in problems)


def test_fresh_database_migrates_to_head(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fresh.db'}")
    upgrade_db(engine)
    with engine.connect() as conn:
        assert conn.execute(text("select version_num from alembic_version")).scalar() == "0002"
    columns = {c["name"] for c in inspect(engine).get_columns("reports")}
    assert {"status", "approved_by", "approved_at", "approval_note"} <= columns


def test_pre_alembic_database_is_stamped_then_upgraded(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    upgrade_db(engine)
    # Recreate the pre-Alembic situation: baseline tables, no version table, no new columns.
    with engine.begin() as conn:
        conn.execute(text("drop table alembic_version"))
        conn.execute(text("alter table runs drop column provenance"))
        for column in ("approval_note", "approved_at", "status"):
            conn.execute(text(f"alter table reports drop column {column}"))
    upgrade_db(engine)
    with engine.connect() as conn:
        assert conn.execute(text("select version_num from alembic_version")).scalar() == "0002"
    assert "provenance" in {c["name"] for c in inspect(engine).get_columns("runs")}


def test_breast_pack_ships_pinned_reference_and_model():
    from app.references import domain_model_for, reference_genes, signatures_for

    pack = get_pack("breast")
    signatures = signatures_for(pack)
    model = domain_model_for(pack)
    assert signatures.version == "wu2021-v1" and len(signatures.sha256) == 64
    assert set(signatures.table.index) <= {ct["id"] for ct in pack["cell_types"]}
    assert model.version == "1.0.0"
    assert set(model.classes) <= {zone["id"] for zone in pack["zones"]}
    assert sorted(model.genes) == sorted(signatures.table.columns)
    assert set(model.card["data"]["test_patients"]).isdisjoint(model.card["data"]["train_patients"])
    assert set(signatures.card["excluded_patients"]) == set(model.card["data"]["test_patients"])
    assert len(reference_genes(pack)) >= 400
    assert get_pack("glioblastoma").get("domain_model") is None
