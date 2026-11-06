"""Run Topiome on a public glioblastoma Visium section and report the
independent Ivy GAP atlas check (GEO GSE331374, sample GSM9744831).

No GBM scRNA reference or trained domain model ships yet, so this measures the
marker-score baseline honestly on real tissue.

Usage (from apps/api):  uv run python -I ../../scripts/validation/validate_gbm_gse331374.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from analysis import load_visium, run_pipeline  # noqa: E402

from app.disease_packs import get_pack  # noqa: E402
from app.services.pipeline import pack_genes  # noqa: E402

SAMPLE = ROOT / "data" / "processed" / "gse331374_gbm" / "GSM9744831"


def main() -> None:
    pack = get_pack("glioblastoma")
    dataset = load_visium(SAMPLE, sample_id="GSM9744831", keep_genes=pack_genes(pack))
    result = run_pipeline(dataset, pack)
    s, atlas = result.summary, result.validation["atlas_check"]
    qc = result.qc["summary"]
    lines = [
        "# Glioblastoma — GSE331374 real-data check",
        "",
        f"_Pipeline {result.pipeline_version} · pack glioblastoma v{pack['version']} · "
        f"{datetime.now(UTC):%Y-%m-%d} · Research Use Only_",
        "",
        "Sample GSM9744831 (primary tumour, 10x Visium, GEO GSE331374). No GBM scRNA reference or "
        "trained domain model is shipped yet, so composition is the marker-score baseline.",
        "",
        "| Measure | Value |",
        "|---|---:|",
        f"| Spots (in tissue) | {s['n_spots']:,} |",
        f"| Genes measured | {s['n_genes']:,} |",
        f"| Spots passing QC | {qc['passed_spots']:,} |",
        f"| QC mito cut-off | {qc['thresholds']['max_mito_fraction']:.0%} ({qc['thresholds']['mito_rule']}) |",
        f"| Method agreement (mean per spot) | {s['method_agreement']} |",
        f"| Significant ligand–receptor pairs | {s['significant_interactions']} / {len(result.communication)} |",
        "",
        "## Independent Ivy GAP atlas check",
        "",
    ]
    if atlas["status"] == "ok":
        zones = atlas["zones"]
        lines += [
            f"- Zone ↔ structure correlation (diagonal mean): **{atlas['diagonal_mean']}**",
            f"- Top-1 match: **{atlas['top1_accuracy']}** over {atlas['n_zones_compared']} zones",
            f"- Genes compared: {atlas['n_genes']} (zone-marker genes excluded: {', '.join(atlas['excluded_genes'])})",
            f"- Spots per zone: {json.dumps(atlas['zone_spots'])}",
            "",
            "| Zone \\ structure | " + " | ".join(atlas["structures"]) + " |",
            "|---|" + "---:|" * len(atlas["structures"]),
            *[
                f"| {zone} | " + " | ".join("—" if v is None else f"{v:.2f}" for v in row) + " |"
                for zone, row in zip(zones, atlas["correlation"], strict=True)
            ],
        ]
    else:
        lines.append(f"- Not computed: {atlas.get('reason')}")
    weak = atlas.get("status") != "ok" or (atlas.get("diagonal_mean") or 0) < 0.1
    verdict = (
        "The marker-based zones do not correspond to the Ivy GAP anatomic structures on this section."
        if weak
        else "The marker-based zones correspond only weakly to the Ivy GAP anatomic structures on this section."
    )
    lines += [
        "",
        "## Reading",
        "",
        verdict + " This matches Glio-Cartography's earlier result on GSE237183 (diagonal mean 0.21, top-1 0.45) and "
        "is why the GBM pack stays in beta: it needs an annotated GBM reference and a domain model "
        "trained on independent labels before zone calls can be trusted.",
        "",
        "Warnings raised by the pipeline:",
        "",
        *[f"- {w}" for w in result.warnings],
        "",
    ]
    out = ROOT / "docs" / "validation" / "gbm-gse331374.md"
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
