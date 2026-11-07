"""Run simple target-held-out baselines on Arc VCC 2025 PIE aggregate effects.

This is an exploratory population-level benchmark, not a single-cell predictor.
The supplied ARC_H1_VAL split holds perturbation targets out within the same
H1 hESC cell line; it is not a held-out biological context.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def _pearson_per_row(truth: np.ndarray, prediction: np.ndarray, mask: np.ndarray) -> list[float]:
    scores: list[float] = []
    for true_row, pred_row, row_mask in zip(truth, prediction, mask, strict=True):
        true_values = true_row[row_mask]
        pred_values = pred_row[row_mask]
        if true_values.size < 2 or np.std(true_values) == 0 or np.std(pred_values) == 0:
            continue
        score = float(np.corrcoef(true_values, pred_values)[0, 1])
        if np.isfinite(score):
            scores.append(score)
    return scores


def _score(truth: np.ndarray, prediction: np.ndarray, mask: np.ndarray) -> dict[str, Any]:
    residual = (prediction - truth)[mask]
    correlations = _pearson_per_row(truth, prediction, mask)
    per_target_rmse: list[float] = []
    per_target_mae: list[float] = []
    top_k = min(50, truth.shape[1])
    overlaps: list[float] = []
    for true_row, pred_row, row_mask in zip(truth, prediction, mask, strict=True):
        indices = np.flatnonzero(row_mask)
        if indices.size == 0:
            continue
        row_residual = pred_row[indices] - true_row[indices]
        per_target_rmse.append(float(np.sqrt(np.mean(np.square(row_residual)))))
        per_target_mae.append(float(np.mean(np.abs(row_residual))))
        k = min(top_k, indices.size)
        true_top = set(indices[np.argpartition(np.abs(true_row[indices]), -k)[-k:]].tolist())
        pred_top = set(indices[np.argpartition(np.abs(pred_row[indices]), -k)[-k:]].tolist())
        overlaps.append(len(true_top & pred_top) / k)
    return {
        "mae_log2_fold_change": float(np.mean(np.abs(residual))),
        "rmse_log2_fold_change": float(np.sqrt(np.mean(np.square(residual)))),
        "mean_per_perturbation_rmse_log2_fold_change": float(np.mean(per_target_rmse)),
        "mean_per_perturbation_mae_log2_fold_change": float(np.mean(per_target_mae)),
        "median_per_perturbation_gene_correlation": (
            float(np.median(correlations)) if correlations else None
        ),
        "mean_top_50_absolute_effect_overlap": float(np.mean(overlaps)),
        "perturbations_scored": int(truth.shape[0]),
        "measured_effects_scored": int(mask.sum()),
    }


def run(data_dir: Path) -> dict[str, Any]:
    metadata = json.loads((data_dir / "meta.json").read_text())
    contexts = np.load(data_dir / "ctx_ids.npy")
    perturbations = np.load(data_dir / "pert_ids.npy")
    truth_all = np.load(data_dir / "lfc_true.npy", mmap_mode="r")
    tested_all = np.load(data_dir / "tested.npy", mmap_mode="r")

    train_context = metadata["context_to_id"]["ARC_H1"]
    validation_context = metadata["context_to_id"]["ARC_H1_VAL"]
    train_rows = np.flatnonzero(contexts == train_context)
    validation_rows = np.flatnonzero(contexts == validation_context)
    if not train_rows.size or not validation_rows.size:
        raise ValueError("Expected non-empty ARC_H1 training and ARC_H1_VAL validation rows")

    train_targets = set(perturbations[train_rows].tolist())
    validation_targets = set(perturbations[validation_rows].tolist())
    overlap = train_targets & validation_targets
    if overlap:
        raise ValueError(f"Perturbation leakage between train and validation: {sorted(overlap)}")

    train_truth = np.asarray(truth_all[train_rows], dtype=np.float64)
    train_mask = np.asarray(tested_all[train_rows], dtype=bool) & np.isfinite(train_truth)
    validation_truth = np.asarray(truth_all[validation_rows], dtype=np.float64)
    validation_mask = np.asarray(tested_all[validation_rows], dtype=bool) & np.isfinite(validation_truth)

    # Only training perturbations contribute to the per-gene mean baseline.
    counts = train_mask.sum(axis=0)
    sums = np.where(train_mask, train_truth, 0.0).sum(axis=0)
    training_mean = np.divide(sums, counts, out=np.zeros_like(sums), where=counts > 0)
    zero_prediction = np.zeros_like(validation_truth)
    mean_prediction = np.broadcast_to(training_mean, validation_truth.shape).copy()

    target_rmse_delta = []
    for true_row, mask_row, mean_row in zip(validation_truth, validation_mask, mean_prediction, strict=True):
        observed = true_row[mask_row]
        target_rmse_delta.append(
            float(np.sqrt(np.mean(np.square(mean_row[mask_row] - observed)))
                  - np.sqrt(np.mean(np.square(observed))))
        )
    deltas = np.asarray(target_rmse_delta, dtype=np.float64)
    rng = np.random.default_rng(20261107)
    sampled = rng.choice(deltas, size=(5000, deltas.size), replace=True).mean(axis=1)

    perturbation_names = {index: name for name, index in metadata["pert_to_id"].items()}
    validation_target_names = [perturbation_names[int(i)] for i in perturbations[validation_rows]]
    return {
        "dataset": "Arc VCC 2025 PIE-preprocessed aggregate effects",
        "cell_line": "H1 hESC (CVCL_9771)",
        "task": "held-out perturbation targets within the same cell line",
        "not_assessed": ["held-out cell contexts", "single-cell response distributions", "prospective experiments"],
        "split": {
            "train_context_label": "ARC_H1",
            "validation_context_label": "ARC_H1_VAL",
            "train_targets": int(len(train_targets)),
            "validation_targets": int(len(validation_targets)),
            "target_overlap": int(len(overlap)),
            "validation_target_names": validation_target_names,
        },
        "genes": int(metadata["num_genes"]),
        "metrics": {
            "zero_effect": _score(validation_truth, zero_prediction, validation_mask),
            "training_mean_effect_per_gene": _score(validation_truth, mean_prediction, validation_mask),
            "paired_target_bootstrap_rmse_delta_vs_zero": {
                "mean_delta_log2_fold_change": float(np.mean(deltas)),
                "percentile_95_ci": [float(x) for x in np.quantile(sampled, [0.025, 0.975])],
                "unit": "validation perturbation target",
                "seed": 20261107,
                "resamples": int(sampled.size),
            },
        },
        "interpretation": "Exploratory baselines on supplied pseudobulk log2 fold changes; no model-selection or product claim.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/perturbation/raw/arc-vcc-2025-pie"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/perturbation/processed/vcc-pie-baseline-metrics.json"),
    )
    args = parser.parse_args()
    result = run(args.data_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
