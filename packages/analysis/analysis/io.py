"""Readers for 10x Visium (Space Ranger) outputs.

Real samples are large (≈4–5k spots × 36k genes), so the count matrix stays
sparse until genes are selected. QC statistics (library size, detected genes,
mitochondrial fraction) are computed on the full matrix first, so subsetting
genes never changes QC or library-size normalization.

Accepted layouts (searched recursively, GEO-style prefixes allowed):

* ``*filtered_feature_bc_matrix.h5`` (preferred) or ``matrix.mtx(.gz)`` with
  ``barcodes.tsv(.gz)`` and ``features.tsv(.gz)`` / ``genes.tsv(.gz)``
* ``tissue_positions.csv`` / ``tissue_positions_list.csv`` (often in ``spatial/``)
* optional ``scalefactors_json.json`` and ``tissue_*_image.png``
"""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io
import scipy.sparse as sp

from .types import SpatialDataset

POSITION_COLUMNS = [
    "barcode",
    "in_tissue",
    "array_row",
    "array_col",
    "pxl_row_in_fullres",
    "pxl_col_in_fullres",
]


@dataclass
class VisiumFiles:
    h5: Path | None = None
    matrix: Path | None = None
    barcodes: Path | None = None
    features: Path | None = None
    positions: Path | None = None
    scalefactors: Path | None = None
    image: Path | None = None
    platform: str = "visium"
    bin_size_um: int | None = None

    def missing(self) -> list[str]:
        problems = []
        if self.h5 is None and not (self.matrix and self.barcodes and self.features):
            problems.append(
                "count matrix (filtered_feature_bc_matrix.h5 or matrix.mtx + barcodes + features)"
            )
        if self.positions is None:
            problems.append("tissue_positions.csv or tissue_positions.parquet")
        return problems


def _files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file() and not p.name.startswith(("._", ".")))


def _prefer(paths: list[Path], *good: str, bad: tuple[str, ...] = ("raw",)) -> Path | None:
    if not paths:
        return None

    def rank(path: Path) -> tuple[int, int, int]:
        text = str(path).lower()
        return (
            sum(1 for word in bad if word in text),
            -sum(1 for word in good if word in text),
            len(text),
        )

    return sorted(paths, key=rank)[0]


