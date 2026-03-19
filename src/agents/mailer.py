"""
Mailer agent — sends the approved white paper PDF via Gmail SMTP.

Closes the delivery loop: the white paper reaches the recipient's inbox
without any manual steps after approval.

Exports:
    run_mailer(ctx, config) -> WorkflowContext
"""
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def run_mailer(ctx, config):
    """Send the approved white paper PDF as an email attachment via Gmail SMTP.

    Args:
        ctx:    WorkflowContext with published_pdf_path and topic set.
        config: Config with gmail_address, recipient_email, and gmail_app_password.

    Returns:
        ctx unchanged (side-effect only).

    Raises:
        EnvironmentError:  gmail_app_password is empty.
        FileNotFoundError: published_pdf_path does not exist on disk.
    """
    # --- Guard clauses (checked before any I/O) ---
    if not config.gmail_app_password:
        raise EnvironmentError(
            "GMAIL_APP_PASSWORD is not set. "
            "Generate a Gmail app password at "
            "myaccount.google.com -> Security -> App passwords "
            "and export it as GMAIL_APP_PASSWORD."
        )

    if not os.path.exists(ctx.published_pdf_path):
        raise FileNotFoundError(f"PDF not found: {ctx.published_pdf_path}")

    # --- Build MIME email ---
    review_feedback = getattr(ctx, "review_feedback", "")

    body_text = (
        f"Please find attached the approved white paper on '{ctx.topic}'.\n\n"
        f"Review notes: {review_feedback}"
    )

    msg = MIMEMultipart()
    msg["From"] = config.gmail_address
    msg["To"] = config.recipient_email
    msg["Subject"] = f"White Paper: {ctx.topic}"

    msg.attach(MIMEText(body_text, "plain"))

    with open(ctx.published_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    attachment = MIMEApplication(pdf_bytes, Name="whitepaper.pdf")
    attachment["Content-Disposition"] = 'attachment; filename="whitepaper.pdf"'
    msg.attach(attachment)

    # --- Send via Gmail SMTP with STARTTLS ---
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(config.gmail_address, config.gmail_app_password)
            server.send_message(msg)
        print(
            f"[Mailer] Email sent to {config.recipient_email} -- '{ctx.topic}'"
        )
    except Exception as e:
        print(f"[Mailer] ERROR: {e}")
        raise

    return ctx
