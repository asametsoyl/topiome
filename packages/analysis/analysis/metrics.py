from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score


def compute_metrics(
    composition: pd.DataFrame,
    ground_truth_composition: pd.DataFrame,
    domain_ids: np.ndarray,
    ground_truth_zones: np.ndarray,
) -> dict:
    """Benchmark metrics against synthetic ground truth."""
    cell_types = sorted(set(composition.columns) | set(ground_truth_composition.columns))
    est = composition.reindex(columns=cell_types, fill_value=0).to_numpy(dtype=float)
    truth = ground_truth_composition.reindex(
        columns=cell_types, fill_value=0
    ).to_numpy(dtype=float)
    # Align spot order.
    common = composition.index.intersection(ground_truth_composition.index)
    est = composition.loc[common].reindex(columns=cell_types, fill_value=0).to_numpy(float)
    truth = ground_truth_composition.loc[common].reindex(
        columns=cell_types, fill_value=0
    ).to_numpy(float)

    est_norm = est / np.clip(est.sum(axis=1, keepdims=True), 1e-8, None)
    truth_norm = truth / np.clip(truth.sum(axis=1, keepdims=True), 1e-8, None)

    jsd = float(
        np.mean([jensenshannon(est_norm[i], truth_norm[i], base=2) for i in range(len(est_norm))])
    )
    rmse = float(np.sqrt(np.mean((est_norm - truth_norm) ** 2)))

    est_dom = np.argmax(est_norm, axis=1)
    truth_dom = np.argmax(truth_norm, axis=1)
    pearson = float(np.corrcoef(est_dom, truth_dom)[0, 1]) if len(est_dom) > 2 else 0.0
    if not np.isfinite(pearson):
        pearson = 0.0

    zone_mask = np.isin(ground_truth_zones, list(set(ground_truth_zones)))
    ari = float(adjusted_rand_score(ground_truth_zones[zone_mask], domain_ids[zone_mask]))
    nmi = float(
        normalized_mutual_info_score(ground_truth_zones[zone_mask], domain_ids[zone_mask])
    )

    return {
        "n_spots": int(len(common)),
        "composition": {
            "jsd_mean": round(jsd, 4),
            "rmse": round(rmse, 4),
            "dominant_type_pearson": round(pearson, 4),
        },
        "domains": {
            "ari": round(ari, 4),
            "nmi": round(nmi, 4),
        },
        "note": "Synthetic ground truth; not a substitute for held-out real-data validation.",
    }
