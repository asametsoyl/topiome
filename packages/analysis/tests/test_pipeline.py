from __future__ import annotations

import numpy as np

from analysis.pipeline import run_pipeline
from analysis.synthetic import generate_demo_dataset


def test_synthetic_demo_is_labelled_and_reproducible(breast_pack):
    first, reference, ground_truth = generate_demo_dataset(
        breast_pack, n_spots=200, seed=7
    )
    second, _, _ = generate_demo_dataset(breast_pack, n_spots=200, seed=7)

    assert first.metadata["synthetic"] is True
    assert first.expression.shape[0] == 200
    assert reference.shape[0] > 0
    assert "composition" in ground_truth
    assert np.allclose(first.expression.to_numpy(), second.expression.to_numpy())


def test_pipeline_returns_composition_and_ground_truth_metrics(breast_pack):
    dataset, signatures, ground_truth = generate_demo_dataset(
        breast_pack, n_spots=300, seed=42
    )
    dataset.ground_truth = ground_truth

    result = run_pipeline(
        dataset, breast_pack, signatures=signatures, params={"random_state": 42}
    )

    assert result.summary["method"] == "nnls"
    assert result.summary["n_spots"] == 300
    assert result.summary["n_cell_types"] == len(breast_pack["cell_types"])
    assert result.summary["n_domains"] >= 2
    assert len(result.domains) == 300
    assert len(result.spots) == 300
    assert result.metrics, "synthetic ground truth must produce benchmark metrics"
    assert result.metrics["composition"]["jsd_mean"] < 0.20
    assert result.metrics["domains"]["ari"] > 0.35

    sums = result.composition.sum(axis=1).to_numpy()
    assert np.allclose(sums, 1.0, atol=0.02)
    assert result.uncertainty.min() >= 0
    assert result.uncertainty.max() <= 1

    target_genes = {target["gene"] for target in result.target_scores}
    assert target_genes.issubset(
        {target["gene"] for target in breast_pack.get("targets", [])}
    )


def test_pipeline_records_fallback_when_no_reference_is_available(breast_pack):
    dataset, _, _ = generate_demo_dataset(breast_pack, n_spots=150, seed=3)

    result = run_pipeline(dataset, breast_pack)

    assert result.summary["method"] == "marker_score"
    assert any("marker-score composition" in warning for warning in result.warnings)
