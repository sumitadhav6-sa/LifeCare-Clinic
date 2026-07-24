"""
Email Utility
=============
Handles OTP generation and email sending via Flask-Mail (Gmail SMTP).
Falls back gracefully if email config is missing (dev mode).
"""

import random
import string
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from __init__ import mail, db
from models.otp import OTP


def generate_otp(length=6):
    """Generate a cryptographically random numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(email, otp_code, patient_name='Patient'):
    """
    Send OTP verification email.
    Returns (success: bool, message: str)
    """
    try:
        subject = "🔐 LifeCare Clinic – Email Verification OTP"
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f4ff; margin: 0; padding: 20px; }}
            .container {{ max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #ff6f00 100%); padding: 30px; text-align: center; }}
            .header h1 {{ color: white; margin: 0; font-size: 24px; }}
            .header p {{ color: rgba(255,255,255,0.8); margin: 5px 0 0; }}
            .body {{ padding: 30px; }}
            .otp-box {{ background: linear-gradient(135deg, #1a237e, #283593); border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0; }}
            .otp-code {{ font-size: 42px; font-weight: 800; color: #ff6f00; letter-spacing: 8px; }}
            .info {{ color: #666; font-size: 14px; line-height: 1.6; }}
            .footer {{ background: #f5f5f5; padding: 15px; text-align: center; color: #999; font-size: 12px; }}
            .warning {{ background: #fff3e0; border-left: 4px solid #ff6f00; padding: 10px 15px; border-radius: 4px; margin: 15px 0; font-size: 13px; color: #e65100; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>🏥 LifeCare Clinic</h1>
              <p>Quality Healthcare at Your Fingertips</p>
            </div>
            <div class="body">
              <p style="font-size:18px; color:#1a237e;"><strong>Hello, {patient_name}! 👋</strong></p>
              <p class="info">Thank you for registering with <strong>LifeCare Clinic</strong>. Use the OTP below to verify your email address.</p>
              <div class="otp-box">
                <p style="color:rgba(255,255,255,0.7); margin:0 0 5px; font-size:13px;">YOUR VERIFICATION CODE</p>
                <div class="otp-code">{otp_code}</div>
              </div>
              <div class="warning">
                ⏰ This OTP is valid for <strong>10 minutes</strong> only. Do not share it with anyone.
              </div>
              <p class="info">If you did not register on LifeCare Clinic, please ignore this email.</p>
            </div>
            <div class="footer">
              © 2024 LifeCare Clinic | This is an automated email, please do not reply.
            </div>
          </div>
        </body>
        </html>
        """

        msg = Message(
            subject=subject,
            recipients=[email],
            html=html_body
        )
        mail.send(msg)
        return True, "OTP sent successfully"

    except Exception as e:
        current_app.logger.error(f"[Email Error] {str(e)}")
        return False, str(e)


def create_and_send_otp(email, name='Patient'):
    """
    Generate OTP, save to DB, send email.
    Returns (success: bool, message: str, otp_code: str|None)
    """
    # Invalidate any previous unused OTPs for this email
    OTP.query.filter_by(email=email, is_used=False).delete()
    db.session.commit()

    otp_code = generate_otp()
    new_otp = OTP(email=email, otp_code=otp_code)
    db.session.add(new_otp)
    db.session.commit()

    success, message = send_otp_email(email, otp_code, name)

    if not success:
        # In dev mode: log OTP to console
        current_app.logger.warning(f"[DEV] OTP for {email}: {otp_code}")
        return False, f"Email sending failed: {message}", otp_code  # Still return OTP for dev

    return True, "OTP sent to your email", otp_code


def verify_otp(email, otp_code):
    """
    Verify submitted OTP against DB.
    Returns (valid: bool, message: str)
    """
    otp = OTP.query.filter_by(
        email=email,
        otp_code=otp_code,
        is_used=False
    ).order_by(OTP.created_at.desc()).first()

    if not otp:
        return False, "Invalid OTP. Please try again."

    if otp.is_expired():
        return False, "OTP has expired. Please request a new one."

    # Mark as used
    otp.is_used = True
    db.session.commit()

    return True, "OTP verified successfully"
