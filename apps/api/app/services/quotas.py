"""Plan quotas.

Limits are enforced at write time, not by hiding the UI. ``None`` means
unlimited. Counts are deliberately simple SQL aggregates; a usage dashboard can
read the same function.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Invitation, Membership, Project, Run, Sample, SampleFile

PLAN_LIMITS: dict[str, dict[str, int | None]] = {
    "academic": {
        "projects": 3,
        "samples": 20,
        "runs_per_month": 50,
        "storage_mb": 5 * 1024,
        "members": 1,
    },
    "lab": {
        "projects": 30,
        "samples": 500,
        "runs_per_month": 1000,
        "storage_mb": 100 * 1024,
        "members": 10,
    },
    "institution": {
        "projects": None,
        "samples": None,
        "runs_per_month": None,
        "storage_mb": None,
        "members": None,
    },
}

PLAN_ORDER = ["academic", "lab", "institution"]


class QuotaExceeded(Exception):
    def __init__(self, resource: str, used: int, limit: int):
        self.resource = resource
        self.used = used
        self.limit = limit
        super().__init__(f"Plan limit reached for {resource}: {used}/{limit}")


def limits_for(plan: str) -> dict[str, int | None]:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["academic"])


def _month_start() -> datetime:
    now = datetime.now(UTC)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def org_usage(db: Session, org_id: str) -> dict[str, int]:
    projects = int(
        db.scalar(
            select(func.count(Project.id)).where(
                Project.org_id == org_id, Project.archived.is_(False)
            )
        )
        or 0
    )
    samples = int(
        db.scalar(
            select(func.count(Sample.id)).where(
                Sample.org_id == org_id, Sample.archived.is_(False)
            )
        )
        or 0
    )
    runs = int(
        db.scalar(
            select(func.count(Run.id)).where(
                Run.org_id == org_id, Run.created_at >= _month_start()
            )
        )
        or 0
    )
    members = int(
        db.scalar(select(func.count(Membership.id)).where(Membership.org_id == org_id)) or 0
    )
    storage_bytes = int(
        db.scalar(
            select(func.coalesce(func.sum(SampleFile.size_bytes), 0))
            .join(Sample, Sample.id == SampleFile.sample_id)
            .where(Sample.org_id == org_id)
        )
        or 0
    )
    return {
        "projects": projects,
        "samples": samples,
        "runs_per_month": runs,
        "members": members,
        "storage_mb": storage_bytes // (1024 * 1024),
    }


def usage_snapshot(db: Session, org_id: str, plan: str) -> dict:
    used = org_usage(db, org_id)
    limits = limits_for(plan)
    return {
        "plan": plan,
        "limits": limits,
        "used": used,
        "resources": {
            key: {
                "used": used.get(key, 0),
                "limit": limits.get(key),
                "remaining": (
                    None
                    if limits.get(key) is None
                    else max(int(limits[key]) - used.get(key, 0), 0)
                ),
            }
            for key in limits
        },
    }


def _ensure(resource: str, used: int, limit: int | None) -> None:
    if limit is not None and used >= limit:
        raise QuotaExceeded(resource, used, int(limit))


def ensure_project(db: Session, org_id: str, plan: str) -> None:
    _ensure("projects", org_usage(db, org_id)["projects"], limits_for(plan)["projects"])


def ensure_sample(db: Session, org_id: str, plan: str) -> None:
    _ensure("samples", org_usage(db, org_id)["samples"], limits_for(plan)["samples"])


def ensure_run(db: Session, org_id: str, plan: str) -> None:
    _ensure(
        "runs_per_month",
        org_usage(db, org_id)["runs_per_month"],
        limits_for(plan)["runs_per_month"],
    )


def ensure_storage(db: Session, org_id: str, plan: str, extra_bytes: int = 0) -> None:
    used_bytes = int(
        db.scalar(
            select(func.coalesce(func.sum(SampleFile.size_bytes), 0))
            .join(Sample, Sample.id == SampleFile.sample_id)
            .where(Sample.org_id == org_id)
        )
        or 0
    )
    limit_mb = limits_for(plan)["storage_mb"]
    limit_bytes = None if limit_mb is None else int(limit_mb) * 1024 * 1024
    if limit_bytes is not None and used_bytes + max(extra_bytes, 0) > limit_bytes:
        raise QuotaExceeded("storage_mb", used_bytes // (1024 * 1024), int(limit_mb))


def ensure_member(db: Session, org_id: str, plan: str) -> None:
    pending = int(
        db.scalar(
            select(func.count(Invitation.id)).where(
                Invitation.org_id == org_id,
                Invitation.accepted_at.is_(None),
                Invitation.expires_at > datetime.now(UTC),
            )
        )
        or 0
    )
    current = org_usage(db, org_id)["members"]
    _ensure("members", current + pending, limits_for(plan)["members"])
