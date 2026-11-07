"""Leakage-controlled perturbation-response benchmark utilities.

The functions here are intentionally independent of the spatial pipeline. They
operate on the PIE preprocessed array format and are used by the scripts under
``scripts/perturbation``. No test labels are read while selecting a
hyperparameter: :func:`select_beta` only receives validation rows.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

import numpy as np

DEFAULT_BETAS: tuple[float, ...] = tuple(
    float(value) for value in np.round(np.arange(0.0, 1.0001, 0.05), 2)
)


@dataclass(frozen=True)
class PieDataset:
    """PIE preprocessed perturbation effects for one dataset."""

    lfc: np.ndarray
    tested: np.ndarray
    contexts: np.ndarray
    perturbations: np.ndarray
    genes: tuple[str, ...]
    context_names: tuple[str, ...]
    perturbation_names: tuple[str, ...]
    context_to_id: dict[str, int]
    pert_to_id: dict[str, int]
    pert_ensembl: dict[str, str]

    @cached_property
    def mask(self) -> np.ndarray:
        """Entries that were tested and have a finite log2 fold-change."""
        return self.tested & np.isfinite(self.lfc)


def load_pie_dataset(data_dir: str | Path) -> PieDataset:
    """Load the arrays written by ``pie prep`` and validate their shapes."""
    root = Path(data_dir)
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    lfc = np.load(root / "lfc_true.npy", mmap_mode="r")
    tested = np.load(root / "tested.npy", mmap_mode="r")
    contexts = np.load(root / "ctx_ids.npy")
    perturbations = np.load(root / "pert_ids.npy")

    n_rows, n_genes = lfc.shape
    if tested.shape != lfc.shape:
        raise ValueError(f"tested shape {tested.shape} != lfc shape {lfc.shape}")
    if contexts.shape != (n_rows,) or perturbations.shape != (n_rows,):
        raise ValueError("context/perturbation id arrays do not match the row count")
    if int(meta["num_rows"]) != n_rows or int(meta["num_genes"]) != n_genes:
        raise ValueError("meta.json shape does not match the arrays")

    context_to_id = {str(k): int(v) for k, v in meta["context_to_id"].items()}
    pert_to_id = {str(k): int(v) for k, v in meta["pert_to_id"].items()}
    context_names = tuple(
        name for name, _ in sorted(context_to_id.items(), key=lambda item: item[1])
    )
    perturbation_names = tuple(
        name for name, _ in sorted(pert_to_id.items(), key=lambda item: item[1])
    )
    if len(context_names) != int(meta["num_contexts"]):
        raise ValueError("context vocabulary length mismatch")
    if len(perturbation_names) != int(meta["num_perts"]):
        raise ValueError("perturbation vocabulary length mismatch")

    return PieDataset(
        lfc=lfc,
        tested=tested,
        contexts=contexts,
        perturbations=perturbations,
        genes=tuple(str(g) for g in meta["genes"]),
        context_names=context_names,
        perturbation_names=perturbation_names,
        context_to_id=context_to_id,
        pert_to_id=pert_to_id,
        pert_ensembl={str(k): str(v) for k, v in (meta.get("pert_ensembl") or {}).items()},
    )


def row_lookup(dataset: PieDataset) -> dict[tuple[int, int], int]:
    """Map ``(context_id, perturbation_id)`` to the preprocessed row index."""
    return {
        (int(context), int(perturbation)): index
        for index, (context, perturbation) in enumerate(
            zip(dataset.contexts, dataset.perturbations, strict=True)
        )
    }


def load_split_rows(
    dataset: PieDataset,
    split_dir: str | Path,
    setting: str,
    fold: str,
    part: str,
) -> np.ndarray:
    """Resolve one PIE split JSON file to preprocessed row indices."""
    path = Path(split_dir) / f"replogle_wdataset_{setting}_{fold}_{part}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    lookup = row_lookup(dataset)
    rows: list[int] = []
    for key, perturbation_names in payload.items():
        context_name = key.split(".")[-1]
        if context_name not in dataset.context_to_id:
            raise ValueError(f"unknown context {context_name!r} in {path.name}")
        context_id = dataset.context_to_id[context_name]
        for perturbation_name in perturbation_names:
            perturbation_id = dataset.pert_to_id.get(perturbation_name)
            if perturbation_id is None:
                raise ValueError(f"unknown perturbation {perturbation_name!r} in {path.name}")
            row = lookup.get((context_id, perturbation_id))
            if row is None:
                raise ValueError(
                    f"split row ({context_name}, {perturbation_name}) is absent from the arrays"
                )
            rows.append(row)
    result = np.asarray(rows, dtype=np.int64)
    if len(np.unique(result)) != len(result):
        raise ValueError(f"duplicate rows in {path.name}")
    return result


def load_unseen_context_fold(
    dataset: PieDataset,
    split_dir: str | Path,
    fold: str,
) -> dict[str, np.ndarray]:
    """Load a fold and enforce context/row isolation for ``unseen_ctx``."""
    train = load_split_rows(dataset, split_dir, "unseen_ctx", fold, "train")
    validation = load_split_rows(dataset, split_dir, "unseen_ctx", fold, "val")
    test = load_split_rows(dataset, split_dir, "unseen_ctx", fold, "test")

    fold_context = dataset.context_to_id[fold]
    test_contexts = set(int(c) for c in np.unique(dataset.contexts[test]))
    train_contexts = set(int(c) for c in np.unique(dataset.contexts[train]))
    validation_contexts = set(int(c) for c in np.unique(dataset.contexts[validation]))
    if test_contexts != {fold_context}:
        raise ValueError(f"test rows for {fold} are not confined to its held-out context")
    if fold_context in train_contexts or fold_context in validation_contexts:
        raise ValueError(f"held-out context {fold} leaked into train or validation")

    seen = np.concatenate([train, validation, test])
    if len(np.unique(seen)) != len(seen):
        raise ValueError(f"train/validation/test rows overlap for fold {fold}")
    return {"train": train, "validation": validation, "test": test}


def masked_gene_mean(dataset: PieDataset, rows: np.ndarray) -> np.ndarray:
    """Per-gene mean over the tested entries of ``rows``."""
    rows = np.asarray(rows, dtype=np.int64)
    if rows.size == 0:
        raise ValueError("cannot average an empty row set")
    selected = dataset.mask[rows]
    counts = selected.sum(axis=0)
    sums = np.where(selected, dataset.lfc[rows], 0.0).sum(axis=0)
    return np.divide(
        sums,
        counts,
        out=np.zeros(sums.shape, dtype=np.float64),
        where=counts > 0,
    )


def perturbation_mean_map(
    dataset: PieDataset,
    train_rows: np.ndarray,
) -> dict[int, np.ndarray]:
    """Per-perturbation mean effects computed only from training rows."""
    train_rows = np.asarray(train_rows, dtype=np.int64)
    train_perturbations = dataset.perturbations[train_rows]
    means: dict[int, np.ndarray] = {}
    for perturbation_id in np.unique(train_perturbations):
        members = train_rows[train_perturbations == perturbation_id]
        means[int(perturbation_id)] = masked_gene_mean(dataset, members)
    return means


def filled_perturbation_mean_map(
    dataset: PieDataset,
    train_rows: np.ndarray,
    global_mean: np.ndarray,
) -> dict[int, np.ndarray]:
    """Per-perturbation means with untested genes filled by the global mean.

    This is the single-training-context variant used by the Orion replication.
    Each perturbation may have only one row in the training context; genes that
    were not tested in that row carry no perturbation-specific information and
    must fall back to ``global_mean``. Without this fallback, the centered
    prediction would silently predict zero for a large fraction of genes.
    """
    train_rows = np.asarray(train_rows, dtype=np.int64)
    train_perturbations = dataset.perturbations[train_rows]
    global_mean = np.asarray(global_mean, dtype=np.float64)
    means: dict[int, np.ndarray] = {}
    for perturbation_id in np.unique(train_perturbations):
        members = train_rows[train_perturbations == perturbation_id]
        tested = dataset.tested[members]
        values = np.asarray(dataset.lfc[members], dtype=np.float64)
        valid = tested & np.isfinite(values)
        counts = valid.sum(axis=0)
        sums = np.where(valid, values, 0.0).sum(axis=0)
        mean = np.divide(
            sums,
            counts,
            out=np.zeros(sums.shape, dtype=np.float64),
            where=counts > 0,
        )
        means[int(perturbation_id)] = np.where(counts > 0, mean, global_mean)
    return means


def perturbation_mean_predictions(
    dataset: PieDataset,
    target_rows: np.ndarray,
    means: dict[int, np.ndarray],
    global_mean: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Predict each target row with its perturbation mean, falling back to global."""
    target_rows = np.asarray(target_rows, dtype=np.int64)
    predictions = np.empty((target_rows.size, dataset.lfc.shape[1]), dtype=np.float64)
    seen = np.zeros(target_rows.size, dtype=bool)
    for index, row in enumerate(target_rows):
        mean = means.get(int(dataset.perturbations[row]))
        if mean is None:
            predictions[index] = global_mean
        else:
            predictions[index] = mean
            seen[index] = True
    return predictions, seen


