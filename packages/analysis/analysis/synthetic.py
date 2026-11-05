from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .types import SpatialDataset

HOUSEKEEPING = ["ACTB", "GAPDH", "MALAT1", "RPLP0", "B2M", "TMSB10", "EEF1A1", "RPL13A"]
MITO = ["MT-CO1", "MT-ND1", "MT-CYB"]
# Background transcriptome so the demo has a realistic gene count and QC
# behaves like a real Visium sample. Names are explicitly synthetic.
BACKGROUND = [f"BG{i:04d}" for i in range(1, 481)]


def _role(cell_type: dict) -> str:
    text = f"{cell_type.get('id', '')} {cell_type.get('name', '')}".lower()
    if any(k in text for k in ("her2", "tumor", "glioma", "melanoma", "proliferating")):
        return "tumor"
    if any(k in text for k in ("t cell", "b cell", "macrophage", "immune", "dendritic", "neutrophil", "mast")):
        return "immune"
    if any(k in text for k in ("endothelial", "vascular")):
        return "vascular"
    if any(k in text for k in ("fibroblast", "smooth muscle", "adipocyte", "astrocyte", "oligodendrocyte")):
        return "stromal"
    if any(k in text for k in ("epithelial", "luminal", "basal", "goblet", "alveolar", "airway", "keratinocyte", "melanocyte")):
        return "normal"
    return "stromal"


def _zone_weights(n_zones: int) -> dict[int, dict[str, float]]:
    templates = [
        {"tumor": 0.55, "immune": 0.20, "stromal": 0.15, "vascular": 0.10},
        {"tumor": 0.30, "immune": 0.30, "stromal": 0.30, "vascular": 0.10},
        {"tumor": 0.05, "immune": 0.20, "stromal": 0.65, "vascular": 0.10},
        {"tumor": 0.05, "immune": 0.70, "stromal": 0.15, "vascular": 0.10},
        {"normal": 0.55, "tumor": 0.10, "immune": 0.15, "stromal": 0.15, "vascular": 0.05},
        {"tumor": 0.15, "immune": 0.20, "stromal": 0.45, "vascular": 0.20},
    ]
    return {i: templates[i % len(templates)] for i in range(n_zones)}


def _assign_zones(coords: np.ndarray, n_zones: int) -> np.ndarray:
    """Deterministic synthetic spatial regions (demo only)."""
    span = np.ptp(coords, axis=0)
    span[span == 0] = 1.0
    x = (coords[:, 0] - coords[:, 0].min()) / span[0]
    y = (coords[:, 1] - coords[:, 1].min()) / span[1]

    zones = np.full(len(coords), 2 if n_zones > 2 else 0, dtype=int)
    if n_zones > 3:
        zones[np.hypot(x - 0.78, y - 0.26) < 0.085] = 3
    if n_zones > 4:
        zones[np.hypot(x - 0.20, y - 0.78) < 0.10] = 4
    if n_zones > 5:
        zones[np.hypot(x - 0.82, y - 0.82) < 0.09] = 5

    center = np.hypot((x - 0.5) / 1.0, (y - 0.5) / 1.0)
    if n_zones > 1:
        zones[center < 0.25] = 0
        zones[(center >= 0.25) & (center < 0.38)] = 1
    else:
        zones[:] = 0

    # Keep the two special regions on top of the radial pattern.
    if n_zones > 4:
        zones[np.hypot(x - 0.20, y - 0.78) < 0.10] = 4
    if n_zones > 3:
        zones[np.hypot(x - 0.78, y - 0.26) < 0.085] = 3
    if n_zones > 5:
        zones[np.hypot(x - 0.82, y - 0.82) < 0.09] = 5
    return zones


