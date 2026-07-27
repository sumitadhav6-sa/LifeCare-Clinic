"""
LifeCare Clinic - Main Application Factory
==========================================
Flask application using Application Factory pattern.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    # ================= Configuration =================

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-in-prod"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///bajrang_clinic.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ================= Brevo SMTP =================

    app.config["MAIL_SERVER"] = os.getenv(
        "MAIL_SERVER",
        "smtp-relay.brevo.com"
    )

    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))

    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False

    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
        "MAIL_DEFAULT_SENDER",
        "lifecareclinic0203@gmail.com"
    )

    app.config["MAIL_TIMEOUT"] = 30

    # ================= Session =================

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["PERMANENT_SESSION_LIFETIME"] = 3600

    # ================= Extensions =================

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please login to access this page."
    login_manager.login_message_category = "warning"

    # ================= Blueprints =================

    from routes.public import public_bp
    from routes.auth import auth_bp
    from routes.patient import patient_bp
    from routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(patient_bp, url_prefix="/patient")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # ================= Database =================

    with app.app_context():
        from models.user import User
        from models.doctor import Doctor
        from models.appointment import Appointment
        from models.otp import OTP

        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    from models.user import User
    from werkzeug.security import generate_password_hash

    admin_email = os.getenv(
        "ADMIN_EMAIL",
        "admin@lifecareclinic.com"
    )

    admin_password = os.getenv(
        "ADMIN_PASSWORD",
        "Admin@123456"
    )

    existing = User.query.filter_by(email=admin_email).first()

    if not existing:
        admin = User(
            name="Admin",
            email=admin_email,
            password=generate_password_hash(admin_password),
            role="admin",
            is_verified=True,
            phone="9999999999"
        )

        db.session.add(admin)
        db.session.commit()

        print(f"[✓] Admin created: {admin_email}")


@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))