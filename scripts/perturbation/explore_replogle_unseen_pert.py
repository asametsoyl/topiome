"""Exploratory check for the unseen-perturbation setting.

This is **not** a pre-registered gate. It asks whether simple target-gene
features (ESM2 protein embeddings, STRING network space, DepMap gene effect)
give a ridge or k-NN model any clear advantage over the context-mean baseline
when the test perturbations are absent from training.

The PIE ``unseen_pert`` split is used as published. Hyperparameters are chosen
on the supplied validation rows only; the test rows are scored once. Because
the validation rows come from seen perturbations, validation-based selection is
a limitation, not evidence of unseen-perturbation generalisation.

The PIE knowledge-source cards have no license field. This script is
research-only and its output must not be used for a commercial claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from analysis.perturbation import (
    load_pie_dataset,
    load_split_rows,
    masked_gene_mean,
    paired_bootstrap_delta,
    score_predictions,
)
from sklearn.linear_model import Ridge
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

SOURCE_NAMES = ("esm2", "string_space", "depmap_gene_effect")
RIDGE_ALPHAS = (0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)
KNN_NEIGHBOURS = (5, 10, 25, 50, 100)


def _load_aliases(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {
        str(key): str(value)
        for key, value in payload.items()
        if value not in (None, "")
    }


def load_feature_block(source_dir: Path, perturbation_names: tuple[str, ...]) -> np.ndarray:
    """Load one PIE knowledge-source block aligned to the perturbation vocabulary."""
    meta = json.loads((source_dir / "meta.json").read_text(encoding="utf-8"))
    embeddings = np.load(source_dir / "embeddings.npy")
    keys = [str(key) for key in meta["keys"]]
    index = {key: position for position, key in enumerate(keys)}
    aliases = _load_aliases(source_dir / "aliases.yaml")
    block = np.full(
        (len(perturbation_names), int(meta["dim"])), np.nan, dtype=np.float32
    )
    for row, name in enumerate(perturbation_names):
        key = name if name in index else aliases.get(name)
        if key is not None and key in index:
            block[row] = np.asarray(embeddings[index[key]], dtype=np.float32)
    if not np.isfinite(block).any():
        raise ValueError(f"{source_dir.name} has no overlap with the perturbation vocabulary")
    return block


def impute_from_training(
    blocks: dict[str, np.ndarray], train_perturbations: np.ndarray
) -> dict[str, np.ndarray]:
    """Fill missing feature values with training-perturbation column means."""
    imputed: dict[str, np.ndarray] = {}
    for name, block in blocks.items():
        filled = block.copy()
        columns = np.nanmean(filled[train_perturbations], axis=0)
        columns = np.where(np.isfinite(columns), columns, 0.0)
        missing = np.where(~np.isfinite(filled))
        filled[missing] = np.take(columns, missing[1])
        imputed[name] = filled
    return imputed


def context_offsets(
    dataset: Any, train_rows: np.ndarray, global_mean: np.ndarray
) -> dict[int, np.ndarray]:
    offsets: dict[int, np.ndarray] = {}
    for context in np.unique(dataset.contexts[train_rows]):
        rows = train_rows[dataset.contexts[train_rows] == context]
        offsets[int(context)] = masked_gene_mean(dataset, rows) - global_mean
    return offsets


def add_context(
    dataset: Any, rows: np.ndarray, predictions: np.ndarray, offsets: dict[int, np.ndarray]
) -> np.ndarray:
    output = predictions.copy()
    for position, row in enumerate(rows):
        offset = offsets.get(int(dataset.contexts[row]))
        if offset is not None:
            output[position] += offset
    return output


def evaluate(
    dataset: Any,
    rows: np.ndarray,
    predictions: np.ndarray,
    context_baseline: Any,
    *,
    resamples: int,
    seed: int,
) -> dict[str, Any]:
    score = score_predictions(dataset, rows, predictions)
    summary = score.summary()
    summary["bootstrap_vs_context"] = paired_bootstrap_delta(
        context_baseline, score, resamples=resamples, seed=seed
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/perturbation/raw/pie-replogle-nadig-essential/preprocessed"),
    )
    parser.add_argument(
        "--split-dir",
        type=Path,
        default=Path("data/perturbation/raw/pie-splits"),
    )
    parser.add_argument(
        "--sources-dir",
        type=Path,
        default=Path("data/perturbation/raw/pie-sources"),
    )
    parser.add_argument("--fold", default="k562")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/perturbation/processed/replogle-unseen-pert-exploratory.json"),
    )
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261107)
    parser.add_argument("--commit", default=None)
    args = parser.parse_args()

    dataset = load_pie_dataset(args.data_dir)
    train = load_split_rows(dataset, args.split_dir, "unseen_pert", args.fold, "train")
    validation = load_split_rows(dataset, args.split_dir, "unseen_pert", args.fold, "val")
    test = load_split_rows(dataset, args.split_dir, "unseen_pert", args.fold, "test")

    train_perturbations = np.unique(dataset.perturbations[train]).astype(int)
    test_perturbations = set(int(value) for value in np.unique(dataset.perturbations[test]))
    if test_perturbations & set(int(value) for value in train_perturbations):
        raise ValueError("unseen_pert test perturbation leaked into training")

    global_mean = masked_gene_mean(dataset, train)
    offsets = context_offsets(dataset, train, global_mean)

    perturbation_targets = np.empty(
        (train_perturbations.size, dataset.lfc.shape[1]), dtype=np.float64
    )
    for position, perturbation in enumerate(train_perturbations):
        rows = train[dataset.perturbations[train] == perturbation]
        perturbation_targets[position] = masked_gene_mean(dataset, rows)
    perturbation_targets -= global_mean

    blocks = {
        name: load_feature_block(args.sources_dir / name, dataset.perturbation_names)
        for name in SOURCE_NAMES
    }
    missing = {name: int(np.isnan(block).any(axis=1).sum()) for name, block in blocks.items()}
    blocks = impute_from_training(blocks, train_perturbations)

    scalers = {
        name: StandardScaler().fit(block[train_perturbations])
        for name, block in blocks.items()
    }
    scaled = {name: scalers[name].transform(block) for name, block in blocks.items()}
    combined_scaler = StandardScaler().fit(
        np.concatenate([blocks[name][train_perturbations] for name in SOURCE_NAMES], axis=1)
    )
    combined = combined_scaler.transform(
        np.concatenate([blocks[name] for name in SOURCE_NAMES], axis=1)
    )

    def base_prediction(rows: np.ndarray, model_effect: np.ndarray) -> np.ndarray:
        return add_context(
            dataset,
            rows,
            np.broadcast_to(global_mean, (rows.size, global_mean.size)) + model_effect,
            offsets,
        )

    zero = np.zeros((test.size, global_mean.size))
    global_prediction = np.broadcast_to(global_mean, zero.shape).copy()
    context_prediction = add_context(dataset, test, global_prediction.copy(), offsets)
    context_score = score_predictions(dataset, test, context_prediction)
    validation_context = add_context(
        dataset,
        validation,
        np.broadcast_to(global_mean, (validation.size, global_mean.size)).copy(),
        offsets,
    )
    validation_context_summary = score_predictions(
        dataset, validation, validation_context
    ).summary()

    results: dict[str, Any] = {
        "dataset": "PIE Replogle-Nadig essential Perturb-seq (4 cell lines)",
        "source": "https://huggingface.co/datasets/arcinstitute/PIE_replogle_nadig_essential",
        "splits": "https://huggingface.co/datasets/arcinstitute/PIE_splits",
        "sources": "https://huggingface.co/datasets/arcinstitute/PIE_sources",
        "code": "scripts/perturbation/explore_replogle_unseen_pert.py",
        "commit": args.commit,
        "license_note": (
            "PIE and PIE_sources dataset cards have no license field. The original "
            "studies are public, but commercial-use terms are not verified. This run "
            "is research-only."
        ),
        "bootstrap_resamples": args.bootstrap_resamples,
        "seed": args.seed,
        "selection": "validation mean row RMSE",
        "fold": args.fold,
        "setting": "unseen_pert",
        "rows": {
            "train": int(train.size),
            "validation": int(validation.size),
            "test": int(test.size),
        },
        "train_perturbations": int(train_perturbations.size),
        "test_perturbations": int(len(test_perturbations)),
        "missing_feature_rows": missing,
        "validation_note": (
            "The published validation rows come from seen perturbations; alpha and k "
            "selection on them is a limitation of this exploratory check."
        ),
        "baselines": {
            "zero": score_predictions(dataset, test, zero).summary(),
            "global_mean": score_predictions(dataset, test, global_prediction).summary(),
            "context_mean": context_score.summary(),
            "context_mean_validation": validation_context_summary,
        },
        "models": {},
    }

    def record(
        name: str,
        validation_predictions: np.ndarray,
        test_predictions: np.ndarray,
        metadata: dict[str, Any],
    ) -> None:
        validation_score = score_predictions(dataset, validation, validation_predictions)
        test_score = score_predictions(dataset, test, test_predictions)
        results["models"][name] = {
            **metadata,
            "validation": validation_score.summary(),
            "test": test_score.summary(),
            "bootstrap_vs_context": paired_bootstrap_delta(
                context_score,
                test_score,
                resamples=args.bootstrap_resamples,
                seed=args.seed,
            ),
        }

    for k in KNN_NEIGHBOURS:
        neighbours = NearestNeighbors(n_neighbors=k).fit(combined[train_perturbations])

        def knn_effect(
            rows: np.ndarray, neighbours: NearestNeighbors = neighbours
        ) -> np.ndarray:
            row_distances, row_indices = neighbours.kneighbors(
                combined[dataset.perturbations[rows]]
            )
            weights = 1.0 / (row_distances + 1e-6)
            weights /= weights.sum(axis=1, keepdims=True)
            return np.einsum("nk,nkg->ng", weights, perturbation_targets[row_indices])

        record(
            f"knn_k{k}",
            base_prediction(validation, knn_effect(validation)),
            base_prediction(test, knn_effect(test)),
            {"model": "knn", "k": k, "features": list(SOURCE_NAMES)},
        )

    for alphas, label, matrix in (
        (RIDGE_ALPHAS, "ridge_all", combined),
        *((RIDGE_ALPHAS, f"ridge_{name}", scaled[name]) for name in SOURCE_NAMES),
    ):
        for alpha in alphas:
            model = Ridge(alpha=alpha, solver="svd", fit_intercept=False).fit(
                matrix[train_perturbations], perturbation_targets
            )
            record(
                f"{label}_alpha{alpha:g}",
                base_prediction(validation, matrix[dataset.perturbations[validation]] @ model.coef_.T),
                base_prediction(test, matrix[dataset.perturbations[test]] @ model.coef_.T),
                {"model": "ridge", "alpha": alpha, "features": label.removeprefix("ridge_")},
            )

    # Rank model families by validation mean row RMSE, then report the selected
    # candidate's test score. This is exploratory model selection only.
    selected: dict[str, str] = {}
    for family in ("knn", "ridge_all", *[f"ridge_{name}" for name in SOURCE_NAMES]):
        candidates = {
            name: payload
            for name, payload in results["models"].items()
            if payload["model"] == family.split("_")[0]
            and (
                family == payload["model"]
                or payload.get("features") == family.removeprefix("ridge_")
            )
        }
        if candidates:
            selected[family] = min(
                candidates,
                key=lambda name: candidates[name]["validation"]["mean_row_rmse"],
            )
    results["selected_by_validation"] = selected

    # Descriptive verdict only; this is not a pre-registered success rule.
    # Never pick a model by its test score: the primary candidate is the
    # validation-selected model with the lowest validation row RMSE.
    primary_name = min(
        selected,
        key=lambda family: results["models"][selected[family]]["validation"][
            "mean_row_rmse"
        ],
    )
    primary_model = results["models"][selected[primary_name]]
    relative = (
        context_score.summary()["mean_row_rmse"] - primary_model["test"]["mean_row_rmse"]
    ) / context_score.summary()["mean_row_rmse"]
    results["primary_candidate"] = {
        "family": primary_name,
        "model": selected[primary_name],
        "relative_improvement_over_context": float(relative),
        "beats_context_on_rmse": bool(relative > 0),
        "beats_context_on_correlation": bool(
            primary_model["test"]["median_row_correlation"]
            >= (context_score.summary()["median_row_correlation"] or 0.0)
        ),
        "beats_context_on_top_k": bool(
            primary_model["test"]["mean_top_k_overlap"]
            >= (context_score.summary()["mean_top_k_overlap"] or 0.0)
        ),
        "bootstrap_ci_above_zero": bool(
            primary_model["bootstrap_vs_context"]["ci95"][0] > 0
        ),
    }
    results["clear_advantage"] = bool(
        relative >= 0.03
        and results["primary_candidate"]["beats_context_on_correlation"]
        and results["primary_candidate"]["beats_context_on_top_k"]
        and results["primary_candidate"]["bootstrap_ci_above_zero"]
    )
    results["interpretation"] = (
        "Exploratory only. A clear advantage requires >=3% relative row-RMSE gain, "
        "no loss in median correlation or top-50 overlap, and a paired bootstrap "
        "interval above zero versus the context-mean baseline. The primary candidate "
        "is selected on validation rows only."
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    print("model                         val RMSE   test RMSE   rel. gain   median r   top50")
    for name, payload in sorted(
        results["models"].items(), key=lambda item: item[1]["test"]["mean_row_rmse"]
    ):
        test_summary = payload["test"]
        print(
            f"{name:28} {payload['validation']['mean_row_rmse']:>8.4f} "
            f"{test_summary['mean_row_rmse']:>10.4f} "
            f"{(context_score.summary()['mean_row_rmse'] - test_summary['mean_row_rmse']) / context_score.summary()['mean_row_rmse']:>+9.2%} "
            f"{test_summary['median_row_correlation']:>10.3f} "
            f"{test_summary['mean_top_k_overlap']:>7.4f}"
        )
    print("\nbaselines (test)")
    for name, summary in results["baselines"].items():
        if name.endswith("_validation"):
            continue
        print(
            f"{name:28} {summary['mean_row_rmse']:>8.4f} {summary['mean_row_rmse']:>10.4f} "
            f"{0.0:>+9.2%} {summary['median_row_correlation'] or 0.0:>10.3f} "
            f"{summary['mean_top_k_overlap'] or 0.0:>7.4f}"
        )
    print(
        f"\nvalidation context-mean RMSE: "
        f"{validation_context_summary['mean_row_rmse']:.4f}"
    )
    print(
        f"primary (validation-selected): {selected[primary_name]} "
        f"({relative:+.2%} vs context mean)"
    )
    print(
        "  beats context on RMSE / correlation / top-50 / bootstrap CI: "
        f"{results['primary_candidate']['beats_context_on_rmse']} / "
        f"{results['primary_candidate']['beats_context_on_correlation']} / "
        f"{results['primary_candidate']['beats_context_on_top_k']} / "
        f"{results['primary_candidate']['bootstrap_ci_above_zero']}"
    )
    print(f"clear advantage: {'yes' if results['clear_advantage'] else 'no'}")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
