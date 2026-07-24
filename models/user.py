"""
User Model
==========
Handles both patients and admin accounts.
Role-based: 'patient' | 'admin'
"""

from datetime import datetime
from flask_login import UserMixin
from __init__ import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    phone         = db.Column(db.String(15), nullable=True)
    password      = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), default='patient')       # 'patient' | 'admin'
    is_verified   = db.Column(db.Boolean, default=False)
    gender        = db.Column(db.String(10), nullable=True)
    dob           = db.Column(db.Date, nullable=True)
    address       = db.Column(db.Text, nullable=True)
    blood_group   = db.Column(db.String(5), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    appointments  = db.relationship('Appointment', backref='patient', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_verified': self.is_verified,
            'gender': self.gender,
            'blood_group': self.blood_group,
            'created_at': self.created_at.strftime('%d %b %Y') if self.created_at else ''
        }
