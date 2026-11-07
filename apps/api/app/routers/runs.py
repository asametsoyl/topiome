from __future__ import annotations

import csv
import io
from datetime import UTC, datetime

import numpy as np
from analysis import load_visium
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import desc, select

from ..config import settings
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
from ..services.pipeline import prepare_visium_dir
from ..services.queue import enqueue
from ..services.quotas import QuotaExceeded, ensure_run
from ..services.report import build_report
from ..services.spatial import roi_expression_differences
from ..services.storage import storage

router = APIRouter(tags=["runs"])


def _get_run(db, auth: CurrentAuth, run_id: str) -> Run:
    run = db.get(Run, run_id)
    if run is None or run.org_id != auth.org.id:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


def _enqueue(run: Run, background: BackgroundTasks) -> None:
    enqueue(run.id, background)


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

    try:
        ensure_run(db, auth.org.id, auth.org.plan)
    except QuotaExceeded as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc

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
        max_attempts=max(1, settings.run_max_attempts),
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
    stmt = select(Run).join(Project, Run.project_id == Project.id).where(
        Run.org_id == auth.org.id,
        Project.archived.is_(False),
    )
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


@router.get("/runs/{run_id}/expression")
def get_gene_expression(
    run_id: str,
    auth: CurrentAuth,
    db: DbSession,
    gene: str = Query(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$"),
) -> dict:
    """Return one real Visium gene layer, normalized to log1p(CP10K)."""
    run = _get_run(db, auth, run_id)
    result = db.scalar(select(Result).where(Result.run_id == run.id))
    if result is None:
        raise HTTPException(status_code=409, detail=f"Results not ready (status={run.status})")
    if (result.payload.get("summary") or {}).get("synthetic"):
        raise HTTPException(status_code=422, detail="Gene expression layers require uploaded Visium data")
    try:
        directory = prepare_visium_dir(run.sample)
        if directory is None:
            raise ValueError("Visium files are unavailable")
        dataset = load_visium(directory, sample_id=run.sample_id, keep_genes={gene}, max_genes=1)
    except (OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail="Unable to read gene expression from this sample") from exc
    column = next((name for name in dataset.expression.columns if name.casefold() == gene.casefold()), None)
    if column is None:
        raise HTTPException(status_code=404, detail=f"Gene {gene} is not present in this sample")
    raw = dataset.expression[column].to_numpy(dtype=float)
    totals = dataset.qc_stats["total_counts"]
    normalized = np.log1p(np.divide(raw * 10_000.0, totals, out=np.zeros_like(raw), where=totals > 0))
    values = {barcode: round(float(value), 5) for barcode, value in zip(dataset.barcodes, normalized, strict=True)}
    return {"gene": column, "scale": "log1p(CP10K)", "values": values}


@router.post("/runs/{run_id}/roi-genes")
def get_roi_genes(
    run_id: str,
    payload: dict,
    auth: CurrentAuth,
    db: DbSession,
) -> dict:
    """Rank descriptive expression differences between a selected ROI and background."""
    run = _get_run(db, auth, run_id)
    result = db.scalar(select(Result).where(Result.run_id == run.id))
    if result is None:
        raise HTTPException(status_code=409, detail=f"Results not ready (status={run.status})")
    if (result.payload.get("summary") or {}).get("synthetic"):
        raise HTTPException(status_code=422, detail="ROI expression requires uploaded Visium data")
    requested = payload.get("barcodes") if isinstance(payload, dict) else None
    top_n = payload.get("top_n", 30) if isinstance(payload, dict) else 30
    if (
        not isinstance(requested, list)
        or not 1 <= len(requested) <= 20_000
        or any(not isinstance(item, str) for item in requested)
        or len(set(requested)) != len(requested)
        or not isinstance(top_n, int)
        or not 1 <= top_n <= 50
    ):
        raise HTTPException(status_code=422, detail="Invalid ROI gene query")
    spots = {spot.get("barcode"): spot for spot in result.payload.get("spots", [])}
    if any(barcode not in spots for barcode in requested):
        raise HTTPException(status_code=422, detail="ROI contains unknown spots")
    try:
        directory = prepare_visium_dir(run.sample)
        if directory is None:
            raise ValueError("Visium files are unavailable")
        return roi_expression_differences(
            directory,
            roi_barcodes=set(requested),
            qc_pass_barcodes={barcode for barcode, spot in spots.items() if spot.get("qc_pass")},
            top_n=top_n,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/runs/{run_id}/roi-export", response_class=Response)
def export_roi(
    run_id: str,
    request: Request,
    payload: dict,
    auth: CurrentAuth,
    db: DbSession,
) -> Response:
    """Export selected spots only after report approval; record the data export."""
    run = _get_run(db, auth, run_id)
    report = _get_report(db, run)
    if report.status != "approved":
        raise HTTPException(status_code=409, detail="Report must be approved before data export")
    requested = payload.get("barcodes") if isinstance(payload, dict) else None
    if not isinstance(requested, list) or not 1 <= len(requested) <= 20_000 or any(not isinstance(item, str) for item in requested):
        raise HTTPException(status_code=422, detail="Select between 1 and 20,000 spots")
    result = db.scalar(select(Result).where(Result.run_id == run.id))
    if result is None:
        raise HTTPException(status_code=409, detail="Results missing for this run")
    by_barcode = {spot.get("barcode"): spot for spot in result.payload.get("spots", [])}
    if len(set(requested)) != len(requested) or any(barcode not in by_barcode for barcode in requested):
        raise HTTPException(status_code=422, detail="Selection contains duplicate or unknown spots")
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["barcode", "x_fullres_px", "y_fullres_px", "domain", "domain_name", "uncertainty", "qc_pass", "composition"])
    for barcode in requested:
        spot = by_barcode[barcode]
        writer.writerow([barcode, spot["x"], spot["y"], spot["domain"], spot["domain_name"], spot["uncertainty"], spot["qc_pass"], ";".join(f"{key}={value}" for key, value in sorted(spot.get("composition", {}).items()))])
    log_audit(db, org_id=auth.org.id, actor_id=auth.user.id, action="run.roi_export", resource_type="run", resource_id=run.id, request=request, metadata={"n_spots": len(requested), "format": "csv", "report_id": report.id})
    db.commit()
    return Response(output.getvalue(), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="topiome-roi-{run.id[:8]}.csv"', "Cache-Control": "no-store"})


@router.post("/runs/{run_id}/map-export")
def log_map_export(
    run_id: str,
    request: Request,
    payload: dict,
    auth: CurrentAuth,
    db: DbSession,
) -> dict[str, bool]:
    """Audit a browser-rendered map image export; approval is required first."""
    run = _get_run(db, auth, run_id)
    report = _get_report(db, run)
    if report.status != "approved":
        raise HTTPException(status_code=409, detail="Report must be approved before data export")
    width = payload.get("width") if isinstance(payload, dict) else None
    height = payload.get("height") if isinstance(payload, dict) else None
    mode = payload.get("mode") if isinstance(payload, dict) else None
    if (
        not isinstance(width, int)
        or not isinstance(height, int)
        or not 1 <= width <= 10_000
        or not 1 <= height <= 10_000
        or mode not in {"domain", "celltype", "uncertainty", "gene"}
    ):
        raise HTTPException(status_code=422, detail="Invalid map export metadata")
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="run.map_export",
        resource_type="run",
        resource_id=run.id,
        request=request,
        metadata={"format": "png", "width": width, "height": height, "mode": mode, "report_id": report.id},
    )
    db.commit()
    return {"ok": True}


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