@dataclass(frozen=True)
class PredictionScore:
    """Per-row diagnostics that can be bootstrapped without recomputing errors."""

    row_mse: np.ndarray
    row_genes: np.ndarray
    row_rmse: np.ndarray
    row_correlation: np.ndarray
    row_top_k: np.ndarray
    row_sign: np.ndarray
    top_k: int

    def summary(self) -> dict[str, Any]:
        valid = np.isfinite(self.row_mse) & (self.row_genes > 0)
        if not valid.any():
            return {
                "rows": 0,
                "tested_genes": 0,
                "pooled_rmse": None,
                "mean_row_rmse": None,
                "median_row_correlation": None,
                "mean_top_k_overlap": None,
                "mean_sign_accuracy": None,
                "top_k": self.top_k,
            }
        genes = int(self.row_genes[valid].sum())
        pooled = float(
            np.sqrt(np.sum(self.row_mse[valid] * self.row_genes[valid]) / genes)
        )
        correlations = self.row_correlation[valid]
        top_k = self.row_top_k[valid]
        signs = self.row_sign[valid]
        return {
            "rows": int(valid.sum()),
            "tested_genes": genes,
            "pooled_rmse": pooled,
            "mean_row_rmse": float(np.mean(self.row_rmse[valid])),
            "median_row_correlation": (
                float(np.nanmedian(correlations))
                if np.isfinite(correlations).any()
                else None
            ),
            "mean_top_k_overlap": float(np.nanmean(top_k)),
            "mean_sign_accuracy": (
                float(np.nanmean(signs)) if np.isfinite(signs).any() else None
            ),
            "top_k": self.top_k,
        }


