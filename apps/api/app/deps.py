from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import ApiKey, AuditLog, Membership, Organization, User
from .security import decode_session_token, hash_api_key

DbSession = Annotated[Session, Depends(get_db)]


@dataclass
class AuthContext:
    user: User
    org: Organization
    membership: Membership
    role_override: str | None = None
    auth_method: str = "session"

    @property
    def role(self) -> str:
        return self.role_override or self.membership.role


def _token_from_request(request: Request) -> str | None:
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return api_key.strip()
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        return token
    header = request.headers.get("Authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return None


def get_auth_context(request: Request, db: DbSession) -> AuthContext:
    raw_token = _token_from_request(request)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Cookie"},
        )

    if raw_token.startswith("topiome_live_"):
        key_hash = hash_api_key(raw_token)
        api_key = db.scalar(
            select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.revoked_at.is_(None))
        )
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked API key",
            )
        api_key.last_used_at = datetime.now(UTC)
        db.commit()

        user = db.get(User, api_key.user_id)
        org = db.get(Organization, api_key.org_id)
        if not user or not user.is_active or not org:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key owner or organization inactive",
            )
        membership = db.scalar(
            select(Membership).where(
                Membership.user_id == user.id, Membership.org_id == org.id
            )
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No organization membership"
            )
        # API keys are limited to analyst capabilities; account admin actions
        # must use the owner's interactive session.
        return AuthContext(
            user=user,
            org=org,
            membership=membership,
            role_override="analyst",
            auth_method="api_key",
        )

    payload = decode_session_token(raw_token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    user = db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    membership = db.scalar(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.org_id == payload.get("org"),
        )
    )
    if membership is None:
        membership = db.scalar(
            select(Membership).where(Membership.user_id == user.id).limit(1)
        )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization")

    org = db.get(Organization, membership.org_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization missing")

    return AuthContext(user=user, org=org, membership=membership)


CurrentAuth = Annotated[AuthContext, Depends(get_auth_context)]
ROLE_RANK = {"viewer": 0, "analyst": 1, "admin": 2, "owner": 3}


def require_role(minimum: str):
    def _checker(auth: CurrentAuth) -> AuthContext:
        if ROLE_RANK.get(auth.role, -1) < ROLE_RANK.get(minimum, 99):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {minimum} role",
            )
        return auth

    return _checker


def log_audit(
    db: Session,
    *,
    org_id: str,
    actor_id: str | None,
    action: str,
    resource_type: str = "",
    resource_id: str = "",
    request: Request | None = None,
    metadata: dict | None = None,
) -> None:
    entry = AuditLog(
        org_id=org_id,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip=(request.client.host if request and request.client else ""),
        user_agent=(request.headers.get("user-agent", "")[:300] if request else ""),
        log_metadata=metadata or {},
    )
    db.add(entry)


# Viewers are read-only; creating or changing data needs at least the analyst role.
AnalystAuth = Annotated[AuthContext, Depends(require_role("analyst"))]
