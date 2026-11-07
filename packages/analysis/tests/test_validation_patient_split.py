from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "validation"))

from wu2021_common import (  # noqa: E402
    TEST_PATIENTS,
    TRAIN_PATIENTS,
    VISIUM_PATIENTS,
    validate_patient_split,
)


def test_wu_patient_split_is_disjoint_complete_and_alias_safe() -> None:
    validate_patient_split(TRAIN_PATIENTS, TEST_PATIENTS, VISIUM_PATIENTS)


@pytest.mark.parametrize(
    ("train", "test", "available", "message"),
    [
        (["CID4290", "CID4290"], ["CID4465"], ["CID4290", "CID4465"], "duplicate"),
        (["CID4290"], ["CID4290"], ["CID4290"], "overlaps"),
        (["CID4290"], ["CID4465"], ["CID4290", "CID4465", "CID4535"], "cover"),
        (["CID4290A"], ["CID4290"], ["CID4290A", "CID4290"], "aliases"),
    ],
)
def test_patient_split_rejects_leakage_and_incomplete_partition(
    train: list[str], test: list[str], available: list[str], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_patient_split(train, test, available)
