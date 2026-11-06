"""Run queue.

``QUEUE_MODE=inline`` (development): runs execute in the API process after the
response is sent. ``QUEUE_MODE=worker`` (production): the API only records
queued runs and one or more ``python -m app.worker`` processes execute them.
Claiming is atomic (queued → running in one UPDATE), so several workers can
share the database safely.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import BackgroundTasks
from sqlalchemy import select, update

from ..config import settings
from ..db import SessionLocal
from ..models import Run
from .pipeline import execute_run

INTERRUPTED = "The service restarted while this run was in progress. Start it again with Re-run."


def enqueue(run_id: str, background: BackgroundTasks) -> None:
    if settings.queue_mode == "inline":
        background.add_task(execute_run, run_id)
    # worker mode: the run stays "queued" until a worker claims it.


def next_queued_run_id() -> str | None:
    with SessionLocal() as db:
        return db.scalar(
            select(Run.id).where(Run.status == "queued").order_by(Run.created_at).limit(1)
        )


def recover_interrupted_runs(*, stale_after: timedelta | None = None) -> int:
    """Fail runs whose executor died. Returns how many were changed.

    Inline mode calls this at API start-up: any run still queued or running
    belonged to the previous process. Workers call it with ``stale_after`` and
    only touch runs that have been running suspiciously long.
    """
    now = datetime.now(UTC)
    values = {
        "status": "failed",
        "stage": "failed",
        "error_code": "interrupted",
        "error_message": INTERRUPTED,
        "finished_at": now,
    }
    with SessionLocal() as db:
        if stale_after is None:
            statement = update(Run).where(Run.status.in_(["queued", "running"]))
        else:
            statement = update(Run).where(
                Run.status == "running", Run.started_at < now - stale_after
            )
        changed = db.execute(statement.values(**values)).rowcount
        db.commit()
        return int(changed or 0)
