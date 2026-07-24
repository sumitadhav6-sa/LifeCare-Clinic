"""
Doctor Model
============
Stores doctor profiles with specializations, schedules and availability.
"""

from datetime import datetime
from __init__ import db


class Doctor(db.Model):
    __tablename__ = 'doctors'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(120), nullable=False)
    email           = db.Column(db.String(150), unique=True, nullable=True)
    phone           = db.Column(db.String(15), nullable=True)
    specialization  = db.Column(db.String(100), nullable=False)
    qualification   = db.Column(db.String(200), nullable=True)
    experience      = db.Column(db.Integer, default=0)             # Years of experience
    bio             = db.Column(db.Text, nullable=True)
    photo           = db.Column(db.String(300), nullable=True)     # URL or filename
    fee             = db.Column(db.Float, default=500.0)
    available_days  = db.Column(db.String(100), default='Mon,Tue,Wed,Thu,Fri')
    available_slots = db.Column(db.String(300), default='09:00,10:00,11:00,14:00,15:00,16:00')
    rating          = db.Column(db.Float, default=4.5)
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointments    = db.relationship('Appointment', backref='doctor', lazy=True)

    def __repr__(self):
        return f'<Doctor {self.name} - {self.specialization}>'

    def get_slots_list(self):
        """Return available time slots as a list"""
        return [s.strip() for s in self.available_slots.split(',') if s.strip()]

    def get_days_list(self):
        """Return available days as a list"""
        return [d.strip() for d in self.available_days.split(',') if d.strip()]

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'specialization': self.specialization,
            'qualification': self.qualification,
            'experience': self.experience,
            'bio': self.bio,
            'fee': self.fee,
            'available_days': self.available_days,
            'available_slots': self.available_slots,
            'rating': self.rating,
            'is_active': self.is_active
        }
