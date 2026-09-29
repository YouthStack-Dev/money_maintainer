import smtplib
from email.message import EmailMessage
from app.core.config import settings


def send_email(to: str, subject: str, body: str) -> None:
    if not all((settings.smtp_host, settings.smtp_username, settings.smtp_password, settings.smtp_from_email)):
        raise RuntimeError("SMTP email service is not configured")
    msg = EmailMessage()
    msg["From"] = settings.smtp_from_email
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        if settings.smtp_use_tls:
            server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)
