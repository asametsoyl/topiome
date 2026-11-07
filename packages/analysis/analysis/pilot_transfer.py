"""Few-shot ("pilot") context transfer for perturbation effects.

Task: a new cell context has been profiled with a small pilot screen of ``k``
perturbations. Predict the remaining perturbations in that context from

* the pilot rows measured in the target context, and
* the full screen measured in a source context.

Zero-shot transfer failed on X-Atlas/Orion because the source context's
average profile does not carry over and typical per-perturbation effects are
nearly uncorrelated across cell lines. Both problems are estimable from a
pilot, so every method here learns the target offset (and any scaling) from
pilot rows only. The fair comparator is ``pilot_mean``: predicting the pilot's
average profile for every held-out perturbation. A transfer method is useful
only if it beats that.

No held-out target labels are read when fitting: every ``fit_*`` function
receives pilot rows only, and pilot perturbations are drawn at random.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .perturbation import PieDataset, masked_gene_mean

RIDGE_LAMBDAS: tuple[float, ...] = (0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)


@dataclass(frozen=True)
class PairRows:
    """Aligned rows of one ordered context pair over common perturbations."""

    source: np.ndarray  # row index in the source context, per perturbation
    target: np.ndarray  # row index in the target context, same order
    perturbations: np.ndarray


def pair_subset(dataset: PieDataset, source_context: int, target_context: int) -> PieDataset:
    """The two contexts' rows loaded into memory once.

    Large PIE arrays are memory-mapped; computing ``mask`` or fancy-indexing the
    full array repeatedly would re-read gigabytes. Working on this subset keeps
    each pair to a single read.
    """
    rows = np.flatnonzero(np.isin(dataset.contexts, [source_context, target_context]))
    return replace(
        dataset,
        lfc=np.asarray(dataset.lfc[rows], dtype=np.float32),
        tested=np.asarray(dataset.tested[rows], dtype=bool),
        contexts=np.asarray(dataset.contexts[rows]),
        perturbations=np.asarray(dataset.perturbations[rows]),
    )


def pair_rows(dataset: PieDataset, source_context: int, target_context: int) -> PairRows:
    """Rows of perturbations measured in both contexts (one row per context)."""
    by_key: dict[tuple[int, int], int] = {}
    for index, (context, perturbation) in enumerate(
        zip(dataset.contexts, dataset.perturbations, strict=True)
    ):
        key = (int(context), int(perturbation))
        if key in by_key:
            raise ValueError(f"duplicate row for context/perturbation {key}")
        by_key[key] = index
    source_perts = {p for (c, p) in by_key if c == source_context}
    target_perts = {p for (c, p) in by_key if c == target_context}
    common = np.array(sorted(source_perts & target_perts), dtype=np.int64)
    return PairRows(
        source=np.array([by_key[(source_context, p)] for p in common], dtype=np.int64),
        target=np.array([by_key[(target_context, p)] for p in common], dtype=np.int64),
        perturbations=common,
    )


def draw_pilot(n: int, k: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Random pilot positions and the remaining (held-out) positions."""
    if not 0 < k < n:
        raise ValueError(f"pilot size {k} must be between 1 and {n - 1}")
    order = rng.permutation(n)
    return np.sort(order[:k]), np.sort(order[k:])


def centered_source_effects(
    dataset: PieDataset, source_rows: np.ndarray, source_mean: np.ndarray
) -> np.ndarray:
    """Source effects minus the source context mean; untested genes become 0."""
    values = np.asarray(dataset.lfc[source_rows], dtype=np.float64)
    tested = dataset.mask[source_rows]
    return np.where(tested, values - source_mean, 0.0)


