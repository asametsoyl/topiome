from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from ..config import settings
from ..deps import AuthContext, CurrentAuth, DbSession, require_role
from ..schemas import BillingCheckoutRequest, BillingStatusOut
from ..services.billing import (
    BillingError,
    BillingUnavailable,
    apply_event,
    create_checkout_url,
    verify_webhook,
)
from ..services.quotas import usage_snapshot

router = APIRouter(prefix="/billing", tags=["billing"])
AdminAuth = Annotated[AuthContext, Depends(require_role("admin"))]


@router.get("/status", response_model=BillingStatusOut)
def billing_status(auth: CurrentAuth, db: DbSession) -> BillingStatusOut:
    usage = usage_snapshot(db, auth.org.id, auth.org.plan)
    return BillingStatusOut(
        plan=auth.org.plan,
        subscription_status=auth.org.subscription_status,
        renewal_at=auth.org.plan_renewal_at,
        billing_configured=bool(settings.stripe_secret_key),
        usage=usage,
    )


@router.post("/checkout")
def checkout(
    payload: BillingCheckoutRequest,
    auth: AdminAuth,
) -> dict[str, str]:
    if auth.org.subscription_status in {"active", "trialing", "past_due"}:
        raise HTTPException(status_code=409, detail="This workspace already has a subscription")
    try:
        url = create_checkout_url(
            org=auth.org,
            plan=payload.plan,
            email=auth.user.email,
        )
        return {"checkout_url": url}
    except BillingUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except BillingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def webhook(
    request: Request,
    db: DbSession,
    stripe_signature: str | None = Header(None, alias="Stripe-Signature"),
) -> dict[str, bool]:
    body = await request.body()
    try:
        event = verify_webhook(body, stripe_signature or "")
        apply_event(db, event)
        return {"received": True}
    except BillingUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except BillingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

