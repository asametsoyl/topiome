"""Versioned reference data shipped next to disease packs.

* ``reference.signatures``: scRNA-derived cell-type signatures (CSV) used for
  NNLS deconvolution of real samples.
* ``domain_model``: a trained spatial GNN (NumPy weights + model card) that
  labels tissue domains on real samples.

Both are pinned by file hash in every run's provenance.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
from analysis.gnn import DomainModel

from .config import PACKS_DIR


def _resolve(relative: str) -> Path:
    path = (PACKS_DIR / relative).resolve()
    if PACKS_DIR.resolve() not in path.parents:
        raise ValueError(f"{relative}: must stay inside packages/disease-packs")
    if not path.exists():
        raise FileNotFoundError(f"{relative}: file not found")
    return path


@dataclass
class ReferenceSignatures:
    table: pd.DataFrame  # cell types × genes, fraction of transcripts
    version: str
    sha256: str
    file: str
    card: dict[str, Any] = field(default_factory=dict)


@lru_cache(maxsize=16)
def _load_signatures(file: str, card_file: str | None, version: str) -> ReferenceSignatures:
    path = _resolve(file)
    table = pd.read_csv(path, index_col=0)
    table.columns = [str(c).upper() for c in table.columns]
    table.index = [str(i) for i in table.index]
    card = json.loads(_resolve(card_file).read_text(encoding="utf-8")) if card_file else {}
    return ReferenceSignatures(
        table=table,
        version=version,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        file=file,
        card=card,
    )


def signatures_for(pack: dict[str, Any]) -> ReferenceSignatures | None:
    spec = (pack.get("reference") or {}).get("signatures")
    if not spec:
        return None
    version = str((pack.get("reference") or {}).get("version") or spec.get("version") or "unversioned")
    return _load_signatures(spec["file"], spec.get("card"), version)


@lru_cache(maxsize=16)
def _load_domain_model(file: str, card: str) -> DomainModel:
    return DomainModel.load(_resolve(file), _resolve(card))


def domain_model_for(pack: dict[str, Any]) -> DomainModel | None:
    spec = pack.get("domain_model")
    if not spec:
        return None
    return _load_domain_model(spec["file"], spec["card"])


def reference_genes(pack: dict[str, Any]) -> set[str]:
    """Genes the shipped signatures and domain model need from every sample."""
    genes: set[str] = set()
    signatures = signatures_for(pack)
    if signatures is not None:
        genes.update(signatures.table.columns)
    model = domain_model_for(pack)
    if model is not None:
        genes.update(g.upper() for g in model.genes)
    return genes


def validate_pack_files(pack: dict[str, Any]) -> list[str]:
    """Problems with the pack's reference files (used when packs are loaded)."""
    problems: list[str] = []
    try:
        signatures = signatures_for(pack)
        if signatures is not None:
            unknown = set(signatures.table.index) - {ct["id"] for ct in pack.get("cell_types", [])}
            if unknown:
                problems.append(f"reference.signatures: unknown cell types {sorted(unknown)}")
    except (OSError, ValueError, KeyError) as exc:
        problems.append(f"reference.signatures: {exc}")
    try:
        model = domain_model_for(pack)
        if model is not None:
            unknown = set(model.classes) - {zone["id"] for zone in pack.get("zones", [])}
            if unknown:
                problems.append(f"domain_model: classes {sorted(unknown)} are not pack zones")
    except (OSError, ValueError, KeyError) as exc:
        problems.append(f"domain_model: {exc}")
    return problems
