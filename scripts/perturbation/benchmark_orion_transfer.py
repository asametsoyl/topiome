"""Run the pre-registered X-Atlas/Orion unseen-context replication.

The protocol is frozen in
``docs/experiments/2026-11-07-orion-unseen-context-preregistration.md``.
The common perturbation set and the fixed beta are defined before Orion test
labels are read; beta is never selected on Orion test rows.

This dataset is CC BY-NC-SA 4.0. The run is research-only and must not be used
for a commercial claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np
from analysis.perturbation import (
    PieDataset,
    PredictionScore,
    filled_perturbation_mean_map,
    load_pie_dataset,
    masked_gene_mean,
    paired_bootstrap_delta,
    perturbation_mean_predictions,
    score_predictions,
)

FIXED_BETA = 0.25
BETA_GRID = (0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.75, 1.00)
COMMON_NAMES_SHA256 = (
    "af2997b213db7ff95bfc6da6744e017d6a4e4305472fa1fba7d5d1ce9a1603dd"
)
FOLDS = (
    ("hct116_to_hek293t", "hct116", "hek293t"),
    ("hek293t_to_hct116", "hek293t", "hct116"),
)
PERMUTATIONS = 20


def _fmt(value: float | None, digits: int = 4) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def _common_perturbation_ids(dataset: PieDataset) -> np.ndarray:
    """Intersection of perturbation ids observed in every context."""
    sets: list[set[int]] = []
    for context_id in np.unique(dataset.contexts):
        rows = np.flatnonzero(dataset.contexts == context_id)
        sets.append({int(value) for value in dataset.perturbations[rows]})
    if len(sets) != 2:
        raise ValueError(f"expected exactly two contexts, found {len(sets)}")
    common = set.intersection(*sets)
    return np.asarray(sorted(common), dtype=np.int64)


def _verify_common_names(dataset: PieDataset, common_ids: np.ndarray) -> str:
    names = sorted(dataset.perturbation_names[int(value)] for value in common_ids)
    digest = hashlib.sha256("\n".join(names).encode("utf-8")).hexdigest()
    if digest != COMMON_NAMES_SHA256:
        raise ValueError(
            f"common perturbation hash {digest} does not match the pre-registration"
        )
    return digest


def _fold_rows(
    dataset: PieDataset,
    train_context: str,
    test_context: str,
    common_ids: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    train_context_id = dataset.context_to_id[train_context]
    test_context_id = dataset.context_to_id[test_context]
    common_mask = np.isin(dataset.perturbations, common_ids)
    train = np.flatnonzero((dataset.contexts == train_context_id) & common_mask)
    test = np.flatnonzero((dataset.contexts == test_context_id) & common_mask)
    train = train[np.argsort(dataset.perturbations[train], kind="stable")]
    test = test[np.argsort(dataset.perturbations[test], kind="stable")]

    if set(int(value) for value in np.unique(dataset.contexts[train])) != {
        train_context_id
    }:
        raise ValueError(f"{train_context} train rows leak another context")
    if set(int(value) for value in np.unique(dataset.contexts[test])) != {
        test_context_id
    }:
        raise ValueError(f"{test_context} test rows leak another context")
    if np.intersect1d(train, test).size:
        raise ValueError("train and test rows overlap")
    if not np.array_equal(
        np.sort(dataset.perturbations[train]), np.sort(dataset.perturbations[test])
    ):
        raise ValueError("train and test do not cover the same perturbation set")
    if len(np.unique(dataset.perturbations[train])) != train.size:
        raise ValueError("training context has duplicate perturbation rows")
    return train, test


def _score(
    dataset: PieDataset,
    rows: np.ndarray,
    prediction: np.ndarray,
    *,
    support: np.ndarray | None = None,
) -> PredictionScore:
    return score_predictions(dataset, rows, prediction, support=support)


def _predictions(
    global_mean: np.ndarray, centered: np.ndarray
) -> Iterator[tuple[str, np.ndarray]]:
    """Yield one prediction at a time to keep peak memory bounded."""
    yield "zero", np.broadcast_to(np.zeros_like(global_mean), centered.shape)
    yield "global_mean", np.broadcast_to(global_mean, centered.shape)
    yield "unscaled_perturbation_mean", centered + global_mean
    yield "centered_perturbation_mean", centered
    yield "scaled_transfer_beta0.25", global_mean + FIXED_BETA * centered


def _sensitivity_predictions(
    global_mean: np.ndarray, centered: np.ndarray
) -> Iterator[tuple[str, np.ndarray]]:
    for beta in BETA_GRID:
        if beta != FIXED_BETA:
            yield f"scaled_transfer_beta{beta:g}", global_mean + beta * centered


def _quantiles(values: np.ndarray) -> dict[str, float] | None:
    finite = np.asarray(values, dtype=np.float64)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return None
    return {
        f"{quantile:g}": float(np.quantile(finite, quantile))
        for quantile in (0.0, 0.25, 0.5, 0.75, 1.0)
    }


def _fraction_better(candidate: np.ndarray, baseline: np.ndarray) -> float | None:
    valid = np.isfinite(candidate) & np.isfinite(baseline)
    if not valid.any():
        return None
    return float(np.mean(candidate[valid] < baseline[valid]))


def _combine_scores(scores: list[PredictionScore]) -> PredictionScore:
    if not scores:
        raise ValueError("no scores to combine")
    top_k = scores[0].top_k
    if any(score.top_k != top_k for score in scores):
        raise ValueError("scores use different top-k values")
    return PredictionScore(
        row_mse=np.concatenate([score.row_mse for score in scores]),
        row_genes=np.concatenate([score.row_genes for score in scores]),
        row_rmse=np.concatenate([score.row_rmse for score in scores]),
        row_correlation=np.concatenate(
            [score.row_correlation for score in scores]
        ),
        row_top_k=np.concatenate([score.row_top_k for score in scores]),
        row_sign=np.concatenate([score.row_sign for score in scores]),
        top_k=top_k,
    )


def _fold_gate(
    candidate: dict[str, Any],
    zero: dict[str, Any],
    global_mean: dict[str, Any],
    bootstrap_vs_zero: dict[str, Any],
    *,
    beta: float,
) -> dict[str, Any]:
    if candidate["mean_row_rmse"] is None or zero["mean_row_rmse"] in (None, 0):
        raise ValueError("gate metrics are undefined")
    relative = (
        zero["mean_row_rmse"] - candidate["mean_row_rmse"]
    ) / zero["mean_row_rmse"]
    candidate_r = candidate["median_row_correlation"]
    global_r = global_mean["median_row_correlation"]
    candidate_top = candidate["mean_top_k_overlap"] or 0.0
    global_top = global_mean["mean_top_k_overlap"] or 0.0
    zero_top = zero["mean_top_k_overlap"] or 0.0
    numeric_checks = {
        "relative_improvement": float(relative),
        "improvement_at_least_3pct": bool(relative >= 0.03),
        "bootstrap_ci_above_zero": bool(bootstrap_vs_zero["ci95"][0] > 0),
        "median_correlation_above_0_20": bool(
            (candidate_r if candidate_r is not None else -1.0) > 0.20
        ),
        "not_worse_than_global_mean_rmse": bool(
            candidate["mean_row_rmse"] <= (global_mean["mean_row_rmse"] or float("inf"))
        ),
        "median_correlation_at_least_global": bool(
            (candidate_r if candidate_r is not None else -1.0)
            >= (global_r if global_r is not None else -1.0)
        ),
        "beta_positive": bool(beta > 0),
    }
    numeric_checks["numeric_pass"] = all(
        numeric_checks[key]
        for key in (
            "improvement_at_least_3pct",
            "bootstrap_ci_above_zero",
            "median_correlation_above_0_20",
            "not_worse_than_global_mean_rmse",
            "median_correlation_at_least_global",
            "beta_positive",
        )
    )
    ranking_checks = {
        "top_k_at_least_global": bool(candidate_top >= global_top),
        "top_k_improvement_vs_zero_at_least_0_02": bool(
            candidate_top - zero_top >= 0.02
        ),
    }
    ranking_checks["ranking_pass"] = all(ranking_checks.values())
    return {**numeric_checks, **ranking_checks}


def _aggregate_gate(fold_results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    folds = list(fold_results)
    numeric_passing = [
        fold for fold in folds if fold_results[fold]["gate"]["numeric_pass"]
    ]
    ranking_passing = [
        fold for fold in folds if fold_results[fold]["gate"]["ranking_pass"]
    ]
    numeric_replicated = len(numeric_passing) == len(folds)
    ranking_replicated = len(ranking_passing) == len(folds)
    if numeric_replicated and ranking_replicated:
        verdict = "full_replication"
    elif numeric_replicated:
        verdict = "numeric_only"
    elif len(numeric_passing) == 1:
        verdict = "partial"
    else:
        verdict = "failed"
    return {
        "folds": folds,
        "required_folds": len(folds),
        "numeric_passing_folds": numeric_passing,
        "ranking_passing_folds": ranking_passing,
        "numeric_replicated": bool(numeric_replicated),
        "ranking_replicated": bool(ranking_replicated),
        "verdict": verdict,
        "rule": (
            "Full replication requires the numeric gate and the ranking gate in "
            "both folds. Numeric-only replication permits no gene-ranking claim. "
            "A single passing fold is partial and supports no general claim."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/perturbation/raw/pie-x-atlas-orion/preprocessed"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/perturbation/processed/orion-unseen-ctx-gate.json"),
    )
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261107)
    parser.add_argument("--commit", default=None)
    args = parser.parse_args()

    dataset = load_pie_dataset(args.data_dir)
    if set(dataset.context_to_id) != {"hct116", "hek293t"}:
        raise SystemExit(f"unexpected contexts: {sorted(dataset.context_to_id)}")
    common_ids = _common_perturbation_ids(dataset)
    common_digest = _verify_common_names(dataset, common_ids)

    fold_results: dict[str, dict[str, Any]] = {}
    combined_candidate: list[PredictionScore] = []
    combined_zero: list[PredictionScore] = []
    combined_global: list[PredictionScore] = []

    for fold_name, train_context, test_context in FOLDS:
        print(f"evaluating {fold_name} ...", flush=True)
        train, test = _fold_rows(dataset, train_context, test_context, common_ids)
        global_mean = masked_gene_mean(dataset, train)
        means = filled_perturbation_mean_map(dataset, train, global_mean)
        test_perturbation_mean, test_seen = perturbation_mean_predictions(
            dataset, test, means, global_mean
        )
        if not test_seen.all():
            raise ValueError("test perturbation coverage is not complete")
        centered = test_perturbation_mean - global_mean
        del test_perturbation_mean

        scores: dict[str, PredictionScore] = {}
        summaries: dict[str, dict[str, Any]] = {}
        for name, prediction in _predictions(global_mean, centered):
            score = _score(dataset, test, prediction)
            scores[name] = score
            summaries[name] = score.summary()
        del prediction

        sensitivity: dict[str, Any] = {}
        for name, prediction in _sensitivity_predictions(global_mean, centered):
            score = _score(dataset, test, prediction)
            sensitivity[name] = score.summary()
        del prediction

        candidate_score = scores["scaled_transfer_beta0.25"]
        zero_score = scores["zero"]
        global_score = scores["global_mean"]
        candidate = summaries["scaled_transfer_beta0.25"]
        zero = summaries["zero"]
        global_summary = summaries["global_mean"]

        bootstrap = {
            "scaled_transfer_beta0.25": {
                "vs_zero": paired_bootstrap_delta(
                    zero_score,
                    candidate_score,
                    resamples=args.bootstrap_resamples,
                    seed=args.seed,
                ),
                "vs_global_mean": paired_bootstrap_delta(
                    global_score,
                    candidate_score,
                    resamples=args.bootstrap_resamples,
                    seed=args.seed,
                ),
            },
            "unscaled_perturbation_mean": {
                "vs_zero": paired_bootstrap_delta(
                    zero_score,
                    scores["unscaled_perturbation_mean"],
                    resamples=args.bootstrap_resamples,
                    seed=args.seed,
                ),
                "vs_global_mean": paired_bootstrap_delta(
                    global_score,
                    scores["unscaled_perturbation_mean"],
                    resamples=args.bootstrap_resamples,
                    seed=args.seed,
                ),
            },
            "centered_perturbation_mean": {
                "vs_zero": paired_bootstrap_delta(
                    zero_score,
                    scores["centered_perturbation_mean"],
                    resamples=args.bootstrap_resamples,
                    seed=args.seed,
                ),
                "vs_global_mean": paired_bootstrap_delta(
                    global_score,
                    scores["centered_perturbation_mean"],
                    resamples=args.bootstrap_resamples,
                    seed=args.seed,
                ),
            },
        }

        # Training-only top-quartile subset: no test labels are used to select it.
        train_effect = np.asarray(
            [
                np.nanmean(
                    np.abs(
                        np.asarray(dataset.lfc[row][dataset.mask[row]], dtype=np.float64)
                    )
                )
                for row in train
            ],
            dtype=np.float64,
        )
        threshold = float(np.nanquantile(train_effect, 0.75))
        strong_perturbations = {
            int(perturbation)
            for perturbation, effect in zip(
                dataset.perturbations[train], train_effect, strict=True
            )
            if effect >= threshold
        }
        strong_mask = np.asarray(
            [
                int(perturbation) in strong_perturbations
                for perturbation in dataset.perturbations[test]
            ],
            dtype=bool,
        )
        strong_rows = test[strong_mask]
        strong_summary = {
            name: _score(dataset, strong_rows, prediction[strong_mask]).summary()
            for name, prediction in _predictions(global_mean, centered)
        }

        # Common-support subset: genes tested in both the training row for the
        # same perturbation and the test row.
        train_row_by_perturbation = {
            int(perturbation): int(row)
            for row, perturbation in zip(
                train, dataset.perturbations[train], strict=True
            )
        }
        support = dataset.mask[
            np.asarray(
                [
                    train_row_by_perturbation[int(perturbation)]
                    for perturbation in dataset.perturbations[test]
                ],
                dtype=np.int64,
            )
        ]
        support_summary = {
            name: _score(
                dataset, test, prediction, support=support
            ).summary()
            for name, prediction in _predictions(global_mean, centered)
        }

        # Negative control: shuffle the training effect vectors across test
        # perturbations. The real matching should beat this null if the signal
        # is perturbation-specific rather than a global-mean artefact.
        rng = np.random.default_rng(args.seed)
        permutation_scores: list[dict[str, Any]] = []
        for _ in range(PERMUTATIONS):
            permutation = rng.permutation(test.size)
            permuted = np.asarray(centered[permutation], dtype=np.float64)
            prediction = global_mean + FIXED_BETA * permuted
            summary = _score(dataset, test, prediction).summary()
            permutation_scores.append(
                {
                    "mean_row_rmse": summary["mean_row_rmse"],
                    "median_row_correlation": summary["median_row_correlation"],
                    "mean_top_k_overlap": summary["mean_top_k_overlap"],
                }
            )
        permutation_rmse = np.asarray(
            [item["mean_row_rmse"] for item in permutation_scores],
            dtype=np.float64,
        )
        permutation_percentile = float(
            np.mean(permutation_rmse <= candidate["mean_row_rmse"])
        )

        gate = _fold_gate(
            candidate,
            zero,
            global_summary,
            bootstrap["scaled_transfer_beta0.25"]["vs_zero"],
            beta=FIXED_BETA,
        )
        fold_results[fold_name] = {
            "fold": fold_name,
            "train_context": train_context,
            "test_context": test_context,
            "rows": {"train": int(train.size), "test": int(test.size)},
            "perturbations": {
                "common": int(common_ids.size),
                "train": int(np.unique(dataset.perturbations[train]).size),
                "test": int(np.unique(dataset.perturbations[test]).size),
                "test_coverage": float(test_seen.mean()),
            },
            "gene_support": {
                "test_tested_genes": int(
                    np.asarray(dataset.mask[test].sum(axis=1)).sum()
                ),
                "train_tested_genes": int(
                    np.asarray(dataset.tested[train].sum(axis=1)).sum()
                ),
                "common_support_genes": int(
                    np.asarray((dataset.mask[test] & support).sum(axis=1)).sum()
                ),
            },
            "beta": {
                "fixed": FIXED_BETA,
                "grid": list(BETA_GRID),
                "selection": "fixed from the prior Replogle-Nadig gate; not tuned on Orion",
            },
            "metrics": {
                "zero": zero,
                "global_mean": global_summary,
                "unscaled_perturbation_mean": summaries["unscaled_perturbation_mean"],
                "centered_perturbation_mean": summaries[
                    "centered_perturbation_mean"
                ],
                "scaled_transfer_beta0.25": candidate,
            },
            "diagnostics": {
                "candidate_rmse_quantiles": _quantiles(candidate_score.row_rmse),
                "zero_rmse_quantiles": _quantiles(zero_score.row_rmse),
                "global_rmse_quantiles": _quantiles(global_score.row_rmse),
                "fraction_rows_candidate_better_than_zero": _fraction_better(
                    candidate_score.row_rmse, zero_score.row_rmse
                ),
                "fraction_rows_candidate_better_than_global": _fraction_better(
                    candidate_score.row_rmse, global_score.row_rmse
                ),
                "top_k_delta_vs_zero": float(
                    (candidate["mean_top_k_overlap"] or 0.0)
                    - (zero["mean_top_k_overlap"] or 0.0)
                ),
                "top_k_delta_vs_global": float(
                    (candidate["mean_top_k_overlap"] or 0.0)
                    - (global_summary["mean_top_k_overlap"] or 0.0)
                ),
            },
            "bootstrap": bootstrap,
            "sensitivity_betas": sensitivity,
            "secondary": {
                "top_quartile_training_effect": {
                    "threshold_mean_abs_lfc": threshold,
                    "perturbations": len(strong_perturbations),
                    "rows": int(strong_rows.size),
                    "metrics": strong_summary,
                },
                "common_support": {
                    "rows": int(test.size),
                    "metrics": support_summary,
                },
                "permutation_control": {
                    "permutations": PERMUTATIONS,
                    "seed": args.seed,
                    "candidate_mean_row_rmse": candidate["mean_row_rmse"],
                    "permutation_mean_row_rmse_mean": float(
                        np.mean(permutation_rmse)
                    ),
                    "permutation_mean_row_rmse_ci95": [
                        float(value)
                        for value in np.quantile(permutation_rmse, [0.025, 0.975])
                    ],
                    "candidate_percentile": permutation_percentile,
                    "scores": permutation_scores,
                },
            },
            "gate": gate,
        }
        combined_candidate.append(candidate_score)
        combined_zero.append(zero_score)
        combined_global.append(global_score)

    combined_candidate_score = _combine_scores(combined_candidate)
    combined_zero_score = _combine_scores(combined_zero)
    combined_global_score = _combine_scores(combined_global)
    combined = {
        "rows": int(combined_candidate_score.row_mse.size),
        "metrics": {
            "zero": combined_zero_score.summary(),
            "global_mean": combined_global_score.summary(),
            "scaled_transfer_beta0.25": combined_candidate_score.summary(),
        },
        "bootstrap": {
            "vs_zero": paired_bootstrap_delta(
                combined_zero_score,
                combined_candidate_score,
                resamples=args.bootstrap_resamples,
                seed=args.seed,
            ),
            "vs_global_mean": paired_bootstrap_delta(
                combined_global_score,
                combined_candidate_score,
                resamples=args.bootstrap_resamples,
                seed=args.seed,
            ),
        },
    }
    aggregate = _aggregate_gate(fold_results)

    payload = {
        "dataset": "PIE X-Atlas/Orion genome-wide CRISPRi Perturb-seq (HCT116, HEK293T)",
        "source": "https://huggingface.co/datasets/arcinstitute/PIE_x_atlas_orion",
        "repo_commit": "abfa3da0f3bb98c9df9c90082386ed0c7c9282d3",
        "preregistration": (
            "docs/experiments/2026-11-07-orion-unseen-context-preregistration.md"
        ),
        "code": "scripts/perturbation/benchmark_orion_transfer.py",
        "commit": args.commit,
        "license": "CC BY-NC-SA 4.0",
        "license_note": (
            "Orion is released under CC BY-NC-SA 4.0. This run is research-only; "
            "it is not evidence for commercial use."
        ),
        "fixed_beta": FIXED_BETA,
        "beta_grid": list(BETA_GRID),
        "common_perturbations": int(common_ids.size),
        "common_names_sha256": common_digest,
        "bootstrap_resamples": args.bootstrap_resamples,
        "seed": args.seed,
        "folds": fold_results,
        "combined": combined,
        "gate": aggregate,
        "interpretation": (
            "Independent dataset-level replication of CRISPRi Perturb-seq "
            "cell-line transfer. It is not unseen-perturbation, single-cell, "
            "dose/time, cross-assay or prospective evidence."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(
        "\nfold                     beta  zero RMSE  cand RMSE  rel gain  "
        "median r  global r  top50   global top50  numeric  ranking"
    )
    for fold_name, _train, _test in FOLDS:
        result = fold_results[fold_name]
        candidate = result["metrics"]["scaled_transfer_beta0.25"]
        zero = result["metrics"]["zero"]
        global_summary = result["metrics"]["global_mean"]
        gate = result["gate"]
        print(
            f"{fold_name:<24} {FIXED_BETA:>4.2f}  "
            f"{_fmt(zero['mean_row_rmse']):>9}  "
            f"{_fmt(candidate['mean_row_rmse']):>9}  "
            f"{gate['relative_improvement']:>8.2%}  "
            f"{_fmt(candidate['median_row_correlation'], 3):>8}  "
            f"{_fmt(global_summary['median_row_correlation'], 3):>8}  "
            f"{_fmt(candidate['mean_top_k_overlap'], 4):>6}  "
            f"{_fmt(global_summary['mean_top_k_overlap'], 4):>12}  "
            f"{'yes' if gate['numeric_pass'] else 'no':>7}  "
            f"{'yes' if gate['ranking_pass'] else 'no':>7}"
        )
    print(
        f"\nnumeric transfer: {'PASS' if aggregate['numeric_replicated'] else 'FAIL'} "
        f"({len(aggregate['numeric_passing_folds'])}/{aggregate['required_folds']} folds)"
    )
    print(
        f"ranking: {'PASS' if aggregate['ranking_replicated'] else 'FAIL'} "
        f"({len(aggregate['ranking_passing_folds'])}/{aggregate['required_folds']} folds)"
    )
    print(f"verdict: {aggregate['verdict']}")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
