"""
E.V.E. Email Verification Router — backend/api/routers/verify_email.py

Flow:
  1. POST /api/send-verification  { email }  -> sends OTP (called after form fill, before DB insert)
  2. POST /api/verify-email       { email, otp }  -> returns verified=True, then frontend calls register
"""
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os
import secrets
import string
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

router = APIRouter(prefix="/api", tags=["verify-email"])

# In-memory store: email -> (otp, expires_at)
_verification_store: Dict[str, Tuple[str, datetime]] = {}

OTP_TTL_MINUTES = 10


def _generate_otp() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(6))


def _send_verification_email(to_email: str, otp: str) -> None:
    otp_display = " ".join(otp)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f6f6f6;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f6f6f6;padding:48px 16px;">
  <tr><td align="center">
    <table width="440" cellpadding="0" cellspacing="0"
           style="background:#ffffff;border-radius:12px;overflow:hidden;
                  border:1px solid #eee;max-width:100%;">

      <tr><td height="3" style="background:#FF14A5;font-size:0;line-height:0;">&nbsp;</td></tr>

      <tr><td style="padding:32px 32px 24px;">
        <div style="font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;
                    color:#FF14A5;margin-bottom:20px;font-family:-apple-system,sans-serif;">E.V.E.</div>
        <div style="font-size:18px;font-weight:600;color:#111;margin-bottom:6px;
                    font-family:-apple-system,sans-serif;">Verify your email</div>
        <div style="font-size:12px;color:#aaa;font-family:-apple-system,sans-serif;">
          You&rsquo;re almost there! Enter this code to complete your account setup.
        </div>
      </td></tr>

      <tr><td style="padding:0 32px;"><div style="height:1px;background:#f0f0f0;"></div></td></tr>

      <tr><td style="padding:36px 32px;text-align:center;">
        <div style="font-size:40px;font-weight:300;letter-spacing:5px;color:#111;
                    font-family:'Courier New',monospace;margin-bottom:16px;">
          {otp_display}
        </div>
        <div style="font-size:11px;color:#bbb;font-family:-apple-system,sans-serif;">
          Expires in
          <span style="color:#FF14A5;font-weight:500;">{OTP_TTL_MINUTES} minutes</span>
        </div>
      </td></tr>

      <tr><td style="padding:0 32px;"><div style="height:1px;background:#f0f0f0;"></div></td></tr>

      <tr><td style="padding:20px 32px 28px;">
        <div style="font-size:11px;color:#ccc;line-height:1.6;font-family:-apple-system,sans-serif;">
          If you didn&rsquo;t create an E.V.E. account, you can safely ignore this email.
        </div>
      </td></tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "[E.V.E.] Verify your email address"
    msg["From"]    = SMTP_USERNAME
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.ehlo(); s.starttls(); s.ehlo()
        s.login(SMTP_USERNAME, SMTP_PASSWORD)
        s.sendmail(SMTP_USERNAME, to_email, msg.as_string())


# ── Schemas ────────────────────────────────────────────────────────────────────

class SendVerificationRequest(BaseModel):
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("/send-verification")
async def send_verification(data: SendVerificationRequest):
    """Step 1. Send OTP to the given email before account creation."""
    from core.database import get_connection
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute("SELECT user_id FROM users WHERE email = %s", (data.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        cur.close()
        conn.close()

    otp = _generate_otp()
    _verification_store[data.email] = (
        otp,
        datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES),
    )

    try:
        _send_verification_email(data.email, otp)
    except Exception as e:
        print(f"Verification email failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {"message": "Verification code sent to your email."}


@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest):
    """Step 2. Validate OTP — returns verified=True so frontend can proceed with register."""
    entry = _verification_store.get(data.email)
    if not entry:
        raise HTTPException(status_code=400, detail="No verification code requested for this email")

    otp, expires_at = entry
    if datetime.now(timezone.utc) > expires_at:
        _verification_store.pop(data.email, None)
        raise HTTPException(status_code=400, detail="Verification code has expired")

    if not secrets.compare_digest(data.otp.strip(), otp):
        raise HTTPException(status_code=400, detail="Invalid verification code")

    _verification_store.pop(data.email, None)  # consume — one-time use
    return {"verified": True}