"""Space Ranger readers: h5 and mtx layouts, nested folders, QC on the full matrix."""

from __future__ import annotations

import gzip
import shutil
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import pytest
import scipy.io
import scipy.sparse as sp

from analysis.io import discover_visium, load_visium

N_SPOTS, N_GENES = 120, 300


def _counts(seed: int = 0) -> tuple[sp.csr_matrix, list[str], list[str]]:
    rng = np.random.default_rng(seed)
    dense = rng.poisson(0.6, size=(N_SPOTS, N_GENES)).astype(np.int32)
    genes = [f"GENE{i}" for i in range(N_GENES - 3)] + ["MT-CO1", "MT-ND1", "RAREMARKER"]
    dense[:, -1] = 0
    dense[:3, -1] = 1  # a rare but requested gene
    dense[:, -3:-1] += 5  # mitochondrial reads
    barcodes = [f"AAAC{i:05d}-1" for i in range(N_SPOTS)]
    return sp.csr_matrix(dense), barcodes, genes


def _write_positions(path: Path, barcodes: list[str], header: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if header:
        lines.append("barcode,in_tissue,array_row,array_col,pxl_row_in_fullres,pxl_col_in_fullres")
    for i, barcode in enumerate(barcodes + ["OFFTISSUE-1"]):
        in_tissue = 0 if barcode.startswith("OFF") or i >= N_SPOTS - 10 else 1
        lines.append(
            f"{barcode},{in_tissue},{i // 12},{i % 12},{100 + 10 * (i // 12)},{200 + 10 * (i % 12)}"
        )
    path.write_text("\n".join(lines) + "\n")


def _write_h5(path: Path, counts: sp.csr_matrix, barcodes: list[str], genes: list[str]) -> None:
    csc = counts.T.tocsc()  # genes × barcodes, CSC over barcodes like Space Ranger
    with h5py.File(path, "w") as handle:
        group = handle.create_group("matrix")
        group["data"] = csc.data
        group["indices"] = csc.indices
        group["indptr"] = csc.indptr
        group["shape"] = np.array(csc.shape)
        group["barcodes"] = np.array(barcodes, dtype="S")
        features = group.create_group("features")
        features["name"] = np.array(genes, dtype="S")
        features["id"] = np.array([f"ENSG{i:05d}" for i in range(len(genes))], dtype="S")
        features["feature_type"] = np.array(["Gene Expression"] * len(genes), dtype="S")


@pytest.fixture()
def h5_sample(tmp_path: Path) -> Path:
    counts, barcodes, genes = _counts()
    root = tmp_path / "GSM0001"
    root.mkdir()
    _write_h5(root / "GSM0001_filtered_feature_bc_matrix_visium.h5", counts, barcodes, genes)
    _write_positions(root / "spatial" / "tissue_positions.csv", barcodes)
    return root


@pytest.fixture()
def mtx_sample(tmp_path: Path) -> Path:
    counts, barcodes, genes = _counts()
    root = tmp_path / "outs"
    matrix_dir = root / "filtered_feature_bc_matrix"
    matrix_dir.mkdir(parents=True)
    scipy.io.mmwrite(str(matrix_dir / "matrix.mtx"), counts.T.tocoo())
    with gzip.open(matrix_dir / "barcodes.tsv.gz", "wt") as fh:
        fh.write("\n".join(barcodes) + "\n")
    with gzip.open(matrix_dir / "features.tsv.gz", "wt") as fh:
        fh.write(
            "\n".join(f"ENSG{i:05d}\t{g}\tGene Expression" for i, g in enumerate(genes)) + "\n"
        )
    _write_positions(root / "spatial" / "tissue_positions_list.csv", barcodes, header=False)
    (root / "._matrix.mtx").write_bytes(b"\x00\x05AppleDouble")  # exFAT junk must be ignored
    return root


def test_discovery_finds_nested_files(h5_sample: Path):
    files = discover_visium(h5_sample)
    assert files.h5 is not None and files.positions is not None
    assert files.missing() == []


def test_discovery_ignores_exfat_barcode_and_feature_sidecars(mtx_sample: Path):
    matrix_dir = mtx_sample / "filtered_feature_bc_matrix"
    (matrix_dir / "._barcodes.tsv.gz").write_bytes(b"AppleDouble, not a barcode table")
    (matrix_dir / "._features.tsv.gz").write_bytes(b"AppleDouble, not a feature table")

    files = discover_visium(mtx_sample)

    assert files.barcodes is not None and files.barcodes.name == "barcodes.tsv.gz"
    assert files.features is not None and files.features.name == "features.tsv.gz"


def test_discovery_uses_unique_series_level_mtx_sidecars(mtx_sample: Path):
    matrix_dir = mtx_sample / "filtered_feature_bc_matrix"
    shutil.move(matrix_dir / "barcodes.tsv.gz", mtx_sample.parent / "barcodes.tsv.gz")
    shutil.move(matrix_dir / "features.tsv.gz", mtx_sample.parent / "features.tsv.gz")

    files = discover_visium(mtx_sample)
    dataset = load_visium(mtx_sample, max_genes=20)

    assert files.barcodes == mtx_sample.parent / "barcodes.tsv.gz"
    assert files.features == mtx_sample.parent / "features.tsv.gz"
    assert len(dataset.barcodes) == N_SPOTS - 10


def test_visium_hd_selects_16um_h5_and_parquet_positions(tmp_path: Path):
    counts, barcodes, genes = _counts()
    hd = tmp_path / "binned_outputs" / "square_016um"
    hd.mkdir(parents=True)
    _write_h5(hd / "filtered_feature_bc_matrix.h5", counts, barcodes, genes)
    positions = hd / "spatial" / "tissue_positions.parquet"
    positions.parent.mkdir(parents=True)
    pd.DataFrame(
        {
            "barcode": barcodes,
            "in_tissue": [0 if i >= N_SPOTS - 10 else 1 for i in range(N_SPOTS)],
            "array_row": [i // 12 for i in range(N_SPOTS)],
            "array_col": [i % 12 for i in range(N_SPOTS)],
            "pxl_row_in_fullres": [100 + 10 * (i // 12) for i in range(N_SPOTS)],
            "pxl_col_in_fullres": [200 + 10 * (i % 12) for i in range(N_SPOTS)],
        }
    ).to_parquet(positions, index=False)

    files = discover_visium(tmp_path)
    dataset = load_visium(tmp_path, max_genes=50)
    assert files.h5 == hd / "filtered_feature_bc_matrix.h5"
    assert files.positions == positions
    assert dataset.metadata["platform"] == "visium_hd"
    assert dataset.metadata["bin_size_um"] == 16
    assert len(dataset.barcodes) == N_SPOTS - 10


def test_visium_hd_rejects_unsupported_finer_bins(tmp_path: Path):
    hd = tmp_path / "binned_outputs" / "square_008um"
    hd.mkdir(parents=True)
    (hd / "filtered_feature_bc_matrix.h5").touch()
    with pytest.raises(ValueError, match="square_016um"):
        discover_visium(tmp_path)


def test_loader_enforces_in_memory_spot_limit(h5_sample: Path):
    with pytest.raises(ValueError, match="in-memory analysis limit"):
        load_visium(h5_sample, max_spots=100)


def test_h5_and_mtx_layouts_load_identically(h5_sample: Path, mtx_sample: Path):
    from_h5 = load_visium(h5_sample, max_genes=50)
    from_mtx = load_visium(mtx_sample, max_genes=50)
    assert from_h5.expression.shape == from_mtx.expression.shape
    assert np.allclose(from_h5.expression.to_numpy(), from_mtx.expression.to_numpy())
    assert from_h5.metadata["matrix_format"] == "h5"
    assert from_mtx.metadata["matrix_format"] == "mtx"


def test_only_in_tissue_spots_are_kept(h5_sample: Path):
    dataset = load_visium(h5_sample)
    assert len(dataset.barcodes) == N_SPOTS - 10
    assert "OFFTISSUE-1" not in dataset.barcodes


def test_qc_uses_full_matrix_and_requested_genes_survive(h5_sample: Path):
    dataset = load_visium(h5_sample, keep_genes={"raremarker"}, max_genes=20)
    assert dataset.expression.shape[1] <= 20
    assert "RAREMARKER" in dataset.expression.columns
    # Library size is computed before gene selection, so it exceeds the loaded subset.
    loaded = dataset.expression.to_numpy().sum(axis=1)
    assert np.all(dataset.qc_stats["total_counts"] >= loaded)
    assert dataset.qc_stats["has_mito"] is True
    assert dataset.qc_stats["n_genes_total"] == N_GENES
    assert dataset.metadata["genes_total"] == N_GENES


def test_coordinates_are_flipped_to_y_up(h5_sample: Path):
    dataset = load_visium(h5_sample)
    first, later = dataset.coordinates[0], dataset.coordinates[-1]
    assert later[1] < first[1]  # higher image row → lower y


def test_incomplete_folder_reports_what_is_missing(tmp_path: Path):
    counts, barcodes, genes = _counts()
    _write_h5(tmp_path / "filtered_feature_bc_matrix.h5", counts, barcodes, genes)
    with pytest.raises(ValueError, match="tissue_positions"):
        load_visium(tmp_path)
