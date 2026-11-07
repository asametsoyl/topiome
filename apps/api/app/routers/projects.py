from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy import desc, func, select

from ..deps import AnalystAuth, CurrentAuth, DbSession, log_audit
from ..disease_packs import get_pack
from ..models import Project, Run, Sample
from ..schemas import ProjectCreate, ProjectDetail, ProjectOut, ProjectUpdate
from ..services.quotas import QuotaExceeded, ensure_project

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_project(db, auth: CurrentAuth, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.org_id != auth.org.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(
    auth: CurrentAuth,
    db: DbSession,
    include_archived: bool = Query(default=False),
) -> list[Project]:
    stmt = select(Project).where(Project.org_id == auth.org.id)
    if not include_archived:
        stmt = stmt.where(Project.archived.is_(False))
    return list(db.scalars(stmt.order_by(desc(Project.updated_at))))


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    request: Request,
    auth: AnalystAuth,
    db: DbSession,
) -> Project:
    try:
        get_pack(payload.disease_pack)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail="Unknown disease pack") from exc

    try:
        ensure_project(db, auth.org.id, auth.org.plan)
    except QuotaExceeded as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc

    project = Project(
        org_id=auth.org.id,
        name=payload.name,
        description=payload.description,
        disease_pack=payload.disease_pack,
        created_by=auth.user.id,
    )
    db.add(project)
    db.flush()
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="project.create",
        resource_type="project",
        resource_id=project.id,
        request=request,
    )
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: str, auth: CurrentAuth, db: DbSession) -> ProjectDetail:
    project = _get_project(db, auth, project_id)
    samples = list(
        db.scalars(
            select(Sample)
            .where(Sample.project_id == project.id)
            .order_by(desc(Sample.created_at))
        )
    )
    runs = list(
        db.scalars(
            select(Run)
            .where(Run.project_id == project.id)
            .order_by(desc(Run.created_at))
            .limit(20)
        )
    )
    detail = ProjectDetail.model_validate(project)
    detail.samples = samples  # type: ignore[assignment]
    detail.runs = runs  # type: ignore[assignment]
    detail.stats = {
        "sample_count": len(samples),
        "run_count": db.scalar(select(func.count(Run.id)).where(Run.project_id == project.id)) or 0,
        "completed_runs": db.scalar(
            select(func.count(Run.id)).where(
                Run.project_id == project.id, Run.status == "succeeded"
            )
        )
        or 0,
        "spots": sum(sample.spot_count or 0 for sample in samples),
    }
    return detail


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    request: Request,
    auth: AnalystAuth,
    db: DbSession,
) -> Project:
    project = _get_project(db, auth, project_id)
    if payload.name is not None:
        project.name = payload.name.strip()
    if payload.description is not None:
        project.description = payload.description
    if payload.archived is not None:
        project.archived = payload.archived
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="project.update",
        resource_type="project",
        resource_id=project.id,
        request=request,
    )
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def archive_project(
    project_id: str,
    request: Request,
    auth: AnalystAuth,
    db: DbSession,
) -> dict:
    project = _get_project(db, auth, project_id)
    project.archived = True
    samples = list(db.scalars(select(Sample).where(Sample.project_id == project.id)))
    for sample in samples:
        sample.archived = True
        sample.status = "archived"
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="project.archive",
        resource_type="project",
        resource_id=project.id,
        request=request,
    )
    db.commit()
    return {"ok": True}
