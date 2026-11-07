"""The frozen Tahoe script runs end to end on a synthetic PIE directory."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "perturbation" / "benchmark_tahoe_pilot_transfer.py"


def _write_pie(directory: Path, n_contexts: int = 3, n_conditions: int = 160, n_genes: int = 30) -> None:
    rng = np.random.default_rng(0)
    contexts = [f"CVCL_{i:04d}" for i in range(n_contexts)]
    conditions = [f"Drug{c // 3}_{[0.05, 0.5, 5.0][c % 3]}uM" for c in range(n_conditions)]
    latent = rng.normal(size=(n_conditions, n_genes))
    rows, ctx_ids, pert_ids = [], [], []
    for ci in range(n_contexts):
        offset = rng.normal(size=n_genes)
        for pi in range(n_conditions):
            rows.append(offset + 0.5 * latent[pi] + rng.normal(scale=0.2, size=n_genes))
            ctx_ids.append(ci)
            pert_ids.append(pi)
    lfc = np.asarray(rows, dtype=np.float32)
    np.save(directory / "lfc_true.npy", lfc)
    np.save(directory / "tested.npy", np.ones_like(lfc, dtype=bool))
    np.save(directory / "ctx_ids.npy", np.asarray(ctx_ids))
    np.save(directory / "pert_ids.npy", np.asarray(pert_ids))
    meta = {
        "num_rows": lfc.shape[0],
        "num_genes": n_genes,
        "num_contexts": n_contexts,
        "num_perts": n_conditions,
        "genes": [f"G{j}" for j in range(n_genes)],
        "context_to_id": {name: i for i, name in enumerate(contexts)},
        "pert_to_id": {name: i for i, name in enumerate(conditions)},
    }
    (directory / "meta.json").write_text(json.dumps(meta))


def test_gate_script_runs_and_reports_a_decision(tmp_path: Path):
    _write_pie(tmp_path)
    out = tmp_path / "gate.json"
    env_path = str(ROOT / "packages" / "analysis")
    subprocess.run(
        [sys.executable, str(SCRIPT), "--commit", "test", "--data-dir", str(tmp_path), "--out", str(out)],
        check=True,
        env={"PYTHONPATH": env_path, "PATH": "/usr/bin:/bin"},
        capture_output=True,
    )
    result = json.loads(out.read_text())
    assert len(result["pairs"]) == 3
    assert result["gate"]["decision"] in {"passed", "failed"}
    assert set(result["gate"]["passed"]) == {
        "1_share_pairs_better",
        "2_median_gain",
        "3_median_gain_ci_above_zero",
        "4_correlation_gain_positive",
        "5_no_harm",
    }
    first = result["pairs"][0]
    assert first["held_out_rows"] == 160 - 100
    assert "unseen_compound_rows" in first
    # The synthetic data carry a shared signal, so transfer should beat the pilot mean.
    assert all(p["relative_rmse_gain"] > 0 for p in result["pairs"])
