from __future__ import annotations

import re
import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import select

from ..config import settings
from ..deps import CurrentAuth, DbSession, log_audit
from ..models import Invitation, Membership, Organization, User
from ..ratelimit import LoginThrottle, register_limiter
from ..schemas import (
    AcceptInvitationRequest,
    LoginRequest,
    MeOut,
    MfaDisableRequest,
    MfaEnableOut,
    MfaEnableRequest,
    MfaSetupOut,
    RegisterRequest,
)
from ..security import (
    consume_recovery_code,
    create_session_token,
    hash_password,
    needs_rehash,
    new_recovery_codes,
    new_totp_secret,
    password_is_breached,
    set_session_cookie,
    totp_qr_svg,
    totp_uri,
    verify_password,
    verify_totp,
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
    ip = _client_ip(request)
    if settings.app_env != "test":
        wait = register_limiter.retry_after(ip)
        if wait is not None:
            raise HTTPException(
                status_code=429,
                detail="Too many registrations from this IP. Try again later.",
                headers={"Retry-After": str(wait)},
            )

    if password_is_breached(payload.password):
        raise HTTPException(
            status_code=400,
            detail="This password has appeared in data breaches. Please choose a more secure password.",
        )

    email = payload.email.lower().strip()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    if settings.app_env != "test":
        register_limiter.hit(ip)

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

    if user.totp_enabled:
        if not payload.totp_code:
            raise HTTPException(
                status_code=401,
                detail="MFA code required",
                headers={"X-MFA-Required": "true"},
            )
        code_valid = verify_totp(user.totp_secret, payload.totp_code)
        if not code_valid:
            remaining = consume_recovery_code(user.recovery_codes, payload.totp_code)
            if remaining is not None:
                user.recovery_codes = remaining
                code_valid = True
        if not code_valid:
            throttle.failed(ip, email)
            raise HTTPException(status_code=401, detail="Invalid MFA code")

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


@router.post("/mfa/setup", response_model=MfaSetupOut)
def mfa_setup(auth: CurrentAuth, db: DbSession) -> MfaSetupOut:
    if auth.auth_method != "session":
        raise HTTPException(status_code=403, detail="MFA settings require an interactive session")
    user = db.get(User, auth.user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.totp_enabled:
        raise HTTPException(status_code=409, detail="MFA is already enabled")
    secret = new_totp_secret()
    user.totp_secret = secret
    db.commit()
    uri = totp_uri(secret, user.email)
    return MfaSetupOut(
        secret=secret,
        otpauth_url=uri,
        qr_svg=totp_qr_svg(uri),
    )


@router.post("/mfa/enable", response_model=MfaEnableOut)
def mfa_enable(
    payload: MfaEnableRequest,
    auth: CurrentAuth,
    request: Request,
    db: DbSession,
) -> MfaEnableOut:
    if auth.auth_method != "session":
        raise HTTPException(status_code=403, detail="MFA settings require an interactive session")
    ip = _client_ip(request)
    email = auth.user.email.lower()
    wait = throttle.retry_after(ip, email)
    if wait is not None:
        raise HTTPException(
            status_code=429,
            detail="Too many MFA verification attempts. Try again later.",
            headers={"Retry-After": str(wait)},
        )
    user = db.get(User, auth.user.id)
    if user is None or not user.totp_secret:
        raise HTTPException(status_code=400, detail="MFA setup has not been initiated")
    if not verify_totp(user.totp_secret, payload.code):
        throttle.failed(ip, email)
        raise HTTPException(status_code=400, detail="Invalid verification code")
    throttle.succeeded(ip, email)
    user.totp_enabled = True
    codes_plain, codes_hashes = new_recovery_codes()
    user.recovery_codes = codes_hashes
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=user.id,
        action="auth.mfa_enable",
        resource_type="user",
        resource_id=user.id,
        request=request,
    )
    db.commit()
    return MfaEnableOut(enabled=True, recovery_codes=codes_plain)


@router.post("/mfa/disable")
def mfa_disable(
    payload: MfaDisableRequest,
    auth: CurrentAuth,
    request: Request,
    db: DbSession,
) -> dict[str, bool]:
    if auth.auth_method != "session":
        raise HTTPException(status_code=403, detail="MFA settings require an interactive session")
    ip = _client_ip(request)
    email = auth.user.email.lower()
    wait = throttle.retry_after(ip, email)
    if wait is not None:
        raise HTTPException(
            status_code=429,
            detail="Too many MFA verification attempts. Try again later.",
            headers={"Retry-After": str(wait)},
        )
    user = db.get(User, auth.user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")
    if not verify_totp(user.totp_secret, payload.code):
        throttle.failed(ip, email)
        raise HTTPException(status_code=400, detail="Invalid verification code")
    throttle.succeeded(ip, email)
    user.totp_enabled = False
    user.totp_secret = None
    user.recovery_codes = []
    log_audit(
        db,
        org_id=auth.org.id,
        actor_id=user.id,
        action="auth.mfa_disable",
        resource_type="user",
        resource_id=user.id,
        request=request,
    )
    db.commit()
    return {"ok": True}


@router.post("/invitations/accept", response_model=MeOut)
def accept_invitation(
    payload: AcceptInvitationRequest,
    request: Request,
    response: Response,
    db: DbSession,
) -> MeOut:
    import hashlib

    token_hash = hashlib.sha256(payload.token.strip().encode()).hexdigest()
    invite = db.scalar(select(Invitation).where(Invitation.token_hash == token_hash))
    if invite is None:
        raise HTTPException(status_code=404, detail="Invitation not found or invalid token")
    if invite.accepted_at is not None:
        raise HTTPException(status_code=400, detail="Invitation has already been accepted")
    now = datetime.now(UTC)
    if invite.expires_at < now:
        raise HTTPException(status_code=400, detail="Invitation has expired")

    org = db.get(Organization, invite.org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    user = db.scalar(select(User).where(User.email == invite.email.lower()))
    if user is None:
        if not payload.name or not payload.password:
            raise HTTPException(
                status_code=400,
                detail="Name and password are required for new accounts",
            )
        if password_is_breached(payload.password):
            raise HTTPException(
                status_code=400,
                detail="This password has appeared in data breaches. Please choose a more secure password.",
            )
        user = User(
            email=invite.email.lower(),
            name=payload.name.strip(),
            password_hash=hash_password(payload.password),
        )
        db.add(user)
        db.flush()
    elif not user.is_active:
        raise HTTPException(status_code=403, detail="This account is inactive")
    elif user.totp_enabled:
        valid = verify_totp(user.totp_secret, payload.totp_code)
        if not valid:
            remaining = consume_recovery_code(user.recovery_codes, payload.totp_code)
            if remaining is not None:
                user.recovery_codes = remaining
                valid = True
        if not valid:
            raise HTTPException(status_code=401, detail="A valid MFA code is required")

    # Check if membership already exists
    membership = db.scalar(
        select(Membership).where(
            Membership.user_id == user.id, Membership.org_id == org.id
        )
    )
    if membership is None:
        membership = Membership(
            user_id=user.id,
            org_id=org.id,
            role=invite.role,
        )
        db.add(membership)

    invite.accepted_at = now
    log_audit(
        db,
        org_id=org.id,
        actor_id=user.id,
        action="auth.invite_accept",
        resource_type="invitation",
        resource_id=invite.id,
        request=request,
    )
    db.commit()
    db.refresh(user)
    db.refresh(org)
    set_session_cookie(response, create_session_token(user.id, org.id))
    return MeOut(user=user, org=org, role=membership.role)


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
