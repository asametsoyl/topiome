from __future__ import annotations

import json
import tarfile
import traceback
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from analysis import generate_demo_dataset, load_visium, run_pipeline
from analysis.io import discover_visium
from sqlalchemy import select, update

from ..db import SessionLocal
from ..disease_packs import get_pack
from ..models import Report, Result, Run, Sample
from ..references import domain_model_for, reference_genes, signatures_for
from .provenance import build_provenance
from .report import build_report
from .storage import storage


class RunCancelled(Exception):
    """Raised when a run was cancelled while the worker was processing it."""


def sample_raw_dir(sample: Sample) -> str:
    return f"orgs/{sample.org_id}/projects/{sample.project_id}/samples/{sample.id}/raw"


ARCHIVE_SUFFIXES = (".zip", ".tar.gz", ".tgz", ".tar")


def _archive_stem(path: Path) -> str:
    name = path.name
    for suffix in ARCHIVE_SUFFIXES:
        if name.lower().endswith(suffix):
            return name[: -len(suffix)] or "archive"
    return name


def _extract_tar(tar_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path) as archive:
        # "data" filter refuses absolute paths, ".." escapes, links outside and devices.
        archive.extractall(destination, filter="data")


def _extract_zip(zip_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if destination.resolve() not in target.parents and target != destination.resolve():
                raise ValueError("Unsafe zip entry")
            archive.extract(member, destination)


def prepare_visium_dir(sample: Sample) -> Path | None:
    """Unpack uploaded archives and return the folder holding a complete Visium sample.

    Returns None for demo samples without files; raises ValueError when files
    were uploaded but do not form a complete sample.
    """
    if not sample.files:
        return None
    raw_key = sample_raw_dir(sample)
    base = storage.path(raw_key)
    if not base.exists():
        return None
    for archive in sorted(base.iterdir()):
        if not archive.is_file() or archive.name.startswith("._"):
            continue
        if not archive.name.lower().endswith(ARCHIVE_SUFFIXES):
            continue
        target = storage.path(f"{raw_key}/extracted/{_archive_stem(archive)}")
        if target.exists():
            continue
        if archive.name.lower().endswith(".zip"):
            _extract_zip(archive, target)
        else:
            _extract_tar(archive, target)
    missing = discover_visium(base).missing()
    if missing:
        raise ValueError("Uploaded files are not a complete Visium sample; missing " + ", ".join(missing))
    return base


def pack_genes(pack: dict) -> set[str]:
    """Genes the analysis needs even if they are not among the most abundant."""
    genes: set[str] = set()
    for group in ("cell_types", "zones"):
        for item in pack.get(group, []):
            genes.update(item.get("markers", []))
    genes.update(t.get("gene", "") for t in pack.get("targets", []))
    for pair in pack.get("ligand_receptor_pairs", []):
        genes.update([pair.get("ligand", ""), pair.get("receptor", "")])
    atlas = (pack.get("atlas_reference") or {}).get("data") or {}
    genes.update(atlas.get("genes", {}).keys())
    return {g.upper() for g in genes if g}


def _update(db, run: Run, *, status=None, stage=None, progress=None, **kwargs) -> None:
    if status is not None:
        run.status = status
    if stage is not None:
        run.stage = stage
    if progress is not None:
        run.progress = float(progress)
    for key, value in kwargs.items():
        setattr(run, key, value)
    db.commit()


def _check_cancelled(db, run: Run) -> None:
    db.refresh(run, attribute_names=["status"])
    if run.status == "cancelled":
        raise RunCancelled(run.id)


def _transition(db, run_id: str, *, expected: str, **values) -> bool:
    """Atomically move a run out of ``expected`` status; False if it was changed meanwhile."""
    result = db.execute(
        update(Run)
        .where(Run.id == run_id, Run.status == expected)
        .values(**values)
        .execution_options(synchronize_session=False)
    )
    return result.rowcount == 1


def execute_run(run_id: str) -> None:
    """Execute a run in its own DB session. Safe for BackgroundTasks/RQ."""
    db = SessionLocal()
    run = db.get(Run, run_id)
    if run is None:
        db.close()
        return
    sample = db.get(Sample, run.sample_id)
    if sample is None:
        run.status = "failed"
        run.error_code = "sample_missing"
        run.error_message = "Sample not found"
        db.commit()
        db.close()
        return

    try:
        started = _transition(
            db,
            run.id,
            expected="queued",
            status="running",
            stage="loading",
            progress=0.05,
            started_at=datetime.now(UTC),
            error_code=None,
            error_message=None,
        )
        db.commit()
        if not started:
            raise RunCancelled(run.id)
        db.refresh(run)
        pack = get_pack(run.disease_pack)
        run.pack_version = pack["version"]
        db.commit()

        params = run.params or {}
        signatures = None
        visium_dir = prepare_visium_dir(sample)
        shipped_reference = signatures_for(pack)
        domain_model = domain_model_for(pack)

        synthetic_seed: int | None = None
        if visium_dir is not None:
            dataset = load_visium(
                visium_dir,
                sample_id=sample.id,
                keep_genes=pack_genes(pack) | reference_genes(pack),
            )
            dataset.metadata.update(sample.sample_metadata or {})
            if shipped_reference is not None:
                signatures = shipped_reference.table
        else:
            synthetic_seed = int(params.get("seed", 42))
            dataset, signatures, ground_truth = generate_demo_dataset(
                pack,
                n_spots=int(params.get("n_spots", 1200)),
                seed=synthetic_seed,
            )
            dataset.sample_id = sample.id
            dataset.ground_truth = ground_truth
            dataset.metadata.update(sample.sample_metadata or {})
            dataset.metadata["synthetic"] = True

        run.provenance = build_provenance(
            pipeline_version=run.pipeline_version,
            pack=pack,
            params=params,
            input_kind="visium" if visium_dir is not None else "synthetic",
            input_files=[
                {"filename": f.filename, "sha256": f.sha256, "size_bytes": f.size_bytes}
                for f in sorted(sample.files, key=lambda f: f.filename)
            ],
            synthetic_seed=synthetic_seed,
            signatures=(
                {
                    "version": shipped_reference.version,
                    "sha256": shipped_reference.sha256,
                    "file": shipped_reference.file,
                }
                if shipped_reference is not None and visium_dir is not None
                else None
            ),
            domain_model=(
                {"version": domain_model.version, "sha256": domain_model.sha256}
                if domain_model is not None
                else None
            ),
        )
        sample.spot_count = int(dataset.expression.shape[0])
        sample.status = "validated"
        db.commit()

        _check_cancelled(db, run)
        _update(db, run, stage="deconvolution", progress=0.25)
        result = run_pipeline(
            dataset,
            pack,
            signatures=signatures,
            params=params,
            domain_model=domain_model,
        )
        _check_cancelled(db, run)

        _update(db, run, stage="report", progress=0.85)
        if result.pipeline_version != run.pipeline_version:
            run.pipeline_version = result.pipeline_version
            run.provenance = {**(run.provenance or {}), "pipeline_version": result.pipeline_version}
        payload = result.to_payload()
        payload["provenance"] = run.provenance
        result_key = f"runs/{run.id}/results.json"
        storage.save_bytes(result_key, json.dumps(payload, ensure_ascii=False).encode("utf-8"))

        existing = db.scalar(select(Result).where(Result.run_id == run.id))
        if existing:
            existing.payload = payload
            existing.storage_key = result_key
        else:
            db.add(Result(run_id=run.id, payload=payload, storage_key=result_key))

        report_html = build_report(run, payload, pack)
        _check_cancelled(db, run)
        report_key = f"runs/{run.id}/report.html"
        storage.save_bytes(report_key, report_html.encode("utf-8"))
        existing_report = db.scalar(select(Report).where(Report.run_id == run.id))
        if existing_report:
            existing_report.html = report_html
            existing_report.status = "draft"
            existing_report.approved_by = None
            existing_report.approved_at = None
            existing_report.approval_note = ""
        else:
            db.add(Report(run_id=run.id, html=report_html, status="draft"))

        run.summary = payload["summary"]
        db.flush()
        # Only succeed if nobody cancelled the run meanwhile; otherwise drop the outputs.
        if not _transition(
            db,
            run.id,
            expected="running",
            status="succeeded",
            stage="done",
            progress=1.0,
            finished_at=datetime.now(UTC),
        ):
            raise RunCancelled(run.id)
        db.commit()
    except RunCancelled:
        db.rollback()
        run = db.get(Run, run_id)
        if run is not None and run.status == "cancelled":
            run.stage = "cancelled"
            run.finished_at = run.finished_at or datetime.now(UTC)
            db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        run = db.get(Run, run_id)
        if run is not None and run.status != "cancelled":
            run.status = "failed"
            run.stage = "failed"
            run.error_code = (
                "invalid_input"
                if isinstance(exc, (ValueError, FileNotFoundError, zipfile.BadZipFile))
                else "pipeline_error"
            )
            run.error_message = str(exc)[:1000]
            run.finished_at = datetime.now(UTC)
            db.commit()
            try:
                storage.save_bytes(
                    f"runs/{run.id}/error.log",
                    traceback.format_exc().encode("utf-8"),
                )
            except Exception:
                pass
    finally:
        db.close()
