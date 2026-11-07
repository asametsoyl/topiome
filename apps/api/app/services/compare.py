"""Side-by-side comparison of two finished runs (port of Glio-Cartography's
multi-patient comparison).

Everything here is read from the stored ``Result.payload``; no analysis is
re-run. The output is descriptive: each side is one tissue section, so no
statistical test is applied between them.
"""

from __future__ import annotations

from typing import Any

from ..disease_packs import get_pack
from ..models import Run

NOTE = (
    "Descriptive side-by-side view of two analysed sections (one section per side). "
    "No statistical test is applied between them; differences are not a basis for "
    "diagnosis, prognosis or treatment decisions."
)


def _pack_zone_ids(pack_id: str) -> set[str] | None:
    try:
        pack = get_pack(pack_id)
    except KeyError:
        return None
    return {str(zone["id"]) for zone in pack.get("zones", [])}


def _pack_name(run: Run, payload: dict[str, Any]) -> str:
    name = (payload.get("summary") or {}).get("disease_pack", {}).get("name")
    if name:
        return str(name)
    try:
        return str(get_pack(run.disease_pack)["name"])
    except KeyError:
        return run.disease_pack


def _side(run: Run, payload: dict[str, Any], label: str) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    communication = payload.get("communication") or []
    concordance = (payload.get("validation") or {}).get("method_concordance") or {}
    agreement = summary.get("method_agreement")
    if agreement is None:
        agreement = concordance.get("mean_spot_agreement")
    significant = summary.get("significant_interactions")
    if significant is None:
        significant = sum(1 for item in communication if item.get("significant"))
    sample = run.sample
    return {
        "label": label,
        "run_id": run.id,
        "sample_id": run.sample_id,
        "sample_name": run.sample.name if run.sample else None,
        "platform": (sample.platform or "unknown") if sample else "unknown",
        "species": (sample.species or "unknown") if sample else "unknown",
        "condition": (sample.condition or "unspecified") if sample else "unspecified",
        "project_id": run.project_id,
        "disease_pack": run.disease_pack,
        "pack_name": _pack_name(run, payload),
        "pack_version": run.pack_version,
        "pipeline_version": run.pipeline_version,
        "created_at": run.created_at,
        "finished_at": run.finished_at,
        "synthetic": bool(summary.get("synthetic", False)),
        "n_spots": int(summary.get("n_spots", 0)),
        "modeled_spots": int(summary.get("modeled_spots", summary.get("n_spots", 0))),
        "n_domains": int(summary.get("n_domains", 0)),
        "n_cell_types": int(summary.get("n_cell_types", 0)),
        "method_agreement": agreement,
        "tested_interactions": sum(1 for item in communication if item.get("tested")),
        "significant_interactions": int(significant),
        "warnings": list(summary.get("warnings") or []),
        "not_assessed": list(summary.get("not_assessed") or []),
    }


def _warnings(run_a: Run, side_a: dict, run_b: Run, side_b: dict) -> list[str]:
    warnings: list[str] = []
    if run_a.disease_pack != run_b.disease_pack:
        warnings.append(
            f"Runs use different disease packs ({side_a['pack_name']} vs {side_b['pack_name']}). "
            "Only cell types, domains and ligand–receptor pairs defined in both packs are "
            "aligned; the rest are shown for one side only."
        )
    elif run_a.pack_version != run_b.pack_version:
        warnings.append(
            f"Runs use different versions of the {side_a['pack_name']} pack "
            f"({run_a.pack_version} vs {run_b.pack_version}). Cell-type, domain or pair "
            "definitions may have changed between versions."
        )
    if run_a.pipeline_version != run_b.pipeline_version:
        warnings.append(
            f"Runs were produced by different pipeline versions "
            f"({run_a.pipeline_version} vs {run_b.pipeline_version})."
        )
    if side_a["platform"].casefold() != side_b["platform"].casefold():
        warnings.append(
            f"Runs use different assay platforms ({side_a['platform']} vs {side_b['platform']}); "
            "spot and cell-level quantities may not be directly comparable."
        )
    if side_a["species"].casefold() != side_b["species"].casefold():
        warnings.append(
            f"Runs use different species ({side_a['species']} vs {side_b['species']}); "
            "gene and cell-type definitions may not be equivalent."
        )
    if side_a["condition"].casefold() != side_b["condition"].casefold():
        warnings.append(
            f"Runs have different recorded conditions ({side_a['condition']} vs "
            f"{side_b['condition']}); differences are descriptive, not a statistical test."
        )
    if run_a.sample_id == run_b.sample_id:
        warnings.append(
            "Both runs analyse the same sample; differences come from parameters or "
            "versions, not from the tissue."
        )
    if side_a["synthetic"] and side_b["synthetic"]:
        warnings.append(
            "Both runs use synthetic demo data; differences reflect simulation settings, "
            "not tissue biology."
        )
    elif side_a["synthetic"] or side_b["synthetic"]:
        synthetic, uploaded = ("A", "B") if side_a["synthetic"] else ("B", "A")
        warnings.append(
            f"Run {synthetic} uses synthetic demo data and run {uploaded} an uploaded sample; "
            "the comparison is not biologically meaningful."
        )
    return warnings


