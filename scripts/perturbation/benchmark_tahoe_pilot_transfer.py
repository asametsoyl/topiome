"""Pre-registered confirmatory test of pilot-calibrated context transfer on Tahoe-100M.

Pre-registration: docs/experiments/2026-11-08-tahoe-pilot-transfer-preregistration.md
This script and that document are committed before ``lfc_true.npy`` of
PIE_tahoe100m is downloaded. Method, pilot size, pairs, seed and decision rule
are fixed below and must not change after the labels are opened.

Usage (repository root):
    PYTHONPATH=packages/analysis apps/api/.venv/bin/python \\
        scripts/perturbation/benchmark_tahoe_pilot_transfer.py --commit "$(git rev-parse --short HEAD)"
"""

from __future__ import annotations

import argparse
import hashlib
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
DATA = ROOT / "data" / "perturbation" / "raw" / "pie-tahoe100m" / "preprocessed"
OUT = ROOT / "data" / "perturbation" / "processed" / "tahoe-pilot-transfer-gate.json"

# ── Frozen protocol ──────────────────────────────────────────────────────────
PILOT_SIZE = 100
SEED = 20261108
PRIMARY = "pilot_scaled_transfer"
COMPARATOR = "pilot_mean"
SECONDARY = ("zero", "zero_shot_beta025", "pilot_lowrank_ridge")
MIN_SHARE_PAIRS_BETTER = 0.70
MIN_MEDIAN_RELATIVE_GAIN = 0.01
MAX_SHARE_PAIRS_HARMED = 0.10  # transfer worse than pilot mean by > 1% RMSE
HARM_MARGIN = 0.01
BOOTSTRAP_RESAMPLES = 2000


def ordered_pairs(context_names: tuple[str, ...]) -> list[tuple[str, str]]:
    """Each context once as source and once as target: sorted names, cyclic shift by one."""
    names = sorted(context_names)
    return [(names[i], names[(i + 1) % len(names)]) for i in range(len(names))]


def pairs_sha256(pairs: list[tuple[str, str]]) -> str:
    return hashlib.sha256("\n".join(f"{s}->{t}" for s, t in pairs).encode()).hexdigest()


def compound(condition: str) -> str:
    """'(S)-Crizotinib_0.5uM' → '(S)-Crizotinib' (dose suffix removed)."""
    return condition.rsplit("_", 1)[0]


