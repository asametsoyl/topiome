from __future__ import annotations

import time
from typing import Any

import numpy as np
import pandas as pd

from .atlas import atlas_correspondence
from .communication import score_ligand_receptor
from .deconvolution import (
    build_signatures,
    marker_pseudosignatures,
    marker_score_composition,
    method_concordance,
    nnls_deconvolve,
)
from .metrics import compute_metrics
from .qc import normalize_counts, run_qc
from .spatial import assign_domains, smooth_composition
from .targets import score_targets
from .types import AnalysisResult, SpatialDataset
from .uncertainty import composition_uncertainty

PIPELINE_VERSION = "0.2.0-baseline"


def _domain_name(domain_id: str, pack: dict) -> str:
    for zone in pack.get("zones", []):
        if zone["id"] == domain_id:
            return zone["name"]
    return "Unassigned" if domain_id == "unassigned" else domain_id


def _domain_color(domain_id: str, pack: dict) -> str:
    for zone in pack.get("zones", []):
        if zone["id"] == domain_id:
            return zone.get("color", "#8A938C")
    return "#4A4F4B"


def _top_items(values: dict[str, float], n: int = 4) -> list[dict]:
    return [
        {"id": key, "value": round(float(val), 4)}
        for key, val in sorted(values.items(), key=lambda kv: kv[1], reverse=True)[:n]
    ]


