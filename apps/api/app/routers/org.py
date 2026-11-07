from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc, select

from ..config import settings
from ..deps import AuthContext, CurrentAuth, DbSession, log_audit, require_role
from ..models import AuditLog, Invitation, Membership, User
from ..schemas import (
    AuditLogOut,
    InvitationCreate,
    InvitationOut,
    MemberOut,
    OrgOut,
)
from ..services.email import send_invitation
from ..services.quotas import QuotaExceeded, ensure_member

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


@router.post("/invitations", response_model=InvitationOut, status_code=status.HTTP_201_CREATED)
def create_invitation(
    payload: InvitationCreate,
    request: Request,
    auth: AdminAuth,
    db: DbSession,
) -> InvitationOut:
    email = payload.email.lower().strip()
    existing = db.scalar(
        select(Membership)
        .join(User, User.id == Membership.user_id)
        .where(Membership.org_id == auth.org.id, User.email == email)
    )
    if existing:
        raise HTTPException(status_code=409, detail="User is already a member of this organization")

    duplicate = db.scalar(
        select(Invitation).where(
            Invitation.org_id == auth.org.id,
            Invitation.email == email,
            Invitation.accepted_at.is_(None),
            Invitation.expires_at > datetime.now(UTC),
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="An active invitation already exists for this email")
    try:
        ensure_member(db, auth.org.id, auth.org.plan)
    except QuotaExceeded as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.now(UTC) + timedelta(hours=settings.invitation_ttl_hours)

    invitation = Invitation(
        org_id=auth.org.id,
        email=email,
        role=payload.role,
        token_hash=token_hash,
        invited_by=auth.user.id,
        expires_at=expires_at,
    )
    db.add(invitation)
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="org.invite",
        resource_type="invitation",
        resource_id=invitation.id,
        request=request,
        metadata={"email": email, "role": payload.role},
    )
    db.commit()
    db.refresh(invitation)

    accept_url = f"{settings.app_url}/accept-invite?token={token}"
    send_invitation(
        to=email,
        org_name=auth.org.name,
        role=payload.role,
        accept_url=accept_url,
        expires_hours=settings.invitation_ttl_hours,
    )

    out = InvitationOut(
        id=invitation.id,
        email=invitation.email,
        role=invitation.role,
        expires_at=invitation.expires_at,
        accepted_at=invitation.accepted_at,
        created_at=invitation.created_at,
        accept_url=accept_url,
    )
    return out


@router.get("/invitations", response_model=list[InvitationOut])
def list_invitations(auth: AdminAuth, db: DbSession) -> list[InvitationOut]:
    invites = list(
        db.scalars(
            select(Invitation)
            .where(Invitation.org_id == auth.org.id, Invitation.accepted_at.is_(None))
            .order_by(desc(Invitation.created_at))
        )
    )
    return [
        InvitationOut(
            id=inv.id,
            email=inv.email,
            role=inv.role,
            expires_at=inv.expires_at,
            accepted_at=inv.accepted_at,
            created_at=inv.created_at,
        )
        for inv in invites
    ]


@router.delete("/invitations/{invite_id}")
def revoke_invitation(
    invite_id: str,
    request: Request,
    auth: AdminAuth,
    db: DbSession,
) -> dict[str, bool]:
    invite = db.get(Invitation, invite_id)
    if invite is None or invite.org_id != auth.org.id:
        raise HTTPException(status_code=404, detail="Invitation not found")
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="org.invite_revoke",
        resource_type="invitation",
        resource_id=invite.id,
        request=request,
    )
    db.delete(invite)
    db.commit()
    return {"ok": True}


@router.patch("/members/{member_id}", response_model=MemberOut)
def update_member_role(
    member_id: str,
    payload: dict,
    request: Request,
    auth: AdminAuth,
    db: DbSession,
) -> MemberOut:
    membership = db.get(Membership, member_id)
    if membership is None or membership.org_id != auth.org.id:
        raise HTTPException(status_code=404, detail="Membership not found")
    new_role = payload.get("role")
    if new_role not in {"owner", "admin", "analyst", "viewer"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    if membership.role == "owner" and new_role != "owner":
        from sqlalchemy import func

        owners_count = db.scalar(
            select(func.count(Membership.id)).where(
                Membership.org_id == auth.org.id,
                Membership.role == "owner",
            )
        )
        if (owners_count or 0) <= 1:
            raise HTTPException(status_code=400, detail="Cannot demote the only owner")
    if new_role == "owner" and auth.role != "owner":
        raise HTTPException(status_code=403, detail="Only an owner can assign the owner role")
    membership.role = new_role
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="org.member_role_update",
        resource_type="membership",
        resource_id=membership.id,
        request=request,
        metadata={"new_role": new_role},
    )
    db.commit()
    user = db.get(User, membership.user_id)
    return MemberOut(
        id=membership.id,
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=membership.role,
        created_at=membership.created_at,
    )


@router.delete("/members/{member_id}")
def remove_member(
    member_id: str,
    request: Request,
    auth: AdminAuth,
    db: DbSession,
) -> dict[str, bool]:
    membership = db.get(Membership, member_id)
    if membership is None or membership.org_id != auth.org.id:
        raise HTTPException(status_code=404, detail="Membership not found")
    if membership.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove an organization owner")
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="org.member_remove",
        resource_type="membership",
        resource_id=membership.id,
        request=request,
    )
    db.delete(membership)
    db.commit()
    return {"ok": True}
