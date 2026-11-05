"""Independent external-atlas correspondence check (ported from Glio-Cartography).

Compares the mean expression of a small reference gene panel in each predicted
domain with an external, independently measured atlas (for glioblastoma: Ivy
GAP ISH expression per anatomic structure, Puchalski et al. 2018). Both sides
are z-scored per gene across zones, then correlated zone-by-structure.

This is a sanity signal, not ground truth: different patients, different
technology and a small gene panel. Negative results are reported as-is.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _zscore_columns(matrix: np.ndarray) -> np.ndarray:
    mean = np.nanmean(matrix, axis=0, keepdims=True)
    std = np.nanstd(matrix, axis=0, keepdims=True)
    return (matrix - mean) / (std + 1e-8)


def atlas_correspondence(
    expression: pd.DataFrame,
    domains: np.ndarray,
    atlas: dict[str, Any],
    *,
    exclude_genes: set[str] | None = None,
    min_spots: int = 5,
    min_genes: int = 4,
) -> dict[str, Any]:
    """Correlate predicted zones with atlas structures.

    ``atlas`` is the pack's ``atlas_reference`` block with resolved ``data``:
    ``{"zone_map": {zone_id: structure}, "data": {"genes": {GENE: {structure: value}}}}``.
    ``exclude_genes`` should hold the genes used to label zones, so the check
    stays independent of how zones were assigned.
    """
    excluded = {g.upper() for g in (exclude_genes or set())}
    zone_map: dict[str, str] = atlas.get("zone_map", {})
    reference_genes: dict[str, dict[str, float | None]] = (atlas.get("data") or {}).get("genes", {})
    structures = list(dict.fromkeys(zone_map.values()))
    base = {
        "name": atlas.get("name", "External atlas"),
        "citation": atlas.get("citation", ""),
        "structures": structures,
        "zones": list(zone_map.keys()),
    }
    if not zone_map or not reference_genes:
        return {**base, "status": "unavailable", "reason": "Pack has no atlas reference data."}

    genes = {g.upper(): g for g in expression.columns}
    panel = [
        g
        for g, values in reference_genes.items()
        if g.upper() in genes
        and g.upper() not in excluded
        and all(values.get(s) is not None for s in structures)
    ]
    excluded_hits = sorted(g for g in reference_genes if g.upper() in excluded)
    base["excluded_genes"] = excluded_hits
    if len(panel) < min_genes:
        return {
            **base,
            "status": "insufficient_genes",
            "reason": f"Only {len(panel)} atlas genes measured in this sample (need {min_genes}).",
            "n_genes": len(panel),
        }

    domains = np.asarray(domains).astype(str)
    zones = list(zone_map.keys())
    zone_spots = {z: int((domains == z).sum()) for z in zones}
    ours = np.full((len(zones), len(panel)), np.nan)
    for i, zone in enumerate(zones):
        mask = domains == zone
        if mask.sum() < min_spots:
            continue
        ours[i] = [float(expression.loc[mask, genes[g.upper()]].mean()) for g in panel]

    covered = [i for i in range(len(zones)) if not np.all(np.isnan(ours[i]))]
    if len(covered) < 2:
        return {
            **base,
            "status": "insufficient_zones",
            "reason": "Fewer than two mapped zones have enough spots for comparison.",
            "n_genes": len(panel),
            "zone_spots": zone_spots,
        }

    reference = np.array(
        [[float(reference_genes[g][s]) for g in panel] for s in structures], dtype=float
    )
    reference_z = _zscore_columns(reference)
    ours_z = ours.copy()
    ours_z[covered] = _zscore_columns(ours[covered])

    corr = np.full((len(zones), len(structures)), np.nan)
    for i in covered:
        for j in range(len(structures)):
            a, b = ours_z[i], reference_z[j]
            mask = ~np.isnan(a) & ~np.isnan(b)
            if mask.sum() >= min_genes and np.std(a[mask]) > 0 and np.std(b[mask]) > 0:
                corr[i, j] = float(np.corrcoef(a[mask], b[mask])[0, 1])

    structure_index = {s: j for j, s in enumerate(structures)}
    diagonal, matches, total = [], 0, 0
    for i in covered:
        j = structure_index[zone_map[zones[i]]]
        if not np.isnan(corr[i, j]):
            diagonal.append(corr[i, j])
        row = corr[i]
        if not np.all(np.isnan(row)):
            total += 1
            matches += int(np.nanargmax(row) == j)

    return {
        **base,
        "status": "ok",
        "n_genes": len(panel),
        "genes": panel,
        "zone_spots": zone_spots,
        "correlation": [
            [None if np.isnan(v) else round(float(v), 4) for v in row] for row in corr
        ],
        "diagonal_mean": round(float(np.mean(diagonal)), 4) if diagonal else None,
        "top1_accuracy": round(matches / total, 4) if total else None,
        "n_zones_compared": total,
        "note": (
            "Independent atlas from different patients and a different technology "
            f"(n={len(panel)} genes). A reliability signal, not ground truth."
        ),
    }
