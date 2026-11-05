from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import nnls


def build_signatures(
    reference: pd.DataFrame,
    cell_type_col: str = "cell_type",
    *,
    normalize_rows: bool = True,
) -> pd.DataFrame:
    """Mean expression profile per cell type from a scRNA-seq reference.

    Each reference cell is library-size normalized first so that a cell with
    more reads does not dominate the profile. Rows are then scaled to the same
    total, so NNLS coefficients can be interpreted as cell fractions under the
    equal-RNA-content assumption.
    """
    if cell_type_col not in reference.columns:
        raise ValueError(f"Reference is missing '{cell_type_col}' column")
    numeric = reference.drop(columns=[cell_type_col]).apply(pd.to_numeric, errors="coerce")
    numeric = numeric.fillna(0.0)
    totals = numeric.sum(axis=1).replace(0, np.nan)
    numeric = numeric.div(totals, axis=0).fillna(0.0) * 1e4
    labels = reference[cell_type_col].astype(str)
    signatures = numeric.groupby(labels, observed=True).mean()
    signatures.index = signatures.index.astype(str)
    if normalize_rows:
        row_totals = signatures.sum(axis=1).replace(0, np.nan)
        signatures = signatures.div(row_totals, axis=0).fillna(0.0)
    return signatures


def marker_pseudosignatures(pack: dict, genes: list[str]) -> pd.DataFrame:
    """Fallback when no scRNA-seq reference is available.

    This is a marker-score baseline, not true deconvolution. The pipeline marks
    it as such in warnings and metadata.
    """
    gene_set = set(genes)
    rows: dict[str, list[float]] = {}
    for cell_type in pack.get("cell_types", []):
        markers = [g for g in cell_type.get("markers", []) if g in gene_set]
        rows[cell_type["id"]] = [1.0 if g in markers else 0.0 for g in genes]
    signatures = pd.DataFrame.from_dict(rows, orient="index", columns=genes)
    row_totals = signatures.sum(axis=1).replace(0, np.nan)
    signatures = signatures.div(row_totals, axis=0).fillna(1.0 / max(len(genes), 1))
    return signatures


def nnls_deconvolve(
    expression: pd.DataFrame,
    signatures: pd.DataFrame,
    *,
    min_shared_genes: int = 10,
) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    """Solve non-negative least squares per spot.

    `expression` must be on a linear (library-size normalized) scale, not
    log-transformed. Returns (composition spots × cell types, residual per
    spot, genes used).
    """
    shared = [g for g in expression.columns if g in signatures.columns]
    if len(shared) < min_shared_genes:
        raise ValueError(
            f"Only {len(shared)} shared genes between sample and reference; "
            f"need at least {min_shared_genes}"
        )

    y_matrix = expression[shared].to_numpy(dtype=float)
    a_matrix = signatures[shared].to_numpy(dtype=float).T  # genes × cell types
    cell_types = list(signatures.index)

    weights = np.zeros((y_matrix.shape[0], a_matrix.shape[1]), dtype=float)
    residuals = np.zeros(y_matrix.shape[0], dtype=float)
    for i, row in enumerate(y_matrix):
        try:
            coef, residual = nnls(a_matrix, row, maxiter=500)
        except Exception:
            coef = np.zeros(a_matrix.shape[1])
            residual = float(np.linalg.norm(row))
        total = coef.sum()
        if total > 0:
            weights[i] = coef / total
        else:
            weights[i] = 1.0 / max(len(cell_types), 1)
        denom = max(float(np.linalg.norm(row)), 1e-8)
        residuals[i] = float(residual) / denom

    composition = pd.DataFrame(weights, index=expression.index, columns=cell_types)
    return composition, residuals, shared


def marker_score_composition(
    expression: pd.DataFrame,
    pack: dict,
    *,
    temperature: float = 1.0,
) -> pd.DataFrame:
    """Softmax marker score composition (fallback, not deconvolution)."""
    scores = []
    labels = []
    values = expression.to_numpy(dtype=float)
    means = values.mean(axis=0)
    stds = values.std(axis=0)
    stds[stds == 0] = 1.0
    z = (values - means) / stds
    gene_index = {g: i for i, g in enumerate(expression.columns)}

    for cell_type in pack.get("cell_types", []):
        idx = [gene_index[g] for g in cell_type.get("markers", []) if g in gene_index]
        if idx:
            scores.append(z[:, idx].mean(axis=1))
        else:
            scores.append(np.zeros(len(expression)))
        labels.append(cell_type["id"])

    score_matrix = np.column_stack(scores) if scores else np.zeros((len(expression), 1))
    score_matrix = score_matrix / max(temperature, 1e-6)
    score_matrix -= score_matrix.max(axis=1, keepdims=True)
    exp = np.exp(score_matrix)
    weights = exp / np.clip(exp.sum(axis=1, keepdims=True), 1e-8, None)
    return pd.DataFrame(weights, index=expression.index, columns=labels)


def method_concordance(
    primary: pd.DataFrame,
    secondary: pd.DataFrame,
    *,
    names: tuple[str, str] = ("primary", "secondary"),
) -> tuple[np.ndarray, dict]:
    """Agreement between two composition estimates (Glio-Cartography's Tangram–NNLS check).

    Returns per-spot agreement in [0, 1] (1 − Jensen–Shannon divergence, base 2)
    and a summary with the mean per-cell-type Pearson correlation across spots.
    Low agreement means the composition depends on the method and should be
    read with more caution.
    """
    shared = [c for c in primary.columns if c in secondary.columns]
    if not shared:
        raise ValueError("No shared cell types between methods")
    a = np.clip(primary[shared].to_numpy(dtype=float), 0, None)
    b = np.clip(secondary[shared].to_numpy(dtype=float), 0, None)
    a = a / np.clip(a.sum(axis=1, keepdims=True), 1e-12, None)
    b = b / np.clip(b.sum(axis=1, keepdims=True), 1e-12, None)
    m = 0.5 * (a + b)

    def _kl(p: np.ndarray, q: np.ndarray) -> np.ndarray:
        p_safe = np.clip(p, 1e-12, None)
        q_safe = np.clip(q, 1e-12, None)
        return (p * (np.log2(p_safe) - np.log2(q_safe))).sum(axis=1)

    jsd = np.clip(0.5 * _kl(a, m) + 0.5 * _kl(b, m), 0, 1)
    agreement = 1.0 - jsd

    per_type: dict[str, float | None] = {}
    for j, cell_type in enumerate(shared):
        x, y = a[:, j], b[:, j]
        if x.std() < 1e-12 or y.std() < 1e-12:
            per_type[cell_type] = None
        else:
            per_type[cell_type] = round(float(np.corrcoef(x, y)[0, 1]), 4)
    valid = [v for v in per_type.values() if v is not None]
    summary = {
        "methods": list(names),
        "mean_spot_agreement": round(float(agreement.mean()), 4),
        "low_agreement_fraction": round(float((agreement < 0.7).mean()), 4),
        "mean_cell_type_pearson": round(float(np.mean(valid)), 4) if valid else None,
        "per_cell_type_pearson": per_type,
    }
    return agreement, summary
