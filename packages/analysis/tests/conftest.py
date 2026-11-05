from __future__ import annotations

from pathlib import Path

import pytest
import yaml

PACKS_DIR = Path(__file__).resolve().parents[2] / "disease-packs"


@pytest.fixture(scope="session")
def packs_dir() -> Path:
    if not PACKS_DIR.is_dir():
        pytest.skip(f"disease packs not found: {PACKS_DIR}")
    return PACKS_DIR


@pytest.fixture(scope="session")
def breast_pack(packs_dir: Path) -> dict:
    with open(packs_dir / "breast.yaml", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@pytest.fixture(scope="session")
def all_packs(packs_dir: Path) -> dict[str, dict]:
    packs: dict[str, dict] = {}
    for path in sorted(packs_dir.glob("*.yaml")):
        if path.name.startswith("._"):
            continue
        with open(path, encoding="utf-8") as handle:
            pack = yaml.safe_load(handle)
        packs[pack["id"]] = pack
    return packs
