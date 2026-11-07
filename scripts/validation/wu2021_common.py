"""Shared setup for the Wu et al. 2021 breast cancer validation.

Data (downloaded to ``data/public``, never committed):
* scRNA-seq atlas: GEO GSE176078 (26 patients, author cell-type annotations)
* Visium + pathologist spot annotations: Zenodo 10.5281/zenodo.4739739 (CC BY 4.0)

The patient-level split below is the single source of truth for every
script: TEST patients are never used to build references, choose genes,
pick hyper-parameters or fit calibration.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

DATA = ROOT / "data"
SCRNA_DIR = DATA / "public" / "wu2021_scrna"
VISIUM_DIR = DATA / "processed" / "wu2021_visium"
GROUP_SUMS = DATA / "processed" / "wu2021_scrna_group_sums.npz"
PACKS = ROOT / "packages" / "disease-packs"

# ── Patient-level split ──────────────────────────────────────────────────────
TRAIN_PATIENTS = ["1142243F", "1160920F", "CID4290", "CID44971"]
TEST_PATIENTS = ["CID4465", "CID4535"]  # held out: one TNBC, one ER+
VISIUM_PATIENTS = TRAIN_PATIENTS + TEST_PATIENTS
# The same patient can carry a different id in the scRNA atlas. Exclusions must
# follow these aliases, otherwise a held-out patient's cells leak into the reference.
SCRNA_ALIASES = {"CID4290": ["CID4290A"]}


def validate_patient_split(
    train: list[str] | tuple[str, ...],
    test: list[str] | tuple[str, ...],
    available: list[str] | tuple[str, ...],
) -> None:
    """Fail closed if patients or scRNA aliases cross the held-out boundary."""
    if len(set(train)) != len(train) or len(set(test)) != len(test):
        raise ValueError("Patient split contains duplicate IDs")
    if set(train) & set(test):
        raise ValueError("Patient-level train/test split overlaps")
    if set(train) | set(test) != set(available):
        raise ValueError(
            "Patient split must cover exactly the available Visium patients"
        )
    if scrna_ids(tuple(train)) & scrna_ids(tuple(test)):
        raise ValueError("scRNA patient aliases cross the train/test boundary")


def scrna_ids(patients: list[str] | tuple[str, ...]) -> set[str]:
    ids = set(patients)
    for patient in patients:
        ids.update(SCRNA_ALIASES.get(patient, []))
    return ids


validate_patient_split(TRAIN_PATIENTS, TEST_PATIENTS, VISIUM_PATIENTS)

# ── scRNA cell types → breast pack cell-type ids ─────────────────────────────
# Cancer epithelium stays generic (subtype calls in the atlas are inferred);
# normal luminal / myoepithelial cells map to the pack's luminal / basal types.
MAJOR_TO_PACK = {
    "Cancer Epithelial": "epithelial",
    "CAFs": "fibroblast",
    "PVL": "fibroblast",
    "Endothelial": "endothelial",
    "T-cells": "t_cell",
    "B-cells": "b_cell",
    "Plasmablasts": "b_cell",
    "Myeloid": "macrophage",
}
NORMAL_EPITHELIAL_MINOR = {
    "Luminal Progenitors": "luminal",
    "Mature Luminal": "luminal",
    "Myoepithelial": "basal",
}
REFERENCE_TYPES = [
    "epithelial",
    "luminal",
    "basal",
    "fibroblast",
    "endothelial",
    "t_cell",
    "b_cell",
    "macrophage",
]


def pack_type(major: str, minor: str) -> str | None:
    if major == "Normal Epithelial":
        return NORMAL_EPITHELIAL_MINOR.get(minor)
    return MAJOR_TO_PACK.get(major)


# ── Pathologist labels → breast pack zones ───────────────────────────────────
# DCIS has no matching zone and is left out of training and scoring, as are
# artefacts and unlabelled spots.
LABEL_TO_ZONE = {
    "Invasive cancer": "tumor_core",
    "Invasive cancer + stroma": "tumor_core",
    "Invasive cancer + lymphocytes": "tumor_core",
    "Invasive cancer + stroma + lymphocytes": "tumor_core",
    "Invasive cancer + adipose tissue + lymphocytes": "tumor_core",
    "Cancer trapped in lymphocyte aggregation": "tumor_core",
    "Stroma": "stroma",
    "Stroma + adipose tissue": "stroma",
    "Adipose tissue": "stroma",
    "Lymphocytes": "immune_aggregate",
    "TLS": "immune_aggregate",
    "Normal glands + lymphocytes": "normal_gland",
    "Normal duct": "normal_gland",
    "Normal + stroma + lymphocytes": "normal_gland",
    "Necrosis": "necrosis",
}
CLASSES = ["tumor_core", "stroma", "immune_aggregate", "normal_gland", "necrosis"]


def load_labels(patient: str) -> pd.Series:
    """Pathologist class per barcode, mapped to pack zones (NaN = ignored)."""
    meta = pd.read_csv(VISIUM_DIR / patient / f"{patient}_metadata.csv", index_col=0)
    raw = meta["Classification"].fillna("").astype(str).str.strip()
    return raw.map(LABEL_TO_ZONE)


def label_array(barcodes: list[str], labels: pd.Series) -> np.ndarray:
    """Integer class per spot (−1 when unlabelled or ignored)."""
    index = {name: i for i, name in enumerate(CLASSES)}
    aligned = labels.reindex(barcodes)
    return np.array(
        [index.get(v, -1) if isinstance(v, str) else -1 for v in aligned], dtype=int
    )


def reference_from_sums(
    sums_path: Path = GROUP_SUMS,
    *,
    exclude_patients: list[str] | tuple[str, ...] = (),
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    """Mean expression (fraction of transcripts) and detection rate per cell type.

    Built only from patients not in ``exclude_patients``.
    """
    data = np.load(sums_path, allow_pickle=False)
    genes = [str(g) for g in data["genes"]]
    patients = [str(p) for p in data["group_patient"]]
    types = [str(t) for t in data["group_type"]]
    excluded = scrna_ids(tuple(exclude_patients))
    keep = [i for i, p in enumerate(patients) if p not in excluded]
    means, detect, cells = {}, {}, {}
    for cell_type in REFERENCE_TYPES:
        rows = [i for i in keep if types[i] == cell_type]
        n = int(data["n_cells"][rows].sum()) if rows else 0
        if n == 0:
            continue
        means[cell_type] = data["cp10k_sums"][rows].sum(axis=0) / n / 1e4
        detect[cell_type] = data["detected"][rows].sum(axis=0) / n
        cells[cell_type] = n
    mean_df = pd.DataFrame(means, index=genes).T
    detect_df = pd.DataFrame(detect, index=genes).T
    return mean_df, detect_df, cells


def marker_panel(
    means: pd.DataFrame,
    detection: pd.DataFrame,
    *,
    per_type: int = 50,
    min_detection: float = 0.2,
) -> list[str]:
    """Top up-regulated genes per cell type (log2 fold change vs the other types)."""
    panel: list[str] = []
    for cell_type in means.index:
        others = means.drop(index=cell_type).mean(axis=0)
        lfc = np.log2((means.loc[cell_type] * 1e4 + 0.1) / (others * 1e4 + 0.1))
        ok = detection.loc[cell_type] >= min_detection
        ranked = lfc[ok].sort_values(ascending=False)
        panel.extend(
            g
            for g in ranked.index[:per_type]
            if not g.upper().startswith(("MT-", "RPL", "RPS"))
        )
    return list(dict.fromkeys(g.upper() for g in panel))
