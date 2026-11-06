from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft7Validator

from .config import PACKS_DIR

ORDER = {"high": 0, "medium": 1, "low": 2}
_cache: dict[str, dict[str, Any]] | None = None


class PackError(ValueError):
    pass


def _schema() -> dict[str, Any]:
    with open(PACKS_DIR / "schema.json", encoding="utf-8") as fh:
        return json.load(fh)


def _load_file(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise PackError(f"{path.name}: root must be a mapping")
    return data


def load_packs(*, force: bool = False) -> dict[str, dict[str, Any]]:
    global _cache
    if _cache is not None and not force:
        return _cache

    schema = _schema()
    validator = Draft7Validator(schema)
    packs: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for path in sorted(PACKS_DIR.glob("*.yaml")):
        if path.name.startswith("._"):
            continue
        try:
            pack = _load_file(path)
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        validation_errors = sorted(validator.iter_errors(pack), key=lambda e: e.path)
        if validation_errors:
            for err in validation_errors:
                errors.append(f"{path.name}: {'/'.join(map(str, err.path))}: {err.message}")
            continue
        problems = _cross_check(pack)
        if problems:
            errors.extend(f"{path.name}: {problem}" for problem in problems)
            continue
        try:
            _resolve_atlas(pack)
        except (OSError, ValueError) as exc:
            errors.append(f"{path.name}: atlas_reference: {exc}")
            continue
        from .references import validate_pack_files

        file_problems = validate_pack_files(pack)
        if file_problems:
            errors.extend(f"{path.name}: {problem}" for problem in file_problems)
            continue
        pack_id = pack["id"]
        if pack_id in packs:
            errors.append(f"{path.name}: duplicate pack id '{pack_id}'")
            continue
        packs[pack_id] = pack
    if errors:
        raise PackError("; ".join(errors))
    _cache = packs
    return packs


def _cross_check(pack: dict[str, Any]) -> list[str]:
    """References inside a pack must point at its own cell types and zones."""
    problems: list[str] = []
    cell_ids = {ct["id"] for ct in pack.get("cell_types", [])}
    zone_ids = {zone["id"] for zone in pack.get("zones", [])}
    for i, pair in enumerate(pack.get("ligand_receptor_pairs", [])):
        for key in ("sender", "receiver"):
            if pair.get(key) not in cell_ids:
                problems.append(f"ligand_receptor_pairs/{i}/{key}: unknown cell type '{pair.get(key)}'")
    for zone_id in (pack.get("atlas_reference") or {}).get("zone_map", {}):
        if zone_id not in zone_ids:
            problems.append(f"atlas_reference/zone_map: unknown zone '{zone_id}'")
    return problems


def _resolve_atlas(pack: dict[str, Any]) -> None:
    """Load the atlas JSON next to the pack into ``atlas_reference['data']``."""
    atlas = pack.get("atlas_reference")
    if not atlas:
        return
    path = (PACKS_DIR / atlas["file"]).resolve()
    if PACKS_DIR.resolve() not in path.parents:
        raise ValueError("file must stay inside packages/disease-packs")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    genes = data.get("genes")
    if not isinstance(genes, dict) or not genes:
        raise ValueError("reference file has no 'genes' table")
    structures = set(atlas["zone_map"].values())
    for gene, values in genes.items():
        if not structures.issubset(values):
            raise ValueError(f"gene {gene} lacks structures {sorted(structures - set(values))}")
    atlas["data"] = {"genes": genes, "meta": data.get("_meta", {})}


def list_packs() -> list[dict[str, Any]]:
    packs = load_packs().values()
    return sorted(
        (pack_summary(p) for p in packs),
        key=lambda p: (ORDER.get(p["data_richness"], 9), p["name"]),
    )


def pack_summary(pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": pack["id"],
        "version": pack["version"],
        "status": pack["status"],
        "name": pack["name"],
        "short_name": pack.get("short_name", pack["name"]),
        "tissue": pack["tissue"],
        "data_richness": pack["data_richness"],
        "color": pack.get("color", "#5FE0C0"),
        "description": pack.get("description", "").strip(),
        "aliases": pack.get("aliases", []),
        "cell_type_count": len(pack.get("cell_types", [])),
        "zone_count": len(pack.get("zones", [])),
        "target_count": len(pack.get("targets", [])),
        "ligand_receptor_count": len(pack.get("ligand_receptor_pairs", [])),
        "has_reference_signatures": bool((pack.get("reference") or {}).get("signatures")),
        "domain_model": (
            {"version": pack["domain_model"].get("version"), "card": pack["domain_model"].get("card")}
            if pack.get("domain_model")
            else None
        ),
        "not_assessed": pack.get("not_assessed", []),
        "atlas_reference": (
            {
                key: pack["atlas_reference"].get(key)
                for key in ("name", "citation", "url", "license_status")
            }
            if pack.get("atlas_reference")
            else None
        ),
        "reference": pack.get("reference", {}),
        "validation": pack.get("validation", {}),
    }


def get_pack(pack_id: str) -> dict[str, Any]:
    packs = load_packs()
    if pack_id not in packs:
        raise KeyError(pack_id)
    return packs[pack_id]


def validate_all() -> list[str]:
    try:
        load_packs(force=True)
    except PackError as exc:
        return [str(exc)]
    return []


def packs_dir() -> Path:
    return PACKS_DIR
