from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.metrics import compute_metrics


def test_perfect_recovery_scores_zero_divergence():
    index = [f"spot-{i}" for i in range(40)]
    truth = pd.DataFrame(
        {
            "tumor": np.linspace(0.2, 0.8, 40),
            "immune": np.linspace(0.3, 0.1, 40),
        },
        index=index,
    )
    truth["stroma"] = 1.0 - truth.sum(axis=1)
    zones = np.array([0] * 20 + [1] * 20)
    domains = np.array([0] * 20 + [1] * 20)

    metrics = compute_metrics(truth, truth, domains, zones)

    assert metrics["composition"]["jsd_mean"] == 0.0
    assert metrics["composition"]["rmse"] == 0.0
    assert metrics["composition"]["dominant_type_pearson"] == 1.0
    assert metrics["domains"]["ari"] == 1.0
    assert metrics["domains"]["nmi"] == 1.0
    assert "Synthetic ground truth" in metrics["note"]


def test_permuted_domains_score_below_perfect():
    index = [f"spot-{i}" for i in range(20)]
    truth = pd.DataFrame({"a": [1.0] * 20, "b": [0.0] * 20}, index=index)
    zones = np.array([0] * 10 + [1] * 10)
    domains = np.array([0, 1] * 10)

    metrics = compute_metrics(truth, truth, domains, zones)

    assert metrics["composition"]["jsd_mean"] == 0.0
    assert metrics["domains"]["ari"] < 1.0
