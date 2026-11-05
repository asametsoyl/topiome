from __future__ import annotations

import numpy as np
import pandas as pd


def run_qc(
    expression: pd.DataFrame,
    *,
    min_counts: int = 200,
    min_genes: int = 100,
    max_mito_fraction: float = 0.30,
) -> dict:
    """Per-spot QC. Returns arrays and a JSON-safe summary."""
    values = expression.to_numpy(dtype=float)
    total_counts = values.sum(axis=1)
    n_genes = (values > 0).sum(axis=1)

    mito_mask = np.array([str(g).upper().startswith("MT-") for g in expression.columns])
    if mito_mask.any():
        mito_counts = values[:, mito_mask].sum(axis=1)
        mito_fraction = np.divide(
            mito_counts,
            total_counts,
            out=np.zeros_like(total_counts),
            where=total_counts > 0,
        )
    else:
        mito_fraction = np.zeros_like(total_counts)

    passed = (
        (total_counts >= min_counts)
        & (n_genes >= min_genes)
        & (mito_fraction <= max_mito_fraction)
    )

    warnings: list[str] = []
    if passed.sum() < 50:
        warnings.append(
            f"Only {int(passed.sum())} spots passed QC; results may be unstable."
        )
    if not mito_mask.any():
        warnings.append("No mitochondrial genes found; mito QC skipped.")

    return {
        "total_counts": total_counts.tolist(),
        "n_genes": n_genes.tolist(),
        "mito_fraction": np.round(mito_fraction, 5).tolist(),
        "passed": passed.tolist(),
        "summary": {
            "n_spots": int(len(total_counts)),
            "n_genes": int(expression.shape[1]),
            "passed_spots": int(passed.sum()),
            "failed_spots": int((~passed).sum()),
            "median_counts": float(np.median(total_counts)),
            "median_genes": float(np.median(n_genes)),
            "median_mito_fraction": float(np.median(mito_fraction)),
            "thresholds": {
                "min_counts": min_counts,
                "min_genes": min_genes,
                "max_mito_fraction": max_mito_fraction,
            },
        },
        "warnings": warnings,
    }


def normalize_counts(
    expression: pd.DataFrame,
    target_sum: float = 1e4,
    *,
    log: bool = True,
) -> pd.DataFrame:
    """Library-size normalization (CP10k), optionally followed by log1p.

    Deconvolution (NNLS) needs the linear scale; marker scores and target
    ranking use the log scale.
    """
    values = expression.to_numpy(dtype=float)
    totals = values.sum(axis=1)
    scale = np.divide(target_sum, totals, out=np.zeros_like(totals), where=totals > 0)
    normalized = values * scale[:, None]
    if log:
        normalized = np.log1p(normalized)
    return pd.DataFrame(normalized, index=expression.index, columns=expression.columns)
