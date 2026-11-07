from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import desc, func, select

from ..deps import CurrentAuth, DbSession
from ..disease_packs import list_packs
from ..models import Project, Run, Sample
from ..schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(auth: CurrentAuth, db: DbSession) -> DashboardSummary:
    org_id = auth.org.id
    active_projects = select(Project.id).where(
        Project.org_id == org_id,
        Project.archived.is_(False),
    )

    projects = int(
        db.scalar(select(func.count(Project.id)).where(Project.id.in_(active_projects))) or 0
    )
    samples = int(
        db.scalar(
            select(func.count(Sample.id)).where(
                Sample.org_id == org_id,
                Sample.project_id.in_(active_projects),
                Sample.archived.is_(False),
            )
        )
        or 0
    )
    runs = int(
        db.scalar(
            select(func.count(Run.id)).where(Run.org_id == org_id, Run.project_id.in_(active_projects))
        )
        or 0
    )

    completed = int(
        db.scalar(
            select(func.count(Run.id)).where(
                Run.org_id == org_id,
                Run.project_id.in_(active_projects),
                Run.status == "succeeded",
            )
        )
        or 0
    )
    failed = int(
        db.scalar(
            select(func.count(Run.id)).where(
                Run.org_id == org_id,
                Run.project_id.in_(active_projects),
                Run.status == "failed",
            )
        )
        or 0
    )
    spots = int(
        db.scalar(
            select(func.coalesce(func.sum(Sample.spot_count), 0)).where(
                Sample.org_id == org_id,
                Sample.project_id.in_(active_projects),
                Sample.archived.is_(False),
            )
        )
        or 0
    )
    recent = list(
        db.scalars(
            select(Run)
            .join(Project, Run.project_id == Project.id)
            .where(Run.org_id == org_id, Project.archived.is_(False))
            .order_by(desc(Run.created_at))
            .limit(6)
        )
    )
    return DashboardSummary(
        projects=projects,
        samples=samples,
        runs=runs,
        completed_runs=completed,
        failed_runs=failed,
        spots_analyzed=spots,
        recent_runs=recent,
        disease_packs=list_packs(),
    )
