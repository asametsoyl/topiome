"""Object storage: local filesystem (development) or S3-compatible (production).

The analysis pipeline needs real files on disk. ``materialize_prefix`` is the
bridge: local storage returns its folder, S3 downloads the prefix into a cache
directory first. Uploads go straight to the configured backend.
"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
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


class BaseStorage:
    def path(self, key: str) -> Path:  # pragma: no cover - interface
        raise NotImplementedError

    def materialize_prefix(self, prefix: str) -> Path:  # pragma: no cover - interface
        raise NotImplementedError

    def save_bytes(self, key: str, data: bytes) -> str:  # pragma: no cover - interface
        raise NotImplementedError

    def save_upload(self, key: str, upload: UploadFile) -> tuple[int, str]:  # pragma: no cover
        raise NotImplementedError

    def read_bytes(self, key: str) -> bytes:  # pragma: no cover - interface
        raise NotImplementedError

    def read_text(self, key: str) -> str:  # pragma: no cover - interface
        raise NotImplementedError

    def delete_prefix(self, prefix: str) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def exists(self, key: str) -> bool:  # pragma: no cover - interface
        raise NotImplementedError

    def signed_url(self, key: str, *, expires: int | None = None) -> str | None:
        return None


class LocalStorage(BaseStorage):
    def __init__(self, base: Path):
        base.mkdir(parents=True, exist_ok=True)
        # Resolve symlinks (e.g. storage moved off the exFAT disk, or macOS /var →
        # /private/var) so the containment check in _safe_path compares like with like.
        self.base = base.resolve()

    def path(self, key: str) -> Path:
        return _safe_path(self.base, key)

    def materialize_prefix(self, prefix: str) -> Path:
        return self.path(prefix)

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


class S3Storage(BaseStorage):
    """S3-compatible backend (AWS S3, MinIO, R2, ...).

    ``client`` is injectable so tests can pass a small fake without boto3.
    """

    def __init__(self, *, cache_dir: Path, client=None):
        self.cache = cache_dir.resolve()
        self.cache.mkdir(parents=True, exist_ok=True)
        self.bucket = settings.s3_bucket
        if client is not None:
            self.client = client
        else:  # pragma: no cover - exercised only with a real backend
            import boto3

            kwargs = {
                "region_name": settings.s3_region,
                "aws_access_key_id": settings.s3_access_key_id or None,
                "aws_secret_access_key": settings.s3_secret_access_key or None,
            }
            if settings.s3_endpoint_url:
                kwargs["endpoint_url"] = settings.s3_endpoint_url
            self.client = boto3.client("s3", **kwargs)

    def path(self, key: str) -> Path:
        target = _safe_path(self.cache, key)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            self.client.download_file(self.bucket, key, str(target))
        return target

    def materialize_prefix(self, prefix: str) -> Path:
        root = _safe_path(self.cache, prefix)
        root.mkdir(parents=True, exist_ok=True)
        token = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": prefix.rstrip("/") + "/"}
            if token:
                kwargs["ContinuationToken"] = token
            response = self.client.list_objects_v2(**kwargs)
            for item in response.get("Contents", []):
                key = item["Key"]
                if key.endswith("/"):
                    continue
                self.path(key)
            if not response.get("IsTruncated"):
                break
            token = response.get("NextContinuationToken")
        return root

    def save_bytes(self, key: str, data: bytes) -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
        return key

    def save_upload(self, key: str, upload: UploadFile) -> tuple[int, str]:
        digest = hashlib.sha256()
        size = 0
        max_bytes = settings.max_upload_mb * 1024 * 1024
        with tempfile.NamedTemporaryFile(delete=False, dir=self.cache) as temp:
            temp_path = Path(temp.name)
            while chunk := upload.file.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    temp_path.unlink(missing_ok=True)
                    raise StorageError(f"File exceeds {settings.max_upload_mb} MB limit")
                digest.update(chunk)
                temp.write(chunk)
        try:
            self.client.upload_file(str(temp_path), self.bucket, key)
        finally:
            temp_path.unlink(missing_ok=True)
        return size, digest.hexdigest()

    def read_bytes(self, key: str) -> bytes:
        return self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()

    def read_text(self, key: str) -> str:
        return self.read_bytes(key).decode("utf-8")

    def delete_prefix(self, prefix: str) -> None:
        token = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": prefix}
            if token:
                kwargs["ContinuationToken"] = token
            response = self.client.list_objects_v2(**kwargs)
            keys = [{"Key": item["Key"]} for item in response.get("Contents", [])]
            if keys:
                self.client.delete_objects(
                    Bucket=self.bucket, Delete={"Objects": keys[:1000]}
                )
            if not response.get("IsTruncated"):
                break
            token = response.get("NextContinuationToken")

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:  # noqa: BLE001 - provider-specific 404 classes
            return False

    def signed_url(self, key: str, *, expires: int | None = None) -> str | None:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires or settings.s3_presign_seconds,
        )


def build_storage() -> BaseStorage:
    if settings.storage_backend == "s3":
        return S3Storage(cache_dir=settings.storage_path / "_cache")
    return LocalStorage(settings.storage_path)


storage = build_storage()
