from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from analysis.perturbation import (
    PredictionScore,
    evaluate_gate,
    load_pie_dataset,
    load_split_rows,
    load_unseen_context_fold,
    masked_gene_mean,
    paired_bootstrap_delta,
    perturbation_mean_map,
    perturbation_mean_predictions,
    score_predictions,
    select_beta,
)


def _write_dataset(
    root: Path,
    *,
    lfc: np.ndarray,
    tested: np.ndarray,
    contexts: np.ndarray,
    perturbations: np.ndarray,
    context_names: tuple[str, ...],
    perturbation_names: tuple[str, ...],
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    np.save(root / "lfc_true.npy", lfc)
    np.save(root / "tested.npy", tested)
    np.save(root / "ctx_ids.npy", contexts)
    np.save(root / "pert_ids.npy", perturbations)
    meta = {
        "num_rows": int(lfc.shape[0]),
        "num_genes": int(lfc.shape[1]),
        "num_contexts": len(context_names),
        "num_perts": len(perturbation_names),
        "genes": [f"G{i + 1}" for i in range(lfc.shape[1])],
        "context_to_id": {name: i for i, name in enumerate(context_names)},
        "pert_to_id": {name: i for i, name in enumerate(perturbation_names)},
        "pert_ensembl": {},
    }
    (root / "meta.json").write_text(json.dumps(meta), encoding="utf-8")


def _dataset(root: Path):
    lfc = np.array(
        [
            [1.0, 2.0, 3.0],
            [3.0, 4.0, 5.0],
            [2.0, 2.0, 2.0],
            [4.0, 4.0, 4.0],
        ]
    )
    tested = np.array(
        [
            [True, False, True],
            [True, True, False],
            [True, True, True],
            [True, True, True],
        ]
    )
    contexts = np.array([0, 0, 1, 1])
    perturbations = np.array([0, 1, 0, 1])
    _write_dataset(
        root,
        lfc=lfc,
        tested=tested,
        contexts=contexts,
        perturbations=perturbations,
        context_names=("ctx0", "ctx1"),
        perturbation_names=("P1", "P2"),
    )
    return load_pie_dataset(root)


def test_load_pie_dataset_reads_shapes_and_vocabularies(tmp_path):
    dataset = _dataset(tmp_path / "data")

    assert dataset.lfc.shape == (4, 3)
    assert dataset.genes == ("G1", "G2", "G3")
    assert dataset.context_names == ("ctx0", "ctx1")
    assert dataset.perturbation_names == ("P1", "P2")
    assert dataset.mask.tolist() == [
        [True, False, True],
        [True, True, False],
        [True, True, True],
        [True, True, True],
    ]


def test_load_pie_dataset_rejects_mismatched_shapes(tmp_path):
    root = tmp_path / "data"
    _dataset(root)
    np.save(root / "tested.npy", np.ones((3, 3), dtype=bool))

    with pytest.raises(ValueError, match="tested shape"):
        load_pie_dataset(root)


def test_masked_gene_mean_ignores_untested_entries(tmp_path):
    dataset = _dataset(tmp_path / "data")

    mean = masked_gene_mean(dataset, np.array([0, 1]))

    assert mean.tolist() == pytest.approx([2.0, 4.0, 3.0])


def test_split_rows_resolve_names_and_reject_duplicates(tmp_path):
    dataset = _dataset(tmp_path / "data")
    split_dir = tmp_path / "splits"
    split_dir.mkdir()
    (split_dir / "replogle_wdataset_unseen_ctx_ctx1_train.json").write_text(
        json.dumps({"replogle.ctx0": ["P1", "P2"]}), encoding="utf-8"
    )

    rows = load_split_rows(dataset, split_dir, "unseen_ctx", "ctx1", "train")

    assert rows.tolist() == [0, 1]

    (split_dir / "replogle_wdataset_unseen_ctx_ctx1_val.json").write_text(
        json.dumps({"replogle.ctx0": ["P1", "P1"]}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="duplicate rows"):
        load_split_rows(dataset, split_dir, "unseen_ctx", "ctx1", "val")


def test_unseen_context_fold_rejects_held_out_context_in_train(tmp_path):
    dataset = _dataset(tmp_path / "data")
    split_dir = tmp_path / "splits"
    split_dir.mkdir()
    for part, key in (
        ("train", "replogle.ctx1"),
        ("val", "replogle.ctx0"),
        ("test", "replogle.ctx1"),
    ):
        (split_dir / f"replogle_wdataset_unseen_ctx_ctx1_{part}.json").write_text(
            json.dumps({key: ["P1"]}), encoding="utf-8"
        )

    with pytest.raises(ValueError, match="leaked"):
        load_unseen_context_fold(dataset, split_dir, "ctx1")


def test_select_beta_prefers_scale_used_to_generate_validation(tmp_path):
    dataset = _dataset(tmp_path / "data")
    train = np.array([0, 1])
    validation = np.array([2, 3])
    global_mean = masked_gene_mean(dataset, train)
    means = perturbation_mean_map(dataset, train)
    prediction, _ = perturbation_mean_predictions(dataset, validation, means, global_mean)
    centered = prediction - global_mean

    beta, curve = select_beta(
        lambda value: value * centered,
        dataset,
        validation,
        betas=(0.0, 0.25, 0.5, 0.75, 1.0),
    )

    assert 0.0 <= beta <= 1.0
    assert len(curve) == 5


def test_score_predictions_ignores_untested_genes(tmp_path):
    dataset = _dataset(tmp_path / "data")
    rows = np.array([0])
    first = np.zeros((1, 3))
    second = first.copy()
    second[0, 1] = 100.0  # gene 1 is untested for row 0

    assert score_predictions(dataset, rows, first).summary() == score_predictions(
        dataset, rows, second
    ).summary()


def test_paired_bootstrap_detects_consistent_improvement():
    baseline = PredictionScore(
        row_mse=np.array([1.0, 1.0]),
        row_genes=np.array([10, 10]),
        row_rmse=np.ones(2),
        row_correlation=np.array([0.0, 0.0]),
        row_top_k=np.array([0.0, 0.0]),
        row_sign=np.array([0.5, 0.5]),
        top_k=50,
    )
    candidate = PredictionScore(
        row_mse=np.array([0.25, 0.25]),
        row_genes=np.array([10, 10]),
        row_rmse=np.full(2, 0.5),
        row_correlation=np.array([0.5, 0.5]),
        row_top_k=np.array([0.1, 0.1]),
        row_sign=np.array([0.8, 0.8]),
        top_k=50,
    )

    result = paired_bootstrap_delta(baseline, candidate, resamples=100, seed=1)

    assert result["mean_delta"] == pytest.approx(0.5)
    assert result["ci95"][0] > 0


def test_evaluate_gate_requires_two_passing_folds():
    fold_results = {
        "a": {"gate": {"passes": True}},
        "b": {"gate": {"passes": False}},
        "c": {"gate": {"passes": True}},
        # k562 is exploratory and must not be needed.
        "k562": {"gate": {"passes": True}},
    }

    result = evaluate_gate(fold_results, ("a", "b", "c"))

    assert result["passed"] is True
    assert result["passing_folds"] == ["a", "c"]
    assert result["n_passing"] == 2