def score_predictions(
    dataset: PieDataset,
    rows: np.ndarray,
    prediction: np.ndarray,
    *,
    top_k: int = 50,
    sign_threshold: float = 0.1,
    support: np.ndarray | None = None,
) -> PredictionScore:
    """Score predictions row by row over the tested genes of each row.

    ``support`` optionally restricts each row to an additional boolean gene
    mask, for example genes tested in both the training and test rows.
    """
    rows = np.asarray(rows, dtype=np.int64)
    prediction = np.asarray(prediction, dtype=np.float64)
    if prediction.shape != (rows.size, dataset.lfc.shape[1]):
        raise ValueError(
            f"prediction shape {prediction.shape} != {(rows.size, dataset.lfc.shape[1])}"
        )
    mask = dataset.mask[rows]
    if support is not None:
        support = np.asarray(support, dtype=bool)
        if support.shape != mask.shape:
            raise ValueError(
                f"support shape {support.shape} != score mask shape {mask.shape}"
            )
        mask = mask & support

    row_mse = np.full(rows.size, np.nan, dtype=np.float64)
    row_genes = np.zeros(rows.size, dtype=np.int64)
    row_correlation = np.full(rows.size, np.nan, dtype=np.float64)
    row_overlap = np.full(rows.size, np.nan, dtype=np.float64)
    row_sign = np.full(rows.size, np.nan, dtype=np.float64)

    for index, row in enumerate(rows):
        selected = mask[index]
        truth = np.asarray(dataset.lfc[row][selected], dtype=np.float64)
        predicted = prediction[index][selected]
        if truth.size == 0:
            continue
        row_genes[index] = truth.size
        row_mse[index] = float(np.mean(np.square(predicted - truth)))

        if truth.size >= 2 and np.std(truth) > 0 and np.std(predicted) > 0:
            correlation = float(np.corrcoef(truth, predicted)[0, 1])
            if np.isfinite(correlation):
                row_correlation[index] = correlation

        k = min(top_k, truth.size)
        true_top = set(np.argpartition(np.abs(truth), -k)[-k:].tolist())
        predicted_top = set(np.argpartition(np.abs(predicted), -k)[-k:].tolist())
        row_overlap[index] = len(true_top & predicted_top) / k

        signal = np.abs(truth) > sign_threshold
        if signal.any():
            row_sign[index] = float(
                np.mean(np.sign(predicted[signal]) == np.sign(truth[signal]))
            )

    return PredictionScore(
        row_mse=row_mse,
        row_genes=row_genes,
        row_rmse=np.sqrt(row_mse),
        row_correlation=row_correlation,
        row_top_k=row_overlap,
        row_sign=row_sign,
        top_k=top_k,
    )


