"""Spatial ligand–receptor communication (ported from Glio-Cartography stage 4).

For each curated pair the score combines

* autocrine / same-spot co-localization: mean(sender · receiver)
* paracrine / neighbour signal: mean(sender · W·receiver)

where ``sender = p(sender cell type) · ligand expression`` and
``receiver = p(receiver cell type) · receptor expression`` and ``W`` is the
row-normalised spatial kNN graph. Significance comes from a spatial
permutation null that shuffles the receiver signal across spots while the
sender signal stays in place, so a pair is significant only when sender and
receiver signals sit together (same spot or neighbours) more than chance.
Benjamini–Hochberg correction is applied across pairs.

Glio-Cartography permuted cell-type proportions instead; that null is liberal
because the ligand is usually expressed by the sender cell type itself, which
the shuffle breaks, so almost every expressed pair came out "significant".

Scores are co-expression evidence, not proof of signalling.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.neighbors import NearestNeighbors


def spatial_graph(coordinates: np.ndarray, k: int = 6) -> sparse.csr_matrix:
    """Row-normalised kNN adjacency (self excluded)."""
    n = len(coordinates)
    if n < 2:
        return sparse.csr_matrix((n, n))
    k = max(1, min(k, n - 1))
    nn = NearestNeighbors(n_neighbors=k + 1).fit(coordinates)
    _, indices = nn.kneighbors(coordinates)
    rows = np.repeat(np.arange(n), k)
    cols = indices[:, 1:].reshape(-1)
    data = np.full(len(rows), 1.0 / k)
    return sparse.csr_matrix((data, (rows, cols)), shape=(n, n))


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    """BH-adjusted q-values, same order as the input."""
    if not p_values:
        return []
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    ranked = p[order] * len(p) / (np.arange(len(p)) + 1)
    q_sorted = np.minimum.accumulate(ranked[::-1])[::-1]
    q = np.empty_like(q_sorted)
    q[order] = np.clip(q_sorted, 0, 1)
    return [float(v) for v in q]


def _score(sender: np.ndarray, receiver: np.ndarray, graph: sparse.csr_matrix) -> float:
    autocrine = float(np.mean(sender * receiver))
    paracrine = float(np.mean(sender * (graph @ receiver)))
    return autocrine + paracrine


def score_ligand_receptor(
    expression: pd.DataFrame,
    composition: pd.DataFrame,
    coordinates: np.ndarray,
    domains: np.ndarray,
    pairs: list[dict[str, Any]],
    *,
    barcodes: list[str] | None = None,
    k: int = 6,
    n_permutations: int = 199,
    seed: int = 42,
    min_domain_spots: int = 10,
) -> list[dict[str, Any]]:
    """Score curated ligand–receptor pairs on log-normalised expression.

    ``expression`` and ``composition`` must share the same spot order as
    ``coordinates`` and ``domains``. Pairs whose genes or cell types are
    missing are returned with ``tested: False`` so the gap stays visible.
    """
    if not pairs:
        return []
    genes = {g.upper(): g for g in expression.columns}
    graph = spatial_graph(coordinates, k=k)
    rng = np.random.default_rng(seed)
    n = len(expression)
    permutations = [rng.permutation(n) for _ in range(n_permutations)]
    domains = np.asarray(domains).astype(str)
    domain_ids = [d for d in dict.fromkeys(domains) if (domains == d).sum() >= min_domain_spots]

    results: list[dict[str, Any]] = []
    for pair in pairs:
        ligand = str(pair["ligand"]).upper()
        receptor = str(pair["receptor"]).upper()
        sender_type = pair.get("sender")
        receiver_type = pair.get("receiver")
        base = {
            "id": f"{ligand}_{receptor}",
            "name": pair.get("name") or f"{ligand} → {receptor}",
            "ligand": ligand,
            "receptor": receptor,
            "sender": sender_type,
            "receiver": receiver_type,
            "category": pair.get("category", ""),
        }
        missing = [g for g in (ligand, receptor) if g not in genes]
        missing += [
            ct for ct in (sender_type, receiver_type) if ct not in composition.columns
        ]
        if missing:
            results.append(
                {**base, "tested": False, "missing": missing, "score": None, "p_value": None}
            )
            continue

        ligand_expr = expression[genes[ligand]].to_numpy(dtype=float)
        receptor_expr = expression[genes[receptor]].to_numpy(dtype=float)
        p_sender = composition[sender_type].to_numpy(dtype=float)
        p_receiver = composition[receiver_type].to_numpy(dtype=float)

        sender = p_sender * ligand_expr
        receiver = p_receiver * receptor_expr
        observed = _score(sender, receiver, graph)
        spot_contribution = sender * (receiver + graph @ receiver)

        exceed = 0
        for perm in permutations:
            if _score(sender, receiver[perm], graph) >= observed:
                exceed += 1
        p_value = (exceed + 1) / (n_permutations + 1)

        by_domain = {}
        for domain_id in domain_ids:
            mask = domains == domain_id
            neighbour = (graph @ receiver)[mask]
            by_domain[domain_id] = round(
                float(np.mean(sender[mask] * receiver[mask]) + np.mean(sender[mask] * neighbour)),
                6,
            )

        results.append(
            {
                **base,
                "tested": True,
                "missing": [],
                "score": round(observed, 6),
                "p_value": round(p_value, 6),
                "ligand_detected_fraction": round(float((ligand_expr > 0).mean()), 4),
                "receptor_detected_fraction": round(float((receptor_expr > 0).mean()), 4),
                "spot_scores": {
                    barcode: round(float(value), 8)
                    for barcode, value in zip(
                        barcodes or [str(index) for index in range(n)],
                        spot_contribution,
                        strict=True,
                    )
                },
                "by_domain": by_domain,
                "top_domain": max(by_domain, key=by_domain.get) if by_domain else None,
            }
        )

    tested = [r for r in results if r["tested"]]
    q_values = benjamini_hochberg([r["p_value"] for r in tested])
    for record, q in zip(tested, q_values, strict=True):
        record["q_value"] = round(q, 6)
        record["significant"] = q < 0.05
    for record in results:
        record.setdefault("q_value", None)
        record.setdefault("significant", False)

    results.sort(
        key=lambda r: (not r["tested"], r["q_value"] if r["q_value"] is not None else 1.0, -(r["score"] or 0))
    )
    return results
