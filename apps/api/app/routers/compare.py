from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from ..deps import CurrentAuth, DbSession
from ..models import Result, Run
from ..schemas import RunComparisonOut
from ..services.compare import build_comparison
from .runs import _get_run

# Registered before the runs router so `/runs/compare` is not read as `/runs/{run_id}`.
router = APIRouter(tags=["runs"])


def _finished_payload(db, run: Run) -> dict:
    if run.status != "succeeded":
        raise HTTPException(
            status_code=409,
            detail=f"Run {run.id[:8]} is {run.status}; only succeeded runs can be compared",
        )
    result = db.scalar(select(Result).where(Result.run_id == run.id))
    if result is None:
        raise HTTPException(status_code=409, detail=f"Results missing for run {run.id[:8]}")
    return result.payload


@router.get("/runs/compare", response_model=RunComparisonOut)
def compare_runs(
    auth: CurrentAuth,
    db: DbSession,
    a: str = Query(min_length=1, max_length=64, description="Run shown on the left (A)"),
    b: str = Query(min_length=1, max_length=64, description="Run shown on the right (B)"),
) -> dict:
    """Side-by-side view of two succeeded runs, read from stored results (no re-analysis)."""
    if a == b:
        raise HTTPException(status_code=400, detail="Choose two different runs to compare")
    # Resolve both before checking status, so a foreign run is always a plain 404.
    run_a = _get_run(db, auth, a)
    run_b = _get_run(db, auth, b)
    payload_a = _finished_payload(db, run_a)
    payload_b = _finished_payload(db, run_b)
    return build_comparison(run_a, payload_a, run_b, payload_b)
