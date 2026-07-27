"""
Email Utility
=============
Handles OTP generation and email sending via Flask-Mail (Gmail SMTP).
"""

import random
import string
from flask import current_app
from flask_mail import Message
from __init__ import mail, db
from models.otp import OTP


def generate_otp(length=6):
    """Generate a random numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(email, otp_code, patient_name='Patient'):
    """
    Send OTP verification email.
    Returns (success: bool, message: str)
    """
    try:
        subject = "LifeCare Clinic - Email Verification OTP"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family:Arial,sans-serif;">
            <h2>🏥 LifeCare Clinic</h2>
            <p>Hello <strong>{patient_name}</strong>,</p>
            <p>Your OTP for email verification is:</p>

            <h1 style="color:#ff6600;">{otp_code}</h1>

            <p>This OTP is valid for <strong>10 minutes</strong>.</p>
            <p>Please do not share this OTP with anyone.</p>

            <br>
            <p>Thank you,<br>LifeCare Clinic Team</p>
        </body>
        </html>
        """

        msg = Message(
            subject=subject,
            recipients=[email]
        )

        msg.html = html_body

       print("========== EMAIL DEBUG ==========")
       print("MAIL_USERNAME:", ...)
       print("Sending email...")

        mail.send(msg)

        print("Email sent successfully")
        print("================================")

        return True, "OTP sent successfully"

    except Exception as e:
        print("EMAIL ERROR:", str(e))
        current_app.logger.error(f"[Email Error] {str(e)}")
        return False, str(e)


def create_and_send_otp(email, name='Patient'):
    """
    Generate OTP, save in database, send email.
    """

    OTP.query.filter_by(email=email, is_used=False).delete()
    db.session.commit()

    otp_code = generate_otp()

    otp = OTP(
        email=email,
        otp_code=otp_code
    )

    db.session.add(otp)
    db.session.commit()

    success, message = send_otp_email(email, otp_code, name)

    if not success:
        current_app.logger.warning(f"OTP: {otp_code}")
        return False, message, otp_code

    return True, message, otp_code


def verify_otp(email, otp_code):
    """
    Verify OTP.
    """

    otp = OTP.query.filter_by(
        email=email,
        otp_code=otp_code,
        is_used=False
    ).order_by(OTP.created_at.desc()).first()

    if not otp:
        return False, "Invalid OTP"

    if otp.is_expired():
        return False, "OTP expired"

    otp.is_used = True
    db.session.commit()

    return True, "OTP verified successfully"