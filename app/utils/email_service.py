"""
Asynchronous Email Service for sending password reset emails.
Utilizes aiosmtplib (if installed) or asyncio.to_thread with smtplib, with dev-mode logger fallback.
"""

import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger("email_service")

try:
    import aiosmtplib
    HAS_AIOSMTPLIB = True
except ImportError:
    HAS_AIOSMTPLIB = False


class EmailService:
    """
    Asynchronous email service.
    """

    async def send_password_reset_email(self, email_to: str, token: str) -> None:
        """
        Sends a password reset link to the user's email address asynchronously.
        If SMTP credentials are not configured, logs the reset URL to console.
        """
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        logger.info("==================================================")
        logger.info(f"PASSWORD RESET REQUESTED FOR: {email_to}")
        logger.info(f"RESET LINK: {reset_link}")
        logger.info("==================================================")

        # Print to stdout for local development visibility
        print(f"\n[DEV EMAIL SERVICE] Password Reset Link for {email_to}:\n{reset_link}\n", flush=True)

        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.info("SMTP credentials not set; skipping live email dispatch.")
            return

        message = EmailMessage()
        message["From"] = settings.SMTP_FROM
        message["To"] = email_to
        message["Subject"] = "Password Reset Request - Vendor Reliability Intelligence Platform"

        body = (
            f"Hello,\n\n"
            f"You have requested to reset your password for the Vendor Reliability Intelligence Platform.\n\n"
            f"Please click the link below to set a new password:\n"
            f"{reset_link}\n\n"
            f"This link will expire in {settings.RESET_TOKEN_EXPIRE_HOURS} hour(s).\n"
            f"If you did not request a password reset, please ignore this email.\n\n"
            f"Regards,\n"
            f"Vendor Reliability Intelligence Team"
        )

        message.set_content(body)

        try:
            if HAS_AIOSMTPLIB:
                await aiosmtplib.send(
                    message,
                    hostname=settings.SMTP_HOST,
                    port=settings.SMTP_PORT,
                    username=settings.SMTP_USER,
                    password=settings.SMTP_PASSWORD,
                    start_tls=True,
                )
            else:
                def _sync_send():
                    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                        server.starttls()
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                        server.send_message(message)

                await asyncio.to_thread(_sync_send)

            logger.info(f"Password reset email successfully sent to {email_to}")
        except Exception as exc:
            logger.error(f"Failed to send email to {email_to}: {exc}")


email_service = EmailService()
