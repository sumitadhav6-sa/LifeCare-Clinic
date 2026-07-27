"""
LifeCare Clinic - Main Application Factory
==========================================
Flask application using Application Factory pattern for scalability.
Supports SQLite (dev) and MySQL (production) via SQLAlchemy.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()


def create_app():
    """Application Factory Function"""
    app = Flask(__name__)

    # ─── Configuration ───────────────────────────────────────────
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///bajrang_clinic.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_TIMEOUT'] = 10

    # Session Configuration
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

    # ─── Initialize Extensions ───────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Login Manager Configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'warning'

    # ─── Register Blueprints ─────────────────────────────────────
    from routes.public import public_bp
    from routes.auth import auth_bp
    from routes.patient import patient_bp
    from routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ─── Create Database Tables ──────────────────────────────────
    with app.app_context():
        from models.user import User
        from models.doctor import Doctor
        from models.appointment import Appointment
        from models.otp import OTP
        db.create_all()
        _seed_admin(app)

    return app


def _seed_admin(app):
    """Create default admin account if not exists"""
    from models.user import User
    from werkzeug.security import generate_password_hash

    admin_email = os.getenv('ADMIN_EMAIL', 'admin@lifecareclinic.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin@123456')

    existing = User.query.filter_by(email=admin_email).first()
    if not existing:
        admin = User(
            name='Admin',
            email=admin_email,
            password=generate_password_hash(admin_password),
            role='admin',
            is_verified=True,
            phone='9999999999'
        )
        db.session.add(admin)
        db.session.commit()
        print(f"[✓] Admin created: {admin_email}")


# ─── User Loader for Flask-Login ─────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))
