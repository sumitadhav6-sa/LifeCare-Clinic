"""
Seed Sample Doctors
====================
Run once to populate the database with sample doctors.
Usage: python seed_doctors.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app, db
from models.doctor import Doctor

app = create_app()

sample_doctors = [
    {
        'name': 'Arun Sharma', 'specialization': 'Cardiologist',
        'qualification': 'MBBS, MD (Cardiology), DM', 'experience': 18,
        'email': 'dr.sharma@lifecareclinic.com', 'phone': '9811001001',
        'bio': 'Experienced cardiologist specializing in interventional cardiology and heart failure management.',
        'fee': 800, 'rating': 4.8,
        'available_days': 'Mon,Tue,Wed,Thu,Fri',
        'available_slots': '09:00,10:00,11:00,14:00,15:00,16:00',
    },
    {
        'name': 'Priya Verma', 'specialization': 'Pediatrician',
        'qualification': 'MBBS, MD (Pediatrics)', 'experience': 12,
        'email': 'dr.priya@lifecareclinic.com', 'phone': '9811002002',
        'bio': 'Compassionate pediatrician with expertise in neonatal care and child development.',
        'fee': 600, 'rating': 4.9,
        'available_days': 'Mon,Tue,Wed,Thu,Fri,Sat',
        'available_slots': '09:00,10:00,11:00,14:00,15:00',
    },
    {
        'name': 'Rajesh Kapoor', 'specialization': 'Orthopedic Surgeon',
        'qualification': 'MBBS, MS (Orthopedics)', 'experience': 15,
        'email': 'dr.kapoor@lifecareclinic.com', 'phone': '9811003003',
        'bio': 'Specialist in joint replacement surgeries and sports injury rehabilitation.',
        'fee': 900, 'rating': 4.7,
        'available_days': 'Mon,Wed,Fri,Sat',
        'available_slots': '10:00,11:00,14:00,15:00,16:00',
    },
    {
        'name': 'Sunita Patel', 'specialization': 'Neurologist',
        'qualification': 'MBBS, MD (Neurology), DM', 'experience': 20,
        'email': 'dr.patel@lifecareclinic.com', 'phone': '9811004004',
        'bio': 'Expert neurologist treating epilepsy, stroke, Parkinson\'s and other neurological disorders.',
        'fee': 1000, 'rating': 4.9,
        'available_days': 'Tue,Thu,Sat',
        'available_slots': '09:00,10:00,11:00,14:00',
    },
    {
        'name': 'Vikram Singh', 'specialization': 'General Physician',
        'qualification': 'MBBS, MD (Medicine)', 'experience': 10,
        'email': 'dr.vikram@lifecareclinic.com', 'phone': '9811005005',
        'bio': 'General practitioner handling primary care, diabetes management and preventive medicine.',
        'fee': 400, 'rating': 4.6,
        'available_days': 'Mon,Tue,Wed,Thu,Fri,Sat',
        'available_slots': '09:00,09:30,10:00,10:30,11:00,11:30,14:00,14:30,15:00,15:30,16:00',
    },
    {
        'name': 'Meena Joshi', 'specialization': 'Gynecologist',
        'qualification': 'MBBS, MS (Obstetrics & Gynecology)', 'experience': 16,
        'email': 'dr.meena@lifecareclinic.com', 'phone': '9811006006',
        'bio': 'Specialist in women\'s health, high-risk pregnancies and minimally invasive surgeries.',
        'fee': 700, 'rating': 4.8,
        'available_days': 'Mon,Tue,Wed,Thu,Fri',
        'available_slots': '09:00,10:00,11:00,14:00,15:00,16:00',
    },
]


def seed():
    with app.app_context():
        count = 0
        for data in sample_doctors:
            existing = Doctor.query.filter_by(email=data['email']).first()
            if not existing:
                doc = Doctor(**data)
                db.session.add(doc)
                count += 1
                print(f"[+] Added: Dr. {data['name']} - {data['specialization']}")
            else:
                print(f"[=] Already exists: Dr. {data['name']}")
        db.session.commit()
        print(f"\n✅ Seeded {count} new doctors. Total: {Doctor.query.count()}")


if __name__ == '__main__':
    seed()
