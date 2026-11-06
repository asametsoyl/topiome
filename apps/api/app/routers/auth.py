from __future__ import annotations

import re
import secrets

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import select

from ..config import settings
from ..deps import CurrentAuth, DbSession, log_audit
from ..models import Membership, Organization, User
from ..ratelimit import LoginThrottle
from ..schemas import LoginRequest, MeOut, RegisterRequest
from ..security import (
    create_session_token,
    hash_password,
    needs_rehash,
    set_session_cookie,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])
throttle = LoginThrottle(settings.login_attempts_per_window, settings.login_window_minutes)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:40]
    return slug or "lab"


def _unique_slug(db, base: str) -> str:
    slug = _slugify(base)
    if db.scalar(select(Organization).where(Organization.slug == slug)) is None:
        return slug
    for _ in range(10):
        candidate = f"{slug}-{secrets.token_hex(2)}"
        if db.scalar(select(Organization).where(Organization.slug == candidate)) is None:
            return candidate
    return f"{slug}-{secrets.token_hex(4)}"


def _me(db, user: User) -> MeOut:
    membership = db.scalar(select(Membership).where(Membership.user_id == user.id).limit(1))
    if membership is None:
        raise HTTPException(status_code=500, detail="User has no organization")
    org = db.get(Organization, membership.org_id)
    return MeOut(user=user, org=org, role=membership.role)


@router.post("/register", response_model=MeOut, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: DbSession,
) -> MeOut:
    email = payload.email.lower().strip()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    org = Organization(
        name=(payload.org_name or f"{payload.name}'s lab").strip(),
        slug=_unique_slug(db, payload.org_name or payload.name),
        plan="academic",
    )
    user = User(
        email=email,
        name=payload.name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add_all([org, user])
    db.flush()
    db.add(Membership(user_id=user.id, org_id=org.id, role="owner"))
    log_audit(
        db,
        org_id=org.id,
        actor_id=user.id,
        action="auth.register",
        resource_type="user",
        resource_id=user.id,
        request=request,
    )
    db.commit()
    db.refresh(user)
    db.refresh(org)
    set_session_cookie(response, create_session_token(user.id, org.id))
    return MeOut(user=user, org=org, role="owner")


@router.post("/login", response_model=MeOut)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: DbSession,
) -> MeOut:
    email = payload.email.lower().strip()
    ip = _client_ip(request)
    wait = throttle.retry_after(ip, email)
    if wait is not None:
        raise HTTPException(
            status_code=429,
            detail="Too many sign-in attempts. Try again later.",
            headers={"Retry-After": str(wait)},
        )
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        throttle.failed(ip, email)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    throttle.succeeded(ip, email)

    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)
        db.commit()

    membership = db.scalar(select(Membership).where(Membership.user_id == user.id).limit(1))
    if membership is None:
        raise HTTPException(status_code=403, detail="No organization membership")
    log_audit(
        db,
        org_id=membership.org_id,
        actor_id=user.id,
        action="auth.login",
        request=request,
    )
    db.commit()
    set_session_cookie(response, create_session_token(user.id, membership.org_id))
    return _me(db, user)


@router.post("/logout")
def logout(response: Response, auth: CurrentAuth, db: DbSession, request: Request) -> dict:
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=auth.user.id,
        action="auth.logout",
        request=request,
    )
    db.commit()
    response.delete_cookie(settings.session_cookie_name, path="/")
    return {"ok": True}


@router.get("/me", response_model=MeOut)
def me(auth: CurrentAuth) -> MeOut:
    return MeOut(user=auth.user, org=auth.org, role=auth.role)


@router.post("/demo", response_model=MeOut)
def demo_login(response: Response, db: DbSession, request: Request) -> MeOut:
    if not settings.allow_demo_login:
        raise HTTPException(status_code=404, detail="Demo login disabled")
    user = db.scalar(select(User).where(User.email == settings.demo_email))
    if user is None:
        raise HTTPException(status_code=404, detail="Demo account not seeded")
    membership = db.scalar(select(Membership).where(Membership.user_id == user.id).limit(1))
    if membership is None:
        raise HTTPException(status_code=403, detail="Demo organization missing")
    log_audit(
        db,
        org_id=membership.org_id,
        actor_id=user.id,
        action="auth.demo_login",
        request=request,
    )
    db.commit()
    set_session_cookie(response, create_session_token(user.id, membership.org_id))
    return _me(db, user)
