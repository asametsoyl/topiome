"""Transactional email.

Development and CI run without SMTP: messages are logged and the call returns
``False`` instead of failing the request. Production sets SMTP_HOST.
"""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from ..config import settings

log = logging.getLogger("topiome.email")


def send_email(to: str, subject: str, body: str) -> bool:
    if not settings.smtp_host:
        log.info("email skipped (no SMTP_HOST): to=%s subject=%s", to, subject)
        return False
    message = EmailMessage()
    message["From"] = settings.email_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=8) as smtp:
            if settings.smtp_port == 587:
                smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
        log.info("email sent: to=%s subject=%s", to, subject)
        return True
    except Exception as exc:  # noqa: BLE001 - email must never break the API
        log.warning("email failed: to=%s subject=%s error=%s", to, subject, exc)
        return False


def send_invitation(
    *, to: str, org_name: str, role: str, accept_url: str, expires_hours: int
) -> bool:
    return send_email(
        to,
        f"You are invited to {org_name} on Topiome",
        (
            f"{org_name} invited you to join their Topiome workspace as {role}.\n\n"
            f"Accept the invitation: {accept_url}\n\n"
            f"The link expires in {expires_hours} hours. If you were not expecting this, "
            "ignore the email.\n\n"
            "Topiome is for Research Use Only — not for diagnosis, prognosis, or treatment "
            "decisions."
        ),
    )


def send_run_finished(
    *, to: str, run_id: str, pack: str, sample_name: str, ok: bool, detail: str = ""
) -> bool:
    if ok:
        subject = f"Topiome run finished: {pack} / {sample_name}"
        body = (
            f"Your {pack} analysis for sample '{sample_name}' finished.\n\n"
            f"Run: {run_id}\n"
            "Open the workspace to review results and the Research Use Only notice.\n"
        )
    else:
        subject = f"Topiome run failed: {pack} / {sample_name}"
        body = (
            f"Your {pack} analysis for sample '{sample_name}' failed.\n\n"
            f"Run: {run_id}\n"
            f"Reason: {detail or 'unknown'}\n"
            "The run is retried automatically when the failure is transient. You can also "
            "start a new run from the sample page.\n"
        )
    return send_email(to, subject, body)
