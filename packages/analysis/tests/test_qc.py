from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.qc import normalize_counts, run_qc


def test_normalize_counts_cp10k_is_library_size_normalized():
    frame = pd.DataFrame(
        {
            "A": [1.0, 10.0, 100.0],
            "B": [3.0, 30.0, 300.0],
            "C": [6.0, 60.0, 600.0],
        },
        index=["s1", "s2", "s3"],
    )
    linear = normalize_counts(frame, log=False)
    np.testing.assert_allclose(linear.sum(axis=1).to_numpy(), 10_000, rtol=1e-9)

    logged = normalize_counts(frame, log=True)
    np.testing.assert_allclose(np.expm1(logged).sum(axis=1).to_numpy(), 10_000, rtol=1e-6)


def test_qc_flags_low_count_spots():
    frame = pd.DataFrame(
        np.full((4, 10), 20.0),
        index=["good-1", "good-2", "low", "good-3"],
        columns=[f"G{i}" for i in range(10)],
    )
    frame.loc["low", :] = 0.2

    result = run_qc(frame, min_counts=100, min_genes=5)

    assert result["passed"] == [True, True, False, True]
    assert result["summary"]["passed_spots"] == 3
    assert result["summary"]["median_counts"] > 0
