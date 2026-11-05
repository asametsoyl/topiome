from __future__ import annotations

import json

from analysis.benchmark import benchmark_pack, main


def test_benchmark_pack_reports_gates(breast_pack):
    result = benchmark_pack(breast_pack, n_spots=300, seed=42)

    assert result["pack"] == "breast"
    assert result["dataset"] == "synthetic"
    assert result["method"] == "nnls"
    assert result["minimum_pass"] is True
    assert set(result["checks"]) == {"jsd_mean", "dominant_type_pearson", "ari"}
    assert "not a substitute" in result["note"]


def test_benchmark_cli_writes_metrics_and_manifest(tmp_path, packs_dir):
    exit_code = main(
        [
            "--pack",
            "breast",
            "--packs-dir",
            str(packs_dir),
            "--spots",
            "200",
            "--out",
            str(tmp_path),
            "--quiet",
        ]
    )

    assert exit_code == 0
    metrics = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))

    assert metrics["results"][0]["pack"] == "breast"
    assert metrics["results"][0]["minimum_pass"] is True
    assert manifest["packs"][0]["id"] == "breast"
    assert manifest["seed"] == 42
