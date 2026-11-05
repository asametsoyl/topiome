from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import desc, select

from ..deps import AuthContext, CurrentAuth, DbSession, log_audit, require_role
from ..models import AuditLog, Membership, User
from ..schemas import AuditLogOut, MemberOut, OrgOut

router = APIRouter(prefix="/org", tags=["organization"])
AdminAuth = Annotated[AuthContext, Depends(require_role("admin"))]


@router.get("", response_model=OrgOut)
def get_org(auth: CurrentAuth) -> OrgOut:
    return OrgOut.model_validate(auth.org)


@router.patch("", response_model=OrgOut)
def update_org(
    payload: dict,
    request: Request,
    auth: AdminAuth,
    db: DbSession,
) -> OrgOut:
    name = str(payload.get("name", "")).strip()
    if name:
        auth.org.name = name[:160]
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="org.update",
        resource_type="organization",
        resource_id=auth.org.id,
        request=request,
    )
    db.commit()
    db.refresh(auth.org)
    return OrgOut.model_validate(auth.org)


@router.get("/members", response_model=list[MemberOut])
def list_members(auth: CurrentAuth, db: DbSession) -> list[MemberOut]:
    rows = db.execute(
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.org_id == auth.org.id)
        .order_by(User.name)
    ).all()
    return [
        MemberOut(
            id=membership.id,
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=membership.role,
            created_at=membership.created_at,
        )
        for membership, user in rows
    ]


@router.get("/audit-logs", response_model=list[AuditLogOut])
def audit_logs(
    auth: AdminAuth,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AuditLog]:
    return list(
        db.scalars(
            select(AuditLog)
            .where(AuditLog.org_id == auth.org.id)
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
        )
    )