def run_pipeline(
    dataset: SpatialDataset,
    pack: dict,
    *,
    reference: pd.DataFrame | None = None,
    signatures: pd.DataFrame | None = None,
    params: dict[str, Any] | None = None,
) -> AnalysisResult:
    started = time.perf_counter()
    params = params or {}
    warnings: list[str] = []

    qc = run_qc(dataset.expression)
    warnings.extend(qc.get("warnings", []))
    passed = np.asarray(qc["passed"], dtype=bool)
    n_spots = len(dataset.barcodes)

    if passed.sum() >= 50:
        model_idx = np.where(passed)[0]
    else:
        model_idx = np.arange(n_spots)
        warnings.append("Too few spots passed QC; using all spots for modeling.")

    expression_model = dataset.expression.iloc[model_idx]
    coords_model = dataset.coordinates[model_idx]
    norm_all = normalize_counts(dataset.expression, log=True)
    norm_model = norm_all.iloc[model_idx]
    linear_model = normalize_counts(expression_model, log=False)

    method = "nnls"
    genes_used: list[str] = []
    if signatures is None:
        if reference is not None:
            try:
                signatures = build_signatures(reference)
            except Exception as exc:  # pragma: no cover - defensive
                warnings.append(f"Could not build reference signatures: {exc}")
                signatures = None
        if signatures is None:
            signatures = marker_pseudosignatures(pack, list(norm_model.columns))
            method = "marker_score"
            warnings.append(
                "No scRNA-seq reference supplied; using marker-score composition. "
                "This is not full deconvolution."
            )

    nnls_ran = True
    try:
        composition_model, residuals, genes_used = nnls_deconvolve(linear_model, signatures)
    except Exception as exc:
        nnls_ran = False
        warnings.append(f"NNLS failed ({exc}); falling back to marker scores.")
        composition_model = marker_score_composition(norm_model, pack)
        residuals = np.zeros(len(composition_model), dtype=float)
        method = "marker_score"

    smooth_model = smooth_composition(
        composition_model,
        coords_model,
        k=int(params.get("k_neighbors", 6)),
        alpha=float(params.get("smoothing_alpha", 0.45)),
    )

    domains_model, names_model, cluster_ids, _ = assign_domains(
        smooth_model,
        coords_model,
        norm_model,
        pack,
        random_state=int(params.get("random_state", 42)),
    )

    # Second, independent estimator (marker z-score softmax) — agreement between the
    # two feeds per-spot uncertainty, as in Glio-Cartography's Tangram–NNLS check.
    agreement = None
    concordance: dict[str, Any] | None = None
    if nnls_ran:
        secondary = marker_score_composition(norm_model, pack)
        try:
            agreement, concordance = method_concordance(
                composition_model,
                secondary,
                names=(
                    "nnls_reference" if method == "nnls" else "nnls_marker_pseudosignature",
                    "marker_zscore_softmax",
                ),
            )
        except ValueError as exc:
            warnings.append(f"Method concordance skipped: {exc}")
        if concordance and concordance["mean_spot_agreement"] < 0.7:
            warnings.append(
                "Low agreement between deconvolution methods "
                f"(mean {concordance['mean_spot_agreement']:.2f}); treat compositions as uncertain."
            )

    uncertainty_model = composition_uncertainty(composition_model, residuals, agreement)
    target_scores = score_targets(norm_model, composition_model, domains_model, pack)

    communication: list[dict[str, Any]] = []
    if pack.get("ligand_receptor_pairs"):
        communication = score_ligand_receptor(
            norm_model,
            composition_model,
            coords_model,
            domains_model,
            pack["ligand_receptor_pairs"],
            k=int(params.get("k_neighbors", 6)),
            n_permutations=int(params.get("lr_permutations", 199)),
            seed=int(params.get("random_state", 42)),
        )

    atlas_check: dict[str, Any] | None = None
    if pack.get("atlas_reference"):
        if dataset.metadata.get("synthetic"):
            atlas_check = {
                "name": pack["atlas_reference"].get("name", "External atlas"),
                "citation": pack["atlas_reference"].get("citation", ""),
                "status": "skipped_synthetic",
                "reason": "Not run on synthetic demo data: the comparison would be meaningless.",
            }
        else:
            zone_markers = {g for zone in pack.get("zones", []) for g in zone.get("markers", [])}
            atlas_check = atlas_correspondence(
                norm_model, domains_model, pack["atlas_reference"], exclude_genes=zone_markers
            )
            if atlas_check.get("status") == "ok" and (atlas_check.get("diagonal_mean") or 0) < 0.1:
                warnings.append(
                    "Predicted zones correspond weakly to the external atlas "
                    f"({atlas_check['name']}); zone labels are low-confidence."
                )

    cell_types = list(composition_model.columns)
    composition_all = pd.DataFrame(
        0.0, index=dataset.barcodes, columns=cell_types
    )
    composition_all.iloc[model_idx] = composition_model.to_numpy()
    smooth_all = pd.DataFrame(0.0, index=dataset.barcodes, columns=cell_types)
    smooth_all.iloc[model_idx] = smooth_model.to_numpy()

    domains_all = np.array(["unassigned"] * n_spots, dtype=object)
    domains_all[model_idx] = domains_model
    names_all = np.array(["Unassigned"] * n_spots, dtype=object)
    names_all[model_idx] = names_model
    uncertainty_all = np.ones(n_spots, dtype=float)
    uncertainty_all[model_idx] = uncertainty_model

    domains_summary: list[dict] = []
    for domain_id in sorted(set(domains_all), key=lambda d: (d == "unassigned", str(d))):
        mask = domains_all == domain_id
        if not mask.any():
            continue
        mean_comp = composition_all.loc[mask].mean().sort_values(ascending=False)
        domains_summary.append(
            {
                "id": str(domain_id),
                "name": _domain_name(str(domain_id), pack),
                "color": _domain_color(str(domain_id), pack),
                "count": int(mask.sum()),
                "pct": round(float(mask.mean()) * 100, 2),
                "mean_uncertainty": round(float(uncertainty_all[mask].mean()), 4),
                "top_cell_types": _top_items(mean_comp.to_dict(), 4),
            }
        )
    domains_summary.sort(key=lambda item: item["count"], reverse=True)

    composition_mean = composition_all.mean().sort_values(ascending=False)
    top_targets = [t for t in target_scores if t["detected"]][:3]

    metrics: dict = {}
    if dataset.ground_truth:
        gt = dataset.ground_truth
        gt_comp = gt.get("composition")
        gt_zones = gt.get("zones")
        if isinstance(gt_comp, pd.DataFrame) and gt_zones is not None:
            gt_model_comp = gt_comp.loc[dataset.barcodes].iloc[model_idx]
            gt_model_zones = np.asarray(gt_zones)[model_idx]
            try:
                metrics = compute_metrics(
                    composition_model, gt_model_comp, cluster_ids, gt_model_zones
                )
            except Exception as exc:  # pragma: no cover - defensive
                warnings.append(f"Could not compute benchmark metrics: {exc}")

    # Viewer payload (cap at 5,000 spots for very large samples).
    viewer_idx = np.arange(n_spots)
    if n_spots > 5000:
        viewer_idx = np.linspace(0, n_spots - 1, 5000, dtype=int)
        warnings.append("Viewer payload downsampled to 5,000 spots.")

    spots: list[dict] = []
    for i in viewer_idx:
        comp = composition_all.iloc[i]
        spots.append(
            {
                "barcode": dataset.barcodes[i],
                "x": round(float(dataset.coordinates[i, 0]), 4),
                "y": round(float(dataset.coordinates[i, 1]), 4),
                "domain": str(domains_all[i]),
                "domain_name": str(names_all[i]),
                "uncertainty": round(float(uncertainty_all[i]), 4),
                "qc_pass": bool(passed[i]),
                "composition": {
                    ct: round(float(comp[ct]), 4) for ct in cell_types
                },
            }
        )

    runtime = time.perf_counter() - started
    summary = {
        "sample_id": dataset.sample_id,
        "pipeline_version": PIPELINE_VERSION,
        "method": method,
        "n_spots": int(n_spots),
        "n_genes": int(dataset.expression.shape[1]),
        "passed_spots": int(passed.sum()),
        "modeled_spots": int(len(model_idx)),
        "n_domains": int(len(set(domains_model))),
        "n_cell_types": int(len(cell_types)),
        "dominant_cell_type": composition_mean.index[0] if len(composition_mean) else None,
        "composition_mean": {
            ct: round(float(val), 4) for ct, val in composition_mean.items()
        },
        "top_targets": [
            {
                "gene": t["gene"],
                "name": t["name"],
                "score": t["overall_score"],
                "evidence_level": t["evidence_level"],
            }
            for t in top_targets
        ],
        "runtime_seconds": round(runtime, 3),
        "synthetic": bool(dataset.metadata.get("synthetic", False)),
        "method_agreement": concordance["mean_spot_agreement"] if concordance else None,
        "significant_interactions": sum(1 for c in communication if c.get("significant")),
        "not_assessed": list(pack.get("not_assessed", [])),
        "disease_pack": {
            "id": pack.get("id"),
            "name": pack.get("name"),
            "version": pack.get("version"),
        },
        "warnings": warnings,
    }

    return AnalysisResult(
        sample_id=dataset.sample_id,
        pipeline_version=PIPELINE_VERSION,
        summary=summary,
        qc=qc,
        composition=composition_all,
        smoothed_composition=smooth_all,
        domains=domains_all,
        domain_names=list(names_all),
        uncertainty=uncertainty_all,
        target_scores=target_scores,
        spots=spots,
        domains_summary=domains_summary,
        metrics=metrics,
        warnings=warnings,
        artifacts={
            "genes_used": len(genes_used),
            "cluster_ids": [int(c) for c in cluster_ids],
        },
        communication=communication,
        validation={
            "method_concordance": concordance,
            "atlas_check": atlas_check,
        },
    )