def select_beta(
    prediction_for_beta: Callable[[float], np.ndarray],
    dataset: PieDataset,
    validation_rows: np.ndarray,
    betas: Sequence[float] = DEFAULT_BETAS,
) -> tuple[float, list[dict[str, float]]]:
    """Pick beta on validation rows only; ties prefer the smaller beta."""
    curve: list[dict[str, float]] = []
    best_beta: float | None = None
    best_rmse = float("inf")
    for beta in betas:
        score = score_predictions(
            dataset, validation_rows, prediction_for_beta(float(beta))
        )
        mean_rmse = score.summary()["mean_row_rmse"]
        if mean_rmse is None:
            raise ValueError("validation score is undefined")
        curve.append({"beta": float(beta), "mean_row_rmse": float(mean_rmse)})
        if mean_rmse < best_rmse - 1e-12:
            best_beta, best_rmse = float(beta), float(mean_rmse)
        elif abs(mean_rmse - best_rmse) <= 1e-12 and best_beta is not None:
            best_beta = min(best_beta, float(beta))
    if best_beta is None:
        raise ValueError("beta grid is empty")
    return best_beta, curve


def paired_bootstrap_delta(
    baseline: PredictionScore,
    candidate: PredictionScore,
    *,
    resamples: int = 2000,
    seed: int = 20261107,
) -> dict[str, Any]:
    """Paired bootstrap of baseline minus candidate equal-row RMSE.

    A positive delta means the candidate has lower error. Resampling is over
    context-perturbation rows, not individual genes.
    """
    if baseline.row_mse.shape != candidate.row_mse.shape:
        raise ValueError("scores must come from the same rows")
    valid = np.isfinite(baseline.row_mse) & np.isfinite(candidate.row_mse)
    base = np.sqrt(baseline.row_mse[valid])
    candidate_rmse = np.sqrt(candidate.row_mse[valid])
    if base.size == 0:
        raise ValueError("no valid rows to bootstrap")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, base.size, size=(resamples, base.size))
    delta = base[indices].mean(axis=1) - candidate_rmse[indices].mean(axis=1)
    return {
        "mean_delta": float(np.mean(delta)),
        "ci95": [float(value) for value in np.quantile(delta, [0.025, 0.975])],
        "unit": "context-perturbation row",
        "resamples": int(resamples),
        "seed": int(seed),
    }


def gate_checks(
    candidate: dict[str, Any],
    zero: dict[str, Any],
    global_mean: dict[str, Any],
    bootstrap_vs_zero: dict[str, Any],
    *,
    beta: float,
) -> dict[str, Any]:
    """Apply the pre-registered success rule to one fold."""
    if candidate["mean_row_rmse"] is None or zero["mean_row_rmse"] in (None, 0):
        raise ValueError("gate metrics are undefined")
    relative = (zero["mean_row_rmse"] - candidate["mean_row_rmse"]) / zero[
        "mean_row_rmse"
    ]
    top_k_delta = (candidate["mean_top_k_overlap"] or 0.0) - (
        zero["mean_top_k_overlap"] or 0.0
    )
    checks = {
        "relative_improvement": float(relative),
        "improvement_at_least_3pct": bool(relative >= 0.03),
        "bootstrap_ci_above_zero": bool(bootstrap_vs_zero["ci95"][0] > 0),
        "median_correlation_above_0_20": bool(
            (candidate["median_row_correlation"] or -1.0) > 0.20
        ),
        "top_k_improvement_at_least_0_02": bool(top_k_delta >= 0.02),
        "not_worse_than_global_mean": bool(
            candidate["mean_row_rmse"] <= (global_mean["mean_row_rmse"] or float("inf"))
        ),
        "beta_positive": bool(beta > 0),
    }
    checks["passes"] = all(
        checks[key]
        for key in (
            "improvement_at_least_3pct",
            "bootstrap_ci_above_zero",
            "median_correlation_above_0_20",
            "top_k_improvement_at_least_0_02",
            "not_worse_than_global_mean",
            "beta_positive",
        )
    )
    return checks


