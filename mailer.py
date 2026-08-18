"""Lightweight SMTP email sending, configured entirely via environment variables.

No third-party mail library is required — this uses Python's built-in smtplib.
If SMTP settings aren't configured (e.g. local dev without a .env file), sending
is silently skipped so the rest of the app keeps working.
"""
import os
import smtplib
from email.message import EmailMessage


def is_configured():
    return bool(os.environ.get("SMTP_USERNAME") and os.environ.get("SMTP_PASSWORD"))


def send_email(to_address, subject, body):
    """Best-effort email send. Returns True on success, False otherwise (never raises)."""
    if not to_address or not is_configured():
        return False

    server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")
    from_name = os.environ.get("SMTP_FROM_NAME", "CollegeOneStop")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{username}>"
    msg["To"] = to_address
    msg.set_content(body)

    try:
        with smtplib.SMTP(server, port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
        return True
    except Exception:
        # Don't let a flaky mail server break page loads — email is a best-effort extra.
        return False
