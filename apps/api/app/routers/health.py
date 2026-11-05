from __future__ import annotations

import os
from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import text

from ..db import SessionLocal
from ..services.storage import storage

router = APIRouter(tags=["health"])
VERSION = "0.1.0"


@router.get("/health")
def health() -> dict:
    db_ok = True
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    storage_ok = storage.base.exists()
    status = "ok" if db_ok and storage_ok else "degraded"
    return {
        "status": status,
        "version": VERSION,
        "service": "topiome-api",
        "db": db_ok,
        "storage": storage_ok,
        "timestamp": datetime.now(UTC).isoformat(),
        "pid": os.getpid(),
    }


@router.get("/version")
def version() -> dict:
    return {
        "name": "Topiome API",
        "version": VERSION,
        "environment": os.getenv("APP_ENV", "development"),
    }
