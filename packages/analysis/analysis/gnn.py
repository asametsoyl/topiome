"""Spatial graph neural network for tissue-domain prediction.

Architecture: two GraphSAGE-mean layers. Each layer combines a spot's own
features with the mean of its spatial neighbours::

    h      = relu(X·W1_self + (A·X)·W1_nb + b1)
    logits = h·W2_self + (A·h)·W2_nb + b2
    p      = softmax(logits / T)

``A`` is the row-normalised kNN graph over spot coordinates and ``T`` a
temperature fitted on held-out folds (calibration).

Unlike Glio-Cartography's GNN, which was trained to reproduce the pipeline's
own deconvolution output (a circular target), these models are trained on
independent pathologist annotations with a patient-level train/test split.
Training is offline (``scripts/validation/train_domain_gnn.py``, PyTorch);
inference here is NumPy-only so the API image does not need PyTorch.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import sparse

from .communication import spatial_graph

WEIGHT_NAMES = ("W1_self", "W1_nb", "b1", "W2_self", "W2_nb", "b2")


def build_features(
    log_expression: pd.DataFrame,
    genes: list[str],
    composition: pd.DataFrame | None = None,
    cell_types: list[str] | None = None,
) -> np.ndarray:
    """Per-sample z-scored log expression of the model's gene panel (+ composition).

    Z-scoring within each sample removes most per-slide batch effects; genes the
    sample does not measure become zeros (the sample mean).
    """
    upper = {str(c).upper(): c for c in log_expression.columns}
    columns = [upper.get(g.upper()) for g in genes]
    values = np.zeros((len(log_expression), len(genes)), dtype=np.float64)
    for j, column in enumerate(columns):
        if column is not None:
            values[:, j] = log_expression[column].to_numpy(dtype=np.float64)
    mean = values.mean(axis=0, keepdims=True)
    std = values.std(axis=0, keepdims=True)
    z = np.clip((values - mean) / (std + 1e-6), -5, 5)
    parts = [z]
    if cell_types:
        if composition is None:
            raise ValueError("Model expects composition features")
        comp = composition.reindex(columns=cell_types, fill_value=0.0).to_numpy(dtype=np.float64)
        parts.append(comp)
    return np.hstack(parts).astype(np.float32)


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=1, keepdims=True)


def forward(weights: dict[str, np.ndarray], features: np.ndarray, graph: sparse.spmatrix) -> np.ndarray:
    """Logits for every spot (NumPy mirror of the PyTorch training model)."""
    x = features.astype(np.float64)
    hidden = x @ weights["W1_self"] + (graph @ x) @ weights["W1_nb"] + weights["b1"]
    hidden = np.maximum(hidden, 0.0)
    return hidden @ weights["W2_self"] + (graph @ hidden) @ weights["W2_nb"] + weights["b2"]


@dataclass
class DomainModel:
    weights: dict[str, np.ndarray]
    genes: list[str]
    classes: list[str]
    cell_types: list[str] = field(default_factory=list)
    k: int = 6
    temperature: float = 1.0
    version: str = "0"
    sha256: str = ""
    card: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, weights_path: str | Path, card_path: str | Path) -> DomainModel:
        weights_path = Path(weights_path)
        card = json.loads(Path(card_path).read_text(encoding="utf-8"))
        with np.load(weights_path, allow_pickle=False) as data:
            weights = {name: data[name].astype(np.float64) for name in WEIGHT_NAMES}
        spec = card["model"]
        model = cls(
            weights=weights,
            genes=list(spec["genes"]),
            classes=list(spec["classes"]),
            cell_types=list(spec.get("cell_types", [])),
            k=int(spec.get("k", 6)),
            temperature=float(spec.get("temperature", 1.0)),
            version=str(card.get("version", "0")),
            sha256=hashlib.sha256(weights_path.read_bytes()).hexdigest(),
            card=card,
        )
        expected_in = len(model.genes) + len(model.cell_types)
        if model.weights["W1_self"].shape[0] != expected_in:
            raise ValueError("Model weights do not match its gene panel")
        if model.weights["W2_self"].shape[1] != len(model.classes):
            raise ValueError("Model weights do not match its classes")
        return model

    def gene_coverage(self, genes: list[str] | pd.Index) -> float:
        present = {str(g).upper() for g in genes}
        return sum(1 for g in self.genes if g.upper() in present) / max(len(self.genes), 1)

    def predict_proba(
        self,
        log_expression: pd.DataFrame,
        coordinates: np.ndarray,
        composition: pd.DataFrame | None = None,
    ) -> np.ndarray:
        features = build_features(log_expression, self.genes, composition, self.cell_types)
        graph = spatial_graph(np.asarray(coordinates, dtype=float), k=self.k)
        logits = forward(self.weights, features, graph)
        return _softmax(logits / max(self.temperature, 1e-3))


def expected_calibration_error(probs: np.ndarray, labels: np.ndarray, n_bins: int = 15) -> float:
    """ECE of the top-class confidence (labels < 0 are ignored)."""
    mask = labels >= 0
    if not mask.any():
        return float("nan")
    confidence = probs[mask].max(axis=1)
    correct = probs[mask].argmax(axis=1) == labels[mask]
    edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:], strict=True):
        in_bin = (confidence > lo) & (confidence <= hi)
        if in_bin.any():
            ece += in_bin.mean() * abs(correct[in_bin].mean() - confidence[in_bin].mean())
    return float(ece)
