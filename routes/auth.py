"""
Auth Routes
===========
Registration, Login, OTP Verification, Logout.
Supports both patient and admin authentication.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db
from models.user import User
from utils.email import create_and_send_otp, verify_otp
import re

auth_bp = Blueprint('auth', __name__)


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

def is_valid_phone(phone):
    return re.match(r'^[6-9]\d{9}$', phone)


# ─── Register ────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('patient.dashboard'))

    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')

        # Validation
        if not all([name, email, phone, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('public/register.html')

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('public/register.html')

        if not is_valid_phone(phone):
            flash('Enter a valid 10-digit Indian mobile number.', 'danger')
            return render_template('public/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('public/register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('public/register.html')

        # Check existing user
        existing = User.query.filter_by(email=email).first()
        if existing:
            if existing.is_verified:
                flash('Email already registered. Please login.', 'warning')
                return redirect(url_for('auth.login'))
            else:
                # Resend OTP to unverified account
                success, msg, _ = create_and_send_otp(email, existing.name)
                session['otp_email'] = email
                flash('OTP resent to your email. Please verify.', 'info')
                return redirect(url_for('auth.verify_otp_page'))

        # Create unverified user
        hashed_pw = generate_password_hash(password)
        new_user = User(
            name=name, email=email, phone=phone,
            password=hashed_pw, role='patient', is_verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        # Send OTP
        success, msg, otp_dev = create_and_send_otp(email, name)
        session['otp_email'] = email

        if success:
            flash(f'OTP sent to {email}. Please verify your email.', 'success')
        else:
            flash(f'Account created! OTP: {otp_dev} (email service unavailable – dev mode)', 'info')

        return redirect(url_for('auth.verify_otp_page'))

    return render_template('public/register.html')


# ─── OTP Verification ────────────────────────────────────────────
@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    email = session.get('otp_email')
    if not email:
        flash('Session expired. Please register again.', 'warning')
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        otp_code = request.form.get('otp', '').strip()

        valid, message = verify_otp(email, otp_code)
        if not valid:
            flash(message, 'danger')
            return render_template('public/verify_otp.html', email=email)

        # Mark user as verified
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_verified = True
            db.session.commit()
            session.pop('otp_email', None)
            login_user(user)
            flash('🎉 Email verified! Welcome to LifeCare Clinic.', 'success')
            return redirect(url_for('patient.dashboard'))

        flash('User not found. Please register again.', 'danger')
        return redirect(url_for('auth.register'))

    return render_template('public/verify_otp.html', email=email)


# ─── Resend OTP ──────────────────────────────────────────────────
@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    email = session.get('otp_email')
    if not email:
        flash('Session expired. Please register again.', 'warning')
        return redirect(url_for('auth.register'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.register'))

    success, msg, otp_dev = create_and_send_otp(email, user.name)
    if success:
        flash('New OTP sent to your email.', 'success')
    else:
        flash(f'OTP resent (dev): {otp_dev}', 'info')

    return redirect(url_for('auth.verify_otp_page'))


# ─── Login ───────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('patient.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('public/login.html')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password.', 'danger')
            return render_template('public/login.html')

        if not user.is_verified:
            session['otp_email'] = email
            create_and_send_otp(email, user.name)
            flash('Please verify your email first. OTP sent.', 'warning')
            return redirect(url_for('auth.verify_otp_page'))

        login_user(user, remember=True)

        if user.role == 'admin':
            flash(f'Welcome back, Admin!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('patient.dashboard'))

    return render_template('public/login.html')


# ─── Logout ──────────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    name = current_user.name
    logout_user()
    flash(f'Goodbye, {name}! You have been logged out.', 'info')
    return redirect(url_for('public.index'))
