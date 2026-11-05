from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy import desc, select

from ..deps import AnalystAuth, CurrentAuth, DbSession, log_audit
from ..disease_packs import get_pack
from ..models import Project, Report, Result, Run, Sample, User
from ..schemas import (
    ReportApproveRequest,
    ReportStatusOut,
    ResultOut,
    RunCreate,
    RunDetail,
    RunOut,
    SampleOut,
)
from ..services.pipeline import execute_run
from ..services.report import build_report
from ..services.storage import storage

router = APIRouter(tags=["runs"])


def _get_run(db, auth: CurrentAuth, run_id: str) -> Run:
    run = db.get(Run, run_id)
    if run is None or run.org_id != auth.org.id:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


def _enqueue(run: Run, background: BackgroundTasks) -> None:
    background.add_task(execute_run, run.id)


@router.post(
    "/samples/{sample_id}/runs",
    response_model=RunOut,
    status_code=status.HTTP_201_CREATED,
)
def create_run(
    sample_id: str,
    payload: RunCreate,
    request: Request,
    background: BackgroundTasks,
    auth: AnalystAuth,
    db: DbSession,
) -> Run:
    sample = db.get(Sample, sample_id)
    if sample is None or sample.org_id != auth.org.id:
        raise HTTPException(status_code=404, detail="Sample not found")
    if sample.archived:
        raise HTTPException(status_code=400, detail="Sample is archived")
    project = db.get(Project, sample.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    pack_id = payload.disease_pack or sample.disease_pack or project.disease_pack
    try:
        pack = get_pack(pack_id)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail="Unknown disease pack") from exc

    active = db.scalar(
        select(Run).where(
            Run.sample_id == sample.id,
            Run.status.in_(["queued", "running"]),
        )
    )
    if active:
        raise HTTPException(status_code=409, detail="A run is already active for this sample")

    run = Run(
        org_id=auth.org.id,
        project_id=project.id,
        sample_id=sample.id,
        disease_pack=pack_id,
        pack_version=pack["version"],
        status="queued",
        stage="queued",
        progress=0.0,
        params=payload.params,
        created_by=auth.user.id,
    )
    db.add(run)
    db.flush()
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="run.create",
        resource_type="run",
        resource_id=run.id,
        request=request,
        metadata={"disease_pack": pack_id, "sample_id": sample.id},
    )
    db.commit()
    db.refresh(run)
    _enqueue(run, background)
    return run


@router.get("/runs", response_model=list[RunOut])
def list_runs(
    auth: CurrentAuth,
    db: DbSession,
    project_id: str | None = None,
    sample_id: str | None = None,
    run_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[Run]:
    stmt = select(Run).where(Run.org_id == auth.org.id)
    if project_id:
        stmt = stmt.where(Run.project_id == project_id)
    if sample_id:
        stmt = stmt.where(Run.sample_id == sample_id)
    if run_status:
        stmt = stmt.where(Run.status == run_status)
    return list(db.scalars(stmt.order_by(desc(Run.created_at)).limit(limit)))


@router.get("/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: str, auth: CurrentAuth, db: DbSession) -> RunDetail:
    run = _get_run(db, auth, run_id)
    report = db.scalar(select(Report).where(Report.run_id == run.id))
    # Built explicitly: Run.report is an ORM relationship, the API exposes a status view.
    return RunDetail(
        **RunOut.model_validate(run).model_dump(),
        params=run.params or {},
        provenance=run.provenance,
        sample=SampleOut.model_validate(run.sample) if run.sample else None,
        report=_report_status(db, report) if report else None,
    )


def _report_status(db, report: Report) -> ReportStatusOut:
    approver = db.get(User, report.approved_by) if report.approved_by else None
    return ReportStatusOut(
        status=report.status,
        created_at=report.created_at,
        approved_at=report.approved_at,
        approved_by_name=approver.name if approver else None,
        approval_note=report.approval_note or "",
    )


def _get_report(db, run: Run) -> Report:
    report = db.scalar(select(Report).where(Report.run_id == run.id))
    if report is None:
        raise HTTPException(status_code=404, detail="Report not ready")
    return report


@router.get("/runs/{run_id}/results", response_model=ResultOut)
def get_results(run_id: str, auth: CurrentAuth, db: DbSession) -> ResultOut:
    run = _get_run(db, auth, run_id)
    if run.status == "failed":
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Run failed",
                "code": run.error_code,
                "error": run.error_message,
            },
        )
    result = db.scalar(select(Result).where(Result.run_id == run.id))
    if result is None:
        raise HTTPException(status_code=409, detail=f"Results not ready (status={run.status})")
    return ResultOut(run_id=run.id, payload=result.payload)


