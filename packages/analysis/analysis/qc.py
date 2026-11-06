from __future__ import annotations

import numpy as np
import pandas as pd


def run_qc(
    expression: pd.DataFrame,
    *,
    min_counts: int = 200,
    min_genes: int = 100,
    max_mito_fraction: float = 0.30,
    precomputed: dict | None = None,
    adaptive_mito: bool = True,
    mito_ceiling: float = 0.60,
) -> dict:
    """Per-spot QC. Returns arrays and a JSON-safe summary.

    ``precomputed`` holds stats from the full count matrix (see ``io.load_visium``);
    when given, QC does not depend on which genes were loaded.
    """
    if precomputed is not None:
        total_counts = np.asarray(precomputed["total_counts"], dtype=float)
        n_genes = np.asarray(precomputed["n_genes"], dtype=float)
        mito_fraction = np.asarray(precomputed["mito_fraction"], dtype=float)
        has_mito = bool(precomputed.get("has_mito", True))
        genes_measured = int(precomputed.get("n_genes_total", expression.shape[1]))
    else:
        values = expression.to_numpy(dtype=float)
        total_counts = values.sum(axis=1)
        n_genes = (values > 0).sum(axis=1)
        mito_mask = np.array([str(g).upper().startswith("MT-") for g in expression.columns])
        has_mito = bool(mito_mask.any())
        genes_measured = int(expression.shape[1])
        if has_mito:
            mito_counts = values[:, mito_mask].sum(axis=1)
            mito_fraction = np.divide(
                mito_counts,
                total_counts,
                out=np.zeros_like(total_counts),
                where=total_counts > 0,
            )
        else:
            mito_fraction = np.zeros_like(total_counts)

    # Some tissues (e.g. glioblastoma) carry a high mitochondrial fraction everywhere.
    # A fixed cut-off would then drop healthy spots, so the limit adapts to the
    # sample (median + 3 MAD) but never falls below the default or exceeds the ceiling.
    warnings: list[str] = []
    mito_cutoff = float(max_mito_fraction)
    mito_rule = "fixed"
    if adaptive_mito and has_mito and len(mito_fraction):
        median = float(np.median(mito_fraction))
        mad = float(np.median(np.abs(mito_fraction - median))) * 1.4826
        adaptive = min(max(median + 3 * mad, max_mito_fraction), mito_ceiling)
        if adaptive > max_mito_fraction:
            mito_cutoff, mito_rule = adaptive, "adaptive (median + 3 MAD)"
            warnings.append(
                f"High mitochondrial fraction across the sample (median {median:.0%}); "
                f"QC used an adaptive cut-off of {mito_cutoff:.0%}."
            )

    passed = (
        (total_counts >= min_counts)
        & (n_genes >= min_genes)
        & (mito_fraction <= mito_cutoff)
    )

    if passed.sum() < 50:
        warnings.append(
            f"Only {int(passed.sum())} spots passed QC; results may be unstable."
        )
    if not has_mito:
        warnings.append("No mitochondrial genes found; mito QC skipped.")

    return {
        "total_counts": total_counts.tolist(),
        "n_genes": n_genes.tolist(),
        "mito_fraction": np.round(mito_fraction, 5).tolist(),
        "passed": passed.tolist(),
        "summary": {
            "n_spots": int(len(total_counts)),
            "n_genes": genes_measured,
            "passed_spots": int(passed.sum()),
            "failed_spots": int((~passed).sum()),
            "median_counts": float(np.median(total_counts)),
            "median_genes": float(np.median(n_genes)),
            "median_mito_fraction": float(np.median(mito_fraction)),
            "thresholds": {
                "min_counts": min_counts,
                "min_genes": min_genes,
                "max_mito_fraction": round(mito_cutoff, 4),
                "mito_rule": mito_rule,
            },
        },
        "warnings": warnings,
    }


def normalize_counts(
    expression: pd.DataFrame,
    target_sum: float = 1e4,
    *,
    log: bool = True,
    totals: np.ndarray | None = None,
) -> pd.DataFrame:
    """Library-size normalization (CP10k), optionally followed by log1p.

    Deconvolution (NNLS) needs the linear scale; marker scores and target
    ranking use the log scale. ``totals`` are the true library sizes when only
    a subset of genes was loaded.
    """
    values = expression.to_numpy(dtype=float)
    if totals is None:
        totals = values.sum(axis=1)
    totals = np.asarray(totals, dtype=float)
    scale = np.divide(target_sum, totals, out=np.zeros_like(totals), where=totals > 0)
    normalized = values * scale[:, None]
    if log:
        normalized = np.log1p(normalized)
    return pd.DataFrame(normalized, index=expression.index, columns=expression.columns)
