from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..disease_packs import get_pack, list_packs, pack_summary

router = APIRouter(prefix="/disease-packs", tags=["disease-packs"])


@router.get("")
def packs(status: str | None = Query(default=None)) -> list[dict]:
    items = list_packs()
    if status:
        items = [item for item in items if item["status"] == status]
    return items


@router.get("/{pack_id}")
def pack_detail(pack_id: str) -> dict:
    try:
        pack = get_pack(pack_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Disease pack not found") from exc
    return {**pack_summary(pack), **pack}


@router.get("/{pack_id}/validation")
def pack_validation(pack_id: str) -> dict:
    try:
        pack = get_pack(pack_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Disease pack not found") from exc
    return {
        "id": pack["id"],
        "version": pack["version"],
        "status": pack["status"],
        "validation": pack.get("validation", {}),
        "note": (
            "Validated status requires benchmark thresholds and expert review. "
            "See docs/VALIDATION.md."
        ),
    }