def discover_visium(root: str | Path) -> VisiumFiles:
    base = Path(root)
    if not base.exists():
        raise FileNotFoundError(f"Visium directory not found: {base}")
    files = _files(base)
    names = [(p, p.name.lower()) for p in files]

    found = VisiumFiles()
    hd_bins = ["square_016um", "square_008um", "square_002um"]
    hd_h5 = [
        p
        for p, n in names
        if n.endswith(".h5") and "matrix" in n and any(b in str(p).lower() for b in hd_bins)
    ]
    if hd_h5:
        # The current analysis uses dense spots × genes tables downstream. Select
        # the coarsest native HD bin; 2/8 µm bins are too large for this pipeline.
        found.h5 = _prefer([p for p in hd_h5 if "square_016um" in str(p).lower()], "filtered")
        if found.h5 is None:
            raise ValueError(
                "Visium HD 2 µm/8 µm bins are not supported yet. Include the "
                "Space Ranger binned_outputs/square_016um output."
            )
        found.platform = "visium_hd"
        found.bin_size_um = 16
        positions = [
            p
            for p, n in names
            if "tissue_positions" in n
            and n.endswith(".parquet")
            and "square_016um" in str(p).lower()
        ]
        found.positions = _prefer(positions, "tissue_positions.parquet")
        # HD bins use parquet coordinates and do not need the Visium microscope image.
    else:
        found.h5 = _prefer([p for p, n in names if n.endswith(".h5") and "matrix" in n], "filtered")
    matrices = [p for p, n in names if n.endswith(("matrix.mtx", "matrix.mtx.gz"))]
    found.matrix = _prefer(matrices, "filtered")
    if found.matrix is not None:
        siblings = [
            (p, p.name.lower())
            for p in found.matrix.parent.iterdir()
            if p.is_file() and not p.name.startswith(("._", "."))
        ]

        def sidecar(candidates: list[Path]) -> Path | None:
            local = [path for path, _ in siblings if path in candidates]
            if local:
                return sorted(local)[0]
            # GEO can store a single shared barcode/features table beside its
            # per-sample folders. Use it only when unambiguous.
            return candidates[0] if len(candidates) == 1 else None

        shared = (
            [p for p in base.parent.iterdir() if p.is_file() and not p.name.startswith(("._", "."))]
            if base.parent != base
            else []
        )
        available = names + [(p, p.name.lower()) for p in shared if p not in {x for x, _ in names}]
        found.barcodes = sidecar(
            [p for p, n in available if "barcodes" in n and n.endswith((".tsv", ".tsv.gz"))]
        )
        found.features = sidecar(
            [
                p
                for p, n in available
                if ("features" in n or "genes" in n) and n.endswith((".tsv", ".tsv.gz"))
            ]
        )
    if found.platform == "visium":
        positions = [
            p for p, n in names if "tissue_positions" in n and n.endswith((".csv", ".csv.gz"))
        ]
        found.positions = _prefer(positions, "tissue_positions.csv", bad=("list",))
    found.scalefactors = next(
        (
            p
            for p, n in names
            if n.endswith(("scalefactors_json.json", "scalefactors_json.json.gz"))
        ),
        None,
    )
    found.image = _prefer(
        [
            p
            for p, n in names
            if n.endswith(
                (
                    "tissue_hires_image.png",
                    "tissue_hires_image.png.gz",
                    "tissue_lowres_image.png",
                    "tissue_lowres_image.png.gz",
                )
            )
        ],
        "hires",
    )
    return found


def _is_gzip(path: Path) -> bool:
    # Trust the bytes, not the extension: some public uploads are ".gz" but plain text.
    with open(path, "rb") as fh:
        return fh.read(2) == b"\x1f\x8b"


def _open_text(path: Path):
    if _is_gzip(path):
        return gzip.open(path, "rt")
    return open(path)


def _open_binary(path: Path):
    if _is_gzip(path):
        return gzip.open(path, "rb")
    return open(path, "rb")


def _read_lines(path: Path) -> list[list[str]]:
    with _open_text(path) as fh:
        return [line.rstrip("\n").split("\t") for line in fh if line.strip()]


def read_10x_mtx(
    matrix: Path, barcodes: Path, features: Path
) -> tuple[sp.csr_matrix, list[str], list[str]]:
    """Return (spots × genes CSR counts, barcodes, gene symbols)."""
    with _open_binary(matrix) as fh:
        counts = sp.csr_matrix(scipy.io.mmread(fh))
    feature_rows = _read_lines(features)
    barcode_list = [row[0] for row in _read_lines(barcodes)]
    if feature_rows and len(feature_rows[0]) >= 3:
        keep = [i for i, row in enumerate(feature_rows) if row[2] == "Gene Expression"]
    else:
        keep = list(range(len(feature_rows)))
    genes = [feature_rows[i][1] if len(feature_rows[i]) > 1 else feature_rows[i][0] for i in keep]
    if counts.shape[0] == len(feature_rows):  # Space Ranger stores genes × barcodes
        counts = counts.T.tocsr()
    if counts.shape != (len(barcode_list), len(feature_rows)):
        raise ValueError(
            f"Matrix shape {counts.shape} does not match barcodes ({len(barcode_list)}) "
            f"and features ({len(feature_rows)})"
        )
    return counts[:, keep].tocsr(), barcode_list, genes


