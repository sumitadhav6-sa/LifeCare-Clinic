"""
Admin Routes
============
Dashboard, Manage Patients, Doctors, Appointments.
All routes require admin role.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from datetime import date, datetime
from __init__ import db
from models.user import User
from models.doctor import Doctor
from models.appointment import Appointment
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


# ─── Dashboard ───────────────────────────────────────────────────
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    today = date.today()
    total_patients     = User.query.filter_by(role='patient', is_verified=True).count()
    total_doctors      = Doctor.query.filter_by(is_active=True).count()
    total_appointments = Appointment.query.count()
    today_appointments = Appointment.query.filter_by(date=today).count()
    pending_approvals  = Appointment.query.filter_by(status='pending').count()
    approved_today     = Appointment.query.filter_by(date=today, status='approved').count()

    recent_appointments = (
        Appointment.query
        .order_by(Appointment.created_at.desc())
        .limit(8).all()
    )

    return render_template('admin/dashboard.html',
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        today_appointments=today_appointments,
        pending_approvals=pending_approvals,
        approved_today=approved_today,
        recent_appointments=recent_appointments,
        today=today
    )


# ─── Manage Patients ─────────────────────────────────────────────
@admin_bp.route('/patients')
@login_required
@admin_required
def patients():
    search = request.args.get('search', '').strip()
    query  = User.query.filter_by(role='patient')

    if search:
        query = query.filter(
            (User.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.phone.ilike(f'%{search}%'))
        )

    all_patients = query.order_by(User.created_at.desc()).all()
    return render_template('admin/patients.html', patients=all_patients, search=search)


@admin_bp.route('/patients/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_patient(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete admin account.', 'danger')
        return redirect(url_for('admin.patients'))

    # Delete related appointments first
    Appointment.query.filter_by(patient_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'Patient {user.name} deleted successfully.', 'success')
    return redirect(url_for('admin.patients'))


# ─── Manage Doctors ──────────────────────────────────────────────
@admin_bp.route('/doctors')
@login_required
@admin_required
def doctors():
    all_doctors = Doctor.query.order_by(Doctor.created_at.desc()).all()
    return render_template('admin/doctors.html', doctors=all_doctors)


@admin_bp.route('/doctors/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_doctor():
    if request.method == 'POST':
        name            = request.form.get('name', '').strip()
        email           = request.form.get('email', '').strip()
        phone           = request.form.get('phone', '').strip()
        specialization  = request.form.get('specialization', '').strip()
        qualification   = request.form.get('qualification', '').strip()
        experience      = request.form.get('experience', 0)
        bio             = request.form.get('bio', '').strip()
        fee             = request.form.get('fee', 500)
        available_days  = ','.join(request.form.getlist('available_days'))
        available_slots = ','.join(request.form.getlist('available_slots'))
        rating          = request.form.get('rating', 4.5)
        photo           = request.form.get('photo', '').strip()

        if not name or not specialization:
            flash('Name and specialization are required.', 'danger')
            return render_template('admin/doctor_form.html', doctor=None, action='Add')

        if email and Doctor.query.filter_by(email=email).first():
            flash('Doctor with this email already exists.', 'danger')
            return render_template('admin/doctor_form.html', doctor=None, action='Add')

        doctor = Doctor(
            name=name, email=email or None, phone=phone,
            specialization=specialization, qualification=qualification,
            experience=int(experience), bio=bio, fee=float(fee),
            available_days=available_days or 'Mon,Tue,Wed,Thu,Fri',
            available_slots=available_slots or '09:00,10:00,11:00,14:00,15:00,16:00',
            rating=float(rating),
            photo=photo or None
        )
        db.session.add(doctor)
        db.session.commit()
        flash(f'Dr. {name} added successfully!', 'success')
        return redirect(url_for('admin.doctors'))

    return render_template('admin/doctor_form.html', doctor=None, action='Add')


@admin_bp.route('/doctors/edit/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == 'POST':
        doctor.name           = request.form.get('name', doctor.name).strip()
        doctor.email          = request.form.get('email', '').strip() or None
        doctor.phone          = request.form.get('phone', '').strip()
        doctor.specialization = request.form.get('specialization', '').strip()
        doctor.qualification  = request.form.get('qualification', '').strip()
        doctor.experience     = int(request.form.get('experience', doctor.experience))
        doctor.bio            = request.form.get('bio', '').strip()
        doctor.fee            = float(request.form.get('fee', doctor.fee))
        doctor.available_days = ','.join(request.form.getlist('available_days'))
        doctor.available_slots = ','.join(request.form.getlist('available_slots'))
        doctor.rating         = float(request.form.get('rating', doctor.rating))
        doctor.is_active      = request.form.get('is_active') == 'on'
        photo = request.form.get('photo', '').strip()
        if photo:
            doctor.photo = photo

        db.session.commit()
        flash(f'Dr. {doctor.name} updated successfully!', 'success')
        return redirect(url_for('admin.doctors'))

    return render_template('admin/doctor_form.html', doctor=doctor, action='Edit')


@admin_bp.route('/doctors/delete/<int:doctor_id>', methods=['POST'])
@login_required
@admin_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.is_active = False   # Soft delete
    db.session.commit()
    flash(f'Dr. {doctor.name} deactivated successfully.', 'success')
    return redirect(url_for('admin.doctors'))


# ─── Manage Appointments ─────────────────────────────────────────
@admin_bp.route('/appointments')
@login_required
@admin_required
def appointments():
    status_filter = request.args.get('status', 'all')
    date_filter   = request.args.get('date', '')

    query = Appointment.query

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(date=filter_date)
        except ValueError:
            pass

    all_appointments = query.order_by(Appointment.date.desc(), Appointment.time_slot).all()
    return render_template('admin/appointments.html',
        appointments=all_appointments,
        status_filter=status_filter,
        date_filter=date_filter
    )


@admin_bp.route('/appointments/approve/<int:appt_id>', methods=['POST'])
@login_required
@admin_required
def approve_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    appt.status = 'approved'
    db.session.commit()
    flash(f'Appointment #{appt_id} approved!', 'success')
    return redirect(url_for('admin.appointments'))


@admin_bp.route('/appointments/cancel/<int:appt_id>', methods=['POST'])
@login_required
@admin_required
def cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    notes = request.form.get('notes', '')
    appt.status = 'cancelled'
    if notes:
        appt.notes = notes
    db.session.commit()
    flash(f'Appointment #{appt_id} cancelled.', 'info')
    return redirect(url_for('admin.appointments'))


@admin_bp.route('/appointments/update-status/<int:appt_id>', methods=['POST'])
@login_required
@admin_required
def update_appointment_status(appt_id):
    """AJAX endpoint for quick status update"""
    appt = Appointment.query.get_or_404(appt_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'approved', 'cancelled']:
        appt.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'status': new_status})
    return jsonify({'success': False}), 400
