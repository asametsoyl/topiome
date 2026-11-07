"""Development run for pilot (few-shot) context transfer.

DEVELOPMENT ONLY. Replogle-Nadig and X-Atlas/Orion test labels were opened in
earlier experiments, so nothing here is a confirmatory result. This run is used
to choose one method and one pilot size, which are then frozen in a
pre-registration and tested once on a dataset that has never been opened.

Usage (repository root):
    PYTHONPATH=packages/analysis apps/api/.venv/bin/python \\
        scripts/perturbation/develop_pilot_transfer.py --commit "$(git rev-parse --short HEAD)"
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from analysis.perturbation import load_pie_dataset
from analysis.pilot_transfer import (
    draw_pilot,
    pair_rows,
    pair_subset,
    predict_pair,
    score_rows_fast,
    summarize_rows,
)

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "perturbation" / "raw"
DATASETS = {
    "replogle_nadig": RAW / "pie-replogle-nadig-essential" / "preprocessed",
    "x_atlas_orion": RAW / "pie-x-atlas-orion" / "preprocessed",
}
PILOT_SIZES = (25, 50, 100, 200)
DRAWS = 3
SEED = 20261108
METHODS = ("zero", "pilot_mean", "zero_shot_beta025", "pilot_scaled_transfer", "pilot_lowrank_ridge")


def _mean_or_none(values: list) -> float | None:
    """Mean over draws; None when undefined (e.g. correlation of a constant prediction)."""
    finite = [float(v) for v in values if v is not None and np.isfinite(v)]
    return float(np.mean(finite)) if finite else None


def run_pair(full, name: str, source: int, target: int, rng: np.random.Generator) -> dict:
    dataset = pair_subset(full, source, target)
    pair = pair_rows(dataset, source, target)
    n = len(pair.perturbations)
    label = f"{dataset.context_names[source]}->{dataset.context_names[target]}"
    result = {"pair": label, "common_perturbations": n, "by_pilot_size": {}}
    for k in PILOT_SIZES:
        if k >= n - 50:
            continue
        draws = []
        for _ in range(DRAWS):
            pilot, held = draw_pilot(n, k, rng)
            predictions, params = predict_pair(dataset, pair, pilot, held)
            rows = pair.target[held]
            truth, tested = dataset.lfc[rows], dataset.tested[rows]
            scores = {
                method: summarize_rows(score_rows_fast(truth, tested, predictions[method]))
                for method in METHODS
            }
            del predictions
            draws.append({"params": params, "scores": scores})
        summary = {}
        for method in METHODS:
            summary[method] = {
                metric: _mean_or_none([d["scores"][method][metric] for d in draws])
                for metric in ("mean_row_rmse", "median_row_correlation", "mean_top_k_overlap")
            }
        summary["fitted"] = {
            "beta_mean": float(np.mean([d["params"]["beta"] for d in draws])),
            "ridge_lambda_median": float(np.median([d["params"]["ridge_lambda"] for d in draws])),
        }
        result["by_pilot_size"][str(k)] = summary
        print(f"  {name} {label} k={k}: "
              + ", ".join(f"{m}={summary[m]['mean_row_rmse']:.4f}" for m in METHODS), flush=True)
    return result


def overview(results: list[dict]) -> dict:
    """Share of pairs where each method beats the pilot mean, per pilot size."""
    out: dict[str, dict] = {}
    for k in PILOT_SIZES:
        rows = [r["by_pilot_size"][str(k)] for r in results if str(k) in r["by_pilot_size"]]
        if not rows:
            continue
        entry = {"pairs": len(rows)}
        for method in ("pilot_scaled_transfer", "pilot_lowrank_ridge", "zero_shot_beta025", "zero"):
            rmse_gain = [
                1 - row[method]["mean_row_rmse"] / row["pilot_mean"]["mean_row_rmse"] for row in rows
            ]
            corr_gain = [
                row[method]["median_row_correlation"] - row["pilot_mean"]["median_row_correlation"]
                for row in rows
                if row[method]["median_row_correlation"] is not None
                and row["pilot_mean"]["median_row_correlation"] is not None
            ]
            entry[method] = {
                "median_relative_rmse_gain_vs_pilot_mean": float(np.median(rmse_gain)),
                "share_pairs_better_rmse": float(np.mean([g > 0 for g in rmse_gain])),
                "median_correlation_gain_vs_pilot_mean": (
                    float(np.median(corr_gain)) if corr_gain else None
                ),
            }
        out[str(k)] = entry
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", default=None)
    args = parser.parse_args()
    rng = np.random.default_rng(SEED)
    started = time.perf_counter()
    report = {
        "status": "development_only",
        "note": "Test labels of these datasets were opened before; not confirmatory.",
        "created": datetime.now(UTC).isoformat(),
        "commit": args.commit,
        "seed": SEED,
        "pilot_sizes": PILOT_SIZES,
        "draws": DRAWS,
        "datasets": {},
    }
    for name, path in DATASETS.items():
        dataset = load_pie_dataset(path)
        contexts = sorted(int(c) for c in np.unique(dataset.contexts))
        results = [
            run_pair(dataset, name, s, t, rng) for s, t in itertools.permutations(contexts, 2)
        ]
        report["datasets"][name] = {"pairs": results, "overview": overview(results)}
        print(json.dumps(report["datasets"][name]["overview"], indent=2), flush=True)
    report["runtime_seconds"] = round(time.perf_counter() - started, 1)
    out = ROOT / "data" / "perturbation" / "processed" / "pilot-transfer-development.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {out} in {report['runtime_seconds']}s")


if __name__ == "__main__":
    main()