def read_10x_h5(path: Path) -> tuple[sp.csr_matrix, list[str], list[str]]:
    """Read a Cell Ranger / Space Ranger HDF5 matrix (v3, with v2 fallback)."""
    import h5py

    def _decode(values) -> list[str]:  # noqa: ANN001
        return [v.decode() if isinstance(v, bytes) else str(v) for v in values]

    with h5py.File(path, "r") as handle:
        if "matrix" in handle:
            group = handle["matrix"]
            names = _decode(group["features"]["name"][:])
            types = (
                _decode(group["features"]["feature_type"][:])
                if "feature_type" in group["features"]
                else ["Gene Expression"] * len(names)
            )
        else:  # v2: one group per genome
            group = handle[next(iter(handle.keys()))]
            names = _decode(group["gene_names"][:])
            types = ["Gene Expression"] * len(names)
        shape = tuple(int(x) for x in group["shape"][:])
        counts = sp.csc_matrix(
            (group["data"][:], group["indices"][:], group["indptr"][:]), shape=shape
        )
        barcodes = _decode(group["barcodes"][:])
    keep = [i for i, kind in enumerate(types) if kind == "Gene Expression"]
    counts = counts.T.tocsr()[:, keep]  # genes × barcodes → barcodes × genes
    return counts, barcodes, [names[i] for i in keep]


def read_positions(path: Path) -> pd.DataFrame:
    """Tissue positions indexed by barcode (handles headered and legacy files)."""
    if path.suffix.lower() == ".parquet":
        try:
            positions = pd.read_parquet(path)
        except ImportError as exc:
            raise ValueError(
                "Reading Visium HD Parquet positions requires the pyarrow package"
            ) from exc
    else:
        positions = pd.read_csv(path)
    positions.columns = [str(c).strip() for c in positions.columns]
    if "barcode" not in positions.columns:
        positions = pd.read_csv(path, header=None)
        if positions.shape[1] < 6:
            raise ValueError("Unrecognized tissue_positions format")
        positions = positions.iloc[:, :6]
        positions.columns = POSITION_COLUMNS
    return positions.drop_duplicates("barcode").set_index("barcode")


def _qc_from_counts(counts: sp.csr_matrix, genes: list[str]) -> dict[str, np.ndarray | int]:
    total = np.asarray(counts.sum(axis=1)).ravel().astype(float)
    detected = np.asarray((counts > 0).sum(axis=1)).ravel().astype(float)
    mito_idx = [i for i, g in enumerate(genes) if g.upper().startswith("MT-")]
    if mito_idx:
        mito = np.asarray(counts[:, mito_idx].sum(axis=1)).ravel()
        mito_fraction = np.divide(mito, total, out=np.zeros_like(total), where=total > 0)
    else:
        mito_fraction = np.zeros_like(total)
    return {
        "total_counts": total,
        "n_genes": detected,
        "mito_fraction": mito_fraction,
        "n_genes_total": len(genes),
        "has_mito": bool(mito_idx),
    }


def _select_genes(
    counts: sp.csr_matrix,
    genes: list[str],
    *,
    keep_genes: set[str],
    max_genes: int,
) -> list[int]:
    """Indices of genes to materialise: requested genes + the most abundant ones."""
    totals = np.asarray(counts.sum(axis=0)).ravel()
    seen: set[str] = set()
    unique = []
    for i, gene in enumerate(genes):
        key = gene.upper()
        if key in seen or totals[i] <= 0:
            continue
        seen.add(key)
        unique.append(i)
    wanted = {g.upper() for g in keep_genes}
    forced = [i for i in unique if genes[i].upper() in wanted]
    forced_set = set(forced)
    rest = sorted((i for i in unique if i not in forced_set), key=lambda i: -totals[i])
    budget = max(max_genes - len(forced), 0)
    return sorted(forced + rest[:budget])