def generate_demo_dataset(
    pack: dict,
    *,
    n_spots: int = 1200,
    seed: int = 42,
    depth_mean: float = 9.0,
    ambient_fraction: float = 0.03,
) -> tuple[SpatialDataset, pd.DataFrame, dict[str, Any]]:
    """Generate a synthetic Visium-like dataset with known ground truth.

    Returns (dataset, reference_signatures, ground_truth).
    The demo is for product testing only; it is not a biological claim.
    """
    rng = np.random.default_rng(seed)
    rows = int(np.ceil(np.sqrt(n_spots * 1.35)))
    cols = int(np.ceil(n_spots / rows))
    coords = []
    for r in range(rows):
        for c in range(cols):
            coords.append((c + 0.5 * (r % 2), r * np.sqrt(3) / 2))
            if len(coords) == n_spots:
                break
        if len(coords) == n_spots:
            break
    coordinates = np.array(coords, dtype=float)

    cell_types = pack.get("cell_types", [])
    zones = pack.get("zones", [])
    n_zones = min(len(zones), 6)
    zone_ids = _assign_zones(coordinates, n_zones)

    roles: dict[str, list[int]] = {}
    for i, cell_type in enumerate(cell_types):
        roles.setdefault(_role(cell_type), []).append(i)

    weights_by_zone = _zone_weights(n_zones)
    compositions = np.zeros((n_spots, len(cell_types)), dtype=float)
    for i in range(n_spots):
        template = weights_by_zone[int(zone_ids[i]) % n_zones]
        base = np.full(len(cell_types), 0.015, dtype=float)
        for role, weight in template.items():
            members = roles.get(role, [])
            if members:
                base[members] += weight / len(members)
        total = base.sum()
        base = base / total
        alpha = base * 28.0 + 0.35
        comp = rng.dirichlet(alpha)
        comp = comp / comp.sum()
        compositions[i] = comp

    genes: list[str] = []
    for ct in cell_types:
        genes.extend(ct.get("markers", []))
    for zone in zones:
        genes.extend(zone.get("markers", []))
    for target in pack.get("targets", []):
        if target.get("gene"):
            genes.append(target["gene"])
    for pair in pack.get("ligand_receptor_pairs", []):
        genes.extend([pair.get("ligand", ""), pair.get("receptor", "")])
    genes.extend(HOUSEKEEPING)
    genes.extend(MITO)
    genes.extend(BACKGROUND)
    genes = list(dict.fromkeys(g.upper() for g in genes if g))

    signatures = pd.DataFrame(
        rng.lognormal(mean=-1.1, sigma=0.45, size=(len(cell_types), len(genes))),
        index=[ct["id"] for ct in cell_types],
        columns=genes,
    )
    gene_index = {g: i for i, g in enumerate(genes)}

    for i, ct in enumerate(cell_types):
        for marker in ct.get("markers", []):
            if marker.upper() in gene_index:
                signatures.iloc[i, gene_index[marker.upper()]] = float(
                    2.8 + rng.lognormal(mean=0.5, sigma=0.35)
                )

    # Make zone markers high in the cell types that dominate that zone.
    for z, zone in enumerate(zones[:n_zones]):
        template = weights_by_zone[z]
        dominant_roles = sorted(template.items(), key=lambda kv: kv[1], reverse=True)[:2]
        for role, _ in dominant_roles:
            for i in roles.get(role, []):
                for marker in zone.get("markers", []):
                    if marker.upper() in gene_index:
                        signatures.iloc[i, gene_index[marker.upper()]] += float(
                            1.4 + rng.lognormal(mean=0.2, sigma=0.3)
                        )

    # Targets: moderate expression in tumor and immune compartments.
    for target in pack.get("targets", []):
        gene = target.get("gene", "").upper()
        if gene not in gene_index:
            continue
        for role in ("tumor", "immune", "vascular"):
            for i in roles.get(role, []):
                signatures.iloc[i, gene_index[gene]] += float(
                    0.8 + rng.lognormal(mean=-0.2, sigma=0.4)
                )

    # Ligand–receptor genes: ligand in the sender, receptor in the receiver cell type.
    cell_index = {ct["id"]: i for i, ct in enumerate(cell_types)}
    for pair in pack.get("ligand_receptor_pairs", []):
        for gene_key, cell_key in (("ligand", "sender"), ("receptor", "receiver")):
            gene = str(pair.get(gene_key, "")).upper()
            i = cell_index.get(pair.get(cell_key))
            if gene in gene_index and i is not None:
                signatures.iloc[i, gene_index[gene]] += float(
                    1.2 + rng.lognormal(mean=0.0, sigma=0.3)
                )

    # Equal-RNA-content profiles: rows sum to one. NNLS uses the same matrix,
    # so the synthetic benchmark measures the estimator rather than a scale bug.
    row_totals = signatures.sum(axis=1).replace(0, np.nan)
    signatures = signatures.div(row_totals, axis=0).fillna(0.0)

    depth = rng.lognormal(mean=depth_mean, sigma=0.22, size=n_spots)
    expected = (compositions @ signatures.to_numpy(dtype=float)) * depth[:, None]
    ambient = (
        ambient_fraction
        * signatures.to_numpy(dtype=float).mean(axis=0)
        * depth[:, None]
    )
    expected = np.clip(expected + ambient, 0, None)
    counts = rng.poisson(expected).astype(int)

    barcodes = [f"DEMO-{i:05d}" for i in range(n_spots)]
    expression = pd.DataFrame(counts, index=barcodes, columns=genes)
    metadata = {
        "platform": "visium",
        "synthetic": True,
        "disease_pack": pack.get("id"),
        "note": "Synthetic demo data generated by Topiome. Not a biological sample.",
    }
    dataset = SpatialDataset(
        sample_id=f"demo-{pack.get('id', 'sample')}",
        barcodes=barcodes,
        coordinates=coordinates,
        expression=expression,
        metadata=metadata,
    )

    reference = signatures.copy()
    reference.index.name = "cell_type"

    ground_truth = {
        "composition": pd.DataFrame(compositions, index=barcodes, columns=reference.index),
        "zones": np.array([zones[int(z) % len(zones)]["id"] for z in zone_ids], dtype=object),
        "zone_ids": zone_ids,
        "synthetic": True,
    }
    return dataset, reference, ground_truth
