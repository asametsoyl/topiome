from __future__ import annotations

import numpy as np
import pandas as pd


def composition_uncertainty(
    composition: pd.DataFrame,
    residuals: np.ndarray,
    agreement: np.ndarray | None = None,
) -> np.ndarray:
    """Per-spot uncertainty in [0, 1]. Higher = less certain.

    Combines normalized Shannon entropy of cell-type weights, the NNLS
    relative residual and — when a second method ran — disagreement between
    the two composition estimates (1 − agreement).
    """
    values = composition.to_numpy(dtype=float)
    k = values.shape[1]
    if k <= 1:
        entropy = np.zeros(len(values))
    else:
        safe = np.clip(values, 1e-12, None)
        entropy = -(safe * np.log(safe)).sum(axis=1) / np.log(k)
    residual = np.asarray(residuals, dtype=float)
    res_lo, res_hi = np.percentile(residual, [5, 95]) if len(residual) else (0, 1)
    if res_hi - res_lo < 1e-8:
        residual_scaled = np.zeros_like(residual)
    else:
        residual_scaled = np.clip((residual - res_lo) / (res_hi - res_lo), 0, 1)
    if agreement is None:
        combined = 0.65 * np.clip(entropy, 0, 1) + 0.35 * residual_scaled
    else:
        disagreement = np.clip(1.0 - np.asarray(agreement, dtype=float), 0, 1)
        combined = (
            0.5 * np.clip(entropy, 0, 1) + 0.25 * residual_scaled + 0.25 * disagreement
        )
    return np.clip(combined, 0, 1)