def load_visium(
    directory: str | Path,
    sample_id: str = "sample",
    *,
    keep_genes: set[str] | None = None,
    max_genes: int = 5000,
    max_spots: int = 12_000,
) -> SpatialDataset:
    """Load a 10x Visium sample from a Space Ranger output folder (or any folder
    containing its files). Only in-tissue spots are kept."""
    files = discover_visium(directory)
    missing = files.missing()
    if missing:
        raise ValueError(f"Missing Visium files: {', '.join(missing)}")

    # Preflight the tissue count before materialising a potentially large HD
    # matrix. HD Parquet coordinates are much smaller than the expression matrix.
    positions = read_positions(files.positions)
    if "in_tissue" in positions.columns:
        positions = positions[pd.to_numeric(positions["in_tissue"], errors="coerce") == 1]
    if len(positions) > max_spots:
        raise ValueError(
            f"This sample has at least {len(positions):,} in-tissue positions; the current "
            f"in-memory analysis limit is {max_spots:,}. Use a tissue crop or smaller sample. "
            "Visium HD is read from the 16 µm bin; tiled analysis for larger samples is not available yet."
        )

    if files.h5 is not None:
        counts, barcodes, genes = read_10x_h5(files.h5)
    else:
        counts, barcodes, genes = read_10x_mtx(files.matrix, files.barcodes, files.features)

    position_index = pd.Index(positions.index)
    barcode_index = pd.Index(barcodes)
    rows = barcode_index.get_indexer(position_index.intersection(barcode_index, sort=False))
    rows = np.sort(rows[rows >= 0])
    if len(rows) < 50:
        raise ValueError(
            f"Only {len(rows)} in-tissue barcodes match the count matrix (need at least 50)"
        )
    if len(rows) > max_spots:
        raise ValueError(
            f"This sample has {len(rows):,} in-tissue spots; the current in-memory analysis "
            f"limit is {max_spots:,}. Use a tissue crop or smaller sample. Visium HD is read "
            "from the 16 µm bin; tiled analysis for larger samples is not available yet."
        )
    kept_barcodes = [barcodes[i] for i in rows]
    counts = counts[rows]

    pos = positions.loc[kept_barcodes]
    if {"pxl_col_in_fullres", "pxl_row_in_fullres"} <= set(pos.columns):
        x = pd.to_numeric(pos["pxl_col_in_fullres"], errors="coerce").to_numpy(dtype=float)
        y = pd.to_numeric(pos["pxl_row_in_fullres"], errors="coerce").to_numpy(dtype=float)
    else:
        x = pd.to_numeric(pos["array_col"], errors="coerce").to_numpy(dtype=float)
        y = pd.to_numeric(pos["array_row"], errors="coerce").to_numpy(dtype=float)
    # Image rows grow downwards; flip so maps drawn with y-up match the H&E image.
    coords = np.column_stack([x, -y])
    good = np.isfinite(coords).all(axis=1)
    counts = counts[good]
    coords = coords[good]
    kept_barcodes = [b for b, ok in zip(kept_barcodes, good, strict=True) if ok]

    qc_stats = _qc_from_counts(counts, genes)
    selected = _select_genes(counts, genes, keep_genes=keep_genes or set(), max_genes=max_genes)
    dense = counts[:, selected].toarray().astype(np.float32)
    expression = pd.DataFrame(
        dense, index=kept_barcodes, columns=[genes[i].upper() for i in selected]
    )

    scalefactors = {}
    if files.scalefactors is not None:
        try:
            with _open_text(files.scalefactors) as handle:
                scalefactors = json.load(handle)
        except (OSError, ValueError):
            scalefactors = {}

    return SpatialDataset(
        sample_id=sample_id,
        barcodes=kept_barcodes,
        coordinates=coords,
        expression=expression,
        metadata={
            "platform": files.platform,
            "bin_size_um": files.bin_size_um,
            "source": str(Path(directory)),
            "matrix_format": "h5" if files.h5 is not None else "mtx",
            "genes_total": int(qc_stats["n_genes_total"]),
            "genes_loaded": int(expression.shape[1]),
            "coordinate_system": "fullres_pixels_y_up",
            "scalefactors": scalefactors,
        },
        image_path=str(files.image) if files.image else None,
        qc_stats={k: v for k, v in qc_stats.items()},
    )
