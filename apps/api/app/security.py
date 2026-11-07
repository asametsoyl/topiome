from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import jwt
import pyotp
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Response

from .config import settings

log = logging.getLogger("topiome.security")

# A short local list catches the worst passwords without a network round-trip.
COMMON_PASSWORDS = {
    "password",
    "password1",
    "password123",
    "1234567890",
    "12345678",
    "123456789",
    "qwerty123",
    "qwertyuiop",
    "letmein123",
    "welcome123",
    "admin12345",
    "iloveyou1",
    "monkey123",
    "dragon123",
    "football1",
    "baseball1",
    "abc123456",
    "topiome123",
}

_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, Exception):
        return False


def needs_rehash(password_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(password_hash)
    except Exception:
        return False


def create_session_token(user_id: str, org_id: str) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": user_id,
        "org": org_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_ttl_minutes),
        "iss": "topiome",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_session_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
            issuer="topiome",
        )
    except jwt.PyJWTError:
        return None


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        secure=not settings.is_dev,
        samesite="lax",
        max_age=settings.access_token_ttl_minutes * 60,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(settings.session_cookie_name, path="/")


def generate_api_key() -> tuple[str, str, str]:
    """Returns (plaintext, prefix, sha256 hash)."""
    raw = secrets.token_urlsafe(32)
    plaintext = f"topiome_live_{raw}"
    prefix = plaintext[:20]
    digest = hashlib.sha256(plaintext.encode()).hexdigest()
    return plaintext, prefix, digest


def hash_api_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode()).hexdigest()


# ── MFA (TOTP + recovery codes) ─────────────────────────────────────────────


def new_totp_secret() -> str:
    return pyotp.random_base32()


def totp_uri(secret: str, email: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=settings.mfa_issuer)


def verify_totp(secret: str | None, code: str | None) -> bool:
    if not secret or not code:
        return False
    normalized = "".join(ch for ch in code if ch.isdigit())
    if len(normalized) != 6:
        return False
    return bool(pyotp.TOTP(secret).verify(normalized, valid_window=1))


def new_recovery_codes(count: int = 8) -> tuple[list[str], list[str]]:
    plaintext = [f"{secrets.token_hex(2)}-{secrets.token_hex(2)}" for _ in range(count)]
    hashes = [hashlib.sha256(code.encode()).hexdigest() for code in plaintext]
    return plaintext, hashes


def consume_recovery_code(stored_hashes: list[str] | None, code: str | None) -> list[str] | None:
    """Returns the remaining hashes when ``code`` is valid, else None."""
    if not stored_hashes or not code:
        return None
    digest = hashlib.sha256(code.strip().lower().encode()).hexdigest()
    for index, stored in enumerate(stored_hashes):
        if secrets.compare_digest(stored, digest):
            return stored_hashes[:index] + stored_hashes[index + 1 :]
    return None


def totp_qr_svg(uri: str) -> str | None:
    try:
        import qrcode
        import qrcode.image.svg

        image = qrcode.make(uri, image_factory=qrcode.image.svg.SvgPathImage)
        import io

        buffer = io.BytesIO()
        image.save(buffer)
        return buffer.getvalue().decode("utf-8")
    except Exception:  # noqa: BLE001 - QR is a convenience, the secret still works
        return None


# ── Breached-password check (Have I Been Pwned k-anonymity) ────────────────


def password_is_breached(password: str) -> bool:
    if password.strip().lower() in COMMON_PASSWORDS:
        return True
    if settings.is_dev or not settings.breach_check_enabled:
        return False
    digest = hashlib.sha1(password.encode()).hexdigest().upper()  # noqa: S324 - HIBP protocol
    prefix, suffix = digest[:5], digest[5:]
    try:
        response = httpx.get(
            f"https://api.pwnedpasswords.com/range/{prefix}",
            headers={"Add-Padding": "true", "User-Agent": "Topiome password check"},
            timeout=4,
        )
        if response.status_code != 200:
            return False
        for line in response.text.splitlines():
            candidate, _, count = line.partition(":")
            if candidate.strip().upper() == suffix and int(count or 0) > 0:
                return True
    except Exception as exc:  # noqa: BLE001 - fail open, never block sign-up on HIBP
        log.warning("breach check failed: %s", exc)
    return False
