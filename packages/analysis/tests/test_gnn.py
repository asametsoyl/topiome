"""NumPy GNN inference: forward pass, model files and pipeline gating."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import sparse

from analysis.gnn import DomainModel, build_features, expected_calibration_error, forward
from analysis.pipeline import run_pipeline
from analysis.synthetic import generate_demo_dataset


def _weights(n_in: int, hidden: int, n_classes: int, seed: int = 0) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    return {
        "W1_self": rng.normal(size=(n_in, hidden)),
        "W1_nb": rng.normal(size=(n_in, hidden)),
        "b1": rng.normal(size=hidden),
        "W2_self": rng.normal(size=(hidden, n_classes)),
        "W2_nb": rng.normal(size=(hidden, n_classes)),
        "b2": rng.normal(size=n_classes),
    }


def test_forward_matches_explicit_sage_layers():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(5, 3))
    graph = sparse.csr_matrix(np.array([[0, 1, 0, 0, 0], [0.5, 0, 0.5, 0, 0], [0, 1, 0, 0, 0],
                                        [0, 0, 0, 0, 1], [0, 0, 0, 1, 0]], dtype=float))
    w = _weights(3, 4, 2)
    expected_hidden = np.maximum(x @ w["W1_self"] + (graph.toarray() @ x) @ w["W1_nb"] + w["b1"], 0)
    expected = expected_hidden @ w["W2_self"] + (graph.toarray() @ expected_hidden) @ w["W2_nb"] + w["b2"]
    assert np.allclose(forward(w, x, graph), expected)


def test_features_are_zscored_within_sample_and_missing_genes_are_zero():
    log_expr = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [5.0, 5.0, 5.0]})
    comp = pd.DataFrame({"t": [0.2, 0.5, 0.3]})
    features = build_features(log_expr, ["A", "B", "MISSING"], comp, ["t", "absent"])
    assert features.shape == (3, 5)
    assert np.allclose(features[:, 0].mean(), 0) and features[:, 0].std() > 0
    assert np.allclose(features[:, 1:3], 0)
    assert np.allclose(features[:, 3], [0.2, 0.5, 0.3])
    assert np.allclose(features[:, 4], 0)


def _save_model(tmp_path: Path, genes: list[str], classes: list[str]) -> DomainModel:
    np.savez(tmp_path / "m.npz", **_weights(len(genes), 8, len(classes)))
    card = {
        "version": "9.9.9",
        "model": {"genes": genes, "classes": classes, "cell_types": [], "k": 4, "temperature": 2.0},
        "metrics": {"test": {"gnn": {"pooled": {"macro_f1": 0.5}}}},
        "data": {"summary": "toy"},
    }
    (tmp_path / "m.json").write_text(json.dumps(card))
    return DomainModel.load(tmp_path / "m.npz", tmp_path / "m.json")


def test_model_files_round_trip_and_probabilities_sum_to_one(tmp_path: Path):
    model = _save_model(tmp_path, ["G1", "G2", "G3"], ["tumor_core", "stroma"])
    assert model.version == "9.9.9" and len(model.sha256) == 64
    log_expr = pd.DataFrame(np.random.default_rng(0).random((30, 3)), columns=["G1", "G2", "G3"])
    coords = np.column_stack([np.arange(30) % 6, np.arange(30) // 6]).astype(float)
    probs = model.predict_proba(log_expr, coords)
    assert probs.shape == (30, 2)
    assert np.allclose(probs.sum(axis=1), 1)


def test_mismatched_weights_are_rejected(tmp_path: Path):
    _save_model(tmp_path, ["G1", "G2", "G3"], ["a", "b"])
    card = json.loads((tmp_path / "m.json").read_text())
    card["model"]["genes"] = ["G1"]
    (tmp_path / "m.json").write_text(json.dumps(card))
    with pytest.raises(ValueError, match="gene panel"):
        DomainModel.load(tmp_path / "m.npz", tmp_path / "m.json")


def test_ece_is_zero_for_perfectly_calibrated_confident_predictions():
    probs = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0]])
    assert expected_calibration_error(probs, np.array([0, 1, 0])) == pytest.approx(0.0)
    assert expected_calibration_error(probs, np.array([1, 0, 1])) == pytest.approx(1.0)


def test_pipeline_applies_model_on_real_data_and_skips_synthetic(tmp_path: Path, breast_pack):
    dataset, signatures, _ = generate_demo_dataset(breast_pack, n_spots=200, seed=2)
    genes = list(dataset.expression.columns[:20])
    model = _save_model(tmp_path, genes, ["tumor_core", "stroma", "immune_aggregate"])
    params = {"lr_permutations": 9}

    synthetic = run_pipeline(dataset, breast_pack, signatures=signatures, params=params, domain_model=model)
    info = synthetic.validation["domain_model"]
    assert info["applied"] is False and "synthetic" in info["reason"]
    assert synthetic.summary["domain_method"] == "kmeans_markers"

    dataset.metadata["synthetic"] = False  # pretend it is a real section
    real = run_pipeline(dataset, breast_pack, signatures=signatures, params=params, domain_model=model)
    assert real.validation["domain_model"]["applied"] is True
    assert real.summary["domain_method"] == "gnn"
    assert set(real.domains) <= {"tumor_core", "stroma", "immune_aggregate", "unassigned"}
    assert all("domain_confidence" in spot for spot in real.spots)

    low_coverage = _save_model(tmp_path, genes[:5] + [f"ABSENT{i}" for i in range(15)], ["tumor_core", "stroma"])
    skipped = run_pipeline(dataset, breast_pack, signatures=signatures, params=params, domain_model=low_coverage)
    assert skipped.validation["domain_model"]["applied"] is False
    assert any("domain model skipped" in w for w in skipped.warnings)
