from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class SpatialDataset:
    """A spatial transcriptomics sample.

    expression: spots × genes raw counts (DataFrame, index=barcodes)
    coordinates: spots × 2 array in a consistent local coordinate system
    """

    sample_id: str
    barcodes: list[str]
    coordinates: np.ndarray
    expression: pd.DataFrame
    metadata: dict[str, Any] = field(default_factory=dict)
    image_path: str | None = None
    ground_truth: dict[str, Any] | None = None
    # QC computed on the full count matrix before gene selection (real samples).
    qc_stats: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if len(self.barcodes) != self.expression.shape[0]:
            raise ValueError("barcodes and expression rows must match")
        if self.coordinates.shape != (len(self.barcodes), 2):
            raise ValueError("coordinates must be spots × 2")


@dataclass
class AnalysisResult:
    sample_id: str
    pipeline_version: str
    summary: dict[str, Any]
    qc: dict[str, Any]
    composition: pd.DataFrame
    smoothed_composition: pd.DataFrame
    domains: np.ndarray
    domain_names: list[str]
    uncertainty: np.ndarray
    target_scores: list[dict[str, Any]]
    spots: list[dict[str, Any]]
    domains_summary: list[dict[str, Any]]
    metrics: dict[str, Any]
    warnings: list[str]
    artifacts: dict[str, Any] = field(default_factory=dict)
    communication: list[dict[str, Any]] = field(default_factory=list)
    validation: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        """JSON-safe payload for API storage."""
        return {
            "sample_id": self.sample_id,
            "pipeline_version": self.pipeline_version,
            "summary": self.summary,
            "qc": self.qc,
            "composition": _df_to_records(self.composition),
            "smoothed_composition": _df_to_records(self.smoothed_composition),
            "domains": [str(d) for d in self.domains],
            "domain_names": self.domain_names,
            "uncertainty": [round(float(x), 4) for x in self.uncertainty],
            "target_scores": self.target_scores,
            "spots": self.spots,
            "domains_summary": self.domains_summary,
            "metrics": self.metrics,
            "warnings": self.warnings,
            "artifacts": self.artifacts,
            "communication": self.communication,
            "validation": self.validation,
        }


def _df_to_records(df: pd.DataFrame) -> dict[str, list[float]]:
    return {
        col: [round(float(v), 5) for v in df[col].to_numpy()]
        for col in df.columns
    }
