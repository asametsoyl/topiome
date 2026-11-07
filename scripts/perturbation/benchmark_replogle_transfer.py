"""Run the pre-registered Replogle-Nadig unseen-context transfer gate.

The protocol is frozen in
``docs/experiments/2026-11-07-replogle-unseen-context-preregistration.md``.
K562 is reported separately because it was inspected before the protocol was
written; only HepG2, Jurkat and RPE1 count toward the gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from analysis.perturbation import (
    DEFAULT_BETAS,
    evaluate_gate,
    evaluate_unseen_context_fold,
    load_pie_dataset,
)

CONFIRMATORY_FOLDS = ("hepg2", "jurkat", "rpe1")
EXPLORATORY_FOLDS = ("k562",)


def _fmt(value: float | None, digits: int = 4) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


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
        "--output",
        type=Path,
        default=Path("data/perturbation/processed/replogle-unseen-ctx-gate.json"),
    )
    parser.add_argument(
        "--folds",
        default=",".join(CONFIRMATORY_FOLDS + EXPLORATORY_FOLDS),
        help="Comma-separated folds to evaluate.",
    )
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261107)
    parser.add_argument("--commit", default=None)
    args = parser.parse_args()

    folds = tuple(fold.strip() for fold in args.folds.split(",") if fold.strip())
    unknown = set(folds) - set(CONFIRMATORY_FOLDS + EXPLORATORY_FOLDS)
    if unknown:
        raise SystemExit(f"Unknown folds: {sorted(unknown)}")

    dataset = load_pie_dataset(args.data_dir)
    results: dict[str, dict[str, Any]] = {}
    for fold in folds:
        print(f"evaluating {fold} ...", flush=True)
        results[fold] = evaluate_unseen_context_fold(
            dataset,
            args.split_dir,
            fold,
            betas=DEFAULT_BETAS,
            resamples=args.bootstrap_resamples,
            seed=args.seed,
        )

    confirmatory = tuple(fold for fold in CONFIRMATORY_FOLDS if fold in results)
    gate = evaluate_gate(results, confirmatory)

    payload = {
        "dataset": "PIE Replogle-Nadig essential Perturb-seq (4 cell lines)",
        "source": "https://huggingface.co/datasets/arcinstitute/PIE_replogle_nadig_essential",
        "splits": "https://huggingface.co/datasets/arcinstitute/PIE_splits",
        "preregistration": (
            "docs/experiments/2026-11-07-replogle-unseen-context-preregistration.md"
        ),
        "code": "scripts/perturbation/benchmark_replogle_transfer.py",
        "commit": args.commit,
        "license_note": (
            "The Hugging Face dataset card has no license field. Original Replogle et al. "
            "2022 and Nadig et al. 2025 data; commercial-use terms are not verified. This "
            "run is research-only."
        ),
        "confirmatory_folds": list(confirmatory),
        "exploratory_folds": [fold for fold in folds if fold in EXPLORATORY_FOLDS],
        "bootstrap_resamples": args.bootstrap_resamples,
        "seed": args.seed,
        "gate": gate,
        "folds": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("\nfold       beta   zero RMSE   model RMSE   rel. gain   median r   top50 Δ   pass")
    for fold in folds:
        result = results[fold]
        candidate = result["test"]["scaled_transfer"]
        zero = result["test"]["zero"]
        checks = result["gate"]
        top_k_delta = (candidate["mean_top_k_overlap"] or 0.0) - (
            zero["mean_top_k_overlap"] or 0.0
        )
        print(
            f"{fold:<10} {result['beta']['scaled_transfer']:>4.2f}   "
            f"{_fmt(zero['mean_row_rmse']):>9}   {_fmt(candidate['mean_row_rmse']):>10}   "
            f"{checks['relative_improvement']:>8.2%}   "
            f"{_fmt(candidate['median_row_correlation'], 3):>8}   "
            f"{top_k_delta:>8.3f}   "
            f"{'yes' if checks['passes'] else 'no'}"
        )

    print(
        f"\nconfirmatory gate: {'PASS' if gate['passed'] else 'FAIL'} "
        f"({gate['n_passing']}/{len(confirmatory)} folds passed; need 2)"
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