def bootstrap_median_ci(values: np.ndarray, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    medians = [
        float(np.median(rng.choice(values, size=values.size, replace=True)))
        for _ in range(BOOTSTRAP_RESAMPLES)
    ]
    low, high = np.percentile(medians, [2.5, 97.5])
    return float(low), float(high)


def decide(per_pair: list[dict]) -> dict:
    gain = np.array([p["relative_rmse_gain"] for p in per_pair])
    corr_gain = np.array(
        [p["correlation_gain"] for p in per_pair if p["correlation_gain"] is not None]
    )
    low, high = bootstrap_median_ci(gain, SEED)
    checks = {
        "share_pairs_better": float(np.mean(gain > 0)),
        "median_relative_rmse_gain": float(np.median(gain)),
        "median_gain_ci95": [low, high],
        "median_correlation_gain": float(np.median(corr_gain)) if corr_gain.size else None,
        "share_pairs_harmed": float(np.mean(gain < -HARM_MARGIN)),
    }
    passed = {
        "1_share_pairs_better": checks["share_pairs_better"] >= MIN_SHARE_PAIRS_BETTER,
        "2_median_gain": checks["median_relative_rmse_gain"] >= MIN_MEDIAN_RELATIVE_GAIN,
        "3_median_gain_ci_above_zero": low > 0,
        "4_correlation_gain_positive": (checks["median_correlation_gain"] or 0) > 0,
        "5_no_harm": checks["share_pairs_harmed"] <= MAX_SHARE_PAIRS_HARMED,
    }
    return {"checks": checks, "passed": passed, "decision": "passed" if all(passed.values()) else "failed"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--dry-run", action="store_true", help="validate structure without labels")
    parser.add_argument("--data-dir", type=Path, default=DATA, help="tests only")
    parser.add_argument("--out", type=Path, default=OUT, help="tests only")
    args = parser.parse_args()

    if args.dry_run:
        meta = json.loads((args.data_dir / "meta.json").read_text())
        names = tuple(sorted(meta["context_to_id"], key=meta["context_to_id"].get))
        pairs = ordered_pairs(names)
        print(f"{len(pairs)} pairs, sha256 {pairs_sha256(pairs)}")
        print(pairs[:3], "…", pairs[-1])
        return

    started = time.perf_counter()
    dataset = load_pie_dataset(args.data_dir)
    pairs = ordered_pairs(dataset.context_names)
    root_seed = np.random.SeedSequence(SEED)
    per_pair = []
    for index, ((source, target), child) in enumerate(zip(pairs, root_seed.spawn(len(pairs)), strict=True)):
        source_id, target_id = dataset.context_to_id[source], dataset.context_to_id[target]
        subset = pair_subset(dataset, source_id, target_id)
        pair = pair_rows(subset, source_id, target_id)
        pilot, held = draw_pilot(len(pair.perturbations), PILOT_SIZE, np.random.default_rng(child))
        predictions, params = predict_pair(subset, pair, pilot, held)
        rows = pair.target[held]
        truth, tested = subset.lfc[rows], subset.tested[rows]
        row_scores = {
            method: score_rows_fast(truth, tested, predictions[method])
            for method in (PRIMARY, COMPARATOR, *SECONDARY)
        }
        del predictions
        summary = {method: summarize_rows(scores) for method, scores in row_scores.items()}
        # Descriptive only: test conditions whose compound has no dose in the pilot.
        names = dataset.perturbation_names
        pilot_compounds = {compound(names[p]) for p in pair.perturbations[pilot]}
        unseen = np.array(
            [compound(names[p]) not in pilot_compounds for p in pair.perturbations[held]]
        )
        unseen_compound = {
            method: summarize_rows({k: v[unseen] for k, v in row_scores[method].items()})
            for method in (PRIMARY, COMPARATOR)
        } if unseen.any() else None
        primary, comparator = summary[PRIMARY], summary[COMPARATOR]
        correlation_gain = (
            primary["median_row_correlation"] - comparator["median_row_correlation"]
            if primary["median_row_correlation"] is not None
            and comparator["median_row_correlation"] is not None
            else None
        )
        per_pair.append(
            {
                "pair": f"{source}->{target}",
                "common_perturbations": int(len(pair.perturbations)),
                "held_out_rows": int(len(held)),
                "fitted": params,
                "scores": summary,
                "unseen_compound_rows": int(unseen.sum()),
                "unseen_compound_scores": unseen_compound,
                "relative_rmse_gain": 1 - primary["mean_row_rmse"] / comparator["mean_row_rmse"],
                "correlation_gain": correlation_gain,
            }
        )
        print(f"[{index + 1}/{len(pairs)}] {source}->{target} beta={params['beta']:.3f} "
              f"gain={per_pair[-1]['relative_rmse_gain'] * 100:.2f}%", flush=True)

    result = {
        "preregistration": "docs/experiments/2026-11-08-tahoe-pilot-transfer-preregistration.md",
        "commit": args.commit,
        "created": datetime.now(UTC).isoformat(),
        "dataset": "arcinstitute/PIE_tahoe100m@0d5089a2b4f13239383f135ef8e2db2462a00808",
        "protocol": {
            "pilot_size": PILOT_SIZE,
            "seed": SEED,
            "primary": PRIMARY,
            "comparator": COMPARATOR,
            "pairs_sha256": pairs_sha256(pairs),
        },
        "gate": decide(per_pair),
        "pairs": per_pair,
        "runtime_seconds": round(time.perf_counter() - started, 1),
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["gate"], indent=2))


if __name__ == "__main__":
    main()
