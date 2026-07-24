"""
Public Routes
=============
Home, About, Services, Doctors, Contact pages.
No authentication required.
"""

from flask import Blueprint, render_template
from models.doctor import Doctor

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    """Home page with stats and featured doctors"""
    doctors = Doctor.query.filter_by(is_active=True).limit(4).all()
    return render_template('public/index.html', doctors=doctors)


@public_bp.route('/about')
def about():
    return render_template('public/about.html')


@public_bp.route('/services')
def services():
    return render_template('public/services.html')


@public_bp.route('/doctors')
def doctors():
    """All active doctors listing"""
    all_doctors = Doctor.query.filter_by(is_active=True).all()
    return render_template('public/doctors.html', doctors=all_doctors)


@public_bp.route('/contact')
def contact():
    return render_template('public/contact.html')
