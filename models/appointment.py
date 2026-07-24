"""
Appointment Model
=================
Manages patient-doctor appointments with status tracking.
Status flow: pending → approved / cancelled
"""

from datetime import datetime
from __init__ import db


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id          = db.Column(db.Integer, primary_key=True)
    patient_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id   = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date        = db.Column(db.Date, nullable=False)
    time_slot   = db.Column(db.String(20), nullable=False)
    status      = db.Column(db.String(20), default='pending')   # pending | approved | cancelled
    symptoms    = db.Column(db.Text, nullable=True)
    notes       = db.Column(db.Text, nullable=True)             # Admin/doctor notes
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment P:{self.patient_id} D:{self.doctor_id} {self.date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'date': self.date.strftime('%d %b %Y') if self.date else '',
            'time_slot': self.time_slot,
            'status': self.status,
            'symptoms': self.symptoms,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%d %b %Y %H:%M') if self.created_at else ''
        }
