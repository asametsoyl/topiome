"""Features ported from Glio-Cartography: method concordance, ligand–receptor
communication, and the independent external-atlas check."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from analysis.atlas import atlas_correspondence
from analysis.communication import benjamini_hochberg, score_ligand_receptor, spatial_graph
from analysis.deconvolution import method_concordance
from analysis.pipeline import run_pipeline
from analysis.synthetic import generate_demo_dataset

# ── Method concordance ──────────────────────────────────────────────────────


def test_identical_methods_agree_fully():
    comp = pd.DataFrame({"a": [0.7, 0.2, 0.5], "b": [0.3, 0.8, 0.5]})
    agreement, summary = method_concordance(comp, comp.copy())
    assert np.allclose(agreement, 1.0)
    assert summary["mean_spot_agreement"] == pytest.approx(1.0)
    assert summary["mean_cell_type_pearson"] == pytest.approx(1.0)


def test_opposite_methods_disagree():
    first = pd.DataFrame({"a": [1.0, 0.0], "b": [0.0, 1.0]})
    second = pd.DataFrame({"a": [0.0, 1.0], "b": [1.0, 0.0]})
    agreement, summary = method_concordance(first, second)
    assert np.allclose(agreement, 0.0, atol=1e-6)
    assert summary["low_agreement_fraction"] == 1.0
    assert summary["mean_cell_type_pearson"] == pytest.approx(-1.0)


def test_concordance_requires_shared_cell_types():
    with pytest.raises(ValueError):
        method_concordance(pd.DataFrame({"a": [1.0]}), pd.DataFrame({"b": [1.0]}))


# ── Ligand–receptor communication ───────────────────────────────────────────


def _grid(n_side: int = 12) -> np.ndarray:
    return np.array([(x, y) for x in range(n_side) for y in range(n_side)], dtype=float)


def test_spatial_graph_rows_sum_to_one():
    graph = spatial_graph(_grid(5), k=4)
    assert np.allclose(np.asarray(graph.sum(axis=1)).ravel(), 1.0)
    assert graph.diagonal().sum() == 0


def test_benjamini_hochberg_matches_reference_values():
    q = benjamini_hochberg([0.01, 0.04, 0.03, 0.5])
    assert q == pytest.approx([0.04, 0.0533333, 0.0533333, 0.5], rel=1e-4)


def test_colocalized_pair_is_significant_and_scattered_pair_is_not():
    coords = _grid(12)
    n = len(coords)
    left = coords[:, 0] < 6
    rng = np.random.default_rng(0)
    composition = pd.DataFrame(
        {
            "sender": np.where(left, 0.8, 0.1),
            "receiver": np.where(left, 0.7, 0.2),
            "everywhere": np.full(n, 0.5),
        }
    )
    expression = pd.DataFrame(
        {
            # Ligand and receptor both concentrated on the left half → co-localized.
            "LIG": np.where(left, 3.0, 0.1) + rng.normal(0, 0.05, n),
            "REC": np.where(left, 2.5, 0.1) + rng.normal(0, 0.05, n),
            # Receptor scattered at random → no spatial relationship.
            "NOISE": rng.random(n),
        }
    ).clip(lower=0)
    domains = np.where(left, "left", "right")
    pairs = [
        {"ligand": "LIG", "receptor": "REC", "sender": "sender", "receiver": "receiver"},
        {"ligand": "LIG", "receptor": "NOISE", "sender": "sender", "receiver": "everywhere"},
    ]
    results = {
        r["receptor"]: r
        for r in score_ligand_receptor(
            expression, composition, coords, domains, pairs, n_permutations=99, seed=1
        )
    }
    assert results["REC"]["significant"] is True
    assert results["REC"]["top_domain"] == "left"
    assert results["NOISE"]["q_value"] > 0.05


def test_missing_genes_or_cell_types_are_reported_not_hidden():
    coords = _grid(4)
    composition = pd.DataFrame({"sender": np.ones(16), "receiver": np.ones(16)})
    expression = pd.DataFrame({"LIG": np.ones(16)})
    results = score_ligand_receptor(
        expression,
        composition,
        coords,
        np.array(["d"] * 16),
        [
            {"ligand": "LIG", "receptor": "ABSENT", "sender": "sender", "receiver": "receiver"},
            {"ligand": "LIG", "receptor": "LIG", "sender": "ghost", "receiver": "receiver"},
        ],
        n_permutations=9,
    )
    assert all(r["tested"] is False for r in results)
    assert results[0]["missing"] == ["ABSENT"]
    assert results[1]["missing"] == ["ghost"]


# ── External atlas check ────────────────────────────────────────────────────

ATLAS = {
    "name": "Toy atlas",
    "citation": "test",
    "zone_map": {"zone_a": "sa", "zone_b": "sb", "zone_c": "sc"},
    "data": {
        "genes": {
            "G1": {"sa": 10.0, "sb": 1.0, "sc": 1.0},
            "G2": {"sa": 1.0, "sb": 10.0, "sc": 1.0},
            "G3": {"sa": 1.0, "sb": 1.0, "sc": 10.0},
            "G4": {"sa": 8.0, "sb": 2.0, "sc": 1.0},
            "G5": {"sa": 1.0, "sb": 8.0, "sc": 2.0},
            "MARK": {"sa": 9.0, "sb": 1.0, "sc": 1.0},
        }
    },
}


def _atlas_sample(matching: bool) -> tuple[pd.DataFrame, np.ndarray]:
    domains = np.repeat(["zone_a", "zone_b", "zone_c"], 20)
    genes = ATLAS["data"]["genes"]
    structures = ["sa", "sb", "sc"] if matching else ["sc", "sa", "sb"]
    rows = []
    for zone_index in range(3):
        structure = structures[zone_index]
        for _ in range(20):
            rows.append({g: genes[g][structure] for g in genes})
    return pd.DataFrame(rows), domains


def test_matching_zones_correlate_with_atlas():
    expression, domains = _atlas_sample(matching=True)
    result = atlas_correspondence(expression, domains, ATLAS, exclude_genes={"MARK"})
    assert result["status"] == "ok"
    assert result["top1_accuracy"] == 1.0
    assert result["diagonal_mean"] > 0.9
    assert "MARK" not in result["genes"]
    assert result["excluded_genes"] == ["MARK"]


def test_mislabelled_zones_are_reported_as_poor_match():
    expression, domains = _atlas_sample(matching=False)
    result = atlas_correspondence(expression, domains, ATLAS)
    assert result["status"] == "ok"
    assert result["top1_accuracy"] == 0.0
    assert result["diagonal_mean"] < 0


def test_atlas_check_needs_enough_genes():
    expression, domains = _atlas_sample(matching=True)
    result = atlas_correspondence(expression[["G1", "G2"]], domains, ATLAS)
    assert result["status"] == "insufficient_genes"


# ── Pipeline integration ────────────────────────────────────────────────────


def test_pipeline_reports_concordance_communication_and_limits(all_packs):
    pack = all_packs["glioblastoma"]
    dataset, signatures, _ = generate_demo_dataset(pack, n_spots=400, seed=3)
    result = run_pipeline(
        dataset, pack, signatures=signatures, params={"lr_permutations": 49}
    )
    payload = result.to_payload()

    concordance = payload["validation"]["method_concordance"]
    assert concordance["methods"] == ["nnls_reference", "marker_zscore_softmax"]
    assert 0 <= concordance["mean_spot_agreement"] <= 1
    assert len(payload["communication"]) == len(pack["ligand_receptor_pairs"])
    # Communication scores are not estimated on synthetic demo data; the gap
    # must stay explicit rather than producing plausible-looking p-values.
    assert all(not c["tested"] for c in payload["communication"])
    assert all(c["missing"] == ["synthetic demo data"] for c in payload["communication"])
    # The Ivy GAP comparison must never run on synthetic data.
    assert payload["validation"]["atlas_check"]["status"] == "skipped_synthetic"
    assert payload["summary"]["not_assessed"] == pack["not_assessed"]
    json.dumps(payload)  # payload stays JSON-serialisable


def test_every_pack_pair_points_at_its_own_cell_types(all_packs):
    for pack_id, pack in all_packs.items():
        cell_ids = {ct["id"] for ct in pack["cell_types"]}
        assert pack.get("ligand_receptor_pairs"), pack_id
        assert pack.get("not_assessed"), pack_id
        for pair in pack["ligand_receptor_pairs"]:
            assert pair["sender"] in cell_ids, (pack_id, pair)
            assert pair["receiver"] in cell_ids, (pack_id, pair)
