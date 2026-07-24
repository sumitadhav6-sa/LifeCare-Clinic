"""
OTP Model
=========
Stores one-time passwords for email verification.
OTPs expire after 10 minutes and are single-use.
"""

from datetime import datetime, timedelta
from __init__ import db


class OTP(db.Model):
    __tablename__ = 'otps'

    id          = db.Column(db.Integer, primary_key=True)
    email       = db.Column(db.String(150), nullable=False)
    otp_code    = db.Column(db.String(6), nullable=False)
    is_used     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at  = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))

    def is_expired(self):
        """Check if OTP has expired (10 min TTL)"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check OTP is not used and not expired"""
        return not self.is_used and not self.is_expired()

    def __repr__(self):
        return f'<OTP {self.email} - {self.otp_code}>'
