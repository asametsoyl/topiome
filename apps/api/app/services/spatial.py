from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from analysis.io import discover_visium, read_10x_h5, read_10x_mtx, read_positions


def roi_expression_differences(
    directory: Path,
    *,
    roi_barcodes: set[str],
    qc_pass_barcodes: set[str],
    top_n: int = 30,
) -> dict:
    """Descriptive ROI-vs-background expression deltas; deliberately no p-values."""
    files = discover_visium(directory)
    missing = files.missing()
    if missing:
        raise ValueError("Missing Visium files: " + ", ".join(missing))
    if files.h5 is not None:
        counts, barcodes, genes = read_10x_h5(files.h5)
    else:
        counts, barcodes, genes = read_10x_mtx(files.matrix, files.barcodes, files.features)

    positions = read_positions(files.positions)
    if "in_tissue" in positions.columns:
        positions = positions[pd.to_numeric(positions["in_tissue"], errors="coerce") == 1]
    matrix_rows = {barcode: index for index, barcode in enumerate(barcodes)}
    tissue_barcodes = [barcode for barcode in positions.index if barcode in matrix_rows]
    rows = np.asarray([matrix_rows[barcode] for barcode in tissue_barcodes], dtype=int)
    tissue_counts = sp.csr_matrix(counts[rows])
    qc_mask = np.asarray([barcode in qc_pass_barcodes for barcode in tissue_barcodes])
    roi_mask = np.asarray([barcode in roi_barcodes for barcode in tissue_barcodes]) & qc_mask
    background_mask = ~np.asarray([barcode in roi_barcodes for barcode in tissue_barcodes]) & qc_mask
    n_roi = int(roi_mask.sum())
    n_background = int(background_mask.sum())
    if n_roi < 10 or n_background < 10:
        raise ValueError("ROI analysis needs at least 10 QC-pass spots inside and outside the selected region")

    totals = np.asarray(tissue_counts.sum(axis=1)).ravel().astype(np.float64)
    factors = np.divide(10_000.0, totals, out=np.zeros_like(totals), where=totals > 0)
    normalized = tissue_counts.multiply(factors[:, None]).tocsr()
    normalized.data = np.log1p(normalized.data)

    roi_counts = tissue_counts[roi_mask]
    background_counts = tissue_counts[background_mask]
    roi_mean = np.asarray(normalized[roi_mask].sum(axis=0)).ravel() / n_roi
    background_mean = np.asarray(normalized[background_mask].sum(axis=0)).ravel() / n_background
    roi_detected = np.asarray((roi_counts > 0).sum(axis=0)).ravel() / n_roi
    background_detected = np.asarray((background_counts > 0).sum(axis=0)).ravel() / n_background
    delta = roi_mean - background_mean
    order = np.argsort(-np.abs(delta), kind="stable")[:top_n]
    rows_out = [
        {
            "gene": genes[index],
            "delta_mean_log1p_cp10k": round(float(delta[index]), 5),
            "roi_detected_fraction": round(float(roi_detected[index]), 5),
            "background_detected_fraction": round(float(background_detected[index]), 5),
            "direction": "higher_in_roi" if delta[index] > 0 else "higher_outside_roi" if delta[index] < 0 else "equal",
        }
        for index in order
    ]
    return {
        "n_roi_qc_pass": n_roi,
        "n_background_qc_pass": n_background,
        "normalization": "log1p(CP10K)",
        "method": "descriptive_mean_difference",
        "genes": rows_out,
        "note": "Descriptive spot-level contrast only; no inferential test is applied. Spatially adjacent spots are not independent biological replicates.",
    }
