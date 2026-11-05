"""Topiome analysis engine.

Baseline spatial transcriptomics pipeline:
  QC → normalize → NNLS deconvolution → spatial smoothing → domains →
  target scoring → uncertainty → summary.

Heavy models (Cell2location, Tangram, GraphST, STAGATE) are optional adapters.
"""

from .io import load_visium
from .pipeline import run_pipeline
from .synthetic import generate_demo_dataset
from .types import AnalysisResult, SpatialDataset

__all__ = [
    "AnalysisResult",
    "SpatialDataset",
    "generate_demo_dataset",
    "load_visium",
    "run_pipeline",
]
__version__ = "0.1.0"
