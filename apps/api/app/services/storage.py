from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from fastapi import UploadFile

from ..config import settings


class StorageError(ValueError):
    pass


def _safe_path(base: Path, key: str) -> Path:
    if key.startswith("/") or ".." in Path(key).parts:
        raise StorageError("Invalid storage key")
    path = (base / key).resolve()
    if base not in path.parents and path != base:
        raise StorageError("Invalid storage key")
    return path


class LocalStorage:
    def __init__(self, base: Path):
        base.mkdir(parents=True, exist_ok=True)
        # Resolve symlinks (e.g. storage moved off the exFAT disk, or macOS /var →
        # /private/var) so the containment check in _safe_path compares like with like.
        self.base = base.resolve()

    def path(self, key: str) -> Path:
        return _safe_path(self.base, key)

    def save_bytes(self, key: str, data: bytes) -> str:
        path = self.path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def save_upload(self, key: str, upload: UploadFile) -> tuple[int, str]:
        path = self.path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        size = 0
        max_bytes = settings.max_upload_mb * 1024 * 1024
        with open(path, "wb") as out:
            while chunk := upload.file.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    out.close()
                    path.unlink(missing_ok=True)
                    raise StorageError(f"File exceeds {settings.max_upload_mb} MB limit")
                digest.update(chunk)
                out.write(chunk)
        return size, digest.hexdigest()

    def read_bytes(self, key: str) -> bytes:
        return self.path(key).read_bytes()

    def read_text(self, key: str) -> str:
        return self.path(key).read_text(encoding="utf-8")

    def delete_prefix(self, prefix: str) -> None:
        path = self.path(prefix)
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)

    def exists(self, key: str) -> bool:
        return self.path(key).exists()


storage = LocalStorage(settings.storage_path)
