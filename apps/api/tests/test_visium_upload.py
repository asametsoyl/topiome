"""End-to-end real-data path: upload Space Ranger files → run → results."""

from __future__ import annotations

import base64
import io
import json
import tarfile

import h5py
import numpy as np
from conftest import register

from app.disease_packs import get_pack
from app.routers.samples import _has_visium_files


def _space_ranger_files(pack_id: str = "breast", n_spots: int = 160) -> tuple[bytes, bytes]:
    """A small but realistic Visium sample: h5 matrix + spatial/ folder as tar.gz."""
    pack = get_pack(pack_id)
    genes = sorted({g for ct in pack["cell_types"] for g in ct["markers"]})
    genes += [f"BG{i}" for i in range(200)] + ["MT-CO1", "MT-ND1"]
    rng = np.random.default_rng(3)
    counts = rng.poisson(2.0, size=(len(genes), n_spots)).astype(np.int32)  # genes × spots
    barcodes = [f"AAAC{i:05d}-1" for i in range(n_spots)]

    h5 = io.BytesIO()
    with h5py.File(h5, "w") as handle:
        group = handle.create_group("matrix")
        from scipy import sparse

        csc = sparse.csc_matrix(counts)
        group["data"], group["indices"], group["indptr"] = csc.data, csc.indices, csc.indptr
        group["shape"] = np.array(csc.shape)
        group["barcodes"] = np.array(barcodes, dtype="S")
        features = group.create_group("features")
        features["name"] = np.array(genes, dtype="S")
        features["id"] = np.array([f"ENSG{i}" for i in range(len(genes))], dtype="S")
        features["feature_type"] = np.array(["Gene Expression"] * len(genes), dtype="S")

    positions = "\n".join(
        f"{b},1,{i // 16},{i % 16},{100 + 20 * (i // 16)},{100 + 20 * (i % 16)}"
        for i, b in enumerate(barcodes)
    ).encode()
    spatial = io.BytesIO()
    with tarfile.open(fileobj=spatial, mode="w:gz") as archive:
        for name, payload in (
            ("spatial/tissue_positions_list.csv", positions),
            (
                "spatial/scalefactors_json.json",
                b'{"spot_diameter_fullres": 89.4, "tissue_hires_scalef": 0.15}',
            ),
            (
                "spatial/tissue_hires_image.png",
                base64.b64decode(
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aSZsAAAAASUVORK5CYII="
                ),
            ),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
    return h5.getvalue(), spatial.getvalue()


def test_upload_validation_accepts_visium_hd_parquet_positions():
    valid, missing = _has_visium_files(
        ["filtered_feature_bc_matrix.h5", "tissue_positions.parquet"]
    )
    assert valid is True
    assert missing == []


def test_uploaded_visium_sample_runs_end_to_end(client):
    register(client)
    project = client.post(
        "/api/v1/projects", json={"name": "Real path", "description": "", "disease_pack": "breast"}
    ).json()
    h5, spatial = _space_ranger_files()
    sample = client.post(
        f"/api/v1/projects/{project['id']}/samples",
        data={"metadata": json.dumps({"name": "Uploaded section"})},
        files=[
            ("files", ("filtered_feature_bc_matrix.h5", h5, "application/octet-stream")),
            ("files", ("spatial.tar.gz", spatial, "application/gzip")),
        ],
    )
    assert sample.status_code == 201, sample.text
    assert sample.json()["status"] == "uploaded"

    tissue = client.get(f"/api/v1/samples/{sample.json()['id']}/spatial-image")
    assert tissue.status_code == 200, tissue.text
    assert tissue.headers["content-type"] == "image/png"
    assert tissue.headers["x-visium-hires-scale"] == "0.15"
    assert tissue.content.startswith(b"\x89PNG\r\n\x1a\n")

    run = client.post(
        f"/api/v1/samples/{sample.json()['id']}/runs", json={"params": {"lr_permutations": 9}}
    ).json()
    detail = client.get(f"/api/v1/runs/{run['id']}").json()
    assert detail["status"] == "succeeded", detail.get("error_message")

    provenance = detail["provenance"]
    assert provenance["input"]["kind"] == "visium"
    assert {f["filename"] for f in provenance["input"]["files"]} == {
        "filtered_feature_bc_matrix.h5",
        "spatial.tar.gz",
    }
    assert all(len(f["sha256"]) == 64 for f in provenance["input"]["files"])
    # Real samples use the pack's shipped scRNA signatures, pinned by hash.
    assert provenance["reference"]["signatures"]["version"] == "wu2021-v1"
    assert len(provenance["reference"]["signatures"]["sha256"]) == 64

    assert provenance["domain_model"]["version"] == "1.0.0"
    assert len(provenance["domain_model"]["sha256"]) == 64

    payload = client.get(f"/api/v1/runs/{run['id']}/results").json()["payload"]
    assert payload["summary"]["method"] == "nnls"
    assert payload["summary"]["synthetic"] is False
    assert payload["summary"]["n_spots"] == 160
    # This toy sample lacks most of the model's 408-gene panel, so the GNN must
    # step aside (with the reason recorded) instead of guessing.
    domain_model = payload["validation"]["domain_model"]
    assert domain_model["applied"] is False
    assert "genes were measured" in domain_model["reason"]
    assert payload["summary"]["domain_method"] == "kmeans_markers"
    assert domain_model["test_metrics"]["gnn"]["pooled"]["macro_f1"] > 0

    expression = client.get(f"/api/v1/runs/{run['id']}/expression", params={"gene": "BG0"})
    assert expression.status_code == 200, expression.text
    assert expression.json()["gene"] == "BG0"
    assert expression.json()["scale"] == "log1p(CP10K)"
    assert len(expression.json()["values"]) == 160

    qc_barcodes = [spot["barcode"] for spot in payload["spots"] if spot["qc_pass"]]
    assert len(qc_barcodes) >= 20
    roi = client.post(
        f"/api/v1/runs/{run['id']}/roi-genes", json={"barcodes": qc_barcodes[:10]}
    )
    assert roi.status_code == 200, roi.text
    roi_data = roi.json()
    assert roi_data["n_roi_qc_pass"] == 10
    assert roi_data["n_background_qc_pass"] == len(qc_barcodes) - 10
    assert roi_data["method"] == "descriptive_mean_difference"
    assert roi_data["genes"]
    assert all("p_value" not in item for item in roi_data["genes"])
    assert "no inferential test" in roi_data["note"]


def test_incomplete_archive_fails_the_run_with_a_clear_message(client):
    register(client)
    project = client.post(
        "/api/v1/projects", json={"name": "Broken", "description": "", "disease_pack": "breast"}
    ).json()
    _, spatial = _space_ranger_files()
    sample = client.post(
        f"/api/v1/projects/{project['id']}/samples",
        data={"metadata": json.dumps({"name": "Only spatial"})},
        files=[("files", ("spatial.tar.gz", spatial, "application/gzip"))],
    ).json()
    run = client.post(f"/api/v1/samples/{sample['id']}/runs", json={"params": {}}).json()
    detail = client.get(f"/api/v1/runs/{run['id']}").json()
    assert detail["status"] == "failed"
    assert detail["error_code"] == "invalid_input"
    assert "count matrix" in detail["error_message"]
