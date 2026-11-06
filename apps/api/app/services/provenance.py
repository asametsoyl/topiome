"""Run provenance: everything needed to trace and reproduce an analysis.

AGENTS.md rule 5 — every run records pipeline, disease pack, reference data and
software versions plus its parameters and input checksums.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import UTC, datetime
from functools import lru_cache
from importlib import metadata
from typing import Any

from ..config import ROOT

API_VERSION = "0.1.0"
UNVERSIONED = "unversioned"


@lru_cache
def software_commit() -> str:
    """Commit of the running code: TOPIOME_GIT_COMMIT, then git, else 'unversioned'."""
    env_commit = os.environ.get("TOPIOME_GIT_COMMIT", "").strip()
    if env_commit:
        return env_commit
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return UNVERSIONED
    commit = out.stdout.strip()
    if out.returncode != 0 or not commit:
        return UNVERSIONED
    try:
        dirty = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        dirty = ""
    return f"{commit}-dirty" if dirty else commit


def pack_fingerprint(pack: dict[str, Any]) -> str:
    """Stable SHA-256 of the pack content (markers, zones, targets, reference)."""
    canonical = json.dumps(pack, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "unknown"


def reference_info(pack: dict[str, Any]) -> dict[str, Any]:
    reference = pack.get("reference") or {}
    return {
        # Until real scRNA references are versioned, the marker sets in the pack are
        # the reference; the pack fingerprint pins them exactly.
        "version": str(reference.get("version") or f"pack-markers@{pack['version']}"),
        "scrna_sources": list(reference.get("scrna_sources", [])),
        "spatial_sources": list(reference.get("spatial_sources", [])),
    }


def build_provenance(
    *,
    pipeline_version: str,
    pack: dict[str, Any],
    params: dict[str, Any],
    input_kind: str,
    input_files: list[dict[str, Any]],
    synthetic_seed: int | None = None,
    signatures: dict[str, Any] | None = None,
    domain_model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "recorded_at": datetime.now(UTC).isoformat(),
        "pipeline_version": pipeline_version,
        "disease_pack": {
            "id": pack["id"],
            "version": pack["version"],
            "status": pack.get("status", ""),
            "sha256": pack_fingerprint(pack),
        },
        "reference": {**reference_info(pack), "signatures": signatures},
        "domain_model": domain_model,
        "params": params,
        "input": {
            "kind": input_kind,
            "files": input_files,
            "synthetic_seed": synthetic_seed,
        },
        "software": {
            "commit": software_commit(),
            "api_version": API_VERSION,
            "analysis_package": _package_version("topiome-analysis"),
            "python": platform.python_version(),
            "numpy": _package_version("numpy"),
            "scipy": _package_version("scipy"),
            "scikit_learn": _package_version("scikit-learn"),
            "pandas": _package_version("pandas"),
        },
    }
