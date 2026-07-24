"""
Decorators & Helpers
====================
Custom decorators for role-based access control.
"""

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    """Decorator: restrict route to admin users only"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('patient.dashboard'))
        return f(*args, **kwargs)
    return decorated


def patient_required(f):
    """Decorator: restrict route to patient users only"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role != 'patient':
            flash('Access denied.', 'danger')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated
