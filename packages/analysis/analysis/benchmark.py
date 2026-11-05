"""Synthetic pseudospot benchmark CLI.

Usage (from apps/api, where the analysis package is installed):

    uv run python -m analysis.benchmark --pack breast
    uv run python -m analysis.benchmark --pack all --out data/benchmarks

The benchmark generates synthetic spots with known composition and zones,
runs the same pipeline used in production, and compares the result against
pre-registered minimum and target gates (docs/VALIDATION.md).

This is a numerical-recovery check. It is not clinical validation and it
does not replace held-out real-data validation.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from . import __version__
from .pipeline import PIPELINE_VERSION, run_pipeline
from .synthetic import generate_demo_dataset

MINIMUM_GATES = {
    "jsd_mean": 0.20,
    "dominant_type_pearson": 0.75,
    "ari": 0.35,
}

TARGET_GATES = {
    "jsd_mean": 0.12,
    "dominant_type_pearson": 0.85,
    "ari": 0.55,
}

# Lower is better for JSD; higher is better for the other two.
LOWER_IS_BETTER = {"jsd_mean"}


def _default_packs_dir() -> Path:
    # analysis/benchmark.py -> analysis -> packages/analysis -> packages -> repo root
    return Path(__file__).resolve().parents[2] / "disease-packs"


def load_pack(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        pack = yaml.safe_load(handle)
    if not isinstance(pack, dict) or "id" not in pack:
        raise ValueError(f"{path.name}: not a valid disease pack")
    return pack


def discover_packs(packs_dir: Path) -> dict[str, dict[str, Any]]:
    packs: dict[str, dict[str, Any]] = {}
    for path in sorted(packs_dir.glob("*.yaml")):
        if path.name.startswith("._"):
            continue
        pack = load_pack(path)
        packs[pack["id"]] = pack
    return packs


def _score(value: float | None, gate: float, lower_is_better: bool) -> str:
    if value is None:
        return "fail"
    passed = value <= gate if lower_is_better else value >= gate
    return "pass" if passed else "fail"


def benchmark_pack(
    pack: dict[str, Any],
    *,
    n_spots: int = 1200,
    seed: int = 42,
) -> dict[str, Any]:
    dataset, signatures, ground_truth = generate_demo_dataset(
        pack, n_spots=n_spots, seed=seed
    )
    dataset.ground_truth = ground_truth
    result = run_pipeline(
        dataset, pack, signatures=signatures, params={"random_state": seed}
    )

    metrics = result.metrics or {}
    composition = metrics.get("composition", {})
    domains = metrics.get("domains", {})
    observed = {
        "jsd_mean": composition.get("jsd_mean"),
        "rmse": composition.get("rmse"),
        "dominant_type_pearson": composition.get("dominant_type_pearson"),
        "ari": domains.get("ari"),
        "nmi": domains.get("nmi"),
    }

    checks: dict[str, dict[str, Any]] = {}
    minimum_pass = True
    target_pass = True
    for key, gate in MINIMUM_GATES.items():
        lower = key in LOWER_IS_BETTER
        minimum = _score(observed.get(key), gate, lower)
        target = _score(observed.get(key), TARGET_GATES[key], lower)
        minimum_pass = minimum_pass and minimum == "pass"
        target_pass = target_pass and target == "pass"
        checks[key] = {
            "value": observed.get(key),
            "minimum_gate": gate,
            "target_gate": TARGET_GATES[key],
            "minimum": minimum,
            "target": target,
        }

    return {
        "pack": pack["id"],
        "pack_version": pack.get("version"),
        "dataset": "synthetic",
        "n_spots": int(n_spots),
        "seed": seed,
        "pipeline_version": PIPELINE_VERSION,
        "analysis_version": __version__,
        "method": result.summary.get("method"),
        "n_domains": result.summary.get("n_domains"),
        "metrics": observed,
        "checks": checks,
        "minimum_pass": minimum_pass,
        "target_pass": target_pass,
        "warnings": result.warnings,
        "note": metrics.get(
            "note", "Synthetic ground truth; not a substitute for real-data validation."
        ),
    }


def _print_table(results: list[dict[str, Any]]) -> None:
    header = (
        f"{'pack':<14} {'JSD':>7} {'r':>7} {'ARI':>7} "
        f"{'min':>5} {'target':>7} {'method':<13}"
    )
    print(header)
    print("-" * len(header))
    for item in results:
        metrics = item["metrics"]
        print(
            f"{item['pack']:<14} "
            f"{metrics.get('jsd_mean') or float('nan'):>7.3f} "
            f"{metrics.get('dominant_type_pearson') or float('nan'):>7.3f} "
            f"{metrics.get('ari') or float('nan'):>7.3f} "
            f"{'PASS' if item['minimum_pass'] else 'FAIL':>5} "
            f"{'PASS' if item['target_pass'] else 'FAIL':>7} "
            f"{item['method'] or '-':<13}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the synthetic pseudospot benchmark for one or all disease packs."
    )
    parser.add_argument(
        "--pack",
        action="append",
        default=None,
        help="Pack id (repeatable) or 'all'. Default: all.",
    )
    parser.add_argument(
        "--packs-dir",
        type=Path,
        default=None,
        help="Directory containing disease pack YAML files.",
    )
    parser.add_argument("--spots", type=int, default=1200, help="Synthetic spots per pack.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory. Writes metrics.json and manifest.json.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only write files; do not print the summary table.",
    )
    args = parser.parse_args(argv)

    packs_dir = args.packs_dir or _default_packs_dir()
    if not packs_dir.is_dir():
        parser.error(f"packs directory not found: {packs_dir}")

    available = discover_packs(packs_dir)
    if not available:
        parser.error(f"no disease packs found in {packs_dir}")

    requested = args.pack or ["all"]
    if "all" in requested:
        selected = list(available.values())
    else:
        missing = [pack_id for pack_id in requested if pack_id not in available]
        if missing:
            parser.error(f"unknown pack(s): {', '.join(missing)}")
        selected = [available[pack_id] for pack_id in requested]

    results = [
        benchmark_pack(pack, n_spots=args.spots, seed=args.seed) for pack in selected
    ]

    if not args.quiet:
        _print_table(results)

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "pipeline_version": PIPELINE_VERSION,
        "analysis_version": __version__,
        "spots_per_pack": args.spots,
        "seed": args.seed,
        "results": results,
    }

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "metrics.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )
        manifest = {
            key: payload[key]
            for key in (
                "generated_at",
                "python",
                "platform",
                "pipeline_version",
                "analysis_version",
                "spots_per_pack",
                "seed",
            )
        }
        manifest["packs"] = [
            {
                "id": item["pack"],
                "version": item["pack_version"],
                "minimum_pass": item["minimum_pass"],
                "target_pass": item["target_pass"],
            }
            for item in results
        ]
        (args.out / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        if not args.quiet:
            print(f"\nwrote {args.out / 'metrics.json'}")
            print(f"wrote {args.out / 'manifest.json'}")

    failed = [item["pack"] for item in results if not item["minimum_pass"]]
    if failed:
        print(
            f"\nMINIMUM GATES FAILED: {', '.join(failed)}. "
            "Do not mark these packs as validated.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
