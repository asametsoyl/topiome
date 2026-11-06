from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import desc, select

from ..deps import AnalystAuth, CurrentAuth, DbSession, log_audit
from ..disease_packs import get_pack
from ..models import Project, Run, Sample, SampleFile
from ..schemas import SampleDetail, SampleOut
from ..services.pipeline import sample_raw_dir
from ..services.storage import StorageError, storage

router = APIRouter(tags=["samples"])

ARCHIVES = (".zip", ".tar.gz", ".tgz", ".tar")


def _safe_filename(name: str) -> str:
    cleaned = Path(name).name
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", cleaned)
    return cleaned[:200] or "file"


def _has_visium_files(names: list[str]) -> tuple[bool, list[str]]:
    """Cheap upload-time check; the full check runs when the archive is unpacked."""
    lower = [name.lower() for name in names]
    archives = [name for name in lower if name.endswith(ARCHIVES)]
    has_h5 = any(name.endswith(".h5") for name in lower)
    has_mtx = (
        any(name.endswith(("matrix.mtx", "matrix.mtx.gz")) for name in lower)
        and any("barcodes" in name for name in lower)
        and any("features" in name or "genes" in name for name in lower)
    )
    has_positions = any("tissue_positions" in name and name.endswith(".csv") for name in lower)
    if archives and not (has_h5 or has_mtx or has_positions):
        return True, []  # one archive with everything inside
    missing = []
    if not (has_h5 or has_mtx or archives):
        missing.append("count matrix (filtered_feature_bc_matrix.h5, or matrix.mtx + barcodes.tsv + features.tsv)")
    if not (has_positions or archives):
        missing.append("tissue_positions.csv (or the spatial/ folder as .tar.gz)")
    return not missing, missing


def _get_project(db, auth: CurrentAuth, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.org_id != auth.org.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_sample(db, auth: CurrentAuth, sample_id: str) -> Sample:
    sample = db.get(Sample, sample_id)
    if sample is None or sample.org_id != auth.org.id:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.get("/projects/{project_id}/samples", response_model=list[SampleOut])
def list_samples(project_id: str, auth: CurrentAuth, db: DbSession) -> list[Sample]:
    project = _get_project(db, auth, project_id)
    return list(
        db.scalars(
            select(Sample)
            .where(Sample.project_id == project.id, Sample.archived.is_(False))
            .order_by(desc(Sample.created_at))
        )
    )


@router.post(
    "/projects/{project_id}/samples",
    response_model=SampleDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_sample(
    project_id: str,
    request: Request,
    auth: AnalystAuth,
    db: DbSession,
    metadata: str = Form(...),
    files: list[UploadFile] = File(default=[]),
) -> SampleDetail:
    project = _get_project(db, auth, project_id)
    try:
        meta = json.loads(metadata)
        if not isinstance(meta, dict):
            raise ValueError
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="metadata must be a JSON object") from exc

    pack_id = str(meta.get("disease_pack") or project.disease_pack)
    try:
        get_pack(pack_id)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail="Unknown disease pack") from exc

    filenames = [_safe_filename(file.filename or "") for file in files]
    has_files, missing = _has_visium_files(filenames)
    if files and not has_files:
        raise HTTPException(
            status_code=400,
            detail=(
                "Missing Visium files: "
                + ", ".join(missing)
                + ". Upload a Space Ranger folder or a zip archive."
            ),
        )

    sample = Sample(
        org_id=auth.org.id,
        project_id=project.id,
        name=str(meta.get("name") or meta.get("sample_id") or "Untitled sample")[:160],
        external_id=str(meta.get("sample_id") or "")[:120],
        disease_pack=pack_id,
        platform=str(meta.get("platform") or "visium")[:40],
        species=str(meta.get("species") or "human")[:40],
        condition=str(meta.get("condition") or "")[:80],
        sample_metadata=meta,
        status="uploaded" if files else "demo",
    )
    db.add(sample)
    db.flush()

    raw_key = sample_raw_dir(sample)
    for upload, filename in zip(files, filenames, strict=True):
        try:
            size, digest = storage.save_upload(f"{raw_key}/{filename}", upload)
        except StorageError as exc:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        db.add(
            SampleFile(
                sample_id=sample.id,
                filename=filename,
                kind=(
                    "visium"
                    if filename.lower().endswith((".mtx", ".mtx.gz", ".h5", *ARCHIVES))
                    else "data"
                ),
                size_bytes=size,
                sha256=digest,
                storage_key=f"{raw_key}/{filename}",
            )
        )

    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="sample.create",
        resource_type="sample",
        resource_id=sample.id,
        request=request,
        metadata={"files": len(files), "disease_pack": pack_id},
    )
    db.commit()
    db.refresh(sample)
    return _detail(db, sample)


def _detail(db, sample: Sample) -> SampleDetail:
    detail = SampleDetail.model_validate(sample)
    detail.files = list(
        db.scalars(
            select(SampleFile)
            .where(SampleFile.sample_id == sample.id)
            .order_by(SampleFile.filename)
        )
    )  # type: ignore[assignment]
    detail.runs = list(
        db.scalars(
            select(Run).where(Run.sample_id == sample.id).order_by(desc(Run.created_at)).limit(10)
        )
    )  # type: ignore[assignment]
    return detail


@router.get("/samples/{sample_id}", response_model=SampleDetail)
def get_sample(sample_id: str, auth: CurrentAuth, db: DbSession) -> SampleDetail:
    sample = _get_sample(db, auth, sample_id)
    return _detail(db, sample)


@router.get("/samples/{sample_id}/files")
def list_files(sample_id: str, auth: CurrentAuth, db: DbSession) -> list[dict]:
    sample = _get_sample(db, auth, sample_id)
    return [
        {
            "id": file.id,
            "filename": file.filename,
            "kind": file.kind,
            "size_bytes": file.size_bytes,
            "created_at": file.created_at,
        }
        for file in sample.files
    ]


@router.get("/samples/{sample_id}/files/{file_id}/download")
def download_file(sample_id: str, file_id: str, auth: CurrentAuth, db: DbSession) -> FileResponse:
    sample = _get_sample(db, auth, sample_id)
    file = db.get(SampleFile, file_id)
    if file is None or file.sample_id != sample.id:
        raise HTTPException(status_code=404, detail="File not found")
    path = storage.path(file.storage_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing from storage")
    return FileResponse(path, filename=file.filename)


@router.delete("/samples/{sample_id}")
def archive_sample(
    sample_id: str,
    request: Request,
    auth: AnalystAuth,
    db: DbSession,
) -> dict:
    sample = _get_sample(db, auth, sample_id)
    sample.archived = True
    sample.status = "archived"
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="sample.archive",
        resource_type="sample",
        resource_id=sample.id,
        request=request,
    )
    db.commit()
    return {"ok": True}