def _composition(payload_a: dict, payload_b: dict) -> list[dict[str, Any]]:
    mean_a = (payload_a.get("summary") or {}).get("composition_mean") or {}
    mean_b = (payload_b.get("summary") or {}).get("composition_mean") or {}
    rows = []
    for cell_type in dict.fromkeys([*mean_a, *mean_b]):
        a = mean_a.get(cell_type)
        b = mean_b.get(cell_type)
        delta = round(float(b) - float(a), 4) if a is not None and b is not None else None
        rows.append({"cell_type": cell_type, "a": a, "b": b, "delta": delta})
    # Largest shifts first; cell types defined on one side only go last.
    rows.sort(key=lambda r: (r["delta"] is None, -abs(r["delta"] or 0.0), r["cell_type"]))
    return rows


def _domains(run_a: Run, payload_a: dict, run_b: Run, payload_b: dict) -> list[dict[str, Any]]:
    by_a = {str(d["id"]): d for d in payload_a.get("domains_summary") or []}
    by_b = {str(d["id"]): d for d in payload_b.get("domains_summary") or []}
    same_pack = run_a.disease_pack == run_b.disease_pack
    zones_a = _pack_zone_ids(run_a.disease_pack)
    zones_b = _pack_zone_ids(run_b.disease_pack)

    def defined(domain_id: str, zones: set[str] | None) -> bool:
        # A domain absent from the summary had zero spots if the pack defines it.
        return same_pack or domain_id == "unassigned" or (zones is not None and domain_id in zones)

    rows = []
    for domain_id in dict.fromkeys([*by_a, *by_b]):
        da, db = by_a.get(domain_id), by_b.get(domain_id)
        ref = da or db or {}
        row: dict[str, Any] = {
            "id": domain_id,
            "name": ref.get("name", domain_id),
            "color": ref.get("color"),
        }
        for key, found, zones in (("a", da, zones_a), ("b", db, zones_b)):
            if found is not None:
                row[f"{key}_count"] = int(found.get("count", 0))
                row[f"{key}_pct"] = float(found.get("pct", 0.0))
            elif defined(domain_id, zones):
                row[f"{key}_count"] = 0
                row[f"{key}_pct"] = 0.0
            else:
                row[f"{key}_count"] = None
                row[f"{key}_pct"] = None
        if row["a_pct"] is not None and row["b_pct"] is not None:
            row["delta_pct"] = round(row["b_pct"] - row["a_pct"], 2)
        else:
            row["delta_pct"] = None
        rows.append(row)
    rows.sort(
        key=lambda r: (
            r["id"] == "unassigned",
            -max(r["a_pct"] or 0.0, r["b_pct"] or 0.0),
            r["name"],
        )
    )
    return rows


def _interaction_side(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    return {
        "tested": bool(item.get("tested")),
        "score": item.get("score"),
        "p_value": item.get("p_value"),
        "q_value": item.get("q_value"),
        "significant": bool(item.get("significant")),
        "missing": list(item.get("missing") or []),
    }


def _communication(payload_a: dict, payload_b: dict) -> list[dict[str, Any]]:
    by_a = {str(i["id"]): i for i in payload_a.get("communication") or []}
    by_b = {str(i["id"]): i for i in payload_b.get("communication") or []}
    rows = []
    for pair_id in dict.fromkeys([*by_a, *by_b]):
        ref = by_a.get(pair_id) or by_b[pair_id]
        rows.append(
            {
                "id": pair_id,
                "name": ref.get("name", pair_id),
                "ligand": ref.get("ligand", ""),
                "receptor": ref.get("receptor", ""),
                "sender": ref.get("sender", ""),
                "receiver": ref.get("receiver", ""),
                "category": ref.get("category") or "",
                "a": _interaction_side(by_a.get(pair_id)),
                "b": _interaction_side(by_b.get(pair_id)),
            }
        )

    def sort_key(row: dict[str, Any]) -> tuple:
        sides = [s for s in (row["a"], row["b"]) if s is not None]
        q_values = [s["q_value"] for s in sides if s["q_value"] is not None]
        return (
            not any(s["significant"] for s in sides),
            min(q_values) if q_values else 1.0,
            row["name"],
        )

    rows.sort(key=sort_key)
    return rows


def build_comparison(
    run_a: Run, payload_a: dict[str, Any], run_b: Run, payload_b: dict[str, Any]
) -> dict[str, Any]:
    side_a = _side(run_a, payload_a, "A")
    side_b = _side(run_b, payload_b, "B")
    return {
        "a": side_a,
        "b": side_b,
        "same_pack": run_a.disease_pack == run_b.disease_pack,
        "same_pack_version": (
            run_a.disease_pack == run_b.disease_pack and run_a.pack_version == run_b.pack_version
        ),
        "warnings": _warnings(run_a, side_a, run_b, side_b),
        "composition": _composition(payload_a, payload_b),
        "domains": _domains(run_a, payload_a, run_b, payload_b),
        "communication": _communication(payload_a, payload_b),
        "note": NOTE,
    }
