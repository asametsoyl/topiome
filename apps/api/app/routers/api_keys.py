from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import desc, select

from ..deps import AuthContext, CurrentAuth, DbSession, log_audit, require_role
from ..models import ApiKey
from ..schemas import ApiKeyCreate, ApiKeyCreated, ApiKeyOut
from ..security import generate_api_key

router = APIRouter(prefix="/api-keys", tags=["api_keys"])
AdminAuth = Annotated[AuthContext, Depends(require_role("admin"))]


@router.post("", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: ApiKeyCreate,
    request: Request,
    auth: AdminAuth,
    db: DbSession,
) -> ApiKeyCreated:
    plaintext, prefix, digest = generate_api_key()
    api_key = ApiKey(
        org_id=auth.org.id,
        user_id=auth.user.id,
        name=payload.name.strip()[:120],
        prefix=prefix,
        key_hash=digest,
    )
    db.add(api_key)
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="api_key.create",
        resource_type="api_key",
        resource_id=api_key.id,
        request=request,
        metadata={"name": api_key.name, "prefix": prefix},
    )
    db.commit()
    db.refresh(api_key)
    return ApiKeyCreated(
        id=api_key.id,
        name=api_key.name,
        prefix=api_key.prefix,
        last_used_at=api_key.last_used_at,
        revoked_at=api_key.revoked_at,
        created_at=api_key.created_at,
        key=plaintext,
    )


@router.get("", response_model=list[ApiKeyOut])
def list_api_keys(auth: CurrentAuth, db: DbSession) -> list[ApiKeyOut]:
    keys = list(
        db.scalars(
            select(ApiKey)
            .where(ApiKey.org_id == auth.org.id, ApiKey.revoked_at.is_(None))
            .order_by(desc(ApiKey.created_at))
        )
    )
    return [ApiKeyOut.model_validate(k) for k in keys]


@router.delete("/{key_id}")
def revoke_api_key(
    key_id: str,
    request: Request,
    auth: AdminAuth,
    db: DbSession,
) -> dict[str, bool]:
    api_key = db.get(ApiKey, key_id)
    if api_key is None or api_key.org_id != auth.org.id:
        raise HTTPException(status_code=404, detail="API key not found")
    api_key.revoked_at = datetime.now(UTC)
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="api_key.revoke",
        resource_type="api_key",
        resource_id=api_key.id,
        request=request,
        metadata={"name": api_key.name, "prefix": api_key.prefix},
    )
    db.commit()
    return {"ok": True}

