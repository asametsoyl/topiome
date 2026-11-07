#!/usr/bin/env python3
"""Inventory locally available public Visium cohorts without committing data.

Run from ``apps/api`` with:
    uv run python -I ../../scripts/validation/inventory_public_visium.py

The output defaults to ``data/public/inventory.json`` (git-ignored). Incomplete
downloads and non-Visium directories are never counted as usable samples.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tarfile
import tempfile
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "packages" / "analysis"))

from analysis.io import discover_visium, load_visium


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    matrices = [
        *root.rglob("*filtered_feature_bc_matrix*.h5"),
        *root.rglob("*matrix.mtx"),
        *root.rglob("*matrix.mtx.gz"),
    ]
    matrices = [
        p
        for p in matrices
        if not p.name.startswith(("._", ".")) and not p.name.endswith(".part")
    ]

    # Some GEO/ArrayExpress releases publish each Space Ranger H5 beside a
    # separate spatial.tar. Validate the matched pair as one section, using a
    # temporary extraction so the public data tree stays compact.
    flat_pairs: list[tuple[Path, Path]] = []
    for archive in sorted(root.rglob("*-spatial.tar")):
        if archive.name.startswith(("._", ".")):
            continue
        matrix = archive.with_name(
            archive.name.removesuffix("-spatial.tar") + "-filtered_feature_bc_matrix.h5"
        )
        if matrix.is_file() and not matrix.name.startswith(("._", ".")):
            flat_pairs.append((matrix, archive))
    flat_roots = {matrix.parent for matrix, _ in flat_pairs}
    sample_dirs = sorted({matrix.parent for matrix in matrices} - flat_roots)

    for matrix, archive in flat_pairs:
        sample_id = matrix.name.removesuffix("-filtered_feature_bc_matrix.h5")
        base_record: dict[str, object] = {
            "sample_id": sample_id,
            "path": str(matrix.parent.relative_to(root) / sample_id),
            "matrix": str(matrix.relative_to(root)),
            "matrix_sha256": sha256(matrix),
            "spatial_archive": str(archive.relative_to(root)),
            "spatial_archive_sha256": sha256(archive),
        }
        try:
            with tempfile.TemporaryDirectory(
                prefix="topiome-visium-inventory-"
            ) as temp_name:
                sample_dir = Path(temp_name)
                os.symlink(matrix.resolve(), sample_dir / matrix.name)
                with tarfile.open(archive, "r:") as tar:
                    members = tar.getmembers()
                    for member in members:
                        member_path = Path(member.name)
                        if member_path.is_absolute() or ".." in member_path.parts:
                            raise ValueError(
                                f"Unsafe path in spatial archive: {member.name}"
                            )
                    tar.extractall(sample_dir, members=members, filter="data")
                files = discover_visium(sample_dir)
                missing = files.missing()
                if missing:
                    records.append(
                        {
                            **base_record,
                            "reader_status": "incomplete",
                            "missing": missing,
                        }
                    )
                    continue
                positions_path = files.positions
                dataset = load_visium(sample_dir, sample_id=sample_id, max_genes=10)
                records.append(
                    {
                        **base_record,
                        "positions_sha256": sha256(positions_path)
                        if positions_path
                        else None,
                        "n_tissue_spots": len(dataset.barcodes),
                        "n_genes_total": int(dataset.metadata["genes_total"]),
                        "has_hires_image": files.image is not None,
                        "has_scalefactors": files.scalefactors is not None,
                        "reader_status": "loaded",
                    }
                )
        except Exception as exc:  # noqa: BLE001  # inventory reports bad pairs without stopping
            records.append({**base_record, "reader_status": "error", "error": str(exc)})

    for sample_dir in sample_dirs:
        matrix_candidates = [
            path
            for path in matrices
            if path.parent == sample_dir
            and not path.name.startswith(("._", "."))
            and not path.name.endswith(".part")
        ]
        if not matrix_candidates:
            continue
        matrix = min(
            matrix_candidates,
            key=lambda path: (not path.name.endswith(".h5"), path.name),
        )
        try:
            files = discover_visium(sample_dir)
            matrix_path = files.h5 or files.matrix
            missing = files.missing()
            spatial_source: Path | None = None
            if missing == ["tissue_positions.csv or tissue_positions.parquet"]:
                sample_key = sample_dir.name.split("_filtered", maxsplit=1)[0].lower()
                candidates = [
                    p
                    for p in root.rglob("tissue_positions*")
                    if p.is_file()
                    and not p.name.startswith(("._", "."))
                    and sample_key in str(p.parent).lower()
                    and p.suffix.lower() in {".csv", ".parquet"}
                ]
                if len(candidates) == 1:
                    spatial_source = candidates[0]
                    missing = []
            if missing:
                records.append(
                    {
                        "sample_id": sample_dir.name,
                        "path": str(sample_dir.relative_to(root)),
                        "matrix": str(matrix.relative_to(root)),
                        "matrix_sha256": sha256(matrix),
                        "reader_status": "incomplete",
                        "missing": missing,
                    }
                )
                continue
            if spatial_source is None:
                dataset = load_visium(
                    sample_dir, sample_id=sample_dir.name, max_genes=10
                )
                has_hires_image = files.image is not None
                has_scalefactors = files.scalefactors is not None
                positions_path = files.positions
            else:
                with tempfile.TemporaryDirectory(
                    prefix="topiome-visium-inventory-"
                ) as temp_name:
                    normalized = Path(temp_name)
                    for source in sample_dir.iterdir():
                        if source.is_file() and not source.name.startswith(("._", ".")):
                            os.symlink(source.resolve(), normalized / source.name)
                    os.symlink(
                        spatial_source.resolve(), normalized / spatial_source.name
                    )
                    for spatial_file in spatial_source.parent.iterdir():
                        if (
                            spatial_file.is_file()
                            and not spatial_file.name.startswith(("._", "."))
                            and (
                                "scalefactors" in spatial_file.name
                                or "tissue_hires_image" in spatial_file.name
                            )
                        ):
                            target = normalized / spatial_file.name
                            if not target.exists():
                                os.symlink(spatial_file.resolve(), target)
                    dataset = load_visium(
                        normalized, sample_id=sample_dir.name, max_genes=10
                    )
                positions_path = spatial_source
                has_hires_image = files.image is not None or any(
                    "tissue_hires_image" in p.name
                    for p in spatial_source.parent.iterdir()
                )
                has_scalefactors = files.scalefactors is not None or any(
                    "scalefactors" in p.name for p in spatial_source.parent.iterdir()
                )
            records.append(
                {
                    "sample_id": sample_dir.name,
                    "path": str(sample_dir.relative_to(root)),
                    "matrix": str(matrix_path.relative_to(root)),
                    "matrix_sha256": sha256(matrix_path),
                    "barcodes": str(files.barcodes.relative_to(root))
                    if files.barcodes
                    else None,
                    "barcodes_sha256": sha256(files.barcodes)
                    if files.barcodes
                    else None,
                    "features": str(files.features.relative_to(root))
                    if files.features
                    else None,
                    "features_sha256": sha256(files.features)
                    if files.features
                    else None,
                    "positions": str(positions_path.relative_to(root))
                    if positions_path
                    else None,
                    "positions_sha256": sha256(positions_path)
                    if positions_path
                    else None,
                    "n_tissue_spots": len(dataset.barcodes),
                    "n_genes_total": int(dataset.metadata["genes_total"]),
                    "has_hires_image": has_hires_image,
                    "has_scalefactors": has_scalefactors,
                    "reader_status": "loaded",
                }
            )
        except Exception as exc:  # noqa: BLE001  # report bad samples without stopping
            records.append(
                {
                    "sample_id": sample_dir.name,
                    "path": str(sample_dir.relative_to(root)),
                    "matrix": str(matrix.relative_to(root)),
                    "matrix_sha256": sha256(matrix),
                    "reader_status": "error",
                    "error": str(exc),
                }
            )
    return records


def cohort_summary(records: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for record in records:
        cohort = str(record["path"]).split("/")[0]
        status = str(record["reader_status"])
        counts = summary.setdefault(
            cohort,
            {
                "loaded_sections": 0,
                "incomplete_sections": 0,
                "failed_sections": 0,
                "tissue_spots": 0,
            },
        )
        status_key = "failed" if status == "error" else status
        counts[f"{status_key}_sections"] += 1
        counts["tissue_spots"] += int(record.get("n_tissue_spots", 0))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO_ROOT / "data" / "public")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    records = inventory(root)
    output = args.out or root / "inventory.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "root": str(root),
        "n_loaded_samples": sum(r.get("reader_status") == "loaded" for r in records),
        "n_incomplete_samples": sum(
            r.get("reader_status") == "incomplete" for r in records
        ),
        "n_failed_samples": sum(r.get("reader_status") == "error" for r in records),
        "cohorts": cohort_summary(records),
        "samples": records,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {output}: {payload['n_loaded_samples']} loaded, {payload['n_failed_samples']} failed"
    )


if __name__ == "__main__":
    main()