def _target_residuals(
    dataset: PieDataset, target_rows: np.ndarray, target_mean: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(dataset.lfc[target_rows], dtype=np.float64)
    tested = dataset.mask[target_rows]
    return np.where(tested, values - target_mean, 0.0), tested


# ── Methods ──────────────────────────────────────────────────────────────────


def fit_scale(
    source_effects_pilot: np.ndarray, residual_pilot: np.ndarray, tested_pilot: np.ndarray
) -> float:
    """Least-squares scale beta for residual ≈ beta · source effect, clipped to [0, 1]."""
    x = np.where(tested_pilot, source_effects_pilot, 0.0)
    denominator = float(np.sum(x * x))
    if denominator <= 0:
        return 0.0
    return float(np.clip(np.sum(x * residual_pilot) / denominator, 0.0, 1.0))


@dataclass(frozen=True)
class RidgeMap:
    components: np.ndarray  # genes × r (source PCA basis)
    weights: np.ndarray  # r × genes
    lam: float
    rank: int


def fit_lowrank_ridge(
    source_effects_all: np.ndarray,
    source_effects_pilot: np.ndarray,
    residual_pilot: np.ndarray,
    *,
    rank: int = 20,
    lambdas: tuple[float, ...] = RIDGE_LAMBDAS,
) -> RidgeMap:
    """Ridge map from source-effect principal components to target residuals.

    The PCA basis uses source-context effects only (inputs, never target
    labels). Lambda is chosen by exact leave-one-out error over pilot rows.
    """
    centered = source_effects_all - source_effects_all.mean(axis=0, keepdims=True)
    rank = int(min(rank, centered.shape[0] - 1, centered.shape[1]))
    # Top right-singular vectors via the (rows × rows) Gram matrix: same basis as
    # a full SVD but memory scales with perturbations, not with ~20k genes.
    eigenvalues, eigenvectors = np.linalg.eigh(centered @ centered.T)
    top = np.argsort(eigenvalues)[::-1][:rank]
    singular = np.sqrt(np.clip(eigenvalues[top], 1e-12, None))
    components = (centered.T @ eigenvectors[:, top]) / singular
    z = source_effects_pilot @ components
    gram = z.T @ z
    best: tuple[float, float, np.ndarray] | None = None
    for lam in lambdas:
        inverse = np.linalg.inv(gram + lam * np.eye(rank))
        hat = z @ inverse @ z.T
        fitted = hat @ residual_pilot
        leverage = np.clip(np.diag(hat), 0.0, 0.999)
        loo = (residual_pilot - fitted) / (1.0 - leverage)[:, None]
        error = float(np.mean(loo * loo))
        if best is None or error < best[1] - 1e-15:
            best = (float(lam), error, inverse @ z.T @ residual_pilot)
    assert best is not None
    return RidgeMap(components=components, weights=best[2], lam=best[0], rank=rank)


def predict_pair(
    dataset: PieDataset,
    pair: PairRows,
    pilot: np.ndarray,
    held_out: np.ndarray,
    *,
    rank: int = 20,
) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    """Predictions for the held-out target rows from every method + fitted params."""
    source_mean = masked_gene_mean(dataset, pair.source)  # source inputs only
    target_pilot_rows = pair.target[pilot]
    target_mean = masked_gene_mean(dataset, target_pilot_rows)
    effects = centered_source_effects(dataset, pair.source, source_mean)
    residual_pilot, tested_pilot = _target_residuals(dataset, target_pilot_rows, target_mean)

    beta = fit_scale(effects[pilot], residual_pilot, tested_pilot)
    ridge = fit_lowrank_ridge(effects, effects[pilot], residual_pilot, rank=rank)

    n_genes = dataset.lfc.shape[1]
    held = effects[held_out]
    zeros = np.zeros((held_out.size, n_genes))
    predictions = {
        "zero": zeros,
        "pilot_mean": zeros + target_mean,
        "zero_shot_beta025": zeros + source_mean + 0.25 * held,
        "pilot_scaled_transfer": target_mean + beta * held,
        "pilot_lowrank_ridge": target_mean + (held @ ridge.components) @ ridge.weights,
    }
    predictions = {name: value.astype(np.float32) for name, value in predictions.items()}
    return predictions, {"beta": beta, "ridge_lambda": ridge.lam, "ridge_rank": ridge.rank}


# ── Fast scoring ─────────────────────────────────────────────────────────────


def score_rows_fast(
    truth: np.ndarray,
    tested: np.ndarray,
    prediction: np.ndarray,
    *,
    top_k: int = 50,
) -> dict[str, np.ndarray]:
    """Vectorised per-row RMSE, Pearson r and top-k |effect| overlap.

    Same definitions as :func:`analysis.perturbation.score_predictions`
    (scored over each row's tested genes), without a Python loop over rows.
    """
    truth = np.asarray(truth, dtype=np.float64)
    prediction = np.asarray(prediction, dtype=np.float64)
    mask = np.asarray(tested, dtype=bool) & np.isfinite(truth)
    n = mask.sum(axis=1)
    t = np.where(mask, truth, 0.0)
    p = np.where(mask, prediction, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        mse = np.where(mask, (p - t) ** 2, 0.0).sum(axis=1) / n
        t_mean = t.sum(axis=1) / n
        p_mean = p.sum(axis=1) / n
        tc = np.where(mask, t - t_mean[:, None], 0.0)
        pc = np.where(mask, p - p_mean[:, None], 0.0)
        covariance = (tc * pc).sum(axis=1)
        denominator = np.sqrt((tc * tc).sum(axis=1) * (pc * pc).sum(axis=1))
        correlation = np.where(denominator > 0, covariance / denominator, np.nan)

    overlap = np.full(truth.shape[0], np.nan)
    neg = -np.inf
    abs_t = np.where(mask, np.abs(truth), neg)
    abs_p = np.where(mask, np.abs(prediction), neg)
    for row in range(truth.shape[0]):  # argpartition per row on ≤ genes; cheap
        k = int(min(top_k, n[row]))
        if k == 0:
            continue
        top_t = np.argpartition(abs_t[row], -k)[-k:]
        top_p = np.argpartition(abs_p[row], -k)[-k:]
        overlap[row] = len(np.intersect1d(top_t, top_p, assume_unique=True)) / k
    valid = n > 0
    return {
        "rmse": np.where(valid, np.sqrt(mse), np.nan),
        "correlation": np.where(valid, correlation, np.nan),
        "top_k_overlap": overlap,
        "genes": n,
    }


def summarize_rows(scores: dict[str, np.ndarray]) -> dict[str, float | None]:
    def _stat(values: np.ndarray, fn) -> float | None:  # noqa: ANN001
        finite = values[np.isfinite(values)]
        return float(fn(finite)) if finite.size else None

    return {
        "mean_row_rmse": _stat(scores["rmse"], np.mean),
        "median_row_correlation": _stat(scores["correlation"], np.median),
        "mean_top_k_overlap": _stat(scores["top_k_overlap"], np.mean),
    }
