from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors


def smooth_composition(
    composition: pd.DataFrame,
    coordinates: np.ndarray,
    *,
    k: int = 6,
    alpha: float = 0.45,
) -> pd.DataFrame:
    """Smooth cell-type weights over a spatial kNN graph."""
    n = len(composition)
    if n < 3:
        return composition.copy()
    k = min(k, n - 1)
    nn = NearestNeighbors(n_neighbors=k + 1).fit(coordinates)
    _, indices = nn.kneighbors(coordinates)
    values = composition.to_numpy(dtype=float)
    smoothed = np.zeros_like(values)
    for i in range(n):
        neighbors = indices[i, 1:]
        smoothed[i] = (1 - alpha) * values[i] + alpha * values[neighbors].mean(axis=0)
    smoothed = np.clip(smoothed, 0, None)
    smoothed = smoothed / np.clip(smoothed.sum(axis=1, keepdims=True), 1e-8, None)
    return pd.DataFrame(smoothed, index=composition.index, columns=composition.columns)


def _zone_marker_scores(expression: pd.DataFrame, pack: dict) -> pd.DataFrame:
    values = expression.to_numpy(dtype=float)
    means = values.mean(axis=0)
    stds = values.std(axis=0)
    stds[stds == 0] = 1.0
    z = (values - means) / stds
    gene_index = {g: i for i, g in enumerate(expression.columns)}
    rows: dict[str, np.ndarray] = {}
    for zone in pack.get("zones", []):
        idx = [gene_index[g] for g in zone.get("markers", []) if g in gene_index]
        rows[zone["id"]] = z[:, idx].mean(axis=1) if idx else np.zeros(len(expression))
    return pd.DataFrame(rows, index=expression.index)


def assign_domains(
    composition_smooth: pd.DataFrame,
    coordinates: np.ndarray,
    expression: pd.DataFrame,
    pack: dict,
    *,
    random_state: int = 42,
) -> tuple[np.ndarray, list[str], np.ndarray, pd.DataFrame]:
    """Cluster spots into spatial domains and label each cluster by zone markers."""
    n = len(composition_smooth)
    zones = pack.get("zones", [])
    n_domains = max(2, min(len(zones), n // 25 if n >= 50 else n))
    n_domains = min(n_domains, n)

    coords = np.asarray(coordinates, dtype=float)
    span = np.ptp(coords, axis=0)
    span[span == 0] = 1.0
    coords_scaled = (coords - coords.min(axis=0)) / span

    features = np.hstack(
        [
            composition_smooth.to_numpy(dtype=float) * 2.0,
            coords_scaled * 0.15,
        ]
    )
    kmeans = KMeans(n_clusters=n_domains, random_state=random_state, n_init=10)
    cluster_ids = kmeans.fit_predict(features)

    zone_scores = _zone_marker_scores(expression, pack)
    cluster_zone_scores = zone_scores.groupby(cluster_ids, observed=True).mean()
    zone_ids = [z["id"] for z in zones]
    zone_names = {z["id"]: z["name"] for z in zones}

    assigned: dict[int, str] = {}
    used: set[str] = set()
    for cluster in range(n_domains):
        if cluster not in cluster_zone_scores.index:
            assigned[cluster] = "unassigned"
            continue
        scores = cluster_zone_scores.loc[cluster]
        ordered = [z for z in scores.sort_values(ascending=False).index if z in zone_ids]
        choice = next((z for z in ordered if z not in used), None)
        if choice is None:
            choice = ordered[0] if ordered else zone_ids[0]
        assigned[cluster] = choice
        used.add(choice)

    domain_ids = np.array([assigned[int(c)] for c in cluster_ids], dtype=object)
    names = [zone_names.get(str(d), str(d)) for d in domain_ids]
    return domain_ids, names, cluster_ids, zone_scores
