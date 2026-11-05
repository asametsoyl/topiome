from __future__ import annotations

import numpy as np
import pandas as pd


def _scale(values: np.ndarray) -> np.ndarray:
    lo = float(np.nanmin(values)) if len(values) else 0.0
    hi = float(np.nanmax(values)) if len(values) else 0.0
    if hi - lo < 1e-8:
        return np.zeros_like(values)
    return (values - lo) / (hi - lo)


def score_targets(
    expression_norm: pd.DataFrame,
    composition: pd.DataFrame,
    domain_ids: np.ndarray,
    pack: dict,
) -> list[dict]:
    """Score disease-pack target genes by domain and cell type.

    This is a research prioritization score, not a therapeutic recommendation.
    """
    results: list[dict] = []
    expr = expression_norm.to_numpy(dtype=float)
    gene_index = {g: i for i, g in enumerate(expression_norm.columns)}

    for target in pack.get("targets", []):
        gene = target.get("gene", "")
        entry = {
            "gene": gene,
            "name": target.get("name", gene),
            "rationale": target.get("rationale", ""),
            "evidence_level": target.get("evidence_level", "exploratory"),
            "detected": gene in gene_index,
            "overall_score": 0.0,
            "by_domain": {},
            "by_cell_type": {},
        }
        if gene not in gene_index:
            results.append(entry)
            continue

        values = expr[:, gene_index[gene]]
        entry["overall_score"] = round(float(_scale(values).mean()), 4)

        domain_scores: dict[str, float] = {}
        for domain in sorted(set(domain_ids)):
            mask = domain_ids == domain
            if mask.any():
                domain_scores[str(domain)] = float(values[mask].mean())
        scaled_domains = _scale(np.array(list(domain_scores.values())))
        entry["by_domain"] = {
            key: round(float(val), 4)
            for key, val in zip(domain_scores.keys(), scaled_domains, strict=True)
        }

        comp_values = composition.to_numpy(dtype=float)
        totals = comp_values.sum(axis=0)
        weighted = np.divide(
            comp_values.T @ values,
            totals,
            out=np.zeros_like(totals),
            where=totals > 0,
        )
        scaled_cell_types = _scale(weighted)
        entry["by_cell_type"] = {
            str(ct): round(float(val), 4)
            for ct, val in zip(composition.columns, scaled_cell_types, strict=True)
        }
        results.append(entry)

    results.sort(key=lambda item: (item["detected"], item["overall_score"]), reverse=True)
    return results