def evaluate_unseen_context_fold(
    dataset: PieDataset,
    split_dir: str | Path,
    fold: str,
    *,
    betas: Sequence[float] = DEFAULT_BETAS,
    resamples: int = 2000,
    seed: int = 20261107,
) -> dict[str, Any]:
    """Run the pre-registered unseen-context comparison for one fold."""
    splits = load_unseen_context_fold(dataset, split_dir, fold)
    train, validation, test = splits["train"], splits["validation"], splits["test"]

    global_mean = masked_gene_mean(dataset, train)
    means = perturbation_mean_map(dataset, train)
    train_contexts = sorted(
        dataset.context_names[int(c)] for c in np.unique(dataset.contexts[train])
    )

    validation_perturbation_mean, validation_seen = perturbation_mean_predictions(
        dataset, validation, means, global_mean
    )
    test_perturbation_mean, test_seen = perturbation_mean_predictions(
        dataset, test, means, global_mean
    )
    validation_centered = validation_perturbation_mean - global_mean
    test_centered = test_perturbation_mean - global_mean

    beta, beta_curve = select_beta(
        lambda value: value * validation_centered,
        dataset,
        validation,
        betas,
    )
    beta_uncentered, beta_curve_uncentered = select_beta(
        lambda value: value * validation_perturbation_mean,
        dataset,
        validation,
        betas,
    )

    test_predictions = {
        "zero": np.zeros_like(test_centered),
        "global_mean": np.broadcast_to(global_mean, test_centered.shape).copy(),
        "unscaled_perturbation_mean": test_perturbation_mean,
        "centered_perturbation_mean": test_centered,
        "scaled_transfer": beta * test_centered,
        "scaled_uncentered_sensitivity": beta_uncentered * test_perturbation_mean,
    }
    validation_predictions = {
        "zero": np.zeros_like(validation_centered),
        "global_mean": np.broadcast_to(global_mean, validation_centered.shape).copy(),
        "unscaled_perturbation_mean": validation_perturbation_mean,
        "centered_perturbation_mean": validation_centered,
        "scaled_transfer": beta * validation_centered,
        "scaled_uncentered_sensitivity": beta_uncentered * validation_perturbation_mean,
    }

    test_scores = {
        name: score_predictions(dataset, test, prediction)
        for name, prediction in test_predictions.items()
    }
    validation_scores = {
        name: score_predictions(dataset, validation, prediction)
        for name, prediction in validation_predictions.items()
    }
    test_summaries = {name: score.summary() for name, score in test_scores.items()}
    validation_summaries = {
        name: score.summary() for name, score in validation_scores.items()
    }

    comparisons = {}
    for name in test_scores:
        if name in {"zero", "global_mean"}:
            continue
        comparisons[name] = {
            "vs_zero": paired_bootstrap_delta(
                test_scores["zero"],
                test_scores[name],
                resamples=resamples,
                seed=seed,
            ),
            "vs_global_mean": paired_bootstrap_delta(
                test_scores["global_mean"],
                test_scores[name],
                resamples=resamples,
                seed=seed,
            ),
        }

    checks = gate_checks(
        test_summaries["scaled_transfer"],
        test_summaries["zero"],
        test_summaries["global_mean"],
        comparisons["scaled_transfer"]["vs_zero"],
        beta=beta,
    )
    return {
        "fold": fold,
        "held_out_context": fold,
        "train_contexts": train_contexts,
        "rows": {
            "train": int(train.size),
            "validation": int(validation.size),
            "test": int(test.size),
        },
        "perturbation_coverage": {
            "validation": float(validation_seen.mean()),
            "test": float(test_seen.mean()),
        },
        "beta": {
            "scaled_transfer": beta,
            "scaled_uncentered_sensitivity": beta_uncentered,
            "grid": [float(value) for value in betas],
            "selection_metric": "validation mean row RMSE",
            "curve": beta_curve,
            "curve_uncentered_sensitivity": beta_curve_uncentered,
        },
        "validation": validation_summaries,
        "test": test_summaries,
        "bootstrap": comparisons,
        "gate": checks,
    }


def evaluate_gate(
    fold_results: dict[str, dict[str, Any]],
    confirmatory_folds: Sequence[str],
) -> dict[str, Any]:
    """Aggregate folds with the pre-registered two-of-three rule."""
    passing = [
        fold for fold in confirmatory_folds if fold_results[fold]["gate"]["passes"]
    ]
    return {
        "confirmatory_folds": list(confirmatory_folds),
        "passing_folds": passing,
        "n_passing": len(passing),
        "required": 2,
        "passed": len(passing) >= 2,
        "rule": (
            "At least two untouched folds must satisfy all pre-registered checks: "
            ">=3% relative row-RMSE improvement, bootstrap CI above zero, median row "
            "correlation > 0.20, top-50 overlap +0.02, not worse than global mean, "
            "and beta > 0."
        ),
    }