@router.get("/runs/{run_id}/report", response_class=HTMLResponse)
def get_report(run_id: str, auth: CurrentAuth, db: DbSession) -> HTMLResponse:
    """In-app preview. Drafts carry a visible 'not approved' banner."""
    run = _get_run(db, auth, run_id)
    report = _get_report(db, run)
    return HTMLResponse(report.html, headers={"Cache-Control": "no-store"})


@router.post("/runs/{run_id}/report/approve", response_model=ReportStatusOut)
def approve_report(
    run_id: str,
    payload: ReportApproveRequest,
    request: Request,
    auth: AnalystAuth,
    db: DbSession,
) -> ReportStatusOut:
    """Human sign-off (AGENTS.md rule 6). Required before the report can be exported."""
    run = _get_run(db, auth, run_id)
    if run.status != "succeeded":
        raise HTTPException(status_code=409, detail="Only reports of succeeded runs can be approved")
    report = _get_report(db, run)
    if report.status == "approved":
        raise HTTPException(status_code=409, detail="Report is already approved")
    if not payload.confirm_ruo:
        raise HTTPException(
            status_code=422,
            detail="Confirm that the report is for Research Use Only before approving",
        )
    result = db.scalar(select(Result).where(Result.run_id == run.id))
    if result is None:
        raise HTTPException(status_code=409, detail="Results missing for this run")

    report.status = "approved"
    report.approved_by = auth.user.id
    report.approved_at = datetime.now(UTC)
    report.approval_note = payload.note.strip()
    pack = get_pack(run.disease_pack)
    report.html = build_report(
        run,
        result.payload,
        pack,
        approval={
            "by": auth.user.name,
            "at": report.approved_at,
            "note": report.approval_note,
        },
    )
    storage.save_bytes(f"runs/{run.id}/report.html", report.html.encode("utf-8"))
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="report.approve",
        resource_type="report",
        resource_id=report.id,
        request=request,
        metadata={"run_id": run.id, "note": report.approval_note[:200]},
    )
    db.commit()
    db.refresh(report)
    return _report_status(db, report)


@router.get("/runs/{run_id}/report/export", response_class=HTMLResponse)
def export_report(
    run_id: str,
    request: Request,
    auth: CurrentAuth,
    db: DbSession,
) -> HTMLResponse:
    """Download the approved report. Every export is written to the audit log."""
    run = _get_run(db, auth, run_id)
    report = _get_report(db, run)
    if report.status != "approved":
        raise HTTPException(status_code=409, detail="Report must be approved before export")
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="report.export",
        resource_type="report",
        resource_id=report.id,
        request=request,
        metadata={"run_id": run.id, "format": "html"},
    )
    db.commit()
    filename = f"topiome-report-{run.disease_pack}-{run.id[:8]}.html"
    return HTMLResponse(
        report.html,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


@router.post("/runs/{run_id}/retry", response_model=RunOut, status_code=201)
def retry_run(
    run_id: str,
    request: Request,
    background: BackgroundTasks,
    auth: AnalystAuth,
    db: DbSession,
) -> Run:
    original = _get_run(db, auth, run_id)
    if original.status in {"queued", "running"}:
        raise HTTPException(status_code=409, detail="Run is still active")
    retry = Run(
        org_id=auth.org.id,
        project_id=original.project_id,
        sample_id=original.sample_id,
        disease_pack=original.disease_pack,
        pack_version=original.pack_version,
        status="queued",
        stage="queued",
        progress=0.0,
        params=original.params or {},
        created_by=auth.user.id,
    )
    db.add(retry)
    db.flush()
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="run.retry",
        resource_type="run",
        resource_id=retry.id,
        request=request,
        metadata={"original_run": original.id},
    )
    db.commit()
    db.refresh(retry)
    _enqueue(retry, background)
    return retry


@router.post("/runs/{run_id}/cancel")
def cancel_run(
    run_id: str,
    request: Request,
    auth: AnalystAuth,
    db: DbSession,
) -> dict:
    run = _get_run(db, auth, run_id)
    if run.status not in {"queued", "running"}:
        raise HTTPException(status_code=409, detail="Run is not active")
    run.status = "cancelled"
    run.stage = "cancelled"
    run.finished_at = datetime.now(UTC)
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="run.cancel",
        resource_type="run",
        resource_id=run.id,
        request=request,
    )
    db.commit()
    return {"ok": True}
