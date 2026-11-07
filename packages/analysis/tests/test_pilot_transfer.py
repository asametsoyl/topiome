"""Pilot (few-shot) context transfer: leakage guards and recoverability."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from analysis.perturbation import PieDataset, masked_gene_mean
from analysis.pilot_transfer import (
    draw_pilot,
    fit_lowrank_ridge,
    fit_scale,
    pair_rows,
    predict_pair,
)


def _dataset(source: np.ndarray, target: np.ndarray) -> PieDataset:
    n, genes = source.shape
    lfc = np.vstack([source, target]).astype(np.float32)
    contexts = np.array([0] * n + [1] * n)
    perturbations = np.concatenate([np.arange(n), np.arange(n)])
    names = tuple(f"P{i}" for i in range(n))
    return PieDataset(
        lfc=lfc,
        tested=np.ones_like(lfc, dtype=bool),
        contexts=contexts,
        perturbations=perturbations,
        genes=tuple(f"G{j}" for j in range(genes)),
        context_names=("src", "tgt"),
        perturbation_names=names,
        context_to_id={"src": 0, "tgt": 1},
        pert_to_id={name: i for i, name in enumerate(names)},
        pert_ensembl={},
    )


def _synthetic(n: int = 300, genes: int = 40, beta: float = 0.5, seed: int = 0):
    rng = np.random.default_rng(seed)
    latent = rng.normal(size=(n, 5)) @ rng.normal(size=(5, genes))
    source_offset = rng.normal(scale=2.0, size=genes)
    target_offset = rng.normal(scale=2.0, size=genes)  # unrelated to the source offset
    source = source_offset + latent + rng.normal(scale=0.1, size=(n, genes))
    target = target_offset + beta * latent + rng.normal(scale=0.1, size=(n, genes))
    return _dataset(source, target)


def test_pairs_align_perturbations_across_contexts():
    pair = pair_rows(_synthetic(n=10), 0, 1)
    assert np.array_equal(pair.perturbations, np.arange(10))
    assert np.array_equal(pair.target - pair.source, np.full(10, 10))


def test_pilot_and_held_out_are_disjoint_and_complete():
    pilot, held = draw_pilot(50, 10, np.random.default_rng(1))
    assert len(pilot) == 10 and len(held) == 40
    assert set(pilot).isdisjoint(held)
    assert set(pilot) | set(held) == set(range(50))
    with pytest.raises(ValueError):
        draw_pilot(5, 5, np.random.default_rng(0))


def test_scale_is_recovered_and_clipped():
    rng = np.random.default_rng(2)
    x = rng.normal(size=(20, 8))
    tested = np.ones_like(x, dtype=bool)
    assert fit_scale(x, 0.4 * x, tested) == pytest.approx(0.4)
    assert fit_scale(x, -x, tested) == 0.0
    assert fit_scale(x, 3 * x, tested) == 1.0


def test_ridge_recovers_a_linear_map_from_few_pilot_rows():
    rng = np.random.default_rng(3)
    effects = rng.normal(size=(200, 5)) @ rng.normal(size=(5, 30))
    residual = 0.7 * effects
    ridge = fit_lowrank_ridge(effects, effects[:40], residual[:40], rank=5)
    predicted = (effects[40:] @ ridge.components) @ ridge.weights
    assert np.mean((predicted - residual[40:]) ** 2) < 0.05 * np.mean(residual[40:] ** 2)


def test_held_out_target_labels_do_not_influence_predictions():
    dataset = _synthetic()
    pair = pair_rows(dataset, 0, 1)
    pilot, held = draw_pilot(len(pair.perturbations), 60, np.random.default_rng(4))
    before, params = predict_pair(dataset, pair, pilot, held, rank=5)

    corrupted = np.array(dataset.lfc, copy=True)
    corrupted[pair.target[held]] = 999.0  # held-out labels only
    leaked = replace(dataset, lfc=corrupted)
    after, params_after = predict_pair(leaked, pair, pilot, held, rank=5)
    assert params == params_after
    for name in before:
        assert np.allclose(before[name], after[name]), name


def test_transfer_beats_pilot_mean_when_signal_exists():
    dataset = _synthetic(beta=0.5)
    pair = pair_rows(dataset, 0, 1)
    pilot, held = draw_pilot(len(pair.perturbations), 60, np.random.default_rng(5))
    predictions, params = predict_pair(dataset, pair, pilot, held, rank=5)
    truth = np.asarray(dataset.lfc[pair.target[held]], dtype=np.float64)
    mse = {name: float(np.mean((p - truth) ** 2)) for name, p in predictions.items()}
    assert params["beta"] == pytest.approx(0.5, abs=0.05)
    assert mse["pilot_mean"] < mse["zero"]  # target offset learned from the pilot
    assert mse["zero_shot_beta025"] > mse["pilot_mean"]  # source offset does not transfer
    assert mse["pilot_scaled_transfer"] < 0.5 * mse["pilot_mean"]
    assert mse["pilot_lowrank_ridge"] < 0.5 * mse["pilot_mean"]
    assert np.allclose(
        masked_gene_mean(dataset, pair.target[pilot]), predictions["pilot_mean"][0]
    )


def test_fast_scoring_matches_reference_scorer():
    from analysis.perturbation import score_predictions
    from analysis.pilot_transfer import score_rows_fast, summarize_rows

    rng = np.random.default_rng(6)
    dataset = _synthetic(n=40, genes=120)
    tested = rng.random(dataset.lfc.shape) > 0.2
    dataset = replace(dataset, tested=tested)
    rows = np.arange(40, 80)
    prediction = rng.normal(size=(40, 120))
    prediction[3] = 0.0  # constant row → undefined correlation in both scorers
    reference = score_predictions(dataset, rows, prediction, top_k=10)
    fast = score_rows_fast(dataset.lfc[rows], dataset.tested[rows], prediction, top_k=10)
    assert np.allclose(reference.row_rmse, fast["rmse"])
    assert np.allclose(reference.row_correlation, fast["correlation"], equal_nan=True)
    assert np.allclose(reference.row_top_k, fast["top_k_overlap"])
    summary = summarize_rows(fast)
    ref = reference.summary()
    assert summary["mean_row_rmse"] == pytest.approx(ref["mean_row_rmse"])
    assert summary["median_row_correlation"] == pytest.approx(ref["median_row_correlation"])


def test_pair_subset_keeps_only_the_two_contexts_in_memory():
    from analysis.pilot_transfer import pair_subset

    dataset = _synthetic(n=20)
    subset = pair_subset(dataset, 0, 1)
    assert isinstance(subset.lfc, np.ndarray) and subset.lfc.shape == dataset.lfc.shape
    pair_full, pair_sub = pair_rows(dataset, 0, 1), pair_rows(subset, 0, 1)
    assert np.allclose(dataset.lfc[pair_full.target], subset.lfc[pair_sub.target])
