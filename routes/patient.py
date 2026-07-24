"""
Patient Routes
==============
Dashboard, Book Appointment, My Appointments, Profile.
All routes require authenticated patient role.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from __init__ import db
from models.doctor import Doctor
from models.appointment import Appointment
from models.user import User
from utils.decorators import patient_required
from werkzeug.security import generate_password_hash, check_password_hash

patient_bp = Blueprint('patient', __name__)


# ─── Dashboard ───────────────────────────────────────────────────
@patient_bp.route('/dashboard')
@login_required
@patient_required
def dashboard():
    today = date.today()
    upcoming = Appointment.query.filter_by(
        patient_id=current_user.id
    ).filter(
        Appointment.date >= today,
        Appointment.status != 'cancelled'
    ).order_by(Appointment.date, Appointment.time_slot).limit(3).all()

    total_appointments = Appointment.query.filter_by(patient_id=current_user.id).count()
    approved = Appointment.query.filter_by(patient_id=current_user.id, status='approved').count()
    pending  = Appointment.query.filter_by(patient_id=current_user.id, status='pending').count()

    return render_template('patient/dashboard.html',
        upcoming=upcoming,
        total=total_appointments,
        approved=approved,
        pending=pending,
        today=today
    )


# ─── Book Appointment ────────────────────────────────────────────
@patient_bp.route('/book-appointment', methods=['GET', 'POST'])
@login_required
@patient_required
def book_appointment():
    doctors = Doctor.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appt_date = request.form.get('date')
        time_slot = request.form.get('time_slot')
        symptoms  = request.form.get('symptoms', '').strip()

        if not all([doctor_id, appt_date, time_slot]):
            flash('Please fill all required fields.', 'danger')
            return render_template('patient/book_appointment.html', doctors=doctors)

        # Parse and validate date
        try:
            appt_date_obj = datetime.strptime(appt_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('patient/book_appointment.html', doctors=doctors)

        if appt_date_obj < date.today():
            flash('Appointment date cannot be in the past.', 'danger')
            return render_template('patient/book_appointment.html', doctors=doctors)

        # Check for duplicate appointment
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=appt_date_obj,
            time_slot=time_slot
        ).filter(Appointment.status != 'cancelled').first()

        if existing:
            flash('This slot is already booked. Please choose another time.', 'warning')
            return render_template('patient/book_appointment.html', doctors=doctors)

        # Create appointment
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=int(doctor_id),
            date=appt_date_obj,
            time_slot=time_slot,
            symptoms=symptoms,
            status='pending'
        )
        db.session.add(appointment)
        db.session.commit()

        flash('🎉 Appointment booked successfully! Awaiting confirmation.', 'success')
        return redirect(url_for('patient.my_appointments'))

    return render_template('patient/book_appointment.html', doctors=doctors)


# ─── AJAX: Get Doctor Slots ───────────────────────────────────────
@patient_bp.route('/get-slots/<int:doctor_id>')
@login_required
def get_slots(doctor_id):
    """Return available time slots for a doctor (AJAX)"""
    doctor = Doctor.query.get_or_404(doctor_id)
    slots = doctor.get_slots_list()
    days  = doctor.get_days_list()
    return jsonify({'slots': slots, 'days': days, 'fee': doctor.fee})


# ─── My Appointments ─────────────────────────────────────────────
@patient_bp.route('/my-appointments')
@login_required
@patient_required
def my_appointments():
    filter_status = request.args.get('status', 'all')
    query = Appointment.query.filter_by(patient_id=current_user.id)

    if filter_status != 'all':
        query = query.filter_by(status=filter_status)

    appointments = query.order_by(Appointment.date.desc()).all()
    return render_template('patient/my_appointments.html',
        appointments=appointments,
        filter_status=filter_status
    )


# ─── Cancel Appointment ──────────────────────────────────────────
@patient_bp.route('/cancel-appointment/<int:appt_id>', methods=['POST'])
@login_required
@patient_required
def cancel_appointment(appt_id):
    appt = Appointment.query.filter_by(
        id=appt_id,
        patient_id=current_user.id
    ).first_or_404()

    if appt.status == 'approved':
        flash('Approved appointments cannot be cancelled. Please contact the clinic.', 'warning')
        return redirect(url_for('patient.my_appointments'))

    appt.status = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled successfully.', 'success')
    return redirect(url_for('patient.my_appointments'))


# ─── Profile ─────────────────────────────────────────────────────
@patient_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@patient_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            current_user.name    = request.form.get('name', current_user.name).strip()
            current_user.phone   = request.form.get('phone', current_user.phone).strip()
            current_user.gender  = request.form.get('gender', current_user.gender)
            current_user.address = request.form.get('address', '').strip()
            current_user.blood_group = request.form.get('blood_group', '')

            dob_str = request.form.get('dob', '')
            if dob_str:
                try:
                    current_user.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                except ValueError:
                    pass

            db.session.commit()
            flash('Profile updated successfully!', 'success')

        elif action == 'change_password':
            old_pw  = request.form.get('old_password', '')
            new_pw  = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')

            if not check_password_hash(current_user.password, old_pw):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('patient.profile'))

            if len(new_pw) < 8:
                flash('New password must be at least 8 characters.', 'danger')
                return redirect(url_for('patient.profile'))

            if new_pw != confirm:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('patient.profile'))

            current_user.password = generate_password_hash(new_pw)
            db.session.commit()
            flash('Password changed successfully!', 'success')

        return redirect(url_for('patient.profile'))

    return render_template('patient/profile.html')
