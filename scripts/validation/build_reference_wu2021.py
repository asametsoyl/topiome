"""Build breast scRNA reference signatures from Wu et al. 2021 (GSE176078).

Step 1 streams the ~100k-cell count matrix once and stores per (patient,
cell type) sums of CP10k expression and detection counts, so references for
any patient subset can be built without reloading the matrix.

Step 2 writes the shipped reference, built only from non-test patients:
``packages/disease-packs/references/breast_wu2021_signatures_v1.csv.gz`` + JSON.

Usage (from apps/api):  uv run python -I ../../scripts/validation/build_reference_wu2021.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import tarfile
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wu2021_common import (  # noqa: E402
    GROUP_SUMS,
    PACKS,
    REFERENCE_TYPES,
    SCRNA_DIR,
    TEST_PATIENTS,
    marker_panel,
    pack_type,
    reference_from_sums,
)

ARCHIVE = SCRNA_DIR / "GSE176078_Wu_etal_2021_BRCA_scRNASeq.tar.gz"
VERSION = "wu2021-v1"


def extract() -> Path:
    target = SCRNA_DIR / "extracted"
    if not target.exists():
        with tarfile.open(ARCHIVE) as archive:
            archive.extractall(target, filter="data")
    matrices = [p for p in target.rglob("*.mtx") if not p.name.startswith("._")]
    if not matrices:
        raise SystemExit("count matrix not found in archive")
    return matrices[0].parent


def _file(folder: Path, word: str, suffix: str) -> Path:
    """The data file whose name contains ``word`` (skips macOS ``._`` files)."""
    for path in sorted(folder.iterdir()):
        if not path.name.startswith(".") and word in path.name and path.name.endswith(suffix):
            return path
    raise SystemExit(f"no *{word}*{suffix} in {folder}")


def stream_group_sums(folder: Path) -> None:
    meta = pd.read_csv(_file(folder, "metadata", ".csv"), index_col=0)
    genes = pd.read_csv(_file(folder, "genes", ".tsv"), header=None)[0].astype(str).tolist()
    barcodes = pd.read_csv(_file(folder, "barcodes", ".tsv"), header=None)[0].astype(str).tolist()
    meta = meta.reindex(barcodes)
    patient_col = "orig.ident" if "orig.ident" in meta.columns else "patient"
    labels = [
        pack_type(str(major), str(minor))
        for major, minor in zip(meta["celltype_major"], meta["celltype_minor"], strict=True)
    ]
    groups = sorted({(str(p), t) for p, t in zip(meta[patient_col], labels, strict=True) if t})
    group_index = {g: i for i, g in enumerate(groups)}
    cell_group = np.array(
        [
            group_index.get((str(p), t), -1) if t else -1
            for p, t in zip(meta[patient_col], labels, strict=True)
        ],
        dtype=np.int64,
    )
    totals_meta = meta["nCount_RNA"].to_numpy(dtype=np.float64)
    n_genes, n_groups = len(genes), len(groups)
    sums = np.zeros(n_groups * n_genes, dtype=np.float64)
    detected = np.zeros(n_groups * n_genes, dtype=np.float64)
    totals_seen = np.zeros(len(barcodes), dtype=np.float64)

    matrix = _file(folder, "matrix", ".mtx")
    header_lines = 0
    with open(matrix) as fh:
        line = fh.readline()
        header_lines += 1
        while line.startswith("%"):
            line = fh.readline()
            header_lines += 1
        rows, cols, nnz = (int(x) for x in line.split())
    genes_are_rows = rows == n_genes
    print(f"matrix {rows}×{cols}, {nnz:,} entries; {n_groups} (patient, type) groups")

    started = time.perf_counter()
    reader = pd.read_csv(
        matrix,
        sep=" ",
        header=None,
        skiprows=header_lines,  # comment lines + the "rows cols nnz" size line
        names=["r", "c", "v"],
        dtype={"r": np.int64, "c": np.int64, "v": np.float64},
        chunksize=10_000_000,
    )
    done = 0
    for chunk in reader:
        r = chunk["r"].to_numpy() - 1
        c = chunk["c"].to_numpy() - 1
        v = chunk["v"].to_numpy()
        gene, cell = (r, c) if genes_are_rows else (c, r)
        totals_seen += np.bincount(cell, weights=v, minlength=len(barcodes))
        group = cell_group[cell]
        ok = group >= 0
        flat = group[ok] * n_genes + gene[ok]
        sums += np.bincount(flat, weights=v[ok] / totals_meta[cell[ok]] * 1e4, minlength=sums.size)
        detected += np.bincount(flat, minlength=sums.size)
        done += len(chunk)
        print(f"  {done / nnz:6.1%}  {time.perf_counter() - started:5.0f}s", flush=True)

    mismatch = np.nanmax(np.abs(totals_seen - totals_meta) / np.maximum(totals_meta, 1))
    print(f"max relative difference between matrix totals and nCount_RNA: {mismatch:.2e}")
    if done != nnz or mismatch > 1e-6:
        raise SystemExit(f"matrix read inconsistently: {done:,} of {nnz:,} entries, mismatch {mismatch:.2e}")
    n_cells = np.bincount(cell_group[cell_group >= 0], minlength=n_groups)
    GROUP_SUMS.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        GROUP_SUMS,
        genes=np.array(genes),
        group_patient=np.array([g[0] for g in groups]),
        group_type=np.array([g[1] for g in groups]),
        n_cells=n_cells,
        cp10k_sums=sums.reshape(n_groups, n_genes),
        detected=detected.reshape(n_groups, n_genes),
        library_mismatch=np.array(mismatch),
    )


def write_shipped_reference() -> None:
    means, detection, cells = reference_from_sums(exclude_patients=TEST_PATIENTS)
    pack = __import__("yaml").safe_load((PACKS / "breast.yaml").read_text())
    # Must match train_domain_gnn.fold_reference exactly (cell-type + zone markers),
    # so the shipped signatures produce the same features the model was trained on.
    pack_markers = {
        g.upper() for group in ("cell_types", "zones") for item in pack[group] for g in item["markers"]
    }
    panel = marker_panel(means, detection)
    genes = [g for g in dict.fromkeys(panel + sorted(pack_markers)) if g in set(means.columns.str.upper())]
    upper = {c.upper(): c for c in means.columns}
    table = means[[upper[g] for g in genes]]
    table.columns = genes
    table = table.loc[[t for t in REFERENCE_TYPES if t in table.index]]

    out_csv = PACKS / "references" / f"breast_{VERSION.replace('-', '_')}_signatures.csv.gz"
    table.to_csv(out_csv, float_format="%.6g", compression={"method": "gzip", "mtime": 0})
    data = np.load(GROUP_SUMS)
    card = {
        "version": VERSION,
        "kind": "scrna_signatures",
        "created": datetime.now(UTC).strftime("%Y-%m-%d"),
        "source": "Wu SZ et al. A single-cell and spatially resolved atlas of human breast cancers. "
        "Nat Genet 2021;53:1334-1347. GEO GSE176078.",
        "license": "Public GEO data; cite the publication.",
        "excluded_patients": TEST_PATIENTS,
        "excluded_reason": "Held out for spatial validation (see docs/validation).",
        "cells_per_type": cells,
        "n_genes": len(genes),
        "values": "Mean fraction of transcripts per cell type (CP10k / 1e4), equal-weighted cells.",
        "cell_type_mapping": "scripts/validation/wu2021_common.py (MAJOR_TO_PACK, NORMAL_EPITHELIAL_MINOR)",
        "library_size_check": float(data["library_mismatch"]),
        "sha256": hashlib.sha256(out_csv.read_bytes()).hexdigest(),
    }
    out_csv.with_suffix("").with_suffix(".json").write_text(json.dumps(card, indent=2) + "\n")
    print(f"wrote {out_csv.name}: {table.shape[0]} cell types × {table.shape[1]} genes")
    print(json.dumps(cells, indent=2))


if __name__ == "__main__":
    if not GROUP_SUMS.exists():
        stream_group_sums(extract())
    write_shipped_reference()
