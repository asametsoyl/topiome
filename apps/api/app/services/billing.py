"""Stripe billing without the SDK.

Checkout sessions are created with form-encoded HTTPS calls; webhooks use the
documented HMAC-SHA256 signature scheme. Nothing here runs unless
STRIPE_SECRET_KEY is configured, so development and CI never call Stripe.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Organization

STRIPE_API = "https://api.stripe.com/v1"
SIGNATURE_TOLERANCE_SECONDS = 300

PLAN_CATALOG: dict[str, dict[str, Any]] = {
    "academic": {"name": "Academic", "price_usd": 0, "interval": None},
    "lab": {"name": "Lab", "price_usd": 399, "interval": "year"},
    "institution": {"name": "Institution", "price_usd": None, "interval": None},
}


class BillingError(Exception):
    pass


class BillingUnavailable(BillingError):
    pass


def _price_id(plan: str) -> str:
    if plan == "lab":
        return settings.stripe_price_lab
    if plan == "institution":
        return settings.stripe_price_institution
    return ""


def create_checkout_url(*, org: Organization, plan: str, email: str) -> str:
    if plan not in PLAN_CATALOG or plan == "academic":
        raise BillingError("Choose the Lab or Institution plan")
    if not settings.stripe_secret_key:
        raise BillingUnavailable("Billing is not configured on this deployment")
    price = _price_id(plan)
    if not price:
        raise BillingUnavailable(f"No Stripe price configured for the {plan} plan")

    data: dict[str, str] = {
        "mode": "subscription",
        "payment_method_types[0]": "card",
        "line_items[0][price]": price,
        "line_items[0][quantity]": "1",
        "success_url": f"{settings.app_url}/app/settings?billing=success",
        "cancel_url": f"{settings.app_url}/app/settings?billing=cancelled",
        "client_reference_id": org.id,
        "metadata[org_id]": org.id,
        "metadata[plan]": plan,
        "subscription_data[metadata][org_id]": org.id,
        "subscription_data[metadata][plan]": plan,
    }
    if org.stripe_customer_id:
        data["customer"] = org.stripe_customer_id
    else:
        data["customer_email"] = email

    response = httpx.post(
        f"{STRIPE_API}/checkout/sessions",
        data=data,
        auth=(settings.stripe_secret_key, ""),
        timeout=20,
    )
    if response.status_code >= 400:
        raise BillingError(f"Stripe checkout failed ({response.status_code})")
    payload = response.json()
    url = payload.get("url")
    if not url:
        raise BillingError("Stripe did not return a checkout URL")
    return str(url)


def verify_webhook(payload: bytes, signature_header: str) -> dict[str, Any]:
    if not settings.stripe_webhook_secret:
        raise BillingUnavailable("Stripe webhook secret is not configured")
    if not signature_header:
        raise BillingError("Missing Stripe-Signature header")

    parts: dict[str, list[str]] = {}
    for item in signature_header.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        parts.setdefault(key.strip(), []).append(value.strip())
    timestamp = parts.get("t", [""])[0]
    signatures = parts.get("v1", [])
    if not timestamp or not signatures:
        raise BillingError("Malformed Stripe-Signature header")
    try:
        age = abs(time.time() - int(timestamp))
    except ValueError as exc:
        raise BillingError("Invalid Stripe signature timestamp") from exc
    if age > SIGNATURE_TOLERANCE_SECONDS:
        raise BillingError("Stripe signature timestamp is too old")

    expected = hmac.new(
        settings.stripe_webhook_secret.encode(),
        timestamp.encode() + b"." + payload,
        hashlib.sha256,
    ).hexdigest()
    if not any(hmac.compare_digest(expected, candidate) for candidate in signatures):
        raise BillingError("Invalid Stripe signature")
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise BillingError("Invalid webhook JSON") from exc


def _org_by_customer(db: Session, customer_id: str) -> Organization | None:
    if not customer_id:
        return None
    return db.scalar(
        select(Organization).where(Organization.stripe_customer_id == customer_id)
    )


def _set_plan(org: Organization, plan: str, status: str, renewal: int | None = None) -> None:
    if plan in PLAN_CATALOG:
        org.plan = plan
    org.subscription_status = status
    if renewal:
        org.plan_renewal_at = datetime.fromtimestamp(renewal, UTC)


def apply_event(db: Session, event: dict[str, Any]) -> None:
    kind = event.get("type", "")
    obj = (event.get("data") or {}).get("object") or {}

    if kind == "checkout.session.completed":
        metadata = obj.get("metadata") or {}
        org_id = metadata.get("org_id") or obj.get("client_reference_id")
        org = db.get(Organization, org_id) if org_id else None
        if org is None:
            return
        if obj.get("customer"):
            org.stripe_customer_id = str(obj["customer"])
        _set_plan(org, str(metadata.get("plan", "lab")), "active")
        db.commit()
        return

    if kind in {"customer.subscription.updated", "customer.subscription.deleted"}:
        metadata = obj.get("metadata") or {}
        org = db.get(Organization, metadata.get("org_id")) if metadata.get("org_id") else None
        if org is None:
            org = _org_by_customer(db, str(obj.get("customer", "")))
        if org is None:
            return
        if kind.endswith("deleted"):
            _set_plan(org, "academic", "canceled")
        else:
            status = str(obj.get("status", "active"))
            plan = str(metadata.get("plan", org.plan))
            _set_plan(org, plan, status, obj.get("current_period_end"))
        db.commit()
        return

    if kind in {"invoice.payment_failed", "invoice.paid"}:
        org = _org_by_customer(db, str(obj.get("customer", "")))
        if org is None:
            return
        org.subscription_status = "past_due" if kind.endswith("failed") else "active"
        db.commit()
