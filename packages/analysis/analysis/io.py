from __future__ import annotations

import gzip
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io
import scipy.sparse as sp

from .types import SpatialDataset


def _open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt")
    return open(path)


def _read_features(path: Path) -> list[str]:
    genes: list[str] = []
    with _open_text(path) as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if not parts or not parts[0]:
                continue
            genes.append(parts[1] if len(parts) > 1 else parts[0])
    return genes


def _read_barcodes(path: Path) -> list[str]:
    with _open_text(path) as fh:
        return [line.strip() for line in fh if line.strip()]


def _find(base: Path, *names: str) -> Path | None:
    for name in names:
        candidate = base / name
        if candidate.exists():
            return candidate
        gz = base / f"{name}.gz"
        if gz.exists():
            return gz
    return None


def load_visium(directory: str | Path, sample_id: str = "sample") -> SpatialDataset:
    """Load a 10x Visium Space Ranger output directory.

    Required: matrix.mtx(.gz), barcodes.tsv(.gz), features.tsv(.gz),
    tissue_positions.csv (or tissue_positions_list.csv).
    """
    base = Path(directory)
    if not base.exists():
        raise FileNotFoundError(f"Visium directory not found: {base}")

    matrix_path = _find(base, "matrix.mtx")
    barcodes_path = _find(base, "barcodes.tsv")
    features_path = _find(base, "features.tsv", "genes.tsv")
    positions_path = _find(base, "tissue_positions.csv", "tissue_positions_list.csv")

    missing = [
        name
        for name, path in {
            "matrix.mtx": matrix_path,
            "barcodes.tsv": barcodes_path,
            "features.tsv": features_path,
            "tissue_positions.csv": positions_path,
        }.items()
        if path is None
    ]
    if missing:
        raise ValueError(f"Missing Visium files: {', '.join(missing)}")

    matrix = scipy.io.mmread(str(matrix_path))
    if sp.issparse(matrix):
        matrix = matrix.toarray()
    matrix = np.asarray(matrix)
    # Space Ranger matrix is genes × spots.
    if matrix.shape[0] != len(_read_features(features_path)):
        matrix = matrix.T

    genes = _read_features(features_path)
    barcodes = _read_barcodes(barcodes_path)

    if matrix.shape != (len(barcodes), len(genes)):
        raise ValueError(
            f"Matrix shape {matrix.shape} does not match barcodes ({len(barcodes)}) "
            f"and genes ({len(genes)})"
        )

    positions = pd.read_csv(positions_path)
    positions.columns = [str(c).strip() for c in positions.columns]
    if "barcode" not in positions.columns:
        # tissue_positions_list.csv has no header in older Space Ranger versions.
        positions = pd.read_csv(positions_path, header=None)
        if positions.shape[1] >= 6:
            positions.columns = [
                "barcode",
                "in_tissue",
                "array_row",
                "array_col",
                "pxl_row_in_fullres",
                "pxl_col_in_fullres",
            ][: positions.shape[1]]
        else:
            raise ValueError("Unrecognized tissue_positions format")

    positions = positions.set_index("barcode")
    common = [b for b in barcodes if b in positions.index]
    if len(common) < 50:
        raise ValueError("Fewer than 50 barcodes match tissue positions")

    idx = [barcodes.index(b) for b in common]
    expression = pd.DataFrame(matrix[idx, :], index=common, columns=genes)
    expression = expression.loc[:, ~expression.columns.duplicated(keep="first")]

    pos = positions.loc[common]
    if "pxl_col_in_fullres" in pos.columns and "pxl_row_in_fullres" in pos.columns:
        x = pd.to_numeric(pos["pxl_col_in_fullres"], errors="coerce").to_numpy()
        y = pd.to_numeric(pos["pxl_row_in_fullres"], errors="coerce").to_numpy()
    else:
        x = pd.to_numeric(pos["array_col"], errors="coerce").to_numpy()
        y = pd.to_numeric(pos["array_row"], errors="coerce").to_numpy()

    coords = np.column_stack([x, y]).astype(float)
    good = np.isfinite(coords).all(axis=1)
    expression = expression.iloc[good]
    coords = coords[good]
    kept = [b for b, ok in zip(common, good, strict=True) if ok]

    image = None
    for candidate in ("tissue_hires_image.png", "tissue_lowres_image.png"):
        if (base / candidate).exists():
            image = str(base / candidate)
            break

    return SpatialDataset(
        sample_id=sample_id,
        barcodes=kept,
        coordinates=coords,
        expression=expression,
        metadata={"platform": "visium", "source": str(base)},
        image_path=image,
    )
